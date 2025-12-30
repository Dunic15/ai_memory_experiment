# Guide to Analyzing Participant Log CSV Files

**Goal:** Calculate performance metrics (Accuracy, AI Hallucination rates, etc.) from raw CSV logs.

## 0. Required Documents & Files

To perform a complete analysis, you need access to the following:

1.  **Participant Log Files** (`experiment_data/P{id}_{name}_{condition}_log.csv`)
    *   Contains all the raw data for a single participant.
2.  **Reference Data Tables** (Included in Section 6 of this guide)
    *   **Source Map**: To know if a question is "AI Summary" or "Article Only".
    *   **False Lure Map**: To identify hallucination checks.
3.  **(Optional) Analysis Script** (`ai_experiment/data_analysis/analyze_participant.py`)
    *   The Python code that automates this process. Useful for checking exact logic.
4.  **(Optional) Data Guide** (`ai_experiment/docs/DATA_GUIDE.md`)
    *   High-level overview of data storage and collection methods.

## 1. File Structure Overview

The log file is a **CSV (Comma Separated Values)** file where each row represents a specific event or phase in the experiment.

*   **Format**: Standard CSV.
*   **Encoding**: UTF-8 (important for handling non-English characters in names or responses).
*   **Key Columns**:
    *   `timestamp`: When the event occurred.
    *   `phase`: The type of event (e.g., `demographics`, `reading_behavior`, `mcq_responses`).
    *   **Variable Columns**: The remaining columns change meaning depending on the `phase`.

## 2. Key Phases & Data Extraction

To analyze a participant, you need to look for specific rows identified by the `phase` column.

### A. Demographics
*   **Phase**: `demographics`
*   **Location**: Usually the first few rows.
*   **Data Points**:
    *   `full_name` (Column 3)
    *   `profession` (Column 4)
    *   `age` (Column 5)
    *   `gender` (Column 6)
    *   `native_language` (Column 7)

### B. Randomization (Condition Assignment)
*   **Phase**: `randomization`
*   **Data Points**:
    *   `structure`: `integrated` vs `segmented` (Column 3).
    *   `timing_order`: The order of conditions (e.g., `["post_reading", "synchronous", "pre_reading"]`).
    *   `article_order`: The order of articles (e.g., `["uhi", "crispr", "semiconductors"]`).

### C. Reading Behavior
*   **Phase**: `reading_behavior`
*   **Event**: Look for rows where the 3rd column is `reading_complete`.
*   **Data Points**:
    *   `reading_time_ms`: Time spent reading the article (Column 5).
    *   `summary_time_ms`: Time spent viewing summaries (Column 6, relevant for synchronous mode).
    *   `scroll_depth`: Percentage of page scrolled (Column 8).

### D. MCQ Responses (The Most Important Section)
*   **Phase**: `mcq_responses`
*   **Frequency**: One row per article (3 rows total per participant).
*   **Data Points**:
    *   `article_key`: Which article this is for (e.g., `crispr`, `uhi`) (Column 4).
    *   `timing`: The condition (e.g., `synchronous`) (Column 5).
    *   **`details_json`**: This is usually the **13th column** (index 12). It contains a JSON string with detailed results for every question.

## 3. Calculating Metrics

Most performance metrics are derived from the `mcq_responses` rows. You will need to parse the `details_json` column.

### Step 1: Parse the JSON
The `details_json` cell looks like this:
```json
{
  "q0": {"is_correct": false, "question_index": 0, "participant_answer": 0, ...},
  "q1": {"is_correct": true, "question_index": 1, ...},
  ...
}
```

### Step 2: Calculate Basic Accuracy
For each article:
1.  Count the total number of questions (usually 14).
2.  Count how many have `"is_correct": true`.
    *   *Note*: The `is_correct` flag in the CSV is based on the answer key *at the time of the experiment*. If answer keys have been updated since, you should re-grade using the participant's answer index and the new key.
3.  **Total Accuracy** = (Total Correct / Total Questions) * 100.

### Step 3: Calculate Specific Metrics (AI Summary vs. Article Only)
To understand *how* the AI affected memory, questions are categorized by where the information was found. You need a **Source Map** to do this.

**Mapping Table (Question Index -> Source):**
*   **AI Summary Questions**: Information was present in the AI summary.
*   **Article Only Questions**: Information was *only* in the full text, not the summary.
*   **False Lure Questions**: Questions designed to test if the user hallucinates information.

