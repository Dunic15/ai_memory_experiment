# AI MEMORY EXPERIMENT  
## Expanded Interpretive Report (Key Findings, Secondary Findings, Robustness, and Variable Relationships)

**Source:** `final_analysis/opus/COMPREHENSIVE_FINAL_ANALYSIS_REPORT.md` (Jan 3, 2026) + supporting outputs in `final_analysis/opus/all_tables/`  
**Data:** 36 participants (24 AI, 12 NoAI), 108 participant×article observations (3 articles)  
**Design (AI group):** 2 (Structure: integrated vs segmented; between-subjects) × 3 (Timing: pre-reading vs synchronous vs post-reading; within-subjects)

---

## Quick Takeaways (What Matters Most)

1. **Pre-reading is the clear “best timing” for MCQ performance** (recognition/selection-based learning). The effect is **large** (d ≈ 1.35–1.62) and **replicates across articles and participants**.
2. **Structure—not timing—is the main driver of false-lure susceptibility.** **Segmented summaries** substantially increase false-lure endorsement (model-based probabilities ≈ **54%** segmented vs **25%** integrated; OR ≈ **3–6** depending on model).
3. **Recall behaves differently from MCQ.** Timing effects on recall are not just “non-significant”; they are **equivalent (TOST-confirmed)**, implying a meaningful dissociation between recognition and generative retrieval.
4. **Time-on-task is not the story.** Total time is essentially constant across timing conditions; pre-reading wins primarily via **quality of encoding** (better summary + article accuracy), not quantity of time.
5. **Trust changes who benefits from post-reading.** High-trust participants can still gain from post-reading, shrinking the pre-reading advantage for them; low-trust participants depend more on the pre-reading scaffold.

---

## 1) Primary Findings (With Plain-Language Interpretation)

### 1.1 Timing → MCQ Accuracy (“Preview Effect” / Cognitive Scaffold)

**Empirical pattern (AI group; mean ± SD, n = 24 per timing):**

| Timing | MCQ accuracy | Interpretation |
|---|---:|---|
| **Pre-reading** | **0.699 ± 0.125** | Best performance |
| Synchronous | 0.533 ± 0.147 | Worse than pre-reading |
| Post-reading | 0.562 ± 0.127 | Worse than pre-reading |

**Key contrasts (Holm-corrected):**
- **Pre vs synchronous:** Δ ≈ **+0.167**, p ≈ **.0019**, **d ≈ 1.62**
- **Pre vs post:** Δ ≈ **+0.137**, p ≈ **.0025**, **d ≈ 1.35**

**Mixed ANOVA (structure × timing, AI group):**
- **Timing:** F(1.77, 38.87) = **11.77**, p = **.00018**, ges = **.254**
- **Structure:** F(1, 22) = **4.69**, p = **.0415**, ges = **.072**
- **Timing × structure:** F(1.77, 38.87) = 0.76, p = .461, ges = .021

**Condition means (MCQ; structure × timing):**

| Structure | Pre-reading | Synchronous | Post-reading |
|---|---:|---:|---:|
| Integrated | 0.750 | 0.542 | 0.607 |
| Segmented | 0.649 | 0.524 | 0.518 |

**Interpretation (mechanism-level):**  
Pre-reading summaries act like a **schema primer**: they give learners a “map” of what to look for, which improves how incoming information is organized during reading. That improved organization shows up strongly when later performance is **cue-supported** (MCQ recognition/selection).

![](all_plots/A1_mcq_accuracy_plot.png)

---

### 1.2 Structure → False Lures (“Fragmentation Problem”)

False lures are **incorrect AI-generated claims** that participants sometimes endorse as true.

**Descriptive pattern (AI group; observed false lures selected, 0–2 per trial):**

| Structure | Mean false lures selected ± SD | Approx. lure endorsement probability |
|---|---:|---:|
| Integrated | 0.58 ± 0.69 | 0.29 |
| **Segmented** | **1.06 ± 0.79** | **0.53** |

**Model-based probability of endorsing false lures (AI group):**

| Structure | Predicted lure-endorsement probability | Practical meaning |
|---|---:|---|
| Integrated | **~0.25** | ~1 in 4 false claims endorsed |
| **Segmented** | **~0.54** | ~1 in 2 false claims endorsed |

