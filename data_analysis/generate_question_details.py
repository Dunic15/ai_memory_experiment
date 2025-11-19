#!/usr/bin/env python3
"""
Generate detailed question-by-question analysis for a participant
Shows full question text, all options, participant's answer, and correct answer
"""

import json
import csv
import sys
import os

# Import articles from app.py to ensure we use the latest answer keys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import ARTICLES as ARTICLES_FROM_APP

# Use articles from app.py (this ensures we always have the latest answer keys)
ARTICLES = ARTICLES_FROM_APP

# Legacy hardcoded data (kept for reference but not used)
_LEGACY_ARTICLES = {
    'uhi': {
        'title': 'Urban Heat Islands: Causes, Consequences, and What Works',
        'questions': [
            {"q": "Urban heat islands form when cities are _______ than surrounding rural regions.", "options": ["cooler", "warmer", "more humid", "less ventilated"], "correct": 1},
            {"q": "Dark low-albedo materials such as asphalt absorb _______ percent of solar radiation.", "options": ["fifty to sixty", "seventy to eighty", "ninety to ninety-five", "forty to fifty"], "correct": 2},
            {"q": "_______ materials retain absorbed heat throughout daylight hours and release it gradually after sunset.", "options": ["Low thermal mass", "Reflective", "Porous", "High thermal mass"], "correct": 3},
            {"q": "Urban canyon geometry traps _______ through multiple inter-surface reflections", "options": ["outgoing longwave radiation", "thermal mass discharge", "convective airflow", "incoming solar reflection"], "correct": 0},
            {"q": "The article describes _______ as a real cooling technology.", "options": ["phase-change wall layers", "radiative cooling materials", "photocatalytic roof tiles", "waste-heat recovery networks"], "correct": 1},
            {"q": "Cool roofs limit heat accumulation because their reflectance often reaches _______.", "options": ["0.05–0.10", "0.30–0.45", "0.70–0.85", "0.15–0.25"], "correct": 2},
            {"q": "Neighborhoods with elevated heat burdens commonly lack _______.", "options": ["access to coastal airflow", "open water bodies", "tree canopy and permeable surfaces", "shaded pedestrian corridors"], "correct": 2},
            {"q": "High-albedo roofing systems limit heat gain primarily through _______.", "options": ["reduction of absorbed solar flux", "increased thermal mass storage", "moisture-driven evaporative cooling", "redistribution of longwave radiation"], "correct": 0},
            {"q": "Urban forestry provides dual thermal benefits: direct radiative shading plus _______ cooling via stomatal transpiration.", "options": ["conductive", "evaporative", "radiative", "convective"], "correct": 1},
            {"q": "Effective heat mitigation requires _______ planning combining technical interventions with equitable resource distribution.", "options": ["sectoral", "regional", "integrated", "centralized"], "correct": 2},
            {"q": "Vegetated ground cover typically has an albedo of _______.", "options": ["0.30–0.35", "0.05–0.10", "0.20–0.25", "0.45–0.60"], "correct": 2},
            {"q": "Aged asphalt commonly exhibits an albedo of _______.", "options": ["0.05", "0.12", "0.22", "0.30"], "correct": 1},
            {"q": "Restricted airflow inside urban canyons prevents _______ heat removal.", "options": ["radiative", "conductive", "evaporative", "convective"], "correct": 3},
            {"q": "Urban centers can be _______ warmer at night than nearby suburbs.", "options": ["3–7°C", "7–10°C", "1–2°C", "10–12°C"], "correct": 0},
            {"q": "Cool pavements can reduce surface temperatures by _______.", "options": ["4–8°C", "10–20°C", "20–30°C", "2–5°C"], "correct": 1}
        ]
    },
    'crispr': {
        'title': 'CRISPR Gene Editing: Promise, Constraints, and Responsible Use',
        'questions': [
            {"q": "CRISPR began as _______ that allows bacteria to capture pieces of viral DNA.", "options": ["a bacterial immune system", "a viral defense mechanism", "a cellular repair system", "a genetic storage method"], "correct": 0},
            {"q": "Early CRISPR agricultural trials created _______ as editing markers.", "options": ["fluorescent proteins", "bioluminescent plants", "pigment variations", "no commercial products"], "correct": 3},
            {"q": "Scientists reprogrammed CRISPR using _______ to direct Cas enzymes.", "options": ["protein markers", "DNA templates", "guide RNA", "chemical signals"], "correct": 2},
            {"q": "The CRISPR process follows: guide, cut, and _______", "options": ["restore", "repair", "replicate", "remove"], "correct": 1},
            {"q": "Compared to TALENs, CRISPR is faster, cheaper, and _______", "options": ["easier to program", "widely adopted", "highly adaptable", "technically refined"], "correct": 2},
            {"q": "Off-target edits occur when guide RNAs _______", "options": ["bind wrong sites", "degrade quickly", "fail to activate", "lose stability"], "correct": 0},
            {"q": "Base editors modify DNA without _______", "options": ["using guide RNA", "breaking both strands", "requiring enzymes", "cellular repair"], "correct": 1},
            {"q": "AAV vectors are efficient but have limited _______", "options": ["precision", "capacity", "persistence", "flexibility"], "correct": 1},
            {"q": "Lipid nanoparticles concentrate in the _______", "options": ["kidneys", "lungs", "heart", "liver"], "correct": 3},
            {"q": "Self-limiting systems use components that _______", "options": ["degrade fast", "trigger once", "persist weakly", "accumulate slowly"], "correct": 0},
            {"q": "Ex vivo editing allows doctors to _______ before reinfusion.", "options": ["modify doses", "test compatibility", "verify accuracy", "label samples"], "correct": 2},
            {"q": "SHERLOCK and DETECTR are CRISPR-based _______", "options": ["gene editors", "pathogen detectors", "delivery systems", "repair tools"], "correct": 1},
            {"q": "After 2018's gene-edited babies, countries imposed _______", "options": ["research limits", "safety protocols", "clinical bans", "patent restrictions"], "correct": 2},
            {"q": "Gene-edited organisms differ from transgenic by lacking _______", "options": ["foreign DNA", "added genes", "external markers", "modified traits"], "correct": 0},
            {"q": "CRISPR components are described as cheap and _______", "options": ["regulated", "rarely used", "highly protected", "widely available"], "correct": 3}
        ]
    },
    'semiconductors': {
        'title': 'Semiconductor Supply Chains: Why Shortages Happen and How to Build Resilience',
        'questions': [
            {"q": "The shortage revealed that semiconductor dependence extends across _______.", "options": ["financial services, medical systems, educational institutions", "automobiles, consumer electronics, and infrastructure", "maritime logistics, rare-earth exports, fertilizer chains", "defense procurement, steel manufacturing, agriculture"], "correct": 1},
            {"q": "Semiconductor supply froze during the pandemic when _______ occurred simultaneously.", "options": ["gas-purity issues, dopant shortages, packaging bottlenecks", "substrate shortages, port slowdowns, chemical-plant outages", "demand surges, factory shutdowns, logistics failures", "workforce gaps, wafer contamination, tool installation delays"], "correct": 2},
            {"q": "Each semiconductor fabrication plant requires _______ billions of dollars and years to build.", "options": ["tens of", "hundreds of", "thousands of", "millions of"], "correct": 0},
            {"q": "Automakers that pre-booked capacity were prioritized because allocation depended as much on contracts as on _______ needs.", "options": ["production", "technology", "financial", "logistics"], "correct": 1},
            {"q": "Geographic concentration in East Asia and the Netherlands creates _______ vulnerabilities.", "options": ["buffered", "redundant", "distributed", "single-point"], "correct": 3},
            {"q": "Just-in-time failed because production involves _______.", "options": ["diverse part numbers", "non-interchangeable chips", "long cycle times", "unstable demand shifts"], "correct": 2},
            {"q": "When automotive demand collapsed in 2020, foundries shifted capacity toward _______.", "options": ["mobile processors", "computing systems", "digital displays", "consumer electronics"], "correct": 3},
            {"q": "Companies shifting to risk-adjusted strategies now maintain inventories and develop _______ supply contracts.", "options": ["adaptive", "multi-year", "flexible", "diversified"], "correct": 0},
            {"q": "Government support for semiconductor initiatives reached funding levels in the range of _______.", "options": ["less than one billion", "several hundred million", "around five trillion", "tens of billions"], "correct": 3},
            {"q": "The technology used in advanced semiconductor manufacturing is _______.", "options": ["quantum processors", "extreme ultraviolet", "deep-UV scanners", "plasma emitters"], "correct": 1},
            {"q": "Photoresist materials require _______", "options": ["rare-earth dopants", "purified gases", "semiconductor-grade coatings", "ultra-pure resins"], "correct": 3},
            {"q": "At the 3nm process node, transistor gate widths correspond to roughly _______.", "options": ["44 carbon atoms", "35 silicon atoms", "48 silicon atoms", "52 carbon atoms"], "correct": 2},
            {"q": "Intermediate capacity expansions typically require _______ to complete.", "options": ["one to two years", "three to five months", "five to seven years", "ten to twelve months"], "correct": 0},
            {"q": "By 2019, some manufacturers operated on _______ for certain components.", "options": ["single-week buffers", "two-month buffers", "quarterly buffers", "ten-day buffers"], "correct": 0},
            {"q": "Western advanced-node production requires subsidies amounting to _______ of total costs.", "options": ["around one-tenth", "roughly one-quarter to one-third", "nearly one-half", "two-thirds"], "correct": 1}
        ]
    }
}  # End of legacy articles - not used, kept for reference only

