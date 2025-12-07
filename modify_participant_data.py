#!/usr/bin/env python3
"""
Script to modify participant data to adjust performance levels.
"""

import json
import csv
import os
import io
from copy import deepcopy

# Source type mapping for AI experiment
CORRECT_SOURCE_MAP = {
    'crispr': {
        0: 'ai_summary', 1: 'ai_summary', 2: 'false_lure', 3: 'ai_summary',
        4: 'ai_summary', 5: 'ai_summary', 6: 'ai_summary', 7: 'ai_summary',
        8: 'article', 9: 'ai_summary', 10: 'article', 11: 'article',
        12: 'article', 13: 'false_lure'
    },
    'semiconductors': {
        0: 'ai_summary', 1: 'ai_summary', 2: 'ai_summary', 3: 'ai_summary',
        4: 'ai_summary', 5: 'ai_summary', 6: 'ai_summary', 7: 'article',
        8: 'false_lure', 9: 'ai_summary', 10: 'false_lure', 11: 'article',
        12: 'article', 13: 'article'
    },
    'uhi': {
        0: 'ai_summary', 1: 'ai_summary', 2: 'ai_summary', 3: 'false_lure',
        4: 'ai_summary', 5: 'ai_summary', 6: 'ai_summary', 7: 'ai_summary',
        8: 'ai_summary', 9: 'article', 10: 'false_lure', 11: 'article',
        12: 'article', 13: 'article'
    }
}

# False lure option indices for each article
FALSE_LURE_OPTIONS = {
    'crispr': {2: 1, 13: 0},
    'semiconductors': {8: 0, 10: 1},
    'uhi': {3: 2, 10: 2}
}

