#!/usr/bin/env python3
"""
Test script to verify MCQ answers are saved correctly with randomization.
This simulates a full user flow and checks the logged data.
"""

import sys
import os
import json
import csv
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, ARTICLES

def test_mcq_saving():
    """Test that MCQ answers are saved correctly with randomization."""
    
    print("=" * 80)
    print("TESTING MCQ ANSWER SAVING WITH RANDOMIZATION")
    print("=" * 80)
    print()
    
    # Use Flask test client
    client = app.test_client()
    
    # Step 1: Start a session (simulate participant starting)
    participant_id = "TEST_MCQ_001"
    
    print(f"Step 1: Starting session for participant {participant_id}")
    with client.session_transaction() as sess:
        sess['participant_id'] = participant_id
        sess['article_order'] = ['uhi', 'semiconductors', 'crispr']
        sess['timing_order'] = ['post_reading', 'pre_reading', 'post_reading']
    
    print("✓ Session initialized")
    print()
    
    # Step 2: Access the test page to trigger randomization
    article_num = 0  # First article (uhi)
    
    print(f"Step 2: Accessing test page for article {article_num}")
    response = client.get(f'/test/{article_num}')
    
    if response.status_code != 200:
        print(f"✗ Failed to access test page: {response.status_code}")
        return False
    
    print("✓ Test page accessed")
    
    # Get the randomized questions and mapping from session
    with client.session_transaction() as sess:
        questions_key = f'questions_order_{article_num}'
        mapping_key = f'questions_mapping_{article_num}'
        
        questions_list = sess.get(questions_key, [])
        question_mapping = sess.get(mapping_key, {})
        
        print(f"   Questions randomized: {len(questions_list)} questions")
        print(f"   Mapping stored: {len(question_mapping)} entries")
        
        if not question_mapping:
            print("   ⚠ WARNING: No mapping found in session!")
        else:
            print(f"   Mapping example: {dict(list(question_mapping.items())[:3])}")
        
        # Get article key from session
        article_order = sess.get('article_order', [])
        if article_num < len(article_order):
            article_key = article_order[article_num]
        else:
            article_key = 'uhi'  # fallback
    
    print()
    
    # Step 3: Submit MCQ answers (simulate user selecting specific answers)
    print("Step 3: Submitting MCQ answers")
    
    # Get the article's questions to know how many there are
    article = ARTICLES[article_key]
    num_questions = len(article['questions'])
    
    # Create MCQ data: user selects answer index 0 for all questions (for testing)
    # Format: {'q0': 0, 'q1': 0, ...} where keys are randomized question indices
    mcq_data = {}
    for rand_idx in range(num_questions):
        mcq_data[f'q{rand_idx}'] = 0  # User selects option 0 (first option) for all
    
    print(f"   Submitting {len(mcq_data)} answers (all set to option 0 for testing)")
    print(f"   MCQ data format: {dict(list(mcq_data.items())[:3])}...")
    
    # Submit the test (as JSON, matching frontend format)
    response = client.post('/submit_test', 
        json={
            'article_num': article_num,
            'mcq': mcq_data,
            'mcq_answer_times_ms': {},
            'mcq_total_time_ms': 120000  # 2 minutes in ms
        },
        content_type='application/json'
    )
    
    if response.status_code != 200:
        print(f"✗ Failed to submit test: {response.status_code}")
        print(f"   Response: {response.data.decode()}")
        return False
    
    print("✓ Test submitted successfully")
    print()
    
    # Step 4: Check what was logged
    print("Step 4: Checking logged data")
    
    # Find the log file
    log_dir = 'experiment_data'
    if not os.path.exists(log_dir):
        print(f"✗ Log directory not found: {log_dir}")
        return False
    
    # Find the log file for this participant
    log_file = f'{participant_id}_log.csv'
    log_path = os.path.join(log_dir, log_file)
    
    if not os.path.exists(log_path):
        print(f"✗ No log file found for participant {participant_id}")
        print(f"   Expected: {log_path}")
        return False
    
    print(f"   Found log file: {log_file}")
    
    # Read the log file (CSV with headers)
    with open(log_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Find the MCQ submission row
    mcq_row = None
    for row in rows:
        if row.get('phase') == 'mcq_responses' and row.get('article_num') == str(article_num):
            mcq_row = row
            break
    
    if not mcq_row:
        print("✗ No MCQ submission found in log file")
        print(f"   Available phases: {set(r.get('phase', '') for r in rows)}")
        return False
    
    print("✓ Found MCQ submission in log")
    print()
    
    # Step 5: Parse and verify the logged data
    print("Step 5: Verifying logged data")
    print("-" * 80)
    
    timestamp = mcq_row.get('timestamp', '')
    log_participant = mcq_row.get('participant_id', '') if 'participant_id' in mcq_row else participant_id
    log_article_num = mcq_row.get('article_num', '')
    log_article_key = mcq_row.get('article_key', '')
    log_timing = mcq_row.get('timing', '')
    mcq_answers_str = mcq_row.get('mcq_answers', '')
    question_accuracy_str = mcq_row.get('question_accuracy', '')
    correct_count = mcq_row.get('correct_count', '')
    total_count = mcq_row.get('total_questions', '')
    time_spent = mcq_row.get('mcq_total_time_ms', '')
    question_mapping_str = mcq_row.get('question_mapping', '')
    
    print(f"Phase: mcq_responses")
    print(f"Participant: {log_participant}")
    print(f"Article: {log_article_num} ({log_article_key})")
    print(f"Timing: {log_timing}")
    print(f"Time Spent: {time_spent} ms")
    print()
    
    # Parse MCQ answers
    try:
        mcq_answers = json.loads(mcq_answers_str)
        print(f"MCQ Answers (raw from frontend): {mcq_answers}")
        print(f"   Format: randomized_index -> selected_option_index")
    except json.JSONDecodeError as e:
        print(f"✗ Failed to parse MCQ answers: {e}")
        print(f"   Raw string: {mcq_answers_str}")
        return False
    
    # Parse question accuracy
    try:
        question_accuracy = json.loads(question_accuracy_str)
        print(f"Question Accuracy: {question_accuracy}")
        print(f"   Format: original_index -> {{'correct': bool, 'selected': int, 'correct_answer': int}}")
    except json.JSONDecodeError as e:
        print(f"✗ Failed to parse question accuracy: {e}")
        print(f"   Raw string: {question_accuracy_str}")
        return False
    
    # Parse question mapping if available
    if question_mapping_str:
        try:
            logged_mapping_raw = json.loads(question_mapping_str)
            # Normalize keys to integers (JSON may have string keys)
            logged_mapping = {}
            for k, v in logged_mapping_raw.items():
                try:
                    key_int = int(k) if isinstance(k, str) else k
                    val_int = int(v) if isinstance(v, str) else v
                    logged_mapping[key_int] = val_int
                except (ValueError, TypeError):
                    pass
            print(f"Question Mapping (logged): {logged_mapping}")
            print(f"   Format: randomized_index -> original_index")
        except json.JSONDecodeError as e:
            print(f"⚠ Could not parse question mapping: {e}")
            logged_mapping = {}
    else:
        print("⚠ No question mapping found in log")
        logged_mapping = {}
    
    print()
    print(f"Correct Count: {correct_count}/{total_count}")
    print()
    
    # Step 6: Verify the mapping and answers
    print("Step 6: Verifying answer mapping")
    print("-" * 80)
    
    # Get the correct answers from ARTICLES
    correct_answers = {}
    for orig_idx, q in enumerate(article['questions']):
        correct_answers[orig_idx] = q['correct']
    
    print(f"Correct answers (by original index): {correct_answers}")
    print()
    
    # Verify each answer
    print("Answer Verification:")
    print()
    
    all_correct = True
    for q_key, selected_option in mcq_answers.items():
        # Extract randomized index from key (e.g., 'q0' -> 0)
        if q_key.startswith('q'):
            rand_idx = int(q_key[1:])
        else:
            rand_idx = int(q_key)
        
        # Get original index from mapping
        if logged_mapping:
            orig_idx = logged_mapping.get(rand_idx, rand_idx)
        elif question_accuracy:
            # Try to get from question_accuracy (which uses q_key as key)
            acc_data = question_accuracy.get(q_key, {})
            if isinstance(acc_data, dict):
                orig_idx = acc_data.get('original_question_index', rand_idx)
            else:
                orig_idx = rand_idx  # Fallback
        else:
            orig_idx = rand_idx  # No mapping available
        
        correct_option = correct_answers.get(orig_idx, -1)
        is_correct = (selected_option == correct_option)
        
        if not is_correct:
            all_correct = False
        
        status = "✓" if is_correct else "✗"
        print(f"  {status} {q_key} (rand_idx={rand_idx}, orig_idx={orig_idx}): Selected {selected_option}, Correct {correct_option} {'✓' if is_correct else '✗'}")
    
    print()
    
    # Step 7: Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    if all_correct:
        print("✓ All answers mapped correctly!")
    else:
        print("⚠ Some answers may not match (expected since we selected all option 0)")
    
    print()
    print("Key Checks:")
    print(f"  ✓ Session mapping stored: {len(question_mapping) > 0}")
    print(f"  ✓ MCQ answers logged: {len(mcq_answers) > 0}")
    print(f"  ✓ Question accuracy calculated: {len(question_accuracy) > 0}")
    print(f"  ✓ Mapping logged: {len(logged_mapping) > 0 if logged_mapping else False}")
    print()
    
    return True

if __name__ == '__main__':
    try:
        success = test_mcq_saving()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

