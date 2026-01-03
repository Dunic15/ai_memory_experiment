# COMPREHENSIVE ANALYSIS REPORT
## AI Memory Experiment - Statistical Results

**Generated:** January 2, 2026  
**Data:** Long format (1 row = 1 participant × 1 trial)  
**AI group:** 24 participants, 72 observations  
**NoAI group:** 12 participants, 36 observations

**Design summary:**
- AI group: within-subject timing manipulation (3 trials: pre-reading, synchronous, post-reading), between-subject structure (integrated vs segmented)
- NoAI group: no timing manipulation; reading only (control comparison)

---

# TABLE OF CONTENTS

1. [Core Findings: Timing Effects (AI only)](#timing-effects)
2. [Core Findings: Structure → False Lures](#false-lures)
3. [Null Effects (Interpretable)](#null-effects)
4. [Process Variables](#process-variables)
5. [Key Robustness Checks](#robustness)
6. [Appendix: Additional Detail](#appendix)

---

<a name="timing-effects"></a>
# 1. CORE FINDINGS: TIMING EFFECTS ON MCQ (AI only)

**Design:** 2×3 mixed ANOVA (Structure: between; Timing: within)

## Main Effect of Timing

| Effect | F | df | p | η²(ges) |
|--------|---|----|----|---------|
| **Timing** | 11.77 | 1.77, 38.87 | **<.001** | .254 |
| Structure | 4.69 | 1, 22 | .042 | .072 |
| Interaction | 0.76 | 1.77, 38.87 | .461 | .021 |

**Post-hoc contrasts (Holm-corrected):**
| Contrast | Δ | Effect Size (d) | p |
|----------|---|-----------------|---|
| **Pre-reading vs Synchronous** | **0.167** | **1.62** | **.002** |
| **Pre-reading vs Post-reading** | **0.137** | **1.35** | **.003** |
| Synchronous vs Post-reading | -0.030 | 0.28 | .334 |

**MCQ was highest in pre-reading across models and descriptives** (estimated marginal means: Pre ≈ 0.70, Post ≈ 0.56, Sync ≈ 0.53).

✅ **Pre-reading timing is optimal for MCQ accuracy**  
✅ **Effect persists after controlling for total time-on-task** (not a confound)

---

<a name="false-lures"></a>
# 2. CORE FINDINGS: STRUCTURE → FALSE LURES (AI only)

**Definitive binomial model** (controlling for timing, summary accuracy, article accuracy, trust, dependence, time, and effort):

| Predictor | OR | 95% CI | p |
|-----------|-----|--------|---|
| **Structure (segmented)** | **5.93** | **[1.63, 21.5]** | **.007** |
| Dependence | 0.49 | [0.22, 1.09] | .080 |

No evidence that timing, time-on-task, effort, summary accuracy, or trust predicted lures in the full model (all p > .10).

**Predicted lure probability by structure:**
| Structure | Probability | 95% CI |
|-----------|-------------|--------|
| Integrated | 0.26 | [0.14, 0.43] |
| Segmented | 0.54 | [0.36, 0.70] |

✅ **Segmented structure increases false lure selection** (OR = 5.9, p = .007)  
❌ **Timing does NOT affect false lures** — structure is the only significant predictor

---

<a name="null-effects"></a>
# 3. NULL EFFECTS (Interpretable)

## 4A. Timing does NOT affect Recall

| Timing | EMM | 95% CI |
|--------|-----|--------|
| Pre-reading | 5.52 | [4.66, 6.37] |
| Synchronous | 5.58 | [4.72, 6.43] |
| Post-reading | 5.51 | [4.65, 6.36] |

**TOST Equivalence Test (SESOI = d = 0.30):**  
All contrasts are **EQUIVALENT** (all TOST p < .035)  
→ Timing does NOT affect recall; this is an interpretable null, not underpowered

## 4B. No AI vs NoAI Differences (Beyond MCQ)

| Outcome | AI EMM | NoAI EMM | Δ | p |
|---------|--------|----------|---|---|
| Recall | 5.53 | 5.40 | 0.13 | .834 |
| Article-only accuracy | 0.48 | 0.51 | -0.03 | .520 |

✅ **No group differences on recall or article-only accuracy**

---

<a name="process-variables"></a>
# 4. PROCESS VARIABLES

## 4A. Time-on-Task is NOT a Confound

Controlling for total time: **timing effects unchanged** (0% reduction)  
→ Pre-reading advantage is not simply due to spending more time

## 4B. Mental Effort as Marker (Not Cause)

Controlling for mental effort: **timing effects unchanged** (0% reduction)  
→ Effort does not drive timing effects

## 4C. Who Benefits? (Trait Moderation)

| Predictor | β | p (raw) | p (Holm) |
|-----------|---|---------|----------|
| **Trust × Timing(Pre-Post) on MCQ** | **-0.15** | **.002** | **.023** |
| Other trait × timing interactions | — | ns | ns |

✅ **Trust × Timing survives Holm correction** (1 of 12 tests)  
→ High-trust participants show smaller pre-reading advantage (they rely on AI regardless of timing)

---

<a name="robustness"></a>
# 5. KEY ROBUSTNESS CHECKS

## 5A. Random Slopes

**MCQ model comparison:** χ²(2) = 8.01, p = .018  
→ Random slopes model preferred, but **timing effects unchanged**

**Participant-level validation:**
- 83% of participants individually show pre-reading MCQ advantage
- Within-person t-test: t(23) = 3.98, p = .0006

## 5B. Leave-One-Article-Out

| Dropped | Pre-Sync Δ | p |
|---------|------------|---|
| Semiconductors | 0.172 | <.001 |
| UHI | 0.126 | .010 |
| CRISPR | 0.116 | .016 |

✅ **Timing effect robust across all article subsets**

## 5C. Model Family (False Lures)

| Model | AIC | Structure p |
|-------|-----|-------------|
| **Binomial** | **155** | **.026** |
| Poisson | 171 | .030 |

✅ **Binomial preferred (ΔAIC = 16); both agree structure is significant**  
✅ **No separation issues** (fitted probabilities range 0.10–0.82)

---

# ARTICLE DIFFERENCES (Stimulus Effects)

MCQ varied across articles; Semiconductors produced lower scores than CRISPR (Δ ≈ 0.145, p < .001) and UHI (Δ ≈ 0.121, p < .001). We treat this as a stimulus-specific difference and control for article in all models.

| Article | MCQ Mean |
|---------|----------|
| CRISPR | 0.625 |
| UHI | 0.601 |
| Semiconductors | 0.480 |

**No Timing × Article interaction** (p = .264)  
→ Timing effects are consistent across articles

---

# SUMMARY OF KEY FINDINGS

## Primary Effects
1. **Pre-reading timing is optimal for MCQ** (d = 1.35–1.62)
2. **Segmented structure increases false lure selection** (OR = 5.9)

## Null Effects (Interpretable)
3. **Timing does NOT affect recall** (TOST equivalence confirmed)
4. **No AI vs NoAI differences** on recall or article-only accuracy
5. **Timing does NOT affect false lures** — structure is the only driver

## Process Variables
6. **Time-on-task does NOT explain timing effect** (0% reduction when controlled)
7. **Mental effort does NOT explain timing effect** (0% reduction)
8. **Trust moderates who benefits** (high trust → smaller pre-reading advantage; survives Holm)

## Robustness
9. **All key findings robust to:** random slopes, leave-one-article-out, model family comparison

---

<a name="appendix"></a>
# APPENDIX: Additional Detail

*The following sections contain supplementary analyses available for review. See individual CSV tables for full results.*

## A1. Individual Differences

**Summary accuracy ~ Trust + Dependence + Prior Knowledge**
- Prior knowledge: β = -0.40, p = .049 (higher PK → lower summary accuracy; unexpected)

**Trust/Dependence → Time-on-Task:**
- High trust → more time on summaries (β = 37.2, p = .005)
- High dependence → less time on summaries (β = -41.6, p < .001)

## A2. Confidence Calibration

- Confidence-recall correlation: r = 0.04 (ns)
- No overconfidence difference between AI and NoAI groups (p = .873)

## A3. Additional Process Variables

**Summary time → Summary accuracy:** β = 0.06, p = .031  
→ Longer time with summary → better summary-based performance

**Recall → MCQ:** β = 0.003, p = .70 (ns)  
→ Recall and MCQ are independent measures

## A4. Nonlinearity Check

Spline models not better than log-linear (both p > .26)  
→ Simple log-transformation is sufficient

## A5. Counterbalancing & Design Checks

Timing × Article counterbalancing: χ²(4) = 3.0, p = .56  
→ Counterbalancing is adequate

One trial at reading time cap (excluded in sensitivity check; no effect on results).

---

# FILES

- **Scripts:** 10 R scripts in `scripts/`
- **Tables:** 162 CSV files in `all_tables/`
- **Plots:** 15 PNG files in `all_plots/`

**Key plots:**
- `ORD_plot1_mcq_by_timing.png` — MCQ accuracy by timing condition
- `ORD_plot2_lure_prob_by_structure.png` — False lure probability by structure
