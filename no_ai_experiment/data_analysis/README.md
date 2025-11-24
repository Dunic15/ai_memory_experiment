# Data Analysis Folder

This folder contains all data analysis files and scripts for the memory experiment (control version - no AI).

## Quick Access

### Analysis Script
- **`analyze_participant.py`** - Python script to analyze individual participant data
  - Usage: `python analyze_participant.py <PARTICIPANT_ID>`
  - Example: `python analyze_participant.py P064`
  - Generates comprehensive analysis reports with MCQ accuracy, reading times, recall quality, etc.

### Participant Analyses
- Analysis files will be generated here as participants complete the experiment
- Files are named: `{PARTICIPANT_ID}_ANALYSIS.txt`

## How to Use

### Analyze a Single Participant

```bash
cd data_analysis
python3 analyze_participant.py P064
```

This generates a comprehensive analysis report including:
- Demographics and basic information
- Prior knowledge assessment
- Experimental conditions
- Reading behavior (times, scroll depth)
- Free recall quality (words, sentences, confidence)
- MCQ performance (accuracy, question-by-question breakdown)
- Summary statistics
- Key findings and data validity assessment

### Analysis Output

The script generates a text file named `{PARTICIPANT_ID}_ANALYSIS.txt` with:
- Complete participant demographics
- All experimental data (reading times, recall, MCQ answers)
- MCQ accuracy calculations (correct/incorrect for each question)
- Summary statistics (averages, totals)
- Data quality assessment
- Recommendations for inclusion/exclusion

## File Structure

```
data_analysis/
├── README.md (this file)
├── analyze_participant.py (analysis script)
├── false_lure_mapping.json (false lure configuration)
├── FALSE_LURE_MAPPING.md (false lure documentation)
└── {PARTICIPANT_ID}_ANALYSIS.txt (generated analysis files)
```

## Analysis Report Contents

Each analysis report includes:

1. **Basic Information** - Demographics, start time
2. **Prior Knowledge Assessment** - Familiarity, recognition, quiz scores
3. **Experimental Conditions** - Article order
4. **Reading Behavior** - Reading times, scroll depth, visibility changes
5. **Free Recall** - Recall text, word count, confidence, difficulty
6. **MCQ Performance** - Accuracy per article, question-by-question breakdown
7. **Summary Statistics** - Averages across all articles
8. **Key Findings** - Reading behavior, recall quality, MCQ performance
9. **Data Validity Assessment** - Strengths, weaknesses, recommendations

## Correct Answers Reference

The script uses the following correct answers for MCQ accuracy calculation:

- **Urban Heat Islands (UHI)**: [1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 1, 1, 1, 1, 1]
- **CRISPR**: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1]
- **Semiconductors**: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1]

These are 0-indexed option indices (0 = first option, 1 = second option, etc.)

## Data Quality Guidelines

### Valid Data (Include)
- Reading times: 6-15 minutes per article
- Recall: Genuine responses with substantive content
- MCQ: Performance above chance (25% for 4 options)
- Complete data for all phases

### Test Data (Exclude)
- Reading times: < 1 minute per article
- Recall: Test inputs or nonsensical responses
- Multiple duplicate submissions
- Empty or missing required fields

### Issues to Note
- Duplicate submissions (may be technical issues)
- Page visibility changes (participant may have switched tabs)
- Paste attempts (may indicate copy-paste behavior)

## Usage Tips

1. **Analyze a new participant:**
   ```bash
   python3 analyze_participant.py P065
   ```

2. **View analysis report:**
   ```bash
   cat P064_COMPLETE_ANALYSIS.txt
   ```

3. **Compare participants:**
   - Open multiple analysis files side-by-side
   - Compare MCQ accuracy, reading times, recall quality

4. **Batch analysis:**
   - Create a script to analyze all participants
   - Use the analysis script in a loop for multiple participants

## Notes

- All analysis files are stored in this folder for easy access
- The analysis script parses CSV log files from `../experiment_data/`
- MCQ accuracy is calculated based on correct answers defined in the script
- Reading times are converted to minutes for readability
- This is the control version (no AI) - analysis focuses on reading behavior, recall, and MCQ performance

## Additional Resources

- See `../docs/DATA_GUIDE.md` for complete data storage and interpretation guide
- See `../docs/README_DOCS.md` for documentation index
- See main `../README.md` for experiment overview