**Inference (full binomial GLMM):**
- **Structure (segmented)** is the **only consistently robust predictor** (e.g., OR ≈ **5.93**, 95% CI [1.63, 21.5], p ≈ **.007** in the full model).
- **Timing is not a reliable predictor** of false-lure endorsement once structure is considered.
- Adding process variables (reading time, summary time, mental effort) **does not explain away** the structure effect.

**Interpretation (mechanism-level):**  
Segmenting the summary appears to **fragment the mental representation**, increasing **source confusion** (what came from the AI vs what came from the article), which makes learners more vulnerable to accepting plausible-but-false claims.

![](all_plots/C1_false_lure_accuracy_plot.png)

![](all_plots/ORD_plot2_lure_prob_by_structure.png)

---

### 1.3 Timing → Recall (Meaningful Null; Equivalence Confirmed)

Timing has **no meaningful effect** on free recall. Importantly, equivalence testing (TOST) supports the conclusion that timing conditions are **functionally equivalent**, not merely underpowered.

**Descriptives (AI group; mean ± SD, n = 24 per timing):**

| Timing | Recall total score |
|---|---:|
| Pre-reading | 5.50 ± 1.92 |
| Synchronous | 5.54 ± 1.99 |
| Post-reading | 5.56 ± 2.17 |

**Mixed ANOVA (structure × timing, AI group):**
- **Timing:** F(1.86, 40.88) = 0.03, p = .969, ges < .001
- **Structure:** F(1, 22) = 0.40, p = .536, ges = .015
- **Timing × structure:** F(1.86, 40.88) = 0.62, p = .532, ges = .004

**Interpretation:**  
This is a classic dissociation:
- **MCQ** benefits from cues and structure in the environment (recognition).
- **Recall** requires self-generated retrieval; the timing manipulation doesn’t strengthen the underlying memory trace enough to move recall.

![](all_plots/A2_recall_total_score_plot.png)

---

### 1.4 Timing/Structure → Article-Only Accuracy (No Detectable Effect)

Performance on questions that do **not** reference AI-summary information does not vary reliably by timing or structure. This suggests the strongest effects are about **how AI summary information is encoded/used**, not about general reading comprehension.

**Mixed ANOVA (structure × timing, AI group):**
- **Timing:** F(1.99, 43.79) = 0.35, p = .707, ges = .011
- **Structure:** F(1, 22) = 1.98, p = .173, ges = .028
- **Timing × structure:** F(1.99, 43.79) = 0.50, p = .608, ges = .015

![](all_plots/A3_article_accuracy_plot.png)

![](all_plots/ORD_plot3_article_difficulty.png)

---

## 2) Secondary Findings (Process Variables + Moderators)

### 2.1 Summary Time and “Time Reallocation”

Summary viewing time differs strongly by timing:

| Timing | Summary time (sec, mean) | What it suggests |
|---|---:|---|
| **Pre-reading** | **~132.5** | Learners engage with the summary when it frames the task |
| Synchronous | ~100.3 | Engagement still substantial |
| **Post-reading** | **~69.5** | Summary becomes “optional” and is used less |

**Descriptives (AI group; mean ± SD, n = 24 per timing):**

| Timing | Summary time (sec) |
|---|---:|
| Pre-reading | 132.5 ± 47.0 |
| Synchronous | 100.3 ± 50.9 |
| Post-reading | 69.5 ± 38.1 |

**Mixed ANOVA (structure × timing, AI group):**
- **Timing:** F(1.98, 43.66) = **13.94**, p = **.000022**, ges = **.253**
- **Structure:** F(1, 22) = 0.50, p = .485, ges = .011
- **Timing × structure:** F(1.98, 43.66) = 0.36, p = .701, ges = .009

**Pairwise timing differences (summary time):**
- Pre vs synchronous: Δ = **+32.2 sec**, p = .026  
- Pre vs post: Δ = **+63.0 sec**, p = .000105  
- Synchronous vs post: Δ = **+30.8 sec**, p = .026

Crucially, when you combine reading time + summary time, **total time is essentially constant** across timing conditions (≈ 531–536 seconds). Pre-reading mainly changes **where** time is spent (more summary time up-front, more efficient reading), rather than **how much** total time is spent.

