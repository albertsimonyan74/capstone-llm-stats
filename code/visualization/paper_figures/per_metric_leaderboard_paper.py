"""Per-metric leaderboard figure for the IEEE paper (Fig. 2).

Adapts poster/scripts/dimension_leaderboard_print.py to paper print size
and renames "chatgpt" -> "GPT-4.1" to match the paper's prose + Table I.
Reuses the poster's MODEL_COLORS_PRINT palette for project-wide
consistency (poster + paper + website all share the same per-model
colors).

Run from repo root:
    python code/visualization/paper_figures/per_metric_leaderboard_paper.py

Output:
    paper/figures/per_metric_leaderboard.png  (300 DPI)
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# Font-size constants (single-column paper layout)
TITLE_FONTSIZE       = 9
TICK_FONTSIZE        = 7
MODEL_LABEL_FONTSIZE = 6.5
VALUE_FONTSIZE       = 6.0
XLABEL_FONTSIZE      = 7

ROOT = Path(__file__).resolve().parents[3]
OUT_PATH = ROOT / "paper" / "figures" / "per_metric_leaderboard.png"

# --------------------------------------------------------------------------
# Palette + theme (mirror of poster/scripts/print_theme.py constants).
# Inlined rather than imported so the paper script has no cross-package
# dependency on poster/.
# --------------------------------------------------------------------------
PRINT_BG       = "#ffffff"
PRINT_FG       = "#0f172a"
PRINT_FG_MUTED = "#475569"

# Paper uses "GPT-4.1" label; poster uses internal "chatgpt" key. Same colors.
MODEL_COLORS = {
    "Claude":   "#0d9488",  # teal-600
    "GPT-4.1":  "#16a34a",  # green-600  (poster: chatgpt)
    "Gemini":   "#e11d48",  # rose-600
    "DeepSeek": "#2563eb",  # blue-600
    "Mistral":  "#7c3aed",  # violet-600
}


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
        "axes.titlesize":    11,
        "axes.labelsize":    9,
        "axes.spines.top":   False,
        "axes.spines.right": False,
    })


def _dim_spines(ax, alpha: float = 0.3):
    for side in ("bottom", "left"):
        if side in ax.spines:
            ax.spines[side].set_alpha(alpha)


# --------------------------------------------------------------------------
# Locked data (canonical v2 numbers — see CLAUDE.md scoring scheme).
# --------------------------------------------------------------------------
ACCURACY_DATA = [
    ("Gemini",   0.731),
    ("Claude",   0.698),
    ("GPT-4.1",  0.673),
    ("DeepSeek", 0.669),
    ("Mistral",  0.668),
]
ROBUSTNESS_DATA = [
    ("GPT-4.1",  0.0003),
    ("Mistral",  0.0013),
    ("Gemini",   0.0129),
    ("Claude",   0.0305),
    ("DeepSeek", 0.0388),
]
CALIBRATION_DATA = [
    ("Claude",   0.033),
    ("GPT-4.1",  0.034),
    ("Gemini",   0.077),
    ("Mistral",  0.081),
    ("DeepSeek", 0.198),
]


def _draw_panel(ax, data, *, ylim, title, ylabel, value_fmt):
    models = [m for m, _ in data]
    values = [v for _, v in data]
    colors = [MODEL_COLORS[m] for m in models]
    x_pos = np.arange(len(models))

    ax.bar(x_pos, values, color=colors, width=0.7, edgecolor="none")

    span = ylim[1] - ylim[0]
    label_offset = span * 0.03
    for i, v in enumerate(values):
        ax.text(i, v + label_offset, value_fmt.format(v),
                ha="center", va="bottom",
                color=PRINT_FG, fontsize=VALUE_FONTSIZE, fontweight="bold")

    ax.set_xticks(x_pos)
    ax.set_xticklabels(models, rotation=45, ha="right",
                       rotation_mode="anchor",
                       fontsize=MODEL_LABEL_FONTSIZE, fontweight="bold")
    for tick_label, color in zip(ax.get_xticklabels(), colors):
        tick_label.set_color(color)

    ax.set_ylim(*ylim)
    ax.set_ylabel(ylabel, color=PRINT_FG_MUTED, fontsize=XLABEL_FONTSIZE)
    ax.tick_params(axis="y", labelsize=TICK_FONTSIZE)
    ax.set_title(title, fontsize=TITLE_FONTSIZE, fontweight="bold",
                 color=PRINT_FG, pad=6, loc="left")
    _dim_spines(ax)
    ax.grid(False)
    ax.set_axisbelow(True)


def main():
    _apply_theme()
    fig = plt.figure(figsize=(3.5, 2.4), dpi=300, facecolor=PRINT_BG)
    # Explicit figure-relative coordinates [left, bottom, width, height].
    # Top row: y from 0.62 to 0.90. Bottom row: y from 0.10 to 0.38.
    # Gap = 0.24 — clear of top-row 45-deg x-labels + ECE title.
    ax_acc = fig.add_axes([0.12, 0.62, 0.34, 0.28])
    ax_rob = fig.add_axes([0.58, 0.62, 0.34, 0.28])
    ax_ece = fig.add_axes([0.34, 0.10, 0.34, 0.28])

    _draw_panel(ax_acc, ACCURACY_DATA,
                ylim=(0.60, 0.78),
                title="Accuracy",
                ylabel="",
                value_fmt="{:.3f}")

    _draw_panel(ax_rob, ROBUSTNESS_DATA,
                ylim=(0.0, 0.048),
                title=r"Robustness  $\cdot$  $\Delta$",
                ylabel="",
                value_fmt="{:+.4f}")

    _draw_panel(ax_ece, CALIBRATION_DATA,
                ylim=(0.0, 0.235),
                title=r"Calibration  $\cdot$  ECE",
                ylabel="Verbalized ECE",
                value_fmt="{:.3f}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(OUT_PATH), format="png", dpi=300,
                bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)

    size_kb = OUT_PATH.stat().st_size / 1024
    print(f"  Wrote {OUT_PATH}  ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
