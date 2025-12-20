#!/usr/bin/env python3
"""
Create master analysis dataset for ANOVA and regression analyses.
Outputs: analysis_dataset.csv

This script extracts all relevant variables from participant log files
and creates a single CSV ready for statistical analysis.

Usage:
    python create_analysis_dataset.py

Output:
    - analysis_dataset.csv: Wide-format dataset (1 row per participant)
    - analysis_dataset_long.csv: Long-format dataset for repeated measures
"""

import json
import csv
import os
import sys

# Try to import pandas, provide helpful message if not available
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    print("Warning: pandas not installed. Will create CSV manually.")
    print("For full functionality, install pandas: pip install pandas")

# Source type mapping for AI experiment (8 AI Summary + 2 False Lure + 4 Article per article)
CORRECT_SOURCE_MAP = {
    'crispr': {
        0: 'ai_summary', 1: 'ai_summary', 2: 'false_lure', 3: 'ai_summary',
        4: 'ai_summary', 5: 'ai_summary', 6: 'ai_summary', 7: 'ai_summary',
        8: 'article', 9: 'ai_summary', 10: 'article', 11: 'article',
        12: 'article', 13: 'false_lure'
    },
    'semiconductors': {
        0: 'ai_summary', 1: 'ai_summary', 2: 'ai_summary', 3: 'ai_summary',
        4: 'ai_summary', 5: 'ai_summary', 6: 'ai_summary', 7: 'article',
        8: 'false_lure', 9: 'ai_summary', 10: 'false_lure', 11: 'article',
        12: 'article', 13: 'article'
    },
    'uhi': {
        0: 'ai_summary', 1: 'ai_summary', 2: 'ai_summary', 3: 'false_lure',
        4: 'ai_summary', 5: 'ai_summary', 6: 'ai_summary', 7: 'ai_summary',
        8: 'ai_summary', 9: 'article', 10: 'false_lure', 11: 'article',
        12: 'article', 13: 'article'
    }
}

# False lure option indices for each article
FALSE_LURE_OPTIONS = {
    'crispr': {2: 1, 13: 0},      # Q3: option b, Q14: option a
    'semiconductors': {8: 0, 10: 1},  # Q9: option a, Q11: option b
    'uhi': {3: 2, 10: 2}          # Q4: option c, Q11: option c
}