def parse_csv_log(log_file_path):
    """Parse participant log CSV file to extract MCQ data"""
    mcq_data_list = []
    
    with open(log_file_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        
        for parts in reader:
            if not parts or len(parts) < 2:
                continue
            
            phase = parts[1]
            
            if phase == 'mcq_responses':
                article_num = int(parts[2]) if len(parts) > 2 else -1
                article_key = parts[3] if len(parts) > 3 else ''
                timing = parts[4] if len(parts) > 4 else ''
                
                # Parse both mcq_answers (raw participant selections) and question_accuracy
                mcq_answers = {}
                question_accuracy = {}
                
                if len(parts) > 5:
                    try:
                        mcq_answers_str = parts[5]
                        if mcq_answers_str.startswith('"') and mcq_answers_str.endswith('"'):
                            mcq_answers_str = json.loads(mcq_answers_str)
                        mcq_answers = json.loads(mcq_answers_str)
                    except (json.JSONDecodeError, ValueError):
                        pass
                
                if len(parts) > 11:
                    try:
                        question_accuracy_str = parts[11]
                        if question_accuracy_str.startswith('"') and question_accuracy_str.endswith('"'):
                            question_accuracy_str = json.loads(question_accuracy_str)
                        question_accuracy = json.loads(question_accuracy_str)
                    except (json.JSONDecodeError, ValueError):
                        pass
                
                if mcq_answers or question_accuracy:
                    mcq_data_list.append({
                        'article_num': article_num,
                        'article_key': article_key,
                        'timing': timing,
                        'mcq_answers': mcq_answers,  # Raw participant selections
                        'question_accuracy': question_accuracy  # Analysis with mappings
                    })
    
    return mcq_data_list

def generate_question_details(participant_id):
    """Generate detailed question-by-question file for a participant"""
    log_file = f"../experiment_data/{participant_id}_log.csv"
    
    if not os.path.exists(log_file):
        print(f"Error: Log file not found: {log_file}")
        return
    
    mcq_data_list = parse_csv_log(log_file)
    
    if not mcq_data_list:
        print(f"Error: No MCQ data found for {participant_id}")
        return
    
    print(f"Found {len(mcq_data_list)} MCQ entries")
    
    output_lines = []
    output_lines.append("=" * 80)
    output_lines.append(f"PARTICIPANT {participant_id} - DETAILED QUESTION ANALYSIS")
    output_lines.append("=" * 80)
    output_lines.append("")
    
    # Process each article
    for mcq_data in mcq_data_list:
        article_key = mcq_data['article_key']
        article_num = mcq_data['article_num']
        timing = mcq_data['timing']
        question_accuracy = mcq_data['question_accuracy']
        
        if article_key not in ARTICLES:
            continue
        
        article = ARTICLES[article_key]
        article_title = article['title']
        questions = article['questions']
        mcq_answers = mcq_data.get('mcq_answers', {})  # Raw participant selections
        question_accuracy = mcq_data.get('question_accuracy', {})  # Analysis with mappings
        
        output_lines.append("=" * 80)
        output_lines.append(f"ARTICLE {article_num + 1}: {article_title}")
        output_lines.append(f"Timing Condition: {timing}")
        output_lines.append("=" * 80)
        output_lines.append("")
        
        # Build mapping from randomized index to original index
        rand_to_orig = {}
        if isinstance(question_accuracy, dict) and len(question_accuracy) > 0:
            for q_key, q_data in question_accuracy.items():
                if isinstance(q_data, dict):
                    rand_idx = q_data.get('randomized_question_index', int(q_key[1:]) if q_key[1:].isdigit() else -1)
                    orig_idx = q_data.get('original_question_index', rand_idx)
                    rand_to_orig[rand_idx] = orig_idx
        
        # If no mapping available, assume questions weren't randomized
        if not rand_to_orig:
            for i in range(len(questions)):
                rand_to_orig[i] = i
        
        # Process each original question
        for orig_idx in range(len(questions)):
            # Find which randomized position this original question was shown at
            rand_idx = None
            for r_idx, o_idx in rand_to_orig.items():
                if o_idx == orig_idx:
                    rand_idx = r_idx
                    break
            
            if rand_idx is None:
                rand_idx = orig_idx  # Fallback if mapping not found
            
            # Get participant's answer from raw mcq_answers using randomized index
            q_key = f'q{rand_idx}'
            participant_answer = mcq_answers.get(q_key)
            
            # If not found in mcq_answers, try question_accuracy as fallback
            if participant_answer is None and q_key in question_accuracy:
                participant_answer = question_accuracy[q_key].get('participant_answer')
            
            # Use the correct answer from the article definition
            correct_answer = questions[orig_idx]['correct']
            is_correct = (participant_answer is not None and participant_answer == correct_answer)
            
            question = questions[orig_idx]
            question_text = question['q']
            options = question['options']
            
            display_note = f" (Displayed as #{rand_idx + 1})" if rand_idx != orig_idx else ""
            output_lines.append(f"Question {orig_idx + 1}{display_note}:")
            output_lines.append(f"  {question_text}")
            output_lines.append("")
            output_lines.append("  Options:")
            
            for i, option in enumerate(options):
                marker = ""
                if i == participant_answer:
                    marker = " ← PARTICIPANT'S ANSWER"
                if i == correct_answer:
                    marker += " [CORRECT ANSWER]"
                if i == participant_answer and i == correct_answer:
                    marker = " ← PARTICIPANT'S ANSWER [CORRECT]"
                
                option_letter = chr(97 + i)  # a, b, c, d
                output_lines.append(f"    {option_letter}) {option}{marker}")
            
            output_lines.append("")
            output_lines.append(f"  Result: {'✓ CORRECT' if is_correct else '✗ WRONG'}")
            output_lines.append("")
            output_lines.append("-" * 80)
            output_lines.append("")
    
    # Write output file
    output_file = f"{participant_id}_QUESTION_DETAILS.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    print(f"Question details file created: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 generate_question_details.py <participant_id>")
        print("Example: python3 generate_question_details.py P091")
        sys.exit(1)
    
    participant_id = sys.argv[1].upper()
    if not participant_id.startswith('P'):
        participant_id = f"P{participant_id.zfill(3)}"
    
    generate_question_details(participant_id)

