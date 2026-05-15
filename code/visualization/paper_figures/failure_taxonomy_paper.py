"""Failure taxonomy stacked bar chart for the IEEE paper (Fig. 3).

Stacked vertical bars: 5 models on x-axis, 5 failure categories stacked,
n=143 judge-classified L1 failures total. Counts derived from
data/processed_data/results_v2/error_taxonomy_v2_judge.jsonl
(Phase 1.2 verification).

Run from repo root:
    python code/visualization/paper_figures/failure_taxonomy_paper.py

Output:
    paper/figures/failure_taxonomy.png  (300 DPI)
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT_PATH = ROOT / "paper" / "figures" / "failure_taxonomy.png"

PRINT_BG       = "#ffffff"
PRINT_FG       = "#0f172a"
PRINT_FG_MUTED = "#475569"

# Display labels mapped to "Claude / GPT-4.1 / Gemini / DeepSeek / Mistral"
# in matrix order.
MODELS_DISPLAY = ["Claude", "GPT-4.1", "Gemini", "DeepSeek", "Mistral"]

# Stack order bottom -> top.
CATEGORIES = [
    ("AssumptionViolation", "#E74C3C"),  # red
    ("MathematicalError",   "#F39C12"),  # orange
    ("FormattingFailure",   "#F1C40F"),  # yellow
    ("ConceptualError",     "#3498DB"),  # blue
    ("Hallucination",       "#9B59B6"),  # purple
]

# Counts: rows = models (Claude, GPT-4.1, Gemini, DeepSeek, Mistral),
# cols  = categories in stack order above.
COUNTS = np.array([
    [ 9, 10, 0, 0, 0],   # Claude       (n=19)
    [25,  4, 6, 3, 0],   # GPT-4.1      (n=38)
    [10,  9, 1, 4, 0],   # Gemini       (n=24)
    [15, 13, 6, 2, 0],   # DeepSeek     (n=36)
    [ 8, 12, 5, 1, 0],   # Mistral      (n=26)
])
assert COUNTS.sum() == 143


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
    fig, ax = plt.subplots(figsize=(3.5, 2.8), dpi=300, facecolor=PRINT_BG)

    x = np.arange(len(MODELS_DISPLAY))
    bottom = np.zeros(len(MODELS_DISPLAY))
    for col, (label, color) in enumerate(CATEGORIES):
        vals = COUNTS[:, col]
        ax.bar(x, vals, bottom=bottom, color=color, edgecolor="none",
               width=0.7, label=label)
        bottom += vals

    ax.set_xticks(x)
    ax.set_xticklabels(MODELS_DISPLAY, rotation=45, ha="right",
                       rotation_mode="anchor",
                       fontsize=7, fontweight="bold")

    ax.set_ylabel("L1 failures (count)", color=PRINT_FG_MUTED, fontsize=8)
    ax.tick_params(axis="y", labelsize=7)
    ax.set_ylim(0, 42)

    # Legend on right, vertical
    leg = ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5),
                    fontsize=7, frameon=False, handlelength=1.2,
                    borderaxespad=0.2, labelspacing=0.4)
    for txt in leg.get_texts():
        txt.set_color(PRINT_FG)

    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("bottom", "left"):
        ax.spines[side].set_alpha(0.3)
    ax.grid(False)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(OUT_PATH), format="png", dpi=300,
                bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)

    size_kb = OUT_PATH.stat().st_size / 1024
    print(f"  Wrote {OUT_PATH}  ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
