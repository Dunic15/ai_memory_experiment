# Complete Analysis Plan for AI Memory Experiment

## Overview

This document outlines all the steps needed to execute your analysis plan for the AI-assisted learning memory experiment.

---

## Your Data Summary

### Available Data
| Experiment | Participants | Structure Conditions | Timing Conditions |
|------------|-------------|---------------------|-------------------|
| **AI Experiment** | ~20 (P233-P261) | Integrated / Segmented | Pre-reading, Synchronous, Post-reading |
| **No-AI Experiment** | ~7 (P171-P182) | N/A (control) | N/A |

### Variables Available Per Participant
| Category | Variables |
|----------|-----------|
| **Demographics** | age, gender, native_language, profession |
| **Prior Knowledge** | familiarity (1-7), recognition, quiz_score |
| **AI Trust** | trust_score (1-7), dependence_score (1-7), skill_score (1-7) |
| **Experimental Design** | structure (Integrated/Segmented), timing_order per article |
| **Reading Behavior** | reading_time_ms, scroll_depth, visibility_changes |
| **Summary Viewing** | time_spent_seconds, overlay_count (for sync mode) |
| **Free Recall** | recall_text, word_count, sentence_count, confidence (1-7), difficulty (1-7) |
| **MCQ Performance** | Total accuracy, AI_Summary accuracy, Article_Only accuracy, False_Lure accuracy |
| **False Lure** | false_lure_selected count (critical for misinformation analysis) |
| **Post-Article Ratings** | mental_effort, task_difficulty, ai_help_understanding, ai_help_memory, mcq_confidence |
| **Manipulation Check** | coherence, connectivity, strategy |

### MCQ Question Distribution (per article)
- **AI Summary questions**: 8
- **False Lure questions**: 2  
- **Article-only questions**: 4
- **Total**: 14 questions × 3 articles = 42 questions per participant

---

## STEP 1: Build the Master Data Table

**Goal:** Create a single CSV/DataFrame with one row per participant containing all dependent and independent variables.

### 1.1 Create Data Extraction Script

Create a new Python script: `create_analysis_dataset.py`

