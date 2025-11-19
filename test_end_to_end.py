#!/usr/bin/env python3
"""
End-to-end test of MCQ answer recording
Simulates the complete flow from user selection to log storage to analysis
"""

import json
import random
import csv
import io
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, ARTICLES

def test_end_to_end():
    """Test the complete flow"""
    
    print("=" * 80)
    print("END-TO-END MCQ TEST")
    print("=" * 80)
    print()
    
    # Set fixed seed
    random.seed(999)
    
    article_key = 'uhi'
    article = ARTICLES.get(article_key)
    questions = article.get('questions', [])
    
    # Step 1: Simulate randomization (as in test_phase)
    questions_list = list(questions)
    original_indices = list(range(len(questions_list)))
    combined = list(zip(questions_list, original_indices))
    random.shuffle(combined)
    questions_list, shuffled_original_indices = zip(*combined)
    questions_list = list(questions_list)
    question_mapping = {i: orig_idx for i, orig_idx in enumerate(shuffled_original_indices)}
    
    print("STEP 1: Question Randomization")
    print("-" * 80)
    print("Randomized order (first 5):")
    for rand_idx in range(min(5, len(questions))):
        orig_idx = question_mapping[rand_idx]
        q = questions_list[rand_idx]
        print(f"  Position {rand_idx} → Original Q{orig_idx + 1}: {q['q'][:50]}...")
    print()
    
    # Step 2: Simulate user selecting specific answers
    # User sees questions in randomized order and selects answers
    # For this test, let's say user selects option index 0 for first question, 1 for second, etc.
    user_selections = {}
    print("STEP 2: User Selections")
    print("-" * 80)
    print("User sees questions and selects answers:")
    for rand_idx, q in enumerate(questions_list):
        orig_idx = question_mapping[rand_idx]
        # User selects a specific option (let's use a pattern: 0, 1, 2, 3, 0, 1, ...)
        selected_option = rand_idx % 4
        user_selections[rand_idx] = selected_option
        selected_text = q['options'][selected_option] if selected_option < len(q['options']) else 'N/A'
        print(f"  Position {rand_idx} (Orig Q{orig_idx + 1}): User selects option {chr(97 + selected_option)} = '{selected_text[:40]}...'")
    print()
    
    # Step 3: Simulate frontend collection (as in submitTest function)
    mcq_data = {}
    print("STEP 3: Frontend Collection")
    print("-" * 80)
    print("Frontend collects answers:")
    for rand_idx in range(len(questions)):
        q_key = f"q{rand_idx}"
        selected = user_selections[rand_idx]
        mcq_data[q_key] = selected
        print(f"  {q_key} = {selected}")
    print()
    print("MCQ Data JSON (as sent to backend):")
    print(json.dumps(mcq_data, indent=2))
    print()
    
    # Step 4: Simulate backend processing (as in submit_test)
    print("STEP 4: Backend Processing")
    print("-" * 80)
    question_accuracy = {}
    
    for rand_idx in range(len(questions)):
        q_key = f"q{rand_idx}"
        participant_answer = mcq_data.get(q_key, None)
        orig_idx = question_mapping.get(rand_idx, rand_idx)
        question = questions[orig_idx] if orig_idx < len(questions) else None
        
        if question:
            correct_answer = question.get("correct", None)
            is_correct = (participant_answer is not None and participant_answer == correct_answer)
            
            question_accuracy[q_key] = {
                "participant_answer": participant_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "original_question_index": orig_idx,
                "randomized_question_index": rand_idx
            }
            
            print(f"  Q{orig_idx + 1} (rand_pos={rand_idx}): "
                  f"Participant={participant_answer}, Correct={correct_answer}, "
                  f"Match={is_correct}")
    print()
    
    # Step 5: Simulate what gets logged
    print("STEP 5: Data Logging")
    print("-" * 80)
    log_entry = {
        "article_num": 0,
        "article_key": article_key,
        "timing": "post_reading",
        "mcq_answers": json.dumps(mcq_data),
        "question_accuracy": json.dumps(question_accuracy)
    }
    
    print("Logged mcq_answers:")
    print(json.dumps(mcq_data, indent=2))
    print()
    print("Logged question_accuracy (first 3 entries):")
    qa_sample = {k: question_accuracy[k] for k in list(question_accuracy.keys())[:3]}
    print(json.dumps(qa_sample, indent=2))
    print()
    
    # Step 6: Simulate reading from log (as in analysis script)
    print("STEP 6: Reading from Log")
    print("-" * 80)
    
    # Parse the logged data
    logged_mcq_answers = json.loads(log_entry["mcq_answers"])
    logged_question_accuracy = json.loads(log_entry["question_accuracy"])
    
    print("Reading mcq_answers from log:")
    for q_key in sorted(logged_mcq_answers.keys(), key=lambda x: int(x[1:])):
        print(f"  {q_key}: {logged_mcq_answers[q_key]}")
    print()
    
    print("Reading question_accuracy from log:")
    for q_key in sorted(list(logged_question_accuracy.keys())[:5], key=lambda x: int(x[1:])):
        qa = logged_question_accuracy[q_key]
        print(f"  {q_key}: participant_answer={qa['participant_answer']}, "
              f"original_question_index={qa['original_question_index']}")
    print()
    
    # Step 7: Verify consistency
    print("STEP 7: Verification")
    print("-" * 80)
    
    mismatches = []
    for rand_idx in range(len(questions)):
        q_key = f"q{rand_idx}"
        
        # What user selected
        user_selected = user_selections[rand_idx]
        
        # What's in mcq_answers log
        logged_answer = logged_mcq_answers.get(q_key)
        
        # What's in question_accuracy log
        qa_answer = logged_question_accuracy.get(q_key, {}).get('participant_answer')
        
        orig_idx = question_mapping[rand_idx]
        
        if user_selected != logged_answer:
            mismatches.append({
                'rand_idx': rand_idx,
                'orig_idx': orig_idx,
                'user_selected': user_selected,
                'logged_mcq': logged_answer
            })
            print(f"  ❌ Q{orig_idx + 1} (pos {rand_idx}): User={user_selected}, Logged(mcq)={logged_answer}")
        elif logged_answer != qa_answer:
            mismatches.append({
                'rand_idx': rand_idx,
                'orig_idx': orig_idx,
                'logged_mcq': logged_answer,
                'logged_qa': qa_answer
            })
            print(f"  ❌ Q{orig_idx + 1} (pos {rand_idx}): mcq_answers={logged_answer}, question_accuracy={qa_answer}")
        else:
            print(f"  ✅ Q{orig_idx + 1} (pos {rand_idx}): User={user_selected}, Logged={logged_answer}")
    
    if mismatches:
        print(f"\n❌ Found {len(mismatches)} mismatches!")
        return False
    else:
        print(f"\n✅ All data consistent!")
        return True

if __name__ == "__main__":
    with app.app_context():
        success = test_end_to_end()
        sys.exit(0 if success else 1)

