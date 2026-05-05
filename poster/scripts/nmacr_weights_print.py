"""NMACR composite weights — stacked horizontal bar.

Matches the website's stacked-bar visualization: single horizontal bar,
five segments sized by weight (A=30, R=25, M=20, C=15, N=10, sum=100),
in-segment white bold labels.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from print_theme import (
    PRINT_BG, PRINT_FG, PRINT_FG_MUTED, NMACR_SEGMENT_COLORS,
    apply_print_theme, dual_save,
)

apply_print_theme()

OUT_DIR = ROOT / "poster" / "figures"

# Segment order, left to right
SEGMENTS = [
    ("A", 30),
    ("R", 25),
    ("M", 20),
    ("C", 15),
    ("N", 10),
]


def main():
    fig, ax = plt.subplots(figsize=(14, 4.0), dpi=150, facecolor=PRINT_BG)
    ax.set_facecolor(PRINT_BG)

    # Subtitle (above bar)
    fig.text(
        0.5, 0.78,
        "Five dimensions, literature-derived weights",
        ha="center", va="bottom",
        fontsize=14, fontweight="bold", color=PRINT_FG,
    )

    # Stacked bar
    cursor = 0.0
    bar_y = 0.42
    bar_h = 0.30  # ~12% of figure (axes coords used for the bar rectangle area)
    for letter, weight in SEGMENTS:
        color = NMACR_SEGMENT_COLORS[letter]
        ax.barh(
            y=bar_y, width=weight, left=cursor, height=bar_h,
            color=color, edgecolor="none", align="center",
        )
        ax.text(
            cursor + weight / 2.0, bar_y,
            f"{letter} · {weight}%",
            ha="center", va="center",
            color="#ffffff", fontsize=15, fontweight="bold",
        )
        cursor += weight

    # Caption (below bar)
    fig.text(
        0.5, 0.10,
        "Weights sum to 1.00. Dimensions weighted by literature convergence "
        "(Du 2025, Boye-Moell 2025, Yamauchi 2025).",
        ha="center", va="top",
        fontsize=10.5, color=PRINT_FG_MUTED, style="italic",
    )

    # Strip axes
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    dual_save(fig, "nmacr_weights", out_dir=str(OUT_DIR))
    plt.close(fig)


if __name__ == "__main__":
    main()
