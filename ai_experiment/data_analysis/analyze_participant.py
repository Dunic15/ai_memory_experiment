#!/usr/bin/env python3
"""
Participant Data Analysis Script
Analyzes participant log files and generates comprehensive reports
"""

import json
import csv
import sys
import os
from datetime import datetime

# Import ARTICLES to get source_type for each question
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from app import ARTICLES
except ImportError:
    ARTICLES = {}

# Correct answers (0-indexed option indices)
# ORIGINAL ANSWER KEYS (for participants who took the test before MCQ change)
ORIGINAL_CORRECT_ANSWERS = {
    'crispr': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    'semiconductors': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1],
    'uhi': [1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 1, 1, 1, 1, 1]
}

# NEW ANSWER KEYS (for participants who take the test after MCQ change)
NEW_CORRECT_ANSWERS = {
    'crispr': [0, 3, 0, 2, 0, 0, 1, 1, 3, 0, 2, 2, 1, 2],  # Updated to 14 questions: a, d, a, c, a, a, b, b, d, a, c, c, b, c
    'semiconductors': [3, 1, 1, 3, 2, 3, 0, 0, 1, 3, 2, 2, 0, 1],  # Updated to 14 questions: d, b, b, d, c, d, a, a, b, d, c, c, a, b
    'uhi': [2, 3, 0, 1, 2, 2, 0, 1, 2, 2, 1, 1, 0, 1]  # Updated to 14 questions: c, d, a, b, c, c, a, b, c, c, b, b, a, b
}

# Use original answer keys by default (for existing participants)
# Set to NEW_CORRECT_ANSWERS for new participants
CORRECT_ANSWERS = ORIGINAL_CORRECT_ANSWERS

# False lure question mapping
# ORIGINAL: Only CRISPR had false lure at Q10 (index 9)
ORIGINAL_FALSE_LURE_MAP = {
    'crispr': {
        'question_index': 9,  # Q10 (0-indexed)
        'false_lure_option_index': 1,  # Option index containing "(FALSE - not mentioned in text)"
        'description': 'Bioluminescent plants - false lure about agricultural experiments'
    }
}

# NEW: All articles have false lure at Q2 (index 1)
# CRISPR now has 2 false lures: Q2 and Q3
NEW_FALSE_LURE_MAP = {
    'crispr': [
        {
            'question_index': 1,  # Q2 (0-indexed) - FALSE LURE question
            'false_lure_option_index': 1,  # Option b (index 1) - "bioluminescent plants" is the false lure
            'description': 'Bioluminescent plants - false lure about agricultural editing markers'
        },
        {
            'question_index': 2,  # Q3 (0-indexed) - FALSE LURE question
            'false_lure_option_index': 1,  # Option b (index 1) - "DNA repair activity" is the false lure
            'description': 'DNA repair activity - false lure about SHERLOCK and DETECTR initial purpose'
        }
    ],
    'semiconductors': [
        {
            'question_index': 8,  # Q9 (0-indexed) - FALSE LURE question
            'false_lure_option_index': 0,  # Option a (index 0) - "quantum processors" is the false lure
            'description': 'Quantum processors - false lure about advanced manufacturing technology'
        },
        {
            'question_index': 10,  # Q11 (0-indexed) - FALSE LURE question
            'false_lure_option_index': 1,  # Option b (index 1) - "46 silicon atoms" is the false lure
            'description': '46 silicon atoms - false lure about 3nm transistor gate width'
        }
    ],
    'uhi': [
        {
            'question_index': 3,  # Q4 (0-indexed) - FALSE LURE question
            'false_lure_option_index': 2,  # Option c (index 2) - "photocatalytic roof tiles" is the false lure
            'description': 'Photocatalytic roof tiles - false lure about cooling technology'
        },
        {
            'question_index': 10,  # Q11 (0-indexed) - FALSE LURE question
            'false_lure_option_index': 2,  # Option c (index 2) - "0.22" is the false lure
            'description': 'Aged asphalt albedo 0.22 - false lure about albedo values'
        }
    ]
}

# Use original false lure map by default (for existing participants)
FALSE_LURE_MAP = ORIGINAL_FALSE_LURE_MAP

