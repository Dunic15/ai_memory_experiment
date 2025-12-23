#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd

TIMINGS = ("pre_reading", "synchronous", "post_reading")
TIMING_SET = set(TIMINGS)

CORRECT_SOURCE_MAP: Dict[str, Dict[int, str]] = {
    "crispr": {
        0: "ai_summary",
        1: "ai_summary",
        2: "false_lure",
        3: "ai_summary",
        4: "ai_summary",
        5: "ai_summary",
        6: "ai_summary",
        7: "ai_summary",
        8: "article",
        9: "ai_summary",
        10: "article",
        11: "article",
        12: "article",
        13: "false_lure",
    },
    "semiconductors": {
        0: "ai_summary",
        1: "ai_summary",
        2: "ai_summary",
        3: "ai_summary",
        4: "ai_summary",
        5: "ai_summary",
        6: "ai_summary",
        7: "article",
        8: "false_lure",
        9: "ai_summary",
        10: "false_lure",
        11: "article",
        12: "article",
        13: "article",
    },
    "uhi": {
        0: "ai_summary",
        1: "ai_summary",
        2: "ai_summary",
        3: "false_lure",
        4: "ai_summary",
        5: "ai_summary",
        6: "ai_summary",
        7: "ai_summary",
        8: "ai_summary",
        9: "article",
        10: "false_lure",
        11: "article",
        12: "article",
        13: "article",
    },
}

FALSE_LURE_OPTIONS: Dict[str, Dict[int, int]] = {
    "crispr": {2: 1, 13: 0},
    "semiconductors": {8: 0, 10: 1},
    "uhi": {3: 2, 10: 2},
}


def safe_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    s = str(value).strip()
    if s == "":
        return None
    try:
        return float(s)
    except Exception:
        return None


def safe_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    s = str(value).strip()
    if s == "":
        return None
    try:
        return int(float(s))
    except Exception:
        return None


def safe_json_load(value: Any) -> Optional[Any]:
    if value is None:
        return None
    s = str(value).strip()
    if not s or s[0] not in "{[":
        return None
    try:
        return json.loads(s)
    except Exception:
        return None


def detect_pid_from_filename(path: Path) -> Optional[str]:
    m = re.match(r"^(P\d+)", path.name)
    return m.group(1) if m else None


def parse_recall_scores(tsv_path: Path) -> Dict[str, float]:
    scores: Dict[str, float] = {}
    if not tsv_path.exists():
        return scores
    with tsv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            pid = (row.get("Participant ID") or "").strip()
            raw = (row.get("Recall Score") or "").strip()
            if not pid or not raw or raw.lower() == "nan":
                continue
            try:
                scores[pid] = float(raw)
            except Exception:
                continue
    return scores


@dataclass(frozen=True)
class TimingMap:
    article_order: List[str]
    timing_order: List[str]

    def timing_for_article_num(self, article_num: int) -> Optional[str]:
        if 0 <= article_num < len(self.timing_order):
            t = str(self.timing_order[article_num])
            return t if t in TIMING_SET else None
        return None

    def article_for_article_num(self, article_num: int) -> Optional[str]:
        if 0 <= article_num < len(self.article_order):
            return str(self.article_order[article_num])
        return None


def extract_ai_randomization(rows: Iterable[List[str]]) -> Optional[Tuple[str, TimingMap]]:
    for row in rows:
        if len(row) > 1 and row[1] == "randomization":
            structure = (row[2] or "").strip().lower()
            timing_order = safe_json_load(row[4]) if len(row) > 4 else None
            article_order = safe_json_load(row[9]) if len(row) > 9 else None
            if isinstance(timing_order, list) and isinstance(article_order, list):
                return structure, TimingMap(
                    article_order=[str(x) for x in article_order],
                    timing_order=[str(x) for x in timing_order],
                )
    return None


def extract_noai_article_order(rows: Iterable[List[str]]) -> Optional[List[str]]:
    for row in rows:
        if len(row) > 1 and row[1] == "randomization":
            article_order = safe_json_load(row[2]) if len(row) > 2 else None
            if isinstance(article_order, list):
                return [str(x) for x in article_order]
    return None


def find_question_accuracy_obj(row: List[str]) -> Optional[Dict[str, Any]]:
    for cell in row:
        obj = safe_json_load(cell)
        if not isinstance(obj, dict) or "q0" not in obj:
            continue
        q0 = obj.get("q0")
        if isinstance(q0, dict) and "is_correct" in q0:
            return obj
    return None


