#!/usr/bin/env python3
"""
Analyze new participants for specific metrics:
- Total MCQ %
- AI Summary %
- AI False Summary % (False Lure questions)
- False Lures Selected
- Article Only %
"""

import json
import csv
import os

# Source type mapping for AI experiment (8 AI Summary + 2 False Lure + 4 Article per article)
CORRECT_SOURCE_MAP = {
    'crispr': {
        0: 'ai_summary',    # Q1
        1: 'ai_summary',    # Q2
        2: 'false_lure',    # Q3 - FALSE LURE
        3: 'ai_summary',    # Q4
        4: 'ai_summary',    # Q5
        5: 'ai_summary',    # Q6
        6: 'ai_summary',    # Q7
        7: 'ai_summary',    # Q8
        8: 'article',       # Q9
        9: 'ai_summary',    # Q10
        10: 'article',      # Q11
        11: 'article',      # Q12
        12: 'article',      # Q13
        13: 'false_lure'    # Q14 - FALSE LURE
    },
    'semiconductors': {
        0: 'ai_summary',    # Q1
        1: 'ai_summary',    # Q2
        2: 'ai_summary',    # Q3
        3: 'ai_summary',    # Q4
        4: 'ai_summary',    # Q5
        5: 'ai_summary',    # Q6
        6: 'ai_summary',    # Q7
        7: 'article',       # Q8
        8: 'false_lure',    # Q9 - FALSE LURE
        9: 'ai_summary',    # Q10
        10: 'false_lure',   # Q11 - FALSE LURE
        11: 'article',      # Q12
        12: 'article',      # Q13
        13: 'article'       # Q14
    },
    'uhi': {
        0: 'ai_summary',    # Q1
        1: 'ai_summary',    # Q2
        2: 'ai_summary',    # Q3
        3: 'false_lure',    # Q4 - FALSE LURE
        4: 'ai_summary',    # Q5
        5: 'ai_summary',    # Q6
        6: 'ai_summary',    # Q7
        7: 'ai_summary',    # Q8
        8: 'ai_summary',    # Q9
        9: 'article',       # Q10
        10: 'false_lure',   # Q11 - FALSE LURE
        11: 'article',      # Q12
        12: 'article',      # Q13
        13: 'article'       # Q14
    }
}

# False lure option indices for each article
FALSE_LURE_OPTIONS = {
    'crispr': {
        2: 1,   # Q3: option b (index 1)
        13: 0   # Q14: option a (index 0)
    },
    'semiconductors': {
        8: 0,   # Q9: option a (index 0)
        10: 1   # Q11: option b (index 1)
    },
    'uhi': {
        3: 2,   # Q4: option c (index 2)
        10: 2   # Q11: option c (index 2)
    }
}

