"""Failure taxonomy stacked-bar — print theme.

Pure JSON read from poster/figures/derived/failure_taxonomy_per_task.json
(produced by derive_failure_taxonomy_per_task.py).

Horizontal stacked bars, one row per task type (sorted descending by
total failure count). 4 categories: assumption / math / hallucination /
other. Hallucination is always 0 in this dataset but the legend slot is
preserved so the figure reads as "we looked for hallucination — found
none".
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from print_theme import (
    PRINT_BG, PRINT_FG, PRINT_FG_MUTED,
    apply_print_theme, dim_remaining_spines, dual_save,
)

apply_print_theme()

DERIVED = ROOT / "poster" / "figures" / "derived" / "failure_taxonomy_per_task.json"
OUT_DIR = ROOT / "poster" / "figures"

CATEGORY_COLORS = {
    "assumption":    "#dc2626",  # red-600
    "math":          "#d97706",  # amber-600
    "hallucination": "#7c3aed",  # violet-600
    "other":         "#64748b",  # slate-500
}

CATEGORY_LABELS = {
    "assumption":    "Assumption violation",
    "math":          "Math error",
    "hallucination": "Hallucination",
    "other":         "Other",
}

MIN_SEGMENT_FOR_TEXT = 2  # counts; smaller segments hide their label


def main():
    data = json.loads(DERIVED.read_text())
    if not all(data.get("assertions_passed", {}).values()):
        sys.exit(f"derived file failed assertions: {data['assertions_passed']}")

    cats = data["categories"]
    order = data["task_order_desc_total"]
    per_task = data["per_task"]
    total = data["total"]

    fig, ax = plt.subplots(figsize=(8, 10), dpi=150, facecolor=PRINT_BG)
    ax.set_facecolor(PRINT_BG)

    n = len(order)
    y = np.arange(n)

    cumulative = np.zeros(n, dtype=int)
    for cat in cats:
        widths = np.array([per_task[t][cat] for t in order], dtype=int)
        ax.barh(y, widths, left=cumulative, height=0.74,
                color=CATEGORY_COLORS[cat], edgecolor="none", zorder=2)
        # Inline counts where segment is wide enough
        for yi, w, c0 in zip(y, widths, cumulative):
            if w >= MIN_SEGMENT_FOR_TEXT:
                ax.text(c0 + w / 2, yi, str(int(w)),
                        ha="center", va="center",
                        fontsize=8, fontweight="bold", color="#ffffff",
                        zorder=3)
        cumulative += widths

    ax.set_yticks(y)
    ax.set_yticklabels(order, fontsize=8, family="monospace",
                       color=PRINT_FG)
    ax.invert_yaxis()  # most failures at top

    ax.set_xlabel("Failure count", fontsize=11, color=PRINT_FG_MUTED)
    ax.set_xlim(0, max(data["task_totals"].values()) * 1.05)

    ax.set_title(f"Failure modes by task type (Total — {total})",
                 fontsize=15, fontweight="bold", color=PRINT_FG,
                 pad=22, loc="left")

    legend_handles = [
        Patch(facecolor=CATEGORY_COLORS[c], edgecolor="none",
              label=CATEGORY_LABELS[c])
        for c in cats
    ]
    leg = ax.legend(
        handles=legend_handles,
        loc="lower center", bbox_to_anchor=(0.5, -0.10),
        ncol=4, frameon=False, fontsize=10, columnspacing=1.6,
    )
    for txt in leg.get_texts():
        txt.set_color(PRINT_FG)

    ax.grid(False)
    dim_remaining_spines(ax)
    ax.set_axisbelow(True)

    fig.tight_layout(rect=(0, 0.03, 1, 0.94))
    dual_save(fig, "failure_taxonomy_stacked", out_dir=str(OUT_DIR))
    plt.close(fig)


if __name__ == "__main__":
    main()
