# Synchronous Reading Time Analysis

## Question
Does the synchronous reading time include the time when the summary overlay was open?

## Answer
**YES** - The synchronous reading time DOES include the time spent viewing the summary overlay.

## Technical Details

### How Reading Time is Tracked
In the `reading.html` template (line 381):
```javascript
readingTime = Date.now() - startTime;
```

This calculates the **total elapsed time** from when the reading page loaded until the user clicked "Continue".

### How Summary Viewing Time is Tracked (Synchronous Mode)
When the summary overlay is opened/closed:
- Opening: `summaryOverlayStartTime = Date.now()`
- Closing: `summaryViewTime += Date.now() - summaryOverlayStartTime`

Both values (`readingTime` and `summaryViewTime`) are logged separately, but **the reading time is NOT adjusted** to exclude the summary viewing time.

## Recalculated Statistics

### Original Values (from your image)
| Condition | Pre-reading | Synchronous | Post-reading | Average |
|-----------|-------------|-------------|--------------|---------|
| **Integrated** | 7.34 min | **9.04 min** | 7.98 min | 8.12 min |
| **Segmented** | 6.11 min | **8.74 min** | 7.40 min | 7.41 min |

### Adjusted Values (Excluding Summary Viewing Time)
| Condition | Pre-reading | Synchronous (Original) | Synchronous (Adjusted) | Post-reading | Average (Original) | Average (Adjusted) |
|-----------|-------------|------------------------|------------------------|--------------|-------------------|-------------------|
| **Integrated** | 7.01 min | **9.04 min** | **6.44 min** | 7.25 min | 7.81 min | **6.89 min** |
| **Segmented** | 5.39 min | **8.25 min** | **6.76 min** | 5.93 min | 6.52 min | **6.03 min** |

### Key Findings

1. **Synchronous Reading Time Reduction:**
   - **Integrated**: 9.04 → 6.44 min (-2.60 min, -28.8%)
   - **Segmented**: 8.25 → 6.76 min (-1.49 min, -18.1%)

2. **Summary Viewing Time:**
   - **Integrated**: Average of 2.60 minutes spent viewing summary
   - **Segmented**: Average of 1.49 minutes spent viewing summary

3. **Overall Average Reading Time:**
   - **Integrated**: 7.81 → 6.89 min (-0.92 min, -11.8%)
   - **Segmented**: 6.52 → 6.03 min (-0.49 min, -7.5%)

## Implications

### With Summary Time Included (Original)
- Synchronous reading appears to take the **longest time** (9.04 and 8.25 min)
- This makes synchronous reading seem less efficient

### With Summary Time Excluded (Adjusted)
- Synchronous reading is actually **more comparable** to other conditions
- **Integrated synchronous**: 6.44 min (between pre-reading 7.01 and post-reading 7.25)
- **Segmented synchronous**: 6.76 min (between pre-reading 5.39 and post-reading 5.93)
- Shows that participants spent similar time on the **actual article reading** across conditions

### Interesting Pattern
- **Integrated condition** participants spent **more time** viewing the summary during synchronous reading (2.60 min vs 1.49 min for segmented)
- This could suggest that:
  - Integrated summaries are more engaging or require more time to process
  - OR segmented summaries are easier to scan/reference quickly
  - OR integrated structure participants rely more on the summary

## Recommendation

For your analysis, you should report **both values**:
1. **Total time on page** (original) - shows total engagement including summary use
2. **Pure reading time** (adjusted) - shows actual article reading time

This distinction is important for understanding:
- How much time participants spend **reading the article** vs **consulting the AI summary**
- Whether synchronous access changes **reading behavior** vs just adding summary consultation time