def parse_log_file(log_file_path, is_ai_experiment=True):
    """Parse log file and extract MCQ data."""
    mcq_data = []
    participant_name = ""
    
    with open(log_file_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            return mcq_data, participant_name
        
        for parts in reader:
            if not parts or len(parts) < 2:
                continue
            
            phase = parts[1]
            
            if phase == 'demographics':
                participant_name = parts[2] if len(parts) > 2 else ''
            
            if phase == 'mcq_responses':
                if is_ai_experiment:
                    # AI format: timestamp, phase, article_num, article_key, timing, answers, ..., question_accuracy_json (index 12)
                    if len(parts) >= 13:
                        article_key = parts[3] if len(parts) > 3 else ''
                        question_accuracy_json = parts[12] if len(parts) > 12 else '{}'
                else:
                    # No-AI format: timestamp, phase, article_num, article_key, answers, ..., question_accuracy_json (index 11)
                    if len(parts) >= 12:
                        article_key = parts[3] if len(parts) > 3 else ''
                        question_accuracy_json = parts[11] if len(parts) > 11 else '{}'
                    else:
                        continue
                
                try:
                    question_details = json.loads(question_accuracy_json.replace('""', '"'))
                except:
                    question_details = {}
                
                mcq_data.append({
                    'article_key': article_key,
                    'question_details': question_details
                })
    
    return mcq_data, participant_name

def analyze_participant(log_file_path, is_ai_experiment=True):
    """Analyze a participant's MCQ performance by source type."""
    mcq_data, participant_name = parse_log_file(log_file_path, is_ai_experiment)
    
    # Aggregate stats
    total_correct = 0
    total_questions = 0
    ai_summary_correct = 0
    ai_summary_total = 0
    article_correct = 0
    article_total = 0
    false_lure_correct = 0
    false_lure_total = 0
    false_lures_selected = 0
    
    for mcq in mcq_data:
        article_key = mcq['article_key']
        question_details = mcq.get('question_details', {})
        
        if not is_ai_experiment:
            # For no-AI experiment, all questions are article-based
            for q_key, q_data in question_details.items():
                if not isinstance(q_data, dict):
                    continue
                total_questions += 1
                article_total += 1
                if q_data.get('is_correct', False):
                    total_correct += 1
                    article_correct += 1
        else:
            source_map = CORRECT_SOURCE_MAP.get(article_key, {})
            false_lure_opts = FALSE_LURE_OPTIONS.get(article_key, {})
            
            for q_key, q_data in question_details.items():
                if not isinstance(q_data, dict):
                    continue
                
                q_idx = q_data.get('question_index', -1)
                p_ans = q_data.get('participant_answer', -1)
                is_correct = q_data.get('is_correct', False)
                source_type = source_map.get(q_idx, 'unknown')
                
                total_questions += 1
                if is_correct:
                    total_correct += 1
                
                if source_type == 'ai_summary':
                    ai_summary_total += 1
                    if is_correct:
                        ai_summary_correct += 1
                elif source_type == 'article':
                    article_total += 1
                    if is_correct:
                        article_correct += 1
                elif source_type == 'false_lure':
                    false_lure_total += 1
                    if is_correct:
                        false_lure_correct += 1
                    # Check if participant selected the false lure option
                    if q_idx in false_lure_opts and p_ans == false_lure_opts[q_idx]:
                        false_lures_selected += 1
    
    # Calculate percentages
    total_pct = (total_correct / total_questions * 100) if total_questions > 0 else 0
    ai_summary_pct = (ai_summary_correct / ai_summary_total * 100) if ai_summary_total > 0 else 0
    article_pct = (article_correct / article_total * 100) if article_total > 0 else 0
    false_lure_pct = (false_lure_correct / false_lure_total * 100) if false_lure_total > 0 else 0
    
    return {
        'name': participant_name,
        'total_pct': total_pct,
        'ai_summary_pct': ai_summary_pct,
        'false_lure_pct': false_lure_pct,
        'false_lures_selected': false_lures_selected,
        'article_pct': article_pct,
        'total_questions': total_questions,
        'ai_summary_total': ai_summary_total,
        'article_total': article_total,
        'false_lure_total': false_lure_total
    }

def main():
    # AI experiment new participants
    ai_participants = ['P250', 'P251', 'P252', 'P253', 'P254', 'P257', 'P258', 'P259', 'P260', 'P261']
    ai_data_dir = 'ai_experiment/experiment_data'
    
    # No-AI experiment new participants
    no_ai_participants = ['P178', 'P180', 'P181', 'P182']
    no_ai_data_dir = 'no_ai_experiment/experiment_data'
    
    print("=" * 100)
    print("AI EXPERIMENT - NEW PARTICIPANTS ANALYSIS")
    print("=" * 100)
    print()
    print(f"{'Participant':<15} {'Total MCQ %':<12} {'AI Summary %':<14} {'AI False Sum %':<15} {'False Lures':<12} {'Article %':<12}")
    print("-" * 100)
    
    ai_results = []
    for pid in ai_participants:
        # Find log file
        log_file = None
        for filename in os.listdir(ai_data_dir):
            if filename.startswith(pid) and filename.endswith('_log.csv'):
                log_file = os.path.join(ai_data_dir, filename)
                break
        
        if log_file:
            result = analyze_participant(log_file, is_ai_experiment=True)
            result['pid'] = pid
            ai_results.append(result)
            print(f"{pid:<15} {result['total_pct']:>10.1f}% {result['ai_summary_pct']:>12.1f}% {result['false_lure_pct']:>13.1f}% {result['false_lures_selected']:>10} {result['article_pct']:>10.1f}%")
        else:
            print(f"{pid:<15} {'NOT FOUND':<12}")
    
    # Calculate averages for AI
    if ai_results:
        avg_total = sum(r['total_pct'] for r in ai_results) / len(ai_results)
        avg_ai = sum(r['ai_summary_pct'] for r in ai_results) / len(ai_results)
        avg_fl = sum(r['false_lure_pct'] for r in ai_results) / len(ai_results)
        avg_fl_sel = sum(r['false_lures_selected'] for r in ai_results) / len(ai_results)
        avg_art = sum(r['article_pct'] for r in ai_results) / len(ai_results)
        print("-" * 100)
        print(f"{'AVERAGE':<15} {avg_total:>10.1f}% {avg_ai:>12.1f}% {avg_fl:>13.1f}% {avg_fl_sel:>10.1f} {avg_art:>10.1f}%")
    
    print()
    print("=" * 100)
    print("NO-AI EXPERIMENT - NEW PARTICIPANTS ANALYSIS")
    print("=" * 100)
    print()
    print(f"{'Participant':<15} {'Total MCQ %':<12} {'AI Summary %':<14} {'AI False Sum %':<15} {'False Lures':<12} {'Article %':<12}")
    print("-" * 100)
    
    no_ai_results = []
    for pid in no_ai_participants:
        # Find log file
        log_file = None
        for filename in os.listdir(no_ai_data_dir):
            if filename.startswith(pid) and filename.endswith('_log.csv'):
                log_file = os.path.join(no_ai_data_dir, filename)
                break
        
        if log_file:
            result = analyze_participant(log_file, is_ai_experiment=False)
            result['pid'] = pid
            no_ai_results.append(result)
            print(f"{pid:<15} {result['total_pct']:>10.1f}% {'N/A':>12} {'N/A':>13} {'N/A':>10} {result['article_pct']:>10.1f}%")
        else:
            print(f"{pid:<15} {'NOT FOUND':<12}")
    
    # Calculate averages for No-AI
    if no_ai_results:
        avg_total = sum(r['total_pct'] for r in no_ai_results) / len(no_ai_results)
        avg_art = sum(r['article_pct'] for r in no_ai_results) / len(no_ai_results)
        print("-" * 100)
        print(f"{'AVERAGE':<15} {avg_total:>10.1f}% {'N/A':>12} {'N/A':>13} {'N/A':>10} {avg_art:>10.1f}%")

if __name__ == "__main__":
    main()
