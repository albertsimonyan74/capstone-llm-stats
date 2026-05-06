"""Failure taxonomy stacked-bar — print theme, vertical layout.

Mirrors the website's failure-rate-by-task-type figure
(visualizations.js:failure_by_tasktype, R-generated PNG via
report_materials/r_analysis/05_failure_analysis.R).

Pure JSON read from poster/figures/derived/failure_taxonomy_per_task.json
(produced by derive_failure_taxonomy_per_task.py — run that first).

Layout:
  - Vertical stacked bars: x = task type, y = failure count
  - X-axis ordering: descending by total_failures
  - Stack order (bottom → top): assumption_violation → mathematical_error
    → formatting_failure → conceptual_error
  - Above-bar label: failure rate as `{rate:.0f}%`
  - X-tick labels rotated 45° for print readability
  - Legend below x-axis with mono small-caps eyebrow header
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
    PRINT_BG, PRINT_FG, BUCKET_COLORS_PRINT,
    apply_print_theme, dim_remaining_spines, dual_save,
)

apply_print_theme()

DERIVED = ROOT / "poster" / "figures" / "derived" / "failure_taxonomy_per_task.json"
OUT_DIR = ROOT / "poster" / "figures"

SLATE_700 = "#334155"
SLATE_600 = "#475569"
SLATE_500 = "#64748b"
SLATE_900 = "#0f172a"

# Stack order, bottom → top
STACK_ORDER = [
    "assumption_violation",
    "mathematical_error",
    "formatting_failure",
    "conceptual_error",
]

BUCKET_LABEL = {
    "assumption_violation": "Assumption Violation",
    "mathematical_error":   "Mathematical Error",
    "formatting_failure":   "Formatting Failure",
    "conceptual_error":     "Conceptual Error",
}


def main():
    data = json.loads(DERIVED.read_text())
    if not all(data.get("assertions_passed", {}).values()):
        sys.exit(f"derived file failed assertions: {data['assertions_passed']}")

    order   = data["task_order_desc_total"]
    per_task = data["per_task"]

    fig, ax = plt.subplots(figsize=(13, 7.5), dpi=150, facecolor=PRINT_BG)
    ax.set_facecolor(PRINT_BG)

    n = len(order)
    x = np.arange(n)

    # Stacked vertical bars, accumulating per category
    cumulative = np.zeros(n, dtype=int)
    for bucket in STACK_ORDER:
        heights = np.array([per_task[t][bucket] for t in order], dtype=int)
        ax.bar(x, heights, bottom=cumulative, width=0.78,
               color=BUCKET_COLORS_PRINT[bucket], edgecolor="none", zorder=2)
        cumulative += heights

    # Above-bar rate labels
    for xi, tt, top in zip(x, order, cumulative):
        rate = per_task[tt]["failure_rate_pct"]
        ax.text(xi, top + max(cumulative) * 0.02, f"{rate:.0f}%",
                ha="center", va="bottom",
                fontsize=10, fontweight="bold", color=SLATE_900, zorder=3)

    ax.set_xticks(x)
    ax.set_xticklabels(order, fontsize=9, family="monospace",
                       color=PRINT_FG, rotation=45, ha="right",
                       rotation_mode="anchor")
    ax.set_xlim(-0.6, n - 0.4)

    ax.set_ylim(0, max(cumulative) * 1.15)
    ax.set_ylabel("Failure count (stacked)",
                  fontsize=10, color=SLATE_700)

    ax.set_title("Failure rate by task type · sorted by total failures",
                 fontsize=14, fontweight="bold", color=SLATE_900,
                 pad=24, loc="left")

    # Legend
    legend_handles = [
        Patch(facecolor=BUCKET_COLORS_PRINT[b], edgecolor="none",
              label=BUCKET_LABEL[b])
        for b in STACK_ORDER
    ]
    leg = ax.legend(
        handles=legend_handles,
        loc="upper center", bbox_to_anchor=(0.5, -0.42),
        ncol=4, frameon=False, fontsize=10, columnspacing=2.0,
        handlelength=1.4, handleheight=1.0, handletextpad=0.6,
    )
    for txt in leg.get_texts():
        txt.set_color(PRINT_FG)

    ax.grid(False)
    dim_remaining_spines(ax)
    ax.set_axisbelow(True)

    fig.tight_layout(rect=(0, 0.26, 1, 0.93))
    dual_save(fig, "failure_taxonomy_stacked", out_dir=str(OUT_DIR))
    plt.close(fig)


if __name__ == "__main__":
    main()
