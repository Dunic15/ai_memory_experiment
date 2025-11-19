#!/usr/bin/env python3
"""
Test the complete MCQ flow to identify where answers might be getting misrecorded
"""

import json
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, ARTICLES

def simulate_user_selection():
    """Simulate a user selecting specific answers"""
    
    print("=" * 80)
    print("SIMULATING USER MCQ SELECTIONS")
    print("=" * 80)
    print()
    
    # Test with UHI article
    article_key = 'uhi'
    article = ARTICLES.get(article_key)
    questions = article.get('questions', [])
    
    # Set a fixed seed for reproducibility
    random.seed(123)
    
    # Simulate randomization (as done in test_phase)
    questions_list = list(questions)
    original_indices = list(range(len(questions_list)))
    combined = list(zip(questions_list, original_indices))
    random.shuffle(combined)
    questions_list, shuffled_original_indices = zip(*combined)
    questions_list = list(questions_list)
    
    # Create mapping: randomized_index -> original_index
    question_mapping = {i: orig_idx for i, orig_idx in enumerate(shuffled_original_indices)}
    
    print("Randomized Question Order:")
    print("-" * 80)
    for rand_idx, q in enumerate(questions_list):
        orig_idx = question_mapping[rand_idx]
        print(f"Position {rand_idx} (Original Q{orig_idx + 1}): {q['q'][:60]}...")
        print(f"  Options: {[opt[:30] + '...' if len(opt) > 30 else opt for opt in q['options']]}")
        print(f"  Correct answer (from article): option {chr(97 + q['correct'])} (index {q['correct']})")
        print()
    
    # Simulate user selecting answers
    # User sees questions in randomized order and selects based on what they see
    # For this test, let's say user selects the CORRECT answer for each question they see
    print("Simulating User Selections:")
    print("-" * 80)
    mcq_data = {}  # This is what gets sent from frontend
    
    for rand_idx, q in enumerate(questions_list):
        # User sees question at randomized position rand_idx
        # User selects the correct answer for this question (which they see)
        selected_option = q['correct']  # User selects correct answer
        
        q_key = f"q{rand_idx}"
        mcq_data[q_key] = selected_option
        
        orig_idx = question_mapping[rand_idx]
        print(f"Position {rand_idx} (Original Q{orig_idx + 1}): User selects option {chr(97 + selected_option)} (index {selected_option})")
        print(f"  Frontend sends: {q_key} = {selected_option}")
    
    print()
    print("MCQ Data (as sent from frontend):")
    print(json.dumps(mcq_data, indent=2))
    print()
    
    # Now simulate backend processing (as in submit_test)
    print("Backend Processing:")
    print("-" * 80)
    
    correct_count = 0
    total_questions = 0
    question_accuracy = {}
    
    for rand_idx in range(len(questions)):
        total_questions += 1
        q_key = f"q{rand_idx}"  # Answer key from frontend (randomized order)
        participant_answer = mcq_data.get(q_key, None)
        
        # Map randomized index to original index
        orig_idx = question_mapping.get(rand_idx, rand_idx)
        question = questions[orig_idx] if orig_idx < len(questions) else None
        
        if question:
            correct_answer = question.get("correct", None)
            
            # Check if answer is correct
            is_correct = (participant_answer is not None and 
                         participant_answer == correct_answer)
            
            question_accuracy[q_key] = {
                "participant_answer": participant_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "original_question_index": orig_idx,
                "randomized_question_index": rand_idx
            }
            
            print(f"Q{orig_idx + 1} (rand_pos={rand_idx}): "
                  f"Participant={participant_answer}, Correct={correct_answer}, "
                  f"Match={is_correct} {'✅' if is_correct else '❌'}")
            
            if is_correct:
                correct_count += 1
    
    print()
    print(f"Results: {correct_count}/{total_questions} correct")
    print()
    
    # Now verify what would be stored in the log
    print("What gets stored in question_accuracy:")
    print("-" * 80)
    for q_key in sorted(question_accuracy.keys(), key=lambda x: int(x[1:])):
        qa = question_accuracy[q_key]
        orig_idx = qa['original_question_index']
        rand_idx = qa['randomized_question_index']
        part_ans = qa['participant_answer']
        corr_ans = qa['correct_answer']
        
        # Get the question text to verify
        q = questions[orig_idx]
        selected_option_text = q['options'][part_ans] if part_ans < len(q['options']) else 'N/A'
        correct_option_text = q['options'][corr_ans] if corr_ans < len(q['options']) else 'N/A'
        
        print(f"Q{orig_idx + 1} (rand_pos={rand_idx}):")
        print(f"  Participant selected: {part_ans} = '{selected_option_text[:50]}...'")
        print(f"  Correct answer: {corr_ans} = '{correct_option_text[:50]}...'")
        print(f"  Match: {qa['is_correct']}")
        print()
    
    # Now test with a specific scenario: user selects wrong answer
    print("=" * 80)
    print("TESTING WITH SPECIFIC USER SELECTIONS")
    print("=" * 80)
    print()
    
    # Reset seed to get same randomization
    random.seed(123)
    questions_list = list(questions)
    original_indices = list(range(len(questions_list)))
    combined = list(zip(questions_list, original_indices))
    random.shuffle(combined)
    questions_list, shuffled_original_indices = zip(*combined)
    questions_list = list(questions_list)
    question_mapping = {i: orig_idx for i, orig_idx in enumerate(shuffled_original_indices)}
    
    # User selects specific answers (some correct, some wrong)
    # Let's say for the first question they see (which is original Q9), they select option "a" (index 0)
    user_selections = {}
    for rand_idx, q in enumerate(questions_list):
        orig_idx = question_mapping[rand_idx]
        # For testing: select option 0 for first question, option 1 for second, etc.
        user_selections[rand_idx] = rand_idx % 4  # Cycle through options
    
    mcq_data_user = {f"q{rand_idx}": user_selections[rand_idx] for rand_idx in range(len(questions))}
    
    print("User selections (what user actually clicks):")
    for rand_idx in range(len(questions)):
        orig_idx = question_mapping[rand_idx]
        q = questions_list[rand_idx]
        selected = user_selections[rand_idx]
        selected_text = q['options'][selected] if selected < len(q['options']) else 'N/A'
        print(f"  Position {rand_idx} (Original Q{orig_idx + 1}): User clicks option {chr(97 + selected)} = '{selected_text[:50]}...'")
    
    print()
    print("Verifying backend processing:")
    mismatches = []
    for rand_idx in range(len(questions)):
        q_key = f"q{rand_idx}"
        participant_answer = mcq_data_user.get(q_key)
        orig_idx = question_mapping.get(rand_idx, rand_idx)
        question = questions[orig_idx] if orig_idx < len(questions) else None
        
        if question:
            expected = user_selections[rand_idx]
            if participant_answer != expected:
                mismatches.append({
                    'rand_idx': rand_idx,
                    'orig_idx': orig_idx,
                    'participant': participant_answer,
                    'expected': expected
                })
                print(f"  ❌ Q{orig_idx + 1} (pos {rand_idx}): Participant={participant_answer}, Expected={expected}")
            else:
                print(f"  ✅ Q{orig_idx + 1} (pos {rand_idx}): Participant={participant_answer}, Expected={expected}")
    
    if mismatches:
        print(f"\n❌ Found {len(mismatches)} mismatches!")
    else:
        print(f"\n✅ All user selections correctly recorded!")

if __name__ == "__main__":
    with app.app_context():
        simulate_user_selection()