def compute_mcq_metrics(article_key: str, question_accuracy: Dict[str, Any]) -> Dict[str, Any]:
    total_questions = 0
    total_correct = 0

    ai_summary_total = 0
    ai_summary_correct = 0
    article_total = 0
    article_correct = 0
    false_lure_total = 0
    false_lure_correct = 0
    false_lures_selected = 0

    for qk, qinfo in question_accuracy.items():
        if not isinstance(qinfo, dict):
            continue

        q_idx = qinfo.get("question_index")
        if q_idx is None:
            m = re.match(r"q(\d+)$", str(qk))
            q_idx = int(m.group(1)) if m else None
        try:
            q_idx = int(q_idx)
        except Exception:
            continue

        is_correct = bool(qinfo.get("is_correct"))
        participant_answer = qinfo.get("participant_answer")
        try:
            participant_answer = int(participant_answer) if participant_answer is not None else None
        except Exception:
            participant_answer = None

        total_questions += 1
        if is_correct:
            total_correct += 1

        q_type = CORRECT_SOURCE_MAP.get(article_key, {}).get(q_idx)
        if q_type == "ai_summary":
            ai_summary_total += 1
            if is_correct:
                ai_summary_correct += 1
        elif q_type == "article":
            article_total += 1
            if is_correct:
                article_correct += 1
        elif q_type == "false_lure":
            false_lure_total += 1
            if is_correct:
                false_lure_correct += 1
            lure_opt = FALSE_LURE_OPTIONS.get(article_key, {}).get(q_idx)
            if lure_opt is not None and participant_answer == lure_opt:
                false_lures_selected += 1

    def div(n: int, d: int) -> Optional[float]:
        return (n / d) if d else None

    return {
        "mcq_total_questions": total_questions,
        "mcq_total_correct": total_correct,
        "mcq_overall_accuracy": div(total_correct, total_questions),
        "mcq_ai_summary_accuracy": div(ai_summary_correct, ai_summary_total),
        "mcq_article_only_accuracy": div(article_correct, article_total),
        "mcq_false_lure_accuracy": div(false_lure_correct, false_lure_total),
        "false_lures_selected_number": false_lures_selected,
        "ai_summary_correct": ai_summary_correct,
        "ai_summary_total": ai_summary_total,
        "article_only_correct": article_correct,
        "article_only_total": article_total,
        "false_lure_correct": false_lure_correct,
        "false_lure_total": false_lure_total,
    }


