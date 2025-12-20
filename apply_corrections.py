#!/usr/bin/env python3
"""
Apply specific corrections to the analysis datasets based on manual verification.

Corrections:
- P241: False lures selected = 5 (was 6)
- P246: False lures selected = 5 (was 6)
- P245: AI Summary Accuracy = 87.5% (was 100%)
- P243: AI Summary Accuracy = 91.6% (was 100%)
"""

import pandas as pd
import sys

def apply_corrections():
    # Load datasets
    try:
        wide = pd.read_csv('analysis_dataset.csv')
        long = pd.read_csv('analysis_dataset_long.csv')
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please run create_analysis_dataset.py first")
        return False
    
    print("Applying manual corrections...")
    
    # === WIDE DATASET CORRECTIONS ===
    
    # P241: False lures selected = 5 (was 6)
    idx_241 = wide['participant_id'] == 'P241'
    old_241_fl = wide.loc[idx_241, 'false_lures_selected'].values[0]
    wide.loc[idx_241, 'false_lures_selected'] = 5
    # Recalculate false_lure_rate (out of 6 total false lure questions)
    wide.loc[idx_241, 'false_lure_rate'] = round((5 / 6 * 100), 2)  # 5 out of 6 = 83.33%
    print(f"✓ P241: false_lures_selected {old_241_fl} → 5, false_lure_rate updated to 83.33%")
    
    # P246: False lures selected = 5 (was 6)
    idx_246 = wide['participant_id'] == 'P246'
    old_246_fl = wide.loc[idx_246, 'false_lures_selected'].values[0]
    wide.loc[idx_246, 'false_lures_selected'] = 5
    # Recalculate false_lure_rate
    wide.loc[idx_246, 'false_lure_rate'] = round((5 / 6 * 100), 2)  # 83.33%
    print(f"✓ P246: false_lures_selected {old_246_fl} → 5, false_lure_rate updated to 83.33%")
    
    # P245: AI Summary Accuracy = 87.5% (was 100%)
    idx_245 = wide['participant_id'] == 'P245'
    old_245_ai = wide.loc[idx_245, 'ai_summary_accuracy'].values[0]
    wide.loc[idx_245, 'ai_summary_accuracy'] = 87.5
    print(f"✓ P245: ai_summary_accuracy {old_245_ai}% → 87.5%")
    
    # P243: AI Summary Accuracy = 91.6% (was 100%)
    idx_243 = wide['participant_id'] == 'P243'
    old_243_ai = wide.loc[idx_243, 'ai_summary_accuracy'].values[0]
    wide.loc[idx_243, 'ai_summary_accuracy'] = 91.6
    # Note: user specified 0.916, which is 91.6%
    print(f"✓ P243: ai_summary_accuracy {old_243_ai}% → 91.6%")
    
    # === LONG DATASET CORRECTIONS ===
    # Note: For the long dataset, we need to apply corrections proportionally
    # Since we don't know which specific articles have the corrections,
    # we'll need to adjust the aggregates only
    
    # For false lures, we assume the correction applies to specific articles
    # But without knowing which ones, we keep long dataset as-is for now
    # (The wide dataset is the authoritative summary)
    
    print("\nLong dataset note: Corrections applied to wide dataset summary values.")
    print("If specific per-article corrections are needed in long dataset, please specify which articles.")
    
    # Save corrected datasets
    wide.to_csv('analysis_dataset.csv', index=False)
    long.to_csv('analysis_dataset_long.csv', index=False)
    
    print("\n✓ Corrected datasets saved:")
    print("  - analysis_dataset.csv")
    print("  - analysis_dataset_long.csv")
    
    return True

if __name__ == '__main__':
    success = apply_corrections()
    sys.exit(0 if success else 1)



