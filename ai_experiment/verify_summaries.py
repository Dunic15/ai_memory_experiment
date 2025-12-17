#!/usr/bin/env python3
"""
Script to verify integrated summaries and segmented bullet points for all articles.
Checks for false lure markers and allows systematic verification.
"""

import sys
import os
import re

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import ARTICLES

def clean_false_lure_markers(text):
    """Remove false lure markers from text for display"""
    # Remove arrow-style markers: ← FALSE LURE #1
    text = re.sub(r'\s*←\s*FALSE LURE\s*#?\d*\s*', '', text)
    # Remove parenthetical markers: (FALSE LURE #1)
    text = re.sub(r'\s*\(FALSE LURE\s*#?\d*\)\s*', '', text)
    # Remove inline markers: FALSE LURE #1
    text = re.sub(r'\s*FALSE LURE\s*#?\d*\s*', '', text)
    return text.strip()

def find_false_lure_markers(text):
    """Find all false lure markers in text"""
    markers = []
    # Find arrow-style: ← FALSE LURE #1
    arrow_matches = re.findall(r'←\s*FALSE LURE\s*#?(\d*)', text)
    for match in arrow_matches:
        markers.append(f"← FALSE LURE #{match if match else '?'}")
    # Find parenthetical: (FALSE LURE #1)
    paren_matches = re.findall(r'\(FALSE LURE\s*#?(\d*)\)', text)
    for match in paren_matches:
        markers.append(f"(FALSE LURE #{match if match else '?'})")
    # Find inline: FALSE LURE #1
    inline_matches = re.findall(r'FALSE LURE\s*#?(\d*)', text)
    for match in inline_matches:
        if f"FALSE LURE #{match if match else '?'}" not in markers:
            markers.append(f"FALSE LURE #{match if match else '?'}")
    return markers

def display_article_summaries(article_key, article_data):
    """Display summaries for a single article"""
    print("\n" + "="*80)
    print(f"ARTICLE: {article_data.get('title', article_key.upper())}")
    print(f"Key: {article_key}")
    print("="*80)
    
    # Display segmented summary (bullet points)
    print("\n--- SEGMENTED SUMMARY (Bullet Points) ---")
    segmented = article_data.get('summary_segmented', '')
    if segmented:
        print(segmented)
        
        # Check for false lures
        false_lures = find_false_lure_markers(segmented)
        if false_lures:
            print(f"\n⚠️  WARNING: Found false lure markers in segmented summary: {false_lures}")
            print("\n--- CLEANED SEGMENTED SUMMARY (False Lures Removed) ---")
            print(clean_false_lure_markers(segmented))
        else:
            print("\n✓ No false lure markers found in segmented summary")
    else:
        print("(No segmented summary found)")
    
    # Display integrated summary
    print("\n--- INTEGRATED SUMMARY (Paragraph Format) ---")
    integrated = article_data.get('summary_integrated', '')
    if integrated:
        print(integrated)
        
        # Check for false lures
        false_lures = find_false_lure_markers(integrated)
        if false_lures:
            print(f"\n⚠️  WARNING: Found false lure markers in integrated summary: {false_lures}")
            print("\n--- CLEANED INTEGRATED SUMMARY (False Lures Removed) ---")
            print(clean_false_lure_markers(integrated))
        else:
            print("\n✓ No false lure markers found in integrated summary")
    else:
        print("(No integrated summary found)")
    
    print("\n" + "="*80)

def main():
    """Main verification function"""
    print("="*80)
    print("ARTICLE SUMMARY VERIFICATION TOOL")
    print("="*80)
    print("\nThis tool will display each article's summaries for verification.")
    print("You can check:")
    print("  1. Segmented summary (bullet points) - should match your provided version")
    print("  2. Integrated summary (paragraph) - should match your provided version")
    print("  3. False lure markers - should be present in source but removed in display")
    print("\nPress Enter to continue with each article, or 'q' to quit...")
    
    article_keys = ['uhi', 'crispr', 'semiconductors']
    
    for article_key in article_keys:
        if article_key not in ARTICLES:
            print(f"\n⚠️  Article '{article_key}' not found in ARTICLES dictionary")
            continue
        
        article_data = ARTICLES[article_key]
        display_article_summaries(article_key, article_data)
        
        if article_key != article_keys[-1]:  # Not the last article
            user_input = input("\nPress Enter to continue to next article, or 'q' to quit: ")
            if user_input.lower() == 'q':
                break
    
    print("\n" + "="*80)
    print("VERIFICATION COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("1. Compare each segmented summary with your correct version")
    print("2. Compare each integrated summary with your correct version")
    print("3. Verify false lures are marked correctly (they should be in source)")
    print("4. Verify false lures are removed in the display (check templates)")

if __name__ == "__main__":
    main()





























