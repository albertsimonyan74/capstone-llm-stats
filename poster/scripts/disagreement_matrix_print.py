"""4-panel keyword × judge agreement heatmaps — print theme.

Pure JSON read from poster/figures/derived/keyword_judge_heatmap_4panel.json
(produced by derive_keyword_judge_heatmap_4panel.py — run that first).

Layout:
  1×4 row, shared y-axis. Each panel: 5×5 grid, x = keyword score, y = judge
  score, both ∈ {0, 0.25, 0.5, 0.75, 1}. Cells colored by count via teal
  sequential cmap. Cell text: count (omitted if 0); white text on dark cells,
  dark text on light cells. Off-diagonal cells outlined in gold (#d97706 from
  print theme); diagonal cells outlined in thin teal to mark agreement.

Panel order: ascending off-diagonal % (per derived JSON
`panel_order_ascending_off_diag` field).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from print_theme import (
    PRINT_BG, PRINT_FG, PRINT_FG_MUTED, ACCENT_GOLD_PRINT, ACCENT_TEAL_PRINT,
    apply_print_theme, dual_save,
)

apply_print_theme()

DERIVED = ROOT / "poster" / "figures" / "derived" / "keyword_judge_heatmap_4panel.json"
OUT_DIR = ROOT / "poster" / "figures"

# Teal sequential, light → dark
TEAL_CMAP = LinearSegmentedColormap.from_list(
    "teal_seq", ["#ffffff", "#ccfbf1", "#5eead4", "#0d9488", "#115e59"], N=256,
)

LEVELS = [0.0, 0.25, 0.5, 0.75, 1.0]
LEVEL_LABELS = ["0", "0.25", "0.5", "0.75", "1"]

# Cell luminance threshold for swapping text color
DARK_TEXT_THRESHOLD = 0.55  # if intensity > this, switch to white text


def main():
    data = json.loads(DERIVED.read_text())

    if not all(data.get("assertions_passed", {}).values()):
        sys.exit(f"derived file failed assertions: {data['assertions_passed']}")

    panel_order = data["panel_order_ascending_off_diag"]
    n_total = data["n_total"]
    dims = data["dimensions"]

    # Compute global vmax (across all 4 panels) so cmap is comparable
    global_max = 0
    matrices: dict[str, np.ndarray] = {}
    for key in panel_order:
        grid = dims[key]["grid"]
        # axis 0 (rows) = keyword level; axis 1 (cols) = judge level
        # We want x = keyword (cols), y = judge (rows) for plotting.
        m = np.zeros((5, 5), dtype=int)
        for i_kw, kl in enumerate(LEVELS):
            kl_key = f"{kl:.2f}"
            for j_jd, jl in enumerate(LEVELS):
                jl_key = f"{jl:.2f}"
                m[j_jd, i_kw] = grid[kl_key][jl_key]
        matrices[key] = m
        if m.max() > global_max:
            global_max = int(m.max())

    fig, axes = plt.subplots(1, 4, figsize=(18, 5.4), dpi=150,
                             facecolor=PRINT_BG, sharey=True)

    for panel_idx, key in enumerate(panel_order):
        ax = axes[panel_idx]
        ax.set_facecolor(PRINT_BG)
        m = matrices[key]
        intensity = m / global_max if global_max else m.astype(float)

        ax.imshow(intensity, cmap=TEAL_CMAP, vmin=0, vmax=1,
                  aspect="equal", origin="lower")

        for i_jd in range(5):
            for i_kw in range(5):
                count = int(m[i_jd, i_kw])
                is_diag = (i_jd == i_kw)
                # Borders: gold for off-diagonal, teal for diagonal
                border_color = ACCENT_TEAL_PRINT if is_diag else ACCENT_GOLD_PRINT
                border_lw = 1.2 if is_diag else (1.6 if count > 0 else 0.0)
                if border_lw > 0:
                    rect = Rectangle(
                        (i_kw - 0.5, i_jd - 0.5), 1, 1,
                        fill=False, edgecolor=border_color,
                        linewidth=border_lw, zorder=3,
                    )
                    ax.add_patch(rect)

                if count > 0:
                    text_color = "#ffffff" if intensity[i_jd, i_kw] > DARK_TEXT_THRESHOLD else PRINT_FG
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

    # Suptitle
    fig.suptitle(
        "Keyword rubric vs external LLM judge — agreement heatmaps",
        fontsize=16, fontweight="bold", color=PRINT_FG, y=1.02,
    )

    fig.tight_layout(rect=(0, 0.02, 1, 0.96))

    # Footer in bottom-right of last panel
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
