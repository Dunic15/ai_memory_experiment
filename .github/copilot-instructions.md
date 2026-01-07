# Copilot Instructions for AI Memory Experiment

## Project Overview
- This repo contains two parallel web-based experiments: **AI-enabled** (`ai_experiment/`) and **control/no-AI** (`no_ai_experiment/`).
- The goal is to study how AI-generated summaries affect learning and memory, with detailed analysis scripts and final reports included.

## Architecture & Data Flow
- **Experiment Apps:** Flask-based web apps (`app.py` for AI, `app_control.py` for control) run independently.
- **Data Logging:** Each experiment saves participant data to its own `experiment_data/` folder.
- **Analysis:** Python scripts in `data_analysis/` process raw data and generate participant-level reports (`*_ANALYSIS.txt`).
- **Final Analysis:** Integrated results and statistical analyses are in `final_analysis/` and `Final result/`.

## Developer Workflows
- **Run AI Experiment:**
  ```bash
  cd ai_experiment
  flask --app app.py run
  ```
- **Run Control Experiment:**
  ```bash
  cd no_ai_experiment
  flask --app app_control.py run
  ```
- **Analyze Participant Data:**
  ```bash
  cd ai_experiment/data_analysis
  python3 analyze_participant.py P064
  ```
  (Replace `P064` with any participant ID)

## Key Patterns & Conventions
- **Participant Analysis:** Each participant gets a `{ID}_ANALYSIS.txt` file with MCQ accuracy, reading times, recall, and recommendations.
- **AI Condition:** Manipulates summary timing (`pre_reading`, `synchronous`, `post_reading`) and structure (`integrated`, `segmented`).
- **Control Condition:** No AI summaries or related questions; flow is otherwise parallel.
- **Analysis Scripts:** Designed for CLI use; outputs are text files for review and inclusion/exclusion decisions.
- **Data Quality:** Scripts include recommendations for data inclusion/exclusion based on validity checks.

## Integration Points
- **AI summaries:** Only present in `ai_experiment/` (see summary logic in `app.py`).
- **False Lure Mapping:** Shared JSON files (`false_lure_mapping.json`) for misinformation analysis.
- **Final Reports:** See `Final result/EXPANDED_INTERPRETIVE_REPORT.md` and `final_analysis/opus/COMPREHENSIVE_FINAL_ANALYSIS_REPORT.md` for integrated findings.

## External Dependencies
- **Flask** for web apps
- **Python 3** for all scripts
- **No database:** All data is file-based (JSON, TXT, CSV)

## Example: Adding a New Analysis
- Place new scripts in the relevant `data_analysis/` folder.
- Follow the CLI pattern: `python3 <script>.py <PARTICIPANT_ID>`
- Output should be a text file named `{PARTICIPANT_ID}_ANALYSIS.txt`.

## References
- For experiment logic: `ai_experiment/app.py`, `no_ai_experiment/app_control.py`
- For analysis: `ai_experiment/data_analysis/analyze_participant.py`, `no_ai_experiment/data_analysis/analyze_participant.py`
- For final reports: `Final result/EXPANDED_INTERPRETIVE_REPORT.md`, `final_analysis/opus/COMPREHENSIVE_FINAL_ANALYSIS_REPORT.md`

---
**Update this file as project conventions evolve.**
