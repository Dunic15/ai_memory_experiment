# CSV Data Interpretation Guide

This document explains how to interpret the data collected in the experiment CSV files, with special focus on understanding the time tracking and all data fields.

## File Structure

### 1. `participants.csv`
Master file containing participant demographics and basic information.

**Columns:**
- `participant_id`: Unique identifier (P001, P002, etc.)
- `timestamp`: When the participant started the experiment (ISO format)
- `full_name`: Participant's name
- `profession`: Participant's profession
- `age`: Participant's age
- `gender`: Participant's gender
- `native_language`: Participant's native language

### 2. `{participant_id}_log.csv`
Detailed log file for each participant containing all phase data.

**Structure:** Each row represents one event/phase with:
- `timestamp`: When the event occurred (ISO format)
- `phase`: The phase name (see Phase Types below)
- Additional columns: Phase-specific data fields

## Phase Types and Data Fields

### 1. Demographics Phase
**Phase:** `demographics`

**Fields:**
- `full_name`: Participant's name
- `profession`: Participant's profession
- `age`: Participant's age
- `gender`: Participant's gender
- `native_language`: Participant's native language

### 2. Consent Phase
**Phase:** `consent`

**Fields:**
- `consent_given`: Whether consent was provided (true/false)

### 3. Prior Knowledge Phase
**Phase:** `prior_knowledge`

**Fields:**
- `familiarity_scores`: JSON string of familiarity ratings (1-7 scale) for technical terms
- `recognition_responses`: JSON string of Yes/No recognition responses
- `quiz_scores`: JSON string of quiz answers
- `total_score`: Total quiz score

### 4. AI Trust Phase
**Phase:** `ai_trust`

**Fields:**
- `ai_trust_score`: Average trust rating (1-7 scale)
- `ai_dependence_score`: Average dependence rating (1-7 scale)
- `tech_skill_score`: Average technical skill rating (1-7 scale)
- `open_reflection`: Text response with three questions:
  - Q1: Frequency of AI tool use
  - Q2: Specific AI tools used
  - Q3: Tasks/activities using AI tools

### 5. Randomization Phase
**Phase:** `randomization`

**Fields:**
- `structure`: Summary structure condition (`integrated` or `segmented`)
- `timing_order`: JSON array of timing conditions for each article (`synchronous`, `pre_reading`, `post_reading`)
- `article_order`: JSON array of article keys in order (`uhi`, `crispr`, `semiconductors`)

### 6. Summary Viewing Phase ⭐ NEW
**Phase:** `summary_viewing`

**Fields:**
- `article_num`: Article number (0, 1, or 2)
- `article_key`: Article identifier (`uhi`, `crispr`, or `semiconductors`)
- `mode`: When summary was viewed (`pre_reading` or `post_reading`)
- `structure`: Summary structure (`integrated` or `segmented`)
- `time_spent_ms`: **Total time spent viewing the summary in milliseconds**
- `time_spent_seconds`: **Total time spent viewing the summary in seconds** (for easier reading)
- `timestamp`: When the summary viewing ended

**How to Interpret Summary Viewing Time:**
- This measures how long participants actively viewed the AI summary
- Time is tracked only when the page is visible (pauses when tab is hidden)
- `time_spent_seconds` is the primary metric for analysis
- Compare across conditions:
  - `pre_reading` vs `post_reading` modes
  - `integrated` vs `segmented` structures
  - Different articles

**Example Analysis:**
```python
import pandas as pd
import json

# Load data
df = pd.read_csv('P001_log.csv')

# Filter summary viewing data
summary_data = df[df['phase'] == 'summary_viewing']

# Calculate average viewing time by condition
avg_time = summary_data.groupby(['mode', 'structure'])['time_spent_seconds'].mean()
print(avg_time)
```

### 7. Reading Behavior Phase
**Phase:** `reading_behavior`

**Fields:**
- `article_num`: Article number (0, 1, or 2)
- `article_key`: Article identifier
- `timing`: Timing condition for this article
- `event`: Type of event (e.g., `reading_complete`)
- `totalReadingTime`: Total time spent reading (milliseconds)
- `summaryViewTime`: Time spent viewing summary during reading (if synchronous mode)
- `summaryViews`: Number of times summary was viewed
- `scrollDepth`: Maximum scroll depth reached (percentage)

### 8. Recall Response Phase
**Phase:** `recall_response`

**Fields:**
- `article_num`: Article number (0, 1, or 2)
- `article_key`: Article identifier
- `timing`: Timing condition
- `recall_text`: Free recall text (bullet points separated by `\n`)
- `sentence_count`: Number of bullet points/sentences
- `word_count`: Total word count
- `char_count`: Total character count
- `confidence`: Confidence rating (1-7 scale)
- `perceived_difficulty`: Difficulty rating (1-7 scale)
- `time_spent_ms`: Time spent on recall task (milliseconds)
- `paste_attempts`: Number of paste attempts (should be 0)
- `over_limit`: Whether time limit was exceeded

### 9. MCQ Responses Phase
**Phase:** `mcq_responses`

**Fields:**
- `article_num`: Article number (0, 1, or 2)
- `article_key`: Article identifier
- `timing`: Timing condition
- `mcq_answers`: JSON string of answers
  - Format: `{"q0": 1, "q1": 2, ...}` where values are option indices (0-based)
  - Example: `{"q0": 1, "q1": 0, "q2": 2}` means:
    - Question 1: Selected option 2 (index 1)
    - Question 2: Selected option 1 (index 0)
    - Question 3: Selected option 3 (index 2)

