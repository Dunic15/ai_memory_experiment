#!/usr/bin/env python3
"""
Generate a document with all articles in both English and Chinese.
Similar to Articles.docx format for thesis documentation.
"""

import sys
import os
import json
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import (
    ARTICLES, 
    _auto_translate, 
    _load_translation_cache,
    PRIOR_KNOWLEDGE_FAMILIARITY_TERMS,
    PRIOR_KNOWLEDGE_RECOGNITION_TERMS,
    PRIOR_KNOWLEDGE_QUIZ,
    AI_TRUST_QUESTIONS
)

# Load translation cache
_load_translation_cache()

# Consent form content (extracted from template)
CONSENT_CONTENT = {
    'title': 'AI-Assisted Reading and Memory Study',
    'warning_title': 'Important information about AI summaries',
    'warning_points': [
        'The AI summary accuracy is approximately 90%',
        'AI is only an assistant – make sure you read all the articles',
        'Not all questions can be answered with the AI summary alone'
    ],
    'time_commitment': '105 minutes',
    'what_you_do': [
        'Read short scientific articles',
        'Answer questions about the content',
        'Evaluate your experience with AI-assisted reading'
    ],
    'important_info': [
        'Your participation is voluntary',
        'You may withdraw at any time without penalty',
        'No personal identifying information will be collected; data will be stored anonymously',
        'You must be 18 years or older',
        'You must use a laptop or desktop computer (no phones or tablets)'
    ],
    'during_study': [
        'Please remain in full-screen mode',
        'Avoid multitasking or switching tabs',
        'Ensure you\'re in a quiet environment'
    ],
    'consent_confirmation': 'By clicking "I Agree and Continue," you confirm that:',
    'consent_points': [
        'You have read and understood this information',
        'You are 18 years or older',
        'You consent to participate in this study'
    ]
}

def translate_article_to_chinese(article_key, article_data):
    """Translate an article to Chinese."""
    print(f"Translating {article_key}...")
    
    translated = {
        'title': _auto_translate(article_data['title'], 'zh'),
        'free_recall_prompt': _auto_translate(article_data['free_recall_prompt'], 'zh'),
        'text': _auto_translate(article_data['text'], 'zh'),
        'summary_integrated': _auto_translate(article_data['summary_integrated'], 'zh'),
        'summary_segmented': _auto_translate(article_data['summary_segmented'], 'zh'),
        'questions': []
    }
    
    # Translate questions
    for q in article_data['questions']:
        translated_q = {
            'q': _auto_translate(q['q'], 'zh'),
            'options': [_auto_translate(opt, 'zh') for opt in q['options']],
            'correct': q['correct']
        }
        translated['questions'].append(translated_q)
    
    return translated

