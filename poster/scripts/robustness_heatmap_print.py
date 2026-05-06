"""Robustness Δ heatmap (38 task types × 5 models) — print theme.

Pure JSON read from poster/figures/derived/robustness_heatmap_data.json
(produced by derive_robustness_heatmap.py).

Diverging colormap (RdBu_r): red = positive Δ (drop under perturbation,
bad); blue = negative Δ (improvement, rare); white = 0. Symmetric vmin/
vmax = ±0.3 anchors zero at midpoint.

Y-axis: 38 task type labels grouped into 6 families (Bayesian Core,
MLE/Freq., MCMC, Regression, Causal/Pred., Advanced) with bracket +
rotated label on the far left.
X-axis (top): model names colored per MODEL_COLORS_PRINT.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from print_theme import (
    PRINT_BG, PRINT_FG, PRINT_FG_MUTED, MODEL_COLORS_PRINT,
    apply_print_theme, dual_save,
)

apply_print_theme()

DERIVED = ROOT / "poster" / "figures" / "derived" / "robustness_heatmap_data.json"
OUT_DIR = ROOT / "poster" / "figures"

MODEL_LABEL = {
    "claude":   "CLAUDE",
    "chatgpt":  "CHATGPT",
    "gemini":   "GEMINI",
    "deepseek": "DEEPSEEK",
    "mistral":  "MISTRAL",
}

VMIN, VMAX = -0.3, 0.3
WHITE_TEXT_THRESHOLD = 0.18  # |Δ| above → white text


def main():
    data = json.loads(DERIVED.read_text())
    models      = data["models"]
    cells       = data["cells"]
    fam_of      = data["family_mapping"]
    fam_order   = data["family_order"]

    # Group task types by family, preserving family order then alphabetical
    # within each family. Skip task types with all-null cells (e.g.
    # BETA_BINOM) — empty heatmap rows read as a rendering bug.
    def _has_data(tt: str) -> bool:
        row = cells.get(tt, {})
        return any(row.get(m) is not None for m in models)

    task_types: list[str] = []
    family_blocks: list[tuple[str, int, int]] = []  # (family, row_start, row_end_exclusive)
    cursor = 0
    for fam in fam_order:
        types_in_fam = sorted(
            [t for t, f in fam_of.items() if f == fam and _has_data(t)]
        )
        if not types_in_fam:
            continue
        task_types.extend(types_in_fam)
        family_blocks.append((fam, cursor, cursor + len(types_in_fam)))
        cursor += len(types_in_fam)

    n_rows = len(task_types)
    n_cols = len(models)

    # Build matrix; missing cells → np.nan (rendered white)
    matrix = np.full((n_rows, n_cols), np.nan)
    for i, tt in enumerate(task_types):
        for j, m in enumerate(models):
            v = cells[tt][m]
            if v is not None:
                matrix[i, j] = float(v)

    fig, ax = plt.subplots(figsize=(9.0, 14.5), dpi=150,
                           facecolor=PRINT_BG)
    ax.set_facecolor(PRINT_BG)

    cmap = plt.get_cmap("RdBu_r").copy()
    cmap.set_bad(color=PRINT_BG)

    masked = np.ma.masked_invalid(matrix)
    im = ax.imshow(
        masked, cmap=cmap, vmin=VMIN, vmax=VMAX,
        aspect="auto", origin="upper",
    )

    # Cell annotations
    for i in range(n_rows):
        for j in range(n_cols):
            v = matrix[i, j]
            if np.isnan(v):
                continue
            sign = "+" if v >= 0 else "−"
            txt = f"{sign}{abs(v):.2f}"
            color = "#ffffff" if abs(v) > WHITE_TEXT_THRESHOLD else "#0f172a"
            ax.text(j, i, txt,
                    ha="center", va="center",
                    fontsize=8, fontweight="bold", color=color, zorder=3)

    # X axis (top): model names in their print colors
    ax.set_xticks(range(n_cols))
    ax.set_xticklabels([MODEL_LABEL[m] for m in models], fontsize=10,
                       fontweight="bold", ha="center")
    ax.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False,
                   left=False, right=False, length=0, pad=6)
    for tick, m in zip(ax.get_xticklabels(), models):
        tick.set_color(MODEL_COLORS_PRINT[m])

    # Y axis: task type labels (monospace)
    ax.set_yticks(range(n_rows))
    ax.set_yticklabels(task_types, fontsize=8, family="monospace",
                       color=PRINT_FG)

    # Light slate-200 grid between cells
    ax.set_xticks(np.arange(-0.5, n_cols, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, n_rows, 1), minor=True)
    ax.grid(which="minor", color="#e2e8f0", linewidth=1, alpha=0.6)
    ax.tick_params(which="minor", length=0)

    for spine in ax.spines.values():
        spine.set_visible(False)

    # Family brackets + rotated labels on the left. Skip groups with fewer
    # than 3 rows — single-row families (Regression, Causal/Pred.) don't
    # have room for a rotated label without colliding into neighbors. Task
    # name itself stands in for the family in those cases.
    MIN_ROWS_FOR_BRACKET = 3
    bracket_x = -1.7
    label_x   = -2.4
    for fam, r0, r1 in family_blocks:
        if (r1 - r0) < MIN_ROWS_FOR_BRACKET:
            continue
        y_top = r0 - 0.4
        y_bot = r1 - 0.6
        # Vertical bracket line
        ax.add_line(Line2D(
            [bracket_x, bracket_x], [y_top, y_bot],
            color=PRINT_FG_MUTED, linewidth=1.0, clip_on=False, zorder=4,
        ))
        # Top + bottom tick
        for y in (y_top, y_bot):
            ax.add_line(Line2D(
                [bracket_x, bracket_x + 0.18], [y, y],
                color=PRINT_FG_MUTED, linewidth=1.0, clip_on=False, zorder=4,
            ))
        ax.text(label_x, (y_top + y_bot) / 2, fam,
                ha="center", va="center", rotation=90,
                fontsize=9, fontweight="bold", color=PRINT_FG,
                clip_on=False, zorder=5)

    # Colorbar
    cbar = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.03, shrink=0.55,
                        aspect=18)
    cbar.set_label("Δ score (positive = drop under perturbation)",
                   fontsize=9, color=PRINT_FG_MUTED)
    cbar.ax.tick_params(labelsize=8, color=PRINT_FG_MUTED)
    cbar.outline.set_visible(False)

    # Trim left/right margins; reserve room for family bracket
    ax.set_xlim(-3.0, n_cols - 0.5)

    fig.tight_layout()
    dual_save(fig, "robustness_heatmap", out_dir=str(OUT_DIR))
    plt.close(fig)


if __name__ == "__main__":
    main()
