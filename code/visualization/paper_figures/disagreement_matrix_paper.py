"""Disagreement matrix figure for the IEEE paper (Fig. 2).

2x2 contingency of keyword-rubric pass vs LLM-judge pass on the
n=2,850 combined base+perturbation eligible-run pool, computed on the
assumption_compliance dimension at threshold 0.5.

Counts derived from data/processed_data/results_v2/
(combined_pass_flip_analysis.json and source JSONL files):
    a = both PASS              = 1,345  (47.2%)
    b = kw PASS, judge FAIL    =   591  (20.7%)
    c = kw FAIL, judge PASS    =   131  ( 4.6%)
    d = both FAIL              =   783  (27.5%)

Run from repo root:
    python code/visualization/paper_figures/disagreement_matrix_paper.py

Output:
    paper/figures/disagreement_matrix.png  (300 DPI)
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT_PATH = ROOT / "paper" / "figures" / "disagreement_matrix.png"

PRINT_BG       = "#ffffff"
PRINT_FG       = "#0f172a"
PRINT_FG_MUTED = "#475569"

# Locked counts (Phase 1.1 verification, n=2,850 eligible).
COUNTS = np.array([
    [1345, 591],   # kw PASS row
    [ 131, 783],   # kw FAIL row
])
TOTAL = COUNTS.sum()
PCT = COUNTS / TOTAL * 100.0


def _apply_theme():
    plt.rcParams.update({
        "figure.facecolor":  PRINT_BG,
        "axes.facecolor":    PRINT_BG,
        "savefig.facecolor": PRINT_BG,
        "text.color":        PRINT_FG,
        "axes.labelcolor":   PRINT_FG,
        "axes.edgecolor":    PRINT_FG_MUTED,
        "xtick.color":       PRINT_FG,
        "ytick.color":       PRINT_FG,
        "font.family":       "sans-serif",
        "font.sans-serif":   ["Helvetica", "Arial", "DejaVu Sans"],
        "font.size":         9,
    })


def main():
    _apply_theme()
    fig, ax = plt.subplots(figsize=(3.0, 2.6), dpi=300, facecolor=PRINT_BG)

    im = ax.imshow(COUNTS, cmap="Blues", aspect="auto")

    # Cell annotations
    vmax = COUNTS.max()
    for i in range(2):
        for j in range(2):
            cnt = COUNTS[i, j]
            pct = PCT[i, j]
            # White text on dark cells, dark text on light cells
            text_color = "white" if cnt > 0.55 * vmax else PRINT_FG
            ax.text(j, i - 0.10, f"{cnt:,}",
                    ha="center", va="center",
                    color=text_color, fontsize=11, fontweight="bold")
            ax.text(j, i + 0.18, f"{pct:.1f}%",
                    ha="center", va="center",
                    color=text_color, fontsize=8)

    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(["PASS", "FAIL"], fontsize=8)
    ax.set_yticklabels(["PASS", "FAIL"], fontsize=8)
    ax.set_xlabel("Judge", fontsize=9, color=PRINT_FG)
    ax.set_ylabel("Keyword Rubric", fontsize=9, color=PRINT_FG)

    ax.tick_params(axis="both", which="both", length=0)
    for s in ax.spines.values():
        s.set_visible(False)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(OUT_PATH), format="png", dpi=300,
                bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)

    size_kb = OUT_PATH.stat().st_size / 1024
    print(f"  Wrote {OUT_PATH}  ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