```python
#!/usr/bin/env python3
"""
Create master analysis dataset for ANOVA and regression analyses.
Outputs: analysis_dataset.csv
"""

import json
import csv
import os
import pandas as pd
from collections import defaultdict

# Source type mapping (same as in your existing scripts)
CORRECT_SOURCE_MAP = {
    'crispr': {0: 'ai_summary', 1: 'ai_summary', 2: 'false_lure', 3: 'ai_summary', 
               4: 'ai_summary', 5: 'ai_summary', 6: 'ai_summary', 7: 'ai_summary',
               8: 'article', 9: 'ai_summary', 10: 'article', 11: 'article', 
               12: 'article', 13: 'false_lure'},
    'semiconductors': {0: 'ai_summary', 1: 'ai_summary', 2: 'ai_summary', 3: 'ai_summary',
                       4: 'ai_summary', 5: 'ai_summary', 6: 'ai_summary', 7: 'article',
                       8: 'false_lure', 9: 'ai_summary', 10: 'false_lure', 11: 'article',
                       12: 'article', 13: 'article'},
    'uhi': {0: 'ai_summary', 1: 'ai_summary', 2: 'ai_summary', 3: 'false_lure',
            4: 'ai_summary', 5: 'ai_summary', 6: 'ai_summary', 7: 'ai_summary',
            8: 'ai_summary', 9: 'article', 10: 'false_lure', 11: 'article',
            12: 'article', 13: 'article'}
}

FALSE_LURE_OPTIONS = {
    'crispr': {2: 1, 13: 0},
    'semiconductors': {8: 0, 10: 1},
    'uhi': {3: 2, 10: 2}
}

def extract_participant_data(log_file_path, is_ai_experiment=True):
    """Extract all relevant data from a participant's log file."""
    data = {
        # Demographics
        'participant_id': '',
        'name': '',
        'age': '',
        'gender': '',
        'native_language': '',
        'profession': '',
        
        # Prior Knowledge
        'prior_knowledge_familiarity': 0,
        'prior_knowledge_recognition': 0,
        'prior_knowledge_quiz': 0,
        
        # AI Trust (only for AI experiment)
        'ai_trust_score': 0,
        'ai_dependence_score': 0,
        'tech_skill_score': 0,
        
        # Structure condition (only for AI experiment)
        'structure': '',  # 'integrated' or 'segmented'
        
        # Per-article data (will be expanded)
        'articles': {}  # article_key -> {timing, metrics...}
    }
    
    # Initialize article data
    for article in ['uhi', 'crispr', 'semiconductors']:
        data['articles'][article] = {
            'timing': '',
            'reading_time_ms': 0,
            'scroll_depth': 100,
            'summary_time_seconds': 0,
            'overlay_count': 0,
            'recall_word_count': 0,
            'recall_sentence_count': 0,
            'recall_confidence': 0,
            'recall_difficulty': 0,
            'mcq_total_correct': 0,
            'mcq_total_questions': 0,
            'mcq_ai_summary_correct': 0,
            'mcq_ai_summary_total': 0,
            'mcq_article_correct': 0,
            'mcq_article_total': 0,
            'mcq_false_lure_correct': 0,
            'mcq_false_lure_total': 0,
            'false_lures_selected': 0,
            'post_mental_effort': 0,
            'post_task_difficulty': 0,
            'post_ai_help_understanding': 0,
            'post_ai_help_memory': 0,
            'post_mcq_confidence': 0,
        }
    
    with open(log_file_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            return data
        
        for parts in reader:
            if not parts or len(parts) < 2:
                continue
            
            phase = parts[1]
            
            # Demographics
            if phase == 'demographics':
                data['name'] = parts[2] if len(parts) > 2 else ''
                data['profession'] = parts[3] if len(parts) > 3 else ''
                data['age'] = parts[4] if len(parts) > 4 else ''
                data['gender'] = parts[5] if len(parts) > 5 else ''
                data['native_language'] = parts[6] if len(parts) > 6 else ''
            
            # Prior Knowledge
            elif phase == 'prior_knowledge':
                data['prior_knowledge_familiarity'] = float(parts[2]) if len(parts) > 2 and parts[2] else 0
                data['prior_knowledge_recognition'] = float(parts[4]) if len(parts) > 4 and parts[4] else 0
                data['prior_knowledge_quiz'] = float(parts[6]) if len(parts) > 6 and parts[6] else 0
            
            # AI Trust
            elif phase == 'ai_trust':
                data['ai_trust_score'] = float(parts[2]) if len(parts) > 2 and parts[2] else 0
                data['ai_dependence_score'] = float(parts[4]) if len(parts) > 4 and parts[4] else 0
                data['tech_skill_score'] = float(parts[6]) if len(parts) > 6 and parts[6] else 0
            
            # Randomization
            elif phase == 'randomization':
                data['structure'] = parts[2].lower() if len(parts) > 2 else ''
                try:
                    timing_order = json.loads(parts[3]) if len(parts) > 3 else []
                    article_order = json.loads(parts[10]) if len(parts) > 10 else []
                    for i, (article, timing) in enumerate(zip(article_order, timing_order)):
                        if article in data['articles']:
                            data['articles'][article]['timing'] = timing
                except:
                    pass
            
            # Summary Viewing
            elif phase == 'summary_viewing':
                article_key = parts[3] if len(parts) > 3 else ''
                if article_key in data['articles']:
                    time_seconds = float(parts[7]) if len(parts) > 7 and parts[7] else 0
                    data['articles'][article_key]['summary_time_seconds'] = time_seconds
            
            # Reading Behavior
            elif phase == 'reading_behavior':
                event_type = parts[2] if len(parts) > 2 else ''
                if event_type == 'reading_complete':
                    article_key = parts[9] if len(parts) > 9 else ''
                    if article_key in data['articles']:
                        data['articles'][article_key]['reading_time_ms'] = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 0
                        data['articles'][article_key]['scroll_depth'] = int(parts[7]) if len(parts) > 7 and parts[7].isdigit() else 100
                        # For synchronous mode, get summary time
                        if len(parts) > 5:
                            try:
                                sync_summary_time = int(parts[5])
                                if sync_summary_time > 0:
                                    data['articles'][article_key]['summary_time_seconds'] = sync_summary_time / 1000
                            except:
                                pass
                        if len(parts) > 6:
                            try:
                                data['articles'][article_key]['overlay_count'] = int(parts[6])
                            except:
                                pass
            
            # Recall Response
            elif phase == 'recall_response':
                article_key = parts[3] if len(parts) > 3 else ''
                if article_key in data['articles']:
                    data['articles'][article_key]['recall_word_count'] = int(parts[7]) if len(parts) > 7 and parts[7].isdigit() else 0
                    data['articles'][article_key]['recall_sentence_count'] = int(parts[6]) if len(parts) > 6 and parts[6].isdigit() else 0
                    data['articles'][article_key]['recall_confidence'] = int(parts[9]) if len(parts) > 9 and parts[9].isdigit() else 0
                    data['articles'][article_key]['recall_difficulty'] = int(parts[10]) if len(parts) > 10 and parts[10].isdigit() else 0
            
            # MCQ Responses
            elif phase == 'mcq_responses':
                if is_ai_experiment:
                    article_key = parts[3] if len(parts) > 3 else ''
                    question_json = parts[12] if len(parts) > 12 else '{}'
                else:
                    article_key = parts[3] if len(parts) > 3 else ''
                    question_json = parts[11] if len(parts) > 11 else '{}'
                
                if article_key in data['articles']:
                    try:
                        question_details = json.loads(question_json.replace('""', '"'))
                    except:
                        question_details = {}
                    
                    source_map = CORRECT_SOURCE_MAP.get(article_key, {})
                    false_lure_opts = FALSE_LURE_OPTIONS.get(article_key, {})
                    
                    for q_key, q_data in question_details.items():
                        if not isinstance(q_data, dict):
                            continue
                        
                        q_idx = q_data.get('question_index', -1)
                        p_ans = q_data.get('participant_answer', -1)
                        is_correct = q_data.get('is_correct', False)
                        source_type = source_map.get(q_idx, 'unknown')
                        
                        data['articles'][article_key]['mcq_total_questions'] += 1
                        if is_correct:
                            data['articles'][article_key]['mcq_total_correct'] += 1
                        
                        if source_type == 'ai_summary':
                            data['articles'][article_key]['mcq_ai_summary_total'] += 1
                            if is_correct:
                                data['articles'][article_key]['mcq_ai_summary_correct'] += 1
                        elif source_type == 'article':
                            data['articles'][article_key]['mcq_article_total'] += 1
                            if is_correct:
                                data['articles'][article_key]['mcq_article_correct'] += 1
                        elif source_type == 'false_lure':
                            data['articles'][article_key]['mcq_false_lure_total'] += 1
                            if is_correct:
                                data['articles'][article_key]['mcq_false_lure_correct'] += 1
                            # Check if false lure was selected
                            if q_idx in false_lure_opts and p_ans == false_lure_opts[q_idx]:
                                data['articles'][article_key]['false_lures_selected'] += 1
            
            # Post-Article Ratings
            elif phase == 'post_article_ratings':
                article_key = parts[3] if len(parts) > 3 else ''
                if article_key in data['articles']:
                    data['articles'][article_key]['post_mental_effort'] = int(parts[5]) if len(parts) > 5 and parts[5].isdigit() else 0
                    data['articles'][article_key]['post_task_difficulty'] = int(parts[6]) if len(parts) > 6 and parts[6].isdigit() else 0
                    data['articles'][article_key]['post_ai_help_understanding'] = int(parts[7]) if len(parts) > 7 and parts[7].isdigit() else 0
                    data['articles'][article_key]['post_ai_help_memory'] = int(parts[8]) if len(parts) > 8 and parts[8].isdigit() else 0
                    data['articles'][article_key]['post_mcq_confidence'] = int(parts[12]) if len(parts) > 12 and parts[12].isdigit() else 0
    
    return data


def create_master_dataset():
    """Create the master analysis dataset."""
    
    all_participants = []
    
    # Process AI experiment
    ai_data_dir = 'ai_experiment/experiment_data'
    for filename in os.listdir(ai_data_dir):
        if filename.endswith('_log.csv'):
            pid = filename.split('-')[0]
            log_path = os.path.join(ai_data_dir, filename)
            data = extract_participant_data(log_path, is_ai_experiment=True)
            data['participant_id'] = pid
            data['experiment_group'] = 'AI'
            all_participants.append(data)
    
    # Process No-AI experiment
    no_ai_data_dir = 'no_ai_experiment/experiment_data'
    for filename in os.listdir(no_ai_data_dir):
        if filename.endswith('_log.csv'):
            pid = filename.split('-')[0]
            log_path = os.path.join(no_ai_data_dir, filename)
            data = extract_participant_data(log_path, is_ai_experiment=False)
            data['participant_id'] = pid
            data['experiment_group'] = 'NoAI'
            data['structure'] = 'none'  # No structure for control group
            all_participants.append(data)
    
    # Convert to flat DataFrame format
    rows = []
    for p in all_participants:
        # Calculate aggregated metrics across articles
        total_mcq_correct = sum(p['articles'][a]['mcq_total_correct'] for a in p['articles'])
        total_mcq_questions = sum(p['articles'][a]['mcq_total_questions'] for a in p['articles'])
        total_ai_summary_correct = sum(p['articles'][a]['mcq_ai_summary_correct'] for a in p['articles'])
        total_ai_summary_questions = sum(p['articles'][a]['mcq_ai_summary_total'] for a in p['articles'])
        total_article_correct = sum(p['articles'][a]['mcq_article_correct'] for a in p['articles'])
        total_article_questions = sum(p['articles'][a]['mcq_article_total'] for a in p['articles'])
        total_false_lure_correct = sum(p['articles'][a]['mcq_false_lure_correct'] for a in p['articles'])
        total_false_lure_questions = sum(p['articles'][a]['mcq_false_lure_total'] for a in p['articles'])
        total_false_lures_selected = sum(p['articles'][a]['false_lures_selected'] for a in p['articles'])
        
        # Calculate per-timing metrics (for within-subjects ANOVA)
        timing_metrics = {'pre_reading': {}, 'synchronous': {}, 'post_reading': {}}
        for article_key, article_data in p['articles'].items():
            timing = article_data['timing']
            if timing in timing_metrics:
                timing_metrics[timing][article_key] = article_data
        
        row = {
            'participant_id': p['participant_id'],
            'name': p['name'],
            'age': p['age'],
            'gender': p['gender'],
            'native_language': p['native_language'],
            'experiment_group': p['experiment_group'],
            'structure': p['structure'],
            
            # Prior Knowledge
            'prior_knowledge_familiarity': p['prior_knowledge_familiarity'],
            'prior_knowledge_recognition': p['prior_knowledge_recognition'],
            'prior_knowledge_quiz': p['prior_knowledge_quiz'],
            
            # AI Trust
            'ai_trust': p['ai_trust_score'],
            'ai_dependence': p['ai_dependence_score'],
            'tech_skill': p['tech_skill_score'],
            
            # Aggregated MCQ Performance
            'total_mcq_accuracy': (total_mcq_correct / total_mcq_questions * 100) if total_mcq_questions > 0 else 0,
            'ai_summary_accuracy': (total_ai_summary_correct / total_ai_summary_questions * 100) if total_ai_summary_questions > 0 else 0,
            'article_only_accuracy': (total_article_correct / total_article_questions * 100) if total_article_questions > 0 else 0,
            'false_lure_accuracy': (total_false_lure_correct / total_false_lure_questions * 100) if total_false_lure_questions > 0 else 0,
            'false_lures_selected': total_false_lures_selected,
            'false_lure_rate': (total_false_lures_selected / total_false_lure_questions * 100) if total_false_lure_questions > 0 else 0,
            
            # Recall metrics (averaged)
            'avg_recall_words': sum(p['articles'][a]['recall_word_count'] for a in p['articles']) / 3,
            'avg_recall_confidence': sum(p['articles'][a]['recall_confidence'] for a in p['articles']) / 3,
            'avg_recall_difficulty': sum(p['articles'][a]['recall_difficulty'] for a in p['articles']) / 3,
            
            # Behavioral metrics (averaged)
            'avg_reading_time_min': sum(p['articles'][a]['reading_time_ms'] for a in p['articles']) / 3 / 60000,
            'avg_summary_time_sec': sum(p['articles'][a]['summary_time_seconds'] for a in p['articles']) / 3,
            
            # Cognitive Load (averaged)
            'avg_mental_effort': sum(p['articles'][a]['post_mental_effort'] for a in p['articles']) / 3,
            'avg_task_difficulty': sum(p['articles'][a]['post_task_difficulty'] for a in p['articles']) / 3,
            'avg_mcq_confidence': sum(p['articles'][a]['post_mcq_confidence'] for a in p['articles']) / 3,
        }
        
        # Add per-timing metrics (for within-subjects analysis)
        for timing in ['pre_reading', 'synchronous', 'post_reading']:
            timing_data = timing_metrics.get(timing, {})
            if timing_data:
                article_data = list(timing_data.values())[0]  # Get the one article for this timing
                row[f'{timing}_mcq_total_accuracy'] = (article_data['mcq_total_correct'] / article_data['mcq_total_questions'] * 100) if article_data['mcq_total_questions'] > 0 else 0
                row[f'{timing}_ai_summary_accuracy'] = (article_data['mcq_ai_summary_correct'] / article_data['mcq_ai_summary_total'] * 100) if article_data['mcq_ai_summary_total'] > 0 else 0
                row[f'{timing}_article_accuracy'] = (article_data['mcq_article_correct'] / article_data['mcq_article_total'] * 100) if article_data['mcq_article_total'] > 0 else 0
                row[f'{timing}_false_lure_accuracy'] = (article_data['mcq_false_lure_correct'] / article_data['mcq_false_lure_total'] * 100) if article_data['mcq_false_lure_total'] > 0 else 0
                row[f'{timing}_false_lures_selected'] = article_data['false_lures_selected']
                row[f'{timing}_recall_words'] = article_data['recall_word_count']
                row[f'{timing}_recall_confidence'] = article_data['recall_confidence']
                row[f'{timing}_reading_time_min'] = article_data['reading_time_ms'] / 60000
                row[f'{timing}_summary_time_sec'] = article_data['summary_time_seconds']
                row[f'{timing}_mental_effort'] = article_data['post_mental_effort']
            else:
                # Fill with None for no-AI participants
                for metric in ['mcq_total_accuracy', 'ai_summary_accuracy', 'article_accuracy', 
                              'false_lure_accuracy', 'false_lures_selected', 'recall_words',
                              'recall_confidence', 'reading_time_min', 'summary_time_sec', 'mental_effort']:
                    row[f'{timing}_{metric}'] = None
        
        rows.append(row)
    
    df = pd.DataFrame(rows)
    df.to_csv('analysis_dataset.csv', index=False)
    print(f"Created analysis_dataset.csv with {len(df)} participants")
    print(f"  - AI experiment: {len(df[df['experiment_group'] == 'AI'])} participants")
    print(f"  - No-AI experiment: {len(df[df['experiment_group'] == 'NoAI'])} participants")
    print(f"\nColumns: {list(df.columns)}")
    
    return df


if __name__ == "__main__":
    df = create_master_dataset()
    print("\n" + "="*80)
    print("SAMPLE DATA (first 5 rows):")
    print("="*80)
    print(df.head())
```