**Interpretation:**  
The pre-reading advantage is not a “more time = better score” artifact; it is a **better time allocation + better encoding quality** effect.

![](all_plots/D2_summary_time_plot.png)

**Reading time (minutes; AI group)**

| Timing | Reading time (min; mean ± SD) |
|---|---:|
| Pre-reading | 6.72 ± 1.97 |
| Synchronous | 7.20 ± 2.78 |
| Post-reading | 7.69 ± 2.49 |

Mixed ANOVA indicates no reliable timing effect on reading time in the main analysis dataset: **F(1.96, 43.06) = 1.21, p = .308**.

![](all_plots/D3_reading_time_plot.png)

---

### 2.2 Summary Accuracy and Why Pre-Reading Works

Summary accuracy is substantially higher in pre-reading:
- **Pre vs synchronous:** Δ ≈ **+0.250**, p < **.001**
- **Pre vs post:** Δ ≈ **+0.165**, p ≈ **.002**

**Descriptives (AI group; mean ± SD, n = 24 per timing):**

| Timing | AI summary accuracy |
|---|---:|
| **Pre-reading** | **0.833 ± 0.141** |
| Synchronous | 0.568 ± 0.239 |
| Post-reading | 0.641 ± 0.196 |

When models include both **AI summary accuracy** and **article accuracy**, the timing coefficients shrink dramatically (timing effect is largely “explained” by these quality metrics). This supports the idea that pre-reading improves **how well learners encode both the summary and the article**, which in turn drives MCQ performance.

Methodological note: summary accuracy and MCQ share a common correctness signal, so this “explanation” is best interpreted as **shared variance in encoding quality**, not definitive causal mediation.

![](all_plots/timing_decomposition.png)

---

### 2.3 Mental Effort (Not a Confound)

Self-reported mental effort does **not** differ reliably by timing or structure, which helps rule it out as a confound. There is a small negative association between effort and MCQ (higher effort ↔ slightly lower MCQ), but because effort is not condition-dependent, it does not explain the timing or structure effects.

**Mixed ANOVA (structure × timing, AI group):**
- **Timing:** F(1.34, 29.37) = 0.81, p = .408
- **Structure:** F(1, 22) = 2.43, p = .133
- **Timing × structure:** F(1.34, 29.37) = 1.47, p = .242

![](all_plots/D1_mental_effort_plot.png)

---

### 2.4 Trust, Dependence, and “Who Benefits When”

Key moderator result:
- The **Trust × post-reading** interaction on MCQ survives Holm correction (high-trust participants benefit more from post-reading than low-trust participants).

Engagement pattern:
- **Higher trust → more time** spent with the summary.
- **Higher dependence → less time** spent with the summary (opposite direction to trust).

Interpretation:
- **Trust** may correspond to *active engagement*: learners inspect, evaluate, and integrate the summary.
- **Dependence** may correspond to *passive reliance*: learners accept AI output quickly (less time). Notably, dependence shows at most a **marginal** relationship with false lures in the full binomial lure model and does not reliably predict lures at the participant level.

---

## 3) Robustness and Sensitivity (Why the Main Conclusions Are Stable)

### 3.0 Design Robustness and Internal Validity Checks

These checks evaluate whether the experiment’s *design/assignment* and core *measurement choices* plausibly support the main causal claims (timing → MCQ; structure → false lures), rather than reflecting counterbalancing artifacts, missingness, or timing-specific confounds.

**Design integrity (AI group)**
- **N = 24 participants, 72 observations**; each participant contributes **exactly 3 trials** (one per timing) and sees **all 3 articles**.
- **Structure is balanced** at the participant level (**12 integrated**, **12 segmented**).

**Counterbalancing check (timing × article, AI group)**

| Timing | CRISPR | Semiconductors | UHI |
|---|---:|---:|---:|
| Pre-reading | 8 | 9 | 7 |
| Synchronous | 10 | 8 | 6 |
| Post-reading | 6 | 7 | 11 |

Chi-square independence test: **X²(4) = 3.00, p = .558** → article assignment does **not** appear to confound timing.

