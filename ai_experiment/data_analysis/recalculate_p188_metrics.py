import csv
import json
import os

# --- CONFIGURATION ---
PARTICIPANT_ID = "P188"
LOG_FILE_PATH = "/Users/duccioo/Desktop/ai_memory_experiment/no_ai_experiment/experiment_data/P188-张心旭-NON-AI_log.csv"

# NEW ANSWER KEYS (14 questions)
NEW_CORRECT_ANSWERS = {
    'crispr': [0, 3, 0, 2, 0, 0, 1, 1, 3, 0, 2, 2, 1, 2],
    'semiconductors': [3, 1, 1, 3, 2, 3, 0, 0, 1, 3, 2, 2, 0, 1],
    'uhi': [2, 3, 0, 1, 2, 2, 0, 1, 2, 2, 1, 1, 0, 1]
}

# NEW FALSE LURE MAP
NEW_FALSE_LURE_MAP = {
    'crispr': [
        {'question_index': 2, 'false_lure_option_index': 1},
        {'question_index': 13, 'false_lure_option_index': 0}
    ],
    'semiconductors': [
        {'question_index': 8, 'false_lure_option_index': 0},
        {'question_index': 10, 'false_lure_option_index': 1}
    ],
    'uhi': [
        {'question_index': 3, 'false_lure_option_index': 2},
        {'question_index': 10, 'false_lure_option_index': 2}
    ]
}

# SOURCE MAPPING
CORRECT_SOURCE_MAP = {
    'crispr': {
        0: 'ai_summary', 1: 'ai_summary', 2: 'false_lure', 3: 'ai_summary',
        4: 'ai_summary', 5: 'ai_summary', 6: 'ai_summary', 7: 'ai_summary',
        8: 'article', 9: 'ai_summary', 10: 'article', 11: 'article',
        12: 'article', 13: 'false_lure'
    },
    'semiconductors': {
        0: 'ai_summary', 1: 'ai_summary', 2: 'ai_summary', 3: 'ai_summary',
        4: 'ai_summary', 5: 'ai_summary', 6: 'ai_summary', 7: 'article',
        8: 'false_lure', 9: 'ai_summary', 10: 'false_lure', 11: 'article',
        12: 'article', 13: 'article'
    },
    'uhi': {
        0: 'ai_summary', 1: 'ai_summary', 2: 'ai_summary', 3: 'false_lure',
        4: 'ai_summary', 5: 'ai_summary', 6: 'ai_summary', 7: 'ai_summary',
        8: 'ai_summary', 9: 'article', 10: 'false_lure', 11: 'article',
        12: 'article', 13: 'article'
    }
}

def calculate_metrics():
    print(f"Analyzing {PARTICIPANT_ID}...")
    
    # 1. Read and Deduplicate Responses
    responses_by_article = {}
    
    try:
        with open(LOG_FILE_PATH, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) > 1 and row[1] == 'mcq_responses':
                    # Format: timestamp, type, article_index, article_name, responses_json, ...
                    try:
                        article_idx = int(row[2])
                        article_name = row[3]
                        responses_json = row[4]
                        
                        # Store/Overwrite to handle duplicates (last one wins)
                        responses_by_article[article_idx] = {
                            'name': article_name,
                            'responses': json.loads(responses_json)
                        }
                    except Exception as e:
                        print(f"Error parsing row: {e}")
                        continue
    except FileNotFoundError:
        print(f"File not found: {LOG_FILE_PATH}")
        return

    print(f"Found responses for {len(responses_by_article)} articles.")
    if len(responses_by_article) != 3:
        print("WARNING: Expected 3 articles.")

    # 2. Calculate Metrics
    total_correct = 0
    total_questions = 0
    
    for art_idx, data in responses_by_article.items():
        article_name = data['name']
        responses = data['responses']
        
        correct_answers = NEW_CORRECT_ANSWERS.get(article_name)
        
        if not correct_answers:
            print(f"No answer key for {article_name}")
            continue
            
        print(f"\nProcessing {article_name} (Article {art_idx}):")
        
        for q_key, answer_idx in responses.items():
            q_idx = int(q_key.replace('q', ''))
            
            if q_idx >= len(correct_answers):
                print(f"  Skipping q{q_idx} (out of range)")
                continue
                
            is_correct = (answer_idx == correct_answers[q_idx])
            
            # Update totals
            total_questions += 1
            if is_correct:
                total_correct += 1
            else:
                print(f"  Q{q_idx+1} Incorrect: Selected {answer_idx}, Expected {correct_answers[q_idx]}")

    # 3. Print Results
    print("\n" + "="*40)
    print(f"RESULTS FOR {PARTICIPANT_ID} (CONTROL GROUP)")
    print("="*40)
    
    print(f"Total Questions Processed: {total_questions}")
    if total_questions > 0:
        print(f"Total Accuracy: {total_correct}/{total_questions} ({total_correct/total_questions*100:.2f}%)")


if __name__ == "__main__":
    calculate_metrics()
