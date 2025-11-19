# Post-Article Ratings Feature Documentation

## Overview

After each article's Free Recall and MCQ completion, participants are presented with a short survey to rate their experience with that specific article. This screen appears **three times** (once after each of the three articles).

## When the Screen Appears

The post-article ratings screen is displayed:
- **After** the participant completes the Free Recall for an article
- **After** the participant completes the MCQ block for that article
- **Before** the break (for articles 1 and 2) or before the manipulation check (for article 3)

## Screen Details

### Title
"Short survey about this article"

### Introduction Text
"Please answer the following questions about your experience with this article.

Use the scale from 1 to 7 for each statement, where:
1 = Strongly disagree and 7 = Strongly agree."

## Survey Items

All items use a 1–7 Likert scale.

### 1. Cognitive Load (2 items)

#### Item 1: Mental Effort
- **Field name:** `load_mental_effort`
- **Displayed text:** "How mentally demanding was this task?"
- **Scale labels:** 1 = Not at all demanding, 7 = Extremely demanding

#### Item 2: Task Difficulty
- **Field name:** `load_task_difficulty`
- **Displayed text:** "How difficult was it to understand the content of this article?"
- **Scale labels:** 1 = Very easy, 7 = Very difficult

### 2. AI Experience (4 mandatory + 1 optional)

#### Item 1: AI Help Understanding
- **Field name:** `ai_help_understanding`
- **Displayed text:** "The AI-generated summary helped me understand the article."
- **Required:** Yes

#### Item 2: AI Help Memory
- **Field name:** `ai_help_memory`
- **Displayed text:** "The AI-generated summary helped me remember the content."
- **Required:** Yes

#### Item 3: AI Made Task Easier
- **Field name:** `ai_made_task_easier`
- **Displayed text:** "The AI assistance made the task easier and more efficient."
- **Required:** Yes

#### Item 4: AI Satisfaction
- **Field name:** `ai_satisfaction`
- **Displayed text:** "I am satisfied with the AI assistance provided for this article."
- **Required:** Yes

#### Item 5: AI Preference (Optional)
- **Field name:** `ai_better_than_no_ai`
- **Displayed text:** "I prefer completing this kind of task with AI support rather than without it."
- **Required:** No (marked as optional)

### 3. Overall MCQ Confidence (1 item)

#### Item: MCQ Confidence
- **Field name:** `mcq_overall_confidence`
- **Displayed text:** "Overall, how confident are you in your answers to the multiple-choice questions for this article?"
- **Scale labels:** 1 = Not confident at all, 7 = Extremely confident
- **Required:** Yes

## Data Storage

All ratings are saved to the participant's log file (`{participant_id}_log.csv`) under the phase **`post_article_ratings`**.

### Data Fields Saved

For each rating screen, the following data is stored:

1. **Participant Information:**
   - `participant_id` (from session)
   - `timestamp` (when ratings were submitted)

2. **Article Information:**
   - `article_num` (0, 1, or 2)
   - `article_key` ("uhi", "crispr", or "semiconductors")
   - `timing` ("synchronous", "pre_reading", or "post_reading")

3. **Rating Values:**
   - `load_mental_effort` (1-7)
   - `load_task_difficulty` (1-7)
   - `ai_help_understanding` (1-7)
   - `ai_help_memory` (1-7)
   - `ai_made_task_easier` (1-7)
   - `ai_satisfaction` (1-7)
   - `ai_better_than_no_ai` (1-7 or NULL if not answered)
   - `mcq_overall_confidence` (1-7)

### CSV Structure

Each row in the log file will have:
- `timestamp`: ISO format timestamp
- `phase`: "post_article_ratings"
- All the fields listed above

## Flow Integration

### Current Experiment Flow

1. Language Selection
2. Login/Demographics
3. Consent
4. Prior Knowledge Assessment
5. AI Trust Assessment
6. **Article 1:**
   - Reading Phase
   - Break (5 minutes)
   - Test Phase (Free Recall + MCQ)
   - **Post-Article Ratings** ← NEW
   - Break (1 minute)
7. **Article 2:**
   - Reading Phase
   - Break (5 minutes)
   - Test Phase (Free Recall + MCQ)
   - **Post-Article Ratings** ← NEW
   - Break (1 minute)
8. **Article 3:**
   - Reading Phase
   - Break (5 minutes)
   - Test Phase (Free Recall + MCQ)
   - **Post-Article Ratings** ← NEW
9. Manipulation Check
10. Debrief

## Technical Implementation

### Routes

- **Display:** `/post_article_ratings/<int:article_num>`
- **Submit:** `/submit_post_article_ratings` (POST)

### Template

- **File:** `templates/post_article_ratings.html`
- **Features:**
  - Responsive design
  - Form validation (all required fields must be answered)
  - Visual feedback for missing fields
  - Bilingual support (English/Chinese)

### Data Validation

- All required fields (7 items) must be answered before submission
- Optional field (`ai_better_than_no_ai`) can be left blank
- Values must be integers between 1 and 7

## Analysis Considerations

### Key Metrics to Analyze

1. **Cognitive Load:**
   - Compare mental effort across articles
   - Compare task difficulty across articles
   - Relationship with performance (recall, MCQ accuracy)

2. **AI Experience:**
   - Average ratings across all AI experience items
   - Comparison across timing conditions (synchronous, pre_reading, post_reading)
   - Comparison across summary structures (integrated, segmented)
   - Correlation with actual performance

3. **MCQ Confidence:**
   - Relationship between confidence and actual accuracy
   - Calibration analysis (overconfidence vs. underconfidence)
   - Comparison across articles

### Potential Research Questions

- Do participants rate AI as more helpful in certain conditions?
- Is there a relationship between AI satisfaction and performance?
- How well-calibrated are participants' confidence ratings?
- Does cognitive load vary by article or condition?

## Notes

- The ratings screen appears **immediately after MCQ completion** (no break in between)
- For articles 1 and 2, after ratings → break → next article
- For article 3, after ratings → manipulation check (no break)
- All ratings are article-specific, allowing for within-subject comparisons
- The optional question allows participants to express preference without forcing a response

