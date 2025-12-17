#!/usr/bin/env python3
"""
CORRECTED cleaning script - Fixes BOTH ai_summary_accuracy (125→0.125) 
AND percentage values (50→0.50, 75→0.75, etc.)
"""

import pandas as pd
import numpy as np
import os

BASE_DIR = '/Users/duccioo/Desktop/ai_memory_experiment'
LONG_FILE = os.path.join(BASE_DIR, 'analysis_dataset_long.csv')
PARTICIPANT_FILE = os.path.join(BASE_DIR, 'analysis_dataset.csv')
OUTPUT_LONG = os.path.join(BASE_DIR, 'final_analysis', 'analysis_dataset_long_clean.csv')
OUTPUT_PARTICIPANT = os.path.join(BASE_DIR, 'final_analysis', 'analysis_dataset_clean.csv')

print("="*80)
print("CLEANING AI MEMORY EXPERIMENT DATASETS - FIXED VERSION")
print("="*80)

# Load data
print("\n1. Loading data...")
df_long = pd.read_csv(LONG_FILE)
df_participant = pd.read_csv(PARTICIPANT_FILE)
print(f"   ✓ Trial-level: {df_long.shape}, Participant-level: {df_participant.shape}")

# =============================================================================
# FIX 1: AI SUMMARY ACCURACY (125→0.125, 375→0.375, etc.)
# =============================================================================
print("\n2. Fixing ai_summary_accuracy (125→0.125, etc.)...")

ai_acc_cols_long = ['ai_summary_accuracy']
ai_acc_cols_part = ['ai_summary_accuracy', 'pre_reading_ai_summary_accuracy',
                    'synchronous_ai_summary_accuracy', 'post_reading_ai_summary_accuracy']

for col in ai_acc_cols_long:
    if col in df_long.columns:
        mask = df_long[col] > 1
        if mask.any():
            df_long.loc[mask, col] = df_long.loc[mask, col] / 1000
            print(f"   ✓ Trial-level {col}: Fixed {mask.sum()} values")

for col in ai_acc_cols_part:
    if col in df_participant.columns:
        mask = df_participant[col] > 1
        if mask.any():
            df_participant.loc[mask, col] = df_participant.loc[mask, col] / 1000
            print(f"   ✓ Participant-level {col}: Fixed {mask.sum()} values")

# =============================================================================
# FIX 2: ALL PERCENTAGE VALUES (50.0→0.50, 75.0→0.75, etc.)
# =============================================================================
print("\n3. Converting percentages to proportions...")

# All accuracy columns that might be stored as percentages
percentage_cols_long = ['mcq_accuracy', 'article_accuracy', 'false_lure_accuracy']
percentage_cols_part = ['total_mcq_accuracy', 'article_only_accuracy', 'false_lure_accuracy']

for col in percentage_cols_long:
    if col in df_long.columns:
        # Check if values look like percentages (anything > 1)
        mask = df_long[col] > 1
        if mask.any():
            df_long.loc[mask, col] = df_long.loc[mask, col] / 100
            print(f"   ✓ Trial-level {col}: Converted {mask.sum()} percentage values")

for col in percentage_cols_part:
    if col in df_participant.columns:
        mask = df_participant[col] > 1
        if mask.any():
            df_participant.loc[mask, col] = df_participant.loc[mask, col] / 100
            print(f"   ✓ Participant-level {col}: Converted {mask.sum()} percentage values")

# =============================================================================
# FIX 3: REMOVE UNUSED COLUMNS
# =============================================================================
print("\n4. Removing unused columns...")
cols_to_remove = ['prior_knowledge_recognition', 'prior_knowledge_quiz']
existing = [col for col in cols_to_remove if col in df_participant.columns]
if existing:
    df_participant = df_participant.drop(columns=existing)
    print(f"   ✓ Removed: {existing}")

# =============================================================================
# FIX 4: RECOMPUTE TOTAL_MCQ_ACCURACY
# =============================================================================
print("\n5. Recomputing total_mcq_accuracy...")
if 'total_mcq_correct' in df_participant.columns and 'total_mcq_questions' in df_participant.columns:
    df_participant['total_mcq_accuracy'] = (
        df_participant['total_mcq_correct'] / df_participant['total_mcq_questions']
    )
    print(f"   ✓ Recomputed for all {len(df_participant)} participants")

# =============================================================================
# FIX 5: FIX NOAI PARTICIPANTS
# =============================================================================
print("\n6. Fixing NoAI participants...")
noai_mask = df_participant['experiment_group'] == 'NoAI'
noai_count = noai_mask.sum()

if noai_count > 0:
    print(f"   Found {noai_count} NoAI participants")
    
    # Set AI columns to NaN
    ai_columns = ['ai_trust', 'ai_dependence', 'ai_summary_accuracy',
                  'pre_reading_ai_summary_accuracy', 'synchronous_ai_summary_accuracy',
                  'post_reading_ai_summary_accuracy']
    
    for col in ai_columns:
        if col in df_participant.columns:
            df_participant.loc[noai_mask, col] = np.nan
    
    print(f"   ✓ Set AI columns to NaN")
    
    # Fix corrupted avg_recall_difficulty
    df_participant.loc[noai_mask, 'avg_recall_difficulty'] = df_participant.loc[noai_mask, 'avg_mental_effort']
    print(f"   ✓ Fixed avg_recall_difficulty (was corrupted)")

# =============================================================================
# FIX 6: ENSURE NUMERIC TYPES
# =============================================================================
print("\n7. Ensuring proper numeric types...")

long_numeric = ['mcq_accuracy', 'ai_summary_accuracy', 'article_accuracy', 'false_lure_accuracy',
                'false_lures_selected', 'recall_words', 'recall_confidence', 'reading_time_min',
                'summary_time_sec', 'mental_effort', 'prior_knowledge_familiarity']

for col in long_numeric:
    if col in df_long.columns:
        df_long[col] = pd.to_numeric(df_long[col], errors='coerce')

part_numeric = ['age', 'total_mcq_accuracy', 'ai_summary_accuracy', 'article_only_accuracy',
                'false_lure_accuracy', 'avg_recall_words', 'avg_recall_confidence',
                'avg_mental_effort', 'avg_recall_difficulty']

for col in part_numeric:
    if col in df_participant.columns:
        df_participant[col] = pd.to_numeric(df_participant[col], errors='coerce')

print(f"   ✓ Converted numeric columns")

# =============================================================================
# SAVE
# =============================================================================
print("\n8. Saving cleaned files...")
df_long.to_csv(OUTPUT_LONG, index=False)
df_participant.to_csv(OUTPUT_PARTICIPANT, index=False)
print(f"   ✓ Saved to final_analysis/")

print("\n" + "="*80)
print("✅ CLEANING COMPLETE!")
print("="*80)
print("\nFixed:")
print("  ✓ ai_summary_accuracy (125→0.125, 375→0.375, etc.)")
print("  ✓ Percentage values (50→0.50, 75→0.75, 100→1.0, etc.)")
print("  ✓ Removed unused columns")
print("  ✓ Recomputed total_mcq_accuracy")
print("  ✓ Fixed NoAI participants")
print("  ✓ Ensured numeric types")
print("\n🎉 Data ready for analysis!")
