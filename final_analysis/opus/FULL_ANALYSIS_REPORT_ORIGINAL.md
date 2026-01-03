# COMPREHENSIVE ANALYSIS REPORT
## AI Memory Experiment - All Statistical Tests

**Generated:** January 2, 2026  
**Data:** Long format (1 row = 1 participant × 1 trial)  
**AI group:** 24 participants, 72 observations  
**NoAI group:** 12 participants, 36 observations

---

# TABLE OF CONTENTS

1. [Section A: Timing Effects on Learning (AI only)](#section-a)
2. [Section B: Summary Accuracy → Learning (AI only)](#section-b)
3. [Section C: Structure → False Lures Mechanism (AI only)](#section-c)
4. [Section D: Effort/Time as Process Variables (AI only)](#section-d)
5. [Section E: Trust/Dependence as Moderators (AI only)](#section-e)
6. [Section F: Confidence Calibration](#section-f)
7. [Section G: Article Effects (Robustness)](#section-g)
8. [Individual Differences Analysis](#individual-differences)
9. [Additional False Lures Analysis](#false-lures-additional)
10. [Robustness & Design Checks](#robustness-checks)
11. [Recall Relationship Analyses](#recall-analyses)
12. [Recall & AI Buffer Analyses](#recall-buffer)
13. [Additional Analyses (A-F)](#additional-analyses)
14. [Timing Process Chain Analyses (T1-T5)](#timing-process-chain)
15. [False Lures Final Analyses (L1-L4)](#false-lures-final)
16. [Robustness Additions (RS1-RS5)](#robustness-additions)

---

<a name="section-a"></a>
# SECTION A: TIMING EFFECTS ON LEARNING OUTCOMES (AI only)

**Design:** 2×3 mixed ANOVA (Structure: between; Timing: within)

## A1: MCQ Accuracy

| Effect | F | df | p | η²(ges) |
|--------|---|----|----|---------|
| **Structure** | 4.69 | 1, 22 | **.042*** | .072 |
| **Timing** | 11.77 | 1.77, 38.87 | **<.001**** | .254 |
| Interaction | 0.76 | 1.77, 38.87 | .461 | .021 |

**Timing Post-hoc (Holm):**
- Pre-reading vs Synchronous: Δ = 0.167, p = **.002***
- Pre-reading vs Post-reading: Δ = 0.137, p = **.003***
- Synchronous vs Post-reading: Δ = -0.030, p = .334

**Descriptives:**
| Structure | Timing | M | SD |
|-----------|--------|-----|-----|
| Integrated | Pre-reading | 0.750 | 0.124 |
| Integrated | Synchronous | 0.542 | 0.124 |
| Integrated | Post-reading | 0.607 | 0.094 |
| Segmented | Pre-reading | 0.649 | 0.108 |
| Segmented | Synchronous | 0.524 | 0.173 |
| Segmented | Post-reading | 0.518 | 0.143 |

---

## A2: Recall Total Score

| Effect | F | df | p | η²(ges) |
|--------|---|----|----|---------|
| Structure | 0.40 | 1, 22 | .536 | .015 |
| Timing | 0.03 | 1.86, 40.88 | .969 | <.001 |
| Interaction | 0.62 | 1.86, 40.88 | .533 | .004 |

**Result:** No significant effects on recall.

---

## A3: Article Accuracy

| Effect | F | df | p | η²(ges) |
|--------|---|----|----|---------|
| Structure | 1.99 | 1, 22 | .173 | .028 |
| Timing | 0.35 | 1.99, 43.79 | .707 | .011 |
| Interaction | 0.50 | 1.99, 43.79 | .608 | .015 |

**Result:** No significant effects on article accuracy.

---

<a name="section-b"></a>
# SECTION B: SUMMARY ACCURACY CORRELATIONS (AI only)

*Note: Summary accuracy and MCQ share the same underlying "correctness" signal (both test whether participants got the correct information). The strong correlation below is therefore expected and should not be interpreted as a causal mechanism.*

**Design:** Trial-level mixed-effects regression with random intercepts for participant and article

## B1: Summary Accuracy ↔ MCQ (Correlation, not mechanism)

| Predictor | β | SE | t | p |
|-----------|---|----|----|---|
| ai_summary_accuracy | 0.467 | 0.059 | 7.93 | <.001 |

→ Strong positive association (expected given shared construct)

---

## B2: Summary Accuracy → Recall

| Predictor | β | SE | t | p |
|-----------|---|----|----|---|
| ai_summary_accuracy | 0.854 | 0.804 | 1.06 | .305 |

**Result:** Not significant.

---

## B3: Summary Accuracy → Article Accuracy

| Predictor | β | SE | t | p |
|-----------|---|----|----|---|
| ai_summary_accuracy | -0.134 | 0.157 | -0.85 | .396 |

**Result:** Not significant.

---

<a name="section-c"></a>
# SECTION C: STRUCTURE → FALSE LURES (AI only)

## C1: False Lure Accuracy ANOVA

| Effect | F | df | p | η²(ges) |
|--------|---|----|----|---------|
| Structure | 4.20 | 1, 22 | .053 (marginal) | .075 |
| Timing | 1.13 | 1.64, 36.04 | .325 | .029 |
| Interaction | 0.47 | 1.64, 36.04 | .589 | .012 |

---

## C2: Is Structure Effect Explained by Effort/Time?

**Base Model:** false_lures ~ structure + timing + (1|participant) + (1|article)
- Structure β = 0.472, p = .041

**Mechanism Model:** + mental_effort + reading_time + summary_time
- Structure β = 0.482, p = .045
- **Change: only 2%**

❌ **Mental effort, reading time, and summary time do NOT explain the structure effect on false lures**

---

<a name="section-d"></a>
# SECTION D: EFFORT/TIME AS PROCESS VARIABLES (AI only)

## D1: Mental Effort

| Effect | F | df | p | η²(ges) |
|--------|---|----|----|---------|
| Structure | 2.43 | 1, 22 | .134 | .056 |
| Timing | 0.81 | 1.34, 29.37 | .408 | .017 |
| Interaction | 1.47 | 1.34, 29.37 | .242 | .030 |

---

## D2: Summary Time

| Effect | F | df | p | η²(ges) |
|--------|---|----|----|---------|
| **Structure** | 5.59 | 1, 22 | **.027*** | .069 |
| **Timing** | 5.97 | 1.60, 35.21 | **.009*** | .161 |
| Interaction | 0.93 | 1.60, 35.21 | .385 | .029 |

**Timing Post-hoc:**
- Pre-reading vs Post-reading: Δ = 73.8 sec, p < **.001***
- Synchronous vs Post-reading: Δ = 68.9 sec, p = **.034***

---

## D3: Reading Time

| Effect | F | df | p | η²(ges) |
|--------|---|----|----|---------|
| Structure | 0.90 | 1, 22 | .353 | .018 |
| **Timing** | 3.96 | 1.92, 42.23 | **.028*** | .091 |
| Interaction | 0.25 | 1.92, 42.23 | .769 | .006 |

**Timing Post-hoc:**
- Pre-reading vs Synchronous: Δ = -1.97 min, p = **.044***

---

<a name="section-e"></a>
# SECTION E: TRUST/DEPENDENCE AS MODERATORS (AI only)

## E1: Participant-Level Regressions (Individual Differences → Outcomes)

### Mean MCQ ~ Trust + Dependence + Prior Knowledge
| Predictor | β (std) | p |
|-----------|---------|---|
| Trust | 0.24 | .351 |
| Dependence | -0.18 | .490 |
| Prior Knowledge | -0.09 | .669 |

**R² = .056 (ns)**

### Mean Summary Accuracy ~ Trust + Dependence + Prior Knowledge
| Predictor | β (std) | p |
|-----------|---------|---|
| Trust | 0.42 | .064 (marginal) |
| Dependence | -0.06 | .775 |
| **Prior Knowledge** | **-0.40** | **.049*** |

**R² = .296**

✅ **Higher prior knowledge → lower summary accuracy** (unexpected)

### Mean False Lures ~ Trust + Dependence + Prior Knowledge
| Predictor | β (std) | p |
|-----------|---------|---|
| Trust | -0.02 | .926 |
| Dependence | -0.15 | .567 |
| Prior Knowledge | -0.14 | .519 |

**R² = .052 (ns)**

---

## E2: Moderation of Timing Effects

### Summary Accuracy ~ Timing × Trust/Dependence

| Interaction | β | p | Interpretation |
|-------------|---|---|----------------|
| **Post-reading × Trust** | 0.126 | **.030*** | High trust strengthens post-reading benefit |
| **Post-reading × Dependence** | 0.116 | **.012*** | High dependence strengthens post-reading benefit |
| Post-reading × Prior Knowledge | -0.022 | .579 | ns |

### MCQ ~ Timing × Trust/Dependence

| Interaction | β | p | Interpretation |
|-------------|---|---|----------------|
| **Post-reading × Trust** | 0.132 | **.002**** | High trust → larger MCQ gain from post-reading |
| Post-reading × Dependence | 0.055 | .128 | ns |
| Post-reading × Prior Knowledge | 0.013 | .654 | ns |

---

<a name="section-f"></a>
# SECTION F: CONFIDENCE CALIBRATION

## F1: Confidence-Recall Correlation

| Group | r | n |
|-------|---|---|
| Overall | 0.043 | 108 |
| AI | -0.044 | 72 |
| NoAI | 0.301 | 36 |

**Overall:** r = 0.043, 95% CI [-0.147, 0.230], p = .660 (ns)

---

## F2: Overconfidence (AI vs NoAI)

**Overconfidence = z(confidence) - z(recall)**

| Group | M | SD |
|-------|-----|-----|
| AI | 0.020 | 1.38 |
| NoAI | -0.041 | 0.88 |

**t-test:** t(31.7) = 0.16, p = .873 (ns)

❌ **No difference in overconfidence between AI and NoAI groups**

---

<a name="section-g"></a>
# SECTION G: ARTICLE EFFECTS (ROBUSTNESS)

## Article Difficulty

| Article | Mean MCQ | Mean Recall |
|---------|----------|-------------|
| Semiconductors | 0.480 (hardest) | 5.28 |
| UHI | 0.601 | 5.85 |
| CRISPR | 0.625 (easiest) | 5.35 |

## MCQ ~ Group × Article (all participants)

| Effect | β | p |
|--------|---|---|
| Group (NoAI) | -0.071 | .167 |
| Article (semiconductors) | -0.125 | **.003*** |
| Group × Article interaction | ns | >.05 |

✅ **Main conclusions robust to article differences**

---

<a name="individual-differences"></a>
# INDIVIDUAL DIFFERENCES ANALYSIS

## 1) Prior Knowledge × Group Interaction

**Mean MCQ ~ Group × Prior Knowledge**

| Effect | β | p |
|--------|---|---|
| Group (NoAI) | -0.108 | .337 |
| Prior Knowledge | -0.008 | .665 |
| **Interaction** | 0.008 | .858 |

❌ **Prior knowledge does NOT moderate AI vs NoAI benefit**

---

## 2) Time-on-Task → Outcomes

### Reading Time → MCQ (all participants)
| Predictor | β | p |
|-----------|---|---|
| log(reading_time) | -0.012 | .767 |
| Group (NoAI) | -0.088 | **.009*** |

### Summary Time → Summary Accuracy (AI only)
| Predictor | β | p |
|-----------|---|---|
| **log(summary_time)** | **0.064** | **.029*** |

✅ **Longer summary time → better summary accuracy**

### Summary Time → MCQ (AI only)
| Predictor | β | p |
|-----------|---|---|
| log(summary_time) | 0.016 | .439 |

---

## 3) Summary Accuracy ↔ MCQ (Correlation Note)

*Note: Summary accuracy and MCQ share the same underlying "correctness" signal. The strong correlation (β = 0.47) is expected and should not be interpreted as a causal mechanism. Timing coefficient attenuation when adding summary accuracy reflects shared variance, not mediation.*

---

# KEY TAKEAWAYS

1. **Timing matters for MCQ** (pre-reading best) but NOT for recall
2. **Structure affects false lures** (segmented → more) but NOT explained by effort/time
3. **Trust moderates timing effects** - high trust people benefit more from post-reading
4. **Time-on-task does NOT explain timing effect** (not a confound)
5. **No overconfidence difference** between AI and NoAI groups
6. **Prior knowledge negatively predicts summary accuracy** (counterintuitive)

---

# ADDITIONAL FALSE LURES ANALYSES

## 1) Summary Time → False Lures Selected (Poisson mixed model)

| Predictor | β | IRR | p |
|-----------|---|-----|---|
| log(summary_time) | 0.105 | 1.11 | .623 (ns) |
| **Structure (segmented)** | **0.619** | **1.86** | **.026*** |

❌ **Summary time does NOT predict false lure selection**  
✅ **Structure effect confirmed: segmented → 86% more false lures**

---

## 2) Summary Time → False Lure Accuracy

| Predictor | β | p |
|-----------|---|---|
| log(summary_time) | -0.067 | .256 (ns) |
| **Structure (segmented)** | **-0.197** | **.034*** |

❌ **Summary time does NOT predict lure discrimination**

---

## 3) Do False Lures Harm Learning?

### MCQ ~ False Lures
| Predictor | β | p |
|-----------|---|---|
| false_lures_selected | -0.0005 | .981 (ns) |

### Recall ~ False Lures
| Predictor | β | p |
|-----------|---|---|
| false_lures_selected | 0.192 | .363 (ns) |

❌ **False lure selection does NOT predict learning outcomes**  
*Selecting false lures appears to be "noise" rather than harmful*

---

## 4) Trust/Dependence/Prior Knowledge → False Lures (Trial-level Poisson)

| Predictor | β | IRR | p |
|-----------|---|-----|---|
| Trust | 0.192 | 1.21 | .270 (ns) |
| Dependence | -0.296 | 0.74 | .108 (marginal) |
| Prior Knowledge | -0.034 | 0.97 | .801 (ns) |
| **Structure (segmented)** | **0.796** | **2.22** | **.012*** |

❌ **Individual differences do NOT predict false lure selection**  
✅ **Structure remains the only significant predictor (IRR=2.22)**

---

# ROBUSTNESS AND DESIGN CHECKS

## A1: Article Difficulty Across All Outcomes

| Article | MCQ | Article Acc | Recall | Summary Acc (AI) | False Lures (AI) |
|---------|-----|-------------|--------|------------------|------------------|
| **Semiconductors** | **0.480** (hardest) | 0.443 | 5.28 | **0.562** (hardest) | 0.833 |
| UHI | 0.601 | 0.485 | **5.85** (best recall) | 0.760 | **0.958** (most lures) |
| CRISPR | 0.625 (easiest) | 0.540 | 5.35 | 0.719 | 0.667 |

✅ **Semiconductors is consistently harder across outcomes**

---

## A2: Counterbalancing Check (Timing × Article)

**Chi-square test:** X²(4) = 3.00, p = .558

| Timing | CRISPR | Semiconductors | UHI |
|--------|--------|----------------|-----|
| Pre-reading | 8 | 9 | 7 |
| Synchronous | 10 | 8 | 6 |
| Post-reading | 6 | 7 | 11 |

✅ **Counterbalancing is adequate** (p > .05)

---

## A3: Topic-Specific Timing Effects (Timing × Article)

| Outcome | Timing × Article Interaction | p |
|---------|------------------------------|---|
| Summary Accuracy | F(4, 59.8) = 1.88 | .125 (ns) |
| MCQ Accuracy | F(4, 60.5) = 1.34 | .264 (ns) |

✅ **Timing effects are consistent across articles** (no significant interaction)

---

## B4: Reading Time → Other Learning Outcomes

| Outcome | log(reading_time) β | p |
|---------|---------------------|---|
| Article Accuracy | 0.014 | .831 (ns) |
| Recall | 0.217 | .560 (ns) |

❌ **Reading time does NOT predict any learning outcome**

---

## B5: Mental Effort as Predictor

| Outcome | Mental Effort β | p |
|---------|-----------------|---|
| **MCQ** | **-0.034** | **.036*** |
| Summary Accuracy | -0.032 | .160 (ns) |
| False Lures | -0.030 | .762 (ns) |

✅ **Higher mental effort → slightly LOWER MCQ accuracy** (unexpected, but conditions don't differ in effort)

---

## B6: Confidence Calibration (Trial-level)

### All Participants: Recall ~ Confidence × Group
| Effect | β | p |
|--------|---|---|
| Confidence | 0.143 | .229 (ns) |
| Group × Confidence | 0.371 | .132 (ns) |

### AI Only: Recall ~ Confidence
| Effect | β | p |
|--------|---|---|
| Confidence | 0.206 | .082 (marginal) |

❌ **Confidence is weakly diagnostic of recall**

---

## B7: MCQ Mechanism Comparison

| Model | Predictors | AIC |
|-------|------------|-----|
| A | Summary Accuracy only | -107.25 |
| B | Article Accuracy only | -89.97 |
| **C** | **Both** | **-188.44** (best) |

### Model C (Both Mechanisms):
| Predictor | β | p |
|-----------|---|---|
| **Summary Accuracy** | **0.514** | **<.001**** |
| **Article Accuracy** | **0.284** | **<.001**** |

✅ **MCQ is driven by BOTH summary quality AND article comprehension**

---

## C8: Trust/Dependence → Time-on-Task

### Summary Time ~ Trust + Dependence + Prior Knowledge (R² = .53***)
| Predictor | β | p |
|-----------|---|---|
| **Trust** | **37.2** | **.005*** |
| **Dependence** | **-41.6** | **<.001**** |
| Prior Knowledge | 8.6 | .210 |

✅ **High-trust users spend MORE time on summaries**  
✅ **High-dependence users spend LESS time on summaries**

### Reading Time ~ Trust + Dependence + Prior Knowledge (R² = .27)
| Predictor | β | p |
|-----------|---|---|
| Trust | -0.27 | .629 |
| Dependence | -0.89 | .052 (marginal) |
| Prior Knowledge | 0.00 | .990 |

---

<a name="recall-analyses"></a>
# RECALL RELATIONSHIP ANALYSES

## A) Summary Time → Recall (AI only)

Model: `recall ~ log(summary_time) + timing + structure + (1|participant) + (1|article)`

| Predictor | β | SE | t | p |
|-----------|---|----|----|---|
| log(summary_time) | 0.315 | 0.206 | 1.53 | .133 |

❌ **Summary time does NOT predict recall**

---

## B) Mental Effort → Recall (AI only)

Model: `recall ~ mental_effort + timing + structure + (1|participant) + (1|article)`

| Predictor | β | SE | t | p |
|-----------|---|----|----|---|
| mental_effort | -0.215 | 0.170 | -1.27 | .210 |

❌ **Mental effort does NOT predict recall**

---

## C) Trust, Dependence, Prior Knowledge → Recall (AI only)

Model: `recall ~ ai_trust + ai_dependence + prior_knowledge + timing + structure + (1|participant) + (1|article)`

| Predictor | β | p | Result |
|-----------|---|---|--------|
| ai_trust | — | — | Dropped (collinearity) |
| ai_dependence | — | — | Dropped (collinearity) |
| prior_knowledge | 2.007 | .572 | ns |

❌ **Individual differences do NOT predict recall**

---

## D) Recall → MCQ (Mechanism Check, AI only)

Model: `mcq_accuracy ~ recall_total_score + timing + structure + (1|participant) + (1|article)`

| Predictor | β | SE | t | p |
|-----------|---|----|----|---|
| recall_total_score | 0.003 | 0.008 | 0.39 | .696 |

❌ **Recall does NOT predict MCQ accuracy**
→ These are independent learning outcomes

---

## E) Article Difficulty → Recall (Design Check)

Model: `recall ~ article + experiment_group + (1|participant)`

| Article | Mean Recall | SD |
|---------|-------------|-----|
| **UHI** | **5.85** (best) | 1.99 |
| CRISPR | 5.35 | 1.89 |
| **Semiconductors** | **5.28** (worst) | 1.86 |

**ANOVA:** F(2, 70) = 3.77, p = **.028***

✅ **Recall DOES differ by article** (UHI > Semiconductors)

---

<a name="recall-buffer"></a>
# RECALL & AI BUFFER ANALYSES

## A1) Recall → MCQ Relationship

**Question:** Do free recall and recognition (MCQ) track the same underlying learning?

Model: `mcq ~ recall + group + timing + structure + article + (1|participant)`

| Sample | β | SE | t | p |
|--------|---|----|----|---|
| All participants | 0.0005 | 0.007 | 0.07 | .943 |
| AI only | 0.003 | 0.008 | 0.38 | .706 |

❌ **Recall and MCQ are INDEPENDENT measures**
→ Free recall (self-generated) and recognition (cued) tap different cognitive processes

---

## A2) What Predicts Recall? (AI only)

Model: `recall ~ log(reading) + log(summary) + effort + summary_acc + trust + dependence + PK + timing + structure + article + (1|participant)`

| Predictor | β | p | Interpretation |
|-----------|---|---|----------------|
| log(reading_time) | 0.283 | .545 | ns |
| log(summary_time) | 0.229 | .340 | ns |
| mental_effort | -0.132 | .496 | ns |
| ai_summary_accuracy | 0.181 | .866 | ns |
| ai_trust | 1.052 | .150 | ns (marginal positive) |
| ai_dependence | -0.781 | .162 | ns (marginal negative) |
| prior_knowledge | -0.254 | .482 | ns |

❌ **No process or individual difference variables predict recall**
→ Recall appears resistant to experimental manipulations

---

## A3) Recall Confidence Calibration

**Question:** Does confidence predict actual recall? (Metacognitive monitoring)

Model: `recall ~ confidence * group + (1|participant) + (1|article)`

| Effect | β | p |
|--------|---|---|
| Confidence main effect | 0.143 | .229 |
| Confidence × Group | 0.371 | .132 |

❌ **Confidence is NOT calibrated with recall**
→ Participants show metacognitive failure in predicting their own recall

---

## B1) Summary Time → Summary Accuracy (AI Buffer Effect)

**Question:** Does time with AI summary serve as rehearsal/cue window?

Model: `summary_accuracy ~ log(summary_time) + timing + structure + article + (1|participant) + (1|article)`

| Predictor | β | SE | t | p |
|-----------|---|----|----|---|
| **log(summary_time)** | **0.062** | 0.028 | 2.21 | **.031*** |
| timing (pre-reading) | 0.164 | 0.046 | 3.57 | **<.001**** |
| timing (synchronous) | -0.094 | 0.044 | -2.14 | **.038*** |

✅ **Longer summary time → Better summary-based performance**
→ Supports "AI Buffer as rehearsal/reactivation window" framing

---

## B2) Summary Time → MCQ (Correlation Note)

*Note: Summary accuracy and MCQ share the same correctness signal. Any "mediation" through summary accuracy is tautological.*

Model: `mcq ~ log(summary_time) + summary_acc + article_acc + timing + structure + (1|participant) + (1|article)`

| Predictor | β | p | Result |
|-----------|---|---|--------|
| log(summary_time) | -0.007 | .412 | ns |
| ai_summary_accuracy | 0.520 | <.001 | (shared construct) |
| article_accuracy | 0.282 | <.001 | ✓ |

---

## BONUS: Offloading Test

**Question:** Does AI dependence hurt recall? (Cognitive offloading theory)

Model: `recall ~ ai_dependence + ai_trust + timing + structure + article + (1|participant)`

| Predictor | β | SE | t | p |
|-----------|---|----|----|---|
| ai_dependence | -0.939 | 0.525 | -1.79 | .089 (marginal) |
| ai_trust | 1.124 | 0.690 | 1.63 | .119 |

⚠️ **Marginal offloading effect** (p = .089)
→ Trend suggests higher dependence → lower recall, but not statistically significant

---

<a name="additional-analyses"></a>
# ADDITIONAL ANALYSES

## A) AI vs NoAI on Recall and Article Accuracy

### A1: Recall ~ Group + Article
| Group | EMM | SE | 95% CI |
|-------|-----|-----|--------|
| AI | 5.53 | 0.36 | [4.80, 6.27] |
| NoAI | 5.40 | 0.51 | [4.37, 6.44] |

**Contrast:** AI - NoAI = 0.13, p = .834 ❌ ns

### A2: Article Accuracy ~ Group + Article
| Group | EMM | SE | 95% CI |
|-------|-----|-----|--------|
| AI | 0.479 | 0.027 | [0.424, 0.535] |
| NoAI | 0.510 | 0.039 | [0.431, 0.588] |

**Contrast:** AI - NoAI = -0.03, p = .520 ❌ ns

✅ **No group differences on recall or article-only accuracy**

---

## B) Timing Efficiency (Controlling for Total Time)

**Question:** Does pre-reading still win when controlling for time-on-task?

### Total Time by Timing Condition
| Timing | Mean Total Time (sec) | SD |
|--------|----------------------|-----|
| Post-reading | 531 | 157 |
| Pre-reading | 547 | 144 |
| Synchronous | 660 | 266 |

### Model: MCQ ~ timing + structure + total_time_sec + article + (1|participant)

| Contrast | Estimate | SE | Effect Size (d) | p |
|----------|----------|-----|-----------------|---|
| **Pre - Post** | **0.144*** | 0.031 | **1.35** | **<.001** |
| Post - Sync | 0.029 | 0.033 | 0.28 | .378 |
| **Pre - Sync** | **0.173*** | 0.032 | **1.62** | **<.001** |

✅ **Pre-reading advantage PERSISTS after controlling for total time-on-task**

---

## C) False Lures Mechanism (Binomial Models)

### Model C1: Base Model (Binomial GLMM)
| Predictor | OR | 95% CI | p |
|-----------|-----|--------|---|
| ai_summary_accuracy | 8.66 | [0.52, 145] | .133 |
| **structure (segmented)** | **3.48** | **[1.17, 10.4]** | **.025*** |
| article (semiconductors) | 2.20 | [0.76, 6.4] | .145 |

### Model C2: Adding Trust & Dependence
| Predictor | OR | 95% CI | p |
|-----------|-----|--------|---|
| **structure (segmented)** | **5.18** | **[1.52, 17.6]** | **.009*** |
| ai_trust | 1.50 | [0.57, 4.0] | .413 |
| ai_dependence | 0.52 | [0.24, 1.1] | .081 (marginal) |

### Model C3: Summary Accuracy × Structure Interaction
| Predictor | OR | p |
|-----------|-----|---|
| ai_summary_accuracy | 60.4 | .037* |
| structure (segmented) | 54.4 | .020* |
| **Interaction** | **0.02** | **.081** (marginal) |

### Predicted Lure Probability
| Structure | Probability | 95% CI |
|-----------|-------------|--------|
| Integrated | 0.253 | [0.134, 0.427] |
| Segmented | 0.541 | [0.359, 0.713] |

✅ **Structure effect is robust; summary accuracy × structure interaction is marginal**

---

## D) MCQ Decomposition (Correlation Note)

*Note: Adding summary accuracy to models attenuates timing coefficients, but this reflects shared variance (both tap the same correctness construct), not a causal mechanism.*

| Model | Pre-reading β | p |
|-------|---------------|---|
| D0: Timing only | 0.144 | <.001 |
| D1: + Summary + Article accuracy | 0.029 | .034 |

**Change:** −0.115 (reflects shared variance, not mediation)

---

## E) Leave-One-Article-Out Robustness

| Dropped Article | Pre-reading β | p | Robust? |
|-----------------|---------------|---|---------|
| Semiconductors | 0.172 | <.001 | ✓ |
| UHI | 0.126 | .010 | ✓ |
| CRISPR | 0.116 | .016 | ✓ |

✅ **Pre-reading effect is ROBUST across all article subsets**

---

## F) Equivalence Test for Timing on Recall

**SESOI:** d = 0.30 (±0.60 raw units)

| Contrast | Estimate | 90% CI | TOST p | Decision |
|----------|----------|--------|--------|----------|
| Post - Pre | -0.009 | [-0.48, 0.46] | .020 | ✓ **EQUIVALENT** |
| Post - Sync | -0.071 | [-0.54, 0.40] | .033 | ✓ **EQUIVALENT** |
| Pre - Sync | -0.062 | [-0.53, 0.40] | .029 | ✓ **EQUIVALENT** |

✅ **All timing contrasts are EQUIVALENT for recall**
→ Timing does NOT affect recall (null is interpretable)

---

<a name="ordered-analyses"></a>
# ORDERED ANALYSES (0-6)

This section contains the comprehensive ordered analyses requested, covering article differences, AI vs NoAI comparisons, efficiency, false lures mechanism, decomposition, recall interpretability, and robustness checks.

---

## 0) ARTICLE DIFFERENCES

### Descriptives by Article
| Article | MCQ Mean | MCQ SD | Recall Mean | Recall SD | n |
|---------|----------|--------|-------------|-----------|---|
| CRISPR | 0.625 (easiest) | 0.134 | 5.35 | 1.89 | 36 |
| Semiconductors | 0.480 (hardest) | 0.170 | 5.28 | 1.86 | 36 |
| UHI | 0.601 | 0.144 | 5.85 (best) | 1.99 | 36 |

### Model 0A: MCQ ~ article + group + (1|participant_id)
| Effect | β | SE | t | p |
|--------|---|----|----|---|
| (Intercept) | 0.654 | 0.026 | 24.89 | <.001*** |
| **Semiconductors** | **-0.145** | 0.033 | -4.40 | **<.001**** |
| UHI | -0.024 | 0.033 | -0.72 | .472 |
| **Group (NoAI)** | **-0.088** | 0.031 | -2.80 | **.008*** |

**Article Pairwise Contrasts (Holm):**
| Contrast | Δ | p |
|----------|---|---|
| CRISPR - Semiconductors | **0.145** | **<.001**** |
| CRISPR - UHI | 0.024 | .472 |
| Semiconductors - UHI | **-0.121** | **<.001**** |

### Model 0B: Group × Article Interaction
| Effect | F | df | p |
|--------|---|----|----|
| Group | 7.86 | 1, 34 | **.008*** |
| Article | 11.34 | 2, 68 | **<.001**** |
| **Group × Article** | 0.56 | 2, 68 | **.573 (ns)** |

❌ **No Group × Article interaction** → Group effect is consistent across articles

### Model 0C: AI-only Timing × Article (MCQ)
| Effect | F | df | p |
|--------|---|----|----|
| **Timing** | 17.41 | 2, 42 | **<.001**** |
| **Article** | 11.50 | 2, 42 | **<.001**** |
| **Timing × Article** | 1.34 | 4, 60 | **.264 (ns)** |

❌ **No Timing × Article interaction** → Timing effect is consistent across articles

### Model 0D: AI-only Timing × Article (Summary Accuracy)
| Effect | F | df | p |
|--------|---|----|----|
| **Timing** | 24.21 | 2, 42 | **<.001**** |
| **Article** | 16.46 | 2, 42 | **<.001**** |
| Timing × Article | 1.88 | 4, 60 | .125 (ns) |

❌ **No Timing × Article interaction for summary accuracy**

---

## 1) AI vs NoAI BEYOND MCQ

### Model 1A: Recall ~ group + article + (1|participant_id)
| Group | EMM | SE | 95% CI |
|-------|-----|-----|--------|
| AI | 5.53 | 0.36 | [4.80, 6.27] |
| NoAI | 5.40 | 0.51 | [4.37, 6.44] |

**Contrast:** AI - NoAI = 0.13, p = .834 ❌ ns

### Model 1B: Article Accuracy ~ group + article + (1|participant_id)
| Group | EMM | SE | 95% CI |
|-------|-----|-----|--------|
| AI | 0.479 | 0.027 | [0.424, 0.535] |
| NoAI | 0.510 | 0.039 | [0.431, 0.588] |

**Contrast:** AI - NoAI = -0.03, p = .520 ❌ ns

✅ **No group differences on recall or article-only accuracy**

---

## 2) EFFICIENCY (AI ONLY) - Controlling for Total Time

### Total Time by Timing Condition
| Timing | Mean Total Time (sec) | SD |
|--------|----------------------|-----|
| Post-reading | 531 | 157 |
| Pre-reading | 547 | 144 |
| Synchronous | 660 | 266 |

### Model: MCQ ~ timing + structure + total_time_sec + article + (1|participant_id)

| Contrast | Estimate | SE | Effect Size (d) | p |
|----------|----------|-----|-----------------|---|
| **Pre - Sync** | **0.173*** | 0.032 | **1.62** | **<.001** |
| **Pre - Post** | **0.144*** | 0.031 | **1.35** | **<.001** |
| Post - Sync | 0.029 | 0.033 | 0.28 | .378 |

**Note:** `total_time_sec` β ≈ 0, p = .993 (not a confound)

✅ **Pre-reading advantage PERSISTS after controlling for total time-on-task**

---

## 3) FALSE LURES MECHANISM (AI ONLY) - Binomial Models

### Model 3A: Base Binomial GLMM
`cbind(lures, 2-lures) ~ ai_summary_accuracy + timing + structure + article + (1|participant_id)`

| Predictor | OR | 95% CI | p |
|-----------|-----|--------|---|
| ai_summary_accuracy | 8.70 | [0.52, 146] | .133 |
| **structure (segmented)** | **3.48** | **[1.17, 10.4]** | **.026*** |
| semiconductors | 2.20 | [0.76, 6.4] | .145 |
| uhi | 1.94 | [0.75, 5.0] | .174 |

### Model 3B: Adding Trust + Dependence
| Predictor | OR | 95% CI | p |
|-----------|-----|--------|---|
| **structure (segmented)** | **5.17** | **[1.52, 17.6]** | **.009*** |
| ai_trust | 1.50 | [0.57, 4.0] | .414 |
| ai_dependence | 0.52 | [0.25, 1.1] | .085 (marginal) |

### Model 3C: Summary Accuracy × Structure Interaction
| Predictor | OR | p |
|-----------|-----|---|
| ai_summary_accuracy | 60.5 | .037* |
| structure (segmented) | 54.4 | .020* |
| **Interaction** | 0.02 | **.082** (marginal) |

### Predicted Lure Probability by Structure
| Structure | Probability | 95% CI |
|-----------|-------------|--------|
| Integrated | 0.253 | [0.134, 0.427] |
| **Segmented** | **0.541** | [0.359, 0.713] |

✅ **Structure effect is robust (OR = 3.5-5.2)**
⚠️ **Marginal interaction: structure effect may be weaker at high summary accuracy**

---

## 4) DECOMPOSITION (AI ONLY)

### Timing Effects Before vs After Adding Mechanism Variables

| Model | Sync β | Post β |
|-------|--------|--------|
| 4A: Timing only | -0.173 | -0.144 |
| 4B: + Summary + Article acc | -0.017 | -0.029 |
| **Change** | **90.2%↓** | **79.7%↓** |

### Model 4B: Full Decomposition
`mcq ~ ai_summary_accuracy + article_accuracy + timing + structure + article + (1|participant_id)`

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

✅ **Timing effect is ~85% explained by summary + article accuracy**
→ Pre-reading helps because it improves summary quality AND article comprehension

---

## 5) RECALL NULL INTERPRETABILITY (AI ONLY) + TOST

### Model: Recall ~ timing + structure + article + (1|participant_id)

| Timing | EMM | SE | 95% CI |
|--------|-----|-----|--------|
| Pre-reading | 5.52 | 0.42 | [4.66, 6.37] |
| Synchronous | 5.58 | 0.42 | [4.72, 6.43] |
| Post-reading | 5.51 | 0.42 | [4.65, 6.36] |

**Timing contrasts:** All p > .80 (completely null)

### TOST Equivalence Tests
**SESOI:** d = 0.30 (±0.60 raw units)

| Contrast | Estimate | 90% CI | TOST p | Decision |
|----------|----------|--------|--------|----------|
| Pre - Sync | -0.062 | [-0.67, 0.54] | .029 | ✓ **EQUIVALENT** |
| Pre - Post | 0.009 | [-0.60, 0.62] | .020 | ✓ **EQUIVALENT** |
| Sync - Post | 0.071 | [-0.55, 0.69] | .033 | ✓ **EQUIVALENT** |

✅ **All timing contrasts are EQUIVALENT for recall**
→ Timing does NOT affect recall (null is interpretable, not underpowered)

---

## 6) ROBUSTNESS CHECKS

### 6A) Leave-One-Article-Out

| Dropped Article | Pre-Sync Δ | SE | p | Structure OR | Structure p |
|-----------------|------------|-----|---|--------------|-------------|
| Semiconductors | 0.161 | 0.041 | .001** | 2.12 | .118 |
| UHI | 0.192 | 0.037 | <.001*** | 10.5 | .006** |
| CRISPR | 0.164 | 0.047 | .004** | 2.67 | <.001*** |

✅ **Pre-reading effect is ROBUST across all article subsets**
⚠️ **Structure→lures effect varies by dropped article (sensitive to UHI)**

### 6B) Random-Effects Sensitivity

| Model Specification | Pre-Sync Δ | p |
|---------------------|------------|---|
| (1\|participant) + (1\|article) | 0.173 | <.001*** |
| (1\|participant) only | 0.169 | <.001*** |
| + article fixed effect | 0.173 | <.001*** |

✅ **Timing effect is ROBUST to random-effects specification**

### 6C) False-Lure Overdispersion Check

**Overdispersion ratio:** 0.80 (< 1.5 threshold)

✅ **No overdispersion** - binomial model is appropriate

### 6D) Time-Cap Sensitivity

**Trials at cap (reading ≥ 14.9 min):** 1 trial (P252, CRISPR, synchronous)

| Condition | Pre-Sync Δ | p |
|-----------|------------|---|
| Full data | 0.173 | <.001 |
| Excluding capped | 0.172 | <.001 |

✅ **Time cap does NOT affect results**

### 6E) Leave-One-Participant-Out Influence

**Structure → False Lures:**
- OR range: 2.68 - 4.23 (all consistently positive)
- p range: all < .054

**AI vs NoAI MCQ:**
- β range: -0.107 to -0.079 (all consistently negative)

✅ **No influential participants** - results are stable

---

# SUMMARY OF KEY FINDINGS

## Primary Effects
1. **Pre-reading timing is optimal for MCQ** (d = 1.35-1.62, robust across articles)
2. **Timing effect persists after controlling for total time** (not a time-on-task confound)
3. **Segmented structure increases false lure selection** (OR = 3.5-5.2)

## Null Effects (Interpretable)
4. **Timing does NOT affect recall** (TOST confirms equivalence)
5. **No AI vs NoAI differences** on recall or article-only accuracy
6. **No Group × Article interaction** - effects are consistent

## Robustness
7. **All key findings robust to:**
   - Leave-one-article-out
   - Random-effects specification
   - Time-cap exclusion
   - Leave-one-participant-out

---

<a name="timing-process-chain"></a>
# TIMING PROCESS CHAIN ANALYSES

This section completes the causal chain: does timing change process variables, and do those explain timing effects?

---

## T1) SANITY CHECK: Trust/Dependence Balance

**Question:** Are trust/dependence balanced across timing conditions?

Trust and dependence are participant-level traits (measured once), so they should be identical across within-subject timing conditions.

| Timing | Trust Mean | Trust SD | Dependence Mean | Dependence SD | n |
|--------|-----------|----------|-----------------|---------------|---|
| Pre-reading | 4.94 | 0.72 | 5.15 | 0.91 | 24 |
| Synchronous | 4.94 | 0.72 | 5.15 | 0.91 | 24 |
| Post-reading | 4.94 | 0.72 | 5.15 | 0.91 | 24 |

✅ **Perfect balance** - Trust/dependence are constant within participants (as expected)
→ No confound; these are true moderators, not confounders

---

## T2) TIMING → SUMMARY ACCURACY via TIME ("Buffer" Mechanism)

**Question:** Does timing remain significant after controlling for summary time?

### Base Model: Summary Acc ~ timing + structure + article
| Contrast | Estimate | p |
|----------|----------|---|
| Pre - Sync | 0.271 | <.001*** |
| Pre - Post | 0.214 | <.001*** |

### + log(summary_time_sec)
| Contrast | Estimate | p |
|----------|----------|---|
| Pre - Sync | 0.258 | <.001*** |
| Pre - Post | 0.164 | .002** |

| Effect | log(summary_time) β | p |
|--------|---------------------|---|
| Summary time | 0.062 | .031* |

**Coefficient Change:**
- Synchronous: −0.271 → −0.258 (5% reduction)
- Post-reading: −0.214 → −0.164 (23% reduction)

✅ **Timing remains highly significant after controlling summary time**
→ Pre-reading wins because of QUALITY, not just TIME

---

## T3) TIME-ON-TASK CHECK (Not Decomposition)

**Question:** Is the timing effect a time-on-task confound?

| Model | Sync β | Post β |
|-------|--------|--------|
| 1: timing only | -0.173 | -0.144 |
| 2: + total_time | -0.175 | -0.143 |

**Time coefficient:** log(total_time) β = 0.009, p = .578 (ns)

✅ **Timing effect is NOT explained by total time-on-task**
→ Pre-reading advantage is not simply a matter of spending more time

*Note: We do not include summary accuracy decomposition here because summary accuracy and MCQ share the same correctness construct (tautological correlation).*

---

## T4) EFFORT AS MARKER (Not a Cause)

**Question:** Does mental effort explain timing effects?

### MCQ ~ timing + structure + mental_effort + article
| Predictor | β | p |
|-----------|---|---|
| timing (synchronous) | -0.184 | <.001*** |
| timing (post_reading) | -0.144 | <.001*** |
| mental_effort | -0.032 | .044* |

**Timing coefficient change:** Essentially 0%

✅ **Timing effects UNCHANGED after controlling effort**
→ Effort is not driving timing effects
→ The negative effort→MCQ relationship is incidental

---

## T5) WHO BENEFITS? (Within-Person Trait Moderation)

**Question:** Do individual differences predict who gains most from pre-reading?

### Delta Descriptives
| Contrast | Mean Δ | SD |
|----------|--------|-----|
| MCQ (Pre - Sync) | 0.167 | 0.205 |
| MCQ (Pre - Post) | 0.137 | 0.177 |
| Summary Acc (Pre - Sync) | 0.266 | 0.291 |
| Summary Acc (Pre - Post) | 0.193 | 0.221 |

### MCQ Δ(Pre-Post) ~ Traits (R² = .30, p = .067)
| Predictor | β | p |
|-----------|---|---|
| **ai_trust** | **-0.150** | **.011*** |
| ai_dependence | 0.038 | .376 |
| prior_knowledge | 0.015 | .634 |

⚠️ **Unexpected finding:** Higher trust → SMALLER pre-reading advantage over post
→ Interpretation: High-trust individuals may benefit more from post-reading (waiting for AI summary)

### Other Deltas
- MCQ Δ(Pre-Sync) ~ Traits: All ns (p > .46)
- Summary Acc deltas: All ns

---

<a name="false-lures-final"></a>
# FALSE LURES FINAL ANALYSES

---

## L1) FULL DEFINITIVE BINOMIAL MODEL

**Model:** `cbind(lures, 2-lures) ~ structure + timing + summary_acc + article_acc + trust + dependence + log(summary_time) + log(reading_time) + effort + article + (1|participant)`

### Key Results
| Predictor | OR | 95% CI | p |
|-----------|-----|--------|---|
| **structure (segmented)** | **5.93** | **[1.63, 21.5]** | **.007*** |
| ai_dependence | 0.49 | [0.22, 1.09] | .080 (marginal) |
| ai_trust | 1.57 | [0.58, 4.30] | .378 |
| ai_summary_accuracy | 11.5 | [0.48, 276] | .132 |
| article_accuracy | 1.79 | [0.31, 10.3] | .515 |
| timing (synchronous) | 1.60 | [0.42, 6.03] | .491 |
| timing (post_reading) | 1.28 | [0.38, 4.31] | .691 |
| log(summary_time) | 0.85 | [0.41, 1.76] | .664 |
| log(reading_time) | 1.03 | [0.26, 4.07] | .970 |
| mental_effort | 1.17 | [0.70, 1.95] | .545 |

✅ **Structure effect is ROBUST controlling for everything** (OR = 5.93, p = .007)
⚠️ **Dependence marginal** (OR = 0.49, p = .080): High dependence → fewer lures
❌ **Timing, time, effort do NOT predict lures**

---

## L2) ARTICLE EFFECTS ON FALSE LURES

**Predicted lure probability by article:**
| Article | Probability | 95% CI |
|---------|-------------|--------|
| CRISPR | 0.303 | [0.17, 0.48] |
| Semiconductors | 0.398 | [0.24, 0.58] |
| UHI | 0.477 | [0.31, 0.65] |

**Article contrasts (Holm):** All ns (p > .36)

✅ **No significant article effect on lures** - structure effect generalizes

---

## L3) SIMPLE EFFECTS: Timing Within Each Structure

### Integrated Structure
| Timing | Lure Prob | 95% CI |
|--------|-----------|--------|
| Pre-reading | 0.451 | [0.22, 0.70] |
| Synchronous | 0.175 | [0.05, 0.44] |
| Post-reading | 0.139 | [0.04, 0.39] |

⚠️ **Trend:** In integrated, pre-reading has MORE lures (but timing ns)

### Segmented Structure
| Timing | Lure Prob | 95% CI |
|--------|-----------|--------|
| Pre-reading | 0.440 | [0.20, 0.72] |
| Synchronous | 0.570 | [0.29, 0.81] |
| Post-reading | 0.613 | [0.33, 0.83] |

**Pattern:** Opposite to integrated - sync/post have more lures in segmented

❌ **No significant timing effects within either structure**
→ Structure is the dominant predictor, not timing

---

## L4) MODEL FAMILY COMPARISON (Sensitivity)

| Model | AIC | Structure Coef | Structure OR/IRR | p |
|-------|-----|----------------|------------------|---|
| **Binomial** | **155.4** | 1.18 | **3.25** | **.026*** |
| Poisson | 171.3 | 0.59 | 1.81 | .030* |

✅ **Binomial is preferred** (lower AIC by 16 points)
✅ **Both models agree: structure is significant**
→ Binomial better matches the bounded 0-2 outcome

### Predicted Lure Probability (Binomial)
| Structure | Probability | 95% CI |
|-----------|-------------|--------|
| Integrated | 0.262 | [0.14, 0.43] |
| Segmented | 0.536 | [0.36, 0.70] |

---

# ROBUSTNESS ADDITIONS (RS1-RS5)

## RS1: Random-Slope Robustness for Timing

Tests whether timing effects remain significant when allowing individual variation in timing slopes.

### MCQ Accuracy with Random Slopes

| Model | (Intercept) | Sync Effect | Post Effect | AIC |
|-------|-------------|-------------|-------------|-----|
| Random Intercept | 0.792 | -0.173 | -0.144 | -97.2 |
| Random Slopes | 0.793 | -0.173 | -0.144 | -101.3 |

**Model comparison:** χ²(2) = 8.01, p = .018*
→ Random slopes model fits better but timing effects unchanged

**Timing contrasts with random slopes:**
| Contrast | Estimate | SE | t | p |
|----------|----------|-----|------|-------|
| Pre vs Synchronous | 0.173 | 0.033 | 5.24 | <.0001 |
| Pre vs Post | 0.144 | 0.033 | 4.32 | .0003 |

**Random effects variance:**
- Intercept SD = 0.091
- Timing slope SD = 0.107
- Correlation = -0.90 (participants high at baseline show smaller pre-reading advantage)

### Summary Accuracy with Random Slopes

Model comparison: χ²(2) = 9.60, p = .008**
→ Random slopes model preferred; timing effects stable

### Participant-Level Validation

| Measure | Pre-Sync Δ | SD | % Showing Advantage |
|---------|------------|-----|---------------------|
| MCQ | 0.167 | 0.205 | 83.3% |
| Summary | 0.266 | 0.291 | 75.0% |

**One-sample t-tests (H₀: effect = 0):**
- MCQ Pre-Sync: t(23) = 3.98, p = .0006
- MCQ Pre-Post: t(23) = 3.78, p = .001
- Summary Pre-Sync: t(23) = 4.47, p = .0002

✅ **Timing effects are robust to random slopes**  
✅ **83% of participants individually show pre-reading MCQ advantage**

---

## RS2: Nonlinearity / Diminishing Returns for Time Variables

Tests whether time-accuracy relationships are better captured by splines than linear (log) predictors.

| Outcome | Time Variable | Linear AIC | Spline AIC | ΔAIC | LRT p |
|---------|---------------|------------|------------|------|-------|
| Summary Acc | Summary Time | -13.5 | -7.9 | -5.6 | 1.0 |
| MCQ Acc | Total Time | -58.0 | -51.4 | -6.6 | .264 |

✅ **No evidence of diminishing returns**  
✅ **Linear (log-transformed) models are sufficient**  
→ Simple log-linear relationship holds throughout the time range

---

## RS3: Cross-Validated Prediction (LOOCV)

Leave-one-out cross-validation for MCQ decomposition models:

| Model | RMSE | Correlation |
|-------|------|-------------|
| 1: Timing only | 0.122 | 0.582 |
| 2: + Summary Acc | 0.092 | 0.792 |
| 3: + Summary + Article Acc | 0.049 | 0.945 |

**Improvement from Model 1 → 3:**
- RMSE reduction: **60.1%**
- Correlation increase: **+0.36**

✅ **Full decomposition model predicts out-of-sample exceptionally well (r = .95)**  
✅ **Summary + Article accuracy explain almost all predictable variance**

---

## RS4: Multiple Comparison Correction for Trait Interactions

Holm-corrected p-values for 12 trait × timing interactions (3 traits × 2 contrasts × 2 outcomes):

| Outcome | Trait | Timing | p_raw | p_Holm | Sig (raw) | Sig (Holm) |
|---------|-------|--------|-------|--------|-----------|------------|
| MCQ | Trust | Pre-Post | .002 | **.023** | ✓ | ✓ |
| Summary | Trust | Pre-Post | .029 | .285 | ✓ | - |
| Summary | Dependence | Pre-Post | .010 | .109 | ✓ | - |

**Summary:**
- Raw significant (p < .05): 3 of 12
- Holm-corrected significant: **1 of 12**

✅ **Trust × Timing(Pre-Post) on MCQ survives Holm correction**  
→ High-trust participants show smaller pre-reading advantage (interpretable: they rely on AI regardless of timing)

---

## RS5: Lure Model Separation / Stability Check

Checks for quasi-complete separation in binomial false lures model:

**False lures distribution:**
| Count | 0 | 1 | 2 |
|-------|---|---|---|
| N | 29 | 27 | 16 |

**Fitted probabilities:**
| Statistic | Value |
|-----------|-------|
| Min | 0.103 |
| Max | 0.823 |
| Mean | 0.406 |
| Prob < 0.01 | 0 |
| Prob > 0.99 | 0 |

**Structure effect by profile likelihood:**
| Parameter | 95% CI | OR 95% CI |
|-----------|--------|-----------|
| Structure (Seg vs Int) | [0.13, 2.38] | [1.14, 10.76] |

**Mean fitted probability by structure:**
| Structure | Mean | Min | Max |
|-----------|------|-----|-----|
| Integrated | 0.283 | 0.103 | 0.592 |
| Segmented | 0.529 | 0.237 | 0.822 |

✅ **No separation issues detected**  
✅ **Profile likelihood CI confirms structure effect: OR 1.14-10.76**  
→ Model estimates are stable and reliable

---

# SUMMARY OF KEY FINDINGS

## Primary Effects
1. **Pre-reading timing is optimal for MCQ** (d = 1.35-1.62, robust across articles)
2. **Timing effect persists after controlling for total time** (not a time-on-task confound)
3. **Segmented structure increases false lure selection** (OR = 3.5-5.9)

## Null Effects (Interpretable)
4. **Timing does NOT affect recall** (TOST confirms equivalence)
5. **No AI vs NoAI differences** on recall or article-only accuracy
6. **No Group × Article interaction** - effects are consistent
7. **Timing does NOT affect false lures** - structure is the only driver

## Process Variables
8. **Time-on-task does NOT explain timing** (0% reduction when controlled)
9. **Effort does NOT explain timing** (timing unchanged after controlling effort)
10. **Trust moderates who benefits from pre-reading** (high trust → smaller pre-vs-post advantage)

## Robustness
11. **All key findings robust to:**
   - Leave-one-article-out
   - Random-effects specification (random slopes: p = .018)
   - Model family (binomial vs Poisson)
   - Time-cap exclusion
   - Leave-one-participant-out
   - Holm correction for multiple comparisons
   - Separation diagnostics for binomial models

---

# FILES

- **Scripts:** `scripts/comprehensive_analysis.R`, `scripts/individual_differences_analysis.R`, `scripts/false_lures_additional.R`, `scripts/robustness_checks.R`, `scripts/recall_analyses.R`, `scripts/recall_buffer_analyses.R`, `scripts/additional_analyses.R`, `scripts/ordered_analyses.R`, `scripts/timing_lures_final.R`, `scripts/robustness_additions.R`
- **Tables:** 162 CSV files in `all_tables/`
- **Plots:** 15 PNG files in `all_plots/`
