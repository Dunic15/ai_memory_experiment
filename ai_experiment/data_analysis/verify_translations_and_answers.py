#!/usr/bin/env python3
"""
Verify Chinese translations and answer keys for all articles
"""

import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import ARTICLES

# Expected answer keys from user
EXPECTED_ANSWERS = {
    'uhi': [2, 3, 0, 1, 2, 2, 0, 1, 2, 2, 1, 1, 0, 1],  # c, d, a, b, c, c, a, b, c, c, b, b, a, b
    'semiconductors': [2, 1, 1, 3, 2, 3, 0, 0, 1, 3, 2, 2, 0, 1],  # c, b, b, d, c, d, a, a, b, d, c, c, a, b
    'crispr': [0, 3, 0, 2, 0, 0, 1, 1, 3, 0, 2, 1, 1, 2]  # a, d, a, c, a, a, b, b, d, a, c, b, b, c
}

# Load translations
translations_file = "../translation_cache/translations.json"
with open(translations_file, 'r', encoding='utf-8') as f:
    translations = json.load(f)

def get_translation(key):
    """Get Chinese translation for a key"""
    zh_key = f"zh:{key}"
    return translations.get(zh_key, key)

def verify_article(article_key, article_name):
    """Verify translations and answers for an article"""
    print("=" * 80)
    print(f"VERIFYING {article_name.upper()}")
    print("=" * 80)
    print()
    
    article = ARTICLES.get(article_key, {})
    questions = article.get('questions', [])
    expected = EXPECTED_ANSWERS.get(article_key, [])
    
    if len(questions) != len(expected):
        print(f"⚠️  WARNING: Number of questions ({len(questions)}) doesn't match expected answers ({len(expected)})")
        print()
    
    issues = []
    correct_count = 0
    
    for q_idx, question in enumerate(questions):
        q_num = q_idx + 1
        q_text_en = question.get('q', '')
        options_en = question.get('options', [])
        correct_idx = question.get('correct', -1)
        expected_idx = expected[q_idx] if q_idx < len(expected) else -1
        
        # Get Chinese translations
        q_text_zh = get_translation(q_text_en)
        options_zh = [get_translation(opt) for opt in options_en]
        
        # Check if answer key matches
        if correct_idx != expected_idx:
            issues.append({
                'question': q_num,
                'type': 'answer_mismatch',
                'current': correct_idx,
                'expected': expected_idx,
                'question_text': q_text_en[:60] + '...' if len(q_text_en) > 60 else q_text_en
            })
        else:
            correct_count += 1
        
        # Print question info
        print(f"Q{q_num}:")
        print(f"  English: {q_text_en[:80]}...")
        print(f"  Chinese: {q_text_zh[:80]}...")
        print(f"  Options:")
        for opt_idx, (opt_en, opt_zh) in enumerate(zip(options_en, options_zh)):
            marker = ""
            if opt_idx == correct_idx:
                marker = " [CORRECT]"
            if opt_idx == expected_idx and opt_idx != correct_idx:
                marker += " [EXPECTED]"
            print(f"    {chr(97+opt_idx)}) EN: {opt_en[:50]}")
            print(f"       ZH: {opt_zh[:50]}{marker}")
        print(f"  Current Answer Key: {correct_idx} ({chr(97+correct_idx) if correct_idx >= 0 else 'N/A'})")
        print(f"  Expected Answer: {expected_idx} ({chr(97+expected_idx) if expected_idx >= 0 else 'N/A'})")
        if correct_idx != expected_idx:
            print(f"  ⚠️  MISMATCH!")
        print()
    
    # Summary
    print("-" * 80)
    print(f"Summary for {article_name}:")
    print(f"  Total Questions: {len(questions)}")
    print(f"  Matching Answers: {correct_count}/{len(questions)}")
    if issues:
        print(f"  ⚠️  Issues Found: {len(issues)}")
        for issue in issues:
            print(f"    Q{issue['question']}: Current={issue['current']}, Expected={issue['expected']}")
            print(f"      {issue['question_text']}")
    else:
        print(f"  ✓ All answer keys match!")
    print()
    
    return issues

def main():
    print("=" * 80)
    print("TRANSLATION AND ANSWER KEY VERIFICATION")
    print("=" * 80)
    print()
    
    all_issues = []
    
    # Verify each article
    all_issues.extend(verify_article('uhi', 'Urban Heat Islands'))
    all_issues.extend(verify_article('semiconductors', 'Semiconductors'))
    all_issues.extend(verify_article('crispr', 'CRISPR'))
    
    # Final summary
    print("=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print()
    
    if all_issues:
        print(f"⚠️  Found {len(all_issues)} issues that need to be fixed:")
        print()
        for issue in all_issues:
            print(f"  Q{issue['question']}: Answer key mismatch")
            print(f"    Current: {issue['current']}, Expected: {issue['expected']}")
            print()
    else:
        print("✓ All translations and answer keys are correct!")
        print()
    
    # Create fix file
    if all_issues:
        fix_file = "ANSWER_KEY_FIXES_NEEDED.txt"
        with open(fix_file, 'w', encoding='utf-8') as f:
            f.write("ANSWER KEY FIXES NEEDED\n")
            f.write("=" * 80 + "\n\n")
            for issue in all_issues:
                f.write(f"Question {issue['question']}:\n")
                f.write(f"  Current answer key: {issue['current']}\n")
                f.write(f"  Expected answer key: {issue['expected']}\n")
                f.write(f"  Question: {issue['question_text']}\n")
                f.write("\n")
        print(f"Fix list saved to: {fix_file}")

if __name__ == "__main__":
    main()






