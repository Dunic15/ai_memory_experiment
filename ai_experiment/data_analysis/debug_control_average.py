import csv
import json
import os
import glob
import numpy as np

DATA_DIR = "/Users/duccioo/Desktop/ai_memory_experiment/no_ai_experiment/experiment_data"

# ORIGINAL ANSWER KEYS (15 questions)
ORIGINAL_CORRECT_ANSWERS = {
    'crispr': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    'semiconductors': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1],
    'uhi': [1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 1, 1, 1, 1, 1]
}

# NEW ANSWER KEYS (14 questions)
NEW_CORRECT_ANSWERS = {
    'crispr': [0, 3, 0, 2, 0, 0, 1, 1, 3, 0, 2, 2, 1, 2],
    'semiconductors': [3, 1, 1, 3, 2, 3, 0, 0, 1, 3, 2, 2, 0, 1],
    'uhi': [2, 3, 0, 1, 2, 2, 0, 1, 2, 2, 1, 1, 0, 1]
}

def calculate_control_stats_debug():
    accuracies = []
    participant_scores = {}

    csv_files = glob.glob(os.path.join(DATA_DIR, "*_log.csv"))
    
    print(f"Found {len(csv_files)} log files.")
    
    for file_path in csv_files:
        filename = os.path.basename(file_path)
        p_id = filename.split('-')[0]
        
        # Skip P185 if P186 exists and is the same person (based on name)
        # P185 had no responses in previous run.
        
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
                        except Exception as e:
                            continue
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            continue
            
        if not responses_by_article:
            print(f"{p_id}: No responses found")
            continue
            
        # Calculate Score
        total_correct = 0
        total_questions = 0
        
        for art_idx, data in responses_by_article.items():
            article_name = data['name']
            responses = data['responses']
            
            max_q_idx = 0
            if responses:
                max_q_idx = max([int(k.replace('q', '')) for k in responses.keys()])
            
            if max_q_idx >= 14:
                correct_answers = ORIGINAL_CORRECT_ANSWERS.get(article_name)
            else:
                correct_answers = NEW_CORRECT_ANSWERS.get(article_name)
            
            if not correct_answers:
                continue
                
            for q_key, answer_idx in responses.items():
                q_idx = int(q_key.replace('q', ''))
                if q_idx < len(correct_answers):
                    if answer_idx == correct_answers[q_idx]:
                        total_correct += 1
                    total_questions += 1
        
        if total_questions > 0:
            accuracy = (total_correct / total_questions) * 100
            accuracies.append(accuracy)
            participant_scores[p_id] = accuracy
            print(f"{p_id}: {accuracy:.2f}% ({total_correct}/{total_questions})")
        else:
            print(f"{p_id}: No valid questions")

    if accuracies:
        mean_acc = np.mean(accuracies)
        print("\n" + "="*30)
        print(f"CONTROL GROUP STATISTICS (N={len(accuracies)})")
        print("="*30)
        print(f"Average Accuracy: {mean_acc:.2f}%")
        
        # Try to find combination that yields 50.99%
        target = 50.99
        print(f"\nSearching for subset matching {target}%...")
        
        import itertools
        
        # Try removing 1 participant
        for p_id, score in participant_scores.items():
            subset = [s for pid, s in participant_scores.items() if pid != p_id]
            if subset:
                avg = np.mean(subset)
                if abs(avg - target) < 0.1:
                    print(f"Excluding {p_id}: {avg:.2f}%")

        # Try removing 2 participants
        for combo in itertools.combinations(participant_scores.keys(), 2):
            subset = [s for pid, s in participant_scores.items() if pid not in combo]
            if subset:
                avg = np.mean(subset)
                if abs(avg - target) < 0.1:
                    print(f"Excluding {combo}: {avg:.2f}%")

if __name__ == "__main__":
    calculate_control_stats_debug()