![](all_plots/EXP_fig_counterbalancing_timing_by_article.png)

**Moderator validity check (traits across within-subject timing)**
- Trust and dependence are measured once (participant-level) and therefore constant across timing; empirically, timing means are identical: **trust = 4.94**, **dependence = 5.15** in pre/synchronous/post.

**Time-on-task and measurement robustness**
- In the main analysis dataset, **total time (reading + summary) is essentially constant** across timing (~531–536 sec), consistent with a *sequencing/quality* explanation rather than a “more time” explanation.
- A log-derived correction file (`reading_time_corrected.csv`, **67 observations**) shows that the large “synchronous reading time” inflation in raw logs is largely an accounting artifact:  
  - **Original reading time (min):** pre = **6.13**, sync = **8.63**, post = **6.53**  
  - **Corrected reading time (min):** pre = **6.13**, sync = **6.61**, post = **6.53**

![](all_plots/EXP_fig_reading_time_original_vs_corrected.png)

**Assumption/sensitivity checks (supporting stability of inference)**
- False-lure models show **no substantial overdispersion** (ratio ≈ **0.80**, threshold 1.5).
- **No trials hit the reading-time cap** (n capped = **0**), reducing concerns about truncation artifacts.

### 3.1 MCQ Timing Effect Robustness

Evidence the pre-reading MCQ advantage is stable:
- **Random-slopes models** fit better but leave the timing estimates essentially unchanged.
- **Participant-level validation:** ~**83%** of participants show an individual pre-reading advantage on MCQ.
- **Leave-one-article-out:** the pre-reading advantage persists regardless of which article is removed.
- **Cross-validated prediction:** models that incorporate summary + article accuracy predict MCQ exceptionally well out-of-sample (high r, low RMSE), indicating the pattern is not fragile.

**Random-effects / specification sensitivity (pre vs synchronous, estimate scale = MCQ proportion):**

| Model specification | Pre–sync estimate | p |
|---|---:|---:|
| (1\|participant) + (1\|article) | 0.173 | 0.000004 |
| (1\|participant) only | 0.167 | 0.000123 |
| + article fixed effect | 0.173 | 0.000004 |

![](all_plots/ORD_plot1_mcq_by_timing.png)

### 3.2 False Lure Structure Effect Robustness

Evidence the structure effect is stable:
- Structure remains the dominant lure predictor across model families (binomial preferred to Poisson; conclusions align).
- **Model stability checks** show no separation issues and stable estimates under leave-one-participant-out.
- Profile-likelihood confidence intervals support a **non-trivial** structure effect (OR confidence interval excludes 1).

### 3.3 Multiple Comparisons Discipline

Many trait × timing interactions can look promising at raw p-values; after Holm correction, the “survivor” is the **trust moderation of post-reading MCQ**. The interpretation should prioritize this corrected result and treat the others as exploratory.

---

## 4) Interesting Relationships Across Variables (Integrated Interpretation)

### 4.1 Two Largely Independent Pathways

The data support two separable pathways:

1. **Timing → learning quality → MCQ**
   - Pre-reading improves *encoding quality* (summary + article accuracy), driving higher MCQ.

2. **Structure → representation coherence → false lures**
   - Segmentation increases *source confusion* and false-lure endorsement.

**Practical synthesis:**  
If you want both high performance and low misinformation risk, the “best” pairing is:
- **Pre-reading timing + integrated structure**

---

### 4.2 Pre-Reading Improves MCQ Even Though It Doesn’t “Fix” Lures

An important nuance: the timing manipulation strongly improves MCQ, but false-lure susceptibility remains primarily structure-driven. This means it is possible to **increase correct recognition** (MCQ) without proportionally reducing **misinformation acceptance** (false lures).

This is practically important: a UI that maximizes MCQ might still be unsafe if it presents summaries in a segmented way (or if summary factuality is not ensured).

---

### 4.3 Time Allocation Is a Feature, Not a Confound

Pre-reading increases summary time and tends to reduce/streamline reading time, while holding total time constant. This looks like a **better sequencing strategy**: learners invest in building a scaffold first, then read with a clearer target.

---

## 5) Focus Section: Pre-Reading Timing + False Lures (and Their Relationships With Other Variables)

