import json

# P188's MCQ data extracted from the experiment log file
# From: P188-张心旭-NON-AI_log.csv

# Article 0: Semiconductors
semiconductors_responses = {"q0": 1, "q1": 0, "q2": 0, "q3": 3, "q4": 2, "q5": 2, "q6": 0, "q7": 1, "q8": 1, "q9": 2, "q10": 1, "q11": 2, "q12": 1, "q13": 1}
semiconductors_correct = 6
semiconductors_total = 14
semiconductors_accuracy = 42.86

# Article 1: CRISPR (first occurrence - all three have identical responses)
crispr_responses = {"q0": 0, "q1": 2, "q2": 1, "q3": 2, "q4": 1, "q5": 0, "q6": 0, "q7": 2, "q8": 3, "q9": 1, "q10": 1, "q11": 1, "q12": 2, "q13": 2}
crispr_correct = 6
crispr_total = 14
crispr_accuracy = 42.86

# Article 2: UHI
uhi_responses = {"q0": 1, "q1": 3, "q2": 1, "q3": 2, "q4": 2, "q5": 3, "q6": 0, "q7": 1, "q8": 2, "q9": 2, "q10": 2, "q11": 0, "q12": 1, "q13": 0}
uhi_correct = 6
uhi_total = 14
uhi_accuracy = 42.86

# Calculate overall
total_correct = semiconductors_correct + crispr_correct + uhi_correct
total_questions = semiconductors_total + crispr_total + uhi_total
overall_accuracy = (total_correct / total_questions) * 100

print("=" * 70)
print("P188 MCQ RECALCULATION FROM EXPERIMENT DATA")
print("Participant: 张心旭 (Control Group - No AI)")
print("=" * 70)
print()

print("Article 0: SEMICONDUCTORS")
print(f"  Responses: {semiconductors_responses}")
print(f"  Correct: {semiconductors_correct}/{semiconductors_total}")
print(f"  Accuracy: {semiconductors_accuracy:.2f}%")
print()

print("Article 1: CRISPR")
print(f"  Responses: {crispr_responses}")
print(f"  Correct: {crispr_correct}/{crispr_total}")
print(f"  Accuracy: {crispr_accuracy:.2f}%")
print(f"  Note: CRISPR article had 3 duplicate log entries with identical responses")
print()

print("Article 2: UHI")
print(f"  Responses: {uhi_responses}")
print(f"  Correct: {uhi_correct}/{uhi_total}")
print(f"  Accuracy: {uhi_accuracy:.2f}%")
print()

print("-" * 70)
print("OVERALL MCQ PERFORMANCE")
print(f"  Total Correct: {total_correct}/{total_questions}")
print(f"  Overall Accuracy: {overall_accuracy:.2f}%")
print("=" * 70)
print()

print("DATA SOURCE: /no_ai_experiment/experiment_data/P188-张心旭-NON-AI_log.csv")
print("Log entries:")
print("  - Semiconductors: 2025-12-18T16:20:49.928344")
print("  - CRISPR: 2025-12-18T16:34:21.931352 (+ 2 duplicates)")
print("  - UHI: 2025-12-18T16:51:50.443540")
