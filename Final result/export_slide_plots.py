#!/usr/bin/env python3
import os
from pathlib import Path

# Ensure Matplotlib cache is writable (avoid warnings / slowdowns).
_script_dir = Path(__file__).resolve().parent
_mpl_cache = _script_dir / "slide_assets" / ".mplconfig"
_mpl_cache.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(_mpl_cache))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def _ensure_outdir() -> Path:
    outdir = Path(__file__).resolve().parent / "slide_assets"
    outdir.mkdir(parents=True, exist_ok=True)
    return outdir


def plot_slide1(outdir: Path) -> Path:
    # From `Final result/KEY_FINDINGS_SLIDES.tex`
    # Means ± SD:
    # Pre: 0.833 ± 0.141, Sync: 0.568 ± 0.239, Post: 0.641 ± 0.196
    # Approx 95% CI used in slides: ±0.0565, ±0.0956, ±0.0784
    categories = ["Pre-reading", "Synchronous", "Post-reading"]
    means = np.array([0.833, 0.568, 0.641])
    ci = np.array([0.0565, 0.0956, 0.0784])

    fig, ax = plt.subplots(figsize=(9.6, 5.4), dpi=200)
    ax.set_facecolor("#F5F7FA")
    fig.patch.set_facecolor("white")
    x = np.arange(len(categories))

    ax.bar(x, means, yerr=ci, capsize=6, color="#0066CC", edgecolor="#0B3D91", linewidth=1.0)
    ax.set_xticks(x, categories, rotation=15, ha="right")
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("AI summary accuracy")
    ax.set_title("Main Finding 1: Pre-reading improves AI-summary learning")
    ax.grid(axis="y", color="#DDE3EA", linewidth=0.8)
    ax.set_axisbelow(True)

    for i, value in enumerate(means):
        ax.text(i, value + 0.03, f"{value:.3f}", ha="center", va="bottom", fontsize=10, color="#0B3D91")

    ax.text(
        0.99,
        0.02,
        "Error bars: approx. 95% CI",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=9,
        color="#333333",
    )

    outpath = outdir / "slide1_main_finding_1_ai_summary_accuracy.png"
    fig.tight_layout()
    fig.savefig(outpath, bbox_inches="tight")
    plt.close(fig)
    return outpath


def plot_slide2(outdir: Path, repo_root: Path) -> Path:
    # False-lure accuracy from long-format descriptives (averaged across timing)
    false_lure_accuracy = _read_csv(
        repo_root / "final_analysis" / "long_format_outputs" / "tables" / "A1_descriptives_false_lure_accuracy.csv"
    )
    mean_false_lure_acc_by_structure = (
        false_lure_accuracy.groupby("structure", as_index=False)["mean"].mean().rename(columns={"mean": "mean_acc"})
    )
    mean_false_lure_acc_by_structure["structure"] = mean_false_lure_acc_by_structure["structure"].str.title()

    # False lures selected (means across timing) from ANOVA report text:
    # integrated vs segmented (subject mean across timing): 0.583333 vs 1.05556
    false_lures_selected = pd.DataFrame(
        {
            "Structure": ["Integrated", "Segmented"],
            "mean_lures": [0.583333, 1.05556],
        }
    )

    merged = false_lures_selected.merge(
        mean_false_lure_acc_by_structure.rename(columns={"structure": "Structure"}), on="Structure", how="left"
    )

    fig, axes = plt.subplots(1, 2, figsize=(11.2, 5.4), dpi=200)
    fig.patch.set_facecolor("white")

    for ax in axes:
        ax.set_facecolor("#F5F7FA")
        ax.grid(axis="y", color="#DDE3EA", linewidth=0.8)
        ax.set_axisbelow(True)

    # Panel A: false lures selected
    axes[0].bar(merged["Structure"], merged["mean_lures"], color=["#0B3D91", "#FF8C00"], edgecolor="#222222")
    axes[0].set_title("False lures selected (lower is better)")
    axes[0].set_ylabel("Mean per article")

    for i, value in enumerate(merged["mean_lures"].to_numpy()):
        axes[0].text(i, value + 0.03, f"{value:.2f}", ha="center", va="bottom", fontsize=10)

    # Panel B: false-lure accuracy
    axes[1].bar(merged["Structure"], merged["mean_acc"], color=["#0B3D91", "#FF8C00"], edgecolor="#222222")
    axes[1].set_title("False-lure accuracy (higher is better)")
    axes[1].set_ylabel("Proportion correct")
    axes[1].set_ylim(0, 1.0)

    for i, value in enumerate(merged["mean_acc"].to_numpy()):
        axes[1].text(i, value + 0.03, f"{value:.3f}", ha="center", va="bottom", fontsize=10)

    fig.suptitle("Main Finding 2: Integrated format reduces misinformation risk", fontsize=14, y=1.02)
    outpath = outdir / "slide2_main_finding_2_misinformation_risk.png"
    fig.tight_layout()
    fig.savefig(outpath, bbox_inches="tight")
    plt.close(fig)
    return outpath


