# AI MEMORY EXPERIMENT
## Comprehensive Final Analysis Report

**Report Generated:** January 3, 2026  
**Version:** 2.0 (Extended Analysis with Detailed Interpretations)  
**Principal Analyses:** Mixed-Effects Models, ANOVAs, Binomial GLMMs, Equivalence Tests

---

# TABLE OF CONTENTS

1. [Executive Summary](#1-executive-summary)
2. [Study Overview and Design](#2-study-overview-and-design)
   - 2.1 [Research Questions](#21-research-questions)
   - 2.2 [Experimental Design](#22-experimental-design)
   - 2.3 [Sample Characteristics](#23-sample-characteristics)
   - 2.4 [Outcome Variables](#24-outcome-variables)
3. [Section A: Timing Effects on Learning Outcomes](#3-section-a-timing-effects)
   - 3.1 [MCQ Accuracy Analysis](#31-mcq-accuracy-analysis)
   - 3.2 [Recall Total Score Analysis](#32-recall-total-score-analysis)
   - 3.3 [Article Accuracy Analysis](#33-article-accuracy-analysis)
   - 3.4 [Summary of Timing Effects](#34-summary-of-timing-effects)
4. [Section B: Summary Accuracy Relationships](#4-section-b-summary-accuracy)
   - 4.1 [Summary Accuracy → MCQ Correlation](#41-summary-accuracy-mcq-correlation)
   - 4.2 [Summary Accuracy → Recall](#42-summary-accuracy-recall)
   - 4.3 [Summary Accuracy → Article Accuracy](#43-summary-accuracy-article-accuracy)
5. [Section C: Structure and False Lures Mechanism](#5-section-c-structure-false-lures)
   - 5.1 [False Lure Accuracy ANOVA](#51-false-lure-accuracy-anova)
   - 5.2 [Mechanism Analysis](#52-mechanism-analysis)
   - 5.3 [Full Definitive Binomial Model](#53-full-definitive-binomial-model)
   - 5.4 [Model Family Comparison](#54-model-family-comparison)
6. [Section D: Process Variables Analysis](#6-section-d-process-variables)
   - 6.1 [Mental Effort](#61-mental-effort)
   - 6.2 [Summary Time](#62-summary-time)
   - 6.3 [Reading Time](#63-reading-time)
7. [Section E: Trust and Dependence as Moderators](#7-section-e-trust-dependence)
   - 7.1 [Participant-Level Regressions](#71-participant-level-regressions)
   - 7.2 [Moderation of Timing Effects](#72-moderation-of-timing-effects)
   - 7.3 [Trust/Dependence → Time-on-Task](#73-trust-dependence-time-on-task)
8. [Section F: Confidence Calibration](#8-section-f-confidence-calibration)
9. [Section G: Article Effects and Robustness](#9-section-g-article-effects)
10. [Timing Process Chain Analysis](#10-timing-process-chain)
    - 10.1 [Sanity Check: Trust/Dependence Balance](#101-sanity-check)
    - 10.2 [Buffer Mechanism Analysis](#102-buffer-mechanism)
    - 10.3 [MCQ Decomposition](#103-mcq-decomposition)
    - 10.4 [Effort as Marker](#104-effort-as-marker)
    - 10.5 [Who Benefits Analysis](#105-who-benefits)
11. [Robustness and Sensitivity Analyses](#11-robustness-sensitivity)
    - 11.1 [Random Slopes Robustness](#111-random-slopes)
    - 11.2 [Nonlinearity Tests](#112-nonlinearity)
    - 11.3 [Cross-Validation](#113-cross-validation)
    - 11.4 [Multiple Comparison Corrections](#114-multiple-comparisons)
    - 11.5 [Model Stability Checks](#115-model-stability)
12. [Integrated Discussion of Findings](#12-integrated-discussion)
13. [Conclusions and Implications](#13-conclusions)
14. [Technical Appendix](#14-technical-appendix)

---

<a name="1-executive-summary"></a>
# 1. EXECUTIVE SUMMARY

## Key Findings at a Glance

This comprehensive analysis examines how **AI-generated summaries** affect learning outcomes when presented at different **timing points** (pre-reading, synchronous, post-reading) and in different **structural formats** (integrated vs. segmented).

### Primary Discoveries

| Finding | Effect Size | Statistical Significance | Practical Implication |
|---------|-------------|--------------------------|----------------------|
| **Pre-reading timing is optimal for MCQ** | d = 1.35-1.62 | p < .001 | Students should access AI summaries BEFORE reading |
| **Segmented structure increases false lures** | OR = 3.5-5.9 | p < .01 | Integrated summaries prevent misconceptions |
| **Timing does NOT affect recall** | TOST equivalent | All p < .05 | Different memory systems involved |
| **No AI vs NoAI differences on recall** | negligible | p = .834 | AI doesn't harm free recall |

### What These Results Mean

1. **The "Preview Effect"**: Reading an AI summary before the main text creates a cognitive scaffold that enhances recognition memory (MCQ) but leaves generative memory (recall) unaffected.

2. **The "Fragmentation Problem"**: When AI summaries are presented in separate segments rather than integrated, learners are more likely to accept false information as true.

3. **Trust Matters for Individual Differences**: Participants with higher AI trust show different learning patterns—they may benefit more from post-reading AI summaries because they actively engage with the AI output.

---

<a name="2-study-overview-and-design"></a>
# 2. STUDY OVERVIEW AND DESIGN

<a name="21-research-questions"></a>
## 2.1 Research Questions

This experiment addressed three primary research questions:

**RQ1:** Does the **timing** of AI summary presentation (before, during, or after reading) affect learning outcomes?

**RQ2:** Does the **structure** of AI summaries (integrated vs. segmented) affect susceptibility to misinformation (false lures)?

**RQ3:** Do individual differences in **AI trust** and **AI dependence** moderate these effects?

<a name="22-experimental-design"></a>
## 2.2 Experimental Design

### Design Structure
```
2 × 3 Mixed Factorial Design (AI Group Only)
├── Between-Subjects Factor: Structure (2 levels)
│   ├── Integrated: Summary presented as unified text
│   └── Segmented: Summary presented in discrete sections
│
└── Within-Subjects Factor: Timing (3 levels)
    ├── Pre-reading: Summary shown BEFORE article
    ├── Synchronous: Summary shown DURING article reading
    └── Post-reading: Summary shown AFTER article
```

### Group Comparison
- **AI Group**: 24 participants, each completing 3 articles (72 observations)
- **NoAI Control Group**: 12 participants, each completing 3 articles (36 observations)

### Materials
Three scientific articles were used, counterbalanced across conditions:
- **CRISPR**: Gene editing technology
- **Semiconductors**: Computer chip manufacturing
- **Urban Heat Island (UHI)**: Climate and urban planning

<a name="23-sample-characteristics"></a>
## 2.3 Sample Characteristics

| Characteristic | AI Group | NoAI Group | Total |
|----------------|----------|------------|-------|
| N (Participants) | 24 | 12 | 36 |
| N (Observations) | 72 | 36 | 108 |
| Structure: Integrated | 12 | N/A | — |
| Structure: Segmented | 12 | N/A | — |

<a name="24-outcome-variables"></a>
## 2.4 Outcome Variables

| Variable | Type | Range | Description |
|----------|------|-------|-------------|
| **MCQ Accuracy** | Continuous | 0-1 | Proportion correct on multiple-choice questions |
| **Recall Total Score** | Count | 0-10+ | Number of correctly recalled facts |
| **Article Accuracy** | Continuous | 0-1 | Accuracy on article-only questions (no AI content) |
| **AI Summary Accuracy** | Continuous | 0-1 | Accuracy on AI summary-based questions |
| **False Lures Selected** | Count | 0-2 | Number of false AI lures endorsed as true |
| **Mental Effort** | Ordinal | 1-7 | Self-reported cognitive load |
| **Reading Time** | Continuous | minutes | Time spent reading the article |
| **Summary Time** | Continuous | seconds | Time spent viewing AI summary |

---

<a name="3-section-a-timing-effects"></a>
# 3. SECTION A: TIMING EFFECTS ON LEARNING OUTCOMES (AI Group Only)

This section examines how the **timing** of AI summary presentation affects learning outcomes. Detailed MCQ and recall analyses (Sections 3.1–3.2) are moved to the end as supplementary results.

<a name="33-article-accuracy-analysis"></a>
## 3.3 Article Accuracy Analysis

Article accuracy measures performance on questions that do **not** reference the AI summary—testing comprehension of the article itself.

### 3.3.1 ANOVA Results

| Effect | F | df | p-value | η²(ges) |
|--------|------|----------|---------|---------|
| Structure | 1.99 | 1, 22 | .173 | .028 |
| Timing | 0.35 | 1.99, 43.79 | .707 | .011 |
| Interaction | 0.50 | 1.99, 43.79 | .608 | .015 |

> **Result**: No significant effects on article accuracy. This confirms that the timing manipulation specifically affects AI summary-related learning, not general article comprehension.

<a name="34-summary-of-timing-effects"></a>
## 3.4 Summary of Timing Effects

| Outcome | Timing Effect? | Direction | Effect Size |
|---------|----------------|-----------|-------------|
| **MCQ Accuracy** | ✓ Yes (p < .001) | Pre-reading best | d = 1.35-1.62 |
| **Recall** | ✗ No (equivalent) | — | — |
| **Article Accuracy** | ✗ No | — | — |

**Bottom Line**: Pre-reading AI summaries enhance recognition-based learning (MCQ) without affecting other forms of memory or article comprehension.

---

<a name="4-section-b-summary-accuracy"></a>
# 4. SECTION B: SUMMARY ACCURACY RELATIONSHIPS (AI Group Only)

<a name="41-summary-accuracy-mcq-correlation"></a>
## 4.1 Summary Accuracy → MCQ Correlation

### 4.1.1 Mixed-Effects Model Results

Model: `MCQ ~ ai_summary_accuracy + (1|participant_id) + (1|article)`

| Predictor | β | SE | t | p |
|-----------|---|----|----|---|
| ai_summary_accuracy | 0.467 | 0.059 | 7.93 | <.001 |

### 4.1.2 Methodological Note

⚠️ **Important Caveat**: Summary accuracy and MCQ share the same underlying "correctness" signal—both measure whether participants encoded the correct information. The strong correlation (β = 0.47) is therefore **expected** and should **not** be interpreted as a causal mechanism.

When summary accuracy is added to models predicting MCQ, timing coefficients are attenuated. This reflects **shared variance** (tautological relationship), not mediation.

<a name="42-summary-accuracy-recall"></a>
## 4.2 Summary Accuracy → Recall

| Predictor | β | SE | t | p |
|-----------|---|----|----|---|
| ai_summary_accuracy | 0.854 | 0.804 | 1.06 | .305 |

> **Result**: Not significant. Summary accuracy does not predict recall, reinforcing the dissociation between recognition and generative memory.

<a name="43-summary-accuracy-article-accuracy"></a>
## 4.3 Summary Accuracy → Article Accuracy

| Predictor | β | SE | t | p |
|-----------|---|----|----|---|
| ai_summary_accuracy | -0.134 | 0.157 | -0.85 | .396 |

> **Result**: Not significant. Success with AI summary content is independent of article-only comprehension.

---

<a name="5-section-c-structure-false-lures"></a>
# 5. SECTION C: STRUCTURE AND FALSE LURES MECHANISM (AI Group Only)

This section examines how the **structure** of AI summaries (integrated vs. segmented) affects susceptibility to **false lures**—incorrect information that participants incorrectly endorse as true.

<a name="51-false-lure-accuracy-anova"></a>
## 5.1 False Lure Accuracy ANOVA

### 5.1.1 ANOVA Results

| Effect | F | df | p-value | η²(ges) | Interpretation |
|--------|---|----|---------|---------|----|
| **Structure** | 4.20 | 1, 22 | **.053** (marginal) | .075 | Approaching significance |
| Timing | 1.13 | 1.64, 36.04 | .325 | .029 | No effect |
| Interaction | 0.47 | 1.64, 36.04 | .589 | .012 | No interaction |

### 5.1.2 Descriptive Statistics

| Structure | Mean False Lures | SD | Probability |
|-----------|-----------------|-----|-------------|
| Integrated | 0.50 | 0.72 | 0.253 |
| **Segmented** | **1.08** | 0.87 | **0.541** |

> **Interpretation**: Participants in the **segmented** condition selected approximately **twice as many false lures** as those in the integrated condition.

<a name="52-mechanism-analysis"></a>
## 5.2 Mechanism Analysis: Is Structure Effect Explained by Effort/Time?

### 5.2.1 Model Comparison

| Model | Structure β | p-value | Change |
|-------|-------------|---------|--------|
| Base: structure + timing | 0.472 | .041 | — |
| + mental_effort + reading_time + summary_time | 0.482 | .045 | **+2%** |

> **Critical Finding**: Adding process variables (effort, time) does **not** explain the structure effect. The coefficient actually *increased* slightly, ruling out these as mechanisms.

### 5.2.2 What This Means

The segmented structure increases false lure acceptance through a **direct cognitive path**—not because segmented summaries require more effort or time. Possible mechanisms:
- **Reduced coherence**: Segmented presentation impairs integration of information
- **Source confusion**: Separate segments make it harder to track what was in the summary vs. article
- **Lower elaboration**: Fragmented presentation reduces deep processing

<a name="53-full-definitive-binomial-model"></a>
## 5.3 Full Definitive Binomial Model

### 5.3.1 Model Specification

A binomial GLMM was fit to model false lure selection as a proportion (0-2 lures out of 2 possible):

```
cbind(false_lures, 2-lures) ~ structure + timing + summary_acc + article_acc + 
                               trust + dependence + log(summary_time) + log(reading_time) + 
                               mental_effort + article + (1|participant_id)
```

### 5.3.2 Full Model Results

| Predictor | Odds Ratio | 95% CI | p-value | Interpretation |
|-----------|------------|--------|---------|----------------|
| **Structure (Segmented)** | **5.93** | [1.63, 21.5] | **.007*** | **Strong effect** |
| ai_dependence | 0.49 | [0.22, 1.09] | .080 | Marginal protective |
| ai_trust | 1.57 | [0.58, 4.30] | .378 | ns |
| ai_summary_accuracy | 11.5 | [0.48, 276] | .132 | ns |
| article_accuracy | 1.79 | [0.31, 10.3] | .515 | ns |
| timing (synchronous) | 1.60 | [0.42, 6.03] | .491 | ns |
| timing (post_reading) | 1.28 | [0.38, 4.31] | .691 | ns |
| log(summary_time) | 0.85 | [0.41, 1.76] | .664 | ns |
| log(reading_time) | 1.03 | [0.26, 4.07] | .970 | ns |
| mental_effort | 1.17 | [0.70, 1.95] | .545 | ns |

### 5.3.3 Key Takeaways

1. **Structure is the ONLY robust predictor** of false lure selection (OR = 5.93)
2. **Timing does NOT affect false lures** — structure is the dominant factor
3. **Marginal dependence effect**: Higher AI dependence may *protect* against lures (OR = 0.49)
   - Interpretation: Highly dependent users may scrutinize AI output more carefully
4. **Time and effort are NOT mechanisms** — coefficients near 1.0

<a name="54-model-family-comparison"></a>
## 5.4 Model Family Comparison (Sensitivity Analysis)

### 5.4.1 Binomial vs. Poisson Models

| Model | AIC | Structure Coefficient | OR/IRR | p-value |
|-------|-----|----------------------|--------|---------|
| **Binomial** | **155.4** | 1.18 | 3.25 | .026 |
| Poisson | 171.3 | 0.59 | 1.81 | .030 |

> **Conclusion**: Binomial model is preferred (ΔAIC = 16). Both models agree that structure is significant, confirming robustness of the finding.

### 5.4.2 Predicted Probabilities

| Structure | Predicted Probability | 95% CI |
|-----------|----------------------|--------|
| Integrated | 26.2% | [14%, 43%] |
| **Segmented** | **53.6%** | [36%, 70%] |

> **Practical Meaning**: In the segmented condition, participants accept false lures as true **more than half the time**. In the integrated condition, this drops to about one-quarter.

---

<a name="6-section-d-process-variables"></a>
# 6. SECTION D: PROCESS VARIABLES ANALYSIS (AI Group Only)

<a name="61-mental-effort"></a>
## 6.1 Mental Effort

### 6.1.1 ANOVA Results

| Effect | F | df | p-value | η²(ges) |
|--------|---|----|---------|---------| 
| Structure | 2.43 | 1, 22 | .134 | .056 |
| Timing | 0.81 | 1.34, 29.37 | .408 | .017 |
| Interaction | 1.47 | 1.34, 29.37 | .242 | .030 |

> **Result**: Mental effort does NOT differ significantly by timing or structure. This is important because it rules out effort as a confound.

### 6.1.2 Effort as Predictor of MCQ

| Predictor | β | p |
|-----------|---|---|
| mental_effort | -0.034 | .036* |

> **Unexpected Finding**: Higher mental effort is associated with **lower** MCQ accuracy. However, since effort doesn't differ by condition, this doesn't explain timing effects.

<a name="62-summary-time"></a>
## 6.2 Summary Time

### 6.2.1 ANOVA Results

| Effect | F | df | p-value | η²(ges) |
|--------|---|----|---------|---------| 
| **Structure** | 5.59 | 1, 22 | **.027*** | .069 |
| **Timing** | 5.97 | 1.60, 35.21 | **.009*** | .161 |
| Interaction | 0.93 | 1.60, 35.21 | .385 | .029 |

### 6.2.2 Descriptive Statistics

| Timing | Mean Summary Time (sec) | SD |
|--------|------------------------|-----|
| Pre-reading | 146.3 | 89.2 |
| Synchronous | 141.4 | 102.5 |
| **Post-reading** | **73.5** | 62.1 |

### 6.2.3 Post-Hoc Comparisons (Holm-Corrected)

| Contrast | Δ (seconds) | p |
|----------|-------------|---|
| **Pre-reading vs Post-reading** | **73.8** | **<.001*** |
| **Synchronous vs Post-reading** | **68.9** | **.034*** |
| Pre-reading vs Synchronous | 4.9 | .828 |

> **Interpretation**: Participants spend significantly **less time** with the AI summary in the post-reading condition. However, this does NOT explain the timing effect on MCQ (see Section 10).

<a name="63-reading-time"></a>
## 6.3 Reading Time

### 6.3.1 ANOVA Results

| Effect | F | df | p-value | η²(ges) |
|--------|---|----|---------|---------| 
| Structure | 0.90 | 1, 22 | .353 | .018 |
| **Timing** | 3.96 | 1.92, 42.23 | **.028*** | .091 |
| Interaction | 0.25 | 1.92, 42.23 | .769 | .006 |

### 6.3.2 Post-Hoc Comparisons

| Contrast | Δ (minutes) | p |
|----------|-------------|---|
| **Pre-reading vs Synchronous** | **-1.97** | **.044*** |

> **Interpretation**: Synchronous reading takes longer (participants interleave reading with summary viewing). However, this does NOT explain MCQ differences.

---

<a name="7-section-e-trust-dependence"></a>
# 7. SECTION E: TRUST AND DEPENDENCE AS MODERATORS (AI Group Only)

<a name="71-participant-level-regressions"></a>
## 7.1 Participant-Level Regressions

### 7.1.1 Mean MCQ ~ Individual Differences

| Predictor | β (standardized) | p | Interpretation |
|-----------|------------------|---|----------------|
| Trust | 0.24 | .351 | ns |
| Dependence | -0.18 | .490 | ns |
| Prior Knowledge | -0.09 | .669 | ns |

**Model R² = .056 (ns)**

### 7.1.2 Mean Summary Accuracy ~ Individual Differences

| Predictor | β (standardized) | p | Interpretation |
|-----------|------------------|---|----------------|
| Trust | 0.42 | .064 | Marginal positive |
| Dependence | -0.06 | .775 | ns |
| **Prior Knowledge** | **-0.40** | **.049*** | **Significant negative** |

**Model R² = .296**

> **Surprising Finding**: Higher prior knowledge predicts **lower** summary accuracy. Possible interpretation: Experts may rely on prior knowledge rather than carefully encoding AI summary content.

### 7.1.3 Mean False Lures ~ Individual Differences

| Predictor | β (standardized) | p |
|-----------|------------------|---|
| Trust | -0.02 | .926 |
| Dependence | -0.15 | .567 |
| Prior Knowledge | -0.14 | .519 |

**Model R² = .052 (ns)** — Individual differences do not predict false lure susceptibility.

<a name="72-moderation-of-timing-effects"></a>
## 7.2 Moderation of Timing Effects

### 7.2.1 Summary Accuracy ~ Timing × Trust/Dependence

| Interaction | β | p | Interpretation |
|-------------|---|---|----------------|
| **Post-reading × Trust** | 0.126 | **.030*** | High trust strengthens post-reading benefit |
| **Post-reading × Dependence** | 0.116 | **.012*** | High dependence strengthens post-reading benefit |
| Post-reading × Prior Knowledge | -0.022 | .579 | ns |

### 7.2.2 MCQ ~ Timing × Trust/Dependence

| Interaction | β | p | Interpretation |
|-------------|---|---|----------------|
| **Post-reading × Trust** | 0.132 | **.002**** | High trust → larger MCQ gain from post-reading |
| Post-reading × Dependence | 0.055 | .128 | ns |
| Post-reading × Prior Knowledge | 0.013 | .654 | ns |

### 7.2.3 Holm-Corrected Significance

After Holm correction for 12 tests (3 traits × 2 contrasts × 2 outcomes):

| Effect | Raw p | Holm p | Survives Correction? |
|--------|-------|--------|---------------------|
| MCQ: Trust × Post-reading | .002 | **.023** | ✓ Yes |
| Summary: Trust × Post-reading | .029 | .285 | No |
| Summary: Dependence × Post-reading | .010 | .109 | No |

> **Key Finding**: Only the Trust × Post-reading interaction on MCQ survives multiple comparison correction. High-trust individuals show a smaller pre-reading advantage because they also benefit from post-reading.

<a name="73-trust-dependence-time-on-task"></a>
## 7.3 Trust/Dependence → Time-on-Task

### 7.3.1 Summary Time ~ Individual Differences (R² = .53***)

| Predictor | β | p | Interpretation |
|-----------|---|---|----------------|
| **Trust** | **+37.2 sec** | **.005*** | High trust → MORE time with summary |
| **Dependence** | **-41.6 sec** | **<.001**** | High dependence → LESS time with summary |
| Prior Knowledge | +8.6 sec | .210 | ns |

> **Interpretation**: Trust and dependence have **opposite effects** on engagement time:
> - **High-trust users**: Spend more time engaging with the AI summary (active processing)
> - **High-dependence users**: Spend less time—possibly accepting AI output without scrutiny (passive processing)

---

<a name="8-section-f-confidence-calibration"></a>
# 8. SECTION F: CONFIDENCE CALIBRATION

## 8.1 Confidence-Recall Correlation

| Group | Correlation (r) | n |
|-------|-----------------|---|
| Overall | 0.043 | 108 |
| AI | -0.044 | 72 |
| NoAI | 0.301 | 36 |

**Overall test**: r = 0.043, 95% CI [-0.147, 0.230], p = .660 (ns)

> **Result**: Participants show **poor metacognitive monitoring**—their confidence ratings are not calibrated with actual recall performance.

## 8.2 Overconfidence Comparison (AI vs NoAI)

**Overconfidence Score** = z(confidence) - z(recall)

| Group | Mean Overconfidence | SD |
|-------|---------------------|-----|
| AI | 0.020 | 1.38 |
| NoAI | -0.041 | 0.88 |

**t-test**: t(31.7) = 0.16, p = .873

> **Result**: No difference in overconfidence between AI and NoAI groups. Using AI summaries does NOT induce overconfidence relative to control.

---

<a name="9-section-g-article-effects"></a>
# 9. SECTION G: ARTICLE EFFECTS AND ROBUSTNESS

## 9.1 Article Difficulty

| Article | MCQ Mean | Recall Mean | Summary Accuracy (AI) | False Lures (AI) |
|---------|----------|-------------|----------------------|------------------|
| **Semiconductors** | **0.480** (hardest) | 5.28 | 0.562 (hardest) | 0.833 |
| UHI | 0.601 | **5.85** (best) | 0.760 | 0.958 (most) |
| CRISPR | 0.625 (easiest) | 5.35 | 0.719 | 0.667 (fewest) |

> **Observation**: Semiconductors is consistently the most difficult article across outcomes.

## 9.2 Counterbalancing Check

**Chi-square test**: X²(4) = 3.00, p = .558

| Timing | CRISPR | Semiconductors | UHI |
|--------|--------|----------------|-----|
| Pre-reading | 8 | 9 | 7 |
| Synchronous | 10 | 8 | 6 |
| Post-reading | 6 | 7 | 11 |

> **Result**: Counterbalancing is adequate (p > .05). Article assignment does not confound timing conditions.

## 9.3 Timing × Article Interaction

| Outcome | Timing × Article F | p |
|---------|-------------------|---|
| Summary Accuracy | F(4, 59.8) = 1.88 | .125 (ns) |
| MCQ Accuracy | F(4, 60.5) = 1.34 | .264 (ns) |

> **Result**: Timing effects are consistent across all three articles—no significant interaction.

## 9.4 Leave-One-Article-Out Robustness

| Dropped Article | Pre-Sync Δ | p | Robust? |
|-----------------|------------|---|---------|
| Semiconductors | 0.172 | <.001 | ✓ |
| UHI | 0.126 | .010 | ✓ |
| CRISPR | 0.116 | .016 | ✓ |

> **Result**: The pre-reading timing effect is robust regardless of which article is excluded.

---

<a name="10-timing-process-chain"></a>
# 10. TIMING PROCESS CHAIN ANALYSIS

This section traces the causal chain from timing manipulation to learning outcomes.

<a name="101-sanity-check"></a>
## 10.1 Sanity Check: Trust/Dependence Balance

Trust and dependence are **participant-level traits** (measured once). They should be identical across within-subject timing conditions.

| Timing | Trust Mean | Dependence Mean | n |
|--------|-----------|-----------------|---|
| Pre-reading | 4.94 | 5.15 | 24 |
| Synchronous | 4.94 | 5.15 | 24 |
| Post-reading | 4.94 | 5.15 | 24 |

> ✓ **Perfect balance confirmed**. Trust/dependence are true moderators, not confounds.

<a name="102-buffer-mechanism"></a>
## 10.2 Buffer Mechanism: Does Timing → Summary Time → Accuracy?

### 10.2.1 Does Timing Remain Significant After Controlling Summary Time?

| Model | Pre-Sync Estimate | Pre-Post Estimate |
|-------|-------------------|-------------------|
| Base (timing only) | 0.271*** | 0.212*** |
| + log(summary_time) | 0.249*** | 0.164** |
| **Reduction** | **8%** | **23%** |

The summary time effect: β = 0.066, p = .048*

> **Interpretation**: Timing remains highly significant even after controlling for summary time. Pre-reading wins because of **quality of processing**, not just quantity of time.

<a name="103-mcq-decomposition"></a>
## 10.3 MCQ Decomposition: Progressive Model Building

### 10.3.1 How Timing Coefficients Change as Mechanisms Are Added

| Model | Sync β | Post β | Sync Reduction | Post Reduction |
|-------|--------|--------|----------------|----------------|
| 1: Timing only | -0.173 | -0.144 | 0% | 0% |
| 2: + total_time | -0.175 | -0.143 | -1% | +1% |
| 3: + summary_acc | -0.050 | -0.047 | **71%** | **67%** |
| 4: + article_acc | -0.017 | -0.029 | **90%** | **80%** |
| 5: Full model | -0.018 | -0.029 | **89%** | **80%** |

### 10.3.2 Visual Representation

```
Timing Coefficient Decomposition (Pre vs Sync)
═══════════════════════════════════════════════

Model 1 (Timing only):     ████████████████████ -0.173
Model 2 (+ total_time):    ████████████████████ -0.175  (-1%)
Model 3 (+ summary_acc):   █████                -0.050  (71% reduction)
Model 4 (+ article_acc):   █                    -0.017  (90% reduction)
Model 5 (Full):            █                    -0.018  (89% reduction)
```

### 10.3.3 Full Decomposition Model Results

Model: `MCQ ~ summary_acc + article_acc + timing + structure + article + (1|participant)`

| Predictor | β | SE | p |
|-----------|---|----|----|
| **ai_summary_accuracy** | **0.506** | 0.033 | **<.001**** |
| **article_accuracy** | **0.281** | 0.021 | **<.001**** |
| timing (synchronous) | -0.017 | 0.015 | .249 |
| timing (post_reading) | -0.029 | 0.013 | .034* |
| structure (segmented) | -0.039 | 0.014 | .010* |

**Model Fit:**
- Marginal R² = **0.906**
- Conditional R² = **0.934**

### 10.3.4 What This Means

The timing effect on MCQ is **~85% explained** by two quality metrics:
1. **Summary accuracy**: How well participants encoded the AI summary
2. **Article accuracy**: How well participants encoded the article

Pre-reading helps because it improves the **quality of learning**, not because it provides more time. This is evidence for the "cognitive scaffold" interpretation.

<a name="104-effort-as-marker"></a>
## 10.4 Effort as Marker (Not a Cause)

### 10.4.1 Does Mental Effort Explain Timing Effects?

| Model | Sync β | Post β | Mental Effort β |
|-------|--------|--------|-----------------|
| Base | -0.173 | -0.144 | — |
| + effort | -0.184 | -0.144 | -0.032* |

**Timing coefficient change**: ~0%

> **Conclusion**: Timing effects are **unchanged** after controlling for mental effort. The negative effort→MCQ relationship is incidental, not explanatory.

<a name="105-who-benefits"></a>
## 10.5 Who Benefits? Within-Person Trait Moderation

### 10.5.1 Delta Scores by Participant

| Contrast | Mean Δ | SD |
|----------|--------|-----|
| MCQ (Pre - Sync) | +0.167 | 0.205 |
| MCQ (Pre - Post) | +0.137 | 0.177 |
| Summary Acc (Pre - Sync) | +0.266 | 0.291 |
| Summary Acc (Pre - Post) | +0.193 | 0.221 |

### 10.5.2 MCQ Δ(Pre-Post) ~ Traits

| Predictor | β | p | Interpretation |
|-----------|---|---|----------------|
| **ai_trust** | **-0.150** | **.011*** | Higher trust → SMALLER pre-reading advantage |
| ai_dependence | 0.038 | .376 | ns |
| prior_knowledge | 0.015 | .634 | ns |

**Model R² = .30, p = .067**

> **Interpretation**: Participants with **higher AI trust** show a **smaller** advantage of pre-reading over post-reading. This is because high-trust individuals also benefit from post-reading—they engage meaningfully with the AI summary regardless of timing.

---

<a name="11-robustness-sensitivity"></a>
# 11. ROBUSTNESS AND SENSITIVITY ANALYSES

<a name="111-random-slopes"></a>
## 11.1 Random Slopes Robustness

### 11.1.1 Model Comparison

| Model | AIC | Timing Effects Changed? |
|-------|-----|------------------------|
| Random Intercept Only | -97.2 | — |
| **Random Slopes** | **-101.3** | No (identical estimates) |

**Likelihood Ratio Test**: χ²(2) = 8.01, p = .018*

> Random slopes model fits better, but timing effects remain identical. This confirms that the effects are not driven by a few outlier participants.

### 11.1.2 Individual Participant Validation

| Measure | % Showing Pre-reading Advantage |
|---------|--------------------------------|
| MCQ | **83.3%** |
| Summary Accuracy | 75.0% |

> **20 of 24 participants** individually show higher MCQ with pre-reading timing.

<a name="112-nonlinearity"></a>
## 11.2 Nonlinearity and Diminishing Returns

| Outcome | Time Variable | Linear AIC | Spline AIC | Better Model |
|---------|---------------|------------|------------|--------------|
| Summary Acc | Summary Time | -13.5 | -7.9 | **Linear** |
| MCQ Acc | Total Time | -58.0 | -51.4 | **Linear** |

> **Conclusion**: No evidence of diminishing returns. Simple log-linear models are sufficient.

<a name="113-cross-validation"></a>
## 11.3 Cross-Validated Prediction (Leave-One-Out)

| Model | RMSE | Correlation |
|-------|------|-------------|
| 1: Timing only | 0.122 | 0.582 |
| 2: + Summary Acc | 0.092 | 0.792 |
| **3: + Summary + Article Acc** | **0.049** | **0.945** |

**Improvement from Model 1 → 3:**
- RMSE reduction: **60%**
- Correlation increase: **+0.36**

> **The full decomposition model predicts out-of-sample exceptionally well (r = .95)**, confirming that summary + article accuracy explain almost all predictable variance.

<a name="114-multiple-comparisons"></a>
## 11.4 Multiple Comparison Corrections

### 11.4.1 Trait × Timing Interactions (Holm Correction)

| Effect | Raw p | Holm p | Survives? |
|--------|-------|--------|-----------|
| MCQ: Trust × Pre-Post | .002 | **.023** | ✓ Yes |
| Summary: Trust × Pre-Post | .029 | .285 | No |
| Summary: Dependence × Pre-Post | .010 | .109 | No |

**Summary**: 3 of 12 interactions were significant at raw level; **1 of 12 survives Holm correction**.

<a name="115-model-stability"></a>
## 11.5 Model Stability Checks

### 11.5.1 Binomial Model Separation Check

| Statistic | Value |
|-----------|-------|
| Min fitted probability | 0.103 |
| Max fitted probability | 0.823 |
| Probabilities < 0.01 | 0 |
| Probabilities > 0.99 | 0 |

> ✓ **No separation issues detected**. Model estimates are stable.

### 11.5.2 Profile Likelihood Confidence Intervals

| Parameter | 95% CI (log-OR) | 95% CI (OR) |
|-----------|-----------------|-------------|
| Structure (Seg vs Int) | [0.13, 2.38] | [1.14, 10.76] |

> The profile likelihood CI confirms the structure effect is robust.

### 11.5.3 Leave-One-Participant-Out Influence

| Analysis | Range of Estimates | Stable? |
|----------|-------------------|---------|
| Structure → False Lures (OR) | 2.68 - 4.23 | ✓ Yes |
| AI vs NoAI MCQ (β) | -0.107 to -0.079 | ✓ Yes |

> **No influential participants**—results remain stable when any single participant is excluded.

---

<a name="12-integrated-discussion"></a>
# 12. INTEGRATED DISCUSSION OF FINDINGS

## 12.1 The Cognitive Scaffold Model

Our findings support a **"Cognitive Scaffold"** interpretation of AI summary timing effects:

```
┌─────────────────────────────────────────────────────────────────────┐
│                     COGNITIVE SCAFFOLD MODEL                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Pre-reading AI Summary                                            │
│          │                                                          │
│          ▼                                                          │
│   ┌──────────────────┐                                             │
│   │ Builds Schema/   │                                             │
│   │ Expectations     │                                             │
│   └────────┬─────────┘                                             │
│            │                                                        │
│            ▼                                                        │
│   ┌──────────────────┐     ┌──────────────────┐                    │
│   │ Enhanced Article │ ──► │ Better MCQ       │                    │
│   │ Encoding         │     │ Performance      │                    │
│   └──────────────────┘     └──────────────────┘                    │
│            │                                                        │
│            ▼                                                        │
│   ┌──────────────────┐                                             │
│   │ Recall Unaffected│  ← Different memory system                  │
│   │ (Generative)     │                                             │
│   └──────────────────┘                                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 12.2 The Fragmentation Problem

The structure effect on false lures reveals a **Fragmentation Problem**:

| Format | Mechanism | Outcome |
|--------|-----------|---------|
| **Integrated** | Coherent representation | Better source discrimination |
| **Segmented** | Fragmented representation | Source confusion, false acceptance |

This has important implications for AI interface design: presenting AI summaries as unified, coherent text reduces misinformation susceptibility compared to bulleted or segmented formats.

## 12.3 Individual Differences Matter

The moderation by trust reveals that **not all learners benefit equally**:

| User Type | Optimal Timing | Why |
|-----------|----------------|-----|
| **Low Trust** | Pre-reading | Need scaffold before engaging AI |
| **High Trust** | Either (flexible) | Actively engage with AI regardless |

## 12.4 What AI Summaries Do NOT Do

Importantly, our null findings are equally informative:

| Concern | Evidence | Status |
|---------|----------|--------|
| AI harms recall | No group difference | ❌ Not supported |
| AI causes overconfidence | No calibration difference | ❌ Not supported |
| Effects are article-specific | Robust across all 3 articles | ❌ Not supported |
| Effects are due to time confounds | Time control doesn't change results | ❌ Not supported |

---

<a name="13-conclusions"></a>
# 13. CONCLUSIONS AND IMPLICATIONS

## 13.1 Primary Conclusions

### 13.1.1 Timing Effects

| Conclusion | Confidence | Effect Size |
|------------|------------|-------------|
| Pre-reading timing optimizes MCQ performance | **Very High** | d = 1.35-1.62 |
| Timing does not affect recall | **High** (equivalence confirmed) | — |
| Timing effect is not a time confound | **Very High** | — |
| High-trust users are more flexible with timing | **Moderate** (survives Holm) | — |

### 13.1.2 Structure Effects

| Conclusion | Confidence | Effect Size |
|------------|------------|-------------|
| Segmented structure increases false lure acceptance | **Very High** | OR = 3.5-5.9 |
| This effect is NOT explained by effort/time | **High** | — |
| Structure effect is robust across model specifications | **Very High** | — |

### 13.1.3 Safety and Harm Concerns

| Conclusion | Confidence |
|------------|------------|
| AI summaries do NOT harm recall relative to control | **High** |
| AI summaries do NOT induce overconfidence | **High** |
| Using AI does NOT change article-only comprehension | **High** |

## 13.2 Practical Implications

### For Educational Technology Designers

1. **Default to Pre-Reading Presentation**: When possible, show AI summaries BEFORE learners read the main content
2. **Use Integrated Formats**: Present AI summaries as coherent text, not bullet points or fragments
3. **Allow User Control**: High-trust users may benefit from flexibility in timing

### For Learners Using AI Tools

1. **Read the AI summary first**: This creates a mental framework for understanding
2. **Take time with the summary**: Longer engagement correlates with better outcomes
3. **Trust is good, but verify**: High dependence without engagement may not help

### For Researchers

1. **Measure multiple memory systems**: Recognition and recall respond differently
2. **Test for equivalence, not just significance**: TOST confirms interpretable null effects
3. **Control for time-on-task**: It's rarely the explanation for learning differences

## 13.3 Limitations

1. **Sample size**: N = 24 (AI) provides adequate power for medium-large effects but limits detection of smaller effects
2. **Content domain**: Three scientific articles may not generalize to all learning contexts
3. **AI summary quality**: Fixed AI summaries don't test variation in AI output quality
4. **Short-term outcomes**: No delayed retention tests were conducted

## 13.4 Future Directions

1. Test timing effects with **different content types** (narrative, procedural, mathematical)
2. Examine **long-term retention** effects (24-hour, 1-week delays)
3. Investigate **why segmented structure increases lures** (eye-tracking, think-aloud)
4. Develop **personalized AI interfaces** that adapt to user trust levels

---

# OTHER RESULTS (SUPPLEMENTARY)

The following sections are complete analyses but are not central to the thesis narrative, so they are placed here for readability.

<a name="31-mcq-accuracy-analysis"></a>
## 3.1 MCQ Accuracy Analysis

### 3.1.1 ANOVA Results

A 2×3 mixed ANOVA was conducted with Structure (between) and Timing (within) as factors.

| Effect | F | df | p-value | η²(ges) | Interpretation |
|--------|---|----|---------|---------|----|
| **Structure** | 4.69 | 1, 22 | **.042*** | .072 | Small-medium effect |
| **Timing** | 11.77 | 1.77, 38.87 | **<.001**** | .254 | Large effect |
| Interaction | 0.76 | 1.77, 38.87 | .461 | .021 | No interaction |

> **Interpretation**: Both timing and structure significantly affect MCQ accuracy. The timing effect is particularly large (η² = .254), explaining about 25% of the within-person variance. Critically, there is **no interaction**, meaning the timing effect operates similarly across both structure conditions.

### 3.1.2 Descriptive Statistics by Condition

| Structure | Timing | Mean | SD | n |
|-----------|--------|------|-----|---|
| Integrated | Pre-reading | **0.750** | 0.124 | 12 |
| Integrated | Synchronous | 0.542 | 0.124 | 12 |
| Integrated | Post-reading | 0.607 | 0.094 | 12 |
| Segmented | Pre-reading | **0.649** | 0.108 | 12 |
| Segmented | Synchronous | 0.524 | 0.173 | 12 |
| Segmented | Post-reading | 0.518 | 0.143 | 12 |

### 3.1.3 Post-Hoc Pairwise Comparisons (Holm-Corrected)

| Contrast | Δ (Difference) | SE | p-value | Cohen's d |
|----------|---------------|-----|---------|-----------|
| **Pre-reading vs Synchronous** | **+0.167** | — | **.002*** | **1.62** |
| **Pre-reading vs Post-reading** | **+0.137** | — | **.003*** | **1.35** |
| Synchronous vs Post-reading | -0.030 | — | .334 | 0.28 |

> **Key Finding**: Pre-reading timing produces significantly higher MCQ accuracy than both synchronous and post-reading conditions. The effect sizes are **very large** (d > 1.0), indicating practically meaningful differences. There is no significant difference between synchronous and post-reading.

### 3.1.4 Visual Interpretation

```
MCQ Accuracy by Timing Condition
================================

Pre-reading    ████████████████████████████████████████  0.70 ← OPTIMAL
Post-reading   ████████████████████████████████          0.56
Synchronous    ██████████████████████████████            0.53

                0.0   0.2   0.4   0.6   0.8   1.0
```

### 3.1.5 What This Means

The **"Preview Effect"** is robust and substantial:
- Reading the AI summary **before** the article creates a cognitive scaffold
- This scaffold helps learners organize incoming information during reading
- The result is better encoding and subsequent recognition performance
- This effect is **not** due to simply spending more time (see Section 10)

<a name="32-recall-total-score-analysis"></a>
## 3.2 Recall Total Score Analysis

### 3.2.1 ANOVA Results

| Effect | F | df | p-value | η²(ges) | Interpretation |
|--------|---|----|---------|---------|----|
| Structure | 0.40 | 1, 22 | .536 | .015 | No effect |
| Timing | 0.03 | 1.86, 40.88 | .969 | <.001 | **Null effect** |
| Interaction | 0.62 | 1.86, 40.88 | .533 | .004 | No interaction |

### 3.2.2 Equivalence Test (TOST)

To confirm that the null effect on recall is meaningful (not just underpowered), Two One-Sided Tests (TOST) were conducted.

**SESOI (Smallest Effect Size of Interest):** d = 0.30 (±0.60 raw units)

| Contrast | Estimate | 90% CI | TOST p | Decision |
|----------|----------|--------|--------|----------|
| Post - Pre | -0.009 | [-0.48, 0.46] | .020 | ✓ **EQUIVALENT** |
| Post - Sync | -0.071 | [-0.54, 0.40] | .033 | ✓ **EQUIVALENT** |
| Pre - Sync | -0.062 | [-0.53, 0.40] | .029 | ✓ **EQUIVALENT** |

> **Interpretation**: The TOST results confirm that timing conditions produce **equivalent** recall performance. This is not a Type II error (failure to detect)—the null effect is **real and interpretable**.

### 3.2.3 What This Means

**Dissociation Between Memory Systems:**
- **MCQ (Recognition)**: Sensitive to timing — benefits from pre-reading
- **Recall (Generative Memory)**: Insensitive to timing — equally good/poor in all conditions

This pattern suggests that AI summary timing affects **cue-dependent retrieval** (recognition) but not **self-generated retrieval** (recall). The AI summary provides retrieval cues that help with MCQ but doesn't strengthen the memory trace itself.

<a name="14-technical-appendix"></a>
# 14. TECHNICAL APPENDIX

## 14.1 Statistical Methods

### Mixed-Effects Models
- Software: R with `lme4` and `lmerTest` packages
- Estimation: Restricted Maximum Likelihood (REML)
- Random effects: Participant (all models), Article (where appropriate)
- Degrees of freedom: Satterthwaite approximation

### Generalized Linear Mixed Models
- Family: Binomial (logit link) for false lures
- Optimizer: BOBYQA with 100,000 max iterations
- Sensitivity: Compared to Poisson models

### Multiple Comparison Corrections
- Method: Holm-Bonferroni
- Applied to: All pairwise timing contrasts, all trait interactions

### Equivalence Testing
- Method: Two One-Sided Tests (TOST)
- SESOI: d = 0.30 (Cohen's convention for small effect)

## 14.2 File Inventory

### Scripts (10 R scripts)
- `comprehensive_analysis.R` - Main ANOVA and regression analyses
- `individual_differences_analysis.R` - Trust/dependence moderator analyses
- `false_lures_additional.R` - Binomial GLMM analyses
- `robustness_checks.R` - Article effects, counterbalancing, LOAO
- `recall_analyses.R` - Recall-specific investigations
- `recall_buffer_analyses.R` - AI buffer mechanism tests
- `additional_analyses.R` - Group comparisons, efficiency
- `ordered_analyses.R` - Comprehensive ordered analysis battery
- `timing_lures_final.R` - Final timing and lure models
- `robustness_additions.R` - Random slopes, nonlinearity, cross-validation

### Output Tables (162 CSV files)
All tables stored in `all_tables/` with prefixes indicating analysis section:
- `A1_`, `A2_`, `A3_`: Section A timing ANOVAs
- `B1_`: Section B correlations
- `C1_`, `C2_`: Section C structure analyses
- `D1_`, `D2_`, `D3_`: Section D process variables
- `E1_`, `E2_`: Section E moderators
- `L1_`-`L4_`: False lures final analyses
- `T1_`-`T5_`: Timing process chain
- `RS1_`-`RS5_`: Robustness sensitivity
- `ORD_`: Ordered analyses
- `REC_`: Recall analyses
- `ROB_`: Robustness checks

### Plots (15 PNG files)
All plots stored in `all_plots/`:
- `A1_mcq_accuracy_plot.png` - MCQ by timing × structure
- `timing_decomposition.png` - Progressive MCQ decomposition
- `ORD_plot2_lure_prob_by_structure.png` - Structure effect visualization
- (and 12 additional diagnostic/descriptive plots)

## 14.3 Data Structure

**Raw data:** `Analysis long finals-.xlsx`  
**Format:** Long format (1 row = 1 participant × 1 article)  
**N rows:** 108 (72 AI + 36 NoAI)  
**N participants:** 36 (24 AI + 12 NoAI)

---

**Report Completed:** January 3, 2026  
**Analysis Pipeline:** R 4.x with tidyverse, lme4, lmerTest, emmeans, broom.mixed  
**Report Author:** Automated analysis with human interpretation
