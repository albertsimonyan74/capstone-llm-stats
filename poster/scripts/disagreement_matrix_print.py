"""2×2 large-cell keyword × judge disagreement matrix — print theme.

Pure JSON read from poster/figures/derived/disagreement_matrix_2x2.json
(produced by derive_disagreement_matrix_2x2.py — run that first).

Layout — minimal, metadata-stripped:
  - Column headers above the matrix (JUDGE: PASS / JUDGE: FAIL)
  - Row headers left of the matrix (KEYWORD: PASS / KEYWORD: FAIL),
    rotated 90°
  - 2 × 2 saturated cells with rounded corners
      · agreement: bg teal-600  + 2pt teal-700  border
      · flip:      bg red-600   + 2pt red-800   border
  - All cell text white (count, row %, italic label)

No header, no footer, no rule, no summary line. Metadata moves to poster
body text. Cell grid fills ~85% of figure, with just enough padding for
the row/column headers.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from print_theme import (
    PRINT_BG,
    apply_print_theme, dual_save,
)

apply_print_theme()

DERIVED = ROOT / "poster" / "figures" / "derived" / "disagreement_matrix_2x2.json"
OUT_DIR = ROOT / "poster" / "figures"

# ── Palette ────────────────────────────────────────────────────────────────
TEAL_600   = "#0d9488"
TEAL_700   = "#0f766e"
RED_600    = "#dc2626"
RED_800    = "#991b1b"
SLATE_900  = "#0f172a"
WHITE      = "#ffffff"

# ── Cell layout (axes coords, ax limits 0..1) ─────────────────────────────
CELLS = {
    # (left, bottom, width, height, kind)
    "kw_pass_judge_pass": (0.12,  0.46, 0.435, 0.42, "agreement"),
    "kw_pass_judge_fail": (0.555, 0.46, 0.435, 0.42, "flip"),
    "kw_fail_judge_pass": (0.12,  0.04, 0.435, 0.42, "flip"),
    "kw_fail_judge_fail": (0.555, 0.04, 0.435, 0.42, "agreement"),
}

CELL_LABELS = {
    "kw_pass_judge_pass": "agreement — both pass",
    "kw_pass_judge_fail": "flip — keyword over-credits",
    "kw_fail_judge_pass": "flip — keyword under-credits",
    "kw_fail_judge_fail": "agreement — both fail",
}

ROUNDING = 0.018  # axes-units, ~8pt corner radius


def _draw_cell(ax, key, count, row_pct):
    left, bottom, w, h, kind = CELLS[key]
    if kind == "agreement":
        face, edge = TEAL_600, TEAL_700
    else:
        face, edge = RED_600, RED_800

    box = FancyBboxPatch(
        (left, bottom), w, h,
        boxstyle=f"round,pad=0,rounding_size={ROUNDING}",
        facecolor=face, edgecolor=edge, linewidth=2.0, zorder=2,
    )
    ax.add_patch(box)

    cx, cy = left + w / 2, bottom + h / 2
    ax.text(cx, cy + 0.07, f"{count:,}",
            ha="center", va="center",
            fontsize=44, fontweight="bold", color=WHITE, zorder=3)
    ax.text(cx, cy - 0.025, f"{row_pct:.1f}% of row",
            ha="center", va="center",
            fontsize=16, fontweight="semibold", color=WHITE, zorder=3)
    ax.text(cx, cy - 0.10, CELL_LABELS[key],
            ha="center", va="center",
            fontsize=10, color=WHITE, style="italic", zorder=3,
            family="monospace", alpha=0.95)


def _row_pct_for(data, key):
    cells = data["cells"]
    row_totals = data["row_totals"]
    denom = row_totals["kw_pass"] if key.startswith("kw_pass") else row_totals["kw_fail"]
    return 100.0 * cells[key] / denom if denom else 0.0


def main():
    data = json.loads(DERIVED.read_text())
    if not all(data.get("assertions_passed", {}).values()):
        sys.exit(f"derived file failed assertions: {data['assertions_passed']}")

    cells = data["cells"]

    fig, ax = plt.subplots(figsize=(13, 11), dpi=150, facecolor=PRINT_BG)
    ax.set_facecolor(PRINT_BG)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    # ── Column headers ─────────────────────────────────────────────────────
    for x_center, label in [
        (0.3375, "J U D G E :   P A S S"),
        (0.7725, "J U D G E :   F A I L"),
    ]:
        ax.text(x_center, 0.92, label,
                ha="center", va="bottom",
                fontsize=12, fontweight="bold", color=SLATE_900,
                family="monospace")

    # ── Row headers (rotated) ──────────────────────────────────────────────
    for y_center, label in [
        (0.67, "K E Y W O R D :   P A S S"),
        (0.25, "K E Y W O R D :   F A I L"),
    ]:
        ax.text(0.06, y_center, label,
                ha="center", va="center", rotation=90,
                fontsize=12, fontweight="bold", color=SLATE_900,
                family="monospace")

    # ── Cells ──────────────────────────────────────────────────────────────
    for key in ("kw_pass_judge_pass", "kw_pass_judge_fail",
                "kw_fail_judge_pass", "kw_fail_judge_fail"):
        _draw_cell(ax, key, cells[key], _row_pct_for(data, key))

    fig.subplots_adjust(left=0.0, right=1.0, top=1.0, bottom=0.0)
    dual_save(fig, "disagreement_matrix", out_dir=str(OUT_DIR))
    plt.close(fig)


if __name__ == "__main__":
    main()
