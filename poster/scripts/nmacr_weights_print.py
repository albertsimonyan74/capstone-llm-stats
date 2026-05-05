"""NMACR composite weights — horizontal bar chart for poster.

Hardcoded data (see CLAUDE.md and llm-stats-vault for weight derivation).
Sorted descending. Accent palette (teal/purple/gold/slate/red), not model
colors — these bars are about score components, not models.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from print_theme import (
    PRINT_BG, PRINT_FG, PRINT_FG_MUTED,
    ACCENT_TEAL_PRINT, ACCENT_PURPLE_PRINT, ACCENT_GOLD_PRINT,
    COLOR_NEUTRAL_PRINT, COLOR_BAD_PRINT,
    apply_print_theme, dim_remaining_spines, dual_save,
)

apply_print_theme()

OUT_DIR = ROOT / "poster" / "figures"

WEIGHTS = [
    ("Assumption",   30, ACCENT_TEAL_PRINT),
    ("Reasoning",    25, ACCENT_PURPLE_PRINT),
    ("Method",       20, ACCENT_GOLD_PRINT),
    ("Calibration",  15, COLOR_NEUTRAL_PRINT),
    ("Numerical",    10, COLOR_BAD_PRINT),
]


def main():
    items = sorted(WEIGHTS, key=lambda x: -x[1])
    labels = [x[0] for x in items]
    weights = [x[1] for x in items]
    colors = [x[2] for x in items]

    fig, ax = plt.subplots(figsize=(14, 5), dpi=150, facecolor=PRINT_BG)
    ax.set_facecolor(PRINT_BG)

    y_pos = np.arange(len(items))
    ax.barh(y_pos, weights, color=colors, height=0.62)

    for i, w in enumerate(weights):
        ax.text(w + 0.6, y_pos[i], f"{w}%",
                va="center", ha="left",
                color=PRINT_FG, fontsize=12, fontweight="bold")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=12, fontweight="bold")
    for tick, c in zip(ax.get_yticklabels(), colors):
        tick.set_color(c)
    ax.invert_yaxis()

    ax.set_xlim(0, 35)
    ax.set_xlabel("Weight (%)", color=PRINT_FG_MUTED, fontsize=11)
    ax.set_title("NMACR composite score weights",
                 fontsize=15, fontweight="bold", color=PRINT_FG,
                 pad=12, loc="left")

    dim_remaining_spines(ax)
    ax.grid(False)
    ax.set_axisbelow(True)

    fig.tight_layout()
    dual_save(fig, "nmacr_weights", out_dir=str(OUT_DIR))
    plt.close(fig)


if __name__ == "__main__":
    main()