### 1.2 Run the Script

```bash
cd /Users/duccioo/Desktop/ai_memory_experiment
python3 create_analysis_dataset.py
```

This will create `analysis_dataset.csv` with all your variables.

---

## STEP 2: Run the Core ANOVAs

### 2.1 Mixed ANOVA (2×3) - Structure × Timing (AI group only)

**This is your central analysis.**

**Design:**
- **Factor A (Between):** Structure (Integrated vs Segmented)
- **Factor B (Within):** Timing (Pre-reading, Synchronous, Post-reading)
- **DV:** MCQ Total Accuracy (per article timing condition)

**Python Code (using pingouin):**

```python
import pandas as pd
import pingouin as pg

# Load data
df = pd.read_csv('analysis_dataset.csv')

# Filter AI group only
ai_df = df[df['experiment_group'] == 'AI'].copy()

# Reshape for mixed ANOVA (long format)
timing_cols = ['pre_reading_mcq_total_accuracy', 'synchronous_mcq_total_accuracy', 'post_reading_mcq_total_accuracy']
ai_long = ai_df.melt(
    id_vars=['participant_id', 'structure'],
    value_vars=timing_cols,
    var_name='timing',
    value_name='mcq_accuracy'
)
ai_long['timing'] = ai_long['timing'].str.replace('_mcq_total_accuracy', '')

# Run Mixed ANOVA
aov = pg.mixed_anova(
    data=ai_long,
    dv='mcq_accuracy',
    within='timing',
    between='structure',
    subject='participant_id'
)
print("="*80)
print("MIXED ANOVA: Structure × Timing on MCQ Accuracy")
print("="*80)
print(aov.round(4))

# Post-hoc tests if significant
if aov[aov['Source'] == 'timing']['p-unc'].values[0] < 0.05:
    print("\nPost-hoc: Pairwise comparisons for Timing")
    posthoc = pg.pairwise_tests(data=ai_long, dv='mcq_accuracy', within='timing', 
                                 subject='participant_id', padjust='bonf')
    print(posthoc)
```

