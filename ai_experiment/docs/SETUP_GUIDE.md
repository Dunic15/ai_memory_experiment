# Setup & Quick Reference Guide

Complete setup instructions and quick reference for the AI memory experiment.

## Quick Start (5 minutes)

```bash
# 1. Create project folder
mkdir ai_memory_experiment
cd ai_memory_experiment

# 2. Install Flask
pip install flask

# 3. Create folder structure
mkdir templates
mkdir static
mkdir experiment_data

# 4. Save files (get from artifacts)
# - Save app.py in main folder
# - Save all .html files in templates/ folder

# 5. Run setup check
python setup-script.py

# 6. Start server
python app.py
```

## File Checklist

```
ai_memory_experiment/
├── app.py ✓
├── setup-script.py ✓
├── README.md ✓
├── templates/
│   ├── login.html ✓
│   ├── consent.html ✓
│   ├── prior_knowledge.html ✓
│   ├── ai_trust.html ✓
│   ├── reading.html ✓
│   ├── test.html ✓
│   ├── break.html ✓
│   ├── manipulation_check.html ✓
│   ├── debrief.html ✓
│   └── excluded.html ✓
└── experiment_data/ (auto-created)
```

## Experimental Conditions Quick Reference

### Structure (Between-Subject)
| Condition | Format | Content |
|-----------|--------|---------|
| **A1 - Integrated** | Single paragraph | ~200-220 words, coherent narrative |
| **A2 - Segmented** | Bullet points | 8-10 bullets, ~15-20 words each |

### Timing (Within-Subject)
| Condition | When | How |
|-----------|------|-----|
| **B1 - Synchronous** | During reading | Sidebar (toggleable) |
| **B2 - Pre-reading** | Before article | 90s min, can revisit |
| **B3 - Post-reading** | After article | 10 min article → 2 min summary |

• Flow note: After each reading → 5-min break → test; after each test → 30s break → next reading.

## Critical Timing

| Phase | Duration |
|-------|----------|
| Reading (soft limit) | 12 min |
| Reading (hard cap) | 15 min |
| Pre-reading summary | 90s minimum |
| Free recall | 3 min |
| MCQs | 7 min |
| Break (after reading, pre-test) | 5 min |
| Break (after test, before next article) | 30 s |
| Total per article | ~25–27 min |
| **Full session** | **~105 min (1 hour 45 minutes)** |

## Common Commands

```bash
# Start server
python app.py

# Run on different port
# (edit app.py, change port=5000 to port=5001)

# Check setup
python setup-script.py

# Stop server
Ctrl+C

# View data
# Open experiment_data/ folder
# Import CSVs to Excel, R, or Python
```

## URLs

- **Start**: http://127.0.0.1:5000
- **Check participants**: Open `experiment_data/participants.csv`
- **Individual logs**: `experiment_data/P001_log.csv`, etc.

## Data Files

### Generated automatically:
- `experiment_data/participants.csv` - Master participant list
- `experiment_data/P001_log.csv` - Individual logs per participant

### Key columns to analyze:
```csv
Phase,
timestamp,
familiarity_mean,
prior_knowledge_score,
ai_trust_score,
structure_condition,
timing_condition,
total_reading_time,
summary_view_time,
mcq_accuracy,
confidence_mean,
cognitive_load,
manipulation_check_scores
```

## Participant Instructions (to read aloud)

> "Welcome! This study takes about 105 minutes (1 hour 45 minutes). You'll:
> 1. Read 3 scientific articles with AI-generated summaries
> 2. Answer questions about each article
> 3. Rate your experience
> 
> Requirements:
> - Use a computer (no phones)
> - Stay in full-screen mode
> - Avoid distractions
> 
> Your ID will be generated automatically. Ready to begin?"

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **Port in use** | Change port in app.py line: `app.run(port=5001)` |
| **Templates not found** | Ensure templates/ folder is next to app.py |
| **No data saving** | Check experiment_data/ folder exists |
| **Fullscreen fails** | Some browsers block it - instruct participants to press F11 |
| **Timer not working** | Check JavaScript console for errors |

