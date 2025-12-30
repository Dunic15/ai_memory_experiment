#!/usr/bin/env python3
"""
Calculate recall total scores from participant data
"""

# Data extracted from the spreadsheet
# Format: (participant, condition, structure, timing, article, recall_score)
data = [
    # Integrated + pre_reading
    ("P233", "ai", "integrated", "pre_reading", "semiconductors", 7.0),
    ("P234", "ai", "integrated", "pre_reading", "crispr", 2.5),
    ("P235", "ai", "integrated", "pre_reading", "crispr", 2.5),
    ("P236", "ai", "integrated", "pre_reading", "semiconductors", 3.5),
    ("P243", "ai", "integrated", "pre_reading", "uhi", 9.0),
    ("P246", "ai", "integrated", "pre_reading", "semiconductors", 8.5),
    ("P251", "ai", "integrated", "pre_reading", "uhi", 4.0),
    ("P253", "ai", "integrated", "pre_reading", "crispr", 6.5),
    ("P258", "ai", "integrated", "pre_reading", "crispr", 4.5),
    ("P260", "ai", "integrated", "pre_reading", "crispr", 7.0),
    ("P261", "ai", "integrated", "pre_reading", "uhi", 4.5),
    ("P265", "ai", "integrated", "pre_reading", "semiconductors", 5.5),
    
    # Integrated + synchronous
    ("P233", "ai", "integrated", "synchronous", "crispr", 6.5),
    ("P234", "ai", "integrated", "synchronous", "uhi", 3.0),
    ("P235", "ai", "integrated", "synchronous", "semiconductors", 3.0),
    ("P236", "ai", "integrated", "synchronous", "uhi", 6.5),
    ("P243", "ai", "integrated", "synchronous", "crispr", 8.5),
    ("P246", "ai", "integrated", "synchronous", "uhi", 8.0),
    ("P251", "ai", "integrated", "synchronous", "crispr", 5.0),
    ("P253", "ai", "integrated", "synchronous", "semiconductors", 3.5),
    ("P258", "ai", "integrated", "synchronous", "semiconductors", 3.0),
    ("P260", "ai", "integrated", "synchronous", "semiconductors", 6.0),
    ("P261", "ai", "integrated", "synchronous", "semiconductors", 5.0),
    ("P265", "ai", "integrated", "synchronous", "crispr", 5.5),
    
    # Integrated + post_reading
    ("P233", "ai", "integrated", "post_reading", "uhi", 7.0),
    ("P234", "ai", "integrated", "post_reading", "semiconductors", 2.0),
    ("P235", "ai", "integrated", "post_reading", "uhi", 3.0),
    ("P236", "ai", "integrated", "post_reading", "crispr", 4.0),
    ("P243", "ai", "integrated", "post_reading", "semiconductors", 8.0),
    ("P246", "ai", "integrated", "post_reading", "crispr", 8.0),
    ("P251", "ai", "integrated", "post_reading", "semiconductors", 3.5),
    ("P253", "ai", "integrated", "post_reading", "uhi", 3.0),
    ("P258", "ai", "integrated", "post_reading", "uhi", 5.0),
    ("P260", "ai", "integrated", "post_reading", "uhi", 7.5),
    ("P261", "ai", "integrated", "post_reading", "crispr", 2.5),
    ("P265", "ai", "integrated", "post_reading", "uhi", 8.5),
    
    # Segmented + pre_reading
    ("P239", "ai", "segmented", "pre_reading", "uhi", 8.5),
    ("P240", "ai", "segmented", "pre_reading", "uhi", 3.0),
    ("P241", "ai", "segmented", "pre_reading", "semiconductors", 7.5),
    ("P245", "ai", "segmented", "pre_reading", "semiconductors", 5.0),
    ("P250", "ai", "segmented", "pre_reading", "crispr", 3.5),
    ("P252", "ai", "segmented", "pre_reading", "uhi", 4.0),
    ("P254", "ai", "segmented", "pre_reading", "semiconductors", 6.5),
    ("P257", "ai", "segmented", "pre_reading", "uhi", 4.5),
    ("P259", "ai", "segmented", "pre_reading", "crispr", 5.0),
    ("P263", "ai", "segmented", "pre_reading", "semiconductors", 6.5),
    ("P264", "ai", "segmented", "pre_reading", "crispr", 6.0),
    ("P266", "ai", "segmented", "pre_reading", "semiconductors", 7.0),
    
    # Segmented + synchronous
    ("P239", "ai", "segmented", "synchronous", "semiconductors", 9.0),
    ("P240", "ai", "segmented", "synchronous", "crispr", 1.5),
    ("P241", "ai", "segmented", "synchronous", "crispr", 7.5),
    ("P245", "ai", "segmented", "synchronous", "uhi", 7.5),
    ("P250", "ai", "segmented", "synchronous", "semiconductors", 6.0),
    ("P252", "ai", "segmented", "synchronous", "crispr", 3.0),
    ("P254", "ai", "segmented", "synchronous", "crispr", 5.5),
    ("P257", "ai", "segmented", "synchronous", "crispr", 5.5),
    ("P259", "ai", "segmented", "synchronous", "semiconductors", 4.5),
    ("P263", "ai", "segmented", "synchronous", "crispr", 6.0),
    ("P264", "ai", "segmented", "synchronous", "uhi", 5.5),
    ("P266", "ai", "segmented", "synchronous", "uhi", 8.5),
    
    # Segmented + post_reading
    ("P239", "ai", "segmented", "post_reading", "crispr", 8.5),
    ("P240", "ai", "segmented", "post_reading", "semiconductors", 3.5),
    ("P241", "ai", "segmented", "post_reading", "uhi", 8.0),
    ("P245", "ai", "segmented", "post_reading", "crispr", 6.5),
    ("P250", "ai", "segmented", "post_reading", "uhi", 3.0),
    ("P252", "ai", "segmented", "post_reading", "semiconductors", 3.5),
    ("P254", "ai", "segmented", "post_reading", "uhi", 7.0),
    ("P257", "ai", "segmented", "post_reading", "semiconductors", 5.5),
    ("P259", "ai", "segmented", "post_reading", "uhi", 5.0),
    ("P263", "ai", "segmented", "post_reading", "uhi", 6.5),
    ("P264", "ai", "segmented", "post_reading", "semiconductors", 7.0),
    ("P266", "ai", "segmented", "post_reading", "crispr", 7.5),
    
    # Non AI - control group
    ("P171", "control", "control", "control", "semiconductors", 6.5),
    ("P171", "control", "control", "control", "uhi", 7.5),
    ("P171", "control", "control", "control", "crispr", 3.5),
    ("P172", "control", "control", "control", "semiconductors", 6.0),
    ("P172", "control", "control", "control", "uhi", 8.0),
    ("P172", "control", "control", "control", "crispr", 8.5),
    ("P175", "control", "control", "control", "semiconductors", 6.0),
    ("P175", "control", "control", "control", "uhi", 6.5),
    ("P175", "control", "control", "control", "crispr", 5.0),
    ("P178", "control", "control", "control", "semiconductors", 3.5),
    ("P178", "control", "control", "control", "uhi", 3.5),
    ("P178", "control", "control", "control", "crispr", 4.5),
    ("P180", "control", "control", "control", "semiconductors", 3.5),
    ("P180", "control", "control", "control", "uhi", 4.0),
    ("P180", "control", "control", "control", "crispr", 4.0),
    ("P181", "control", "control", "control", "semiconductors", 7.5),
    ("P181", "control", "control", "control", "uhi", 6.5),
    ("P181", "control", "control", "control", "crispr", 7.0),
    ("P182", "control", "control", "control", "semiconductors", 6.5),
    ("P182", "control", "control", "control", "uhi", 8.0),
    ("P182", "control", "control", "control", "crispr", 7.5),
    ("P183", "control", "control", "control", "uhi", 4.5),
    ("P183", "control", "control", "control", "crispr", 4.5),
    ("P183", "control", "control", "control", "semiconductors", 4.0),
    ("P184", "control", "control", "control", "uhi", 8.0),
    ("P184", "control", "control", "control", "semiconductors", 3.5),
    ("P184", "control", "control", "control", "crispr", 4.5),
    ("P186", "control", "control", "control", "uhi", 3.5),
    ("P186", "control", "control", "control", "semiconductors", 3.0),
    ("P186", "control", "control", "control", "crispr", 4.0),
    ("P187", "control", "control", "control", "semiconductors", 7.0),
    ("P187", "control", "control", "control", "crispr", 6.5),
    ("P187", "control", "control", "control", "uhi", 7.0),
    ("P188", "control", "control", "control", "semiconductors", 3.0),
    ("P188", "control", "control", "control", "crispr", 4.0),
    ("P188", "control", "control", "control", "uhi", 4.0),
    ("P233", "ai", "integrated", "pre_reading", "semiconductors", 0.9),
    ("P234", "ai", "integrated", "pre_reading", "crispr", 0.83),
    ("P234", "ai", "integrated", "pre_reading", "semiconductors", 0.5),
    ("P236", "ai", "integrated", "pre_reading", "crispr", 0.71),
    ("P236", "ai", "integrated", "pre_reading", "semiconductors", 0.9),
    ("P243", "ai", "integrated", "pre_reading", "crispr", 0.1),
    ("P243", "ai", "integrated", "pre_reading", "semiconductors", 0.5),
    ("P246", "ai", "integrated", "pre_reading", "crispr", 0.71),
    ("P246", "ai", "integrated", "pre_reading", "semiconductors", 0.7),
    ("P251", "ai", "integrated", "pre_reading", "crispr", 0.1),
    ("P251", "ai", "integrated", "pre_reading", "semiconductors", 0.3),
    ("P253", "ai", "integrated", "pre_reading", "crispr", 0.71),
    ("P253", "ai", "integrated", "pre_reading", "semiconductors", 0.7),
    ("P258", "ai", "integrated", "pre_reading", "crispr", 0.1),
    ("P258", "ai", "integrated", "pre_reading", "semiconductors", 0.3),
    ("P260", "ai", "integrated", "pre_reading", "crispr", 0.71),
    ("P260", "ai", "integrated", "pre_reading", "semiconductors", 0.7),
    ("P261", "ai", "integrated", "pre_reading", "crispr", 0.71),
    ("P261", "ai", "integrated", "pre_reading", "semiconductors", 0.7),
    ("P265", "ai", "integrated", "pre_reading", "crispr", 0.71),
    ("P265", "ai", "integrated", "pre_reading", "semiconductors", 0.7),
    
    # Integrated + synchronous
    ("P233", "ai", "integrated", "synchronous", "uhi", 0.71),
    ("P234", "ai", "integrated", "synchronous", "uhi", 0.5),
    ("P236", "ai", "integrated", "synchronous", "uhi", 0.71),
    ("P243", "ai", "integrated", "synchronous", "uhi", 0.1),
    ("P246", "ai", "integrated", "synchronous", "uhi", 0.71),
    ("P251", "ai", "integrated", "synchronous", "uhi", 0.1),
    ("P253", "ai", "integrated", "synchronous", "uhi", 0.71),
    ("P258", "ai", "integrated", "synchronous", "uhi", 0.1),
    ("P260", "ai", "integrated", "synchronous", "uhi", 0.71),
    ("P261", "ai", "integrated", "synchronous", "uhi", 0.71),
    ("P265", "ai", "integrated", "synchronous", "uhi", 0.71),
    
    # Integrated + post_reading
    ("P233", "ai", "integrated", "post_reading", "semiconductors", 0.2),
    ("P234", "ai", "integrated", "post_reading", "semiconductors", 0.9),
    ("P236", "ai", "integrated", "post_reading", "semiconductors", 0.2),
    ("P243", "ai", "integrated", "post_reading", "semiconductors", 0.3),
    ("P246", "ai", "integrated", "post_reading", "semiconductors", 0.2),
    ("P251", "ai", "integrated", "post_reading", "semiconductors", 0.9),
    ("P253", "ai", "integrated", "post_reading", "semiconductors", 0.2),
    ("P258", "ai", "integrated", "post_reading", "semiconductors", 0.9),
    ("P260", "ai", "integrated", "post_reading", "semiconductors", 0.2),
    ("P261", "ai", "integrated", "post_reading", "semiconductors", 0.2),
    ("P265", "ai", "integrated", "post_reading", "semiconductors", 0.2),
    
    # Segmented + pre_reading
    ("P239", "ai", "segmented", "pre_reading", "crispr", 0.71),
    ("P239", "ai", "segmented", "pre_reading", "uhi", 0.71),
    ("P240", "ai", "segmented", "pre_reading", "semiconductors", 0.7),
    ("P240", "ai", "segmented", "pre_reading", "uhi", 0.71),
    ("P245", "ai", "segmented", "pre_reading", "crispr", 0.71),
    ("P245", "ai", "segmented", "pre_reading", "semiconductors", 0.7),
    ("P249", "ai", "segmented", "pre_reading", "crispr", 0.71),
    ("P249", "ai", "segmented", "pre_reading", "uhi", 0.71),
    ("P250", "ai", "segmented", "pre_reading", "crispr", 0.71),
    ("P250", "ai", "segmented", "pre_reading", "uhi", 0.71),
    ("P252", "ai", "segmented", "pre_reading", "semiconductors", 0.7),
    ("P252", "ai", "segmented", "pre_reading", "uhi", 0.71),
    ("P254", "ai", "segmented", "pre_reading", "semiconductors", 0.7),
    ("P254", "ai", "segmented", "pre_reading", "uhi", 0.71),
    ("P257", "ai", "segmented", "pre_reading", "semiconductors", 0.7),
    ("P257", "ai", "segmented", "pre_reading", "uhi", 0.71),
    ("P259", "ai", "segmented", "pre_reading", "crispr", 0.71),
    ("P259", "ai", "segmented", "pre_reading", "uhi", 0.71),
    ("P263", "ai", "segmented", "pre_reading", "semiconductors", 0.7),
    ("P263", "ai", "segmented", "pre_reading", "uhi", 0.71),
    ("P264", "ai", "segmented", "pre_reading", "crispr", 0.71),
    ("P264", "ai", "segmented", "pre_reading", "semiconductors", 0.7),
    ("P266", "ai", "segmented", "pre_reading", "crispr", 0.71),
    ("P266", "ai", "segmented", "pre_reading", "semiconductors", 0.7),
    
    # Segmented + synchronous
    ("P239", "ai", "segmented", "synchronous", "semiconductors", 0.7),
    ("P240", "ai", "segmented", "synchronous", "crispr", 0.71),
    ("P245", "ai", "segmented", "synchronous", "uhi", 0.71),
    ("P249", "ai", "segmented", "synchronous", "semiconductors", 0.7),
    ("P250", "ai", "segmented", "synchronous", "semiconductors", 0.7),
    ("P252", "ai", "segmented", "synchronous", "crispr", 0.71),
    ("P254", "ai", "segmented", "synchronous", "crispr", 0.71),
    ("P257", "ai", "segmented", "synchronous", "crispr", 0.71),
    ("P259", "ai", "segmented", "synchronous", "semiconductors", 0.7),
    ("P263", "ai", "segmented", "synchronous", "crispr", 0.71),
    ("P264", "ai", "segmented", "synchronous", "uhi", 0.71),
    ("P266", "ai", "segmented", "synchronous", "uhi", 0.71),
    
    # Segmented + post_reading
    ("P239", "ai", "segmented", "post_reading", "uhi", 0.2),
    ("P240", "ai", "segmented", "post_reading", "semiconductors", 0.2),
    ("P245", "ai", "segmented", "post_reading", "semiconductors", 0.2),
    ("P249", "ai", "segmented", "post_reading", "uhi", 0.2),
    ("P250", "ai", "segmented", "post_reading", "crispr", 0.2),
    ("P252", "ai", "segmented", "post_reading", "semiconductors", 0.2),
    ("P254", "ai", "segmented", "post_reading", "semiconductors", 0.2),
    ("P257", "ai", "segmented", "post_reading", "semiconductors", 0.2),
    ("P259", "ai", "segmented", "post_reading", "semiconductors", 0.2),
    ("P263", "ai", "segmented", "post_reading", "crispr", 0.2),
    ("P264", "ai", "segmented", "post_reading", "semiconductors", 0.2),
    ("P266", "ai", "segmented", "post_reading", "crispr", 0.2),
    
    # Non AI - control group
    ("P220", "control", "control", "control", "crispr", 0.71),
    ("P220", "control", "control", "control", "semiconductors", 0.9),
    ("P220", "control", "control", "control", "uhi", 0.5),
    ("P221", "control", "control", "control", "crispr", 0.71),
    ("P221", "control", "control", "control", "semiconductors", 0.7),
    ("P221", "control", "control", "control", "uhi", 0.71),
    ("P224", "control", "control", "control", "crispr", 0.1),
    ("P224", "control", "control", "control", "semiconductors", 0.1),
    ("P224", "control", "control", "control", "uhi", 0.5),
    ("P225", "control", "control", "control", "crispr", 0.1),
    ("P225", "control", "control", "control", "semiconductors", 0.1),
    ("P225", "control", "control", "control", "uhi", 0.1),
    ("P226", "control", "control", "control", "crispr", 0.71),
    ("P226", "control", "control", "control", "semiconductors", 0.9),
    ("P226", "control", "control", "control", "uhi", 0.71),
    ("P230", "control", "control", "control", "crispr", 0.71),
    ("P230", "control", "control", "control", "semiconductors", 0.7),
    ("P230", "control", "control", "control", "uhi", 0.71),
    ("P235", "control", "control", "control", "crispr", 0.71),
    ("P235", "control", "control", "control", "semiconductors", 0.7),
    ("P235", "control", "control", "control", "uhi", 0.71),
    ("P238", "control", "control", "control", "crispr", 0.1),
    ("P238", "control", "control", "control", "semiconductors", 0.1),
    ("P238", "control", "control", "control", "uhi", 0.1),
    ("P241", "control", "control", "control", "crispr", 0.71),
    ("P241", "control", "control", "control", "semiconductors", 0.7),
    ("P241", "control", "control", "control", "uhi", 0.71),
    ("P248", "control", "control", "control", "crispr", 0.71),
    ("P248", "control", "control", "control", "semiconductors", 0.7),
    ("P248", "control", "control", "control", "uhi", 0.71),
    ("P256", "control", "control", "control", "crispr", 0.71),
    ("P256", "control", "control", "control", "semiconductors", 0.7),
    ("P256", "control", "control", "control", "uhi", 0.71),
    ("P188", "control", "control", "control", "semiconductors", 3.0),
    ("P188", "control", "control", "control", "crispr", 4.0),
    ("P188", "control", "control", "control", "uhi", 4.0),
]

