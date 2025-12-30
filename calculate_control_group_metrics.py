import csv
import json
import os
import glob

# List of participants to analyze
target_participants = [
    "P171", "P172", "P175", "P178", "P180", "P181", 
    "P182", "P183", "P184", "P186", "P187", "P188"
]

data_dir = '/Users/duccioo/Desktop/ai_memory_experiment/no_ai_experiment/experiment_data'

def calculate_participant_accuracy(file_path):
    total_correct = 0
    total_questions = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if not row or len(row) < 2: continue
                phase = row[1]
                
                if phase == 'mcq_responses':
                    # For No-AI logs, details_json is typically at index 11
                    # Structure: timestamp, phase, article_num, article_key, answers_json, answers_text_json, timing_json, total_time, score, total_questions, accuracy, details_json
                    try:
                        if len(row) > 11:
                            details_json_str = row[11]
                            # sometimes it might be at 12 if the format varies, but P171 was 11
                            # Let's try to parse it. If it fails, try 12.
                            try:
                                details = json.loads(details_json_str)
                            except:
                                if len(row) > 12:
                                    details = json.loads(row[12])
                                else:
                                    continue
                            
                            for q_key, q_data in details.items():
                                total_questions += 1
                                if q_data.get('is_correct'):
                                    total_correct += 1
                    except Exception as e:
                        print(f"Error parsing row in {file_path}: {e}")
                        continue
                        
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return 0, 0

    return total_correct, total_questions

print(f"{'Participant':<12} | {'Correct':<8} | {'Total':<6} | {'Accuracy':<10}")
print("-" * 45)

for pid in target_participants:
    # Find the file for this participant
    pattern = os.path.join(data_dir, f"{pid}*log.csv")
    files = glob.glob(pattern)
    
    if not files:
        print(f"{pid:<12} | {'N/A':<8} | {'N/A':<6} | {'N/A':<10}")
        continue
        
    file_path = files[0]
    correct, total = calculate_participant_accuracy(file_path)
    
    accuracy = (correct / total * 100) if total > 0 else 0
    print(f"{pid:<12} | {correct:<8} | {total:<6} | {accuracy:.2f}%")
