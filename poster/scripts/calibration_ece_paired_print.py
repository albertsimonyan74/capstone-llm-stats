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
    PRINT_BG, PRINT_FG, PRINT_FG_MUTED, MODEL_COLORS_PRINT,
    ACCENT_GOLD_PRINT,
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

# Website pastel model colors (sitePalette.js MODEL_COLORS) — used here in
# place of the canonical MODEL_COLORS_PRINT to mirror the website's
# calibration panel aesthetic per design request.
MODEL_COLORS_PASTEL = {
    "claude":   "#5eead4",  # teal-300
    "chatgpt":  "#86efac",  # green-300
    "gemini":   "#fda4af",  # rose-300
    "deepseek": "#93c5fd",  # blue-300
    "mistral":  "#c4b5fd",  # violet-300
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
    bar_h = 0.36
    y_centers = np.arange(n)

    for i, m in enumerate(order):
        color = MODEL_COLORS_PASTEL[m]
        y_v = y_centers[i] - bar_h / 2 - 0.02
        y_s = y_centers[i] + bar_h / 2 + 0.02

        ax.barh(y_v, verb_ece[m], height=bar_h,
                color=color, edgecolor="none", zorder=2)
        ax.barh(y_s, sc_ece[m], height=bar_h,
                facecolor=color, hatch="///",
                edgecolor="white", linewidth=0.8, zorder=2)

        ax.text(verb_ece[m] + 0.012, y_v, f"{verb_ece[m]:.3f}",
                va="center", ha="left",
                fontsize=10, fontweight="bold", color=PRINT_FG, zorder=3)
        ax.text(sc_ece[m] + 0.012, y_s, f"{sc_ece[m]:.3f}",
                va="center", ha="left",
                fontsize=10, fontweight="bold", color=PRINT_FG, zorder=3)

    # Rank callouts on Claude (top of order, since it has highest avg rank
    # asymmetry: #1 verb / #5 sc)
    if order[0] == "claude":
        i = 0
        y_v = y_centers[i] - bar_h / 2 - 0.02
        y_s = y_centers[i] + bar_h / 2 + 0.02
        ax.text(0.001, y_v, f"#{verb_rank['claude']}",
                va="center", ha="left",
                fontsize=11, fontweight="bold",
                color=ACCENT_GOLD_PRINT, zorder=4)
        ax.text(0.001, y_s, f"#{sc_rank['claude']}",
                va="center", ha="left",
                fontsize=11, fontweight="bold",
                color=ACCENT_GOLD_PRINT, zorder=4)

    ax.set_yticks(y_centers)
    ax.set_yticklabels([MODEL_LABEL[m] for m in order],
                       fontsize=11, fontweight="bold")
    for tick, m in zip(ax.get_yticklabels(), order):
        tick.set_color(MODEL_COLORS_PRINT[m])
    ax.invert_yaxis()

    xmax = max(max(verb_ece.values()), max(sc_ece.values())) * 1.1
    ax.set_xlim(0, xmax)
    ax.set_xlabel("ECE (smaller = better)",
                  fontsize=11, color=PRINT_FG_MUTED)

    ax.set_title("Calibration ranks flip across measurement methods",
                 fontsize=15, fontweight="bold", color=PRINT_FG,
                 pad=18, loc="left")

    # Legend — placed above the chart, right-aligned, outside plot bars
    from matplotlib.patches import Patch
    legend_handles = [
        Patch(facecolor=PRINT_FG_MUTED, edgecolor="none",
              label="Verbalized ECE"),
        Patch(facecolor=PRINT_FG_MUTED, edgecolor="white",
              hatch="///", linewidth=0.8,
              label="Self-consistency ECE"),
    ]
    leg = ax.legend(
        handles=legend_handles,
        loc="lower left", bbox_to_anchor=(1.0, 0.0),
        frameon=False, fontsize=10, borderaxespad=0.0,
    )
    for txt in leg.get_texts():
        txt.set_color(PRINT_FG)

    ax.grid(False)
    dim_remaining_spines(ax)
    ax.set_axisbelow(True)

    fig.tight_layout()
    dual_save(fig, "calibration_ece_paired", out_dir=str(OUT_DIR))
    plt.close(fig)


if __name__ == "__main__":
    main()
