# MCQ Questions Update - Changes Summary

## Date: 2025-11-12

## What Changed

### 1. **All MCQ Questions Replaced**
   - **CRISPR (Article 1)**: All 15 questions completely replaced with new questions
   - **Semiconductors (Article 2)**: All 15 questions completely replaced with new questions  
   - **Urban Heat Islands (Article 3)**: All 15 questions completely replaced with new questions

### 2. **Answer Keys Updated**
   - **CRISPR**: New answer key: `[1, 2, 1, 0, 2, 0, 2, 0, 2, 3, 1, 3, 2, 1, 0]`
   - **Semiconductors**: New answer key: `[2, 1, 1, 0, 0, 2, 2, 1, 0, 1, 3, 1, 2, 1, 3]`
   - **Urban Heat Islands**: New answer key: `[0, 2, 0, 2, 1, 0, 3, 1, 2, 0, 1, 2, 1, 2, 2]`

### 3. **False Lure Questions Updated**
   - **Previous**: Only CRISPR had a false lure at Q10 (index 9)
   - **New**: All three articles now have false lure questions at **Q2 (index 1)**
     - CRISPR Q2: False lure about "Bioluminescent marker plants"
     - Semiconductors Q2: False lure about "Ultra-pure resins"
     - Urban Heat Islands Q2: False lure about "Stored heat releases gradually"

### 4. **Analysis Output Format**
   - Analysis files are saved as: `{PARTICIPANT_ID}_ANALYSIS.txt`
   - Example: `P064_ANALYSIS.txt`, `P069_ANALYSIS.txt`, etc.
   - False lure tracking now appears in all analyses with:
     - `✓ FALSE LURE: Did NOT select false lure option on Q2` (if participant avoided the lure)
     - `⚠️ FALSE LURE: Selected false lure option on Q2` (if participant selected the lure)
     - Question details show `[FALSE LURE Q]` marker for false lure questions
     - Question details show `[SELECTED FALSE LURE]` marker if participant selected the lure

## Impact on Existing Data

### Why Accuracy Scores Changed
The accuracy scores for existing participants have changed because:
1. **Questions are completely different** - The new questions test different knowledge
2. **Answer keys are different** - The correct answers for the new questions don't match the old participant responses
3. **This is expected** - Participant responses were given to the old questions, so they cannot be accurately scored against the new questions

### Example: P064
- **Old Analysis**: CRISPR 66.7%, Semiconductors 100%, UHI 86.7%
- **New Analysis**: CRISPR 20.0%, Semiconductors 33.3%, UHI 40.0%
- **Reason**: P064's responses were to the old questions, which don't match the new answer keys

## Files Modified

1. **`app.py`**: 
   - Updated `ARTICLES['crispr']['questions']` (15 new questions)
   - Updated `ARTICLES['semiconductors']['questions']` (15 new questions)
   - Updated `ARTICLES['uhi']['questions']` (15 new questions)

2. **`data_analysis/analyze_participant.py`**:
   - Updated `CORRECT_ANSWERS` dictionary with new answer keys for all articles
   - Updated `FALSE_LURE_MAP` to include false lures for all three articles at Q2
   - Enhanced false lure tracking in `calculate_mcq_accuracy()` function
   - Enhanced false lure reporting in `generate_analysis_report()` function
   - Added comment clarifying filename format: `{PARTICIPANT_ID}_ANALYSIS.txt`

## Re-analysis Results

All existing participant data has been re-analyzed with the new questions and answer keys:

- **P064**: Average accuracy 26.7% (CRISPR 20%, Semiconductors 33.3%, UHI 40%)
- **P069**: Average accuracy 22.2% (CRISPR 20%, Semiconductors 20%, UHI 26.7%) - **Selected false lure on Semiconductors Q2**
- **P074**: Average accuracy 24.4% (CRISPR 26.7%, Semiconductors 20%, UHI 26.7%)
- **P076**: Average accuracy 28.9% (CRISPR 20%, Semiconductors 26.7%, UHI 40%)
- **P077**: Average accuracy 17.8% (CRISPR 6.7%, Semiconductors 20%, UHI 26.7%)

## Important Note

⚠️ **The accuracy scores for existing participants are NOT meaningful** because their responses were given to the old questions. These participants would need to retake the test with the new questions to get valid accuracy scores.

The re-analysis is useful for:
- Testing the new analysis system
- Verifying false lure tracking works correctly
- Ensuring the analysis script functions properly with new questions

## Next Steps

For future participants:
- They will see the new questions
- Their responses will be scored against the new answer keys
- False lure tracking will work correctly for all three articles

