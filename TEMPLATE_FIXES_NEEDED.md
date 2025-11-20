# TEMPLATE FIXES NEEDED

## Problem Identified:

The templates are displaying summaries, but there's a mismatch in formatting:

1. **INTEGRATED summaries** (A1) → Should display as paragraphs with line breaks
2. **SEGMENTED summaries** (A2) → Should display as **NUMBERED** list (1. 2. 3. ... 10.)

## Current Issues:

### Issue 1: Integrated Summary Display
When you see this:
```
Between 2020 and 2022, a synchronized disruption...
* Allocation during the shortage...
* Recent pilot programs explored...
* Major semiconductor companies...
```

This is because the template is breaking the integrated summary into bullets. **This might be intentional design**, but if you want continuous paragraphs instead, we need to fix the templates.

### Issue 2: Segmented Summary Display
The segmented bullets should be **NUMBERED** (1-10), not disc bullets (•).

## Files That Need Fixing:

1. `/templates/reading.html` - Lines 226-246 (synchronous mode summary display)
2. `/templates/ai_summary_view.html` - Lines 100-130 (pre/post reading summary display)

## Recommended Fixes:

### Fix 1: reading.html (Synchronous Mode)
Around line 226-246, change the integrated summary display from bullets to paragraphs.

### Fix 2: ai_summary_view.html  
Around line 100-130, ensure segmented summaries show **numbered** lists (1-10).

## Quick Test:
To verify which format you're seeing:
- **INTEGRATED (A1)**: Should be 4 paragraphs (like your document shows with bullet points/asterisks from \n\n breaks)
- **SEGMENTED (A2)**: Should be 10 numbered items (1. 2. 3. ... 10.)

Would you like me to create the exact template fixes?