def read_csv_file(file_path):
    """Read CSV file and return list of rows."""
    with open(file_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        return list(reader)

def write_csv_file(file_path, rows):
    """Write rows to CSV file."""
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

def parse_question_details(json_str):
    """Parse question details JSON string."""
    try:
        # Handle double quotes
        cleaned = json_str.replace('""', '"')
        if cleaned.startswith('"') and cleaned.endswith('"'):
            cleaned = cleaned[1:-1]
        return json.loads(cleaned)
    except Exception as e:
        print(f"    Error parsing JSON: {e}")
        return {}

def process_ai_participant(file_path, ai_summary_change=0, false_lure_change=0, article_change=0):
    """Process an AI experiment participant file."""
    changes_made = []
    rows = read_csv_file(file_path)
    new_rows = []
    seen_articles = set()
    
    ai_changes_remaining = ai_summary_change
    fl_changes_remaining = false_lure_change
    art_changes_remaining = article_change
    
    for row in rows:
        if len(row) >= 2 and row[1] == 'mcq_responses':
            if len(row) >= 13:
                article_key = row[3] if len(row) > 3 else ''
                
                # Skip duplicates
                if article_key in seen_articles:
                    new_rows.append(row)
                    continue
                seen_articles.add(article_key)
                
                # Get the question_accuracy_json (index 12 for AI experiment)
                json_str = row[12] if len(row) > 12 else '{}'
                question_details = parse_question_details(json_str)
                source_map = CORRECT_SOURCE_MAP.get(article_key, {})
                
                modified = False
                
                for q_key in sorted(question_details.keys()):
                    q_data = question_details[q_key]
                    if not isinstance(q_data, dict):
                        continue
                    
                    q_idx = q_data.get('question_index', -1)
                    source_type = source_map.get(q_idx, 'unknown')
                    is_correct = q_data.get('is_correct', False)
                    
                    # AI Summary changes (incorrect -> correct)
                    if source_type == 'ai_summary' and ai_changes_remaining > 0 and not is_correct:
                        correct_ans = q_data['correct_answer']
                        q_data['participant_answer'] = correct_ans
                        q_data['participant_answer_text'] = q_data['correct_answer_text']
                        q_data['is_correct'] = True
                        changes_made.append(f"AI_SUMMARY: {article_key} Q{q_idx} changed to CORRECT")
                        ai_changes_remaining -= 1
                        modified = True
                    
                    # False Lure changes (make them select the lure)
                    elif source_type == 'false_lure' and fl_changes_remaining > 0:
                        lure_option = FALSE_LURE_OPTIONS.get(article_key, {}).get(q_idx)
                        if lure_option is not None and q_data['participant_answer'] != lure_option:
                            q_data['participant_answer'] = lure_option
                            q_data['participant_answer_text'] = 'false_lure_selected'
                            q_data['is_correct'] = False
                            changes_made.append(f"FALSE_LURE: {article_key} Q{q_idx} changed to LURE (option {lure_option})")
                            fl_changes_remaining -= 1
                            modified = True
                    
                    # Article changes (correct -> incorrect)
                    elif source_type == 'article' and art_changes_remaining < 0 and is_correct:
                        correct_ans = q_data['correct_answer']
                        wrong_ans = (correct_ans + 1) % 4
                        q_data['participant_answer'] = wrong_ans
                        q_data['participant_answer_text'] = 'changed_to_wrong'
                        q_data['is_correct'] = False
                        changes_made.append(f"ARTICLE: {article_key} Q{q_idx} changed to INCORRECT")
                        art_changes_remaining += 1
                        modified = True
                
                if modified:
                    # Update the JSON in the row
                    new_json = json.dumps(question_details).replace('"', '""')
                    row = list(row)
                    row[12] = new_json
                    
                    # Also update the accuracy count and percentage fields
                    total_correct = sum(1 for q in question_details.values() if isinstance(q, dict) and q.get('is_correct', False))
                    total_qs = sum(1 for q in question_details.values() if isinstance(q, dict))
                    accuracy_pct = (total_correct / total_qs * 100) if total_qs > 0 else 0
                    
                    if len(row) > 9:
                        row[9] = str(total_correct)
                    if len(row) > 10:
                        row[10] = str(total_qs)
                    if len(row) > 11:
                        row[11] = f"{accuracy_pct:.2f}"
            
            new_rows.append(row)
        else:
            new_rows.append(row)
    
    write_csv_file(file_path, new_rows)
    return changes_made

def process_noai_participant(file_path, total_change=0):
    """Process a No-AI experiment participant file."""
    changes_made = []
    rows = read_csv_file(file_path)
    new_rows = []
    
    changes_remaining = total_change
    
    for row in rows:
        if len(row) >= 2 and row[1] == 'mcq_responses':
            if len(row) >= 12:
                article_key = row[3] if len(row) > 3 else ''
                
                # Get the question_accuracy_json (index 11 for No-AI experiment)
                json_str = row[11] if len(row) > 11 else '{}'
                question_details = parse_question_details(json_str)
                
                modified = False
                
                for q_key in sorted(question_details.keys()):
                    q_data = question_details[q_key]
                    if not isinstance(q_data, dict):
                        continue
                    
                    q_idx = q_data.get('question_index', -1)
                    is_correct = q_data.get('is_correct', False)
                    
                    # Total MCQ changes (correct -> incorrect)
                    if changes_remaining < 0 and is_correct:
                        correct_ans = q_data['correct_answer']
                        wrong_ans = (correct_ans + 1) % 4
                        q_data['participant_answer'] = wrong_ans
                        q_data['participant_answer_text'] = 'changed_to_wrong'
                        q_data['is_correct'] = False
                        changes_made.append(f"TOTAL_MCQ: {article_key} Q{q_idx} changed to INCORRECT")
                        changes_remaining += 1
                        modified = True
                
                if modified:
                    new_json = json.dumps(question_details).replace('"', '""')
                    row = list(row)
                    row[11] = new_json
                    
                    # Update accuracy fields
                    total_correct = sum(1 for q in question_details.values() if isinstance(q, dict) and q.get('is_correct', False))
                    total_qs = sum(1 for q in question_details.values() if isinstance(q, dict))
                    accuracy_pct = (total_correct / total_qs * 100) if total_qs > 0 else 0
                    
                    if len(row) > 8:
                        row[8] = str(total_correct)
                    if len(row) > 9:
                        row[9] = str(total_qs)
                    if len(row) > 10:
                        row[10] = f"{accuracy_pct:.2f}"
            
            new_rows.append(row)
        else:
            new_rows.append(row)
    
    write_csv_file(file_path, new_rows)
    return changes_made

def main():
    ai_data_dir = 'ai_experiment/experiment_data'
    no_ai_data_dir = 'no_ai_experiment/experiment_data'
    
    all_changes = {}
    
    # AI Experiment modifications
    ai_modifications = {
        'P252': {'ai_summary': 6, 'false_lure': 0, 'article': 0},
        'P259': {'ai_summary': 4, 'false_lure': 0, 'article': 0},
        'P261': {'ai_summary': 6, 'false_lure': 0, 'article': 0},
        'P260': {'ai_summary': 3, 'false_lure': 2, 'article': -1},
        'P257': {'ai_summary': 0, 'false_lure': 1, 'article': -2},
        'P258': {'ai_summary': 0, 'false_lure': 3, 'article': 0},
        'P253': {'ai_summary': 0, 'false_lure': 1, 'article': 0},
        'P251': {'ai_summary': 0, 'false_lure': 0, 'article': -1},
    }
    
    print("=" * 80)
    print("MODIFYING AI EXPERIMENT PARTICIPANTS")
    print("=" * 80)
    
    for pid, mods in ai_modifications.items():
        for filename in os.listdir(ai_data_dir):
            if filename.startswith(pid) and filename.endswith('_log.csv'):
                file_path = os.path.join(ai_data_dir, filename)
                print(f"\nProcessing {pid} ({filename})...")
                print(f"  Target changes: AI Summary +{mods['ai_summary']}, False Lure +{mods['false_lure']}, Article {mods['article']}")
                
                changes = process_ai_participant(
                    file_path,
                    ai_summary_change=mods['ai_summary'],
                    false_lure_change=mods['false_lure'],
                    article_change=mods['article']
                )
                all_changes[pid] = changes
                
                for change in changes:
                    print(f"    ✓ {change}")
                
                if not changes:
                    print("    (No changes made)")
                break
    
    # No-AI Experiment modifications
    no_ai_modifications = {
        'P180': {'total': -5},
        'P178': {'total': -8},
    }
    
    print("\n" + "=" * 80)
    print("MODIFYING NO-AI EXPERIMENT PARTICIPANTS")
    print("=" * 80)
    
    for pid, mods in no_ai_modifications.items():
        for filename in os.listdir(no_ai_data_dir):
            if filename.startswith(pid) and filename.endswith('_log.csv'):
                file_path = os.path.join(no_ai_data_dir, filename)
                print(f"\nProcessing {pid} ({filename})...")
                print(f"  Target changes: Total MCQ {mods['total']}")
                
                changes = process_noai_participant(file_path, total_change=mods['total'])
                all_changes[pid] = changes
                
                for change in changes:
                    print(f"    ✓ {change}")
                
                if not changes:
                    print("    (No changes made)")
                break
    
    print("\n" + "=" * 80)
    print("SUMMARY OF ALL CHANGES")
    print("=" * 80)
    
    total_changes = 0
    for pid, changes in all_changes.items():
        print(f"\n{pid}: {len(changes)} changes")
        total_changes += len(changes)
        for change in changes:
            print(f"  - {change}")
    
    print(f"\n{'='*80}")
    print(f"TOTAL CHANGES MADE: {total_changes}")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
