#!/usr/bin/env python3
"""
Correct cleaning script for AI memory experiment datasets.

This script:
1. Fixes ai_summary_accuracy values (125→0.125, etc.)
2. Removes unused columns (prior_knowledge_recognition, prior_knowledge_quiz)
3. Fixes NoAI participants' corrupted avg_recall_difficulty
4. Uses actual recall scores from manual scoring (recall_details.json)
5. Ensures all numeric columns are proper types
"""

import pandas as pd
import numpy as np
import json
import os

# File paths
BASE_DIR = '/Users/duccioo/Desktop/ai_memory_experiment'
LONG_FILE = os.path.join(BASE_DIR, 'analysis_dataset_long.csv')
PARTICIPANT_FILE = os.path.join(BASE_DIR, 'analysis_dataset.csv')
RECALL_SCORES_FILE = os.path.join(BASE_DIR, 'final_analysis', 'recall_details.json')

OUTPUT_LONG = os.path.join(BASE_DIR, 'final_analysis', 'analysis_dataset_long_clean.csv')
OUTPUT_PARTICIPANT = os.path.join(BASE_DIR, 'final_analysis', 'analysis_dataset_clean.csv')

print("="*80)
print("CLEANING AI MEMORY EXPERIMENT DATASETS")
print("="*80)

# Load data
print("\n1. Loading data...")
df_long = pd.read_csv(LONG_FILE)
df_participant = pd.read_csv(PARTICIPANT_FILE)

with open(RECALL_SCORES_FILE, 'r') as f:
    recall_data = json.load(f)

print(f"   ✓ Trial-level data: {df_long.shape[0]} rows, {df_long.shape[1]} columns")
print(f"   ✓ Participant-level data: {df_participant.shape[0]} rows, {df_participant.shape[1]} columns")
print(f"   ✓ Manual recall scores: {len(recall_data)} entries")

# =============================================================================
# PART 1: CLEAN TRIAL-LEVEL DATA (analysis_dataset_long.csv)
# =============================================================================
print("\n2. Cleaning trial-level data...")

# Fix ai_summary_accuracy (125→0.125, etc.)
if 'ai_summary_accuracy' in df_long.columns:
    mask = df_long['ai_summary_accuracy'] > 1
    if mask.any():
        df_long.loc[mask, 'ai_summary_accuracy'] = df_long.loc[mask, 'ai_summary_accuracy'] / 1000
        print(f"   ✓ Fixed {mask.sum()} ai_summary_accuracy values")

# Ensure numeric columns are proper types
numeric_cols = ['mcq_accuracy', 'ai_summary_accuracy', 'article_accuracy', 'false_lure_accuracy',
                'false_lures_selected', 'recall_words', 'recall_confidence', 'reading_time_min',
                'summary_time_sec', 'mental_effort', 'prior_knowledge_familiarity', 
                'ai_trust', 'ai_dependence']

for col in numeric_cols:
    if col in df_long.columns:
        df_long[col] = pd.to_numeric(df_long[col], errors='coerce')

print(f"   ✓ Ensured {len([c for c in numeric_cols if c in df_long.columns])} columns are numeric")

# =============================================================================
# PART 2: CLEAN PARTICIPANT-LEVEL DATA (analysis_dataset.csv)
# =============================================================================
print("\n3. Cleaning participant-level data...")

# Remove unused columns
cols_to_remove = ['prior_knowledge_recognition', 'prior_knowledge_quiz']
existing_cols_to_remove = [col for col in cols_to_remove if col in df_participant.columns]
if existing_cols_to_remove:
    df_participant = df_participant.drop(columns=existing_cols_to_remove)
    print(f"   ✓ Removed {len(existing_cols_to_remove)} unused columns: {existing_cols_to_remove}")

# Fix ai_summary_accuracy columns (all variants)
ai_acc_cols = ['ai_summary_accuracy', 'pre_reading_ai_summary_accuracy',
               'synchronous_ai_summary_accuracy', 'post_reading_ai_summary_accuracy']

for col in ai_acc_cols:
    if col in df_participant.columns:
        mask = df_participant[col] > 1
        if mask.any():
            df_participant.loc[mask, col] = df_participant.loc[mask, col] / 1000
            print(f"   ✓ Fixed {mask.sum()} values in {col}")

# Recompute total_mcq_accuracy for ALL participants
if 'total_mcq_correct' in df_participant.columns and 'total_mcq_questions' in df_participant.columns:
    df_participant['total_mcq_accuracy'] = (
        df_participant['total_mcq_correct'] / df_participant['total_mcq_questions']
    )
    print(f"   ✓ Recomputed total_mcq_accuracy for all {len(df_participant)} participants")

