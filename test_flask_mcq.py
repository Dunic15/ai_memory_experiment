#!/usr/bin/env python3
"""
Test MCQ submission using Flask test client
Simulates actual HTTP requests to verify answer recording
"""

import json
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, ARTICLES

def test_mcq_submission_flow():
    """Test MCQ submission using Flask test client"""
    
    with app.test_client() as client:
        with app.app_context():
            # Set up session (simulate user going through the flow)
            with client.session_transaction() as sess:
                sess['participant_id'] = 'TEST_USER'
                sess['article_order'] = ['uhi', 'semiconductors', 'crispr']
                sess['timing_order'] = ['post_reading', 'pre_reading', 'synchronous']
                sess['structure_condition'] = 'integrated'
            
            # Step 1: Access test page for article 0 (UHI)
            print("=" * 80)
            print("TESTING MCQ SUBMISSION FLOW")
            print("=" * 80)
            print()
            
            # Get the test page to trigger randomization
            response = client.get('/test/0')
            assert response.status_code == 200, f"Failed to load test page: {response.status_code}"
            
            # Get the session to see the randomization
            with client.session_transaction() as sess:
                questions_key = 'questions_order_0'
                mapping_key = 'questions_mapping_0'
                
                if questions_key in sess:
                    questions_list = sess[questions_key]
                    question_mapping = sess.get(mapping_key, {})
                    
                    print("Question Randomization (first 5):")
                    for rand_idx in range(min(5, len(questions_list))):
                        orig_idx = question_mapping.get(rand_idx, rand_idx)
                        q = questions_list[rand_idx]
                        print(f"  Position {rand_idx} → Original Q{orig_idx + 1}")
                    print()
                else:
                    print("⚠️ Questions not randomized yet")
                    question_mapping = {i: i for i in range(15)}
                    questions_list = ARTICLES['uhi']['questions']
            
            # Step 2: Simulate user selecting specific answers
            # User sees questions in randomized order
            # For this test, let's select specific answers that we can verify
            print("Simulating User Selections:")
            print("-" * 80)
            
            mcq_data = {}
            test_selections = {}  # Track what we're selecting for each original question
            
            # For each randomized position, determine what the user selects
            for rand_idx in range(len(questions_list)):
                orig_idx = question_mapping.get(rand_idx, rand_idx)
                q = questions_list[rand_idx]
                
                # User selects a specific option (let's use a pattern we can verify)
                # For original Q1, select option b (index 1)
                # For original Q2, select option c (index 2)
                # etc.
                selected_option = (orig_idx + 1) % 4  # Pattern: Q1→1, Q2→2, Q3→3, Q4→0, Q5→1, ...
                test_selections[orig_idx] = selected_option
                
                q_key = f"q{rand_idx}"
                mcq_data[q_key] = selected_option
                
                selected_text = q['options'][selected_option] if selected_option < len(q['options']) else 'N/A'
                print(f"  Position {rand_idx} (Orig Q{orig_idx + 1}): Select option {chr(97 + selected_option)} = '{selected_text[:40]}...'")
            
            print()
            print("MCQ Data to submit:")
            print(json.dumps(mcq_data, indent=2))
            print()
            
            # Step 3: Submit the test
            print("Submitting test...")
            response = client.post('/submit_test', 
                                 json={
                                     'article_num': 0,
                                     'mcq': mcq_data,
                                     'mcq_answer_times_ms': {},
                                     'mcq_total_time_ms': 0,
                                     'recall': {}
                                 },
                                 content_type='application/json')
            
            if response.status_code != 200:
                print(f"❌ Submission failed: {response.status_code}")
                print(response.get_data(as_text=True))
                return False
            
            # Step 4: Check what was logged
            print("Checking logged data...")
            print("-" * 80)
            
            # Read the log file
            log_file = 'experiment_data/TEST_USER_log.csv'
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    header = next(reader)
                    for row in reader:
                        if len(row) > 1 and row[1] == 'mcq_responses':
                            logged_mcq = json.loads(row[5]) if len(row) > 5 else {}
                            logged_qa = json.loads(row[11]) if len(row) > 11 else {}
                            
                            print("Logged mcq_answers:")
                            for q_key in sorted(logged_mcq.keys(), key=lambda x: int(x[1:])):
                                print(f"  {q_key}: {logged_mcq[q_key]}")
                            
                            print()
                            print("Verifying consistency:")
                            mismatches = []
                            for rand_idx in range(len(questions_list)):
                                q_key = f"q{rand_idx}"
                                orig_idx = question_mapping.get(rand_idx, rand_idx)
                                
                                expected = test_selections[orig_idx]
                                logged_mcq_ans = logged_mcq.get(q_key)
                                logged_qa_ans = logged_qa.get(q_key, {}).get('participant_answer')
                                
                                if logged_mcq_ans != expected:
                                    mismatches.append({
                                        'q': orig_idx + 1,
                                        'expected': expected,
                                        'logged_mcq': logged_mcq_ans
                                    })
                                    print(f"  ❌ Q{orig_idx + 1} (pos {rand_idx}): Expected={expected}, Logged(mcq)={logged_mcq_ans}")
                                elif logged_mcq_ans != logged_qa_ans:
                                    mismatches.append({
                                        'q': orig_idx + 1,
                                        'logged_mcq': logged_mcq_ans,
                                        'logged_qa': logged_qa_ans
                                    })
                                    print(f"  ❌ Q{orig_idx + 1} (pos {rand_idx}): mcq_answers={logged_mcq_ans}, question_accuracy={logged_qa_ans}")
                                else:
                                    print(f"  ✅ Q{orig_idx + 1} (pos {rand_idx}): Expected={expected}, Logged={logged_mcq_ans}")
                            
                            if mismatches:
                                print(f"\n❌ Found {len(mismatches)} mismatches!")
                                return False
                            else:
                                print(f"\n✅ All answers correctly recorded!")
                                return True
            else:
                print(f"⚠️ Log file not found: {log_file}")
                return False

if __name__ == "__main__":
    import csv
    success = test_mcq_submission_flow()
    sys.exit(0 if success else 1)