**R Code (if you prefer):**

```r
library(tidyverse)
library(afex)
library(emmeans)

df <- read_csv("analysis_dataset.csv")

# Filter AI group
ai_df <- df %>% filter(experiment_group == "AI")

# Reshape to long format
ai_long <- ai_df %>%
  pivot_longer(
    cols = c(pre_reading_mcq_total_accuracy, synchronous_mcq_total_accuracy, post_reading_mcq_total_accuracy),
    names_to = "timing",
    values_to = "mcq_accuracy"
  ) %>%
  mutate(timing = str_remove(timing, "_mcq_total_accuracy"))

# Mixed ANOVA
model <- aov_ez(
  id = "participant_id",
  dv = "mcq_accuracy", 
  data = ai_long,
  between = "structure",
  within = "timing"
)

summary(model)
emmeans(model, pairwise ~ timing)
emmeans(model, pairwise ~ structure * timing)
```

---

### 2.2 One-Way ANOVA - AI vs No-AI

**Design:**
- **Factor:** Group (No-AI, AI-Integrated, AI-Segmented)
- **DV:** Total MCQ Accuracy (mean across 3 articles)

**Python Code:**

```python
import pandas as pd
import pingouin as pg
from scipy import stats

# Load data
df = pd.read_csv('analysis_dataset.csv')

# Create 3-group variable
df['group'] = df.apply(
    lambda x: 'NoAI' if x['experiment_group'] == 'NoAI' 
              else f"AI_{x['structure'].capitalize()}", axis=1
)

# One-way ANOVA
aov = pg.anova(data=df, dv='total_mcq_accuracy', between='group')
print("="*80)
print("ONE-WAY ANOVA: AI vs No-AI on Total MCQ Accuracy")
print("="*80)
print(aov.round(4))

# Post-hoc tests
posthoc = pg.pairwise_tukey(data=df, dv='total_mcq_accuracy', between='group')
print("\nPost-hoc Tukey HSD:")
print(posthoc)

# Planned contrasts
# Contrast 1: No-AI vs (AI-Integrated + AI-Segmented)
noai = df[df['group'] == 'NoAI']['total_mcq_accuracy']
ai_all = df[df['group'] != 'NoAI']['total_mcq_accuracy']
t, p = stats.ttest_ind(noai, ai_all)
print(f"\nContrast: No-AI vs AI (all): t={t:.3f}, p={p:.4f}")

# Contrast 2: AI-Integrated vs AI-Segmented  
integrated = df[df['group'] == 'AI_Integrated']['total_mcq_accuracy']
segmented = df[df['group'] == 'AI_Segmented']['total_mcq_accuracy']
t, p = stats.ttest_ind(integrated, segmented)
print(f"Contrast: Integrated vs Segmented: t={t:.3f}, p={p:.4f}")
```