## Randomization Logic

```
Participant → Assigned to:
1. ONE structure (A1 or A2) for all articles
2. THREE timings (B1, B2, B3) - counterbalanced across articles

Example:
- P001: A1-Integrated, [B1-uhi, B2-crispr, B3-semiconductors]
- P002: A2-Segmented, [B2-crispr, B3-semiconductors, B1-uhi]
```

## Before Running Your Study

- [ ] Test with 2-3 pilot participants
- [ ] Check all timers work correctly
- [ ] Verify data saves properly
- [ ] Test on different browsers
- [ ] Prepare quiet testing environment
- [ ] Have backup plan for technical issues
- [ ] Print participant instructions

## Data Analysis Quick Start

```python
import pandas as pd

# Load participant data
participants = pd.read_csv('experiment_data/participants.csv')

# Load individual logs
p001 = pd.read_csv('experiment_data/P001_log.csv')

# Common analyses
print(participants['structure_condition'].value_counts())
print(participants['ai_trust_score'].describe())

# MCQ accuracy by condition
# (extract from test_responses phase rows)
```

## Customization

### To Modify Articles:
Edit the `ARTICLES` dictionary in `app.py`:
```python
ARTICLES = {
    'article_key': {
        'title': 'Your Title',
        'text': '''Your article text...''',
        'summary_integrated': '''Paragraph summary...''',
        'summary_segmented': '''• Bullet 1\n• Bullet 2...''',
        'questions': [
            {'q': 'Question?', 'options': [...], 'correct': 0},
            # ... more questions
        ]
    }
}
```

### To Change Timing:
Modify constants in `config.py` (created by `setup-script.py`):
```python
READING_TIME_SOFT_LIMIT = 12 * 60 * 1000  # 12 minutes
READING_TIME_HARD_CAP   = 15 * 60 * 1000  # 15 minutes
PRE_READING_MIN_TIME    = 90 * 1000       # 90 seconds
RECALL_TIME_LIMIT       = 3 * 60 * 1000   # 3 minutes
MCQ_TIME_LIMIT          = 7 * 60 * 1000   # 7 minutes
BREAK_AFTER_READING_MS  = 5 * 60 * 1000   # 5 minutes (pre-test break)
BREAK_BETWEEN_ARTICLES_MS = 30 * 1000     # 30 seconds (after-test break)
```

## Technical Requirements

### For Participants:
- Laptop or desktop computer (mobile blocked)
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Full-screen mode capability
- Stable internet connection

### For Researcher:
- Python 3.7+
- Flask 2.0+
- CSV-compatible analysis software (Excel, R, Python)

## Experimental Flow

### Phase 1: Setup & Screening (~10 min)
1. **Login** - Demographics collection
2. **Consent** - Study information and agreement
3. **Prior Knowledge** - 4-part assessment with auto-exclusion
4. **AI Trust** - Technology attitude and proficiency

### Phase 2: Reading & Testing (~70 min)
Repeated 3 times (one per article):
1. **Reading Phase** (≤12 min, 15 min cap)
   - **B1 Synchronous**: Summary in sidebar during reading
   - **B2 Pre-reading**: Summary first (90s min), then article
   - **B3 Post-reading**: Article first (10 min), then summary (2 min)

2. **Test Phase** (~13 min)
   - Free recall (3 min)
   - 15 MCQs with confidence ratings (7 min)
   - Cognitive load & AI satisfaction scales (3 min)

3. **Break after reading (pre-test)** — 5 min
4. **Break after test (before next article)** — 30 s

### Phase 3: Manipulation Check (~3-4 min)
- Semantic coherence rating
- Relational connectivity rating
- Memory strategy choice

### Phase 4: Debrief (~2 min)
- Thank you message

## Support

- **Technical issues**: Check README.md
- **Experimental design**: Review research documents
- **Data analysis**: Consult supervisor
- **Data interpretation**: See `DATA_GUIDE.md`

---

**Ready? Run `python app.py` and open http://127.0.0.1:5000** 🎯

