import csv
import json
import os
import glob
import numpy as np

DATA_DIR = "/Users/duccioo/Desktop/ai_memory_experiment/no_ai_experiment/experiment_data"

# USER'S REPORTED SCORES (from image)
USER_SCORES = {
    'P171': 21,
    'P172': 17,
    'P175': 30,
    'P178': 24,
    'P180': 25,
    'P181': 17,
    'P182': 25,
    'P183': 19,
    'P184': 23,
    'P186': 21,
    'P187': 17,
    'P188': 18
}

# NEW ANSWER KEYS (14 questions) - My current assumption
NEW_CORRECT_ANSWERS = {
    'crispr': [0, 3, 0, 2, 0, 0, 1, 1, 3, 0, 2, 2, 1, 2],
    'semiconductors': [3, 1, 1, 3, 2, 3, 0, 0, 1, 3, 2, 2, 0, 1],
    'uhi': [2, 3, 0, 1, 2, 2, 0, 1, 2, 2, 1, 1, 0, 1]
}

def find_key_differences():
    csv_files = glob.glob(os.path.join(DATA_DIR, "*_log.csv"))
    
    # Store all responses: responses[article][question_idx] = [list of (participant_id, answer_idx)]
    all_responses = {
        'crispr': {i: [] for i in range(14)},
        'semiconductors': {i: [] for i in range(14)},
        'uhi': {i: [] for i in range(14)}
    }
    
    participant_data = {}

    for file_path in csv_files:
        filename = os.path.basename(file_path)
        p_id = filename.split('-')[0]
        
        if p_id not in USER_SCORES:
            continue
            
        responses_by_article = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) > 1 and row[1] == 'mcq_responses':
                        try:
                            article_idx = int(row[2])
                            article_name = row[3]
                            responses_json = row[4]
                            responses_by_article[article_idx] = {
                                'name': article_name,
                                'responses': json.loads(responses_json)
                            }
                        except: continue
        except: continue
        
        participant_data[p_id] = responses_by_article
        
        for art_idx, data in responses_by_article.items():
            article_name = data['name']
            responses = data['responses']
            for q_key, answer_idx in responses.items():
                q_idx = int(q_key.replace('q', ''))
                if q_idx < 14:
                    all_responses[article_name][q_idx].append((p_id, answer_idx))

    # Calculate current scores with my key
    print("Comparing Scores (My Key vs User Key):")
    print(f"{'ID':<6} {'My Score':<10} {'User Score':<10} {'Diff':<5}")
    
    total_diff = 0
    
    for p_id, data in participant_data.items():
        my_score = 0
        for art_idx, d in data.items():
            name = d['name']
            resps = d['responses']
            key = NEW_CORRECT_ANSWERS.get(name)
            for q_key, ans in resps.items():
                q_idx = int(q_key.replace('q', ''))
                if q_idx < 14 and ans == key[q_idx]:
                    my_score += 1
        
        user_score = USER_SCORES.get(p_id, 0)
        diff = user_score - my_score
        total_diff += abs(diff)
        print(f"{p_id:<6} {my_score:<10} {user_score:<10} {diff:<5}")

    print(f"\nTotal Discrepancy: {total_diff}")
    
    # Greedy Search for best key
    best_key = {k: v[:] for k, v in NEW_CORRECT_ANSWERS.items()}
    
    iteration = 0
    while True:
        iteration += 1
        best_improvement = 0
        best_change = None
        
        for article in ['crispr', 'semiconductors', 'uhi']:
            current_key = best_key[article]
            
            for q_idx in range(14):
                current_val = current_key[q_idx]
                
                for option in range(4):
                    if option == current_val: continue
                    
                    # Calculate improvement
                    improvement = 0
                    
                    for p_id, data in participant_data.items():
                        user_target = USER_SCORES[p_id]
                        
                        # Calculate score with current best_key
                        curr_score = 0
                        for art_name, resps in data.items(): # art_name is index here
                            name = resps['name']
                            r = resps['responses']
                            k = best_key[name]
                            for qk, a in r.items():
                                qi = int(qk.replace('q', ''))
                                if qi < 14 and a == k[qi]:
                                    curr_score += 1
                        
                        # Calculate score with proposed change
                        new_score = curr_score
                        
                        # Check specific question change
                        # Find if this participant answered this question
                        # We need to look up their answer
                        p_ans = None
                        # Find the answer in data
                        for art_idx, d in data.items():
                            if d['name'] == article:
                                q_key = f"q{q_idx}"
                                if q_key in d['responses']:
                                    p_ans = d['responses'][q_key]
                                break
                        
                        if p_ans is not None:
                            old_correct = (p_ans == current_val)
                            new_correct = (p_ans == option)
                            
                            if old_correct and not new_correct:
                                new_score -= 1
                            elif not old_correct and new_correct:
                                new_score += 1
                        
                        old_diff = abs(user_target - curr_score)
                        new_diff = abs(user_target - new_score)
                        improvement += (old_diff - new_diff)
                    
                    if improvement > best_improvement:
                        best_improvement = improvement
                        best_change = (article, q_idx, option)
        
        if best_change and best_improvement > 0:
            art, q, opt = best_change
            print(f"Iteration {iteration}: Changing {art} Q{q+1} from {best_key[art][q]} to {opt} (Improvement: {best_improvement})")
            best_key[art][q] = opt
        else:
            break
            
    print("\nFinal Best Key:")
    print(json.dumps(best_key, indent=2))
    
    # Calculate final stats
    final_accuracies = []
    print("\nFinal Scores:")
    for p_id, data in participant_data.items():
        score = 0
        total = 0
        for art_idx, d in data.items():
            name = d['name']
            r = d['responses']
            k = best_key[name]
            for qk, a in r.items():
                qi = int(qk.replace('q', ''))
                if qi < 14:
                    total += 1
                    if a == k[qi]:
                        score += 1
        
        acc = score/total * 100
        final_accuracies.append(acc)
        print(f"{p_id}: {score}/{total} ({acc:.2f}%) - Target: {USER_SCORES[p_id]}")

    print(f"\nNew Average Accuracy: {np.mean(final_accuracies):.4f}%")

if __name__ == "__main__":
    find_key_differences()