---

### 2.3 Additional Mixed ANOVAs (Same 2×3 Design)

Run the same Structure × Timing ANOVA for each of these DVs:

| DV | What it Measures |
|---|---|
| `false_lure_rate` | Vulnerability to AI-planted misinformation |
| `article_only_accuracy` | Encoding of article-only content |
| `recall_words` | Free recall quantity (proxy for schema building) |
| `recall_confidence` | Metacognitive awareness |

**Python Template:**

```python
# For each DV:
for dv_prefix in ['false_lure_accuracy', 'article_accuracy', 'recall_words', 'recall_confidence']:
    timing_cols = [f'pre_reading_{dv_prefix}', f'synchronous_{dv_prefix}', f'post_reading_{dv_prefix}']
    
    # Check if columns exist
    if all(col in ai_df.columns for col in timing_cols):
        ai_long = ai_df.melt(
            id_vars=['participant_id', 'structure'],
            value_vars=timing_cols,
            var_name='timing',
            value_name='dv'
        )
        ai_long['timing'] = ai_long['timing'].str.replace(f'_{dv_prefix}', '')
        
        aov = pg.mixed_anova(
            data=ai_long.dropna(),
            dv='dv',
            within='timing',
            between='structure',
            subject='participant_id'
        )
        print(f"\n{'='*80}")
        print(f"MIXED ANOVA: Structure × Timing on {dv_prefix}")
        print(f"{'='*80}")
        print(aov.round(4))
```

