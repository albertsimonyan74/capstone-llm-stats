"""Krippendorff α forest plot — print theme version.

Reads experiments/results_v2/krippendorff_agreement.json directly. The
file already stores 95% bootstrap CIs at
overall.{dim}.{alpha,ci_lower,ci_upper}, so no separate CI source is
needed.

Three rows: assumption_compliance (+0.573), reasoning_quality (-0.125),
method_structure (-0.009). Point colored by sign (positive = teal,
negative = gold). Dashed reference at α=0.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from print_theme import (
    PRINT_BG, PRINT_FG, PRINT_FG_MUTED,
    ACCENT_TEAL_PRINT, ACCENT_GOLD_PRINT,
    apply_print_theme, dim_remaining_spines, dual_save,
)

apply_print_theme()

KRIPP = ROOT / "experiments" / "results_v2" / "krippendorff_agreement.json"
OUT_DIR = ROOT / "poster" / "figures"

DIMS = [
    ("assumption_compliance", "Assumption compliance"),
    ("reasoning_quality",     "Reasoning quality"),
    ("method_structure",      "Method structure"),
]


def main():
    data = json.loads(KRIPP.read_text())
    overall = data["overall"]

    rows = []
    for key, label in DIMS:
        rec = overall[key]
        rows.append({
            "label": label,
            "alpha": rec["alpha"],
            "lo":    rec["ci_lower"],
            "hi":    rec["ci_upper"],
        })

    fig, ax = plt.subplots(figsize=(14, 4.5), dpi=150, facecolor=PRINT_BG)
    ax.set_facecolor(PRINT_BG)

    y_pos = np.arange(len(rows))[::-1]  # top-down

    for y, r in zip(y_pos, rows):
        color = ACCENT_TEAL_PRINT if r["alpha"] >= 0 else ACCENT_GOLD_PRINT
        ax.plot([r["lo"], r["hi"]], [y, y],
                color=color, lw=2.5, solid_capstyle="round", zorder=2)
        ax.scatter([r["alpha"]], [y],
                   color=color, s=90, zorder=3, edgecolor=PRINT_BG, linewidth=1.5)

        ax.text(r["hi"] + 0.025, y,
                f"α = {r['alpha']:+.3f}  [{r['lo']:+.3f}, {r['hi']:+.3f}]",
                va="center", ha="left",
                color=PRINT_FG, fontsize=10.5, fontweight="bold")

    ax.axvline(0, color=PRINT_FG_MUTED, linestyle="--", lw=1.2, alpha=0.6, zorder=1)

    ax.set_yticks(y_pos)
    ax.set_yticklabels([r["label"] for r in rows],
                       fontsize=12, fontweight="bold", color=PRINT_FG)

    lo_min = min(r["lo"] for r in rows)
    hi_max = max(r["hi"] for r in rows)
    pad = (hi_max - lo_min) * 0.6
    ax.set_xlim(lo_min - pad * 0.15, hi_max + pad)

    ax.set_xlabel("α (95% CI)", color=PRINT_FG_MUTED, fontsize=11)
    ax.set_title("Judge–keyword agreement (Krippendorff α)",
                 fontsize=15, fontweight="bold", color=PRINT_FG,
                 pad=12, loc="left")

    dim_remaining_spines(ax)
    ax.grid(False)
    ax.set_axisbelow(True)

    fig.tight_layout()
    dual_save(fig, "krippendorff_forest", out_dir=str(OUT_DIR))
    plt.close(fig)


if __name__ == "__main__":
    main()
