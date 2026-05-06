"""Paired ECE (verbalized vs self-consistency) — print theme.

Mirrors scripts/plot_self_consistency_calibration.py exactly, swapping
the dark site theme for the white print theme + vivid -400 model colors.

Sources:
  experiments/results_v2/calibration.json:[model].ece
    → verbalized ECE
  experiments/results_v2/self_consistency_calibration.json
    :ece_comparison_full[model].consistency_ece_full
    → self-consistency ECE (Phase 1C full coverage)
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

MODEL_ORDER = ["claude", "chatgpt", "gemini", "deepseek", "mistral"]

# Vivid -400 model colors (readable on white)
MODEL_COLORS_VIVID = {
    "claude":   "#2dd4bf",  # teal-400
    "chatgpt":  "#4ade80",  # green-400
    "gemini":   "#fb7185",  # rose-400
    "deepseek": "#60a5fa",  # blue-400
    "mistral":  "#a78bfa",  # violet-400
}


def main() -> None:
    verb_data = json.loads(VERB_FILE.read_text())
    sc_data   = json.loads(SC_FILE.read_text())
    sc_cmp    = sc_data["ece_comparison_full"]

    verb   = [verb_data[m]["ece"] for m in MODEL_ORDER]
    cons   = [sc_cmp[m]["consistency_ece_full"] for m in MODEL_ORDER]
    colors = [MODEL_COLORS_VIVID[m] for m in MODEL_ORDER]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 6.875),
                                   facecolor=PRINT_BG)
    x = np.arange(len(MODEL_ORDER))

    # === LEFT: Verbalized ECE ===
    ax1.set_facecolor(PRINT_BG)
    bars1 = ax1.bar(x, verb, color=colors, edgecolor=PRINT_BG, linewidth=1.5)
    ax1.set_xticks(x)
    ax1.set_xticklabels(MODEL_ORDER, fontsize=10)
    for tick, m in zip(ax1.get_xticklabels(), MODEL_ORDER):
        tick.set_color(MODEL_COLORS_VIVID[m])
    ax1.set_ylabel("ECE (verbalized)", fontsize=11, color=PRINT_FG_MUTED)
    ax1.set_ylim(0, max(verb) * 1.30)
    ax1.set_title("Verbalized extraction\n(keyword, n=855 truly-base runs)",
                  fontsize=11, fontweight="bold", color=PRINT_FG, pad=10)
    ax1.grid(axis="y", linestyle="-", alpha=0.7, color="#e2e8f0")
    ax1.set_axisbelow(True)
    dim_remaining_spines(ax1)
    for bar, val in zip(bars1, verb):
        ax1.text(bar.get_x() + bar.get_width() / 2, val + max(verb) * 0.025,
                 f"{val:.3f}", ha="center", va="bottom",
                 fontsize=9, fontweight="semibold", color=PRINT_FG)

    # === RIGHT: Consistency ECE ===
    ax2.set_facecolor(PRINT_BG)
    bars2 = ax2.bar(x, cons, color=colors, edgecolor=PRINT_BG, linewidth=1.5)
    ax2.axhline(0.6, color=PRINT_FG_MUTED, linestyle=":", linewidth=1.2,
                alpha=0.9, zorder=0)
    ax2.text(-0.45, 0.605, "0.6", fontsize=8, color=PRINT_FG_MUTED,
             ha="left", va="bottom", style="italic")
    ax2.text(2, 0.93,
             "all models > 0.6 — severe overconfidence",
             fontsize=9, color=PRINT_FG, style="italic",
             ha="center", va="center",
             bbox=dict(facecolor=PRINT_BG, edgecolor=PRINT_FG_MUTED,
                       boxstyle="round,pad=0.4", alpha=0.95))
    ax2.set_xticks(x)
    ax2.set_xticklabels(MODEL_ORDER, fontsize=10)
    for tick, m in zip(ax2.get_xticklabels(), MODEL_ORDER):
        tick.set_color(MODEL_COLORS_VIVID[m])
    ax2.set_ylabel("ECE (consistency)", fontsize=11, color=PRINT_FG_MUTED)
    ax2.set_ylim(0, 1.0)
    ax2.set_title("Self-consistency extraction\n(3-rerun, T=0.7, n=2,415 reruns)",
                  fontsize=11, fontweight="bold", color=PRINT_FG, pad=10)
    ax2.grid(axis="y", linestyle="-", alpha=0.7, color="#e2e8f0")
    ax2.set_axisbelow(True)
    dim_remaining_spines(ax2)
    for bar, val in zip(bars2, cons):
        ax2.text(bar.get_x() + bar.get_width() / 2, val + 0.015,
                 f"{val:.3f}", ha="center", va="bottom",
                 fontsize=9, fontweight="semibold", color=PRINT_FG)

    fig.tight_layout()
    dual_save(fig, "calibration_ece_paired", out_dir=str(OUT_DIR))
    plt.close(fig)


if __name__ == "__main__":
    main()