---

## STEP 3: Correlations & Regressions (Mechanisms)

### 3.1 Correlation Matrix

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv('analysis_dataset.csv')
ai_df = df[df['experiment_group'] == 'AI']

# Key variables for correlation
corr_vars = [
    'total_mcq_accuracy',
    'ai_summary_accuracy', 
    'article_only_accuracy',
    'false_lure_rate',
    'avg_recall_words',
    'avg_reading_time_min',
    'avg_summary_time_sec',
    'prior_knowledge_familiarity',
    'ai_trust',
    'ai_dependence',
    'avg_mental_effort',
    'avg_mcq_confidence'
]

corr_matrix = ai_df[corr_vars].corr()

plt.figure(figsize=(14, 12))
sns.heatmap(corr_matrix, annot=True, cmap='RdBu_r', center=0, fmt='.2f')
plt.title('Correlation Matrix - AI Experiment Variables')
plt.tight_layout()
plt.savefig('correlation_matrix.png', dpi=150)
plt.show()
```

### 3.2 Regression: False Lure Rate Predictors

```python
import statsmodels.api as sm
import statsmodels.formula.api as smf

df = pd.read_csv('analysis_dataset.csv')
ai_df = df[df['experiment_group'] == 'AI'].copy()

# Code structure as dummy variable
ai_df['structure_integrated'] = (ai_df['structure'] == 'integrated').astype(int)