def calculate_averages():
    """Calculate average recall scores by condition"""
    
    # Storage for scores
    integrated_pre = []
    integrated_sync = []
    integrated_post = []
    segmented_pre = []
    segmented_sync = []
    segmented_post = []
    non_ai = []
    
    # Group scores
    for entry in data:
        participant, condition, structure, timing, article, score = entry
        
        if condition == "ai":
            if structure == "integrated":
                if timing == "pre_reading":
                    integrated_pre.append(score)
                elif timing == "synchronous":
                    integrated_sync.append(score)
                elif timing == "post_reading":
                    integrated_post.append(score)
            elif structure == "segmented":
                if timing == "pre_reading":
                    segmented_pre.append(score)
                elif timing == "synchronous":
                    segmented_sync.append(score)
                elif timing == "post_reading":
                    segmented_post.append(score)
        elif condition == "control":
            non_ai.append(score)
    
    # Calculate averages
    def avg(lst):
        return sum(lst) / len(lst) if lst else 0
    
    print("=" * 80)
    print("RECALL TOTAL SCORE ANALYSIS")
    print("=" * 80)
    print()
    
    print("INTEGRATED (With AI):")
    print(f"  Pre-reading:   {avg(integrated_pre):.2f} (n={len(integrated_pre)}) - scores: {integrated_pre}")
    print(f"  Synchronous:   {avg(integrated_sync):.2f} (n={len(integrated_sync)}) - scores: {integrated_sync}")
    print(f"  Post-reading:  {avg(integrated_post):.2f} (n={len(integrated_post)}) - scores: {integrated_post}")
    print(f"  → Average for Integrated: {avg(integrated_pre + integrated_sync + integrated_post):.2f}")
    print()
    
    print("SEGMENTED (With AI):")
    print(f"  Pre-reading:   {avg(segmented_pre):.2f} (n={len(segmented_pre)}) - scores: {segmented_pre}")
    print(f"  Synchronous:   {avg(segmented_sync):.2f} (n={len(segmented_sync)}) - scores: {segmented_sync}")
    print(f"  Post-reading:  {avg(segmented_post):.2f} (n={len(segmented_post)}) - scores: {segmented_post}")
    print(f"  → Average for Segmented: {avg(segmented_pre + segmented_sync + segmented_post):.2f}")
    print()
    
    print("NON AI (Control):")
    print(f"  Average: {avg(non_ai):.2f} (n={len(non_ai)})")
    print()
    
    # Calculate overall averages
    all_with_ai = integrated_pre + integrated_sync + integrated_post + segmented_pre + segmented_sync + segmented_post
    
    print("=" * 80)
    print("SUMMARY FOR YOUR SPREADSHEET")
    print("=" * 80)
    print()
    print("Row values:")
    print(f"  Integrated pre_reading:   {avg(integrated_pre):.2f}")
    print(f"  Integrated synchronous:   {avg(integrated_sync):.2f}")
    print(f"  Integrated post_reading:  {avg(integrated_post):.2f}")
    print(f"  Segmented pre_reading:    {avg(segmented_pre):.2f}")
    print(f"  Segmented synchronous:    {avg(segmented_sync):.2f}")
    print(f"  Segmented post_reading:   {avg(segmented_post):.2f}")
    print(f"  Non AI:                   {avg(non_ai):.2f}")
    print()
    print("Averages:")
    print(f"  Average for integrated:   {avg(integrated_pre + integrated_sync + integrated_post):.2f}")
    print(f"  Average for segmented:    {avg(segmented_pre + segmented_sync + segmented_post):.2f}")
    print(f"  Average for With AI:      {avg(all_with_ai):.2f}")
    print()
    
    # Calculate overall weighted average
    # 72 readings with AI, 36 readings non-AI
    overall = (72 * avg(all_with_ai) + 36 * avg(non_ai)) / 108
    print(f"  Overall average (weighted): {overall:.2f}")
    print()

if __name__ == '__main__':
    calculate_averages()
