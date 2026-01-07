# New Findings Using trust_new / dependence_new (Post-block Ratings)

This summary reflects analyses rerun with `trust_new` and `dependence_new` mapped to
`ai_trust` and `ai_dependence` (post-reading, block-level ratings). Results come from
`final_analysis/run_long_format_analyses.R` and outputs in `final_analysis/long_format_outputs/`.

Method note (mixed design):
- All Structure × Timing tests are run as mixed-effects models (not a naïve 2-way between-subject ANOVA), e.g.
  `lmer(dv ~ structure * timing + (1|participant_id) + (1|article))`, which treats timing as within-subject and structure as between-subject.

## 1) Condition Effects on Trust/Dependence (AI only)

Mixed ANOVA (structure x timing; random intercepts for participant and article):

- Trust: timing F(2, 43) = 7.90, p = .001; structure p = .222; interaction p = .194.
- Dependence: structure F(1, 22) = 6.21, p = .021; timing F(2, 43) = 7.74, p = .001; interaction p = .559.

Post-hoc timing contrasts (Holm-corrected):
- Pre-reading > synchronous and post-reading for both trust and dependence.
- Synchronous vs post-reading is ns for both.

Condition means (trust / dependence):
- Integrated, pre-reading: 4.17 / 4.25
- Integrated, synchronous: 3.58 / 3.83
- Integrated, post-reading: 3.92 / 3.67
- Segmented, pre-reading: 4.83 / 5.33
- Segmented, synchronous: 4.17 / 4.50
- Segmented, post-reading: 4.00 / 4.58

Collapsed means by structure (descriptive):
- Integrated: trust 3.89; dependence 3.92
- Segmented: trust 4.33; dependence 4.81

Sources:
- `final_analysis/long_format_outputs/tables/A1_anova_ai_trust.csv`
- `final_analysis/long_format_outputs/tables/A1_anova_ai_dependence.csv`
- `final_analysis/long_format_outputs/tables/A1_posthoc_timing_ai_trust.csv`
- `final_analysis/long_format_outputs/tables/A1_posthoc_timing_ai_dependence.csv`
- `final_analysis/long_format_outputs/tables/A1_descriptives_ai_trust.csv`
- `final_analysis/long_format_outputs/tables/A1_descriptives_ai_dependence.csv`

## 2) Participant-level Regressions (AI only)

Mean outcomes regressed on trust, dependence, prior knowledge:
- Mean MCQ: trust p = .585, dependence p = .283 (ns).
- Mean summary accuracy: trust p = .154, dependence p = .971 (ns); prior knowledge negative, p = .041.
- Mean false lures: trust p = .828, dependence p = .730 (ns).

Sources:
- `final_analysis/long_format_outputs/tables/E1_mean_mcq_coefficients.csv`
- `final_analysis/long_format_outputs/tables/E1_mean_ai_summary_accuracy_coefficients.csv`
- `final_analysis/long_format_outputs/tables/E1_mean_false_lures_selected_coefficients.csv`

## 3) Timing Moderation (AI only)

Timing x trust/dependence interactions are no longer reliable with the new measures:
- Summary accuracy: trust p = .296; dependence p = .665.
- MCQ accuracy: trust p = .073; dependence p = .847.

Source:
- `final_analysis/long_format_outputs/report.txt` (Section E)

## 4) Exploratory Within/Between-person Effects (AI only)

Within-person (block-to-block) deviations vs between-person averages:
- dep_within -> higher summary accuracy (p = .026).
- dep_within -> marginal MCQ gain (p = .062).
- dep_mean -> less reading time (p = .010).
- dep_mean -> marginally less summary time (p = .057).
- Trust and dependence covary between participants (trust_mean <-> dep_mean p = .009); within-person coupling is ns (p = .167).
- Summary-time proportion is not predicted by trust/dependence in within/between models (all p > .65).

Sources:
- `final_analysis/long_format_outputs/tables/E0_ai_summary_accuracy_within_between_fixed_effects.csv`
- `final_analysis/long_format_outputs/tables/E0_mcq_accuracy_within_between_fixed_effects.csv`
- `final_analysis/long_format_outputs/tables/E0_reading_time_min_within_between_fixed_effects.csv`
- `final_analysis/long_format_outputs/tables/E0_summary_time_sec_within_between_fixed_effects.csv`
- `final_analysis/long_format_outputs/tables/E0_summary_prop_within_between_fixed_effects.csv`
- `final_analysis/long_format_outputs/tables/E0b_ai_dependence_from_trust_fixed_effects.csv`
- `final_analysis/long_format_outputs/tables/E0b_ai_trust_from_dependence_fixed_effects.csv`
- `final_analysis/long_format_outputs/tables/E0c_false_lures_selected_trust_dependence_fixed_effects.csv`
- `final_analysis/long_format_outputs/tables/E0c_false_lure_accuracy_trust_dependence_fixed_effects.csv`

