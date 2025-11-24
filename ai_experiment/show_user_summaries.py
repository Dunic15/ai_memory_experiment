#!/usr/bin/env python3
"""
Script to show exactly what users see when viewing summaries.
Displays translated summaries with false lures removed, matching the display logic.
"""

import sys
import os
import re
import json

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import ARTICLES, _auto_translate, _set_lang, _get_lang

def clean_false_lure_segmented(text):
    """Clean false lure markers from segmented summary (matching template logic)"""
    # Remove numbered list markers (e.g., "1. ", "2. ", "10. ")
    text = re.sub(r'^\d+\.\s+', '', text)
    # Remove false lure markers but keep the rest of the text
    # Pattern: ⚠️虚假引诱 #1： or ⚠️虚假引诱 #2： - only remove the marker prefix
    text = re.sub(r'⚠️虚假引诱\s*#?\d*[：:]\s*', '', text)
    # Remove trailing false lure markers (← 错误诱饵 #1, etc.) - all Chinese variants
    text = re.sub(r'\s*←\s*错误诱饵\s*#?\d*', '', text)
    text = re.sub(r'\s*←\s*虚假诱导\s*#?\d*', '', text)
    text = re.sub(r'\s*←\s*假诱饵\s*#?\d*', '', text)  # Added variant
    text = re.sub(r'\s*←\s*FALSE LURE\s*#?\d*', '', text)
    # Remove parenthetical false lure markers
    text = re.sub(r'\s*\(⚠️虚假引诱[^)]*\)', '', text)
    text = re.sub(r'\s*（⚠️虚假引诱[^）]*）', '', text)
    # Remove parenthetical false lure markers: （错误诱饵 #1）, （错误诱饵 #2）
    text = re.sub(r'\s*（错误诱饵\s*#?\d*）', '', text)
    text = re.sub(r'\s*\(错误诱饵\s*#?\d*\)', '', text)
    text = re.sub(r'\s*（虚假诱导\s*#?\d*）', '', text)
    text = re.sub(r'\s*\(虚假诱导\s*#?\d*\)', '', text)
    text = re.sub(r'\s*（假诱饵\s*#?\d*）', '', text)  # Added variant
    text = re.sub(r'\s*\(假诱饵\s*#?\d*\)', '', text)  # Added variant
    text = re.sub(r'\s*\(FALSE LURE\s*#?\d*\)', '', text)
    # Remove inline false lure markers (FALSE LURE #1 in middle of text)
    text = re.sub(r'\s*FALSE LURE\s*#?\d*\s*', '', text)
    text = re.sub(r'\s*错误诱惑\s*#?\d*\s*', '', text)  # Added variant
    text = re.sub(r'\s*错误诱饵\s*#?\d*\s*', '', text)  # Added variant
    # Clean up any double spaces or leading/trailing spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def clean_false_lure_integrated(text):
    """Clean false lure markers from integrated summary (matching template logic)"""
    # Remove false lure markers (all formats)
    text = re.sub(r'\s*⚠️[^。]*虚假引诱[^。]*', '', text)
    text = re.sub(r'\s*←\s*错误诱饵[^。]*', '', text)
    text = re.sub(r'\s*←\s*虚假诱导[^。]*', '', text)
    text = re.sub(r'\s*←\s*假诱饵[^。]*', '', text)  # Added variant
    text = re.sub(r'\s*←\s*FALSE LURE[^。]*', '', text)
    text = re.sub(r'\s*\(⚠️虚假引诱[^)]*\)', '', text)
    text = re.sub(r'\s*（⚠️虚假引诱[^）]*）', '', text)
    # Remove parenthetical false lure markers: （错误诱饵 #1）, （错误诱饵 #2）
    text = re.sub(r'\s*（错误诱饵\s*#?\d*）', '', text)
    text = re.sub(r'\s*\(错误诱饵\s*#?\d*\)', '', text)
    text = re.sub(r'\s*（虚假诱导\s*#?\d*）', '', text)
    text = re.sub(r'\s*\(虚假诱导\s*#?\d*\)', '', text)
    text = re.sub(r'\s*（假诱饵\s*#?\d*）', '', text)  # Added variant
    text = re.sub(r'\s*\(假诱饵\s*#?\d*\)', '', text)  # Added variant
    text = re.sub(r'\s*\(FALSE LURE\s*#?\d*\)', '', text)
    # Remove inline false lure markers
    text = re.sub(r'\s*FALSE LURE\s*#?\d*\s*', '', text)
    text = re.sub(r'\s*错误诱惑\s*#?\d*\s*', '', text)  # Added variant
    text = re.sub(r'\s*错误诱饵\s*#?\d*\s*', '', text)  # Added variant
    return text.strip()

