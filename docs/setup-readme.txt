# AI-Assisted Memory Experiment Platform

Complete Flask-based web application for conducting your master's thesis experiment on AI-assisted human memory encoding.

## 📋 Quick Overview

- **Design**: 2×3 mixed factorial (Structure × Timing)
- **Duration**: ~105 minutes (1 hour 45 minutes) per session
- **Participants**: 36 total (18 per structure condition)
- **Articles**: 3 scientific texts (~1500 words each)
- **Data**: Automatic CSV logging of all interactions

## 🚀 Setup Instructions

### 1. Install Requirements

```bash
# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Flask
pip install flask
```

### 2. Create Project Structure

```
your_project/
├── app.py                  # Main Flask application (from artifact)
├── templates/              # HTML templates
│   ├── login.html
│   ├── consent.html
│   ├── prior_knowledge.html
│   ├── ai_trust.html
│   ├── reading.html
│   ├── test.html
│   ├── break.html
│   ├── manipulation_check.html
│   ├── debrief.html
│   └── excluded.html
├── static/                 # Static files (optional for CSS/JS)
└── experiment_data/        # Created automatically for CSV logs
```

### 3. Verify Setup

```bash
python setup-script.py
```

This script checks Python/Flask versions, the presence of all templates, creates `experiment_data/`, and writes a `config.py` with default timing values (including the two break durations).

### 4. Copy Files

1. Save the main Python code as `app.py`
2. Create `templates/` folder
3. Save each HTML template in the `templates/` folder:
   - `login.html`
   - `consent.html`
   - `prior_knowledge.html`
   - `ai_trust.html`
   - `reading.html`
   - `test.html`
   - `break.html`
   - `manipulation_check.html`
   - `debrief.html`
   - `excluded.html`

### 5. Run the Application

```bash
# Navigate to your project folder
cd your_project

# Run Flask
python app.py
```

The server will start at `http://127.0.0.1:5000`

## 📊 Experimental Flow

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
- Follow-up instructions

## 📁 Data Output

All data is saved to `experiment_data/` folder:

### Files Created:
1. **`participants.csv`** - Master list of all participants
2. **`P001_log.csv`, `P002_log.csv`, etc.** - Individual participant logs

### Logged Variables:
- Demographics
- Prior knowledge scores
- AI trust/dependence scores
- Reading behavior (time, scroll depth, summary views)
- Test responses (MCQ answers, confidence, free recall)
- Cognitive load ratings
- AI experience ratings
- Manipulation check responses

## 🎯 Experimental Conditions

### Between-Subject: AI Output Structure (A)
- **A1 - Integrated**: Paragraph format (~200-220 words)
- **A2 - Segmented**: Bullet points (8-10 items)

### Within-Subject: Summary Timing (B)
- **B1 - Synchronous**: Sidebar during reading
- **B2 - Pre-reading**: Summary → Article
- **B3 - Post-reading**: Article → Summary

Each participant:
- Gets ONE structure (A1 or A2) for all 3 articles
- Experiences ALL THREE timings (B1, B2, B3) - one per article
- Article order and timing order are counterbalanced

## 🔒 Quality Control Features

### Automatic Exclusion:
- Familiarity mean ≥ 6.0
- Term recognition count ≥ 8
- Perfect prior knowledge quiz score
- Participants meeting 2+ criteria are excluded

### Behavioral Logging:
- Reading time per article
- Summary viewing time
- Number of summary/text reviews
- Scroll depth percentage
- Answer times for each MCQ
- Page visibility changes

### Timing Enforcement:
- 12-minute soft limit (continue button appears)
- 15-minute hard cap (auto-advance)
- 30-second minimum for pre-reading summary
- Automatic timers for all timed tasks
- 5-minute pre-test break and 30-second inter-article break are enforced automatically

## 🛠️ Customization

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

## 📱 Technical Requirements

### For Participants:
- Laptop or desktop computer (mobile blocked)
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Full-screen mode capability
- Stable internet connection

### For Researcher:
- Python 3.7+
- Flask 2.0+
- CSV-compatible analysis software (Excel, R, Python)

## 🔍 Data Analysis

### Key Variables to Analyze:

**Performance:**
- Free recall quality (idea units, relational links)
- MCQ accuracy (overall, summary-based, text-based)
- Delayed retention (follow-up session)

**Metacognition:**
- Confidence ratings
- Calibration error (confidence - accuracy)

**Behavior:**
- Reading time distribution
- Summary reliance patterns
- Scroll depth and engagement

**Experience:**
- Cognitive load ratings
- AI trust and satisfaction
- Manipulation check confirmations

## 🐛 Troubleshooting

### Port Already in Use:
```bash
# Use a different port
python app.py --port 5001
```

### Templates Not Found:
- Ensure `templates/` folder is in same directory as `app.py`
- Check file names match exactly (case-sensitive)

### Data Not Saving:
- Check write permissions in project directory
- Verify `experiment_data/` folder was created
- Look for error messages in console

## 📧 Support & Questions

For issues or questions about:
- **Experimental design**: Refer to your research documents
- **Technical setup**: Check Flask documentation
- **Data analysis**: Consult your supervisor or stats advisor

## 📄 Citation

If you use this platform, please cite your thesis and acknowledge the experimental design based on:
- Craik & Lockhart (1972) - Levels of Processing
- Baddeley (2012) - Working Memory Model
- Risko & Gilbert (2016) - Cognitive Offloading Theory

---

**Good luck with your master's thesis! 🎓**

Built with Flask and designed for rigorous cognitive psychology research.