# Regression model
model = smf.ols('''
    false_lure_rate ~ 
    structure_integrated + 
    avg_summary_time_sec + 
    prior_knowledge_familiarity + 
    ai_trust + 
    ai_dependence
''', data=ai_df).fit()

print("="*80)
print("REGRESSION: Predictors of False Lure Rate")
print("="*80)
print(model.summary())
```

### 3.3 Regression: MCQ Accuracy Predictors

```python
# Full model with behavioral and individual difference predictors
model = smf.ols('''
    total_mcq_accuracy ~ 
    structure_integrated + 
    avg_reading_time_min + 
    avg_summary_time_sec + 
    prior_knowledge_familiarity + 
    ai_trust + 
    avg_mental_effort
''', data=ai_df).fit()

print("="*80)
print("REGRESSION: Predictors of Total MCQ Accuracy")
print("="*80)
print(model.summary())
```

---

## STEP 4: Visualizations

### 4.1 Bar Plot: Structure × Timing Interaction

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('analysis_dataset.csv')
ai_df = df[df['experiment_group'] == 'AI']

# Reshape for plotting
timing_cols = ['pre_reading_mcq_total_accuracy', 'synchronous_mcq_total_accuracy', 'post_reading_mcq_total_accuracy']
ai_long = ai_df.melt(
    id_vars=['participant_id', 'structure'],
    value_vars=timing_cols,
    var_name='timing',
    value_name='mcq_accuracy'
)
ai_long['timing'] = ai_long['timing'].str.replace('_mcq_total_accuracy', '').str.replace('_', ' ').str.title()

plt.figure(figsize=(10, 6))
sns.barplot(data=ai_long, x='timing', y='mcq_accuracy', hue='structure', 
            order=['Pre Reading', 'Synchronous', 'Post Reading'],
            palette={'integrated': '#2ecc71', 'segmented': '#3498db'})
plt.xlabel('Timing Condition')
plt.ylabel('MCQ Accuracy (%)')
plt.title('MCQ Accuracy by Structure × Timing')
plt.legend(title='Structure')
plt.tight_layout()
plt.savefig('structure_timing_interaction.png', dpi=150)
plt.show()
```

### 4.2 Box Plot: AI vs No-AI Comparison

```python
plt.figure(figsize=(8, 6))
df['group'] = df.apply(
    lambda x: 'No AI' if x['experiment_group'] == 'NoAI' 
              else f"AI {x['structure'].capitalize()}", axis=1
)
sns.boxplot(data=df, x='group', y='total_mcq_accuracy', 
            order=['No AI', 'AI Integrated', 'AI Segmented'],
            palette=['#95a5a6', '#2ecc71', '#3498db'])
plt.xlabel('Condition')
plt.ylabel('Total MCQ Accuracy (%)')
plt.title('MCQ Accuracy: AI vs No-AI Conditions')
plt.tight_layout()
plt.savefig('ai_vs_noai.png', dpi=150)
plt.show()
```

---

## STEP 5: Summary Checklist

### Data Preparation
- [ ] Run `create_analysis_dataset.py` to create master dataset
- [ ] Check for missing values and outliers
- [ ] Verify sample sizes per condition

### Mandatory Analyses
- [ ] **Mixed ANOVA (2×3):** Structure × Timing → MCQ Total Accuracy
- [ ] **One-Way ANOVA:** No-AI vs AI-Integrated vs AI-Segmented

### Recommended Additional Analyses
- [ ] **Mixed ANOVA:** Structure × Timing → False Lure Rate
- [ ] **Mixed ANOVA:** Structure × Timing → Article-Only Accuracy  
- [ ] **Mixed ANOVA:** Structure × Timing → Free Recall (word count)

### Mechanism Analyses
- [ ] Correlation matrix of all key variables
- [ ] Regression: False Lure Rate ~ behavioral + individual differences
- [ ] Regression: MCQ Accuracy ~ behavioral + individual differences