def format_segmented_summary(summary_text, lang='en'):
    """Format segmented summary as users see it (bullet points, false lures removed)"""
    lines = summary_text.split('\n')
    formatted_lines = []
    for line in lines:
        trimmed = line.strip()
        if trimmed:
            cleaned = clean_false_lure_segmented(trimmed)
            if cleaned:
                formatted_lines.append(f"  • {cleaned}")
    return '\n'.join(formatted_lines)

def format_integrated_summary(summary_text, lang='en'):
    """Format integrated summary as users see it (paragraphs, false lures removed)"""
    paragraphs = summary_text.split('\n\n')
    formatted_paragraphs = []
    for para in paragraphs:
        cleaned = clean_false_lure_integrated(para.strip())
        if cleaned:
            formatted_paragraphs.append(f"  {cleaned}")
    return '\n\n'.join(formatted_paragraphs)

def get_localized_summary(article_key, summary_type, lang='en'):
    """Get translated summary for an article"""
    article = ARTICLES.get(article_key, {})
    if not article:
        return None
    
    summary_key = f'summary_{summary_type}'
    summary = article.get(summary_key, '')
    
    if not summary:
        return None
    
    # Translate if needed
    if lang == 'zh':
        # Set language context (simulate session)
        translated = _auto_translate(summary, 'zh')
        return translated
    else:
        return summary

def display_article_for_language(article_key, article_data, lang='en'):
    """Display summaries for a single article in a specific language"""
    lang_name = "English" if lang == 'en' else "中文 (Chinese)"
    print(f"\n{'='*80}")
    print(f"ARTICLE: {article_data.get('title', article_key.upper())}")
    print(f"Language: {lang_name}")
    print(f"{'='*80}")
    
    # Get localized summaries
    segmented_raw = get_localized_summary(article_key, 'segmented', lang)
    integrated_raw = get_localized_summary(article_key, 'integrated', lang)
    
    if not segmented_raw or not integrated_raw:
        print(f"⚠️  Missing summaries for {article_key}")
        return
    
    # Display SEGMENTED summary (what users see in bullet point condition)
    print(f"\n{'─'*80}")
    print("📋 SEGMENTED SUMMARY (Bullet Points) - What users see in 'Segmented' condition")
    print(f"{'─'*80}")
    formatted_segmented = format_segmented_summary(segmented_raw, lang)
    print(formatted_segmented)
    
    # Display INTEGRATED summary (what users see in integrated condition)
    print(f"\n{'─'*80}")
    print("📄 INTEGRATED SUMMARY (Paragraph) - What users see in 'Integrated' condition")
    print(f"{'─'*80}")
    formatted_integrated = format_integrated_summary(integrated_raw, lang)
    print(formatted_integrated)
    
    print(f"\n{'='*80}")

def main():
    """Main function to display all summaries"""
    print("="*80)
    print("USER-FACING SUMMARY DISPLAY VERIFICATION")
    print("="*80)
    print("\nThis shows EXACTLY what participants see when viewing summaries.")
    print("False lure markers are removed (as they should be in the display).")
    print("\n" + "="*80)
    
    article_keys = ['uhi', 'crispr', 'semiconductors']
    languages = ['en', 'zh']
    
    for article_key in article_keys:
        if article_key not in ARTICLES:
            print(f"\n⚠️  Article '{article_key}' not found")
            continue
        
        article_data = ARTICLES[article_key]
        
        for lang in languages:
            display_article_for_language(article_key, article_data, lang)
            
            if lang == 'en' and article_key != article_keys[-1]:
                print("\n")  # Space between articles
    
    print("\n" + "="*80)
    print("VERIFICATION COMPLETE")
    print("="*80)
    print("\nNotes:")
    print("  • Segmented summaries are shown as bullet points (numbered prefixes removed)")
    print("  • Integrated summaries are shown as continuous paragraphs")
    print("  • All false lure markers are removed (matching template display logic)")
    print("  • Summaries are translated for Chinese (zh) language")

if __name__ == "__main__":
    main()

