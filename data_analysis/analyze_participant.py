#!/usr/bin/env python3
"""
Participant Data Analysis Script
Analyzes participant log files and generates comprehensive reports
"""

import json
import csv
import sys
import os
from datetime import datetime

# Correct answers (0-indexed option indices)
CORRECT_ANSWERS = {
    'uhi': [1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 1, 1, 1, 1, 1],
    'crispr': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    'semiconductors': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1]
}

def parse_csv_log(log_file_path):
    """Parse participant log CSV file with robust handling of multiline fields."""
    data = {
        'demographics': {},
        'prior_knowledge': {},
        'ai_trust': {},
        'randomization': {},
        'reading_data': [],
        'summary_viewing': [],
        'recall_data': [],
        'mcq_data': [],
        'manipulation_check': {}
    }

    with open(log_file_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        # Skip header
        try:
            header = next(reader)
        except StopIteration:
            return data

        for parts in reader:
            if not parts or len(parts) < 2:
                continue

            timestamp = parts[0]
            phase = parts[1]

            try:
                if phase == 'demographics':
                    data['demographics'] = {
                        'full_name': parts[2] if len(parts) > 2 else '',
                        'profession': parts[3] if len(parts) > 3 else '',
                        'age': parts[4] if len(parts) > 4 else '',
                        'gender': parts[5] if len(parts) > 5 else '',
                        'native_language': parts[6] if len(parts) > 6 else '',
                        'timestamp': timestamp
                    }
                elif phase == 'prior_knowledge':
                    data['prior_knowledge'] = {
                        'familiarity': float(parts[2]) if len(parts) > 2 and parts[2] else 0,
                        'recognition': float(parts[3]) if len(parts) > 3 and parts[3] else 0,
                        'quiz_score': float(parts[4]) if len(parts) > 4 and parts[4] else 0,
                        'excluded': parts[5] if len(parts) > 5 else 'False',
                        'timestamp': timestamp
                    }
                elif phase == 'ai_trust':
                    trust_score = float(parts[2]) if len(parts) > 2 and parts[2] else 0
                    dependence_score = float(parts[3]) if len(parts) > 3 and parts[3] else 0
                    skill_score = float(parts[4]) if len(parts) > 4 and parts[4] else 0
                    reflection = parts[5] if len(parts) > 5 else ''
                    data['ai_trust'] = {
                        'trust_score': trust_score,
                        'dependence_score': dependence_score,
                        'skill_score': skill_score,
                        'reflection': reflection,
                        'timestamp': timestamp
                    }
                elif phase == 'randomization':
                    data['randomization'] = {
                        'structure': (parts[2] if len(parts) > 2 else '').lower(),
                        'timing_order': parts[3] if len(parts) > 3 else '',
                        'article_order': parts[4] if len(parts) > 4 else '',
                        'timestamp': timestamp
                    }
                elif phase == 'reading_behavior':
                    # Handle end-of-reading events; schema can vary slightly between versions
                    if len(parts) >= 6 and parts[2] == 'reading_complete':
                        # Prefer index 4 (observed in newer logs), fallback to 5
                        reading_time_ms = 0
                        for idx in (4, 5, 3):
                            if len(parts) > idx:
                                try:
                                    reading_time_ms = int(parts[idx])
                                    # Heuristic: treat very small values as invalid
                                    if reading_time_ms >= 1000 or idx == 4:
                                        break
                                except:
                                    continue
                        article_key = parts[-2] if len(parts) >= 2 else ''
                        timing = parts[-1] if len(parts) >= 1 else ''
                        # Article number is optional; attempt parse if present as penultimate-2
                        article_num = -1
                        try:
                            maybe_num = parts[-3]
                            article_num = int(maybe_num)
                        except:
                            pass
                        data['reading_data'].append({
                            'timestamp': timestamp,
                            'article_num': article_num,
                            'article_key': article_key,
                            'timing': timing,
                            'reading_time_ms': reading_time_ms
                        })
                elif phase == 'summary_viewing':
                    if len(parts) >= 8:
                        # In these rows, indices are stable as they don't include multiline fields
                        data['summary_viewing'].append({
                            'timestamp': timestamp,
                            'article_num': int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else -1,
                            'article_key': parts[3] if len(parts) > 3 else '',
                            'mode': parts[4] if len(parts) > 4 else '',
                            'structure': parts[5] if len(parts) > 5 else '',
                            'time_spent_ms': int(float(parts[6])) if len(parts) > 6 and parts[6] else 0,
                            'time_spent_seconds': float(parts[7]) if len(parts) > 7 and parts[7] else 0
                        })
                elif phase == 'recall_response':
                    # csv.reader already joined multiline recall text into a single field (index 5)
                    if len(parts) >= 13:
                        article_num = int(parts[2]) if parts[2] else -1
                        article_key = parts[3]
                        timing = parts[4]
                        recall_text = parts[5] if len(parts) > 5 else ''
                        def _as_int(idx, default=0):
                            try:
                                return int(parts[idx])
                            except:
                                return default
                        data['recall_data'].append({
                            'timestamp': timestamp,
                            'article_num': article_num,
                            'article_key': article_key,
                            'timing': timing,
                            'recall_text': recall_text,
                            'sentence_count': _as_int(6),
                            'word_count': _as_int(7),
                            'character_count': _as_int(8),
                            'confidence': _as_int(9),
                            'difficulty': _as_int(10),
                            'time_spent_ms': _as_int(11),
                            'paste_attempts': _as_int(12),
                            'over_limit': (parts[13].lower() == 'true') if len(parts) > 13 else False
                        })
                elif phase == 'mcq_responses':
                    # Expected columns:
                    # timestamp, phase, article_num, article_key, timing,
                    # answers_json, answer_times_json, total_time_ms, correct_count, total_questions, accuracy_rate, question_accuracy_json
                    if len(parts) >= 6:
                        answers_json = parts[5]
                        try:
                            mcq_answers = json.loads(answers_json.replace('""', '"'))
                        except:
                            mcq_answers = {}
                        article_num = int(parts[2]) if len(parts) > 2 and parts[2] else -1
                        article_key = parts[3] if len(parts) > 3 else ''
                        timing = parts[4] if len(parts) > 4 else ''
                        data['mcq_data'].append({
                            'timestamp': timestamp,
                            'article_num': article_num,
                            'article_key': article_key,
                            'timing': timing,
                            'answers': mcq_answers
                        })
                elif phase == 'manipulation_check':
                    if len(parts) >= 4:
                        def _as_int_safe(idx):
                            try:
                                return int(parts[idx])
                            except:
                                return -1
                        data['manipulation_check'] = {
                            'coherence': _as_int_safe(2),
                            'connectivity': _as_int_safe(3),
                            'strategy': parts[4] if len(parts) > 4 else '',
                            'timestamp': timestamp
                        }
            except Exception:
                # Robust to any malformed rows
                continue

    return data

def calculate_mcq_accuracy(mcq_data):
    """Calculate MCQ accuracy for all articles"""
    results = []
    
    for mcq in mcq_data:
        article_key = mcq['article_key']
        if article_key not in CORRECT_ANSWERS:
            continue
            
        correct = CORRECT_ANSWERS[article_key]
        answers = mcq['answers']
        
        correct_count = 0
        total = len(correct)
        details = []
        
        for q_idx in range(total):
            q_key = f'q{q_idx}'
            p_ans = answers.get(q_key, -1)
            c_ans = correct[q_idx]
            is_correct = p_ans == c_ans
            if is_correct:
                correct_count += 1
            details.append({
                'question': q_idx + 1,
                'participant_answer': p_ans,
                'correct_answer': c_ans,
                'is_correct': is_correct
            })
        
        accuracy = (correct_count / total) * 100 if total > 0 else 0
        
        results.append({
            'article_key': article_key,
            'article_num': mcq['article_num'],
            'timing': mcq['timing'],
            'accuracy': accuracy,
            'correct_count': correct_count,
            'total': total,
            'details': details,
            'timestamp': mcq['timestamp']
        })
    
    return results

def generate_analysis_report(participant_id, data, mcq_results):
    """Generate comprehensive analysis report"""
    
    report = []
    report.append("=" * 80)
    report.append(f"PARTICIPANT {participant_id} - COMPREHENSIVE DATA ANALYSIS")
    report.append("=" * 80)
    report.append("")
    report.append(f"Analysis Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Demographics
    report.append("=" * 80)
    report.append("BASIC INFORMATION")
    report.append("=" * 80)
    if data['demographics']:
        demo = data['demographics']
        report.append(f"Name: {demo.get('full_name', 'N/A')}")
        report.append(f"Age: {demo.get('age', 'N/A')}, {demo.get('gender', 'N/A')}")
        report.append(f"Profession: {demo.get('profession', 'N/A')}")
        report.append(f"Native Language: {demo.get('native_language', 'N/A')}")
        report.append(f"Start Time: {demo.get('timestamp', 'N/A')}")
    report.append("")
    
    # Prior Knowledge
    report.append("=" * 80)
    report.append("PRIOR KNOWLEDGE ASSESSMENT")
    report.append("=" * 80)
    if data['prior_knowledge']:
        pk = data['prior_knowledge']
        report.append(f"Familiarity Score: {pk.get('familiarity', 0):.1f}/7")
        report.append(f"Recognition Score: {pk.get('recognition', 0)}/10")
        report.append(f"Quiz Score: {pk.get('quiz_score', 0):.1f}/5")
        report.append(f"Excluded: {pk.get('excluded', 'False')}")
    report.append("")
    
    # AI Trust
    report.append("=" * 80)
    report.append("AI TRUST & TECHNOLOGY USE")
    report.append("=" * 80)
    if data['ai_trust']:
        ai = data['ai_trust']
        report.append(f"AI Trust Score: {ai.get('trust_score', 0):.2f}/7")
        report.append(f"AI Dependence Score: {ai.get('dependence_score', 0):.2f}/7")
        report.append(f"Tech Skill Score: {ai.get('skill_score', 0):.2f}/7")
        reflection = ai.get('reflection', '')
        if reflection:
            report.append(f"Open Reflection: {reflection[:200]}..." if len(reflection) > 200 else f"Open Reflection: {reflection}")
    report.append("")
    
    # Experimental Conditions
    report.append("=" * 80)
    report.append("EXPERIMENTAL CONDITIONS")
    report.append("=" * 80)
    if data['randomization']:
        rand = data['randomization']
        report.append(f"Structure Condition: {rand.get('structure', 'N/A').upper()}")
        try:
            timing_order = json.loads(rand.get('timing_order', '[]'))
            article_order = json.loads(rand.get('article_order', '[]'))
            report.append(f"Article Order: {' → '.join([a.upper() for a in article_order])}")
            report.append(f"Timing Order: {', '.join(timing_order)}")
        except:
            report.append(f"Timing Order: {rand.get('timing_order', 'N/A')}")
            report.append(f"Article Order: {rand.get('article_order', 'N/A')}")
    report.append("")
    
    # Reading Behavior
    report.append("=" * 80)
    report.append("READING BEHAVIOR")
    report.append("=" * 80)
    for rd in data['reading_data']:
        reading_min = rd['reading_time_ms'] / 60000
        reading_sec = rd['reading_time_ms'] / 1000
        article_label = f"{rd['article_key'].upper()}" if rd.get('article_key') else f"#{rd.get('article_num', -1)+1}"
        report.append(f"Article {article_label}:")
        report.append(f"  Reading Time: {reading_min:.2f} minutes ({reading_sec:.1f} seconds)")
        report.append(f"  Timing Mode: {rd['timing']}")
        report.append("")
    
    # Summary Viewing
    report.append("=" * 80)
    report.append("SUMMARY VIEWING")
    report.append("=" * 80)
    for sv in data['summary_viewing']:
        sv_min = sv['time_spent_seconds'] / 60
        report.append(f"Article {sv['article_num']+1} ({sv['article_key'].upper()}):")
        report.append(f"  Mode: {sv['mode']}")
        report.append(f"  Structure: {sv['structure']}")
        report.append(f"  Time Spent: {sv['time_spent_seconds']:.2f} seconds ({sv_min:.2f} minutes)")
        report.append("")
    
    # Free Recall
    report.append("=" * 80)
    report.append("FREE RECALL")
    report.append("=" * 80)
    for rec in data['recall_data']:
        rec_min = rec['time_spent_ms'] / 60000
        report.append(f"Article {rec['article_num']+1} ({rec['article_key'].upper()}):")
        report.append(f"  Timing: {rec['timing']}")
        report.append(f"  Text: {rec['recall_text'][:100]}..." if len(rec['recall_text']) > 100 else f"  Text: {rec['recall_text']}")
        report.append(f"  Words: {rec['word_count']}, Sentences: {rec['sentence_count']}, Characters: {rec['character_count']}")
        report.append(f"  Confidence: {rec['confidence']}/7, Difficulty: {rec['difficulty']}/7")
        report.append(f"  Time Spent: {rec_min:.2f} minutes ({rec['time_spent_ms']/1000:.1f} seconds)")
        report.append(f"  Paste Attempts: {rec['paste_attempts']}")
        report.append("")
    
    # MCQ Performance
    report.append("=" * 80)
    report.append("MCQ PERFORMANCE")
    report.append("=" * 80)
    for result in mcq_results:
        article_label = f"{result['article_key'].upper()}" if result.get('article_key') else f"#{result.get('article_num', -1)+1}"
        report.append(f"Article {article_label} - {result['timing']} mode")
        report.append(f"Accuracy: {result['correct_count']}/{result['total']} = {result['accuracy']:.1f}%")
        report.append("Question Details:")
        for detail in result['details']:
            status = "CORRECT" if detail['is_correct'] else "WRONG"
            report.append(f"  Q{detail['question']:2d}: Participant={detail['participant_answer']}, Correct={detail['correct_answer']} - {status}")
        report.append("")
    
    # Manipulation Check
    report.append("=" * 80)
    report.append("MANIPULATION CHECK")
    report.append("=" * 80)
    if data['manipulation_check']:
        mc = data['manipulation_check']
        report.append(f"Semantic Coherence: {mc.get('coherence', -1)}/7")
        report.append(f"Relational Connectivity: {mc.get('connectivity', -1)}/7")
        report.append(f"Memory Strategy: {mc.get('strategy', 'N/A')}")
    report.append("")
    
    # Summary Statistics
    report.append("=" * 80)
    report.append("SUMMARY STATISTICS")
    report.append("=" * 80)
    
    if data['reading_data']:
        avg_reading = sum(rd['reading_time_ms'] for rd in data['reading_data']) / len(data['reading_data']) / 60000
        report.append(f"Average Reading Time: {avg_reading:.2f} minutes")
    
    if data['summary_viewing']:
        avg_summary = sum(sv['time_spent_seconds'] for sv in data['summary_viewing']) / len(data['summary_viewing']) / 60
        report.append(f"Average Summary Viewing Time: {avg_summary:.2f} minutes")
    
    if data['recall_data']:
        avg_words = sum(rec['word_count'] for rec in data['recall_data']) / len(data['recall_data'])
        avg_confidence = sum(rec['confidence'] for rec in data['recall_data']) / len(data['recall_data'])
        report.append(f"Average Recall Words: {avg_words:.1f}")
        report.append(f"Average Confidence: {avg_confidence:.2f}/7")
    
    if mcq_results:
        avg_accuracy = sum(r['accuracy'] for r in mcq_results) / len(mcq_results)
        report.append(f"Average MCQ Accuracy: {avg_accuracy:.1f}%")
    
    report.append("")
    report.append("=" * 80)
    report.append("END OF ANALYSIS")
    report.append("=" * 80)
    
    return "\n".join(report)

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_participant.py <participant_id>")
        print("Example: python analyze_participant.py P064")
        sys.exit(1)
    
    participant_id = sys.argv[1].upper()
    log_file = f"../experiment_data/{participant_id}_log.csv"
    
    if not os.path.exists(log_file):
        print(f"Error: Log file not found: {log_file}")
        sys.exit(1)
    
    print(f"Analyzing {participant_id}...")
    data = parse_csv_log(log_file)
    mcq_results = calculate_mcq_accuracy(data['mcq_data'])
    report = generate_analysis_report(participant_id, data, mcq_results)
    
    output_file = f"{participant_id}_ANALYSIS.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Analysis complete! Report saved to: {output_file}")
    print("\n" + "=" * 80)
    print(report)

if __name__ == "__main__":
    main()