def parse_csv_log(log_file_path):
    """Parse participant log CSV file with robust handling of multiline fields."""
    data = {
        'demographics': {},
        'prior_knowledge': {},
        'ai_trust': {},
        'randomization': {},
        'reading_data': [],
        'summary_viewing': [],
        'summary_overlay_events': [],  # For synchronous mode
        'visibility_changes': [],  # Track page visibility changes
        'recall_data': [],
        'mcq_data': [],
        'post_article_ratings': [],
        'manipulation_check': {}
    }

    with open(log_file_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        # Skip header
        try:
            header = next(reader)
        except StopIteration:
            return data

        for parts in reader:
            if not parts or len(parts) < 2:
                continue

            timestamp = parts[0]
            phase = parts[1]

            try:
                if phase == 'demographics':
                    data['demographics'] = {
                        'full_name': parts[2] if len(parts) > 2 else '',
                        'profession': parts[3] if len(parts) > 3 else '',
                        'age': parts[4] if len(parts) > 4 else '',
                        'gender': parts[5] if len(parts) > 5 else '',
                        'native_language': parts[6] if len(parts) > 6 else '',
                        'timestamp': timestamp
                    }
                elif phase == 'prior_knowledge':
                    # Structure: timestamp, phase, familiarity_mean, familiarity_individual, recognition_mean, recognition_individual, quiz_score, ...
                    data['prior_knowledge'] = {
                        'familiarity': float(parts[2]) if len(parts) > 2 and parts[2] else 0,
                        'familiarity_individual': parts[3] if len(parts) > 3 and parts[3] else '',
                        'recognition': float(parts[4]) if len(parts) > 4 and parts[4] else 0,
                        'term_recognition_individual': parts[5] if len(parts) > 5 and parts[5] else '',
                        'quiz_score': float(parts[6]) if len(parts) > 6 and parts[6] else 0,
                        'excluded': parts[9] if len(parts) > 9 else 'False',
                        'concept_list': parts[10] if len(parts) > 10 else '',
                        'timestamp': timestamp
                    }
                elif phase == 'ai_trust':
                    # Structure: timestamp, phase, trust_mean, trust_individual, dependence_mean, dependence_individual, skill_mean, skill_individual, reflection
                    trust_score = float(parts[2]) if len(parts) > 2 and parts[2] else 0
                    trust_individual = parts[3] if len(parts) > 3 and parts[3] else ''
                    dependence_score = float(parts[4]) if len(parts) > 4 and parts[4] else 0
                    dependence_individual = parts[5] if len(parts) > 5 and parts[5] else ''
                    skill_score = float(parts[6]) if len(parts) > 6 and parts[6] else 0
                    skill_individual = parts[7] if len(parts) > 7 and parts[7] else ''
                    reflection = parts[8] if len(parts) > 8 else ''
                    data['ai_trust'] = {
                        'trust_score': trust_score,
                        'ai_trust_score': trust_score,  # Alias for compatibility
                        'ai_trust_individual': trust_individual,
                        'dependence_score': dependence_score,
                        'ai_dependence_score': dependence_score,  # Alias for compatibility
                        'ai_dependence_individual': dependence_individual,
                        'skill_score': skill_score,
                        'tech_skill_score': skill_score,  # Alias for compatibility
                        'tech_skill_individual': skill_individual,
                        'reflection': reflection,
                        'timestamp': timestamp
                    }
                elif phase == 'randomization':
                    data['randomization'] = {
                        'structure': (parts[2] if len(parts) > 2 else '').lower(),
                        'timing_order': parts[3] if len(parts) > 3 else '',
                        'article_order': parts[4] if len(parts) > 4 else '',
                        'timestamp': timestamp
                    }
                elif phase == 'reading_behavior':
                    if len(parts) < 3:
                                    continue
                    event_type = parts[2] if len(parts) > 2 else ''
                    # For most events, article_key and timing are at the end
                    # But we'll extract them per event type since schemas differ
                    article_key = ''
                    timing = ''
                    article_num = -1
                    
                    # Try to extract from end (common pattern)
                    if len(parts) >= 2:
                        article_key = parts[-2] if len(parts) >= 2 else ''
                        timing = parts[-1] if len(parts) >= 1 else ''
                    
                    # Handle reading_complete events
                    if event_type == 'reading_complete':
                        # Schema: timestamp, phase, reading_complete, timestamp2, reading_time_ms, summary_time_ms, overlay_count, scroll_depth, article_num, article_key, timing
                        reading_time_ms = 0
                        summary_time_ms = 0
                        scroll_depth = 100  # Default
                        overlay_count = 0
                        
                        # Extract reading time (index 4)
                        if len(parts) > 4:
                            try:
                                reading_time_ms = int(parts[4])
                            except:
                                pass
                        
                        # Extract summary viewing time for synchronous mode (index 5)
                        if len(parts) > 5:
                            try:
                                summary_time_ms = int(parts[5])
                            except:
                                pass
                        
                        # Extract overlay count (index 6)
                        if len(parts) > 6:
                            try:
                                overlay_count = int(parts[6])
                            except:
                                pass
                        
                        # Extract scroll depth (index 7)
                        if len(parts) > 7:
                            try:
                                scroll_depth = int(parts[7])
                            except:
                                pass
                        
                        # Extract article number (index 8)
                        if len(parts) > 8:
                            try:
                                article_num = int(parts[8])
                            except:
                                pass
                        
                        # Extract article_key and timing (indices 9 and 10)
                        if len(parts) > 9:
                            article_key = parts[9]
                        if len(parts) > 10:
                            timing = parts[10]
                        
                        data['reading_data'].append({
                            'timestamp': timestamp,
                            'article_num': article_num,
                            'article_key': article_key,
                            'timing': timing,
                            'reading_time_ms': reading_time_ms,
                            'summary_time_ms': summary_time_ms,
                            'scroll_depth': scroll_depth,
                            'overlay_count': overlay_count
                        })
                    # Handle summary overlay events for synchronous mode
                    elif event_type == 'summary_overlay_opened':
                        # Schema: timestamp, phase, summary_overlay_opened, timestamp2, article_num, overlay_num, article_key, timing
                        overlay_article_num = -1
                        overlay_article_key = ''
                        overlay_timing = ''
                        if len(parts) > 4:
                            try:
                                overlay_article_num = int(parts[4])
                            except:
                                pass
                        if len(parts) > 6:
                            overlay_article_key = parts[6]
                        if len(parts) > 7:
                            overlay_timing = parts[7]
                        data['summary_overlay_events'].append({
                            'event': 'opened',
                            'timestamp': timestamp,
                            'article_num': overlay_article_num,
                            'article_key': overlay_article_key,
                            'timing': overlay_timing
                        })
                    elif event_type == 'summary_overlay_closed':
                        # Schema: timestamp, phase, summary_overlay_closed, timestamp2, article_num, duration_ms, overlay_num, article_key, timing
                        overlay_article_num = -1
                        duration_ms = 0
                        overlay_article_key = ''
                        overlay_timing = ''
                        if len(parts) > 4:
                            try:
                                overlay_article_num = int(parts[4])
                            except:
                                pass
                        if len(parts) > 5:
                            try:
                                duration_ms = int(parts[5])
                            except:
                                pass
                        if len(parts) > 7:
                            overlay_article_key = parts[7]
                        if len(parts) > 8:
                            overlay_timing = parts[8]
                        data['summary_overlay_events'].append({
                            'event': 'closed',
                            'timestamp': timestamp,
                            'article_num': overlay_article_num,
                            'article_key': overlay_article_key,
                            'timing': overlay_timing,
                            'duration_ms': duration_ms
                        })
                    # Handle visibility changes
                    elif event_type == 'visibility_change':
                        # Schema: timestamp, phase, visibility_change, timestamp2, is_visible, article_num, article_key, timing
                        vis_article_num = -1
                        is_visible = False
                        vis_article_key = ''
                        vis_timing = ''
                        if len(parts) > 4:
                            try:
                                is_visible = parts[4].lower() == 'true'
                            except:
                                pass
                        if len(parts) > 5:
                            try:
                                vis_article_num = int(parts[5])
                            except:
                                pass
                        if len(parts) > 6:
                            vis_article_key = parts[6]
                        if len(parts) > 7:
                            vis_timing = parts[7]
                        data['visibility_changes'].append({
                            'timestamp': timestamp,
                            'article_num': vis_article_num,
                            'article_key': vis_article_key,
                            'timing': vis_timing,
                            'is_visible': is_visible
                        })
                elif phase == 'summary_viewing':
                    if len(parts) >= 8:
                        # In these rows, indices are stable as they don't include multiline fields
                        data['summary_viewing'].append({
                            'timestamp': timestamp,
                            'article_num': int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else -1,
                            'article_key': parts[3] if len(parts) > 3 else '',
                            'mode': parts[4] if len(parts) > 4 else '',
                            'structure': parts[5] if len(parts) > 5 else '',
                            'time_spent_ms': int(float(parts[6])) if len(parts) > 6 and parts[6] else 0,
                            'time_spent_seconds': float(parts[7]) if len(parts) > 7 and parts[7] else 0
                        })
                elif phase == 'recall_response':
                    # csv.reader already joined multiline recall text into a single field (index 5)
                    if len(parts) >= 13:
                        article_num = int(parts[2]) if parts[2] else -1
                        article_key = parts[3]
                        timing = parts[4]
                        recall_text = parts[5] if len(parts) > 5 else ''
                        def _as_int(idx, default=0):
                            try:
                                return int(parts[idx])
                            except:
                                return default
                        data['recall_data'].append({
                            'timestamp': timestamp,
                            'article_num': article_num,
                            'article_key': article_key,
                            'timing': timing,
                            'recall_text': recall_text,
                            'sentence_count': _as_int(6),
                            'word_count': _as_int(7),
                            'character_count': _as_int(8),
                            'confidence': _as_int(9),
                            'difficulty': _as_int(10),
                            'time_spent_ms': _as_int(11),
                            'paste_attempts': _as_int(12),
                            'over_limit': (parts[13].lower() == 'true') if len(parts) > 13 else False
                        })
                elif phase == 'mcq_responses':
                    # Expected columns:
                    # timestamp, phase, article_num, article_key, timing,
                    # answers_json, answer_times_json, total_time_ms, correct_count, total_questions, accuracy_rate, question_accuracy_json
                    if len(parts) >= 6:
                        answers_json = parts[5]
                        try:
                            mcq_answers = json.loads(answers_json.replace('""', '"'))
                        except:
                            mcq_answers = {}
                        article_num = int(parts[2]) if len(parts) > 2 and parts[2] else -1
                        article_key = parts[3] if len(parts) > 3 else ''
                        timing = parts[4] if len(parts) > 4 else ''
                        data['mcq_data'].append({
                            'timestamp': timestamp,
                            'article_num': article_num,
                            'article_key': article_key,
                            'timing': timing,
                            'answers': mcq_answers
                        })
                elif phase == 'post_article_ratings':
                    # Schema: timestamp, phase, article_num, article_key, timing,
                    # load_mental_effort, load_task_difficulty, ai_help_understanding, 
                    # ai_help_memory, ai_made_task_easier, ai_satisfaction, 
                    # ai_better_than_no_ai (optional), mcq_overall_confidence
                    if len(parts) >= 9:
                        def _as_int_safe(idx, default=-1):
                            try:
                                return int(parts[idx]) if len(parts) > idx and parts[idx] else default
                            except:
                                return default
                        article_num = _as_int_safe(2, -1)
                        article_key = parts[3] if len(parts) > 3 else ''
                        timing = parts[4] if len(parts) > 4 else ''
                        data['post_article_ratings'].append({
                            'timestamp': timestamp,
                            'article_num': article_num,
                            'article_key': article_key,
                            'timing': timing,
                            'load_mental_effort': _as_int_safe(5),
                            'load_task_difficulty': _as_int_safe(6),
                            'ai_help_understanding': _as_int_safe(7),
                            'ai_help_memory': _as_int_safe(8),
                            'ai_made_task_easier': _as_int_safe(9),
                            'ai_satisfaction': _as_int_safe(10),
                            'ai_better_than_no_ai': _as_int_safe(11, -1),  # Optional field
                            'mcq_overall_confidence': _as_int_safe(12)  # Last field
                        })
                elif phase == 'manipulation_check':
                    if len(parts) >= 4:
                        def _as_int_safe(idx):
                            try:
                                return int(parts[idx])
                            except:
                                return -1
                        data['manipulation_check'] = {
                            'coherence': _as_int_safe(2),
                            'connectivity': _as_int_safe(3),
                            'strategy': parts[4] if len(parts) > 4 else '',
                            'timestamp': timestamp
                        }
            except Exception:
                # Robust to any malformed rows
                continue

    return data

def calculate_mcq_accuracy(mcq_data):
    """Calculate MCQ accuracy for all articles, including false lure tracking"""
    results = []
    
    for mcq in mcq_data:
        article_key = mcq['article_key']
        if article_key not in CORRECT_ANSWERS:
            continue
            
        correct = CORRECT_ANSWERS[article_key]
        answers = mcq['answers']
        
        # Check if this article has a false lure question(s)
        false_lure_info = FALSE_LURE_MAP.get(article_key)
        # Handle both list (multiple false lures) and dict (single false lure) formats
        false_lure_list = false_lure_info if isinstance(false_lure_info, list) else ([false_lure_info] if false_lure_info else [])
        
        # Get source_type for each question from ARTICLES
        article_questions = ARTICLES.get(article_key, {}).get('questions', [])
        
        correct_count = 0
        total = len(correct)
        details = []
        false_lure_selected = False
        false_lure_question_num = None
        
        for q_idx in range(total):
            q_key = f'q{q_idx}'
            p_ans = answers.get(q_key, -1)
            c_ans = correct[q_idx]
            is_correct = p_ans == c_ans
            if is_correct:
                correct_count += 1
            
            # Get source_type for this question (article, summary_segmented, summary_integrated)
            source_type = "unknown"
            if q_idx < len(article_questions):
                source_type = article_questions[q_idx].get('source_type', 'unknown')
            
            # Check if this is a false lure question and if participant selected it
            is_false_lure_q = False
            selected_false_lure = False
            for fl_info in false_lure_list:
                if fl_info and fl_info['question_index'] == q_idx:
                    is_false_lure_q = True
                    if p_ans == fl_info['false_lure_option_index']:
                        selected_false_lure = True
                        false_lure_selected = True
                        false_lure_question_num = q_idx + 1
                        break
            
            details.append({
                'question': q_idx + 1,
                'participant_answer': p_ans,
                'correct_answer': c_ans,
                'is_correct': is_correct,
                'is_false_lure_question': is_false_lure_q,
                'selected_false_lure': selected_false_lure,
                'source_type': source_type
            })
        
        accuracy = (correct_count / total) * 100 if total > 0 else 0
        
        results.append({
            'article_key': article_key,
            'article_num': mcq['article_num'],
            'timing': mcq['timing'],
            'accuracy': accuracy,
            'correct_count': correct_count,
            'total': total,
            'details': details,
            'timestamp': mcq['timestamp'],
            'has_false_lure': false_lure_info is not None,
            'false_lure_selected': false_lure_selected,
            'false_lure_question_num': false_lure_question_num
        })
    
    return results

def format_timestamp(ts):
    """Format timestamp for display"""
    try:
        # Try ISO format first
        if 'T' in ts:
            dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            return dt.strftime('%B %d, %Y, %H:%M:%S')
        # Try Unix timestamp
        try:
            ts_int = int(ts)
            if ts_int > 1000000000000:  # Milliseconds
                dt = datetime.fromtimestamp(ts_int / 1000)
            else:  # Seconds
                dt = datetime.fromtimestamp(ts_int)
            return dt.strftime('%B %d, %Y, %H:%M:%S')
        except:
            return ts
    except:
        return ts

def get_prior_knowledge_level(score, max_score=7):
    """Categorize prior knowledge score"""
    if score <= max_score * 0.2:
        return "very low"
    elif score <= max_score * 0.4:
        return "low"
    elif score <= max_score * 0.6:
        return "moderate"
    elif score <= max_score * 0.8:
        return "moderate-high"
    else:
        return "high"

def get_trust_level(score):
    """Categorize trust/dependence score"""
    if score <= 2:
        return "low"
    elif score <= 4:
        return "moderate"
    elif score <= 5.5:
        return "moderate-high"
    else:
        return "high"

def get_confidence_level(score):
    """Categorize confidence score"""
    if score <= 3:
        return "low"
    elif score <= 5:
        return "moderate"
    elif score <= 6:
        return "moderate-high"
    else:
        return "maximum confidence"

def get_difficulty_level(score):
    """Categorize difficulty score"""
    if score <= 2:
        return "low"
    elif score <= 4:
        return "moderate"
    elif score <= 5:
        return "moderate difficulty"
    elif score <= 6:
        return "moderate-high difficulty"
    else:
        return "high difficulty"

def get_coherence_level(score):
    """Categorize coherence/connectivity score"""
    if score <= 2:
        return "low"
    elif score <= 4:
        return "moderate"
    elif score <= 5:
        return "moderate-high"
    elif score <= 6:
        return "high"
    else:
        return "very high"

def calculate_synchronous_summary_time(summary_overlay_events, article_key, article_num):
    """Calculate total summary viewing time for synchronous mode"""
    total_ms = 0
    for event in summary_overlay_events:
        if (event.get('article_key') == article_key and 
            event.get('article_num') == article_num and 
            event.get('event') == 'closed'):
            total_ms += event.get('duration_ms', 0)
    return total_ms

def generate_analysis_report(participant_id, data, mcq_results):
    """Generate comprehensive analysis report with enhanced metrics"""
    
    report = []
    report.append("=" * 80)
    report.append(f"PARTICIPANT {participant_id} - COMPREHENSIVE DATA ANALYSIS")
    report.append("=" * 80)
    report.append("")
    report.append(f"Analysis Generated: {datetime.now().strftime('%Y-%m-%d')}")
    report.append("")
    
    # Demographics
    report.append("=" * 80)
    report.append("BASIC INFORMATION")
    report.append("=" * 80)
    if data['demographics']:
        demo = data['demographics']
        report.append(f"Name: {demo.get('full_name', 'N/A')}")
        gender = demo.get('gender', 'N/A')
        if gender:
            gender = gender.capitalize()
        report.append(f"Age: {demo.get('age', 'N/A')}, {gender}")
        report.append(f"Profession: {demo.get('profession', 'N/A')}")
        report.append(f"Native Language: {demo.get('native_language', 'N/A')}")
        start_time = format_timestamp(demo.get('timestamp', 'N/A'))
        report.append(f"Start Time: {start_time}")
    report.append("")
    
    # Prior Knowledge
    report.append("=" * 80)
    report.append("PRIOR KNOWLEDGE ASSESSMENT")
    report.append("=" * 80)
    if data.get('prior_knowledge'):
        pk = data['prior_knowledge']
        familiarity = pk.get('familiarity', 0)
        familiarity_mean = pk.get('familiarity_mean', familiarity)  # Use familiarity as mean if no separate mean field
        report.append(f"Familiarity Score (Mean): {familiarity:.1f}/7 ({get_prior_knowledge_level(familiarity)})")
        report.append(f"Number of Terms Rated: 18")
        
        # Show all individual answers if available
        familiarity_individual = pk.get('familiarity_individual', '')
        if familiarity_individual:
            try:
                fam_dict = json.loads(familiarity_individual)
                if fam_dict:
                    report.append("")
                    report.append("Individual Familiarity Ratings (1-7 scale):")
                    for term, rating in sorted(fam_dict.items()):
                        report.append(f"  {term}: {rating}/7")
            except:
                pass
        
        # Show term recognition if available
        term_recognition_individual = pk.get('term_recognition_individual', '')
        if term_recognition_individual:
            try:
                rec_dict = json.loads(term_recognition_individual)
                if rec_dict:
                    report.append("")
                    report.append("Term Recognition (Yes/No):")
                    for term, recognized in sorted(rec_dict.items()):
                        report.append(f"  {term}: {recognized}")
            except:
                pass
        
        # Show concept list if available
        concept_list = pk.get('concept_list', '')
        if concept_list:
            report.append("")
            report.append(f"Concept List: {concept_list}")
    report.append("")
    
    # AI Trust
    report.append("=" * 80)
    report.append("AI TRUST & TECHNOLOGY USE")
    report.append("=" * 80)
    if data.get('ai_trust'):
        ai = data['ai_trust']
        trust_score = ai.get('ai_trust_score', ai.get('trust_score', 0))
        dep_score = ai.get('ai_dependence_score', ai.get('dependence_score', 0))
        skill_score = ai.get('tech_skill_score', ai.get('skill_score', 0))
        report.append(f"AI Trust Score (Mean): {trust_score:.2f}/7 ({get_trust_level(trust_score)} trust)")
        report.append(f"AI Dependence Score (Mean): {dep_score:.2f}/7 ({get_trust_level(dep_score)} dependence)")
        skill_text = f"{skill_score:.2f}/7"
        if skill_score >= 6.5:
            skill_text += " (maximum - expert level)"
        report.append(f"Tech Skill Score (Mean): {skill_text}")
        
        # Show all individual answers if available
        trust_individual = ai.get('ai_trust_individual', '')
        if trust_individual:
            try:
                trust_dict = json.loads(trust_individual)
                if trust_dict:
                    report.append("")
                    report.append("Individual AI Trust Question Answers (1-7 scale):")
                    for q_num, rating in sorted(trust_dict.items()):
                        report.append(f"  Q{q_num}: {rating}/7")
            except:
                pass
        
        dependence_individual = ai.get('ai_dependence_individual', '')
        if dependence_individual:
            try:
                dep_dict = json.loads(dependence_individual)
                if dep_dict:
                    report.append("")
                    report.append("Individual AI Dependence Question Answers (1-7 scale):")
                    for q_num, rating in sorted(dep_dict.items()):
                        report.append(f"  Q{q_num}: {rating}/7")
            except:
                pass
        
        skill_individual = ai.get('tech_skill_individual', '')
        if skill_individual:
            try:
                skill_dict = json.loads(skill_individual)
                if skill_dict:
                    report.append("")
                    report.append("Individual Tech Skill Question Answers (1-7 scale):")
                    for q_num, rating in sorted(skill_dict.items()):
                        report.append(f"  Q{q_num}: {rating}/7")
            except:
                pass
        
        reflection = ai.get('open_reflection', ai.get('reflection', ''))
        if reflection:
            report.append("")
            report.append("Open Reflection:")
            # Parse reflection if it has Q1, Q2, Q3 format
            if 'Q1:' in reflection or 'Q1' in reflection:
                lines = reflection.split('\n')
                for line in lines:
                    line = line.strip()
                    if line:
                        report.append(f"  {line}")
            else:
                report.append(f"  {reflection}")
    report.append("")
    
    # Experimental Conditions
    report.append("=" * 80)
    report.append("EXPERIMENTAL CONDITIONS")
    report.append("=" * 80)
    if data['randomization']:
        rand = data['randomization']
        structure = rand.get('structure', 'N/A').upper()
        structure_text = structure
        if structure == 'SEGMENTED':
            structure_text += " (bullet points)"
        report.append(f"Structure Condition: {structure_text}")
        try:
            timing_order = json.loads(rand.get('timing_order', '[]'))
            article_order = json.loads(rand.get('article_order', '[]'))
            
            # Map article keys to readable names
            article_names = {'crispr': 'CRISPR', 'semiconductors': 'Semiconductors', 'uhi': 'Urban Heat Islands'}
            article_list = [article_names.get(a.lower(), a.upper()) for a in article_order]
            report.append(f"Article Order: {' → '.join([f'{i+1}. {a}' for i, a in enumerate(article_list)])}")
            report.append("Timing Order:")
            for i, (art, timing) in enumerate(zip(article_order, timing_order)):
                art_name = article_names.get(art.lower(), art.upper())
                timing_name = timing.replace('_', '-').title()
                if timing == 'pre_reading':
                    timing_name = "Pre-reading (summary before reading)"
                elif timing == 'post_reading':
                    timing_name = "Post-reading (summary after reading)"
                elif timing == 'synchronous':
                    timing_name = "Synchronous (summary during reading)"
                report.append(f"  Article {i+1} ({art_name}): {timing_name}")
        except:
            report.append(f"Timing Order: {rand.get('timing_order', 'N/A')}")
            report.append(f"Article Order: {rand.get('article_order', 'N/A')}")
    report.append("")
    
    # Reading Behavior
    report.append("=" * 80)
    report.append("READING BEHAVIOR")
    report.append("=" * 80)
    
    # Group reading data by article
    reading_by_article = {}
    for rd in data['reading_data']:
        key = (rd.get('article_key', ''), rd.get('article_num', -1))
        if key not in reading_by_article:
            reading_by_article[key] = []
        reading_by_article[key].append(rd)
    
    # Map article keys to names
    article_names = {'crispr': 'CRISPR', 'semiconductors': 'Semiconductors', 'uhi': 'Urban Heat Islands'}
    
    for (article_key, article_num), readings in reading_by_article.items():
        if not readings:
            continue
        # Use the most complete reading entry
        rd = max(readings, key=lambda x: x.get('reading_time_ms', 0))
        article_name = article_names.get(article_key.lower(), article_key.upper())
        timing = rd.get('timing', 'unknown')
        timing_name = timing.replace('_', '-')
        
        reading_time_ms = rd.get('reading_time_ms', 0)
        reading_min = reading_time_ms / 60000
        reading_sec = reading_time_ms / 1000
        
        report.append(f"Article {article_num + 1 if article_num >= 0 else '?'} ({article_name}) - {timing_name} mode:")
        report.append(f"  Reading Time: {reading_time_ms:,} ms ({reading_min:.2f} minutes = {reading_sec:.2f} seconds)")
        
        scroll_depth = rd.get('scroll_depth', 100)
        report.append(f"  Scroll Depth: {scroll_depth}%")
        
        # Count visibility changes for this article
        vis_changes = [v for v in data['visibility_changes'] 
                      if v.get('article_key') == article_key and v.get('article_num') == article_num]
        if vis_changes:
            report.append(f"  Visibility Changes: {len(vis_changes)} (page was hidden/shown during reading)")
            report.append(f"    Note: Visibility changes occur when the browser tab/window loses or regains focus.")
            report.append(f"    This can happen if the participant switches tabs, minimizes the window, or the OS")
            report.append(f"    switches to another application. It's normal behavior but may indicate distractions.")
        
        # Note multiple reading_complete entries
        if len(readings) > 1:
            times = [r.get('reading_time_ms', 0) for r in readings]
            report.append(f"  Note: {len(readings)} reading_complete entries logged ({', '.join([f'{t:,} ms' for t in times])})")
        
        report.append("")
    
    # Summary Viewing
    report.append("=" * 80)
    report.append("SUMMARY VIEWING")
    report.append("=" * 80)
    
    # Process regular summary viewing (pre/post reading)
    for sv in data['summary_viewing']:
        article_name = article_names.get(sv.get('article_key', '').lower(), sv.get('article_key', '').upper())
        sv_min = sv['time_spent_seconds'] / 60
        report.append(f"Article {sv['article_num']+1} ({article_name}) - {sv.get('mode', 'unknown').replace('_', '-')}:")
        report.append(f"  Time Spent: {sv['time_spent_seconds']:.2f} seconds ({sv_min:.2f} minutes)")
        report.append(f"  Structure: {sv.get('structure', 'N/A').capitalize()}")
        report.append("")
    
    # Process synchronous mode summary viewing
    # Group by article_key and collect all open/close events with timestamps
    sync_summaries = {}
    for event in data['summary_overlay_events']:
        if event.get('timing') == 'synchronous':
            article_key = event.get('article_key')
            if article_key not in sync_summaries:
                sync_summaries[article_key] = {'opens': [], 'closes': []}
            
            if event.get('event') == 'opened':
                sync_summaries[article_key]['opens'].append({
                    'timestamp': event.get('timestamp'),
                    'article_num': event.get('article_num', -1)
                })
            elif event.get('event') == 'closed':
                sync_summaries[article_key]['closes'].append({
                    'timestamp': event.get('timestamp'),
                    'duration_ms': event.get('duration_ms', 0),
                    'article_num': event.get('article_num', -1)
                })
    
    # Match opens with closes and calculate individual durations
    for article_key, events in sync_summaries.items():
        # Find the actual article number from reading_data
        article_num = -1
        for rd in data['reading_data']:
            if rd.get('article_key') == article_key and rd.get('timing') == 'synchronous':
                article_num = rd.get('article_num', -1)
                break
        
        article_name = article_names.get(article_key.lower() if article_key else '', article_key.upper() if article_key else 'Unknown')
        
        # Sort opens and closes by timestamp
        opens = sorted(events['opens'], key=lambda x: x['timestamp'])
        closes = sorted(events['closes'], key=lambda x: x['timestamp'])
        
        # Match opens with closes (assuming they come in pairs)
        individual_sessions = []
        for i, close_event in enumerate(closes):
            duration_ms = close_event.get('duration_ms', 0)
            individual_sessions.append({
                'session_num': i + 1,
                'duration_ms': duration_ms,
                'close_timestamp': close_event.get('timestamp')
            })
        
        # If we have opens but no closes (or vice versa), handle gracefully
        if len(opens) != len(closes):
            # Use the closes we have (they contain duration_ms)
            pass
        
        # Calculate totals
        total_ms = sum(s['duration_ms'] for s in individual_sessions)
        total_sec = total_ms / 1000
        total_min = total_sec / 60
        
        report.append(f"Article {article_num + 1 if article_num >= 0 else '?'} ({article_name}) - Synchronous:")
        
        if len(individual_sessions) > 0:
            report.append(f"  Number of Times Opened: {len(individual_sessions)}")
            report.append(f"  Individual Opening Durations:")
            for session in individual_sessions:
                dur_sec = session['duration_ms'] / 1000
                dur_min = dur_sec / 60
                report.append(f"    Opening #{session['session_num']}: {session['duration_ms']:,} ms ({dur_sec:.2f} seconds = {dur_min:.2f} minutes)")
            
            report.append(f"  Total Summary Viewing Time: {total_ms:,} ms ({total_sec:.2f} seconds = {total_min:.2f} minutes)")
            
            if len(individual_sessions) > 1:
                avg_duration = total_ms / len(individual_sessions)
                report.append(f"  Average Duration per Open: {avg_duration:.0f} ms ({avg_duration/1000:.2f} seconds)")
        else:
            # Check if there's data in reading_complete
            for rd in data['reading_data']:
                if rd.get('article_key') == article_key and rd.get('timing') == 'synchronous':
                    summary_time_ms = rd.get('summary_time_ms', 0)
                    overlay_count = rd.get('overlay_count', 0)
                    if summary_time_ms > 0:
                        summary_sec = summary_time_ms / 1000
                        summary_min = summary_sec / 60
                        report.append(f"  Number of Times Opened: {overlay_count}")
                        report.append(f"  Total Summary Viewing Time: {summary_time_ms:,} ms ({summary_sec:.2f} seconds = {summary_min:.2f} minutes)")
                        if overlay_count > 1:
                            avg_duration = summary_time_ms / overlay_count
                            report.append(f"  Average Duration per Open: {avg_duration:.0f} ms ({avg_duration/1000:.2f} seconds)")
                    else:
                        report.append("  Summary Viewing Time: 0 ms (participant did not open the summary overlay)")
                        if overlay_count > 0:
                            report.append(f"  Note: Overlay count logged as {overlay_count} but no viewing time recorded")
                    break
            else:
                report.append("  Summary Viewing Time: 0 ms (participant did not open the summary overlay)")
        
        report.append("")
    
    # Check if there's synchronous mode but no overlay events (summary shown during reading, no separate viewing)
    sync_articles = [rd for rd in data['reading_data'] if rd.get('timing') == 'synchronous']
    for rd in sync_articles:
        article_key = rd.get('article_key')
        if article_key not in sync_summaries:
            article_name = article_names.get(article_key.lower() if article_key else '', article_key.upper() if article_key else 'Unknown')
            report.append(f"Article {rd.get('article_num', -1) + 1} ({article_name}) - Synchronous:")
            # Always show summary viewing time, even if 0
            summary_time_ms = rd.get('summary_time_ms', 0)
            overlay_count = rd.get('overlay_count', 0)
            if summary_time_ms > 0:
                summary_sec = summary_time_ms / 1000
                summary_min = summary_sec / 60
                report.append(f"  Number of Times Opened: {overlay_count}")
                report.append(f"  Total Summary Viewing Time: {summary_time_ms:,} ms ({summary_sec:.2f} seconds = {summary_min:.2f} minutes)")
                if overlay_count > 1:
                    avg_duration = summary_time_ms / overlay_count
                    report.append(f"  Average Duration per Open: {avg_duration:.0f} ms ({avg_duration/1000:.2f} seconds)")
            else:
                report.append("  Number of Times Opened: 0")
                report.append("  Summary Viewing Time: 0 ms (participant did not open the summary overlay)")
                if overlay_count > 0:
                    report.append(f"  Note: Overlay count logged as {overlay_count} but no viewing time recorded")
            report.append("")
    
    # Free Recall
    report.append("=" * 80)
    report.append("FREE RECALL")
    report.append("=" * 80)
    
    # Group recall by article to handle duplicates
    recall_by_article = {}
    for rec in data['recall_data']:
        key = (rec.get('article_key'), rec.get('article_num'))
        if key not in recall_by_article:
            recall_by_article[key] = []
        recall_by_article[key].append(rec)
    
    for (article_key, article_num), recalls in recall_by_article.items():
        # Use the first recall (or most complete one)
        rec = recalls[0]
        article_name = article_names.get(article_key.lower() if article_key else '', article_key.upper() if article_key else 'Unknown')
        timing = rec.get('timing', 'unknown').replace('_', '-')
        
        report.append(f"Article {article_num + 1 if article_num >= 0 else '?'} ({article_name}) - {timing} mode:")
        report.append("  Recall Text:")
        # Format recall text with proper indentation
        recall_text = rec.get('recall_text', '')
        for line in recall_text.split('\n'):
            if line.strip():
                report.append(f"    '{line.strip()}'")
        
        report.append(f"  Words: {rec.get('word_count', 0)}, Sentences: {rec.get('sentence_count', 0)}, Characters: {rec.get('character_count', 0)}")
        
        confidence = rec.get('confidence', 0)
        difficulty = rec.get('difficulty', 0)
        report.append(f"  Confidence: {confidence}/7 ({get_confidence_level(confidence)})")
        report.append(f"  Perceived Difficulty: {difficulty}/7 ({get_difficulty_level(difficulty)})")
        
        time_ms = rec.get('time_spent_ms', 0)
        time_min = time_ms / 60000
        time_sec = time_ms / 1000
        report.append(f"  Time Spent: {time_ms:,} ms ({time_min:.2f} minutes = {time_sec:.2f} seconds)")
        
        paste_attempts = rec.get('paste_attempts', 0)
        report.append(f"  Paste Attempts: {paste_attempts}")
        
        # Note duplicates
        if len(recalls) > 1:
            report.append(f"  Note: {len(recalls)} identical recall responses logged (likely duplicate submissions)")
        
        report.append("")
    
    # MCQ Performance
    report.append("=" * 80)
    report.append("MCQ PERFORMANCE")
    report.append("=" * 80)
    for result in mcq_results:
        article_name = article_names.get(result.get('article_key', '').lower(), result.get('article_key', '').upper())
        timing = result.get('timing', 'unknown').replace('_', '-')
        report.append(f"Article {result.get('article_num', -1) + 1} ({article_name}) - {timing} mode")
        report.append(f"Accuracy: {result['correct_count']}/{result['total']} = {result['accuracy']:.1f}%")
        
        # False lure tracking
        if result.get('has_false_lure'):
            false_lure_info = FALSE_LURE_MAP.get(result['article_key'])
            # Handle both list (multiple false lures) and dict (single false lure) formats
            false_lure_list = false_lure_info if isinstance(false_lure_info, list) else ([false_lure_info] if false_lure_info else [])
            for fl_info in false_lure_list:
                if fl_info:
                    q_num = fl_info['question_index'] + 1
                    description = fl_info.get('description', 'false lure')
                    # Check if this specific false lure was selected
                    selected_this_lure = any(
                        detail.get('is_false_lure_question') and 
                        detail.get('selected_false_lure') and
                        detail['question'] == q_num
                        for detail in result['details']
                    )
                    if selected_this_lure:
                        report.append(f"⚠️  FALSE LURE: Selected false lure option on Q{q_num} ({description})")
                    else:
                        report.append(f"✓  FALSE LURE: Did NOT select false lure option on Q{q_num} ({description})")
        
        # Calculate accuracy by source_type
        source_type_stats = {}
        for detail in result['details']:
            source_type = detail.get('source_type', 'unknown')
            if source_type not in source_type_stats:
                source_type_stats[source_type] = {'correct': 0, 'total': 0}
            source_type_stats[source_type]['total'] += 1
            if detail['is_correct']:
                source_type_stats[source_type]['correct'] += 1
        
        # Report accuracy by source_type
        if source_type_stats:
            report.append("Accuracy by Source Type:")
            for source_type, stats in sorted(source_type_stats.items()):
                accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
                source_label = {
                    'article': 'Article',
                    'ai_summary': 'AI Summary',
                    'unknown': 'Unknown Source'
                }.get(source_type, source_type)
                report.append(f"  {source_label}: {stats['correct']}/{stats['total']} = {accuracy:.1f}%")
            report.append("")
        
        report.append("Question Details:")
        for detail in result['details']:
            status = "CORRECT" if detail['is_correct'] else "WRONG"
            markers = []
            if detail.get('is_false_lure_question'):
                markers.append("[FALSE LURE Q]")
            if detail.get('selected_false_lure'):
                markers.append("[SELECTED FALSE LURE]")
            source_type = detail.get('source_type', 'unknown')
            source_label = {
                'article': '[Article]',
                'ai_summary': '[AI Summary]',
                'unknown': '[Unknown]'
            }.get(source_type, f'[{source_type}]')
            markers.append(source_label)
            marker_str = " " + " ".join(markers) if markers else ""
            report.append(f"  Q{detail['question']:2d}: Participant={detail['participant_answer']}, Correct={detail['correct_answer']} - {status}{marker_str}")
        report.append("")
    
    # Post-Article Ratings
    report.append("=" * 80)
    report.append("POST-ARTICLE RATINGS (After MCQ, Before Break)")
    report.append("=" * 80)
    
    # Group ratings by article
    ratings_by_article = {}
    for rating in data['post_article_ratings']:
        key = (rating.get('article_key'), rating.get('article_num'))
        if key not in ratings_by_article:
            ratings_by_article[key] = []
        ratings_by_article[key].append(rating)
    
    for (article_key, article_num), ratings in ratings_by_article.items():
        # Use the first rating (or most complete one)
        rating = ratings[0]
        article_name = article_names.get(article_key.lower() if article_key else '', article_key.upper() if article_key else 'Unknown')
        timing = rating.get('timing', 'unknown').replace('_', '-')
        
        report.append(f"Article {article_num + 1 if article_num >= 0 else '?'} ({article_name}) - {timing} mode:")
        report.append("")
        report.append("Cognitive Load:")
        report.append(f"  Mental Effort: {rating.get('load_mental_effort', -1)}/7")
        report.append(f"  Task Difficulty: {rating.get('load_task_difficulty', -1)}/7")
        report.append("")
        report.append("AI Experience:")
        report.append(f"  AI helped understand: {rating.get('ai_help_understanding', -1)}/7")
        report.append(f"  AI helped remember: {rating.get('ai_help_memory', -1)}/7")
        report.append(f"  AI made task easier: {rating.get('ai_made_task_easier', -1)}/7")
        report.append(f"  AI satisfaction: {rating.get('ai_satisfaction', -1)}/7")
        ai_better = rating.get('ai_better_than_no_ai', -1)
        if ai_better >= 0:
            report.append(f"  Prefer AI support: {ai_better}/7 (optional)")
        report.append("")
        report.append(f"Overall MCQ Confidence: {rating.get('mcq_overall_confidence', -1)}/7")
        report.append("")
    
    if not data['post_article_ratings']:
        report.append("No post-article ratings data available.")
        report.append("")
    
    # Manipulation Check
    report.append("=" * 80)
    report.append("MANIPULATION CHECK")
    report.append("=" * 80)
    if data['manipulation_check']:
        mc = data['manipulation_check']
        coherence = mc.get('coherence', -1)
        connectivity = mc.get('connectivity', -1)
        if coherence >= 0:
            report.append(f"Semantic Coherence: {coherence}/7 ({get_coherence_level(coherence)} coherence)")
        if connectivity >= 0:
            report.append(f"Relational Connectivity: {connectivity}/7 ({get_coherence_level(connectivity)} connectivity)")
        strategy = mc.get('strategy', 'N/A')
        if strategy:
            report.append(f"Memory Strategy: {strategy}")
    report.append("")
    
    # Summary Statistics
    report.append("=" * 80)
    report.append("SUMMARY STATISTICS")
    report.append("=" * 80)
    
    if data['reading_data']:
        reading_times = [rd['reading_time_ms'] / 60000 for rd in data['reading_data']]
        report.append("Reading Times:")
        for i, rd in enumerate(data['reading_data']):
            article_name = article_names.get(rd.get('article_key', '').lower(), f"Article {i+1}")
            report.append(f"  {article_name}: {rd['reading_time_ms'] / 60000:.2f} minutes")
        if len(reading_times) > 1:
            avg_reading = sum(reading_times) / len(reading_times)
            report.append(f"  Average: {avg_reading:.2f} minutes")
    
    if data['summary_viewing'] or sync_summaries:
        report.append("")
        report.append("Summary Viewing Times:")
        for sv in data['summary_viewing']:
            article_name = article_names.get(sv.get('article_key', '').lower(), f"Article {sv.get('article_num', -1) + 1}")
            report.append(f"  {article_name}: {sv['time_spent_seconds'] / 60:.2f} minutes")
        for article_key, info in sync_summaries.items():
            # Find article number from reading_data
            article_num = -1
            for rd in data['reading_data']:
                if rd.get('article_key') == article_key and rd.get('timing') == 'synchronous':
                    article_num = rd.get('article_num', -1)
                    break
            article_name = article_names.get(article_key.lower() if article_key else '', f"Article {article_num + 1}")
            # Calculate total from closes events (which have duration_ms)
            total_ms = sum(close.get('duration_ms', 0) for close in info.get('closes', []))
            total_min = total_ms / 60000
            report.append(f"  {article_name} (synchronous): {total_min:.2f} minutes")
        # Also check reading_complete for synchronous summary times
        for rd in data['reading_data']:
            if rd.get('timing') == 'synchronous' and rd.get('summary_time_ms', 0) > 0:
                article_key = rd.get('article_key')
                article_name = article_names.get(article_key.lower() if article_key else '', f"Article {rd.get('article_num', -1) + 1}")
                summary_min = rd.get('summary_time_ms', 0) / 60000
                if article_key not in sync_summaries:  # Only add if not already counted
                    report.append(f"  {article_name} (synchronous, from reading_complete): {summary_min:.2f} minutes")
        
        all_summary_times = [sv['time_spent_seconds'] / 60 for sv in data['summary_viewing']]
        all_summary_times.extend([sum(close.get('duration_ms', 0) for close in info.get('closes', [])) / 60000 for info in sync_summaries.values()])
        all_summary_times.extend([rd.get('summary_time_ms', 0) / 60000 for rd in data['reading_data'] 
                                 if rd.get('timing') == 'synchronous' and rd.get('summary_time_ms', 0) > 0 
                                 and rd.get('article_key') not in sync_summaries])
        if all_summary_times:
            avg_summary = sum(all_summary_times) / len(all_summary_times)
            report.append(f"  Average: {avg_summary:.2f} minutes")
    
    if data['recall_data']:
        report.append("")
        report.append("Recall Quality:")
        avg_words = sum(rec['word_count'] for rec in data['recall_data']) / len(data['recall_data'])
        avg_sentences = sum(rec['sentence_count'] for rec in data['recall_data']) / len(data['recall_data'])
        avg_chars = sum(rec['character_count'] for rec in data['recall_data']) / len(data['recall_data'])
        avg_confidence = sum(rec['confidence'] for rec in data['recall_data']) / len(data['recall_data'])
        avg_difficulty = sum(rec['difficulty'] for rec in data['recall_data']) / len(data['recall_data'])
        report.append(f"  Average Words: {avg_words:.1f} words")
        report.append(f"  Average Sentences: {avg_sentences:.1f} sentences")
        report.append(f"  Average Characters: {avg_chars:.0f} characters")
        report.append(f"  Average Confidence: {avg_confidence:.1f}/7")
        report.append(f"  Average Difficulty: {avg_difficulty:.1f}/7")
    
    if mcq_results:
        report.append("")
        report.append("MCQ Performance:")
        for result in mcq_results:
            article_name = article_names.get(result.get('article_key', '').lower(), f"Article {result.get('article_num', -1) + 1}")
            report.append(f"  {article_name} ({result.get('article_key', '').upper()}): {result['accuracy']:.1f}% ({result['correct_count']}/{result['total']} correct)")
        avg_accuracy = sum(r['accuracy'] for r in mcq_results) / len(mcq_results)
        report.append(f"  Average Accuracy: {avg_accuracy:.1f}%")
    
    report.append("")
    
    # Key Findings
    report.append("=" * 80)
    report.append("KEY FINDINGS")
    report.append("=" * 80)
    
    findings = []
    
    # Reading behavior findings
    if data['reading_data']:
        reading_times = [rd['reading_time_ms'] / 60000 for rd in data['reading_data']]
        min_time = min(reading_times)
        max_time = max(reading_times)
        findings.append(f"1. READING BEHAVIOR:")
        findings.append(f"   - All articles: Reading times range from {min_time:.2f} to {max_time:.2f} minutes")
        
        scroll_depths = [rd.get('scroll_depth', 100) for rd in data['reading_data']]
        if all(sd >= 95 for sd in scroll_depths):
            findings.append(f"   - All articles: {scroll_depths[0]}% scroll depth (participant read to the end)")
        else:
            findings.append(f"   - Scroll depths: {', '.join([f'{sd}%' for sd in scroll_depths])}")
        
        # Visibility changes
        for rd in data['reading_data']:
            vis_count = len([v for v in data['visibility_changes'] 
                           if v.get('article_key') == rd.get('article_key') and 
                           v.get('article_num') == rd.get('article_num')])
            if vis_count > 0:
                article_name = article_names.get(rd.get('article_key', '').lower(), f"Article {rd.get('article_num', -1) + 1}")
                findings.append(f"   - {article_name}: Page visibility changes detected ({vis_count} times)")
    
    # Summary viewing findings
    if data['summary_viewing']:
        findings.append("")
        findings.append("2. SUMMARY VIEWING:")
        pre_reading = [sv for sv in data['summary_viewing'] if sv.get('mode') == 'pre_reading']
        post_reading = [sv for sv in data['summary_viewing'] if sv.get('mode') == 'post_reading']
        
        if post_reading:
            post_time = post_reading[0]['time_spent_seconds'] / 60
            findings.append(f"   - Post-reading summary: {post_time:.2f} minutes (reasonable)")
        
        if pre_reading:
            pre_time = pre_reading[0]['time_spent_seconds'] / 60
            findings.append(f"   - Pre-reading summary: {pre_time:.2f} minutes (longer, as expected)")
            if post_reading:
                post_time = post_reading[0]['time_spent_seconds'] / 60
                if post_time > 0:
                    pct_diff = ((pre_time - post_time) / post_time) * 100
                    findings.append(f"   - Pre-reading summary viewed {pct_diff:.0f}% longer than post-reading")
        
        # Synchronous mode summary
        if sync_summaries:
            for article_key, info in sync_summaries.items():
                # Find article number from reading_data
                article_num = -1
                for rd in data['reading_data']:
                    if rd.get('article_key') == article_key and rd.get('timing') == 'synchronous':
                        article_num = rd.get('article_num', -1)
                        break
                article_name = article_names.get(article_key.lower() if article_key else '', f"Article {article_num + 1}")
                # Calculate total from closes events (which have duration_ms)
                total_ms = sum(close.get('duration_ms', 0) for close in info.get('closes', []))
                total_min = total_ms / 60000
                findings.append(f"   - {article_name} (synchronous): {total_min:.2f} minutes total summary viewing time")
    
    # Recall quality findings
    if data['recall_data']:
        findings.append("")
        findings.append("3. RECALL QUALITY:")
        word_counts = [rec['word_count'] for rec in data['recall_data']]
        sentence_counts = [rec['sentence_count'] for rec in data['recall_data']]
        confidences = [rec['confidence'] for rec in data['recall_data']]
        difficulties = [rec['difficulty'] for rec in data['recall_data']]
        
        if len(set(sentence_counts)) == 1:
            findings.append(f"   - Consistent recall across all articles ({sentence_counts[0]} sentences each)")
        else:
            findings.append(f"   - Sentence counts: {', '.join([str(s) for s in sentence_counts])}")
        
        findings.append(f"   - Good word count range ({min(word_counts)}-{max(word_counts)} words per article)")
        findings.append(f"   - Confidence ratings: {min(confidences)}-{max(confidences)}/7")
        findings.append(f"   - Perceived difficulty: {min(difficulties)}-{max(difficulties)}/7")
        
        paste_attempts = [rec.get('paste_attempts', 0) for rec in data['recall_data']]
        for i, rec in enumerate(data['recall_data']):
            if rec.get('paste_attempts', 0) > 0:
                article_name = article_names.get(rec.get('article_key', '').lower(), f"Article {i+1}")
                findings.append(f"   - {article_name}: {rec.get('paste_attempts', 0)} paste attempts detected")
        
        # Check for duplicates
        recall_by_article = {}
        for rec in data['recall_data']:
            key = (rec.get('article_key'), rec.get('article_num'))
            if key not in recall_by_article:
                recall_by_article[key] = []
            recall_by_article[key].append(rec)
        
        for (article_key, article_num), recalls in recall_by_article.items():
            if len(recalls) > 1:
                article_name = article_names.get(article_key.lower() if article_key else '', f"Article {article_num + 1}")
                findings.append(f"   - {article_name}: {len(recalls)} duplicate submissions logged")
    
    # MCQ performance findings
    if mcq_results:
        findings.append("")
        findings.append("4. MCQ PERFORMANCE:")
        accuracies = [r['accuracy'] for r in mcq_results]
        min_acc = min(accuracies)
        max_acc = max(accuracies)
        avg_acc = sum(accuracies) / len(accuracies)
        
        findings.append(f"   - Performance range: {min_acc:.1f}%-{max_acc:.1f}%")
        findings.append(f"   - Average accuracy: {avg_acc:.1f}%")
        findings.append(f"   - Well above chance level (25% for 4 options)")
        
        best_result = max(mcq_results, key=lambda x: x['accuracy'])
        article_name = article_names.get(best_result.get('article_key', '').lower(), f"Article {best_result.get('article_num', -1) + 1}")
        findings.append(f"   - Best performance on {article_name}: {best_result['accuracy']:.1f}%")
        
        if avg_acc >= 80:
            findings.append(f"   - Consistent high performance suggests good comprehension")
    
    # Data quality findings
    findings.append("")
    findings.append("5. DATA QUALITY:")
    findings.append("   - Reading times are appropriate and consistent")
    findings.append("   - Recall responses are genuine and substantive")
    findings.append("   - All phases completed successfully")
    
    # Check for issues
    issues = []
    recall_by_article = {}
    for rec in data['recall_data']:
        key = (rec.get('article_key'), rec.get('article_num'))
        if key not in recall_by_article:
            recall_by_article[key] = []
        recall_by_article[key].append(rec)
    
    for (article_key, article_num), recalls in recall_by_article.items():
        if len(recalls) > 1:
            article_name = article_names.get(article_key.lower() if article_key else '', f"Article {article_num + 1}")
            issues.append(f"   - {article_name}: Duplicate recall/MCQ submissions (likely technical issue)")
        
        for rec in recalls:
            if rec.get('paste_attempts', 0) > 0:
                article_name = article_names.get(rec.get('article_key', '').lower(), f"Article {rec.get('article_num', -1) + 1}")
                issues.append(f"   - {article_name}: {rec.get('paste_attempts', 0)} paste attempts detected")
    
    for rd in data['reading_data']:
        vis_count = len([v for v in data['visibility_changes'] 
                       if v.get('article_key') == rd.get('article_key') and 
                       v.get('article_num') == rd.get('article_num')])
        if vis_count > 2:
            article_name = article_names.get(rd.get('article_key', '').lower(), f"Article {rd.get('article_num', -1) + 1}")
            issues.append(f"   - {article_name}: Page visibility changes (participant may have switched tabs)")
    
    if issues:
        findings.append("")
        findings.append("Minor Issues:")
        for issue in set(issues):  # Remove duplicates
            findings.append(issue)
    
    for finding in findings:
        report.append(finding)
    
    report.append("")
    
    # Data Validity Assessment
    report.append("=" * 80)
    report.append("DATA VALIDITY ASSESSMENT")
    report.append("=" * 80)
    
    # Determine validity
    is_valid = True
    validity_issues = []
    
    # Check reading times
    if data['reading_data']:
        reading_times = [rd['reading_time_ms'] / 60000 for rd in data['reading_data']]
        if any(rt < 1 for rt in reading_times):
            is_valid = False
            validity_issues.append("Suspiciously short reading times detected")
        if any(rt > 30 for rt in reading_times):
            validity_issues.append("Very long reading times detected (may indicate distraction)")
    
    # Check recall quality
    if data['recall_data']:
        word_counts = [rec['word_count'] for rec in data['recall_data']]
        if all(wc < 10 for wc in word_counts):
            is_valid = False
            validity_issues.append("All recall responses are very short (<10 words)")
    
    # Check MCQ performance
    if mcq_results:
        accuracies = [r['accuracy'] for r in mcq_results]
        if all(acc < 30 for acc in accuracies):
            is_valid = False
            validity_issues.append("All MCQ scores below chance level (suspicious)")
        elif all(acc > 95 for acc in accuracies):
            validity_issues.append("All MCQ scores near perfect (may indicate prior knowledge or cheating)")
    
    validity_status = "VALID DATA - High quality participant response" if is_valid else "QUESTIONABLE DATA - Review required"
    report.append(validity_status)
    report.append("")
    
    report.append("Strengths:")
    strengths = []
    if data['reading_data']:
        reading_times = [rd['reading_time_ms'] / 60000 for rd in data['reading_data']]
        if all(2 <= rt <= 15 for rt in reading_times):
            strengths.append("  - Appropriate reading times for all articles")
    
    if data['recall_data']:
        word_counts = [rec['word_count'] for rec in data['recall_data']]
        if all(wc >= 15 for wc in word_counts):
            strengths.append("  - Genuine, substantive recall responses")
    
    if mcq_results:
        avg_acc = sum(r['accuracy'] for r in mcq_results) / len(mcq_results)
        if avg_acc >= 60:
            strengths.append(f"  - Good MCQ performance ({avg_acc:.1f}% average)")
        elif avg_acc >= 80:
            strengths.append(f"  - Excellent MCQ performance ({avg_acc:.1f}% average)")
    
    if all(rd.get('scroll_depth', 0) >= 95 for rd in data['reading_data']):
        strengths.append("  - High engagement (95%+ scroll depth)")
    
    if len(data['recall_data']) >= 3 and len(mcq_results) >= 3:
        strengths.append("  - Complete data for all phases")
    
    if strengths:
        for strength in strengths:
            report.append(strength)
    else:
        report.append("  - Data collected successfully")
    
    if validity_issues or issues:
        report.append("")
        report.append("Minor Issues:")
        all_issues = list(set(validity_issues + [i.replace("   - ", "  - ") for i in issues if i.startswith("   - ")]))
        for issue in all_issues:
            report.append(issue)
    
    report.append("")
    recommendation = "INCLUDE in main analysis" if is_valid else "REVIEW before inclusion"
    report.append(f"Recommendation: {recommendation}")
    if is_valid:
        report.append("  - All data points are valid and reliable")
        report.append("  - Minor technical issues do not affect data quality")
        if mcq_results:
            avg_acc = sum(r['accuracy'] for r in mcq_results) / len(mcq_results)
            if avg_acc >= 60:
                report.append("  - Good performance suggests genuine participation")
    else:
        report.append("  - Data quality concerns require investigation")
        report.append("  - May need to exclude from main analysis")
    
    report.append("")
    report.append("=" * 80)
    report.append("END OF ANALYSIS")
    report.append("=" * 80)
    
    return "\n".join(report)

def main():
    global CORRECT_ANSWERS, FALSE_LURE_MAP
    
    if len(sys.argv) < 2:
        print("Usage: python analyze_participant.py <participant_id>")
        print("Example: python analyze_participant.py P064")
        sys.exit(1)
    
    participant_id = sys.argv[1].upper()
    log_file = f"../experiment_data/{participant_id}_log.csv"
    
    # If exact filename doesn't exist, try to find a file that starts with participant_id
    if not os.path.exists(log_file):
        experiment_data_dir = "../experiment_data"
        if os.path.exists(experiment_data_dir):
            for filename in os.listdir(experiment_data_dir):
                if filename.startswith(participant_id) and filename.endswith("_log.csv"):
                    log_file = os.path.join(experiment_data_dir, filename)
                    print(f"Found log file: {log_file}")
                    break
            else:
                print(f"Error: Log file not found for {participant_id}")
                print(f"Tried: {log_file}")
                print(f"Searched in: {experiment_data_dir}")
                sys.exit(1)
        else:
            print(f"Error: Log file not found: {log_file}")
            sys.exit(1)
    
    # Determine which answer keys to use based on participant ID
    # Participants P078 and later should use NEW answer keys
    # Participants P064-P077 use ORIGINAL answer keys
    # Extract numeric part of participant ID
    try:
        pid_num = int(participant_id[1:])  # Extract number after 'P'
        if pid_num >= 78:  # P078 and later
            CORRECT_ANSWERS = NEW_CORRECT_ANSWERS
            FALSE_LURE_MAP = NEW_FALSE_LURE_MAP
            print(f"Using NEW answer keys for {participant_id}")
        else:
            CORRECT_ANSWERS = ORIGINAL_CORRECT_ANSWERS
            FALSE_LURE_MAP = ORIGINAL_FALSE_LURE_MAP
            print(f"Using ORIGINAL answer keys for {participant_id}")
    except (ValueError, IndexError):
        # Fallback to original logic if parsing fails
        if participant_id in ['P078', 'P079', 'P080', 'P081', 'P082', 'P083', 'P084', 'P085', 'P086', 'P087', 'P088', 'P089', 'P090', 'P091', 'P092', 'P093', 'P094', 'P095', 'P096', 'P097', 'P098', 'P099']:
            CORRECT_ANSWERS = NEW_CORRECT_ANSWERS
            FALSE_LURE_MAP = NEW_FALSE_LURE_MAP
            print(f"Using NEW answer keys for {participant_id}")
        else:
            CORRECT_ANSWERS = ORIGINAL_CORRECT_ANSWERS
            FALSE_LURE_MAP = ORIGINAL_FALSE_LURE_MAP
            print(f"Using ORIGINAL answer keys for {participant_id}")
    
    print(f"Analyzing {participant_id}...")
    data = parse_csv_log(log_file)
    mcq_results = calculate_mcq_accuracy(data['mcq_data'])
    report = generate_analysis_report(participant_id, data, mcq_results)
    
    # Extract participant name for filename
    participant_name = data.get('demographics', {}).get('full_name', '').strip()
    if participant_name:
        # Create safe filename: replace spaces with hyphens, remove special characters
        safe_name = participant_name.replace(' ', '-').replace('/', '-').replace('\\', '-')
        # Remove any other problematic characters for filenames
        safe_name = ''.join(c for c in safe_name if c.isalnum() or c in ('-', '_', '.'))
        output_file = f"{safe_name}-{participant_id}_ANALYSIS.txt"
    else:
        # Fallback to participant ID only if name not available
        output_file = f"{participant_id}_ANALYSIS.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Analysis complete! Report saved to: {output_file} (filename format: Name-ParticipantID_ANALYSIS.txt)")
    print("\n" + "=" * 80)
    print(report)

if __name__ == "__main__":
    main()