def parse_ai_log(path: Path, recall_scores: Dict[str, float]) -> pd.DataFrame:
    pid = detect_pid_from_filename(path)
    if not pid:
        return pd.DataFrame()

    rows = list(csv.reader(path.open("r", encoding="utf-8", newline="")))
    if len(rows) <= 1:
        return pd.DataFrame()
    data_rows = rows[1:]

    rand = extract_ai_randomization(data_rows)
    if rand is None:
        return pd.DataFrame()
    structure, timing_map = rand

    trust = None
    dependence = None
    for row in data_rows:
        if len(row) > 1 and row[1] == "ai_trust":
            trust = safe_float(row[2]) if len(row) > 2 else None
            dependence = safe_float(row[4]) if len(row) > 4 else None
            break

    reading_ms: Dict[int, int] = {}
    summary_sec: Dict[int, float] = {}
    mental_effort: Dict[int, int] = {}
    mcq_by_article_num: Dict[int, Dict[str, Any]] = {}

    for row in data_rows:
        if len(row) < 2:
            continue
        phase = row[1]
        if phase == "reading_behavior" and len(row) > 2 and row[2] == "reading_complete":
            a_num = safe_int(row[8]) if len(row) > 8 else None
            if a_num is None:
                continue
            reading_ms[a_num] = safe_int(row[4]) or 0
        elif phase == "summary_viewing":
            a_num = safe_int(row[2]) if len(row) > 2 else None
            if a_num is None:
                continue
            sec = safe_float(row[7]) if len(row) > 7 else None
            if sec is not None:
                summary_sec[a_num] = float(sec)
        elif phase == "post_article_ratings":
            a_num = safe_int(row[2]) if len(row) > 2 else None
            if a_num is None:
                continue
            me = safe_int(row[5]) if len(row) > 5 else None
            if me is not None:
                mental_effort[a_num] = int(me)
        elif phase == "mcq_responses":
            a_num = safe_int(row[2]) if len(row) > 2 else None
            if a_num is None:
                continue
            article_key = (row[3] or "").strip() if len(row) > 3 else ""
            if article_key not in CORRECT_SOURCE_MAP:
                inferred = timing_map.article_for_article_num(a_num)
                if inferred:
                    article_key = inferred
            qa = find_question_accuracy_obj(row)
            if qa and article_key in CORRECT_SOURCE_MAP:
                mcq_by_article_num[a_num] = compute_mcq_metrics(article_key, qa)

    records: List[Dict[str, Any]] = []
    for a_num in range(3):
        article_key = timing_map.article_for_article_num(a_num)
        timing = timing_map.timing_for_article_num(a_num)
        if not article_key or timing not in TIMING_SET:
            continue

        rt_ms = reading_ms.get(a_num)
        rt_min = (rt_ms / 60000.0) if rt_ms is not None else None
        sum_s = summary_sec.get(a_num)

        sum_pct = None
        if sum_s is not None and rt_ms is not None:
            denom = float(sum_s) + float(rt_ms) / 1000.0
            sum_pct = (float(sum_s) / denom * 100.0) if denom > 0 else None

        mcq = mcq_by_article_num.get(a_num, {})

        records.append(
            {
                "participant_id": pid,
                "experiment": "ai",
                "structure": structure,
                "article_num": a_num,
                "article_key": article_key,
                "timing": timing,
                "reading_time_min": rt_min,
                "summary_time_sec": sum_s,
                "summary_reading_pct": sum_pct,
                "mental_effort": mental_effort.get(a_num),
                "ai_trust": trust,
                "ai_dependence": dependence,
                "recall_total_score": recall_scores.get(pid),
                **mcq,
            }
        )
    return pd.DataFrame.from_records(records)


def parse_noai_log(path: Path, recall_scores: Dict[str, float]) -> pd.DataFrame:
    pid = detect_pid_from_filename(path)
    if not pid:
        return pd.DataFrame()

    rows = list(csv.reader(path.open("r", encoding="utf-8", newline="")))
    if len(rows) <= 1:
        return pd.DataFrame()
    data_rows = rows[1:]

    article_order = extract_noai_article_order(data_rows)
    if not article_order:
        return pd.DataFrame()

    reading_ms: Dict[int, int] = {}
    mental_effort: Dict[int, int] = {}
    mcq_by_article_num: Dict[int, Dict[str, Any]] = {}

    for row in data_rows:
        if len(row) < 2:
            continue
        phase = row[1]
        if phase == "reading_behavior" and len(row) > 2 and row[2] == "reading_complete":
            a_num = safe_int(row[6]) if len(row) > 6 else None
            if a_num is None:
                continue
            reading_ms[a_num] = safe_int(row[4]) or 0
        elif phase == "post_article_ratings":
            a_num = safe_int(row[2]) if len(row) > 2 else None
            if a_num is None:
                continue
            me = safe_int(row[4]) if len(row) > 4 else None
            if me is not None:
                mental_effort[a_num] = int(me)
        elif phase == "mcq_responses":
            a_num = safe_int(row[2]) if len(row) > 2 else None
            if a_num is None:
                continue
            article_key = article_order[a_num] if 0 <= a_num < len(article_order) else None
            if not article_key or article_key not in CORRECT_SOURCE_MAP:
                continue
            qa = find_question_accuracy_obj(row)
            if qa:
                mcq_by_article_num[a_num] = compute_mcq_metrics(article_key, qa)

    records: List[Dict[str, Any]] = []
    for a_num in range(3):
        article_key = article_order[a_num] if 0 <= a_num < len(article_order) else None
        if not article_key:
            continue
        timing = TIMINGS[a_num]  # position-as-timing for NoAI

        rt_ms = reading_ms.get(a_num)
        rt_min = (rt_ms / 60000.0) if rt_ms is not None else None
        mcq = mcq_by_article_num.get(a_num, {})

        records.append(
            {
                "participant_id": pid,
                "experiment": "no_ai",
                "structure": "non_ai",
                "article_num": a_num,
                "article_key": article_key,
                "timing": timing,
                "reading_time_min": rt_min,
                "summary_time_sec": None,
                "summary_reading_pct": None,
                "mental_effort": mental_effort.get(a_num),
                "ai_trust": None,
                "ai_dependence": None,
                "recall_total_score": recall_scores.get(pid),
                **mcq,
            }
        )
    return pd.DataFrame.from_records(records)