def generate_markdown_document(include_answers=True):
    """Generate a markdown document with all sections in English and Chinese.
    
    Args:
        include_answers: If True, mark correct answers with ✓. If False, don't show answers.
    """
    
    output_lines = []
    output_lines.append("# AI Memory Experiment - Complete Materials (English & Chinese)")
    output_lines.append("")
    output_lines.append("This document contains all materials used in the experiment, presented in both English and Chinese.")
    output_lines.append("")
    output_lines.append("---")
    output_lines.append("")
    
    # ============================================================================
    # CONSENT FORM
    # ============================================================================
    output_lines.append("## Consent Form - English")
    output_lines.append("")
    output_lines.append(f"### {CONSENT_CONTENT['title']}")
    output_lines.append("")
    output_lines.append(f"**{CONSENT_CONTENT['warning_title']}:**")
    output_lines.append("")
    for point in CONSENT_CONTENT['warning_points']:
        output_lines.append(f"- {point}")
    output_lines.append("")
    output_lines.append(f"**Time Commitment:** {CONSENT_CONTENT['time_commitment']}")
    output_lines.append("")
    output_lines.append("**What You'll Do:**")
    for item in CONSENT_CONTENT['what_you_do']:
        output_lines.append(f"- {item}")
    output_lines.append("")
    output_lines.append("**Important Information:**")
    for item in CONSENT_CONTENT['important_info']:
        output_lines.append(f"- {item}")
    output_lines.append("")
    output_lines.append("**During the Study:**")
    for item in CONSENT_CONTENT['during_study']:
        output_lines.append(f"- {item}")
    output_lines.append("")
    output_lines.append(f"**{CONSENT_CONTENT['consent_confirmation']}**")
    for point in CONSENT_CONTENT['consent_points']:
        output_lines.append(f"- {point}")
    output_lines.append("")
    
    # Chinese Consent
    output_lines.append("---")
    output_lines.append("")
    output_lines.append("## Consent Form - 中文 (Chinese)")
    output_lines.append("")
    output_lines.append(f"### {_auto_translate(CONSENT_CONTENT['title'], 'zh')}")
    output_lines.append("")
    output_lines.append(f"**{_auto_translate(CONSENT_CONTENT['warning_title'], 'zh')}:**")
    output_lines.append("")
    for point in CONSENT_CONTENT['warning_points']:
        output_lines.append(f"- {_auto_translate(point, 'zh')}")
    output_lines.append("")
    output_lines.append(f"**{_auto_translate('Time Commitment:', 'zh')}** {_auto_translate(CONSENT_CONTENT['time_commitment'], 'zh')}")
    output_lines.append("")
    what_you_do_label = _auto_translate('What You\'ll Do:', 'zh')
    output_lines.append(f"**{what_you_do_label}**")
    for item in CONSENT_CONTENT['what_you_do']:
        output_lines.append(f"- {_auto_translate(item, 'zh')}")
    output_lines.append("")
    output_lines.append(f"**{_auto_translate('Important Information:', 'zh')}**")
    for item in CONSENT_CONTENT['important_info']:
        output_lines.append(f"- {_auto_translate(item, 'zh')}")
    output_lines.append("")
    output_lines.append(f"**{_auto_translate('During the Study:', 'zh')}**")
    for item in CONSENT_CONTENT['during_study']:
        output_lines.append(f"- {_auto_translate(item, 'zh')}")
    output_lines.append("")
    output_lines.append(f"**{_auto_translate(CONSENT_CONTENT['consent_confirmation'], 'zh')}**")
    for point in CONSENT_CONTENT['consent_points']:
        output_lines.append(f"- {_auto_translate(point, 'zh')}")
    output_lines.append("")
    output_lines.append("=" * 80)
    output_lines.append("")
    
    # ============================================================================
    # PRIOR KNOWLEDGE ASSESSMENT
    # ============================================================================
    output_lines.append("## Prior Knowledge Assessment - English")
    output_lines.append("")
    
    # Section 1: Familiarity
    output_lines.append("### Section 1: Familiarity Rating")
    output_lines.append("")
    output_lines.append("Rate how familiar you are with the following scientific terms.")
    output_lines.append("1 = Never heard of it | 7 = Could clearly explain it to others")
    output_lines.append("")
    for i, term in enumerate(PRIOR_KNOWLEDGE_FAMILIARITY_TERMS, 1):
        output_lines.append(f"{i}. {term}")
    output_lines.append("")
    
    # Section 2: Recognition
    output_lines.append("### Section 2: Concept Recognition Check")
    output_lines.append("")
    output_lines.append("For each term below, mark Yes if you believe you could accurately define or describe it without looking it up; otherwise mark No.")
    output_lines.append("")
    for i, term in enumerate(PRIOR_KNOWLEDGE_RECOGNITION_TERMS, 1):
        output_lines.append(f"{i}. {term}")
    output_lines.append("")
    
    # Section 3: Quiz
    output_lines.append("### Section 3: Mini Quiz")
    output_lines.append("")
    for i, q in enumerate(PRIOR_KNOWLEDGE_QUIZ, 1):
        output_lines.append(f"**Question {i}:** {q['q']}")
        output_lines.append("")
        for j, opt in enumerate(q['options']):
            letter = chr(97 + j)  # a, b, c, d
            marker = "✓" if (include_answers and j == q['correct']) else " "
            output_lines.append(f"{marker} {letter}) {opt}")
        output_lines.append("")
    
    # Chinese Prior Knowledge
    output_lines.append("---")
    output_lines.append("")
    output_lines.append("## Prior Knowledge Assessment - 中文 (Chinese)")
    output_lines.append("")
    
    output_lines.append("### 第一部分：熟悉度评级 (Section 1: Familiarity Rating)")
    output_lines.append("")
    output_lines.append(_auto_translate("Rate how familiar you are with the following scientific terms.", 'zh'))
    output_lines.append(_auto_translate("1 = Never heard of it", 'zh') + " | " + _auto_translate("7 = Could clearly explain it to others", 'zh'))
    output_lines.append("")
    for i, term in enumerate(PRIOR_KNOWLEDGE_FAMILIARITY_TERMS, 1):
        output_lines.append(f"{i}. {_auto_translate(term, 'zh')}")
    output_lines.append("")
    
    output_lines.append("### 第二部分：概念识别检查 (Section 2: Concept Recognition Check)")
    output_lines.append("")
    output_lines.append(_auto_translate("For each term below, mark Yes if you believe you could accurately define or describe it without looking it up; otherwise mark No.", 'zh'))
    output_lines.append("")
    for i, term in enumerate(PRIOR_KNOWLEDGE_RECOGNITION_TERMS, 1):
        output_lines.append(f"{i}. {_auto_translate(term, 'zh')}")
    output_lines.append("")
    
    output_lines.append("### 第三部分：小测验 (Section 3: Mini Quiz)")
    output_lines.append("")
    for i, q in enumerate(PRIOR_KNOWLEDGE_QUIZ, 1):
        output_lines.append(f"**问题 {i}:** {_auto_translate(q['q'], 'zh')}")
        output_lines.append("")
        for j, opt in enumerate(q['options']):
            letter = chr(97 + j)
            marker = "✓" if (include_answers and j == q['correct']) else " "
            output_lines.append(f"{marker} {letter}) {_auto_translate(opt, 'zh')}")
        output_lines.append("")
    
    output_lines.append("")
    output_lines.append("=" * 80)
    output_lines.append("")
    
    # ============================================================================
    # AI TRUST ASSESSMENT
    # ============================================================================
    output_lines.append("## AI Trust & Technology Use - English")
    output_lines.append("")
    
    # Trust in AI
    output_lines.append("### Trust in AI Systems")
    output_lines.append("")
    output_lines.append("Scale: 1 = Strongly disagree | 7 = Strongly agree")
    output_lines.append("")
    for i, q in enumerate(AI_TRUST_QUESTIONS['trust'], 1):
        output_lines.append(f"{i}. {q}")
    output_lines.append("")
    
    # Dependence
    output_lines.append("### Technology Dependence")
    output_lines.append("")
    output_lines.append("Scale: 1 = Strongly disagree | 7 = Strongly agree")
    output_lines.append("")
    for i, q in enumerate(AI_TRUST_QUESTIONS['dependence'], 1):
        output_lines.append(f"{i}. {q}")
    output_lines.append("")
    
    # Skill
    output_lines.append("### Technical Proficiency")
    output_lines.append("")
    output_lines.append("Scale: 1 = Strongly disagree | 7 = Strongly agree")
    output_lines.append("")
    for i, q in enumerate(AI_TRUST_QUESTIONS['skill'], 1):
        output_lines.append(f"{i}. {q}")
    output_lines.append("")
    
    # Open Reflection
    output_lines.append("### Optional: AI in Your Life")
    output_lines.append("")
    output_lines.append("1. How frequently do you use AI tools or smart digital tools in your daily life? Please describe your usage patterns (e.g., daily, several times per week, weekly, occasionally, rarely).")
    output_lines.append("")
    output_lines.append("2. What specific AI tools or smart digital tools do you use? Please list the names of the tools, applications, or platforms you regularly interact with (e.g., ChatGPT, Google Search, Siri, Grammarly, GitHub Copilot, language learning apps, productivity tools).")
    output_lines.append("")
    output_lines.append("3. For which tasks or activities do you use these AI tools? Please describe the specific purposes and contexts in which you rely on them (e.g., information searching, writing assistance, problem-solving, learning, communication, creative work, data analysis).")
    output_lines.append("")
    
    # Chinese AI Trust
    output_lines.append("---")
    output_lines.append("")
    output_lines.append("## AI Trust & Technology Use - 中文 (Chinese)")
    output_lines.append("")
    
    output_lines.append("### 对AI系统的信任 (Trust in AI Systems)")
    output_lines.append("")
    output_lines.append(_auto_translate("Scale: 1 = Strongly disagree | 7 = Strongly agree", 'zh'))
    output_lines.append("")
    for i, q in enumerate(AI_TRUST_QUESTIONS['trust'], 1):
        output_lines.append(f"{i}. {_auto_translate(q, 'zh')}")
    output_lines.append("")
    
    output_lines.append("### 技术依赖 (Technology Dependence)")
    output_lines.append("")
    output_lines.append(_auto_translate("Scale: 1 = Strongly disagree | 7 = Strongly agree", 'zh'))
    output_lines.append("")
    for i, q in enumerate(AI_TRUST_QUESTIONS['dependence'], 1):
        output_lines.append(f"{i}. {_auto_translate(q, 'zh')}")
    output_lines.append("")
    
    output_lines.append("### 技术熟练程度 (Technical Proficiency)")
    output_lines.append("")
    output_lines.append(_auto_translate("Scale: 1 = Strongly disagree | 7 = Strongly agree", 'zh'))
    output_lines.append("")
    for i, q in enumerate(AI_TRUST_QUESTIONS['skill'], 1):
        output_lines.append(f"{i}. {_auto_translate(q, 'zh')}")
    output_lines.append("")
    
    output_lines.append("### 可选：您生活中的AI (Optional: AI in Your Life)")
    output_lines.append("")
    output_lines.append(f"1. {_auto_translate('How frequently do you use AI tools or smart digital tools in your daily life? Please describe your usage patterns (e.g., daily, several times per week, weekly, occasionally, rarely).', 'zh')}")
    output_lines.append("")
    output_lines.append(f"2. {_auto_translate('What specific AI tools or smart digital tools do you use? Please list the names of the tools, applications, or platforms you regularly interact with (e.g., ChatGPT, Google Search, Siri, Grammarly, GitHub Copilot, language learning apps, productivity tools).', 'zh')}")
    output_lines.append("")
    output_lines.append(f"3. {_auto_translate('For which tasks or activities do you use these AI tools? Please describe the specific purposes and contexts in which you rely on them (e.g., information searching, writing assistance, problem-solving, learning, communication, creative work, data analysis).', 'zh')}")
    output_lines.append("")
    
    output_lines.append("")
    output_lines.append("=" * 80)
    output_lines.append("")
    
    article_order = ['crispr', 'semiconductors', 'uhi']
    article_names = {
        'crispr': 'CRISPR Gene Editing',
        'semiconductors': 'Semiconductor Supply Chains',
        'uhi': 'Urban Heat Islands'
    }
    
    for article_key in article_order:
        if article_key not in ARTICLES:
            continue
            
        article = ARTICLES[article_key]
        article_name = article_names.get(article_key, article_key.upper())
        
        # English Section
        output_lines.append(f"## {article_name} - English")
        output_lines.append("")
        output_lines.append(f"### Title")
        output_lines.append(article['title'])
        output_lines.append("")
        output_lines.append(f"### Free Recall Prompt")
        output_lines.append(article['free_recall_prompt'])
        output_lines.append("")
        output_lines.append(f"### Article Text")
        output_lines.append(article['text'])
        output_lines.append("")
        output_lines.append(f"### Summary (Integrated)")
        output_lines.append(article['summary_integrated'])
        output_lines.append("")
        output_lines.append(f"### Summary (Segmented)")
        output_lines.append(article['summary_segmented'])
        output_lines.append("")
        output_lines.append(f"### Single Choice Questions with Multiple Options")
        output_lines.append("")
        for i, q in enumerate(article['questions'], 1):
            output_lines.append(f"**Question {i}:** {q['q']}")
            output_lines.append("")
            for j, opt in enumerate(q['options']):
                letter = chr(97 + j)  # a, b, c, d
                marker = "✓" if (include_answers and j == q['correct']) else " "
                output_lines.append(f"{marker} {letter}) {opt}")
            output_lines.append("")
        
        # Translate to Chinese
        print(f"\n{'='*60}")
        print(f"Translating {article_key} to Chinese...")
        print(f"{'='*60}\n")
        
        translated = translate_article_to_chinese(article_key, article)
        
        # Chinese Section
        output_lines.append("---")
        output_lines.append("")
        output_lines.append(f"## {article_name} - 中文 (Chinese)")
        output_lines.append("")
        output_lines.append(f"### 标题 (Title)")
        output_lines.append(translated['title'])
        output_lines.append("")
        output_lines.append(f"### 自由回忆提示 (Free Recall Prompt)")
        output_lines.append(translated['free_recall_prompt'])
        output_lines.append("")
        output_lines.append(f"### 文章正文 (Article Text)")
        output_lines.append(translated['text'])
        output_lines.append("")
        output_lines.append(f"### 摘要（整合版）(Summary - Integrated)")
        output_lines.append(translated['summary_integrated'])
        output_lines.append("")
        output_lines.append(f"### 摘要（分段版）(Summary - Segmented)")
        output_lines.append(translated['summary_segmented'])
        output_lines.append("")
        output_lines.append(f"### 单选题（多选项）(Single Choice Questions with Multiple Options)")
        output_lines.append("")
        for i, q in enumerate(translated['questions'], 1):
            output_lines.append(f"**问题 {i}:** {q['q']}")
            output_lines.append("")
            for j, opt in enumerate(q['options']):
                letter = chr(97 + j)  # a, b, c, d
                marker = "✓" if (include_answers and j == article['questions'][i-1]['correct']) else " "
                output_lines.append(f"{marker} {letter}) {opt}")
            output_lines.append("")
        
        output_lines.append("")
        output_lines.append("=" * 80)
        output_lines.append("")
    
    return "\n".join(output_lines)