def plot_slide3(outdir: Path, repo_root: Path) -> Path:
    summary_time = _read_csv(
        repo_root / "final_analysis" / "long_format_outputs" / "tables" / "A1_descriptives_summary_time_sec.csv"
    )
    summary_prop = _read_csv(
        repo_root / "final_analysis" / "long_format_outputs" / "tables" / "A1_descriptives_summary_prop.csv"
    )
    reading_time = _read_csv(
        repo_root / "final_analysis" / "long_format_outputs" / "tables" / "A1_descriptives_reading_time_min.csv"
    )
    total_time = _read_csv(
        repo_root / "final_analysis" / "long_format_outputs" / "tables" / "A1_descriptives_total_time_sec.csv"
    )

    timing_order = ["pre_reading", "synchronous", "post_reading"]
    timing_labels = ["Pre-reading", "Synchronous", "Post-reading"]

    def mean_by_timing(df: pd.DataFrame) -> pd.Series:
        means = df.groupby("timing")["mean"].mean()
        return means.reindex(timing_order)

    summary_time_by_timing = mean_by_timing(summary_time)
    share_by_timing = mean_by_timing(summary_prop) * 100.0
    reading_by_timing = mean_by_timing(reading_time)
    total_by_timing = mean_by_timing(total_time)

    fig, axes = plt.subplots(1, 2, figsize=(11.2, 5.4), dpi=200)
    fig.patch.set_facecolor("white")

    # Panel A: share (%)
    axes[0].set_facecolor("#F5F7FA")
    axes[0].bar(timing_labels, share_by_timing.to_numpy(), color="#0066CC", edgecolor="#0B3D91")
    axes[0].set_title("Summary share of total time (%)")
    axes[0].set_ylabel("Share (%)")
    axes[0].grid(axis="y", color="#DDE3EA", linewidth=0.8)
    axes[0].set_axisbelow(True)
    axes[0].set_ylim(0, max(30, float(share_by_timing.max()) + 5))

    for i, value in enumerate(share_by_timing.to_numpy()):
        axes[0].text(i, value + 0.7, f"{value:.1f}%", ha="center", va="bottom", fontsize=10, color="#0B3D91")

    # Panel B: summary time + total-time line
    axes[1].set_facecolor("#F5F7FA")
    axes[1].bar(timing_labels, summary_time_by_timing.to_numpy(), color="#34B27D", edgecolor="#1C7A52")
    axes[1].set_title("Summary viewing time (seconds)")
    axes[1].set_ylabel("Seconds")
    axes[1].grid(axis="y", color="#DDE3EA", linewidth=0.8)
    axes[1].set_axisbelow(True)

    for i, value in enumerate(summary_time_by_timing.to_numpy()):
        axes[1].text(i, value + 4, f"{value:.1f}s", ha="center", va="bottom", fontsize=10, color="#1C7A52")

    # Total-time line (secondary axis)
    ax2 = axes[1].twinx()
    ax2.plot(timing_labels, total_by_timing.to_numpy(), color="#FF8C00", marker="o", linewidth=2, label="Total time")
    ax2.set_ylabel("Total time (s)")
    ax2.tick_params(axis="y", labelcolor="#FF8C00")
    ax2.spines["right"].set_color("#FF8C00")

    fig.suptitle(
        "Main Finding 3: Pre-reading increases summary engagement without increasing total time", fontsize=14, y=1.02
    )

    footer = (
        f"Reading time (min): {reading_by_timing.iloc[0]:.2f} / {reading_by_timing.iloc[1]:.2f} / {reading_by_timing.iloc[2]:.2f}  •  "
        f"Total time (s): {total_by_timing.iloc[0]:.1f} / {total_by_timing.iloc[1]:.1f} / {total_by_timing.iloc[2]:.1f}"
    )
    fig.text(0.5, 0.01, footer, ha="center", va="bottom", fontsize=9, color="#333333")

    outpath = outdir / "slide3_main_finding_3_summary_engagement.png"
    fig.tight_layout()
    fig.savefig(outpath, bbox_inches="tight")
    plt.close(fig)
    return outpath


def plot_slide4(outdir: Path, repo_root: Path) -> Path:
    # Leave-one-article-out values as shown on robustness slide.
    dropped = ["Semiconductors", "UHI", "CRISPR"]
    delta = np.array([0.172, 0.126, 0.116])
    pvals = ["<.001", ".010", ".016"]

    fig, ax = plt.subplots(figsize=(9.6, 4.8), dpi=200)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#F5F7FA")
    ax.grid(axis="x", color="#DDE3EA", linewidth=0.8)
    ax.set_axisbelow(True)

    y = np.arange(len(dropped))[::-1]
    ax.scatter(delta, y, color="#0066CC", s=60, zorder=3)
    ax.axvline(0, color="#444444", linewidth=1.0)
    ax.set_yticks(y, dropped)
    ax.set_xlabel("Pre–Sync Δ (MCQ accuracy)")
    ax.set_title("Design robustness: Leave-one-article-out (MCQ Pre–Sync)")
    ax.set_xlim(0, max(0.22, float(delta.max()) + 0.04))

    for i, (d, p) in enumerate(zip(delta, pvals)):
        ax.text(d + 0.005, y[i], f"Δ={d:.3f}, p={p}", va="center", fontsize=10)

    outpath = outdir / "slide4_robustness_leave_one_article_out.png"
    fig.tight_layout()
    fig.savefig(outpath, bbox_inches="tight")
    plt.close(fig)
    return outpath


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    outdir = _ensure_outdir()

    paths = [
        plot_slide1(outdir),
        plot_slide2(outdir, repo_root),
        plot_slide3(outdir, repo_root),
        plot_slide4(outdir, repo_root),
    ]

    print("Generated:")
    for p in paths:
        print(f"- {p.relative_to(repo_root)}")


if __name__ == "__main__":
    main()
