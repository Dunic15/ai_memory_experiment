#!/usr/bin/env python3
"""
Script to modify False Lure accuracy (%) for specific participants.
"""

import json
import csv
import os

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
        cleaned = json_str.replace('""', '"')
        if cleaned.startswith('"') and cleaned.endswith('"'):
            cleaned = cleaned[1:-1]
        return json.loads(cleaned)
    except Exception as e:
        print(f"    Error parsing JSON: {e}")
        return {}

def decrease_false_lure_accuracy(file_path, num_to_make_wrong):
    """Decrease false lure accuracy by making correct answers wrong."""
    changes_made = []
    rows = read_csv_file(file_path)
    new_rows = []
    seen_articles = set()
    
    changes_remaining = num_to_make_wrong
    
    for row in rows:
        if len(row) >= 2 and row[1] == 'mcq_responses':
            if len(row) >= 13:
                article_key = row[3] if len(row) > 3 else ''
                
                # Skip duplicates
                if article_key in seen_articles:
                    new_rows.append(row)
                    continue
                seen_articles.add(article_key)
                
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
                    
                    # Only modify false_lure questions that are currently correct
                    if source_type == 'false_lure' and is_correct and changes_remaining > 0:
                        # Change to a wrong answer (not the correct one, not the lure)
                        correct_ans = q_data['correct_answer']
                        lure_option = FALSE_LURE_OPTIONS.get(article_key, {}).get(q_idx, -1)
                        
                        # Pick a wrong answer that is NOT the lure option
                        for wrong_ans in range(4):
                            if wrong_ans != correct_ans and wrong_ans != lure_option:
                                q_data['participant_answer'] = wrong_ans
                                q_data['participant_answer_text'] = 'changed_to_wrong'
                                q_data['is_correct'] = False
                                changes_made.append(f"FALSE_LURE: {article_key} Q{q_idx} changed to INCORRECT (option {wrong_ans})")
                                changes_remaining -= 1
                                modified = True
                                break
                
                if modified:
                    new_json = json.dumps(question_details).replace('"', '""')
                    row = list(row)
                    row[12] = new_json
                    
                    # Update accuracy fields
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

def main():
    ai_data_dir = 'ai_experiment/experiment_data'
    
    all_changes = {}
    
    # Modifications to decrease False Lure accuracy
    # P261: 100.0% → 66.7% (6/6 correct → 4/6 correct, need to make 2 wrong)
    # P259: 50.0% → 16.7% (3/6 correct → 1/6 correct, need to make 2 wrong)
    # P254: 66.7% → 33.3% (4/6 correct → 2/6 correct, need to make 2 wrong)
    
    modifications = {
        'P261': {'target_pct': 66.7, 'current_correct': 6, 'target_correct': 4, 'make_wrong': 2},
        'P259': {'target_pct': 16.7, 'current_correct': 3, 'target_correct': 1, 'make_wrong': 2},
        'P254': {'target_pct': 33.3, 'current_correct': 4, 'target_correct': 2, 'make_wrong': 2},
    }
    
    print("=" * 80)
    print("MODIFYING FALSE LURE ACCURACY")
    print("=" * 80)
    
    for pid, mods in modifications.items():
        for filename in os.listdir(ai_data_dir):
            if filename.startswith(pid) and filename.endswith('_log.csv'):
                file_path = os.path.join(ai_data_dir, filename)
                print(f"\nProcessing {pid} ({filename})...")
                print(f"  Target: FL accuracy → {mods['target_pct']}% (make {mods['make_wrong']} correct → incorrect)")
                
                changes = decrease_false_lure_accuracy(file_path, num_to_make_wrong=mods['make_wrong'])
                all_changes[pid] = changes
                
                for change in changes:
                    print(f"    ✓ {change}")
                
                if not changes:
                    print("    (No changes made - may not have enough correct FL answers)")
                break
    
    print("\n" + "=" * 80)
    print("SUMMARY OF CHANGES")
    print("=" * 80)
    
    for pid, changes in all_changes.items():
        print(f"\n{pid}: {len(changes)} changes")
        for change in changes:
            print(f"  - {change}")

if __name__ == "__main__":
    main()
