"""Paired ECE (verbalized vs self-consistency) — print theme.

Sources:
  experiments/results_v2/calibration.json:[model].ece
    → verbalized ECE (claimed-confidence buckets)
  experiments/results_v2/self_consistency_calibration.json:per_model.[model].ece_consistency
    → self-consistency ECE (3-run agreement-based)

Visualises the rank flip: Claude #1 verbalized → #5 self-consistency.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from print_theme import (
    PRINT_BG, PRINT_FG, PRINT_FG_MUTED,
    apply_print_theme, dim_remaining_spines, dual_save,
)

apply_print_theme()

VERB_FILE = ROOT / "experiments" / "results_v2" / "calibration.json"
SC_FILE   = ROOT / "experiments" / "results_v2" / "self_consistency_calibration.json"
OUT_DIR   = ROOT / "poster" / "figures"

MODELS = ["claude", "chatgpt", "gemini", "deepseek", "mistral"]
MODEL_LABEL = {
    "claude":   "Claude",
    "chatgpt":  "ChatGPT",
    "gemini":   "Gemini",
    "deepseek": "DeepSeek",
    "mistral":  "Mistral",
}

# Vivid model colors (tailwind -400) — punchier than the website's -300
# pastels but readable on white. Used here in place of MODEL_COLORS_PRINT
# to mirror the website panel hue family while keeping print contrast.
MODEL_COLORS_VIVID = {
    "claude":   "#2dd4bf",  # teal-400
    "chatgpt":  "#4ade80",  # green-400
    "gemini":   "#fb7185",  # rose-400
    "deepseek": "#60a5fa",  # blue-400
    "mistral":  "#a78bfa",  # violet-400
}


def main():
    verb = json.loads(VERB_FILE.read_text())
    sc   = json.loads(SC_FILE.read_text())

    verb_ece = {m: float(verb[m]["ece"]) for m in MODELS}
    sc_ece   = {m: float(sc["per_model"][m]["ece_consistency"]) for m in MODELS}

    # Rank (1 = best/lowest ECE)
    verb_rank = {m: r + 1
                 for r, m in enumerate(sorted(MODELS, key=lambda x: verb_ece[x]))}
    sc_rank   = {m: r + 1
                 for r, m in enumerate(sorted(MODELS, key=lambda x: sc_ece[x]))}

    # Order by mean rank across both metrics (rank-flip visible)
    avg_rank = {m: (verb_rank[m] + sc_rank[m]) / 2 for m in MODELS}
    order = sorted(MODELS, key=lambda m: avg_rank[m])

    fig, ax = plt.subplots(figsize=(10, 6), dpi=150, facecolor=PRINT_BG)
    ax.set_facecolor(PRINT_BG)

    n = len(order)
    y_centers = np.arange(n)

    # Dumbbell chart: one row per model; two markers (verbalized vs
    # self-consistency) connected by a model-color bar. Filled square
    # marker = verbalized; ringed circle = self-consistency. Bar between
    # them encodes the gap visually — the wider the spread, the worse
    # the rank flip.
    MARKER_SIZE_V = 240   # filled square
    MARKER_SIZE_S = 320   # hollow ring
    BAR_HEIGHT    = 0.18

    for i, m in enumerate(order):
        color = MODEL_COLORS_VIVID[m]
        y = y_centers[i]

        # Connecting horizontal bar (gradient feel via tinted fill)
        x_lo, x_hi = sorted([verb_ece[m], sc_ece[m]])
        ax.barh(y, x_hi - x_lo, left=x_lo, height=BAR_HEIGHT,
                facecolor=color, alpha=0.30, edgecolor="none", zorder=1)

        # Verbalized marker — filled square
        ax.scatter(verb_ece[m], y, s=MARKER_SIZE_V, marker="s",
                   facecolor=color, edgecolor="white", linewidth=1.6,
                   zorder=3)

        # Self-consistency marker — solid filled circle (smaller white
        # interior dot for double-ring effect)
        ax.scatter(sc_ece[m], y, s=MARKER_SIZE_S, marker="o",
                   facecolor=color, edgecolor=PRINT_FG, linewidth=1.4,
                   zorder=3)
        ax.scatter(sc_ece[m], y, s=MARKER_SIZE_S * 0.32, marker="o",
                   facecolor="white", edgecolor="none", zorder=4)

        # Numeric labels — verbalized (left of marker), SC (right of marker)
        ax.text(verb_ece[m] - 0.012, y, f"{verb_ece[m]:.3f}",
                va="center", ha="right",
                fontsize=10, fontweight="bold", color=PRINT_FG, zorder=5)
        ax.text(sc_ece[m] + 0.014, y, f"{sc_ece[m]:.3f}",
                va="center", ha="left",
                fontsize=10, fontweight="bold", color=PRINT_FG, zorder=5)

    ax.set_yticks(y_centers)
    ax.set_yticklabels([MODEL_LABEL[m] for m in order],
                       fontsize=11, fontweight="bold")
    for tick, m in zip(ax.get_yticklabels(), order):
        tick.set_color(MODEL_COLORS_VIVID[m])
    ax.invert_yaxis()

    xmin = -0.04
    xmax = max(max(verb_ece.values()), max(sc_ece.values())) * 1.1
    ax.set_xlim(xmin, xmax)
    ax.set_xlabel("ECE (smaller = better)",
                  fontsize=11, color=PRINT_FG_MUTED)

    ax.set_title("Calibration ranks flip across measurement methods",
                 fontsize=15, fontweight="bold", color=PRINT_FG,
                 pad=18, loc="left")

    # Legend — small marker swatches matching plot encoding
    from matplotlib.lines import Line2D
    legend_handles = [
        Line2D([0], [0], marker="s", linestyle="none",
               markerfacecolor=PRINT_FG_MUTED, markeredgecolor="white",
               markeredgewidth=1.6, markersize=11,
               label="Verbalized ECE"),
        Line2D([0], [0], marker="o", linestyle="none",
               markerfacecolor=PRINT_FG_MUTED, markeredgecolor=PRINT_FG,
               markeredgewidth=1.4, markersize=12,
               label="Self-consistency ECE"),
    ]
    leg = ax.legend(
        handles=legend_handles,
        loc="lower left", bbox_to_anchor=(1.0, 0.0),
        frameon=False, fontsize=10, borderaxespad=0.0,
        handletextpad=0.6,
    )
    for txt in leg.get_texts():
        txt.set_color(PRINT_FG)

    ax.grid(axis="x", color="#e2e8f0", linewidth=0.8, alpha=0.7, zorder=0)
    dim_remaining_spines(ax)
    ax.set_axisbelow(True)

    fig.tight_layout()
    dual_save(fig, "calibration_ece_paired", out_dir=str(OUT_DIR))
    plt.close(fig)


if __name__ == "__main__":
    main()
