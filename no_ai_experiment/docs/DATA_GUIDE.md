# Data Storage, Analysis & Interpretation Guide

Complete guide to data collection, storage, analysis, and interpretation for the AI memory experiment.

## Table of Contents

1. [Data Storage](#data-storage)
2. [Data Collection](#data-collection)
3. [Data Interpretation](#data-interpretation)
4. [Data Analysis](#data-analysis)
5. [Analysis Tools & Software Options](#analysis-tools--software-options)
6. [Admin Features](#admin-features)
7. [Recommendations](#recommendations)

---

## Data Storage

### Current System: CSV Files

**Location:** `experiment_data/` folder

**Files:**
1. **`participants.csv`** - Master file with all participant demographics
2. **`{participant_id}_log.csv`** - Detailed log for each participant

### What Gets Saved

#### 1. Participants File (`participants.csv`)
- `participant_id` (P001, P002, etc.)
- `timestamp` (when they started)
- `full_name`, `profession`, `age`, `gender`, `native_language`

#### 2. Participant Log File (`PXXX_log.csv`)
Each row represents one event/phase:
- Demographics, consent, prior knowledge, AI trust
- Randomization (article order, timing mode, summary structure)
- Reading behavior (time spent, scroll depth, summary views)
- Recall responses (text, sentence counts, confidence ratings)
- MCQ responses (answers, correctness)
- Manipulation check (verification questions)

### Data Format

- **CSV files** (simple, readable in Excel/Google Sheets)
- UTF-8 encoding (supports all languages)
- One log file per participant
- Easy to analyze with Python, R, or spreadsheet software

### Storage Options Assessment

#### Current CSV Approach ✅ (Recommended for < 500 participants)

**Pros:**
- Simple & readable - Easy to open in Excel/Google Sheets
- No database setup - Works immediately
- Good for small-medium studies - Perfect for dozens to hundreds of participants
- Easy backup - Just copy the folder
- Human-readable - Can inspect data directly
- Easy to share - Send CSV files to collaborators
- Works with all analysis tools - Python, R, Excel, SPSS

**Cons:**
- Not ideal for very large studies - Gets slower with thousands of participants
- No concurrent write protection - Rare issue, but possible with multiple simultaneous submissions
- No built-in data validation - Need to check data quality manually
- No real-time queries - Need to load files into analysis tools
- Cloud deployment - Data stored on server, need to export regularly

**Recommendation:** Perfect for experiments with < 500 participants

#### Alternative Options (If Needed)

**SQLite Database** (Recommended for 500-5000 participants)
- More efficient for larger datasets
- Built-in data integrity
- SQL queries (complex analysis)
- Still file-based (easy backup)
- Implementation effort: Medium (2-3 days)

**PostgreSQL/MySQL** (Recommended for 5000+ participants or cloud deployment)
- Highly scalable (millions of records)
- Concurrent access safe
- Advanced features (transactions, replication)
- Best for cloud deployment
- Implementation effort: High (1 week)

**Cloud Storage** (AWS S3, Google Cloud Storage)
- Persistent storage (survives server restarts)
- Easy backup
- Can still use CSV format
- Implementation effort: Low (1 day)

---

## Data Collection

### What You Can Measure

#### 1. Reading Behavior
- Reading time per article (milliseconds)
- Scroll depth (percentage, 0-100%)
- Summary views (synchronous mode)
- Summary viewing time during reading
- Page visibility changes

#### 2. AI Summary Engagement ⭐
- **Time spent viewing summary** (`time_spent_seconds` in `summary_viewing` phase)
- Pre-reading vs post-reading comparison
- Integrated vs segmented comparison
- Correlation with performance

#### 3. Recall Performance
- Free recall text (qualitative analysis)
- Sentence/word/character counts
- Confidence ratings (1-7 scale)
- Perceived difficulty (1-7 scale)
- Time spent on recall (milliseconds)
- Paste attempts (data quality indicator)

#### 4. MCQ Performance
- Correct/incorrect answers (0-3 option indices)
- Performance by article
- Performance by condition (timing, structure)
- Relationship to summary viewing time
- False memory questions (Q10 for each article)

#### 5. AI Trust & Demographics
- Trust scores (1-7 scale)
- AI tool usage patterns
- Participant characteristics
- Correlation with performance

---

## Data Interpretation

### File Structure

#### 1. `participants.csv`
Master file containing participant demographics and basic information.

**Columns:**
- `participant_id`: Unique identifier (P001, P002, etc.)
- `timestamp`: When the participant started the experiment (ISO format)
- `full_name`: Participant's name
- `profession`: Participant's profession
- `age`: Participant's age
- `gender`: Participant's gender
- `native_language`: Participant's native language

#### 2. `{participant_id}_log.csv`
Detailed log file for each participant containing all phase data.

**Structure:** Each row represents one event/phase with:
- `timestamp`: When the event occurred (ISO format)
- `phase`: The phase name (see Phase Types below)
- Additional columns: Phase-specific data fields

### Phase Types and Data Fields

#### 1. Demographics Phase
**Phase:** `demographics`

**Fields:**
- `full_name`, `profession`, `age`, `gender`, `native_language`

#### 2. Consent Phase
**Phase:** `consent`

**Fields:**
- `consent_given`: Whether consent was provided (true/false)

#### 3. Prior Knowledge Phase
**Phase:** `prior_knowledge`

**Fields:**
- `familiarity`: Average familiarity rating (1-7 scale)
- `recognition`: Number of recognized terms (0-10)
- `quiz_score`: Quiz score (0-5 scale)
- `excluded`: Whether participant was excluded (True/False)

#### 4. AI Trust Phase
**Phase:** `ai_trust`

**Fields:**
- `trust_score`: Average trust rating (1-7 scale)
- `dependence_score`: Average dependence rating (1-7 scale)
- `skill_score`: Average technical skill rating (1-7 scale)
- `reflection`: Text response with three questions:
  - Q1: Frequency of AI tool use
  - Q2: Specific AI tools used
  - Q3: Tasks/activities using AI tools

#### 5. Randomization Phase
**Phase:** `randomization`

**Fields:**
- `structure`: Summary structure condition (`integrated` or `segmented`)
- `timing_order`: JSON array of timing conditions (`synchronous`, `pre_reading`, `post_reading`)
- `article_order`: JSON array of article keys (`uhi`, `crispr`, `semiconductors`)

#### 6. Summary Viewing Phase ⭐
**Phase:** `summary_viewing`

**Fields:**
- `article_num`: Article number (0, 1, or 2)
- `article_key`: Article identifier (`uhi`, `crispr`, or `semiconductors`)
- `mode`: When summary was viewed (`pre_reading` or `post_reading`)
- `structure`: Summary structure (`integrated` or `segmented`)
- `time_spent_ms`: Total time spent viewing the summary in milliseconds
- `time_spent_seconds`: Total time spent viewing the summary in seconds (for easier reading)
- `timestamp`: When the summary viewing ended

**How to Interpret Summary Viewing Time:**
- This measures how long participants actively viewed the AI summary
- Time is tracked only when the page is visible (pauses when tab is hidden)
- `time_spent_seconds` is the primary metric for analysis
- Compare across conditions:
  - `pre_reading` vs `post_reading` modes
  - `integrated` vs `segmented` structures
  - Different articles

#### 7. Reading Behavior Phase
**Phase:** `reading_behavior`

**Fields:**
- `article_num`: Article number (0, 1, or 2)
- `article_key`: Article identifier
- `timing`: Timing condition for this article
- `event`: Type of event (e.g., `reading_complete`, `visibility_change`)
- `reading_time_ms`: Total time spent reading (milliseconds)
- `scroll_depth`: Maximum scroll depth reached (percentage, 0-100%)
- `summary_views`: Number of times summary was viewed (synchronous mode)

#### 8. Recall Response Phase
**Phase:** `recall_response`

**Fields:**
- `article_num`: Article number (0, 1, or 2)
- `article_key`: Article identifier
- `timing`: Timing condition
- `recall_text`: Free recall text (may contain newlines)
- `sentence_count`: Number of sentences/bullet points
- `word_count`: Total word count
- `character_count`: Total character count
- `confidence`: Confidence rating (1-7 scale)
- `difficulty`: Perceived difficulty rating (1-7 scale)
- `time_spent_ms`: Time spent on recall task (milliseconds)
- `paste_attempts`: Number of paste attempts (should be 0)
- `over_limit`: Whether time limit was exceeded (True/False)

#### 9. MCQ Responses Phase
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

**Correct Answers Reference:**
- **Urban Heat Islands (UHI)**: [1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 1, 1, 1, 1, 1]
- **CRISPR**: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1]
- **Semiconductors**: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1]

These are 0-indexed option indices (0 = first option, 1 = second option, etc.)

#### 10. Manipulation Check Phase
**Phase:** `manipulation_check`

**Fields:**
- `coherence`: Semantic coherence rating (1-7 scale)
- `connectivity`: Relational connectivity rating (1-7 scale)
- `strategy`: Memory strategy choice (text description)

### Key Metrics to Analyze

#### 1. Summary Viewing Time
**Purpose:** Measure attention and engagement with AI summaries

**Metrics:**
- Average time per condition (pre_reading vs post_reading)
- Average time per structure (integrated vs segmented)
- Correlation with recall performance
- Correlation with MCQ performance

#### 2. Recall Performance
**Metrics:**
- Sentence count (quantity)
- Word count (detail)
- Confidence ratings
- Perceived difficulty
- Time spent

#### 3. MCQ Performance
**Metrics:**
- Correct answer rate
- Performance by article
- Performance by timing condition
- Performance by structure condition
- False memory questions (Q10)

#### 4. Reading Behavior
**Metrics:**
- Total reading time
- Scroll depth
- Summary views (synchronous mode)
- Summary view time (synchronous mode)

### Data Quality Checks

#### 1. Summary Viewing Time Validation
- Check for unusually short times (< 10 seconds) - may indicate participants skipped
- Check for unusually long times (> 5 minutes) - may indicate participants left page open
- Compare with reading times to ensure consistency

#### 2. Recall Quality Checks
- `paste_attempts` should be 0 (paste is blocked)
- `sentence_count` should be >= 1
- `time_spent_ms` should be within reasonable bounds (typically 30-180 seconds)

#### 3. MCQ Completeness
- All 15 questions should have answers (check for missing `q0` through `q14`)
- Option indices should be 0-3 (4 options per question)

#### 4. Reading Behavior Validation
- Reading times should be 6-15 minutes per article (appropriate range)
- Scroll depth should be close to 100% (participant read to the end)
- Page visibility changes may indicate participant switched tabs

---

## Data Analysis

### Analysis Workflow

#### For Local Development
1. **Data is automatically saved** to `experiment_data/` folder
2. **Open in Excel/Google Sheets:**
   - `participants.csv` → Demographics overview
   - `P001_log.csv` → Detailed participant data
3. **Analyze with Python:**
   ```python
   import pandas as pd
   participants = pd.read_csv('experiment_data/participants.csv')
   log = pd.read_csv('experiment_data/P001_log.csv')
   ```

#### For Cloud Deployment
1. **Regular data export:**
   - Use `/admin/export` endpoint weekly/daily
   - Download ZIP file to your computer
   - Extract and analyze locally
2. **Monitor participant count:**
   - Use `/admin/stats` to check progress
   - Set up alerts if needed
3. **Backup strategy:**
   - Export data regularly (cloud storage is ephemeral on free tiers)
   - Store backups on your computer or cloud storage (Dropbox, Google Drive)

### Common Analysis Workflows

#### Workflow 1: Summary Viewing Time Analysis
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

#### Workflow 2: Recall-MCQ Relationship
```python
import pandas as pd
import json

# Load data
df = pd.read_csv('experiment_data/P001_log.csv')

# Extract recall data
recall_data = df[df['phase'] == 'recall_response']

# Extract MCQ data
mcq_data = df[df['phase'] == 'mcq_responses']

# Parse MCQ answers and calculate accuracy
for idx, row in mcq_data.iterrows():
    answers = json.loads(row['mcq_answers'])
    article = row['article_key']
    # Calculate accuracy based on correct answers
    # ... (see data_analysis/analyze_participant.py for implementation)
```

#### Workflow 3: Condition Comparison
1. Load randomization data to get condition assignments
2. Merge with performance data (recall, MCQ)
3. Compare performance across:
   - Timing conditions (synchronous, pre_reading, post_reading)
   - Structure conditions (integrated, segmented)
4. Include summary viewing time as a covariate

### Using the Analysis Script

See `data_analysis/analyze_participant.py` for a complete analysis script that:
- Parses CSV log files
- Calculates MCQ accuracy
- Analyzes reading times, recall quality, summary viewing times
- Generates comprehensive reports

**Usage:**
```bash
cd data_analysis
python3 analyze_participant.py P064
```

---

## Analysis Tools & Software Options

This section covers various software and tools you can use to analyze your experiment data, including traditional statistical software, programming languages, and modern AI-assisted analysis tools.

### 1. Python (Recommended for Advanced Analysis)

**Best for:** Advanced statistical analysis, custom visualizations, machine learning, automation

**Key Libraries:**
- **pandas** - Data manipulation and analysis
- **numpy** - Numerical computations
- **scipy** - Statistical tests (t-tests, ANOVA, correlations)
- **matplotlib** - Basic plotting
- **seaborn** - Statistical visualizations
- **scikit-learn** - Machine learning (if needed)
- **statsmodels** - Advanced statistical modeling

**Setup:**
```bash
pip install pandas numpy scipy matplotlib seaborn statsmodels
```

**Example Analysis:**
```python
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_csv('experiment_data/P001_log.csv')

# Summary statistics
summary_viewing = df[df['phase'] == 'summary_viewing']
print(summary_viewing['time_spent_seconds'].describe())

# T-test: pre_reading vs post_reading
pre = summary_viewing[summary_viewing['mode'] == 'pre_reading']['time_spent_seconds']
post = summary_viewing[summary_viewing['mode'] == 'post_reading']['time_spent_seconds']
t_stat, p_value = stats.ttest_ind(pre, post)
print(f"T-test: t={t_stat:.2f}, p={p_value:.4f}")

# Visualization
sns.boxplot(data=summary_viewing, x='mode', y='time_spent_seconds')
plt.show()
```

**Pros:**
- ✅ Free and open-source
- ✅ Highly flexible and customizable
- ✅ Great for automation and batch processing
- ✅ Extensive statistical libraries
- ✅ Excellent for reproducible research
- ✅ Integrates well with Jupyter Notebooks

**Cons:**
- ⚠️ Requires programming knowledge
- ⚠️ Steeper learning curve

**Resources:**
- [Pandas Documentation](https://pandas.pydata.org/)
- [SciPy Statistical Functions](https://docs.scipy.org/doc/scipy/reference/stats.html)
- [Seaborn Tutorial](https://seaborn.pydata.org/tutorial.html)

---

### 2. R / RStudio (Recommended for Statistical Analysis)

**Best for:** Statistical analysis, academic research, publication-quality graphics

**Key Packages:**
- **tidyverse** - Data manipulation (dplyr, ggplot2)
- **psych** - Psychological research functions
- **car** - Statistical tests (ANOVA, regression)
- **lme4** - Mixed-effects models
- **ggplot2** - Publication-quality graphics

**Setup:**
```r
install.packages(c("tidyverse", "psych", "car", "lme4"))
```

**Example Analysis:**
```r
library(tidyverse)
library(psych)

# Load data
df <- read_csv('experiment_data/P001_log.csv')

# Filter summary viewing data
summary_data <- df %>% filter(phase == 'summary_viewing')

# Descriptive statistics
describe(summary_data$time_spent_seconds)

# T-test
t.test(time_spent_seconds ~ mode, data = summary_data)

# Visualization
ggplot(summary_data, aes(x = mode, y = time_spent_seconds)) +
  geom_boxplot() +
  theme_minimal()
```

**Pros:**
- ✅ Free and open-source
- ✅ Excellent for statistical analysis
- ✅ Great visualization capabilities (ggplot2)
- ✅ Extensive packages for psychology research
- ✅ Widely used in academic research

**Cons:**
- ⚠️ Requires programming knowledge
- ⚠️ Different syntax from Python

**Resources:**
- [R for Data Science](https://r4ds.had.co.nz/)
- [RStudio Documentation](https://docs.rstudio.com/)

---

### 3. SPSS (Recommended for Non-Programmers)

**Best for:** Traditional statistical analysis, point-and-click interface, academic research

**Features:**
- Point-and-click interface (no coding required)
- Comprehensive statistical tests
- Good for ANOVA, regression, correlations
- Publication-quality output
- Widely used in psychology research

**Pros:**
- ✅ User-friendly interface
- ✅ No programming required
- ✅ Comprehensive statistical tests
- ✅ Good documentation and tutorials
- ✅ Widely accepted in academic journals

**Cons:**
- ⚠️ Expensive (student licenses available)
- ⚠️ Less flexible than programming languages
- ⚠️ Proprietary software

**Resources:**
- [SPSS Tutorials](https://www.ibm.com/support/pages/spss-statistics-documentation)
- [Laerd Statistics](https://statistics.laerd.com/spss-tutorials/)

---

### 4. JASP (Free Alternative to SPSS)

**Best for:** Bayesian statistics, user-friendly interface, free software

**Features:**
- Free and open-source
- Point-and-click interface
- Bayesian and frequentist statistics
- Good for ANOVA, t-tests, correlations
- Modern, intuitive interface

**Pros:**
- ✅ Free and open-source
- ✅ User-friendly interface
- ✅ Bayesian statistics support
- ✅ No programming required
- ✅ Good for beginners

**Cons:**
- ⚠️ Less features than SPSS
- ⚠️ Smaller community than R/Python

**Resources:**
- [JASP Website](https://jasp-stats.org/)
- [JASP Tutorials](https://jasp-stats.org/tutorials/)

---

### 5. Excel / Google Sheets (Quick Analysis)

**Best for:** Quick data exploration, simple calculations, sharing with collaborators

**Features:**
- Familiar interface
- Basic statistical functions
- Pivot tables
- Charts and graphs
- Easy to share and collaborate

**Example Functions:**
```
=AVERAGE(A2:A100)          # Calculate mean
=STDEV(A2:A100)            # Calculate standard deviation
=T.TEST(A2:A50, B2:B50, 2) # T-test
=CORREL(A2:A100, B2:B100)  # Correlation
```

**Pros:**
- ✅ Familiar interface
- ✅ No programming required
- ✅ Easy to share
- ✅ Good for quick exploration
- ✅ Available everywhere (Google Sheets)

**Cons:**
- ⚠️ Limited statistical capabilities
- ⚠️ Not ideal for complex analyses
- ⚠️ Can be error-prone for large datasets

**Use Cases:**
- Quick data exploration
- Simple descriptive statistics
- Sharing data with collaborators
- Creating simple visualizations

---

### 6. Jupyter Notebooks (Interactive Analysis)

**Best for:** Interactive analysis, data exploration, sharing analysis code, reproducible research

**Features:**
- Interactive code execution
- Combine code, text, and visualizations
- Great for exploratory analysis
- Easy to share and reproduce
- Supports Python, R, and other languages

**Setup:**
```bash
pip install jupyter pandas matplotlib seaborn
jupyter notebook
```

**Pros:**
- ✅ Interactive analysis
- ✅ Combine code and documentation
- ✅ Easy to share and reproduce
- ✅ Great for exploratory analysis
- ✅ Supports multiple languages

**Cons:**
- ⚠️ Requires programming knowledge
- ⚠️ Can be slow for large datasets

**Resources:**
- [Jupyter Notebook Tutorial](https://jupyter-notebook.readthedocs.io/)
- [JupyterLab](https://jupyterlab.readthedocs.io/)

---

### 7. AI-Assisted Analysis Tools

#### ChatGPT / Claude / Gemini (AI Chatbots)

**Best for:** Code generation, statistical advice, data interpretation, learning

**How to Use:**
1. **Code Generation:** Ask AI to write analysis code
   ```
   "Write Python code to load CSV data, calculate mean reading times 
   by condition, and perform a t-test comparing pre_reading vs post_reading"
   ```

2. **Statistical Advice:** Ask for help with statistical tests
   ```
   "What statistical test should I use to compare MCQ accuracy 
   across three timing conditions (synchronous, pre_reading, post_reading)?"
   ```

3. **Data Interpretation:** Get help interpreting results
   ```
   "I found a significant t-test (t=2.45, p=0.02) comparing summary 
   viewing times. What does this mean for my hypothesis?"
   ```

4. **Error Debugging:** Get help fixing code errors
   ```
   "My pandas code gives an error: 'KeyError: time_spent_seconds'. 
   How do I fix it?"
   ```

**Example Prompts:**
```
"Analyze my experiment data:
- Load all participant CSV files from experiment_data/ folder
- Calculate MCQ accuracy for each participant
- Compare accuracy between integrated and segmented conditions
- Perform a t-test and create a visualization"
```

**Pros:**
- ✅ No programming knowledge needed (for prompts)
- ✅ Great for learning and getting started
- ✅ Can generate complete analysis code
- ✅ Helpful for debugging and interpretation
- ✅ Available 24/7

**Cons:**
- ⚠️ May generate incorrect code (always verify)
- ⚠️ Requires data privacy considerations
- ⚠️ May not understand your specific research context
- ⚠️ Should not replace statistical expertise

**Best Practices:**
- ✅ Always verify generated code
- ✅ Don't upload sensitive participant data
- ✅ Use for learning and code generation, not final analysis
- ✅ Consult with statistician for complex analyses

#### Code Interpreter / Advanced Data Analysis (ChatGPT Plus)

**Best for:** Direct data analysis, file uploads, interactive analysis

**Features:**
- Upload CSV files directly
- Interactive data analysis
- Generate visualizations
- Statistical tests
- Code execution

**How to Use:**
1. Upload your CSV file
2. Ask questions about your data
3. Request specific analyses
4. Get visualizations and interpretations

**Example:**
```
"Upload my participants.csv file and:
1. Calculate descriptive statistics for all variables
2. Create a correlation matrix
3. Compare reading times between conditions
4. Generate publication-quality visualizations"
```

---

### 8. Google Colab (Free Cloud Python Environment)

**Best for:** Python analysis without local installation, collaboration, free GPU access

**Features:**
- Free cloud-based Jupyter Notebooks
- No installation required
- Free GPU access (for ML)
- Easy to share and collaborate
- Pre-installed data science libraries

**Setup:**
1. Go to [Google Colab](https://colab.research.google.com/)
2. Create a new notebook
3. Upload your CSV files
4. Start analyzing

**Pros:**
- ✅ Free and cloud-based
- ✅ No installation required
- ✅ Easy to share
- ✅ Free GPU access
- ✅ Pre-installed libraries

**Cons:**
- ⚠️ Requires Google account
- ⚠️ Data privacy considerations
- ⚠️ Limited compute time (free tier)

**Resources:**
- [Google Colab Tutorial](https://colab.research.google.com/notebooks/intro.ipynb)

---

### 9. Tableau / Power BI (Advanced Visualization)

**Best for:** Interactive dashboards, advanced visualizations, data storytelling

**Features:**
- Drag-and-drop interface
- Interactive dashboards
- Advanced visualizations
- Easy to share and present
- Good for exploring data

**Pros:**
- ✅ User-friendly interface
- ✅ Great visualizations
- ✅ Interactive dashboards
- ✅ Easy to share

**Cons:**
- ⚠️ Expensive (free trials available)
- ⚠️ Limited statistical analysis
- ⚠️ Overkill for simple analyses

**Use Cases:**
- Creating interactive dashboards
- Advanced visualizations
- Data storytelling and presentations
- Exploring large datasets

---

### 10. Online Statistical Tools

#### Jamovi (Free Statistical Software)

**Best for:** Free alternative to SPSS, user-friendly interface, modern design

**Features:**
- Free and open-source
- Point-and-click interface
- Comprehensive statistical tests
- Good for ANOVA, regression, t-tests
- Modern, intuitive interface

**Pros:**
- ✅ Free and open-source
- ✅ User-friendly interface
- ✅ Comprehensive statistical tests
- ✅ Good for beginners

**Resources:**
- [Jamovi Website](https://www.jamovi.org/)

---

## Choosing the Right Tool

### For Beginners (No Programming Experience)
1. **Excel/Google Sheets** - Quick exploration
2. **JASP** - Free statistical software
3. **SPSS** - Traditional statistical software (if available)
4. **AI Tools (ChatGPT/Claude)** - Code generation and learning

### For Intermediate Users (Some Programming Experience)
1. **Python + Jupyter Notebooks** - Flexible and powerful
2. **R + RStudio** - Statistical analysis
3. **Google Colab** - Cloud-based Python (no installation)

### For Advanced Users (Strong Programming Skills)
1. **Python (pandas, scipy, matplotlib)** - Maximum flexibility
2. **R (tidyverse, ggplot2)** - Statistical modeling
3. **Custom analysis scripts** - Reproducible research

### For Specific Tasks
- **Quick exploration:** Excel/Google Sheets
- **Statistical tests:** SPSS, JASP, R
- **Advanced statistics:** R, Python
- **Visualizations:** Python (seaborn), R (ggplot2), Tableau
- **Learning/Code generation:** AI tools (ChatGPT, Claude)
- **Collaboration:** Google Colab, Jupyter Notebooks
- **Reproducible research:** Python, R, Jupyter Notebooks

---

## Recommended Workflow

### 1. Data Exploration (Start Here)
- **Tool:** Excel/Google Sheets or Python/R
- **Goal:** Understand your data, check for errors, calculate basic statistics

### 2. Statistical Analysis
- **Tool:** Python (scipy), R, SPSS, or JASP
- **Goal:** Perform statistical tests (t-tests, ANOVA, correlations)

### 3. Visualization
- **Tool:** Python (matplotlib/seaborn), R (ggplot2), or Excel
- **Goal:** Create publication-quality figures

### 4. Advanced Analysis (If Needed)
- **Tool:** Python (scikit-learn), R (lme4), or specialized software
- **Goal:** Machine learning, mixed-effects models, etc.

### 5. Documentation
- **Tool:** Jupyter Notebooks or R Markdown
- **Goal:** Create reproducible analysis reports

---

## Getting Help

### Online Resources
- **Stack Overflow** - Programming questions
- **Cross Validated** - Statistical questions
- **Reddit (r/statistics, r/rstats, r/python)** - Community support
- **YouTube Tutorials** - Video tutorials for all tools

### AI-Assisted Learning
- **ChatGPT/Claude** - Ask questions, get code examples
- **GitHub Copilot** - Code completion and suggestions
- **Google Bard** - Statistical advice and code generation

### Academic Resources
- **Your supervisor** - Research-specific advice
- **Statistical consultant** - Complex analyses
- **University statistics center** - Free consultations

---

## Data Privacy Considerations

### When Using AI Tools
- ⚠️ **Don't upload sensitive participant data** to AI chatbots
- ⚠️ **Use anonymized data** or synthetic data for testing
- ⚠️ **Be careful with cloud-based tools** (Google Colab, etc.)
- ✅ **Use local analysis** for sensitive data
- ✅ **Follow your institution's data privacy guidelines**

### Best Practices
- ✅ Always anonymize data before sharing
- ✅ Use local tools for sensitive data
- ✅ Check data privacy policies of cloud tools
- ✅ Consult with your institution's data protection officer

---

## Next Steps

1. **Choose your tool** based on your experience and needs
2. **Start with data exploration** using Excel or Python
3. **Perform statistical tests** using your chosen tool
4. **Create visualizations** for your results
5. **Document your analysis** for reproducibility
6. **Get help** from AI tools, online resources, or your supervisor

---

## Admin Features

### Feature 1: Download All Data as ZIP

**Endpoint:** `/admin/export?key=YOUR_ADMIN_KEY`

**What it does:**
- Downloads all CSV files as a ZIP archive
- Includes `participants.csv` and all `PXXX_log.csv` files
- Includes translation cache (optional)
- Timestamped filename: `experiment_data_YYYYMMDD_HHMMSS.zip`

**Usage:**
```bash
# Command line
curl "https://your-app.onrender.com/admin/export?key=YOUR_KEY" -o data.zip

# Browser
https://your-app.onrender.com/admin/export?key=YOUR_KEY
```

**Security:**
- Requires `ADMIN_KEY` environment variable
- Must match the `?key=` parameter
- Returns 403 Unauthorized if key doesn't match

### Feature 2: View Statistics

**Endpoint:** `/admin/stats?key=YOUR_ADMIN_KEY`

**What it returns:**
```json
{
  "participant_count": 47,
  "data_files": ["P001_log.csv", "P002_log.csv", ...],
  "total_data_size_mb": 2.45,
  "last_update": "2024-01-15T14:30:00",
  "data_directory": "/path/to/experiment_data"
}
```

**Usage:**
```bash
# Command line
curl "https://your-app.onrender.com/admin/stats?key=YOUR_KEY"

# Browser
https://your-app.onrender.com/admin/stats?key=YOUR_KEY
```

### Setting Up Admin Access

#### Step 1: Generate Admin Key
```bash
# Generate a secure random key
openssl rand -hex 32
```

#### Step 2: Set Environment Variable

**Local testing:**
```bash
export ADMIN_KEY="your-generated-key-here"
python3 app.py
```

**Cloud deployment (Render/Railway):**
- Add `ADMIN_KEY` in environment variables section
- Use the same key you generated

#### Step 3: Use the Endpoints
```bash
# Check stats
curl "http://localhost:8080/admin/stats?key=your-generated-key-here"

# Download data
curl "http://localhost:8080/admin/export?key=your-generated-key-here" -o data.zip
```

### Troubleshooting

#### "Unauthorized" Error
- Check `ADMIN_KEY` environment variable is set
- Verify the `?key=` parameter matches exactly
- Keys are case-sensitive

#### Empty Export
- Check `experiment_data/` folder exists
- Verify CSV files are present
- Check server logs for errors

#### Data Not Appearing
- Ensure `log_data()` is being called in all routes
- Check file permissions on `experiment_data/` folder
- Verify UTF-8 encoding for non-English characters

---

## Recommendations

### For Small Studies (< 100 participants)

✅ **Current CSV approach is perfect:**
- Simple and readable
- Easy to analyze
- No database needed
- All measurements (time, text, scores) work great in CSV

### For Medium Studies (100-500 participants)

✅ **Continue with CSV:**
- Still efficient enough
- Easy to manage
- Suitable for academic research
- Compatible with all analysis tools

### For Large Studies (> 500 participants)

Consider upgrading to:
1. **SQLite database** (500-5000 participants)
   - More efficient for larger datasets
   - Built-in data integrity
   - SQL queries (complex analysis)
   - Still file-based (easy backup)

2. **PostgreSQL database** (5000+ participants)
   - Highly scalable (millions of records)
   - Concurrent access safe
   - Advanced features (transactions, replication)
   - Best for cloud deployment

3. **Cloud Storage** (AWS S3, Google Cloud Storage)
   - Persistent storage (survives server restarts)
   - Easy backup
   - Can still use CSV format

### Cloud Deployment Considerations

#### Important: Data Does NOT Go to Your Laptop
When deployed to cloud (Render/Railway/Fly.io):
- Data is saved on the **cloud server**
- You can't access it directly from your laptop
- Free tiers use **ephemeral storage** (data LOST on redeploy/restart)

#### Solutions for Cloud Deployment:

1. **Database (Recommended for Production)**
   - Use PostgreSQL (free on Render/Railway)
   - Data persists across redeploys
   - Easy to query and export
   - **Best for real studies**

2. **Cloud Storage (Simple Backup)**
   - Use AWS S3, Google Cloud Storage, or Dropbox API
   - Save CSV files to cloud storage
   - **Good for backups**

3. **Export API (Manual Download)**
   - Use `/admin/export` endpoint to download all data
   - Download CSV files manually
   - **Good for small studies**

4. **Email Export (Automated)**
   - Email data to yourself after each participant
   - **Simple but limited**

---

## Notes

- All timestamps are in ISO format (YYYY-MM-DDTHH:MM:SS.ssssss)
- Time values are in milliseconds unless specified as seconds
- JSON fields need to be parsed before analysis
- Participant IDs are sequential (P001, P002, etc.)
- Article numbers are 0-indexed (0, 1, 2) but represent articles 1, 2, 3
- Summary viewing time tracking pauses when page is hidden (by design)
- Very short times may indicate page was closed immediately
- Very long times may indicate page was left open

---

## Additional Resources

- See `data_analysis/README.md` for participant analysis tools
- See `DEPLOYMENT.md` for deployment instructions
- See `PROJECT_STRUCTURE.md` for project organization
- See main `README.md` for experiment overview