This section isolates the two “headline” phenomena—**pre-reading timing** and **false lures**—and connects them to the rest of the measured variables.

### 5.1 What Pre-Reading Changes (Compared to Synchronous/Post)

**Direct outcomes**
- **MCQ:** pre-reading is best (large effect).
- **Recall:** unchanged (equivalence).

**Encoding-quality markers**
- **AI summary accuracy:** substantially higher in pre-reading than synchronous and post-reading (Δ ≈ +0.25 and +0.17, respectively).
- **Article accuracy:** does not show a reliable timing effect in the primary models, suggesting the main action is in how AI information is integrated with reading rather than in article-only comprehension per se.

**Process/time variables**
- **Summary time:** highest in pre-reading (learners actually use the summary when it’s shown before the article).
- **Total time:** essentially constant across timing conditions (so “pre-reading wins” is not because participants simply worked longer).

**Compact timing profile (AI group means)**

| Metric | Pre-reading | Synchronous | Post-reading |
|---|---:|---:|---:|
| MCQ accuracy | **0.699** | 0.533 | 0.562 |
| AI summary accuracy | **0.833** | 0.568 | 0.641 |
| Summary time (sec) | **132.5** | 100.3 | 69.5 |
| Reading time (min) | 6.72 | 7.20 | 7.69 |
| Total time (sec) | 535.9 | 532.5 | 530.8 |

**Moderator angle**
- Pre-reading is broadly beneficial, but **high-trust participants** also benefit more from post-reading than low-trust participants, reducing the *size* (not the direction) of the pre-reading advantage for them.

---

### 5.2 What Drives False Lures (and What Does *Not*)

**Strong driver**
- **Structure:** segmented presentation sharply increases lure endorsement.

**Not reliable drivers**
- **Timing:** does not reliably shift lure endorsement (main effect and interaction tests are not robust).
- **Time-on-task:** adding reading time / summary time does not remove the structure effect.
- **Mental effort:** does not explain lure differences.
- **Traits:** trust and dependence do not reliably predict lure susceptibility at the participant level (with dependence showing at most weak, model-dependent signals).

**Model-predicted lure probability by structure × timing** *(interpret cautiously; intervals are wide)*

| Structure | Pre-reading | Synchronous | Post-reading |
|---|---:|---:|---:|
| Integrated | 0.451 | 0.175 | 0.139 |
| Segmented | 0.440 | 0.570 | 0.613 |

**Model-based “shape” across timing (useful for intuition, not a primary claim):**
- In integrated format, lure probability is highest in pre-reading and lower in synchronous/post-reading.
- In segmented format, lure probability stays high (and may rise) in synchronous/post-reading.

**Interpretation:**  
False-lure susceptibility seems to be a **representation + source-monitoring** problem. Timing can change how much learners benefit for MCQ, but the *format* of the AI information changes whether learners can keep AI vs article content straight.

---

### 5.3 The Key Joint Insight (Why This Matters)

**Pre-reading is the best timing for learning performance, but it is not automatically the safest timing for misinformation.**  
If learners see the summary before having any article knowledge, they may have fewer internal checks available to reject plausible-sounding false claims—especially if the summary is segmented and harder to integrate.

**Design implication:**  
If you want to deploy pre-reading summaries (for learning benefits), you should also:
- Prefer **integrated** summary format, and
- Add **verification affordances** (citations, “show evidence in text”, uncertainty markers, or explicit “AI may be wrong” prompts) to reduce lure endorsement risk.

---

## 6) Practical Recommendations (Based on the Results)

### For interface/ed-tech design
- Default to **pre-reading** summaries when the goal is MCQ/recognition performance.
- Default to **integrated** summary presentation to reduce false-lure susceptibility.
- Treat **false lures** as a structural UI risk, not merely a “user trait” problem.

### For future iterations of the experiment
- Add delayed tests (24h / 1 week) to see whether pre-reading benefits persist and whether lure acceptance consolidates.
- Measure or manipulate summary factuality directly (high vs low accuracy summaries) to test the safety/performance trade-off more directly.
- Use process-tracing (eye-tracking, click-to-evidence, think-aloud) to isolate the source-monitoring mechanism behind segmentation.