def main():
    """Main function to generate the document."""
    print("Generating Chinese translations and documents...")
    print("This may take several minutes as translations are generated...")
    print("")
    
    # Generate markdown document WITH answers
    print("Generating document WITH answers...")
    markdown_content_with_answers = generate_markdown_document(include_answers=True)
    
    # Save markdown file with answers
    output_file_with_answers = Path(__file__).parent.parent / "Articles_English_Chinese.md"
    with open(output_file_with_answers, 'w', encoding='utf-8') as f:
        f.write(markdown_content_with_answers)
    
    print(f"✓ Document with answers saved to: {output_file_with_answers}")
    print(f"  Total size: {len(markdown_content_with_answers)} characters")
    print(f"  Total lines: {len(markdown_content_with_answers.splitlines())}")
    
    # Generate markdown document WITHOUT answers
    print("\nGenerating document WITHOUT answers...")
    markdown_content_no_answers = generate_markdown_document(include_answers=False)
    
    # Save markdown file without answers
    output_file_no_answers = Path(__file__).parent.parent / "Articles_English_Chinese_NoAnswers.md"
    with open(output_file_no_answers, 'w', encoding='utf-8') as f:
        f.write(markdown_content_no_answers)
    
    print(f"✓ Document without answers saved to: {output_file_no_answers}")
    print(f"  Total size: {len(markdown_content_no_answers)} characters")
    print(f"  Total lines: {len(markdown_content_no_answers.splitlines())}")
    print("\nYou can convert these markdown files to .docx using:")
    print("  - python3 scripts/convert_to_docx.py")
    print("  - Or open in Word/Google Docs and save as .docx")

if __name__ == "__main__":
    main()

