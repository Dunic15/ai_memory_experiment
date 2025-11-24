# AI Memory Experiment - Control Version (No AI)

This is the **control version** of the memory encoding experiment. This version contains **NO AI summaries or AI-related functionality**.

## Features

- No AI summaries
- No AI trust questionnaire
- No AI-related manipulation checks
- No AI experience ratings
- Clean experimental flow without AI interventions

## Running the Experiment

```bash
cd no_ai_experiment
flask --app app_control.py run
```

Or with a specific port:

```bash
flask --app app_control.py run --port 5001
```

Or using Python directly:

```bash
cd no_ai_experiment
python3 app_control.py
```

## Experimental Flow

1. Consent
2. Language Selection
3. Instructions (no AI information)
4. Prior Knowledge Assessment
5. Article 1 Reading (no AI summaries)
6. Break
7. Free Recall
8. Multiple Choice Questions
9. Post-Article Ratings (no AI questions)
10. Repeat for Articles 2 and 3
11. Manipulation Check (article coherence questions only)
12. Debrief

## Data Logging

**Data is saved to:** `no_ai_experiment/experiment_data/`

This version logs **only**:
- Participant ID
- Article order
- Reading times
- Recall responses
- MCQ answers
- Memory confidence
- General task ratings

**No AI-related data is logged.**

### Data Files Created:
- `experiment_data/participants.csv` - Participant demographics
- `experiment_data/P001_log.csv` - Complete data for participant P001
- `experiment_data/P002_log.csv` - Complete data for participant P002
- etc.

**All data is completely separate from the AI experiment version.**

## Templates

All templates in this folder are the **control versions** (no AI references):
- `consent.html` - "Reading and Memory Study" (no AI info)
- `instructions.html` - No AI summary warnings
- `post_article_ratings.html` - No AI experience section
- `manipulation_check.html` - Article coherence questions only

## Differences from AI Version

- Removed all AI-related routes (`/ai_summary`, `/ai_trust`, etc.)
- Removed AI condition randomization
- Removed AI session variables
- Simplified experimental flow
- Clean data logging (no AI fields)