### Visualizations
- [ ] Structure × Timing interaction plot
- [ ] AI vs No-AI comparison plot
- [ ] Correlation heatmap
- [ ] False lure rate by condition

---

## Required Python Packages

```bash
pip install pandas numpy scipy statsmodels pingouin seaborn matplotlib
```

Or for R:
```r
install.packages(c("tidyverse", "afex", "emmeans", "effectsize", "ggplot2"))
```

---

## Expected Results Section Outline

1. **Descriptive Statistics**
   - Table of means and SDs by condition
   
2. **Main Analysis: Structure × Timing (AI only)**
   - 2×3 Mixed ANOVA results
   - Post-hoc comparisons
   - Effect sizes (η²)

3. **AI vs No-AI Comparison**
   - One-way ANOVA results
   - Planned contrasts

4. **Secondary Analyses**
   - False lure vulnerability
   - Article-only encoding
   - Free recall quality

5. **Mechanism Analyses**
   - Correlations
   - Regression models

6. **Visualizations**
   - Interaction plots
   - Group comparisons

---

## Notes on Your Current Sample Size

With ~20 AI participants and ~7 No-AI participants:
- You have limited statistical power
- Focus on effect sizes rather than p-values
- Consider reporting confidence intervals
- Use non-parametric alternatives if assumptions are violated
- Consider bootstrap methods for robustness

Good luck with your analysis! 🎓

---

## STEP 6: Free Recall Scoring

The free recall responses have been automatically scored using a structured rubric.

### Scoring System

Each recall is scored on two components:

#### A. Idea Units Score (0-10)
- Recall is compared against 10 canonical ideas per article
- 1 point = idea correctly expressed (even paraphrased)
- 0.5 point = partially present or vague
- 0 points = not present

#### B. Relational Links Score (0-2)
- Points for connecting ideas using causal/temporal/explanatory relations
- Keywords: "because", "leads to", "therefore", "result", "due to", "cause", etc.
- Maximum 2 points

#### C. Total Score (0-12)
```
total_score = idea_units_score + relational_links_score
```

### Running the Scoring Script

```bash
python score_free_recall.py
```

This generates:
- `recall_scores.csv`: Main scoring results
- `recall_details.json`: Detailed breakdown per idea unit

### Variables Added to Datasets

**Wide format (analysis_dataset.csv):**
- `avg_recall_idea_units`: Mean idea units across 3 articles
- `avg_recall_rel_links`: Mean relational links across 3 articles
- `avg_recall_total_score`: Mean total recall score
- `{timing}_recall_idea_units`: Per-timing idea units
- `{timing}_recall_rel_links`: Per-timing relational links
- `{timing}_recall_total_score`: Per-timing total score

**Long format (analysis_dataset_long.csv):**
- `recall_idea_units`: Idea units score for that timing/article
- `recall_rel_links`: Relational links score
- `recall_total_score`: Total recall score

### Current Results

| Group | Idea Units (0-10) | Rel. Links (0-2) | Total (0-12) |
|-------|-------------------|------------------|--------------|
| AI Experiment | 3.27 | 1.24 | 4.51 |
| No-AI Experiment | 3.79 | 1.33 | 5.12 |

**By Timing (AI group):**
| Timing | Total Score |
|--------|-------------|
| Pre-reading | 4.79 |
| Synchronous | 4.21 |
| Post-reading | 4.52 |

### Using Recall in ANOVA

```python
# Mixed ANOVA: Structure × Timing → Recall Total Score
timing_cols = ['pre_reading_recall_total_score', 'synchronous_recall_total_score', 'post_reading_recall_total_score']
ai_long = ai_df.melt(
    id_vars=['participant_id', 'structure'],
    value_vars=timing_cols,
    var_name='timing',
    value_name='recall_score'
)

aov = pg.mixed_anova(
    data=ai_long.dropna(),
    dv='recall_score',
    within='timing',
    between='structure',
    subject='participant_id'
)
```

---

## Complete File List

| File | Description |
|------|-------------|
| `analysis_dataset.csv` | Wide format - 1 row per participant (78 columns) |
| `analysis_dataset_long.csv` | Long format - for repeated measures ANOVA (21 columns) |
| `recall_scores.csv` | Raw recall scores per timing/article |
| `recall_details.json` | Detailed idea unit breakdown |
| `create_analysis_dataset.py` | Script to regenerate MCQ datasets |
| `score_free_recall.py` | Script to score free recall responses |
| `ANALYSIS_PLAN.md` | This document |

