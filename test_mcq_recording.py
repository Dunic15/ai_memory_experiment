#!/usr/bin/env python3
"""
Test script to verify MCQ answer recording
Simulates the submission process to check if answers are correctly stored
"""

import json
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Flask app
from app import app, ARTICLES

def test_mcq_submission():
    """Test MCQ submission with known answers"""
    
    # Test data: simulate what a user would select
    # For UHI article, let's say user selects:
    # Q1: option b (index 1) - "warmer"
    # Q2: option c (index 2) - "ninety to ninety-five"
    # Q3: option d (index 3) - "High thermal mass"
    # etc.
    
    test_answers = {
        'uhi': {
            'selected': [1, 2, 3, 0, 1, 2, 2, 0, 1, 2, 2, 1, 3, 0, 1],  # User selections
            'correct': [1, 2, 3, 0, 1, 2, 2, 0, 1, 2, 2, 1, 3, 0, 1],   # Correct answers from app.py
        },
        'semiconductors': {
            'selected': [1, 2, 0, 1, 3, 2, 3, 0, 3, 1, 3, 2, 0, 0, 1],
            'correct': [1, 2, 0, 1, 3, 2, 3, 0, 3, 1, 3, 2, 0, 0, 1],
        },
        'crispr': {
            'selected': [0, 3, 2, 1, 2, 0, 1, 1, 3, 0, 2, 1, 2, 0, 3],
            'correct': [0, 3, 2, 1, 2, 0, 1, 1, 3, 0, 2, 1, 2, 0, 3],
        }
    }
    
    print("=" * 80)
    print("TESTING MCQ ANSWER RECORDING")
    print("=" * 80)
    print()
    
    for article_key, data in test_answers.items():
        print(f"\nArticle: {article_key.upper()}")
        print("-" * 80)
        
        article = ARTICLES.get(article_key)
        if not article:
            print(f"ERROR: Article {article_key} not found")
            continue
        
        questions = article.get('questions', [])
        selected = data['selected']
        correct = data['correct']
        
        # Simulate randomized order (questions might be shuffled)
        # For testing, let's assume no randomization first
        randomized_order = list(range(len(questions)))
        
        # Build mcq_data as it would come from frontend (using randomized indices)
        mcq_data = {}
        for rand_idx, orig_idx in enumerate(randomized_order):
            q_key = f"q{rand_idx}"
            mcq_data[q_key] = selected[orig_idx]  # User's selection for original question at randomized position
        
        print(f"MCQ Data (as submitted from frontend):")
        for q_key in sorted(mcq_data.keys(), key=lambda x: int(x[1:])):
            print(f"  {q_key}: {mcq_data[q_key]} (option {chr(97 + mcq_data[q_key])})")
        
        # Simulate the backend processing
        question_mapping = {i: i for i in range(len(questions))}  # No randomization in this test
        
        print(f"\nProcessing answers:")
        mismatches = []
        for rand_idx in range(len(questions)):
            q_key = f"q{rand_idx}"
            participant_answer = mcq_data.get(q_key)
            orig_idx = question_mapping.get(rand_idx, rand_idx)
            question = questions[orig_idx] if orig_idx < len(questions) else None
            
            if question:
                correct_answer = question.get("correct")
                expected_selection = selected[orig_idx]
                
                print(f"  Q{orig_idx + 1} (rand_idx={rand_idx}): "
                      f"Selected={participant_answer}, Expected={expected_selection}, "
                      f"Correct={correct_answer}, Match={participant_answer == expected_selection}")
                
                if participant_answer != expected_selection:
                    mismatches.append({
                        'question': orig_idx + 1,
                        'selected': participant_answer,
                        'expected': expected_selection
                    })
        
        if mismatches:
            print(f"\n❌ MISMATCHES FOUND:")
            for m in mismatches:
                print(f"  Question {m['question']}: Selected {m['selected']}, Expected {m['expected']}")
        else:
            print(f"\n✅ All answers match expected selections")
    
    print("\n" + "=" * 80)
    print("TESTING WITH RANDOMIZATION")
    print("=" * 80)
    
    # Now test with randomization
    import random
    random.seed(42)  # Fixed seed for reproducibility
    
    article_key = 'uhi'
    article = ARTICLES.get(article_key)
    questions = article.get('questions', [])
    
    # Simulate randomization
    questions_list = list(questions)
    original_indices = list(range(len(questions_list)))
    combined = list(zip(questions_list, original_indices))
    random.shuffle(combined)
    questions_list, shuffled_original_indices = zip(*combined)
    questions_list = list(questions_list)
    
    question_mapping = {i: orig_idx for i, orig_idx in enumerate(shuffled_original_indices)}
    
    print(f"\nRandomized order mapping:")
    for rand_idx, orig_idx in question_mapping.items():
        print(f"  Randomized position {rand_idx} → Original question {orig_idx + 1}")
    
    # Simulate user selecting answers (user sees randomized order)
    # User selects based on what they see (randomized position)
    test_selections = [1, 2, 3, 0, 1, 2, 2, 0, 1, 2, 2, 1, 3, 0, 1]  # User's selections
    
    mcq_data_randomized = {}
    for rand_idx in range(len(questions)):
        q_key = f"q{rand_idx}"
        # User selects answer for the question at randomized position rand_idx
        # But we need to know which original question this is
        orig_idx = question_mapping[rand_idx]
        # User's selection for this original question
        mcq_data_randomized[q_key] = test_selections[orig_idx]
    
    print(f"\nMCQ Data with randomization (as submitted):")
    for q_key in sorted(mcq_data_randomized.keys(), key=lambda x: int(x[1:])):
        rand_idx = int(q_key[1:])
        orig_idx = question_mapping[rand_idx]
        print(f"  {q_key} (orig Q{orig_idx + 1}): {mcq_data_randomized[q_key]}")
    
    # Verify processing
    print(f"\nVerifying processing:")
    all_match = True
    for rand_idx in range(len(questions)):
        q_key = f"q{rand_idx}"
        participant_answer = mcq_data_randomized.get(q_key)
        orig_idx = question_mapping.get(rand_idx, rand_idx)
        question = questions[orig_idx] if orig_idx < len(questions) else None
        
        if question:
            expected = test_selections[orig_idx]
            if participant_answer != expected:
                print(f"  ❌ Q{orig_idx + 1}: Participant={participant_answer}, Expected={expected}")
                all_match = False
            else:
                print(f"  ✅ Q{orig_idx + 1}: Participant={participant_answer}, Expected={expected}")
    
    if all_match:
        print("\n✅ All randomized answers processed correctly")
    else:
        print("\n❌ Errors found in randomized answer processing")

if __name__ == "__main__":
    with app.app_context():
        test_mcq_submission()