*Example Map (CRISPR):*
*   Q1, Q2, Q4-Q8, Q10: `ai_summary`
*   Q9, Q11-Q13: `article`
*   Q3, Q14: `false_lure`

**Calculation:**
1.  Iterate through all questions in `details_json`.
2.  Check the `question_index` against the map.
3.  If it's an `ai_summary` question, add to the AI Summary counters.
4.  If it's an `article` question, add to the Article Only counters.
5.  Calculate accuracy for each group separately.

### Step 4: False Lure Analysis
This measures if participants "hallucinated" information suggested by the AI or common misconceptions.

1.  Identify **False Lure Questions** (e.g., Q3 and Q14 for CRISPR).
2.  **False Lure Accuracy**: Did they pick the *correct* answer? (High is good).
3.  **False Lures Selected**: Did they pick the specific *distractor* option? (Low is good).
    *   You need a **Lure Map** to know which option index (0, 1, 2, or 3) is the "trap".
    *   *Example*: For CRISPR Q3, Option B (index 1) might be the false lure. If `participant_answer == 1`, they fell for the lure.

## 4. Python Snippet for Analysis

Here is a simple pattern to read the file in Python:

```python
import csv
import json

with open('P233_log.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        phase = row[1]
        
        if phase == 'mcq_responses':
            # The details JSON is usually at index 12
            details = json.loads(row[12])
            
            for q_id, q_data in details.items():
                print(f"Question {q_data['question_index']}: Correct? {q_data['is_correct']}")
```

## 5. Common Pitfalls
1.  **JSON Parsing**: The JSON is stored as a string inside a CSV cell. Excel might mess up the formatting if you save it back. Always treat the raw file as read-only.
2.  **0-Indexing**: Question indices in the JSON (`question_index`) are 0-based (0-13), but in the paper/docs they might be referred to as Q1-Q14.
3.  **Variable Columns**: Don't assume Column 5 is always "Age". Check the `phase` first.

## 6. Reference Data Tables

Use these tables to map questions to their source and identify false lures.

### A. Source Mapping (Question Index -> Source)

| Article | AI Summary Questions (Indices) | Article Only Questions (Indices) | False Lure Questions (Indices) |
| :--- | :--- | :--- | :--- |
| **CRISPR** | 0, 1, 3, 4, 5, 6, 7, 9 | 8, 10, 11, 12 | 2, 13 |
| **Semiconductors** | 0, 1, 2, 3, 4, 5, 6, 9 | 7, 11, 12, 13 | 8, 10 |
| **UHI** | 0, 1, 2, 4, 5, 6, 7, 8 | 9, 11, 12, 13 | 3, 10 |

### B. False Lure Mapping

These are the specific options that represent the "AI Hallucination" or common misconception.

| Article | Question Index | False Lure Option Index | Description |
| :--- | :--- | :--- | :--- |
| **CRISPR** | 2 (Q3) | 1 (Option B) | DNA repair activity |
| **CRISPR** | 13 (Q14) | 0 (Option A) | Restore |
| **Semiconductors** | 8 (Q9) | 0 (Option A) | Quantum processors |
| **Semiconductors** | 10 (Q11) | 1 (Option B) | 46 silicon atoms |
| **UHI** | 3 (Q4) | 2 (Option C) | Photocatalytic roof tiles |
| **UHI** | 10 (Q11) | 2 (Option C) | Aged asphalt albedo 0.22 |

## 7. Analyzing Control Group (Non-AI)

For participants in the `control_no_ai` condition (e.g., P171), the analysis is slightly different but uses the **same metrics** for comparison:

1.  **AI Summary Accuracy**: Since they didn't see the summary, this metric measures their memory of the "gist" or main points (which the summary usually covers) based solely on reading the article.
2.  **False Lure Metrics**: Since they didn't see the AI, they weren't "lured" by a hallucination. However, you **must still calculate this** to establish a baseline.
    *   **Control Group Rate**: Represents the "natural" probability of choosing that specific wrong answer (distractor) due to confusion or guessing.
    *   **Experimental Group Rate**: Represents the probability of choosing it when the AI suggests it.
    *   **AI Hallucination Effect** = (Experimental Rate) - (Control Rate).