def participant_overall(df_long: pd.DataFrame) -> pd.DataFrame:
    def div(n: float, d: float) -> Optional[float]:
        return (float(n) / float(d)) if d else None

    rows: List[Dict[str, Any]] = []
    for (pid, exp, struct), g in df_long.groupby(["participant_id", "experiment", "structure"], dropna=False):
        total_correct = g["mcq_total_correct"].sum(min_count=1)
        total_q = g["mcq_total_questions"].sum(min_count=1)
        ai_c = g["ai_summary_correct"].sum(min_count=1)
        ai_t = g["ai_summary_total"].sum(min_count=1)
        art_c = g["article_only_correct"].sum(min_count=1)
        art_t = g["article_only_total"].sum(min_count=1)
        fl_c = g["false_lure_correct"].sum(min_count=1)
        fl_t = g["false_lure_total"].sum(min_count=1)
        fl_sel = g["false_lures_selected_number"].sum(min_count=1)

        rt_min = g["reading_time_min"].sum(min_count=1)
        sum_sec = g["summary_time_sec"].sum(min_count=1)
        sum_pct = None
        if pd.notna(sum_sec) and pd.notna(rt_min):
            denom = float(sum_sec) + float(rt_min) * 60.0
            sum_pct = (float(sum_sec) / denom * 100.0) if denom > 0 else None

        rows.append(
            {
                "participant_id": pid,
                "experiment": exp,
                "structure": struct,
                "mcq_overall_accuracy_overall": div(total_correct, total_q) if pd.notna(total_correct) and pd.notna(total_q) else None,
                "mcq_ai_summary_accuracy_overall": div(ai_c, ai_t) if pd.notna(ai_c) and pd.notna(ai_t) else None,
                "mcq_article_only_accuracy_overall": div(art_c, art_t) if pd.notna(art_c) and pd.notna(art_t) else None,
                "mcq_false_lure_accuracy_overall": div(fl_c, fl_t) if pd.notna(fl_c) and pd.notna(fl_t) else None,
                "false_lures_selected_number_overall": float(fl_sel) if pd.notna(fl_sel) else None,
                "reading_time_min_overall": float(rt_min) if pd.notna(rt_min) else None,
                "summary_time_sec_overall": float(sum_sec) if pd.notna(sum_sec) else None,
                "summary_reading_pct_overall": sum_pct,
                "mental_effort_overall": g["mental_effort"].mean(),
                "ai_trust": g["ai_trust"].dropna().iloc[0] if g["ai_trust"].notna().any() else None,
                "ai_dependence": g["ai_dependence"].dropna().iloc[0] if g["ai_dependence"].notna().any() else None,
                "recall_total_score": g["recall_total_score"].dropna().iloc[0] if g["recall_total_score"].notna().any() else None,
            }
        )
    return pd.DataFrame.from_records(rows)


