# Chinese Translation System - How It Works

## Overview

The experiment platform uses an **automatic translation system** that translates all content (articles, questions, UI text) from English to Chinese (Simplified Chinese) when a user selects Chinese as their language.

## Architecture

### 1. **Translation Engine**
- Uses `GoogleTranslator` from the `deep-translator` library
- Maps language code `"zh"` to `"zh-CN"` (Simplified Chinese)
- Automatically detects source language (usually English)

### 2. **Two-Level Caching System**

#### **Level 1: In-Memory Cache (Fast)**
- Stored in `_translation_cache` dictionary
- Loaded at application startup
- Provides instant access (no API calls needed)
- Format: `{"zh:English text": "中文翻译"}`

#### **Level 2: File-Based Cache (Persistent)**
- Stored in `translation_cache/translations.json`
- Persists across server restarts
- Loaded into memory at startup
- Format: JSON file with key-value pairs

### 3. **Translation Flow**

```
User selects Chinese language
    ↓
System checks: Is text already translated?
    ↓
YES → Return cached translation (instant)
    ↓
NO → Call Google Translator API
    ↓
Save to cache (both memory and file)
    ↓
Return translation
```

## How Translations Are Generated

### **Step 1: Pre-Translation (On Server Start)**

When the Flask app starts, it automatically:

1. **Loads existing cache** from `translations.json`
2. **Pre-translates UI text** (buttons, labels, etc.)
3. **Pre-translates ALL article content**:
   - Article titles
   - Article text (full articles)
   - AI summaries (both integrated and segmented)
   - All questions and answer options
   - Prior knowledge terms
   - AI trust questions

**Why pre-translate?**
- First run: Takes 30-60 seconds to translate everything
- Subsequent runs: Instant (everything is cached)
- Users never wait for translations during the experiment

### **Step 2: Runtime Translation (On-Demand)**

If a translation is missing (shouldn't happen after pre-translation):

1. Check in-memory cache
2. If not found, check file cache
3. If still not found, call Google Translator
4. Save to both caches
5. Return translation

### **Step 3: Long Text Handling**

For texts longer than 4500 characters (Google's limit):

1. Split text by sentences (periods, exclamation marks, question marks)
2. Translate each chunk separately
3. Recombine translated chunks
4. Save complete translation to cache

## Translation Functions

### **`_auto_translate(text, target_lang)`**
- Main translation function
- Handles caching automatically
- Splits long texts automatically
- Returns original text if translation fails

### **`tr(text)`**
- Helper function for templates
- Uses current session language
- Example: `{{ tr("Continue") }}` → "继续" (if Chinese selected)

### **`get_localized_article(article_key)`**
- Returns fully translated article
- Translates: title, text, summaries, questions, options
- Keeps answer indices unchanged (only translates text)

## Cache Structure

### **Cache Key Format**
```
"{language}:{original_text}"
```

Example:
```json
{
  "zh:Continue": "继续",
  "zh:Dark, low-albedo surfaces such as asphalt absorb approximately _______ percent of incoming solar radiation.": "像沥青等深色、低反照率表面大约会吸收 _______ 的太阳辐射。"
}
```

### **Cache File Location**
```
ai_experiment/translation_cache/translations.json
```

## When Translations Happen

### **Automatic Translation:**
- ✅ Article titles
- ✅ Article full text
- ✅ AI summaries (integrated and segmented)
- ✅ All MCQ questions
- ✅ All MCQ answer options
- ✅ UI buttons and labels
- ✅ Prior knowledge terms
- ✅ AI trust questions

### **NOT Translated:**
- ❌ Answer indices (0, 1, 2, 3 stay the same)
- ❌ Participant IDs
- ❌ Timestamps
- ❌ Numerical data

## Example: How a Question Gets Translated

### **English Version (in app.py):**
```python
{
    "q": "Dark, low-albedo surfaces such as asphalt absorb approximately _______ percent of incoming solar radiation.",
    "options": [
        "fifty to sixty",
        "seventy to eighty",
        "ninety to ninety-five",
        "forty to fifty"
    ],
    "correct": 2  # Index stays the same!
}
```

### **Chinese Version (automatically generated):**
```python
{
    "q": "像沥青等深色、低反照率表面大约会吸收 _______ 的太阳辐射。",
    "options": [
        "50–60%",
        "70–80%",
        "90–95%",
        "40–50%"
    ],
    "correct": 2  # Same index!
}
```

## Language Selection

### **How Users Select Language:**
1. User visits `/language_selection` page
2. Selects "中文" (Chinese) or "English"
3. Language stored in Flask session: `session["lang"] = "zh"`
4. All subsequent pages use this language

### **How System Determines Language:**
```python
def _get_lang():
    lang = session.get("lang") or DEFAULT_LANG
    if lang not in SUPPORTED_LANGS:
        lang = DEFAULT_LANG
    return lang
```

## Performance

### **First Run (No Cache):**
- Pre-translation: 30-60 seconds
- All content translated and cached
- File saved to `translations.json`

### **Subsequent Runs (With Cache):**
- Load cache: < 1 second
- All translations instant (from memory)
- No API calls needed

### **During Experiment:**
- All translations are instant (from cache)
- No delays for users
- No API rate limiting issues

## Manual Translation Updates

If you need to update a specific translation:

1. **Edit the cache file directly:**
   ```json
   {
     "zh:Your English text": "您的中文翻译"
   }
   ```

2. **Or let the system re-translate:**
   - Delete the specific key from `translations.json`
   - Restart the server
   - System will re-translate on next access

## Translation Quality

- Uses Google Translate API (high quality)
- Context-aware translations
- Handles technical terms appropriately
- Preserves formatting and structure

## Troubleshooting

### **Translations not showing:**
1. Check `translation_cache/translations.json` exists
2. Check file has translations (not empty)
3. Check `deep-translator` is installed: `pip install deep-translator`

### **Slow loading:**
- First run always takes 30-60 seconds (pre-translation)
- Subsequent runs should be instant
- If slow, check cache file exists and is loaded

### **Missing translations:**
- Check server logs for translation errors
- Verify Google Translator is working
- Check network connection (needed for first-time translations)

## Summary

The translation system is **fully automatic** and **cached for performance**:
- ✅ Translates everything on first run
- ✅ Caches all translations for instant access
- ✅ No manual translation needed
- ✅ Works seamlessly for users
- ✅ Preserves answer indices and data structure





















