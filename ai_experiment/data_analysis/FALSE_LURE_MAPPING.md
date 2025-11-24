# False Lure Question Mapping

## Overview

This document maps false lure questions across all articles. False lure questions are designed to test whether participants are influenced by information that appears plausible but is explicitly marked as false or not mentioned in the text.

## Current False Lure Questions

### CRISPR Article
- **Question #10** (Index 9, 0-indexed)
- **Question Text**: "Which agricultural experiment served as an early demonstrative marker of CRISPR feasibility?"
- **False Lure Option**: Option 1 (Index 1) - "Bioluminescent plants engineered to visualize successful editing events through light emission (FALSE - not mentioned in text)"
- **Correct Answer**: Option 1 (Index 1) - Note: The correct answer is the same index, but the correct option is actually "Pest-resistant vegetables..." (Option 2, Index 1 in the answer key)
- **Description**: Tests whether participants select the bioluminescent plants option despite it being marked as false

## How False Lures Are Tracked

### In the Data
- False lure questions are identified by the presence of "(FALSE - not mentioned in text)" or similar markers in the option text
- The mapping is stored in `FALSE_LURE_MAP` in `analyze_participant.py`

### In the Analysis
- The analysis script automatically detects false lure questions
- For each article with a false lure:
  - Reports whether the participant selected the false lure option
  - Marks the false lure question in the question details with `[FALSE LURE Q]`
  - Marks if the participant selected it with `[SELECTED FALSE LURE]`

### Example Output
```
Article 1 (CRISPR) - synchronous mode
Accuracy: 10/15 = 66.7%
⚠️  FALSE LURE: Selected false lure option on Q10 (bioluminescent plants)
Question Details:
  Q10: Participant=1, Correct=1 - CORRECT [FALSE LURE Q] [SELECTED FALSE LURE]
```

## Data Structure

The false lure mapping is defined as:
```python
FALSE_LURE_MAP = {
    'crispr': {
        'question_index': 9,  # 0-indexed (Q10 in 1-indexed)
        'false_lure_option_index': 1,  # Option index containing "(FALSE - not mentioned in text)"
        'description': 'Bioluminescent plants - false lure about agricultural experiments'
    }
}
```

## Analysis Fields

For each MCQ result, the following false lure fields are available:
- `has_false_lure`: Boolean indicating if the article has a false lure question
- `false_lure_selected`: Boolean indicating if participant selected the false lure option
- `false_lure_question_num`: Question number (1-indexed) if false lure was selected

In question details:
- `is_false_lure_question`: Boolean indicating if this question is the false lure
- `selected_false_lure`: Boolean indicating if participant selected the false lure option for this question

## Adding New False Lures

To add a false lure for another article:

1. Identify the question index (0-indexed) and the option index containing the false lure
2. Add to `FALSE_LURE_MAP` in `analyze_participant.py`:
```python
'uhi': {
    'question_index': X,  # 0-indexed
    'false_lure_option_index': Y,  # Option index
    'description': 'Description of the false lure'
}
```

## Notes

- Currently, only CRISPR has a false lure question
- The false lure is explicitly marked in the option text with "(FALSE - not mentioned in text)"
- Participants who select the false lure option are flagged in the analysis
- This helps identify whether participants are reading carefully or being influenced by plausible-sounding distractors