def mean_table(df_long: pd.DataFrame, metric_col: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    ai = df_long[df_long["experiment"] == "ai"]
    noai = df_long[df_long["experiment"] == "no_ai"]
    ai_p = (
        ai.pivot_table(index="structure", columns="timing", values=metric_col, aggfunc="mean")
        .reindex(index=["integrated", "segmented"], columns=list(TIMINGS))
    )
    no_p = (
        noai.pivot_table(index="structure", columns="timing", values=metric_col, aggfunc="mean")
        .reindex(index=["non_ai"], columns=list(TIMINGS))
    )
    return ai_p, no_p


def fmt_num(x: Any, decimals: int = 4) -> str:
    if x is None or (isinstance(x, float) and (math.isnan(x) or pd.isna(x))):
        return ""
    try:
        return f"{float(x):.{decimals}f}"
    except Exception:
        return ""


def fmt_min(x: Any) -> str:
    return fmt_num(x, decimals=2)


def build_markdown(df_long: pd.DataFrame, df_wide: Optional[pd.DataFrame] = None) -> str:
    lines: List[str] = []

    def emit(title: str, metric: str, formatter):
        ai_p, no_p = mean_table(df_long, metric)
        lines.append(f"## {title}")
        lines.append("")
        lines.append("| Group | pre_reading | synchronous | post_reading |")
        lines.append("|---|---:|---:|---:|")
        for struct in ["integrated", "segmented"]:
            row = ai_p.loc[struct] if struct in ai_p.index else None
            vals = [formatter(row.get(t)) if row is not None else "" for t in TIMINGS]
            lines.append(f"| AI {struct} | {vals[0]} | {vals[1]} | {vals[2]} |")
        row = no_p.loc["non_ai"] if "non_ai" in no_p.index else None
        vals = [formatter(row.get(t)) if row is not None else "" for t in TIMINGS]
        lines.append(f"| NoAI | {vals[0]} | {vals[1]} | {vals[2]} |")
        lines.append("")

    emit("MCQ Accuracy (overall)", "mcq_overall_accuracy", lambda x: fmt_num(x, 4))
    emit("MCQ Accuracy (ai_summary_accuracy)", "mcq_ai_summary_accuracy", lambda x: fmt_num(x, 4))
    emit("MCQ Accuracy (article_only_accuracy)", "mcq_article_only_accuracy", lambda x: fmt_num(x, 4))
    emit("MCQ Accuracy (false_lure_accuracy)", "mcq_false_lure_accuracy", lambda x: fmt_num(x, 4))
    emit("False Lures Selected (0–2 per article)", "false_lures_selected_number", lambda x: fmt_num(x, 3))

    emit("Reading Time (minutes; per article)", "reading_time_min", fmt_min)
    emit("Summary Reading % (summary / (summary+article))", "summary_reading_pct", lambda x: fmt_num(x, 2))

    emit("Mental Effort (per article)", "mental_effort", lambda x: fmt_num(x, 2))
    emit("AI Trust (participant-level; repeated across timings)", "ai_trust", lambda x: fmt_num(x, 2))
    emit("AI Dependence (participant-level; repeated across timings)", "ai_dependence", lambda x: fmt_num(x, 2))
    emit("Recall Total Score (participant-level; repeated across timings)", "recall_total_score", lambda x: fmt_num(x, 2))

    overall = df_wide if df_wide is not None else participant_overall(df_long)
    lines.append("## Overall Means (per participant across 3 articles)")
    lines.append("")
    lines.append("| Metric | AI integrated | AI segmented | AI overall | NoAI overall | All participants |")
    lines.append("|---|---:|---:|---:|---:|---:|")

    def mean_for(exp: str, struct: Optional[str], col: str) -> Optional[float]:
        g = overall[overall["experiment"] == exp]
        if struct is not None:
            g = g[g["structure"] == struct]
        return float(g[col].mean()) if not g.empty else None

    def mean_for_all(col: str) -> Optional[float]:
        # Only report an "All participants" mean when the metric exists in BOTH experiments.
        ai_has = overall.loc[overall["experiment"] == "ai", col].notna().any()
        no_has = overall.loc[overall["experiment"] == "no_ai", col].notna().any()
        if not (ai_has and no_has):
            return None
        return float(overall[col].mean())

    overall_rows = [
        ("MCQ Accuracy (overall)", "mcq_overall_accuracy_overall", lambda x: fmt_num(x, 4)),
        ("MCQ Accuracy (ai_summary_accuracy)", "mcq_ai_summary_accuracy_overall", lambda x: fmt_num(x, 4)),
        ("MCQ Accuracy (article_only_accuracy)", "mcq_article_only_accuracy_overall", lambda x: fmt_num(x, 4)),
        ("MCQ Accuracy (false_lure_accuracy)", "mcq_false_lure_accuracy_overall", lambda x: fmt_num(x, 4)),
        ("False lures selected (0–6)", "false_lures_selected_number_overall", lambda x: fmt_num(x, 2)),
        ("Recall total score", "recall_total_score", lambda x: fmt_num(x, 2)),
        ("Reading time (min)", "reading_time_min_overall", fmt_min),
        ("Summary reading %", "summary_reading_pct_overall", lambda x: fmt_num(x, 2)),
        ("Mental effort", "mental_effort_overall", lambda x: fmt_num(x, 2)),
        ("AI trust", "ai_trust", lambda x: fmt_num(x, 2)),
        ("AI dependence", "ai_dependence", lambda x: fmt_num(x, 2)),
    ]
    for label, col, fmt in overall_rows:
        ai_int = fmt(mean_for("ai", "integrated", col))
        ai_seg = fmt(mean_for("ai", "segmented", col))
        ai_all = fmt(mean_for("ai", None, col))
        no_all = fmt(mean_for("no_ai", None, col))
        all_all = fmt(mean_for_all(col))
        lines.append(f"| {label} | {ai_int} | {ai_seg} | {ai_all} | {no_all} | {all_all} |")
    lines.append("")

    lines.append("## Notes / Missingness")
    lines.append("")
    miss_cols = [
        "reading_time_min",
        "summary_time_sec",
        "mental_effort",
        "mcq_overall_accuracy",
        "mcq_ai_summary_accuracy",
        "mcq_article_only_accuracy",
        "mcq_false_lure_accuracy",
        "false_lures_selected_number",
        "recall_total_score",
    ]
    any_missing = False
    for (exp, struct), g in df_long.groupby(["experiment", "structure"], dropna=False):
        missing = {c: int(g[c].isna().sum()) for c in miss_cols if c in g.columns and int(g[c].isna().sum())}
        if missing:
            any_missing = True
            lines.append(f"- {exp}/{struct}: " + ", ".join([f"{k} missing={v}" for k, v in missing.items()]))
    if not any_missing:
        lines.append("- No missing values detected in the computed long table.")
    return "\n".join(lines)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    analysis_dir = root / "final_analysis"
    long_path = analysis_dir / "analysis_long_format.csv"
    wide_path = analysis_dir / "analysis_wide_format.csv"
    out_md = analysis_dir / "descriptive_tables.md"

    # Preferred path: use the analysis CSVs that already exist in final_analysis/.
    # This avoids overwriting user-curated datasets.
    if long_path.exists() and wide_path.exists():
        df_long = pd.read_csv(long_path)
        df_wide = pd.read_csv(wide_path)
        out_md.write_text(build_markdown(df_long, df_wide), encoding="utf-8")
        print(f"Read {long_path}")
        print(f"Read {wide_path}")
        print(f"Wrote {out_md}")
        return 0

    # Fallback path: rebuild analysis files from raw logs (if CSVs are missing).
    recall_scores = parse_recall_scores(analysis_dir / "recall_scoring" / "final_clean_recall_results.tsv")

    long_parts: List[pd.DataFrame] = []

    ai_dir = root / "ai_experiment" / "experiment_data"
    for path in sorted(ai_dir.glob("P*-*_log.csv")):
        pid = detect_pid_from_filename(path)
        # Exclusions: demographics-only or no recall scoring entry.
        if pid in {"P249", "P262"}:
            continue
        df = parse_ai_log(path, recall_scores)
        if not df.empty:
            long_parts.append(df)

    no_dir = root / "no_ai_experiment" / "experiment_data"
    for path in sorted(no_dir.glob("P*-*-NON-AI_log.csv")):
        pid = detect_pid_from_filename(path)
        if pid in {"P185"}:
            continue
        df = parse_noai_log(path, recall_scores)
        if not df.empty:
            long_parts.append(df)

    if not long_parts:
        print("No logs parsed.")
        return 1

    df_long = pd.concat(long_parts, ignore_index=True)

    out_long = analysis_dir / "analysis_long_format.csv"
    out_wide = analysis_dir / "analysis_wide_format.csv"

    df_long.to_csv(out_long, index=False)

    wide = participant_overall(df_long)
    per_timing_cols = [
        "mcq_overall_accuracy",
        "mcq_ai_summary_accuracy",
        "mcq_article_only_accuracy",
        "mcq_false_lure_accuracy",
        "false_lures_selected_number",
        "reading_time_min",
        "summary_time_sec",
        "summary_reading_pct",
        "mental_effort",
    ]
    pivot = df_long.pivot_table(
        index=["participant_id", "experiment", "structure"],
        columns="timing",
        values=per_timing_cols,
        aggfunc="first",
    )
    pivot.columns = [f"{col}_{timing}" for col, timing in pivot.columns]
    pivot = pivot.reset_index()
    wide_full = wide.merge(pivot, on=["participant_id", "experiment", "structure"], how="left")
    wide_full.to_csv(out_wide, index=False)

    out_md.write_text(build_markdown(df_long, wide_full), encoding="utf-8")

    print(f"Wrote {out_long}")
    print(f"Wrote {out_wide}")
    print(f"Wrote {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
