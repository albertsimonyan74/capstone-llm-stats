"""Keyword × Judge 2×2 confusion matrix — print theme version.

Pure JSON read from poster/figures/derived/disagreement_matrix_2x2.json
(produced by derive_disagreement_matrix.py). Run that derivation script
first.

Renders 2×2 with counts + row percentages, teal sequential colormap,
adaptive text color (dark on light cells, light on dark cells), and
disagreement headline annotation below.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from print_theme import (
    PRINT_BG, PRINT_FG, PRINT_FG_MUTED,
    apply_print_theme, dim_remaining_spines, dual_save,
)

apply_print_theme()

DERIVED = ROOT / "poster" / "figures" / "derived" / "disagreement_matrix_2x2.json"
OUT_DIR = ROOT / "poster" / "figures"

# Teal sequential: white → teal-600. Dark cells need light text.
TEAL_CMAP = LinearSegmentedColormap.from_list(
    "teal_seq", ["#ffffff", "#ccfbf1", "#5eead4", "#0d9488", "#115e59"], N=256,
)


def main():
    data = json.loads(DERIVED.read_text())

    if not all(data.get("assertions_passed", {}).values()):
        sys.exit(f"derived file failed assertions: {data.get('assertions_passed')}")

    cells = data["cells"]
    matrix = np.array([
        [cells["kw_pass_judge_pass"], cells["kw_pass_judge_fail"]],
        [cells["kw_fail_judge_pass"], cells["kw_fail_judge_fail"]],
    ])
    row_totals = matrix.sum(axis=1)
    total = int(matrix.sum())
    disagreement = data["disagreement"]

    # Normalize for shading (per-cell intensity)
    vmax = matrix.max()
    intensity = matrix / vmax

    fig, ax = plt.subplots(figsize=(11, 9), dpi=150, facecolor=PRINT_BG)
    ax.set_facecolor(PRINT_BG)

    ax.imshow(intensity, cmap=TEAL_CMAP, vmin=0, vmax=1, aspect="equal")

    row_labels = ["Keyword: PASS", "Keyword: FAIL"]
    col_labels = ["Judge: PASS",   "Judge: FAIL"]

    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(col_labels, fontsize=12.5, fontweight="bold", color=PRINT_FG)
    ax.set_yticklabels(row_labels, fontsize=12.5, fontweight="bold", color=PRINT_FG)
    ax.tick_params(top=False, bottom=False, left=False, right=False,
                   labeltop=True, labelbottom=False)
    ax.xaxis.set_label_position("top")

    for i in range(2):
        for j in range(2):
            count = int(matrix[i, j])
            row_pct = 100.0 * count / row_totals[i]
            text_color = "#ffffff" if intensity[i, j] > 0.55 else PRINT_FG
            ax.text(j, i - 0.08, f"{count:,}",
                    ha="center", va="center",
                    fontsize=28, fontweight="bold", color=text_color)
            ax.text(j, i + 0.18, f"{row_pct:.1f}% of row",
                    ha="center", va="center",
                    fontsize=11, color=text_color, alpha=0.85)

    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(1.5, -0.5)

    ax.set_title("Keyword rubric vs external judge",
                 fontsize=16, fontweight="bold", color=PRINT_FG,
                 pad=14, loc="center")

    fig.text(
        0.5, 0.02,
        f"Total disagreement: {disagreement['n']:,} / {total:,}  "
        f"= {100*disagreement['pct']:.2f}%   "
        f"(assumption_compliance, combined base + perturbation, run-id deduped)",
        ha="center", va="bottom",
        fontsize=11, color=PRINT_FG_MUTED, style="italic",
    )

    fig.tight_layout(rect=(0, 0.06, 1, 1))
    dual_save(fig, "disagreement_matrix", out_dir=str(OUT_DIR))
    plt.close(fig)


if __name__ == "__main__":
    main()
