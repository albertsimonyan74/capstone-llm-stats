"""4-panel keyword × judge agreement heatmaps — print theme.

Pure JSON read from poster/figures/derived/keyword_judge_heatmap_4panel.json
(produced by derive_keyword_judge_heatmap_4panel.py — run that first).

Layout:
  1×4 row, shared y-axis. Each panel: 5×5 grid, x = keyword score, y = judge
  score, both ∈ {0, 0.25, 0.5, 0.75, 1}.

Color mapping:
  LogNorm(vmin=1, vmax=global_max across all 4 panels). Linear normalization
  hides anything below ~50 because counts span 1–871. Log fixes that and
  keeps panels comparable.
  Cmap: teal-100 (#ccfbf1) → teal-700 (#0f766e), tight 2-stop range so even
  count=1 cells have a perceptible tint.
  Zero cells: masked → render as figure background. No fill, no border.

Borders:
  Diagonal (agreement) cells: 2pt teal-600 (#0d9488), one rectangle per cell
  (not a connected stair-step).
  Off-diagonal cells: 1.5pt amber-700 (#b45309) — slightly muted vs gold so
  the borders don't dominate the cell shading.

Text:
  Count, bold. White if log-normalized cell intensity > 0.55, else
  slate-900 (#0f172a). Omitted on zero cells.

Panel order: ascending off-diagonal % (per derived JSON
`panel_order_ascending_off_diag` field).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, LogNorm
from matplotlib.patches import Rectangle
import numpy as np
import numpy.ma as ma

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from print_theme import (
    PRINT_BG, PRINT_FG, PRINT_FG_MUTED,
    apply_print_theme, dual_save,
)

apply_print_theme()

DERIVED = ROOT / "poster" / "figures" / "derived" / "keyword_judge_heatmap_4panel.json"
OUT_DIR = ROOT / "poster" / "figures"

# Tight 2-stop teal cmap (teal-100 → teal-700).
TEAL_CMAP = LinearSegmentedColormap.from_list(
    "teal_log", ["#ccfbf1", "#0f766e"], N=256,
)
TEAL_CMAP.set_bad(color=PRINT_BG)

LEVELS = [0.0, 0.25, 0.5, 0.75, 1.0]
LEVEL_LABELS = ["0", "0.25", "0.5", "0.75", "1"]

DIAG_BORDER     = "#0d9488"  # teal-600, 2pt
OFFDIAG_BORDER  = "#b45309"  # amber-700, 1.5pt
DARK_TEXT_COLOR = "#0f172a"  # slate-900
DARK_TEXT_THRESHOLD = 0.55   # log-normed intensity above → white text


def main():
    data = json.loads(DERIVED.read_text())

    if not all(data.get("assertions_passed", {}).values()):
        sys.exit(f"derived file failed assertions: {data['assertions_passed']}")

    panel_order = data["panel_order_ascending_off_diag"]
    n_total = data["n_total"]
    dims = data["dimensions"]

    # Build matrices, find global max for shared LogNorm
    global_max = 0
    matrices: dict[str, np.ndarray] = {}
    for key in panel_order:
        grid = dims[key]["grid"]
        m = np.zeros((5, 5), dtype=int)
        for i_kw, kl in enumerate(LEVELS):
            kl_key = f"{kl:.2f}"
            for j_jd, jl in enumerate(LEVELS):
                jl_key = f"{jl:.2f}"
                m[j_jd, i_kw] = grid[kl_key][jl_key]
        matrices[key] = m
        if m.max() > global_max:
            global_max = int(m.max())

    norm = LogNorm(vmin=1, vmax=global_max)

    fig, axes = plt.subplots(1, 4, figsize=(18, 5.4), dpi=150,
                             facecolor=PRINT_BG, sharey=True)

    for panel_idx, key in enumerate(panel_order):
        ax = axes[panel_idx]
        ax.set_facecolor(PRINT_BG)
        m = matrices[key]
        masked = ma.masked_where(m == 0, m)

        ax.imshow(masked, cmap=TEAL_CMAP, norm=norm,
                  aspect="equal", origin="lower")

        for i_jd in range(5):
            for i_kw in range(5):
                count = int(m[i_jd, i_kw])
                if count == 0:
                    continue  # no fill, no border, no text

                is_diag = (i_jd == i_kw)
                if is_diag:
                    border_color = DIAG_BORDER
                    border_lw = 2.0
                else:
                    border_color = OFFDIAG_BORDER
                    border_lw = 1.5

                rect = Rectangle(
                    (i_kw - 0.5, i_jd - 0.5), 1, 1,
                    fill=False, edgecolor=border_color,
                    linewidth=border_lw, zorder=3,
                )
                ax.add_patch(rect)

                norm_val = float(norm(count))
                text_color = (
                    "#ffffff" if norm_val > DARK_TEXT_THRESHOLD
                    else DARK_TEXT_COLOR
                )
                ax.text(
                    i_kw, i_jd, f"{count}",
                    ha="center", va="center",
                    fontsize=11, fontweight="bold", color=text_color,
                    zorder=4,
                )

        ax.set_xticks(range(5))
        ax.set_yticks(range(5))
        ax.set_xticklabels(LEVEL_LABELS, fontsize=10)
        ax.set_yticklabels(LEVEL_LABELS, fontsize=10)
        ax.tick_params(top=False, bottom=True, left=True, right=False,
                       length=0)

        ax.set_xlabel("Keyword rubric", color=PRINT_FG_MUTED, fontsize=11)
        if panel_idx == 0:
            ax.set_ylabel("LLM judge", color=PRINT_FG_MUTED, fontsize=11)

        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.set_xlim(-0.5, 4.5)
        ax.set_ylim(-0.5, 4.5)

        rec = dims[key]
        ax.set_title(
            f"{rec['panel_label']}  ·  off-diagonal: {rec['off_diag_pct']:.1f}%",
            fontsize=12, fontweight="bold", color=PRINT_FG, pad=10, loc="center",
        )

    fig.suptitle(
        "Keyword rubric vs external LLM judge — agreement heatmaps",
        fontsize=16, fontweight="bold", color=PRINT_FG, y=1.02,
    )

    fig.tight_layout(rect=(0, 0.02, 1, 0.96))

    last_ax = axes[-1]
    last_ax.text(
        4.5, -1.25, f"n = {n_total:,}",
        ha="right", va="top",
        fontsize=11, color=PRINT_FG_MUTED, style="italic",
        transform=last_ax.transData,
    )

    dual_save(fig, "disagreement_matrix", out_dir=str(OUT_DIR))
    plt.close(fig)


if __name__ == "__main__":
    main()