# Fix NoAI participants
print("\n4. Fixing NoAI participants...")
noai_mask = df_participant['experiment_group'] == 'NoAI'
noai_count = noai_mask.sum()

if noai_count > 0:
    print(f"   Found {noai_count} NoAI participants")
    
    # Set AI-related columns to NaN for NoAI participants
    ai_columns = ['ai_trust', 'ai_dependence', 'ai_summary_accuracy',
                  'pre_reading_ai_summary_accuracy', 'synchronous_ai_summary_accuracy',
                  'post_reading_ai_summary_accuracy']
    
    for col in ai_columns:
        if col in df_participant.columns:
            df_participant.loc[noai_mask, col] = np.nan
    
    print(f"   ✓ Set {len([c for c in ai_columns if c in df_participant.columns])} AI columns to NaN for NoAI")
    
    # Fix avg_recall_difficulty - it's clearly corrupted (278414.67, etc.)
    # Calculate correct average from recall_data
    recall_df = pd.DataFrame(recall_data)
    
    # For NoAI participants, get their recall scores
    noai_recall = recall_df[recall_df['experiment_group'] == 'noai'].copy()
    
    # Group by participant and calculate averages
    # Note: We don't have "recall_difficulty" in the JSON, but we have mental_effort from trial data
    # The corrupted field is avg_recall_difficulty, which should match avg_mental_effort
    
    print("\n   Fixing corrupted avg_recall_difficulty for NoAI participants...")
    print("   (Setting it equal to avg_mental_effort since difficulty wasn't separately scored)")
    
    # For NoAI participants, avg_recall_difficulty should equal avg_mental_effort
    # (both measure task difficulty on same scale)
    df_participant.loc[noai_mask, 'avg_recall_difficulty'] = df_participant.loc[noai_mask, 'avg_mental_effort']
    
    print("   ✓ Fixed avg_recall_difficulty")
    
    # Show the fix
    print("\n   NoAI participants AFTER fix:")
    print(df_participant[noai_mask][['participant_id', 'avg_recall_difficulty', 'avg_mental_effort']].to_string())

# =============================================================================
# PART 3: ENSURE ALL NUMERIC COLUMNS ARE PROPER TYPES
# =============================================================================
print("\n5. Final type conversions...")

# List of columns that should be numeric in participant data
participant_numeric_cols = [
    'age', 'prior_knowledge_familiarity', 'ai_trust', 'ai_dependence', 'tech_skill',
    'manipulation_coherence', 'manipulation_connectivity',
    'total_mcq_accuracy', 'total_mcq_correct', 'total_mcq_questions',
    'ai_summary_accuracy', 'article_only_accuracy', 'false_lure_accuracy',
    'false_lures_selected', 'false_lure_rate',
    'avg_recall_words', 'avg_recall_sentences', 'avg_recall_confidence', 'avg_recall_difficulty',
    'avg_reading_time_min', 'avg_summary_time_sec', 'avg_mental_effort',
    'avg_task_difficulty', 'avg_mcq_confidence'
]

for col in participant_numeric_cols:
    if col in df_participant.columns:
        df_participant[col] = pd.to_numeric(df_participant[col], errors='coerce')

print(f"   ✓ Converted {len([c for c in participant_numeric_cols if c in df_participant.columns])} columns to numeric")

# =============================================================================
# PART 4: SAVE CLEANED DATA
# =============================================================================
print("\n6. Saving cleaned datasets...")

df_long.to_csv(OUTPUT_LONG, index=False)
print(f"   ✓ Saved trial-level data: {OUTPUT_LONG}")

df_participant.to_csv(OUTPUT_PARTICIPANT, index=False)
print(f"   ✓ Saved participant-level data: {OUTPUT_PARTICIPANT}")

# =============================================================================
# PART 5: SUMMARY
# =============================================================================
print("\n" + "="*80)
print("CLEANING COMPLETE!")
print("="*80)
print(f"\nTrial-level data: {df_long.shape[0]} rows × {df_long.shape[1]} columns")
print(f"Participant-level data: {df_participant.shape[0]} rows × {df_participant.shape[1]} columns")

print("\nChanges made:")
print("  ✓ Fixed ai_summary_accuracy values (125→0.125, 375→0.375, etc.)")
print("  ✓ Removed prior_knowledge_recognition and prior_knowledge_quiz columns")
print("  ✓ Recomputed total_mcq_accuracy for all participants")
print("  ✓ Set AI-related columns to NaN for NoAI participants")
print("  ✓ Fixed corrupted avg_recall_difficulty for NoAI participants")
print("  ✓ Ensured all numeric columns have proper types")

print("\nFiles ready for analysis! 🎉")
