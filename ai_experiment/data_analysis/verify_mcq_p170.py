#!/usr/bin/env python3
"""
Verify MCQ scoring for P170 and create detailed breakdown
"""

import csv
import json
import sys
import os

# Answer keys
NEW_CORRECT_ANSWERS = {
    'crispr': [0, 3, 0, 2, 0, 0, 1, 1, 3, 0, 2, 2, 1, 2],  # 14 questions
}

# Option labels
OPTION_LABELS = ['a', 'b', 'c', 'd']

def parse_mcq_row(row):
    """Parse MCQ response row from CSV"""
    if len(row) < 14:
        return None
    
    # Extract fields
    timestamp = row[0]
    phase = row[1]
    article_num = int(row[2]) if row[2] else -1
    article_key = row[3]
    timing = row[4]
    
    # Parse answers JSON (field 5)
    answers_json = row[5]
    try:
        answers = json.loads(answers_json.replace('""', '"'))
    except:
        answers = {}
    
    # Parse answer texts (field 6)
    answer_texts_json = row[6]
    try:
        answer_texts = json.loads(answer_texts_json.replace('""', '"'))
    except:
        answer_texts = {}
    
    # Parse detailed results (field 12) - contains mapping and correctness info
    detailed_results_json = row[12] if len(row) > 12 else '{}'
    try:
        detailed_results = json.loads(detailed_results_json.replace('""', '"'))
    except:
        detailed_results = {}
    
    # Question mapping no longer used (questions are not randomized)
    # Keep for backward compatibility with old data
    question_mapping_json = row[13] if len(row) > 13 else '{}'
    try:
        question_mapping = json.loads(question_mapping_json.replace('""', '"'))
    except:
        question_mapping = {}
    
    return {
        'timestamp': timestamp,
        'article_num': article_num,
        'article_key': article_key,
        'timing': timing,
        'answers': answers,
        'answer_texts': answer_texts,
        'detailed_results': detailed_results,
        'question_mapping': question_mapping  # For backward compatibility only
    }

def get_question_text(article_key, q_idx):
    """Get question text from ARTICLES"""
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from app import ARTICLES
        article = ARTICLES.get(article_key, {})
        questions = article.get('questions', [])
        if q_idx < len(questions):
            return questions[q_idx].get('q', 'N/A')
        return 'N/A'
    except:
        return 'N/A'

def get_options(article_key, q_idx):
    """Get options for a question"""
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from app import ARTICLES
        article = ARTICLES.get(article_key, {})
        questions = article.get('questions', [])
        if q_idx < len(questions):
            return questions[q_idx].get('options', [])
        return []
    except:
        return []

def main():
    log_file = "../experiment_data/P170-陈廷书-Segmented_log.csv"
    
    if not os.path.exists(log_file):
        print(f"Error: Log file not found: {log_file}")
        sys.exit(1)
    
    # Read CSV
    mcq_data = None
    with open(log_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        
        for row in reader:
            if len(row) > 1 and row[1] == 'mcq_responses':
                mcq_data = parse_mcq_row(row)
                break
    
    if not mcq_data:
        print("Error: No MCQ data found")
        sys.exit(1)
    
    article_key = mcq_data['article_key']
    answers = mcq_data['answers']
    answer_texts = mcq_data['answer_texts']
    detailed_results = mcq_data['detailed_results']
    question_mapping = mcq_data['question_mapping']
    
    # Get correct answers
    correct_answers = NEW_CORRECT_ANSWERS.get(article_key, [])
    
    # Create output file
    output_file = "P170_MCQ_DETAILED_BREAKDOWN.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("P170 MCQ DETAILED BREAKDOWN - VERIFICATION\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Article: {article_key.upper()}\n")
        f.write(f"Timing: {mcq_data['timing']}\n")
        f.write(f"Total Questions: {len(correct_answers)}\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("QUESTION-BY-QUESTION BREAKDOWN\n")
        f.write("=" * 80 + "\n\n")
        
        correct_count = 0
        total = len(correct_answers)
        
        # Process questions in original order (no randomization)
        for q_idx in range(total):
            q_key = f'q{q_idx}'
            
            # Get participant's answer
            participant_answer_idx = answers.get(q_key, -1)
            participant_answer_text = answer_texts.get(q_key, 'N/A')
            
            # Get stored data from detailed_results (for backward compatibility)
            original_q_idx = q_idx  # Questions are no longer randomized
            stored_correct = None
            stored_is_correct = None
            if q_key in detailed_results:
                # For new data: use question_index; for old data: use original_question_index
                original_q_idx = detailed_results[q_key].get('question_index', 
                                                             detailed_results[q_key].get('original_question_index', q_idx))
                stored_correct = detailed_results[q_key].get('correct_answer', None)
                stored_is_correct = detailed_results[q_key].get('is_correct', None)
            
            # Get correct answer - prefer stored value from detailed_results, then calculate
            if stored_correct is not None:
                correct_answer_idx = stored_correct
            else:
                # Calculate from answer key
                correct_answer_idx = correct_answers[original_q_idx] if original_q_idx < len(correct_answers) else -1
            
            if stored_is_correct is not None:
                is_correct = stored_is_correct
            else:
                # Calculate if not stored
                is_correct = participant_answer_idx == correct_answer_idx
            
            if is_correct:
                correct_count += 1
            
            # Get question text and options
            question_text = get_question_text(article_key, original_q_idx)
            options = get_options(article_key, original_q_idx)
            
            # Write breakdown
            f.write(f"Question {q_idx + 1}:\n")
            f.write(f"  Question: {question_text}\n")
            f.write(f"  Options:\n")
            for opt_idx, opt_text in enumerate(options):
                marker = ""
                if opt_idx == participant_answer_idx:
                    marker = " [SELECTED]"
                if opt_idx == correct_answer_idx:
                    marker += " [CORRECT]"
                f.write(f"    {OPTION_LABELS[opt_idx]}) {opt_text}{marker}\n")
            f.write(f"\n  Participant Selected: {OPTION_LABELS[participant_answer_idx] if participant_answer_idx >= 0 else 'N/A'} ({participant_answer_text})\n")
            f.write(f"  Correct Answer: {OPTION_LABELS[correct_answer_idx] if correct_answer_idx >= 0 else 'N/A'}\n")
            f.write(f"  Result: {'✓ CORRECT' if is_correct else '✗ WRONG'}\n")
            f.write("\n" + "-" * 80 + "\n\n")
        
        # Summary
        accuracy = (correct_count / total) * 100 if total > 0 else 0
        f.write("=" * 80 + "\n")
        f.write("SUMMARY\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total Questions: {total}\n")
        f.write(f"Correct: {correct_count}\n")
        f.write(f"Wrong: {total - correct_count}\n")
        f.write(f"Accuracy: {accuracy:.1f}%\n")
        f.write(f"Chance Level (4 options): 25.0%\n")
        f.write(f"Performance vs Chance: {'Above' if accuracy > 25 else 'Below'} chance level\n")
    
    print(f"Detailed breakdown saved to: {output_file}")
    print(f"\nSummary:")
    print(f"  Correct: {correct_count}/{total}")
    print(f"  Accuracy: {accuracy:.1f}%")

if __name__ == "__main__":
    main()