## 5) Suggested Interpretation (if included in report)

- Pre-reading raises both trust and dependence relative to the other timings, consistent with
  greater perceived reliance when summaries appear before reading.
- Segmented increases dependence without increasing trust, so a "segmented -> excessive trust"
  interpretation is not supported with the post-block measures.
- Dependence appears to track reliance/efficiency: higher dependence (between-person) is linked
  to less reading time, while higher dependence within a block aligns with higher summary accuracy.
- These E0 results are exploratory and not multiple-comparison corrected; treat as tentative.

## 6) Reporting Decision (based on your criteria)

- The section should be redone: `trust_new`/`dependence_new` change the construct from a single trait to a post-block state, and the old `ai_trust`/`ai_dependence` findings do not carry over.
- **“Segmented trust is higher → excessive trust → misled”**: not supported (structure effect on trust is ns; no evidence this maps onto false lures).
- **“Pre-reading and segmented dependence are higher → explains summary accuracy differences”**: dependence is higher in both pre-reading and segmented, but summary accuracy shows a strong timing effect and no structure effect; dependence does not reliably moderate timing on summary accuracy. At most, report this as descriptive/exploratory (E0 dep-within association), not as a confirmed explanation.

Data completeness note:
- `trust_new`/`dependence_new` are present for all AI rows; the only missing values are the NoAI group (expected).

## 7) Hypothesis Checks (based on your new methodology)

- “Integrated users trust AI more than segmented because they notice false lures in bullets”: not supported by these data (trust is descriptively higher in segmented, and the structure effect on trust is ns).
- “If they trust less, they depend less”: supported between participants (trust_mean <-> dep_mean p = .009), but not as a within-person block-to-block effect (p = .167).
- “Pre-reading dependence is higher and matches time-allocation”: supported descriptively (pre-reading produces the highest trust and dependence, and summary-time proportion is also highest in pre-reading), but dependence does not statistically predict summary-time proportion in the within/between models (all p > .65).
- Summary-time proportion means (AI only): pre ≈ 0.25, synchronous ≈ 0.19–0.20, post ≈ 0.13–0.14 (`final_analysis/long_format_outputs/tables/A1_descriptives_summary_prop.csv`; timing effect: `final_analysis/long_format_outputs/tables/A1_anova_summary_prop.csv`).
- “Over-trust explains being misled”: not supported here; trust/dependence do not predict false lures selected (p = .767/.841). (There is a directional hint: trust +, dependence - for false-lure accuracy, p = .152/.121; treat as exploratory.)

## 8) Report-Ready Insert (redo)

**Secondary Finding (subjective reliance): Post-block trust and dependence track timing, and dependence (not trust) is higher in segmented.**

“Because trust and dependence were assessed \emph{after each reading block} (post-block states rather than pre-task traits), we examined whether perceived reliance varied across the six AI assistance conditions using mixed-effects models that respect the mixed design (structure = between-subjects; timing = within-subjects; random intercepts for participant and article). Trust varied by timing, with higher ratings in the pre-reading condition than synchronous or post-reading (timing: $F(2,43)=7.90$, $p=.001$; structure ns). Dependence showed the same timing pattern and was also higher overall in the segmented structure (timing: $F(2,43)=7.74$, $p=.001$; structure: $F(1,22)=6.21$, $p=.021$). This subjective pattern converges with the process evidence: summary-time proportion was highest in pre-reading (timing: $F(2,43)=16.20$, $p<.001$), consistent with pre-reading summaries being used as a stronger scaffold. However, trust/dependence did not reliably explain misinformation susceptibility (false lures selected was not predicted by trust or dependence), so these ratings are best interpreted as markers of experienced reliance rather than a mechanism for being misled.”

Where it connects to main findings:
- Supports Main Finding 3 (pre-reading increases summary engagement / summary share).
- Complements Main Finding 1 (timing advantage) by showing higher perceived reliance in pre-reading.
- Boundary condition for Main Finding 2 (structure effect on misinformation): do not frame the false-lure effect as “over-trust” with these measures.

## 9) Relevant Plots

- Condition means (structure × timing): `final_analysis/long_format_outputs/plots/A1_plot_ai_trust.png`, `final_analysis/long_format_outputs/plots/A1_plot_ai_dependence.png`, `final_analysis/long_format_outputs/plots/A1_plot_summary_prop.png`
- Report copies: `Final result/report_assets/A1_plot_ai_trust.png`, `Final result/report_assets/A1_plot_ai_dependence.png`, `Final result/report_assets/A1_plot_summary_prop.png`
