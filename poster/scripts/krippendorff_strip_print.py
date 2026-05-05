"""Krippendorff α gradient-strip — print theme version.

Reads experiments/results_v2/krippendorff_agreement.json and renders a
horizontal gradient strip (red → neutral → teal) over x ∈ [-1, +1] with
labelled dots at each dimension's α. Footer zone bar partitions the axis
into "systematic disagreement / chance / agreement beyond chance".

Replaces the earlier forest-plot version. No suptitle — header copy lives
in the poster HTML body.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from print_theme import (
    PRINT_BG, PRINT_FG, PRINT_FG_MUTED,
    apply_print_theme, dual_save,
)

apply_print_theme()

KRIPP   = ROOT / "experiments" / "results_v2" / "krippendorff_agreement.json"
OUT_DIR = ROOT / "poster" / "figures"

# Gradient anchor colors (saturated red → slate-300 → saturated teal)
GRAD_LEFT  = "#dc2626"  # red-600
GRAD_MID   = "#cbd5e1"  # slate-300
GRAD_RIGHT = "#0d9488"  # teal-600

# Header / accent colors
TEAL_600 = "#0d9488"
RED_600  = "#dc2626"

# Dot fill — dark anchor on saturated gradient
DOT_FILL = "#0f172a"  # slate-900

# Footer zone backgrounds + borders
ZONE_BG_NEG    = "#fee2e2"  # red-100
ZONE_BG_MID    = "#f1f5f9"  # slate-100
ZONE_BG_POS    = "#ccfbf1"  # teal-100
ZONE_BORDER    = "#cbd5e1"  # slate-300
ZONE_HDR_MID   = "#475569"  # slate-600

# Label box border
BOX_BORDER = "#94a3b8"  # slate-400


def fmt_alpha(value: float) -> str:
    """Signed alpha with 3 decimals and a Unicode minus sign."""
    return f"{value:+.3f}".replace("-", "−")


def main():
    data = json.loads(KRIPP.read_text())
    overall = data["overall"]
    a_alpha = overall["assumption_compliance"]["alpha"]
    r_alpha = overall["reasoning_quality"]["alpha"]
    m_alpha = overall["method_structure"]["alpha"]

    fig, ax = plt.subplots(figsize=(14, 5), dpi=150, facecolor=PRINT_BG)
    ax.set_facecolor(PRINT_BG)
    ax.set_xlim(-1.05, 1.05)
    ax.set_ylim(0.0, 1.0)

    # ------------------------------------------------------------------
    # gradient strip
    # ------------------------------------------------------------------
    strip_y0, strip_y1 = 0.56, 0.64
    strip_mid = (strip_y0 + strip_y1) / 2
    cmap = LinearSegmentedColormap.from_list(
        "krip_strip", [GRAD_LEFT, GRAD_MID, GRAD_RIGHT]
    )
    gradient = np.linspace(-1.0, 1.0, 1024).reshape(1, -1)
    ax.imshow(
        gradient, aspect="auto",
        extent=[-1.0, 1.0, strip_y0, strip_y1],
        cmap=cmap, zorder=2, interpolation="bilinear",
    )
    ax.add_patch(Rectangle(
        (-1.0, strip_y0), 2.0, strip_y1 - strip_y0,
        facecolor="none", edgecolor="#cbd5e1",
        linewidth=0.6, zorder=3,
    ))

    # ------------------------------------------------------------------
    # x-axis ticks beneath strip
    # ------------------------------------------------------------------
    tick_top = strip_y0 - 0.005
    tick_bot = strip_y0 - 0.030
    label_y  = strip_y0 - 0.060
    ax.plot([-1.0, 1.0], [tick_top, tick_top],
            color=PRINT_FG_MUTED, lw=0.9, zorder=2)
    tick_specs = [
        (-1.0, "−1.0"),
        (-0.5, "−0.5"),
        ( 0.0, "0"),
        ( 0.5, "+0.5"),
        ( 1.0, "+1.0"),
    ]
    for tx, lbl in tick_specs:
        ax.plot([tx, tx], [tick_top, tick_bot],
                color=PRINT_FG_MUTED, lw=0.9, zorder=2)
        ax.text(tx, label_y, lbl,
                ha="center", va="top",
                color=PRINT_FG_MUTED, fontsize=10)

    # ------------------------------------------------------------------
    # dots + label boxes
    # ------------------------------------------------------------------
    # (letter, alpha, tag, side, box_y) — all dots share DOT_FILL
    dot_specs = [
        ("A", a_alpha, "above chance",     "above", 0.82),
        ("R", r_alpha, "CI excludes zero", "below", 0.32),
        ("M", m_alpha, "CI contains zero", "above", 0.82),
    ]
    box_w, box_h = 0.28, 0.11

    for letter, alpha, tag, side, box_y in dot_specs:
        # clamp box center so the box stays inside the axes
        bx = max(-1.0 + box_w / 2, min(1.0 - box_w / 2, alpha))

        if side == "above":
            box_edge_y = box_y - box_h / 2
            dot_edge_y = strip_y1
        else:
            box_edge_y = box_y + box_h / 2
            dot_edge_y = strip_y0

        # leader line (under box, over strip border)
        ax.plot([alpha, bx], [dot_edge_y, box_edge_y],
                color=BOX_BORDER, lw=0.8, zorder=3)

        # box
        ax.add_patch(FancyBboxPatch(
            (bx - box_w / 2, box_y - box_h / 2),
            box_w, box_h,
            boxstyle="round,pad=0.0,rounding_size=0.012",
            linewidth=1.5, edgecolor=BOX_BORDER,
            facecolor="#ffffff", zorder=4,
        ))
        ax.text(bx, box_y + 0.022,
                f"{letter} · α={fmt_alpha(alpha)}",
                ha="center", va="center",
                fontsize=10.5, fontweight="bold",
                color=PRINT_FG, zorder=5)
        ax.text(bx, box_y - 0.024, tag,
                ha="center", va="center",
                fontsize=8.5, fontstyle="italic",
                color=PRINT_FG_MUTED, zorder=5)

        # dot on top of everything
        ax.scatter([alpha], [strip_mid], s=320,
                   color=DOT_FILL, edgecolor="white",
                   linewidth=2.0, zorder=6)

    # ------------------------------------------------------------------
    # footer zone bar
    # ------------------------------------------------------------------
    footer_y0, footer_y1 = 0.05, 0.27
    fh = footer_y1 - footer_y0

    zones = [
        (-1.0,  -1.0/3, ZONE_BG_NEG, "SYSTEMATIC DISAGREEMENT",
         RED_600,
         "Raters pull in opposite directions, beyond chance"),
        (-1.0/3, 1.0/3, ZONE_BG_MID, "CHANCE BASELINE",
         ZONE_HDR_MID,
         "Agreement equal to random"),
        ( 1.0/3, 1.0,   ZONE_BG_POS, "AGREEMENT BEYOND CHANCE",
         TEAL_600,
         "Closer to 1 = stronger"),
    ]
    for x0, x1, bg, header, hcolor, sub in zones:
        ax.add_patch(Rectangle(
            (x0, footer_y0), x1 - x0, fh,
            facecolor=bg, edgecolor=ZONE_BORDER,
            linewidth=1.0, zorder=1,
        ))
        cx = (x0 + x1) / 2
        # mild visual letter-spacing via thin spaces
        spaced = " ".join(header)
        ax.text(cx, footer_y0 + fh * 0.62, spaced,
                ha="center", va="center",
                fontsize=9, fontweight="bold",
                color=hcolor, zorder=2)
        ax.text(cx, footer_y0 + fh * 0.28, sub,
                ha="center", va="center",
                fontsize=7.5, fontstyle="italic",
                color="#64748b", zorder=2)

    # ------------------------------------------------------------------
    # strip axes chrome
    # ------------------------------------------------------------------
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)

    fig.tight_layout()
    dual_save(fig, "krippendorff_strip", out_dir=str(OUT_DIR))
    plt.close(fig)


if __name__ == "__main__":
    main()
