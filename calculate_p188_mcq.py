import json

# P188's MCQ data from the log file
# Note: Article 1 (CRISPR) has duplicate entries at timestamps 16:34:21, 16:34:22, 16:34:22
# We'll only count one set of responses per article

articles_data = [
    {
        "article": "semiconductors",
        "responses": {"q0": 1, "q1": 1, "q2": 0, "q3": 3, "q4": 2, "q5": 2, "q6": 0, "q7": 1, "q8": 1, "q9": 2, "q10": 1, "q11": 2, "q12": 1, "q13": 1},
        "accuracy": 50.0,
        "correct": 7,
        "total": 14
    },
    {
        "article": "crispr",
        "responses": {"q0": 0, "q1": 2, "q2": 1, "q3": 2, "q4": 1, "q5": 0, "q6": 0, "q7": 2, "q8": 3, "q9": 1, "q10": 1, "q11": 1, "q12": 2, "q13": 2},
        "accuracy": 42.86,
        "correct": 6,
        "total": 14
    },
    {
        "article": "uhi",
        "responses": {"q0": 1, "q1": 3, "q2": 1, "q3": 2, "q4": 2, "q5": 3, "q6": 0, "q7": 1, "q8": 2, "q9": 2, "q10": 2, "q11": 0, "q12": 0, "q13": 0},
        "accuracy": 50.0,
        "correct": 7,
        "total": 14
    }
]

print("=" * 60)
print("MCQ ACCURACY CALCULATION FOR P188 (张心旭)")
print("=" * 60)
print("\nControl Group (No AI)")
print()

total_correct = 0
total_questions = 0

for i, article in enumerate(articles_data):
    print(f"Article {i}: {article['article'].upper()}")
    print(f"  Correct: {article['correct']}/{article['total']}")
    print(f"  Accuracy: {article['accuracy']:.2f}%")
    print()
    
    total_correct += article['correct']
    total_questions += article['total']

print("-" * 60)
print(f"OVERALL MCQ ACCURACY:")
print(f"  Total Correct: {total_correct}/{total_questions}")
print(f"  Overall Accuracy: {(total_correct/total_questions)*100:.2f}%")
print("=" * 60)

print("\nNote:")
print("- Article 1 (CRISPR) had duplicate log entries at 16:34:21, 16:34:22, 16:34:22")
print("- Only one set of responses per article was counted (deduplicated)")
print("- Original question count would have been 70 (with duplicates)")
print("- Corrected question count: 42 (14 questions × 3 articles)")