def safe_int(value, default=0):
    """Safely convert to int."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value, default=0.0):
    """Safely convert to float."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def extract_participant_data(log_file_path, is_ai_experiment=True):
    """Extract all relevant data from a participant's log file.
    
    Important: This function removes duplicate MCQ entries per article.
    Some participants may have submitted multiple times due to technical issues.
    """
    data = {
        # Demographics
        'participant_id': '',
        'name': '',
        'age': '',
        'gender': '',
        'native_language': '',
        'profession': '',
        
        # Prior Knowledge
        'prior_knowledge_familiarity': 0.0,
        'prior_knowledge_recognition': 0.0,
        'prior_knowledge_quiz': 0.0,
        
        # AI Trust (only for AI experiment)
        'ai_trust_score': 0.0,
        'ai_dependence_score': 0.0,
        'tech_skill_score': 0.0,
        
        # Structure condition (only for AI experiment)
        'structure': '',
        
        # Manipulation check
        'manipulation_coherence': 0,
        'manipulation_connectivity': 0,
        
        # Per-article data
        'articles': {},
        
        # Track duplicates
        'duplicates_removed': 0
    }
    
    # Track which articles have been processed for MCQ (to detect duplicates)
    processed_mcq_articles = set()
    
    # Initialize article data
    for article in ['uhi', 'crispr', 'semiconductors']:
        data['articles'][article] = {
            'timing': '',
            'article_order': -1,
            'reading_time_ms': 0,
            'scroll_depth': 100,
            'summary_time_seconds': 0.0,
            'overlay_count': 0,
            'recall_text': '',
            'recall_word_count': 0,
            'recall_sentence_count': 0,
            'recall_character_count': 0,
            'recall_confidence': 0,
            'recall_difficulty': 0,
            'recall_time_ms': 0,
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
            'post_ai_made_easier': 0,
            'post_ai_satisfaction': 0,
            'post_mcq_confidence': 0,
        }
    
    # Track article order
    article_order_counter = 0
    processed_articles = set()
    
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
            
            try:
                # Demographics
                if phase == 'demographics':
                    data['name'] = parts[2] if len(parts) > 2 else ''
                    data['profession'] = parts[3] if len(parts) > 3 else ''
                    data['age'] = parts[4] if len(parts) > 4 else ''
                    data['gender'] = parts[5] if len(parts) > 5 else ''
                    data['native_language'] = parts[6] if len(parts) > 6 else ''
                
                # Prior Knowledge
                elif phase == 'prior_knowledge':
                    data['prior_knowledge_familiarity'] = safe_float(parts[2]) if len(parts) > 2 else 0
                    data['prior_knowledge_recognition'] = safe_float(parts[4]) if len(parts) > 4 else 0
                    data['prior_knowledge_quiz'] = safe_float(parts[6]) if len(parts) > 6 else 0
                
                # AI Trust
                elif phase == 'ai_trust':
                    data['ai_trust_score'] = safe_float(parts[2]) if len(parts) > 2 else 0
                    data['ai_dependence_score'] = safe_float(parts[4]) if len(parts) > 4 else 0
                    data['tech_skill_score'] = safe_float(parts[6]) if len(parts) > 6 else 0
                
                # Randomization
                elif phase == 'randomization':
                    data['structure'] = parts[2].lower() if len(parts) > 2 else ''
                    try:
                        # Try to parse timing and article orders
                        # Format: timestamp,randomization,structure,A1/A2,"[timing_order]",timing_num,B1/B2/B3,B1/B2/B3,B1/B2/B3,"[article_order]",timestamp
                        # timing_order is at index 4, article_order is at index 9
                        if len(parts) > 4:
                            timing_str = parts[4].replace('""', '"')
                            timing_order = json.loads(timing_str) if timing_str.startswith('[') else []
                        else:
                            timing_order = []
                        
                        if len(parts) > 9:
                            article_str = parts[9].replace('""', '"')
                            article_order = json.loads(article_str) if article_str.startswith('[') else []
                        else:
                            article_order = []
                        
                        for i, (article, timing) in enumerate(zip(article_order, timing_order)):
                            if article.lower() in data['articles']:
                                data['articles'][article.lower()]['timing'] = timing
                                data['articles'][article.lower()]['article_order'] = i
                    except (json.JSONDecodeError, IndexError) as e:
                        # Try alternative parsing for different format
                        pass
                
                # Summary Viewing (for pre/post reading)
                elif phase == 'summary_viewing':
                    article_key = parts[3].lower() if len(parts) > 3 else ''
                    if article_key in data['articles']:
                        time_seconds = safe_float(parts[7]) if len(parts) > 7 else 0
                        data['articles'][article_key]['summary_time_seconds'] = time_seconds
                
                # Reading Behavior
                elif phase == 'reading_behavior':
                    event_type = parts[2] if len(parts) > 2 else ''
                    if event_type == 'reading_complete':
                        article_key = parts[9].lower() if len(parts) > 9 else ''
                        if article_key in data['articles']:
                            data['articles'][article_key]['reading_time_ms'] = safe_int(parts[4])
                            data['articles'][article_key]['scroll_depth'] = safe_int(parts[7]) if len(parts) > 7 else 100
                            
                            # Track article order if not set from randomization
                            if article_key not in processed_articles:
                                if data['articles'][article_key]['article_order'] == -1:
                                    data['articles'][article_key]['article_order'] = article_order_counter
                                article_order_counter += 1
                                processed_articles.add(article_key)
                            
                            # For synchronous mode, get summary time from reading_complete
                            if len(parts) > 5:
                                sync_summary_time = safe_int(parts[5])
                                if sync_summary_time > 0:
                                    data['articles'][article_key]['summary_time_seconds'] = sync_summary_time / 1000
                            if len(parts) > 6:
                                data['articles'][article_key]['overlay_count'] = safe_int(parts[6])
                
                # Recall Response
                elif phase == 'recall_response':
                    article_key = parts[3].lower() if len(parts) > 3 else ''
                    if article_key in data['articles']:
                        data['articles'][article_key]['recall_text'] = parts[5] if len(parts) > 5 else ''
                        data['articles'][article_key]['recall_sentence_count'] = safe_int(parts[6])
                        data['articles'][article_key]['recall_word_count'] = safe_int(parts[7])
                        data['articles'][article_key]['recall_character_count'] = safe_int(parts[8])
                        data['articles'][article_key]['recall_confidence'] = safe_int(parts[9])
                        data['articles'][article_key]['recall_difficulty'] = safe_int(parts[10])
                        data['articles'][article_key]['recall_time_ms'] = safe_int(parts[11])
                
                # MCQ Responses
                elif phase == 'mcq_responses':
                    if is_ai_experiment:
                        article_key = parts[3].lower() if len(parts) > 3 else ''
                        question_json = parts[12] if len(parts) > 12 else '{}'
                    else:
                        article_key = parts[3].lower() if len(parts) > 3 else ''
                        question_json = parts[11] if len(parts) > 11 else '{}'
                    
                    # Skip duplicate MCQ entries for the same article
                    if article_key in processed_mcq_articles:
                        data['duplicates_removed'] += 1
                        continue
                    
                    if article_key in data['articles']:
                        processed_mcq_articles.add(article_key)  # Mark as processed
                        
                        try:
                            question_details = json.loads(question_json.replace('""', '"'))
                        except (json.JSONDecodeError, AttributeError):
                            question_details = {}
                        
                        source_map = CORRECT_SOURCE_MAP.get(article_key, {})
                        false_lure_opts = FALSE_LURE_OPTIONS.get(article_key, {})
                        
                        for q_key, q_data in question_details.items():
                            if not isinstance(q_data, dict):
                                continue
                            
                            q_idx = q_data.get('question_index', -1)
                            p_ans = q_data.get('participant_answer', -1)
                            is_correct = q_data.get('is_correct', False)
                            source_type = source_map.get(q_idx, 'unknown') if is_ai_experiment else 'article'
                            
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
                    article_key = parts[3].lower() if len(parts) > 3 else ''
                    if article_key in data['articles']:
                        data['articles'][article_key]['post_mental_effort'] = safe_int(parts[5])
                        data['articles'][article_key]['post_task_difficulty'] = safe_int(parts[6])
                        data['articles'][article_key]['post_ai_help_understanding'] = safe_int(parts[7])
                        data['articles'][article_key]['post_ai_help_memory'] = safe_int(parts[8])
                        data['articles'][article_key]['post_ai_made_easier'] = safe_int(parts[9])
                        data['articles'][article_key]['post_ai_satisfaction'] = safe_int(parts[10])
                        data['articles'][article_key]['post_mcq_confidence'] = safe_int(parts[12]) if len(parts) > 12 else 0
                
                # Manipulation Check
                elif phase == 'manipulation_check':
                    data['manipulation_coherence'] = safe_int(parts[2])
                    data['manipulation_connectivity'] = safe_int(parts[3])
                    
            except Exception as e:
                # Skip problematic rows
                continue
    
    return data


