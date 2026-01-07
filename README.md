# AI Memory Experiment (AI vs Control)

This repo contains two versions of the same reading/memory experiment (AI-enabled vs control/no-AI) plus analysis-ready datasets and scripts to reproduce the final ANOVAs.

## Thesis (project summary)

This project supports my thesis on how **AI-generated summaries** shape learning and memory during reading. Using a controlled, web-based experiment, participants read three scientific articles and complete both **free recall** and **multiple-choice (MCQ)** tests. The study compares an **AI** condition (summaries available) against a **NoAI** control and, within the AI condition, manipulates:

- **Timing** of summary access: `pre_reading`, `synchronous`, `post_reading`
- **Structure** of the summary: `integrated` vs `segmented`

**Research questions**
- **RQ1:** Does the timing of AI summary presentation affect learning outcomes?
- **RQ2:** Does summary structure affect susceptibility to misinformation (false lures)?
- **RQ3:** Do individual differences in AI trust/dependence moderate these effects?

For the final write-up assets, see:
- `Final result/EXPANDED_INTERPRETIVE_REPORT.md`
- `Final result/FINAL_INTEGRATED_REPORT.tex`
- Figures: `Final result/report_assets/`

Older/archival analysis notes live in `final_analysis/opus/`.
## Experiment Design (for analysis)

- **Control factor (between-subjects):** `experiment_group`
  - `AI` (AI summaries available)
  - `NoAI` (control; no AI summaries)

For the **AI group only** (the mixed-design ANOVAs):

- **Between-subjects factor:** `structure`
  - `integrated`
  - `segmented`
- **Within-subjects factor:** `timing`
  - `pre_reading` (Pre)
  - `synchronous` (Sync)
  - `post_reading` (After)

Each AI participant contributes **3 rows** (one per timing condition / article trial).

## Experiment Procedure (high level)

Participants complete a reading + memory test for **3 scientific articles** (article keys commonly include: `uhi`, `crispr`, `semiconductors`).

### Shared flow (AI + NoAI)

1. Consent + demographics
2. Prior knowledge questionnaire (familiarity/recognition/quiz; see raw logs/docs)
3. For each of 3 articles:
   - Read the article (timed)
   - Break
   - Free recall (timed) + confidence/difficulty ratings
   - MCQ test (timed) + confidence rating
   - Post-article ratings (e.g., mental effort, task difficulty)
4. Debrief

### AI-only additions

- AI trust / dependence / tech skill questionnaire
- AI summary exposure on each article trial, with:
  - **Structure** fixed per participant (`integrated` or `segmented`)
  - **Timing** counterbalanced across the 3 articles (`pre_reading`, `synchronous`, `post_reading`)
- AI-related manipulation check items (e.g., coherence/connectivity)

For the full web-app flow details, see `ai_experiment/README.md` and `no_ai_experiment/README.md`.

## Repository Layout

- `ai_experiment/` — AI-enabled experiment app (see `ai_experiment/README.md`)
- `no_ai_experiment/` — control/no-AI experiment app (see `no_ai_experiment/README.md`)
- `final_analysis/` — analysis-ready spreadsheets + scripts (outputs are regenerated)
- `Final result/` — final report assets (figures + report docs)

## Data Files

### Raw logs (trial-level)

- AI version logs: `ai_experiment/experiment_data/*_log.csv`
- Control version logs: `no_ai_experiment/experiment_data/*_log.csv`
- AI condition assignment record: `ai_experiment/experiment_data/condition_assignments.csv`
- Participant demographics: `ai_experiment/experiment_data/participants.csv`, `no_ai_experiment/experiment_data/participants.csv`

Note: some raw files include identifiable info (e.g., names in filenames/columns). Anonymize before sharing.

### Analysis-ready datasets (used for ANOVAs)

- **Wide (1 row per participant):** `final_analysis/analysis_wide_format.xlsx`
  - Key columns include: `participant_id`, `experiment_group`, `structure`, `total_mcq_accuracy`, `ai_summary_accuracy`, `false_lures_selected`, plus timing-specific columns like `pre_reading_mcq_accuracy`, etc.
- **Long (1 row per participant × timing/trial):** `final_analysis/Analysis long finals-.xlsx`
  - Sheet used by the ANOVA script is auto-detected (the sheet that contains the header row with `participant_id`)
  - Key columns include: `participant_id`, `experiment_group`, `structure`, `timing`, `mcq_accuracy`, `ai_summary_accuracy`, `false_lures_selected`, etc.
  - NoAI `mcq_accuracy` / `article_accuracy` values are synced to the raw log-derived MCQ accuracy per article

## Codebook (variables)

If you need a phase-by-phase schema of the raw log CSVs (all logged variables), the most complete references are:
- `ai_experiment/docs/DATA_GUIDE.md`
- `ai_experiment/docs/CSV_LOG_ANALYSIS_TUTORIAL.md`

Below is the codebook for the **analysis-ready** datasets used in `final_analysis/run_mixed_anovas.py` / `final_analysis/run_long_format_analyses.R`.

### Long dataset: `final_analysis/Analysis long finals*.xlsx` (trial-level; 1 row per participant × timing)

Columns:

| Column | Type / scale | Meaning |
|---|---|---|
| `participant_id` | ID string | Participant identifier |
| `experiment_group` | category | `AI` or `NoAI` |
| `structure` | category | `integrated` / `segmented` (AI) or `control` (NoAI) |
| `timing` | category | `pre_reading` / `synchronous` / `post_reading` (AI) or `control` (NoAI) |
| `article` | category | Article key for this trial (e.g., `uhi`, `crispr`, `semiconductors`) |
| `mcq_accuracy` | proportion (0–1) | Accuracy on all MCQs for this article trial |
| `ai_summary_accuracy` | proportion (0–1) | Accuracy on **AI-summary-sourced** questions for this article trial (only populated for `AI`) |
| `article_accuracy` | proportion (0–1) | Accuracy on **article-only** questions for this article trial |
| `false_lure_accuracy` | proportion (0–1) | Accuracy on false-lure questions (correct rejection) for this article trial |
| `false_lures_selected` | count (0–2) | Number of false-lure *options* selected for this article trial |
| `recall_total_score` | continuous | Total free-recall score for this article trial (scoring method defined in your scoring rubric) |
| `recall_confidence` | Likert (1–7) | Self-rated recall confidence |
| `reading_time_min` | minutes | Time spent reading the article |
| `summary_time_sec` | seconds | Time spent viewing the summary (pre/sync/post depending on `timing`) |
| `mental_effort` | Likert (1–7) | Self-rated mental effort |
| `prior_knowledge_familiarity` | Likert (1–7) | Prior knowledge familiarity score (participant-level; repeated across rows) |
| `ai_trust` | Likert (1–7) | AI trust score (participant-level; typically only meaningful for `AI`) |
| `ai_dependence` | Likert (1–7) | AI dependence score (participant-level; typically only meaningful for `AI`) |

### Wide dataset: `final_analysis/analysis_wide_format.xlsx` (participant-level; 1 row per participant)

**Identifiers & demographics**
- `participant_id`, `name`, `age`, `gender`, `native_language`, `profession`

**Group / condition variables**
- `experiment_group`: `AI` or `NoAI`
- `structure`: `integrated` / `segmented` (AI) or `control` (NoAI)

**Questionnaires / individual differences**
- `prior_knowledge_familiarity`: Likert (1–7)
- `ai_trust`, `ai_dependence`, `tech_skill`: Likert (1–7) (AI group)
- `manipulation_coherence`, `manipulation_connectivity`: Likert (1–7)

**Overall performance (aggregated across 3 article trials)**
- `total_mcq_accuracy`: proportion (0–1), over `total_mcq_questions` (42)
- `total_mcq_correct`: count of correct MCQs (0–42)
- `total_mcq_questions`: total MCQs answered (42)
- `ai_summary_accuracy`: mean of trial-level `ai_summary_accuracy` across the 3 trials (AI group)
- `article_only_accuracy`: mean of trial-level article-only accuracy across the 3 trials
- `false_lure_accuracy`: mean of trial-level `false_lure_accuracy` across the 3 trials
- `false_lures_selected`: total number of false-lure options selected across all trials (0–6)
- `false_lure_rate`: `false_lures_selected / 6` (proportion)
- `avg_recall_total_score`, `avg_recall_confidence`, `avg_recall_difficulty`
- `avg_reading_time_min`, `avg_summary_time_sec`, `avg_mental_effort`, `avg_task_difficulty`, `avg_mcq_confidence`

Note: `final_analysis/run_anovas.py` uses `total_mcq_accuracy` for the AI vs NoAI MCQ ANOVA.

**Timing-specific columns (one set per timing; values come from the trial assigned to that timing for that participant)**

For each timing prefix in `{pre_reading, synchronous, post_reading}`:
- `<timing>_article`: article key assigned to that timing for this participant
- `<timing>_mcq_accuracy`: proportion (0–1)
- `<timing>_ai_summary_accuracy`: proportion (0–1)
- `<timing>_article_accuracy`: proportion (0–1)
- `<timing>_false_lure_accuracy`: proportion (0–1)
- `<timing>_false_lures_selected`: count (0–2)
- `<timing>_recall_confidence`: Likert (1–7)
- `<timing>_reading_time_min`: minutes
- `<timing>_summary_time_sec`: seconds
- `<timing>_mental_effort`: Likert (1–7)

## How accuracy categories are defined (AI summary vs article-only vs false lure)

MCQ questions are categorized by their information source (AI summary vs article-only) and include dedicated false-lure questions.
For the exact mapping and computation logic, see:
- `ai_experiment/docs/CSV_LOG_ANALYSIS_TUTORIAL.md`
- `ai_experiment/data_analysis/analyze_participant.py`
- `ai_experiment/false_lure_mapping.json` (and `ai_experiment/data_analysis/false_lure_mapping.json`)

## Reproducing Analyses (after cleanup)

This repo is periodically “deep cleaned” to remove large, reproducible artifacts (e.g., local virtualenvs and generated plots/tables).

**Python env (optional)**
- Create a venv: `python3 -m venv .venv && source .venv/bin/activate`
- Install deps (needs network): `pip install -r ai_experiment/requirements.txt` (and/or `no_ai_experiment/requirements.txt`)

**R analyses (regenerates outputs)**
- Long-format mixed models + descriptives/plots: `Rscript final_analysis/run_long_format_analyses.R` (writes `final_analysis/long_format_outputs/`)
- Legacy ANOVA outputs: `Rscript final_analysis/run_mixed_anovas.R` (writes `final_analysis/anova_outputs/`)

Generated folders that may be absent (and are ignored by git):
- `final_analysis/long_format_outputs/`
- `final_analysis/anova_outputs/`
- `final_analysis/opus/all_plots/`, `final_analysis/opus/all_tables/`
- `report_assets/` (duplicate of `Final result/report_assets/`)
