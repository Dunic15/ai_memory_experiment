# AI Memory Experiment - AI Version

This is the **AI-enabled version** of the memory encoding experiment. This version includes AI summaries and all AI-related functionality.

## Features

- AI-generated summaries (integrated and segmented)
- AI trust questionnaire
- AI-related manipulation checks
- AI experience ratings
- Full experimental flow with AI interventions

## Running the Experiment

```bash
cd ai_experiment
flask --app app.py run
```

Or with a specific port:

```bash
flask --app app.py run --port 5000
```

## Experimental Flow

1. Consent
2. Language Selection
3. Instructions (with AI summary information)
4. Prior Knowledge Assessment
5. **AI Trust Questionnaire** ← AI-specific
6. Article 1 Reading (with AI summary access)
7. Break
8. Free Recall
9. Multiple Choice Questions
10. Post-Article Ratings (with AI experience questions)
11. Repeat for Articles 2 and 3
12. Manipulation Check (AI-related questions)
13. Debrief

## Data Logging

**Data is saved to:** `ai_experiment/experiment_data/`

This version logs:
- AI condition assignments (structure, timing)
- Summary viewing behavior (opens, clicks, time)
- AI trust scores
- AI experience ratings
- All standard experiment data

### Data Files Created:
- `experiment_data/participants.csv` - Participant demographics
- `experiment_data/P001_log.csv` - Complete data for participant P001
- `experiment_data/P002_log.csv` - Complete data for participant P002
- etc.

**All data is completely separate from the control experiment version.**

## Templates

All templates in this folder are the **AI-enabled versions**:
- `consent.html` - Includes AI information
- `instructions.html` - Includes AI summary warnings
- `post_article_ratings.html` - Includes AI experience section
- `manipulation_check.html` - Includes AI-related questions