**How to Interpret MCQ Answers:**
```python
import pandas as pd
import json

# Load data
df = pd.read_csv('P001_log.csv')

# Filter MCQ responses
mcq_data = df[df['phase'] == 'mcq_responses']

# Parse JSON answers
for idx, row in mcq_data.iterrows():
    answers = json.loads(row['mcq_answers'])
    article = row['article_key']
    print(f"Article: {article}")
    for q_num, option_idx in answers.items():
        print(f"  Question {int(q_num[1:])+1}: Selected option {option_idx+1}")
```

### 10. Manipulation Check Phase
**Phase:** `manipulation_check`

**Fields:**
- Varies based on manipulation check questions
- Typically includes awareness questions about experimental conditions

## Key Metrics to Analyze

### 1. Summary Viewing Time
**Purpose:** Measure attention and engagement with AI summaries

**Metrics:**
- Average time per condition (pre_reading vs post_reading)
- Average time per structure (integrated vs segmented)
- Correlation with recall performance
- Correlation with MCQ performance

**Analysis Example:**
```python
import pandas as pd
import numpy as np

# Load all participant logs
participants = ['P001', 'P002', 'P003']  # Add all participant IDs
all_summary_data = []

for pid in participants:
    df = pd.read_csv(f'experiment_data/{pid}_log.csv')
    summary = df[df['phase'] == 'summary_viewing']
    all_summary_data.append(summary)

summary_df = pd.concat(all_summary_data)

# Compare viewing times
pre_reading = summary_df[summary_df['mode'] == 'pre_reading']['time_spent_seconds']
post_reading = summary_df[summary_df['mode'] == 'post_reading']['time_spent_seconds']

print(f"Pre-reading average: {pre_reading.mean():.2f} seconds")
print(f"Post-reading average: {post_reading.mean():.2f} seconds")

# Compare structures
integrated = summary_df[summary_df['structure'] == 'integrated']['time_spent_seconds']
segmented = summary_df[summary_df['structure'] == 'segmented']['time_spent_seconds']

print(f"Integrated average: {integrated.mean():.2f} seconds")
print(f"Segmented average: {segmented.mean():.2f} seconds")
```

### 2. Recall Performance
**Metrics:**
- Sentence count (quantity)
- Word count (detail)
- Confidence ratings
- Perceived difficulty
- Time spent

### 3. MCQ Performance
**Metrics:**
- Correct answer rate
- Performance by article
- Performance by timing condition
- Performance by structure condition

### 4. Reading Behavior
**Metrics:**
- Total reading time
- Scroll depth
- Summary views (synchronous mode)
- Summary view time (synchronous mode)

## Data Quality Checks

### 1. Summary Viewing Time Validation
- Check for unusually short times (< 10 seconds) - may indicate participants skipped
- Check for unusually long times (> 5 minutes) - may indicate participants left page open
- Compare with reading times to ensure consistency

### 2. Recall Quality Checks
- `paste_attempts` should be 0 (paste is blocked)
- `sentence_count` should be >= 1
- `time_spent_ms` should be within reasonable bounds (typically 30-180 seconds)

### 3. MCQ Completeness
- All 15 questions should have answers (check for missing `q0` through `q14`)
- Option indices should be 0-3 (4 options per question)

## Common Analysis Workflows

### Workflow 1: Summary Viewing Time Analysis
1. Load all participant log files
2. Filter for `summary_viewing` phase
3. Group by `mode` and `structure`
4. Calculate descriptive statistics (mean, median, std)
5. Perform statistical tests (t-tests, ANOVA) if needed
6. Visualize with box plots or bar charts

### Workflow 2: Recall-MCQ Relationship
1. Load recall and MCQ data
2. Match by `article_num` and `participant_id`
3. Calculate recall metrics (sentence_count, word_count)
4. Calculate MCQ accuracy
5. Correlate recall metrics with MCQ performance
6. Check if summary viewing time moderates the relationship

### Workflow 3: Condition Comparison
1. Load randomization data to get condition assignments
2. Merge with performance data (recall, MCQ)
3. Compare performance across:
   - Timing conditions (synchronous, pre_reading, post_reading)
   - Structure conditions (integrated, segmented)
4. Include summary viewing time as a covariate

## Exporting and Sharing Data

### Export All Data
Use the admin export endpoint:
```
/admin/export?key=YOUR_ADMIN_KEY
```

This downloads a ZIP file containing:
- `participants.csv`
- All `PXXX_log.csv` files
- `translations.json` (if available)

### Manual Export
Simply copy the `experiment_data/` folder from your server/deployment.

## Notes

- All timestamps are in ISO format (YYYY-MM-DDTHH:MM:SS.ssssss)
- Time values are in milliseconds unless specified as seconds
- JSON fields need to be parsed before analysis
- Participant IDs are sequential (P001, P002, etc.)
- Article numbers are 0-indexed (0, 1, 2) but represent articles 1, 2, 3

## Troubleshooting

### Missing Summary Viewing Data
- Check if the `/log_summary_viewing` endpoint was called
- Verify JavaScript is enabled (required for time tracking)
- Check browser console for errors

### Inconsistent Time Data
- Time tracking pauses when page is hidden (by design)
- Very short times may indicate page was closed immediately
- Very long times may indicate page was left open

### MCQ Answer Parsing Issues
- MCQ answers are stored as JSON strings
- Use `json.loads()` to parse
- Option indices are 0-based (0, 1, 2, 3)
- Question numbers in JSON are 0-based (q0, q1, ..., q14)

## Additional Resources

- See `DATA_STORAGE_ANALYSIS.md` for storage architecture details
- See `DATA_ANALYSIS_FEATURES.md` for export features
- See main `README.md` for experiment overview

