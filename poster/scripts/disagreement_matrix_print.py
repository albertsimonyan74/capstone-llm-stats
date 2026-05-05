"""2×2 large-cell keyword × judge disagreement matrix — print theme.

Pure JSON read from poster/figures/derived/disagreement_matrix_2x2.json
(produced by derive_disagreement_matrix_2x2.py — run that first).

Layout matches the website screenshot:
  - Header band (title + subtitle + thin rule)
  - Column headers above the matrix
  - Row headers left of the matrix
  - 2 × 2 large rounded cells (~40% × ~29% of figure each)
      · agreement cells: teal-100 bg + teal-600 border
      · flip cells:      red-100 bg  + red-600 border
  - Footer band, light slate bg, single line summary with bold-coloured
    counts/percentages

n=2,850 combined eligible. Disagreement rates computed from the derived
JSON, no constants hard-coded here.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.lines import Line2D

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
TEAL_100   = "#ccfbf1"
RED_600    = "#dc2626"
RED_100    = "#fee2e2"
SLATE_900  = "#0f172a"
SLATE_600  = "#475569"
SLATE_500  = "#64748b"
SLATE_300  = "#cbd5e1"
SLATE_100  = "#f1f5f9"

# ── Cell layout (axes coords, ax limits 0..1) ─────────────────────────────
CELLS = {
    # (left, bottom, width, height, kind)
    "kw_pass_judge_pass": (0.20, 0.46, 0.39, 0.28, "agreement"),
    "kw_pass_judge_fail": (0.59, 0.46, 0.39, 0.28, "flip"),
    "kw_fail_judge_pass": (0.20, 0.18, 0.39, 0.28, "flip"),
    "kw_fail_judge_fail": (0.59, 0.18, 0.39, 0.28, "agreement"),
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
        face, edge = TEAL_100, TEAL_600
    else:
        face, edge = RED_100, RED_600

    box = FancyBboxPatch(
        (left, bottom), w, h,
        boxstyle=f"round,pad=0,rounding_size={ROUNDING}",
        facecolor=face, edgecolor=edge, linewidth=1.5, zorder=2,
    )
    ax.add_patch(box)

    cx, cy = left + w / 2, bottom + h / 2
    ax.text(cx, cy + 0.06, f"{count:,}",
            ha="center", va="center",
            fontsize=44, fontweight="bold", color=SLATE_900, zorder=3)
    ax.text(cx, cy - 0.025, f"{row_pct:.1f}% of row",
            ha="center", va="center",
            fontsize=15, fontweight="bold", color=SLATE_900, zorder=3)
    ax.text(cx, cy - 0.085, CELL_LABELS[key],
            ha="center", va="center",
            fontsize=10, color=SLATE_500, style="italic", zorder=3,
            family="monospace")


def _row_pct_for(data, key):
    cells = data["cells"]
    row_totals = data["row_totals"]
    if key.startswith("kw_pass"):
        denom = row_totals["kw_pass"]
    else:
        denom = row_totals["kw_fail"]
    return 100.0 * cells[key] / denom if denom else 0.0


def main():
    data = json.loads(DERIVED.read_text())
    if not all(data.get("assertions_passed", {}).values()):
        sys.exit(f"derived file failed assertions: {data['assertions_passed']}")

    cells = data["cells"]
    n_total = data["n_total"]
    summary = data["summary"]

    fig, ax = plt.subplots(figsize=(13.5, 11), dpi=150, facecolor=PRINT_BG)
    ax.set_facecolor(PRINT_BG)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    # ── Header ─────────────────────────────────────────────────────────────
    ax.text(
        0.04, 0.95,
        "J U D G E   vs   K E Y W O R D   —   D I S A G R E E M E N T   M A T R I X",
        ha="left", va="bottom",
        fontsize=13, fontweight="bold", color=TEAL_600,
        family="monospace",
    )
    ax.text(
        0.04, 0.915,
        "Combined scope · n=2,850 eligible · assumption_compliance dimension",
        ha="left", va="bottom",
        fontsize=10, color=SLATE_600,
        family="monospace",
    )
    ax.add_line(Line2D([0.04, 0.96], [0.895, 0.895],
                       color=SLATE_300, linewidth=0.8, zorder=1))

    # ── Column headers ─────────────────────────────────────────────────────
    for key, x_center, label in [
        ("kw_pass_judge_pass", 0.395, "J U D G E :   P A S S"),
        ("kw_pass_judge_fail", 0.785, "J U D G E :   F A I L"),
    ]:
        ax.text(x_center, 0.785, label,
                ha="center", va="bottom",
                fontsize=11, fontweight="bold", color=SLATE_600,
                family="monospace")

    # ── Row headers (vertical) ─────────────────────────────────────────────
    for y_center, label in [
        (0.60, "K E Y W O R D :   P A S S"),
        (0.32, "K E Y W O R D :   F A I L"),
    ]:
        ax.text(0.13, y_center, label,
                ha="center", va="center", rotation=90,
                fontsize=11, fontweight="bold", color=SLATE_600,
                family="monospace")

    # ── Cells ──────────────────────────────────────────────────────────────
    for key in ("kw_pass_judge_pass", "kw_pass_judge_fail",
                "kw_fail_judge_pass", "kw_fail_judge_fail"):
        _draw_cell(ax, key, cells[key], _row_pct_for(data, key))

    # ── Footer band ────────────────────────────────────────────────────────
    footer_band = Rectangle(
        (0.04, 0.05), 0.92, 0.08,
        facecolor=SLATE_100, edgecolor="none", zorder=1,
    )
    ax.add_patch(footer_band)

    n_disagree = summary["n_disagree"]
    total_disagreement_pct = summary["total_disagreement_pct"]
    directional_pct = summary["directional_pass_flip_pct"]

    tokens = [
        (f"{n_disagree:,}", "bold", SLATE_900),
        (" of ",            "normal", SLATE_600),
        (f"{n_total:,}",    "bold", SLATE_900),
        (" runs flip pass/fail (", "normal", SLATE_600),
        (f"{total_disagreement_pct:.1f}%", "bold", TEAL_600),
        (" total disagreement; ", "normal", SLATE_600),
        (f"{directional_pct:.2f}%", "bold", TEAL_600),
        (" directional pass-flip)", "normal", SLATE_600),
    ]

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    inv = ax.transData.inverted()

    # Pre-render off-screen to measure widths, then re-place starting at
    # the centred origin.
    measured = []
    for txt, weight, color in tokens:
        t = ax.text(
            0, -1, txt,  # off-axis
            ha="left", va="center",
            fontsize=11, fontweight=weight, color=color,
            family="monospace",
        )
        bbox = t.get_window_extent(renderer=renderer)
        x0_d, _ = inv.transform((bbox.x0, bbox.y0))
        x1_d, _ = inv.transform((bbox.x1, bbox.y0))
        measured.append((txt, weight, color, x1_d - x0_d))
        t.remove()

    total_w = sum(w for _, _, _, w in measured)
    cursor = 0.5 - total_w / 2
    for txt, weight, color, w in measured:
        ax.text(
            cursor, 0.09, txt,
            ha="left", va="center",
            fontsize=11, fontweight=weight, color=color,
            family="monospace", zorder=3,
        )
        cursor += w

    dual_save(fig, "disagreement_matrix", out_dir=str(OUT_DIR))
    plt.close(fig)


if __name__ == "__main__":
    main()
