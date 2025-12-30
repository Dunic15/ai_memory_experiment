#!/usr/bin/env python3
"""
Recalculate synchronous reading times excluding summary viewing time
This script analyzes the reading times and adjusts synchronous times to exclude 
the time spent viewing the summary overlay.
"""

import csv
import json
import os
from glob import glob

def parse_log_file(log_file_path):
    """Parse a participant log file and extract reading data"""
    data = {
        'reading_data': [],
        'participant_id': os.path.basename(log_file_path).split('-')[0]
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
            
            if phase == 'reading_behavior' and len(parts) > 2:
                event_type = parts[2]
                
                if event_type == 'reading_complete':
                    # Schema: timestamp, phase, reading_complete, timestamp2, reading_time_ms, summary_time_ms, overlay_count, scroll_depth, article_num, article_key, timing
                    reading_time_ms = 0
                    summary_time_ms = 0
                    article_num = -1
                    article_key = ''
                    timing = ''
                    
                    if len(parts) > 4:
                        try:
                            reading_time_ms = int(parts[4])
                        except:
                            pass
                    
                    if len(parts) > 5:
                        try:
                            summary_time_ms = int(parts[5])
                        except:
                            pass
                    
                    if len(parts) > 8:
                        try:
                            article_num = int(parts[8])
                        except:
                            pass
                    
                    if len(parts) > 9:
                        article_key = parts[9]
                    
                    if len(parts) > 10:
                        timing = parts[10]
                    
                    data['reading_data'].append({
                        'article_num': article_num,
                        'article_key': article_key,
                        'timing': timing,
                        'reading_time_ms': reading_time_ms,
                        'summary_time_ms': summary_time_ms,
                        'adjusted_reading_time_ms': reading_time_ms - summary_time_ms if timing == 'synchronous' else reading_time_ms
                    })
    
    return data

def calculate_statistics():
    """Calculate reading time statistics for all participants"""
    
    # Find all log files
    log_files = glob('/Users/duccioo/Desktop/ai_memory_experiment/ai_experiment/experiment_data/P*-*-*.csv')
    
    # Storage for statistics
    integrated_pre = []
    integrated_sync = []
    integrated_post = []
    segmented_pre = []
    segmented_sync = []
    segmented_post = []
    non_ai = []
    
    integrated_sync_adjusted = []
    segmented_sync_adjusted = []
    
    print("=" * 80)
    print("READING TIME ANALYSIS - WITH SYNCHRONOUS ADJUSTMENT")
    print("=" * 80)
    print()
    
    # Process each file
    for log_file in sorted(log_files):
        data = parse_log_file(log_file)
        participant_id = data['participant_id']
        
        # Determine if integrated or segmented based on filename
        filename = os.path.basename(log_file)
        if 'Integrated' in filename:
            structure = 'integrated'
        elif 'Segmented' in filename:
            structure = 'segmented'
        else:
            continue  # Skip files without structure info
        
        # Process reading data
        for rd in data['reading_data']:
            timing = rd['timing']
            reading_time_min = rd['reading_time_ms'] / 60000
            adjusted_time_min = rd['adjusted_reading_time_ms'] / 60000
            summary_time_min = rd['summary_time_ms'] / 60000
            
            # Print synchronous articles with adjustment details
            if timing == 'synchronous':
                print(f"{participant_id} - {rd['article_key']} ({structure}, synchronous):")
                print(f"  Original Reading Time: {reading_time_min:.2f} min")
                print(f"  Summary Viewing Time: {summary_time_min:.2f} min")
                print(f"  Adjusted Reading Time: {adjusted_time_min:.2f} min (excluding summary time)")
                print()
            
            # Categorize by structure and timing
            if structure == 'integrated':
                if timing == 'pre_reading':
                    integrated_pre.append(reading_time_min)
                elif timing == 'synchronous':
                    integrated_sync.append(reading_time_min)
                    integrated_sync_adjusted.append(adjusted_time_min)
                elif timing == 'post_reading':
                    integrated_post.append(reading_time_min)
            elif structure == 'segmented':
                if timing == 'pre_reading':
                    segmented_pre.append(reading_time_min)
                elif timing == 'synchronous':
                    segmented_sync.append(reading_time_min)
                    segmented_sync_adjusted.append(adjusted_time_min)
                elif timing == 'post_reading':
                    segmented_post.append(reading_time_min)
    
    # Calculate averages
    print()
    print("=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    print()
    
    def avg(lst):
        return sum(lst) / len(lst) if lst else 0
    
    print("INTEGRATED (With AI):")
    print(f"  Pre-reading:   {avg(integrated_pre):.2f} min (n={len(integrated_pre)})")
    print(f"  Synchronous:   {avg(integrated_sync):.2f} min (ORIGINAL - includes summary time) (n={len(integrated_sync)})")
    print(f"  Synchronous:   {avg(integrated_sync_adjusted):.2f} min (ADJUSTED - excludes summary time) (n={len(integrated_sync_adjusted)})")
    print(f"  Post-reading:  {avg(integrated_post):.2f} min (n={len(integrated_post)})")
    print(f"  Average (ORIGINAL): {avg(integrated_pre + integrated_sync + integrated_post):.2f} min")
    print(f"  Average (ADJUSTED): {avg(integrated_pre + integrated_sync_adjusted + integrated_post):.2f} min")
    print()
    
    print("SEGMENTED (With AI):")
    print(f"  Pre-reading:   {avg(segmented_pre):.2f} min (n={len(segmented_pre)})")
    print(f"  Synchronous:   {avg(segmented_sync):.2f} min (ORIGINAL - includes summary time) (n={len(segmented_sync)})")
    print(f"  Synchronous:   {avg(segmented_sync_adjusted):.2f} min (ADJUSTED - excludes summary time) (n={len(segmented_sync_adjusted)})")
    print(f"  Post-reading:  {avg(segmented_post):.2f} min (n={len(segmented_post)})")
    print(f"  Average (ORIGINAL): {avg(segmented_pre + segmented_sync + segmented_post):.2f} min")
    print(f"  Average (ADJUSTED): {avg(segmented_pre + segmented_sync_adjusted + segmented_post):.2f} min")
    print()
    
    print("COMPARISON TABLE:")
    print("-" * 80)
    print(f"{'Condition':<20} | {'Pre-reading':<12} | {'Synchronous (Orig)':<20} | {'Synchronous (Adj)':<20} | {'Post-reading':<12}")
    print("-" * 80)
    print(f"{'Integrated':<20} | {avg(integrated_pre):>12.2f} | {avg(integrated_sync):>20.2f} | {avg(integrated_sync_adjusted):>20.2f} | {avg(integrated_post):>12.2f}")
    print(f"{'Segmented':<20} | {avg(segmented_pre):>12.2f} | {avg(segmented_sync):>20.2f} | {avg(segmented_sync_adjusted):>20.2f} | {avg(segmented_post):>12.2f}")
    print("-" * 80)
    print()
    
    print("OVERALL AVERAGES:")
    print(f"  Integrated (ORIGINAL): {avg(integrated_pre + integrated_sync + integrated_post):.2f} min")
    print(f"  Integrated (ADJUSTED): {avg(integrated_pre + integrated_sync_adjusted + integrated_post):.2f} min")
    print(f"  Segmented  (ORIGINAL): {avg(segmented_pre + segmented_sync + segmented_post):.2f} min")
    print(f"  Segmented  (ADJUSTED): {avg(segmented_pre + segmented_sync_adjusted + segmented_post):.2f} min")
    print()
    
    # Calculate the difference
    sync_diff_integrated = avg(integrated_sync) - avg(integrated_sync_adjusted)
    sync_diff_segmented = avg(segmented_sync) - avg(segmented_sync_adjusted)
    
    print("SYNCHRONOUS TIME DIFFERENCE (Summary Viewing Time):")
    print(f"  Integrated: {sync_diff_integrated:.2f} min average spent viewing summary")
    print(f"  Segmented:  {sync_diff_segmented:.2f} min average spent viewing summary")
    print()
    
    # Calculate overall With AI average (all conditions combined)
    all_with_ai_original = integrated_pre + integrated_sync + integrated_post + segmented_pre + segmented_sync + segmented_post
    all_with_ai_adjusted = integrated_pre + integrated_sync_adjusted + integrated_post + segmented_pre + segmented_sync_adjusted + segmented_post
    
    print("=" * 80)
    print("RECALCULATED AVERAGES FOR YOUR TABLE")
    print("=" * 80)
    print()
    print("INDIVIDUAL CONDITION AVERAGES (ADJUSTED):")
    print(f"  Integrated - Pre-reading:   {avg(integrated_pre):.2f} min")
    print(f"  Integrated - Synchronous:   {avg(integrated_sync_adjusted):.2f} min (ADJUSTED - excluding summary time)")
    print(f"  Integrated - Post-reading:  {avg(integrated_post):.2f} min")
    print(f"  → Average for Integrated:   {avg(integrated_pre + integrated_sync_adjusted + integrated_post):.2f} min")
    print()
    print(f"  Segmented - Pre-reading:    {avg(segmented_pre):.2f} min")
    print(f"  Segmented - Synchronous:    {avg(segmented_sync_adjusted):.2f} min (ADJUSTED - excluding summary time)")
    print(f"  Segmented - Post-reading:   {avg(segmented_post):.2f} min")
    print(f"  → Average for Segmented:    {avg(segmented_pre + segmented_sync_adjusted + segmented_post):.2f} min")
    print()
    print(f"  → Overall average for With AI: {avg(all_with_ai_adjusted):.2f} min")
    print()
    print("=" * 80)
    print("FORMATTED FOR YOUR SPREADSHEET")
    print("=" * 80)
    print()
    print("Row 6 values (adjusted synchronous):")
    print(f"  Integrated pre_reading:   {avg(integrated_pre):.2f}")
    print(f"  Integrated synchronous:   {avg(integrated_sync_adjusted):.2f}")
    print(f"  Integrated post_reading:  {avg(integrated_post):.2f}")
    print(f"  Segmented pre_reading:    {avg(segmented_pre):.2f}")
    print(f"  Segmented synchronous:    {avg(segmented_sync_adjusted):.2f}")
    print(f"  Segmented post_reading:   {avg(segmented_post):.2f}")
    print()
    print("Row 7 (averages by structure):")
    print(f"  Average for integrated:   {avg(integrated_pre + integrated_sync_adjusted + integrated_post):.2f}")
    print(f"  Average for segmented:    {avg(segmented_pre + segmented_sync_adjusted + segmented_post):.2f}")
    print()
    print("Row 8 (overall averages):")
    print(f"  Average for with AI:      {avg(all_with_ai_adjusted):.2f}")
    print()

if __name__ == '__main__':
    calculate_statistics()
