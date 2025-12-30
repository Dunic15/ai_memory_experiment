import csv
import json
import os
import glob

DATA_DIR = "/Users/duccioo/Desktop/ai_memory_experiment/no_ai_experiment/experiment_data"

# Current Best Key from Greedy Search
CURRENT_KEY = {
  "crispr": [0, 3, 0, 2, 0, 0, 1, 1, 3, 0, 2, 2, 1, 2],
  "semiconductors": [3, 1, 1, 0, 2, 3, 0, 0, 1, 3, 2, 2, 0, 1], # Note Q4 changed to 0
  "uhi": [2, 3, 1, 1, 2, 2, 0, 1, 2, 2, 1, 1, 0, 1] # Note Q3 changed to 1
}

TARGETS = {
    'P172': 17,
    'P175': 30,
    'P182': 25,
    'P188': 18,
    'P181': 17
}

def check_answers():
    csv_files = glob.glob(os.path.join(DATA_DIR, "*_log.csv"))
    participant_data = {}

    for file_path in csv_files:
        filename = os.path.basename(file_path)
        p_id = filename.split('-')[0]
        if p_id not in TARGETS: continue
        
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
                            responses_by_article[article_name] = json.loads(responses_json)
                        except: continue
        except: continue
        participant_data[p_id] = responses_by_article

    print("Answers for Problem Participants:")
    
    for article in ['crispr', 'semiconductors', 'uhi']:
        print(f"\n--- {article} ---")
        key = CURRENT_KEY[article]
        
        # Header
        print(f"{'Q':<3} {'Key':<3}", end="")
        for p_id in TARGETS:
            print(f" {p_id:<4}", end="")
        print()
        
        for q_idx in range(14):
            print(f"{q_idx:<3} {key[q_idx]:<3}", end="")
            for p_id in TARGETS:
                ans = participant_data.get(p_id, {}).get(article, {}).get(f"q{q_idx}", "-")
                mark = " "
                if ans != "-":
                    if ans == key[q_idx]: mark = "*" # Currently Correct
                print(f" {ans}{mark:<3}", end="")
            print()

if __name__ == "__main__":
    check_answers()