def create_master_dataset():
    """Create the master analysis dataset."""
    
    all_participants = []
    
    # Process AI experiment
    ai_data_dir = 'ai_experiment/experiment_data'
    if os.path.exists(ai_data_dir):
        for filename in sorted(os.listdir(ai_data_dir)):
            if filename.endswith('_log.csv') and not filename.startswith('.'):
                pid = filename.split('-')[0]
                if pid == 'P249':
                    print(f"Skipping outlier AI: {pid}...")
                    continue
                log_path = os.path.join(ai_data_dir, filename)
                print(f"Processing AI: {pid}...")
                data = extract_participant_data(log_path, is_ai_experiment=True)
                data['participant_id'] = pid
                data['experiment_group'] = 'AI'
                all_participants.append(data)
    
    # Process No-AI experiment
    no_ai_data_dir = 'no_ai_experiment/experiment_data'
    if os.path.exists(no_ai_data_dir):
        for filename in sorted(os.listdir(no_ai_data_dir)):
            if filename.endswith('_log.csv') and not filename.startswith('.'):
                pid = filename.split('-')[0]
                log_path = os.path.join(no_ai_data_dir, filename)
                print(f"Processing No-AI: {pid}...")
                data = extract_participant_data(log_path, is_ai_experiment=False)
                data['participant_id'] = pid
                data['experiment_group'] = 'NoAI'
                data['structure'] = 'none'
                all_participants.append(data)
    
    # Convert to rows
    rows = []
    for p in all_participants:
        # Calculate aggregated metrics
        articles_with_data = [a for a in p['articles'].values() if a['mcq_total_questions'] > 0]
        n_articles = len(articles_with_data)
        
        if n_articles == 0:
            print(f"Warning: {p['participant_id']} has no MCQ data, skipping...")
            continue
        
        # Aggregate MCQ metrics
        total_mcq_correct = sum(a['mcq_total_correct'] for a in articles_with_data)
        total_mcq_questions = sum(a['mcq_total_questions'] for a in articles_with_data)
        total_ai_summary_correct = sum(a['mcq_ai_summary_correct'] for a in articles_with_data)
        total_ai_summary_questions = sum(a['mcq_ai_summary_total'] for a in articles_with_data)
        total_article_correct = sum(a['mcq_article_correct'] for a in articles_with_data)
        total_article_questions = sum(a['mcq_article_total'] for a in articles_with_data)
        total_false_lure_correct = sum(a['mcq_false_lure_correct'] for a in articles_with_data)
        total_false_lure_questions = sum(a['mcq_false_lure_total'] for a in articles_with_data)
        total_false_lures_selected = sum(a['false_lures_selected'] for a in articles_with_data)
        
        row = {
            'participant_id': p['participant_id'],
            'name': p['name'],
            'age': p['age'],
            'gender': p['gender'],
            'native_language': p['native_language'],
            'profession': p['profession'],
            'experiment_group': p['experiment_group'],
            'structure': p['structure'],
            
            # Prior Knowledge
            'prior_knowledge_familiarity': round(p['prior_knowledge_familiarity'], 3),
            'prior_knowledge_recognition': round(p['prior_knowledge_recognition'], 3),
            'prior_knowledge_quiz': round(p['prior_knowledge_quiz'], 3),
            
            # AI Trust
            'ai_trust': round(p['ai_trust_score'], 3),
            'ai_dependence': round(p['ai_dependence_score'], 3),
            'tech_skill': round(p['tech_skill_score'], 3),
            
            # Manipulation Check
            'manipulation_coherence': p['manipulation_coherence'],
            'manipulation_connectivity': p['manipulation_connectivity'],
            
            # Aggregated MCQ Performance
            'total_mcq_accuracy': round((total_mcq_correct / total_mcq_questions * 100), 2) if total_mcq_questions > 0 else 0,
            'total_mcq_correct': total_mcq_correct,
            'total_mcq_questions': total_mcq_questions,
            'ai_summary_accuracy': round((total_ai_summary_correct / total_ai_summary_questions * 100), 2) if total_ai_summary_questions > 0 else None,
            'article_only_accuracy': round((total_article_correct / total_article_questions * 100), 2) if total_article_questions > 0 else 0,
            'false_lure_accuracy': round((total_false_lure_correct / total_false_lure_questions * 100), 2) if total_false_lure_questions > 0 else None,
            'false_lures_selected': total_false_lures_selected,
            'false_lure_rate': round((total_false_lures_selected / total_false_lure_questions * 100), 2) if total_false_lure_questions > 0 else None,
            
            # Recall metrics (averaged)
            'avg_recall_words': round(sum(a['recall_word_count'] for a in articles_with_data) / n_articles, 2),
            'avg_recall_sentences': round(sum(a['recall_sentence_count'] for a in articles_with_data) / n_articles, 2),
            'avg_recall_confidence': round(sum(a['recall_confidence'] for a in articles_with_data) / n_articles, 2),
            'avg_recall_difficulty': round(sum(a['recall_difficulty'] for a in articles_with_data) / n_articles, 2),
            
            # Behavioral metrics (averaged)
            'avg_reading_time_min': round(sum(a['reading_time_ms'] for a in articles_with_data) / n_articles / 60000, 2),
            'avg_summary_time_sec': round(sum(a['summary_time_seconds'] for a in articles_with_data) / n_articles, 2),
            
            # Cognitive Load (averaged)
            'avg_mental_effort': round(sum(a['post_mental_effort'] for a in articles_with_data) / n_articles, 2),
            'avg_task_difficulty': round(sum(a['post_task_difficulty'] for a in articles_with_data) / n_articles, 2),
            'avg_mcq_confidence': round(sum(a['post_mcq_confidence'] for a in articles_with_data) / n_articles, 2),
        }
        
        # Add per-timing metrics (for within-subjects analysis)
        for timing in ['pre_reading', 'synchronous', 'post_reading']:
            # Find article with this timing
            timing_article = None
            timing_article_key = None
            for article_key, article_data in p['articles'].items():
                if article_data['timing'] == timing and article_data['mcq_total_questions'] > 0:
                    timing_article = article_data
                    timing_article_key = article_key
                    break
            
            if timing_article:
                t_total = timing_article['mcq_total_questions']
                t_ai = timing_article['mcq_ai_summary_total']
                t_art = timing_article['mcq_article_total']
                t_fl = timing_article['mcq_false_lure_total']
                
                row[f'{timing}_article'] = timing_article_key  # Add article name
                row[f'{timing}_mcq_accuracy'] = round((timing_article['mcq_total_correct'] / t_total * 100), 2) if t_total > 0 else None
                row[f'{timing}_ai_summary_accuracy'] = round((timing_article['mcq_ai_summary_correct'] / t_ai * 100), 2) if t_ai > 0 else None
                row[f'{timing}_article_accuracy'] = round((timing_article['mcq_article_correct'] / t_art * 100), 2) if t_art > 0 else None
                row[f'{timing}_false_lure_accuracy'] = round((timing_article['mcq_false_lure_correct'] / t_fl * 100), 2) if t_fl > 0 else None
                row[f'{timing}_false_lures_selected'] = timing_article['false_lures_selected']
                row[f'{timing}_recall_words'] = timing_article['recall_word_count']
                row[f'{timing}_recall_confidence'] = timing_article['recall_confidence']
                row[f'{timing}_reading_time_min'] = round(timing_article['reading_time_ms'] / 60000, 2)
                row[f'{timing}_summary_time_sec'] = round(timing_article['summary_time_seconds'], 2)
                row[f'{timing}_mental_effort'] = timing_article['post_mental_effort']
            else:
                row[f'{timing}_article'] = None  # Add article name placeholder
                for metric in ['mcq_accuracy', 'ai_summary_accuracy', 'article_accuracy',
                              'false_lure_accuracy', 'false_lures_selected', 'recall_words',
                              'recall_confidence', 'reading_time_min', 'summary_time_sec', 'mental_effort']:
                    row[f'{timing}_{metric}'] = None
        
        rows.append(row)
    
    # Create output
    if HAS_PANDAS:
        df = pd.DataFrame(rows)
        df.to_csv('analysis_dataset.csv', index=False)
        
        # Also create long format for repeated measures
        timing_metrics = []
        for timing in ['pre_reading', 'synchronous', 'post_reading']:
            for row in rows:
                if row.get(f'{timing}_mcq_accuracy') is not None:
                    timing_metrics.append({
                        'participant_id': row['participant_id'],
                        'experiment_group': row['experiment_group'],
                        'structure': row['structure'],
                        'timing': timing,
                        'article': row.get(f'{timing}_article'),  # Add article name
                        'mcq_accuracy': row[f'{timing}_mcq_accuracy'],
                        'ai_summary_accuracy': row.get(f'{timing}_ai_summary_accuracy'),
                        'article_accuracy': row.get(f'{timing}_article_accuracy'),
                        'false_lure_accuracy': row.get(f'{timing}_false_lure_accuracy'),
                        'false_lures_selected': row.get(f'{timing}_false_lures_selected'),
                        'recall_words': row.get(f'{timing}_recall_words'),
                        'recall_confidence': row.get(f'{timing}_recall_confidence'),
                        'reading_time_min': row.get(f'{timing}_reading_time_min'),
                        'summary_time_sec': row.get(f'{timing}_summary_time_sec'),
                        'mental_effort': row.get(f'{timing}_mental_effort'),
                        'prior_knowledge_familiarity': row['prior_knowledge_familiarity'],
                        'ai_trust': row['ai_trust'],
                        'ai_dependence': row['ai_dependence'],
                    })
        
        df_long = pd.DataFrame(timing_metrics)
        df_long.to_csv('analysis_dataset_long.csv', index=False)
        
        return df, df_long
    else:
        # Manual CSV creation without pandas
        if rows:
            fieldnames = list(rows[0].keys())
            with open('analysis_dataset.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
        return rows, None


def print_summary(df):
    """Print summary statistics."""
    print("\n" + "=" * 80)
    print("ANALYSIS DATASET SUMMARY")
    print("=" * 80)
    
    if HAS_PANDAS:
        print(f"\nTotal participants: {len(df)}")
        print(f"  - AI experiment: {len(df[df['experiment_group'] == 'AI'])}")
        print(f"  - No-AI experiment: {len(df[df['experiment_group'] == 'NoAI'])}")
        
        ai_df = df[df['experiment_group'] == 'AI']
        if len(ai_df) > 0:
            print(f"\nAI experiment breakdown:")
            print(f"  - Integrated: {len(ai_df[ai_df['structure'] == 'integrated'])}")
            print(f"  - Segmented: {len(ai_df[ai_df['structure'] == 'segmented'])}")
        
        print(f"\nKey metrics (AI group):")
        if len(ai_df) > 0:
            print(f"  - Mean Total MCQ Accuracy: {ai_df['total_mcq_accuracy'].mean():.1f}%")
            if 'ai_summary_accuracy' in ai_df.columns:
                print(f"  - Mean AI Summary Accuracy: {ai_df['ai_summary_accuracy'].mean():.1f}%")
            print(f"  - Mean Article-Only Accuracy: {ai_df['article_only_accuracy'].mean():.1f}%")
            if 'false_lure_rate' in ai_df.columns:
                print(f"  - Mean False Lure Rate: {ai_df['false_lure_rate'].mean():.1f}%")
        
        print(f"\nOutput files created:")
        print(f"  - analysis_dataset.csv (wide format, 1 row per participant)")
        print(f"  - analysis_dataset_long.csv (long format for repeated measures)")
        
        print(f"\nColumns in wide dataset: {len(df.columns)}")
        print(f"  {list(df.columns)}")
    else:
        print(f"\nTotal participants: {len(df)}")
        print("Note: Install pandas for detailed summary statistics")


if __name__ == "__main__":
    print("Creating analysis dataset...")
    print("-" * 80)
    
    result = create_master_dataset()
    
    if HAS_PANDAS:
        df, df_long = result
        print_summary(df)
    else:
        rows, _ = result
        print(f"\nCreated analysis_dataset.csv with {len(rows)} participants")
    
    print("\n" + "=" * 80)
    print("DONE! Your analysis dataset is ready.")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Open analysis_dataset.csv in Excel/Python/R")
    print("2. Follow ANALYSIS_PLAN.md for statistical analyses")
    print("3. Run the ANOVA code provided in the plan")
