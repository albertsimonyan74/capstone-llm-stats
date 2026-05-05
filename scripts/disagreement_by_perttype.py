"""Per-perturbation-type pass-flip disagreement chart for §2 Judge Validation.

Three horizontal bars showing directional pass-flip rate (keyword vs Llama
judge) split by perturbation flavor: REPHRASE, NUMERICAL, SEMANTIC. Reference
line at the combined cohort rate (20.74%) demonstrates structural stability.

Source (canonical):
  experiments/results_v2/combined_pass_flip_analysis.json
    perturbation.per_perturbation_type.{rephrase,numerical,semantic}.{n_pass_flip,n_eligible,pct}
    combined.pct_pass_flip

Output (dual-write):
  report_materials/figures/disagreement_by_perttype.png
  capstone-website/frontend/public/visualizations/png/v2/disagreement_by_perttype.png
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from site_palette import (
    SITE_BG, SITE_FG, SITE_FG_MUTED,
    ACCENT_TEAL, ACCENT_PURPLE, ACCENT_GOLD,
    apply_site_theme, dim_remaining_spines,
)

apply_site_theme()

SRC = ROOT / "experiments" / "results_v2" / "combined_pass_flip_analysis.json"
OUT = ROOT / "report_materials" / "figures" / "disagreement_by_perttype.png"
WEB_OUT = ROOT / "capstone-website" / "frontend" / "public" / "visualizations" / "png" / "v2" / "disagreement_by_perttype.png"

ROWS = [
    ("REPHRASE",  "rephrase",  ACCENT_TEAL),
    ("NUMERICAL", "numerical", ACCENT_PURPLE),
    ("SEMANTIC",  "semantic",  ACCENT_GOLD),
]


def main():
    data = json.loads(SRC.read_text())
    per = data["perturbation"]["per_perturbation_type"]
    combined_pct = data["combined"]["pct_pass_flip"] * 100.0

    fig, ax = plt.subplots(figsize=(7, 5), dpi=150, facecolor=SITE_BG)
    ax.set_facecolor(SITE_BG)

    y_pos = np.arange(len(ROWS))
    pcts, ns, totals, colors, labels = [], [], [], [], []
    for label, key, color in ROWS:
        d = per[key]
        pcts.append(d["pct"] * 100.0)
        ns.append(d["n_pass_flip"])
        totals.append(d["n_eligible"])
        colors.append(color)
        labels.append(label)

    bar_height = 0.42
    ax.barh(y_pos, pcts, color=colors, edgecolor=SITE_BG,
            linewidth=0.7, height=bar_height)

    x_max = max(max(pcts), combined_pct) * 1.35
    sub_x_offset = x_max * 0.012
    for i, (pct, n, tot) in enumerate(zip(pcts, ns, totals)):
        ax.text(pct + x_max * 0.012, y_pos[i], f"{pct:.1f}%",
                va="center", ha="left",
                color=SITE_FG, fontsize=16, fontweight="800")
        ax.text(sub_x_offset, y_pos[i] + bar_height / 2 + 0.10,
                f"{n} / {tot} · keyword↔judge flips",
                va="top", ha="left",
                color=SITE_FG_MUTED, fontsize=8, fontweight="600",
                family="monospace")

    ax.axvline(combined_pct, color=SITE_FG_MUTED, linestyle="--",
               linewidth=1.2, alpha=0.75, zorder=1)
    ax.text(combined_pct, -0.78,
            f"combined {combined_pct:.2f}%",
            va="bottom", ha="center",
            color=SITE_FG_MUTED, fontsize=9, fontweight="700",
            family="monospace")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=11, fontweight="800",
                       family="monospace")
    for tick, color in zip(ax.get_yticklabels(), colors):
        tick.set_color(color)
    ax.invert_yaxis()
    ax.set_xlim(0, x_max)
    ax.set_ylim(len(ROWS) - 0.5, -0.95)
    ax.set_xlabel("Directional pass-flip rate (%)",
                  color=SITE_FG_MUTED, fontsize=9)
    ax.tick_params(axis="x", labelsize=8)
    dim_remaining_spines(ax)
    ax.grid(axis="x", linestyle="-", alpha=0.06, color="#ffffff")
    ax.set_axisbelow(True)

    fig.suptitle("Disagreement by perturbation type",
                 fontsize=13, fontweight="700", color=SITE_FG,
                 x=0.02, ha="left", y=0.985)
    fig.text(0.02, 0.935,
             "Pass-flip rate, keyword vs Llama judge",
             ha="left", fontsize=8.5, style="italic", color=SITE_FG_MUTED)

    fig.text(0.5, 0.015,
             "All three within ±5pp of combined — disagreement is structural,\n"
             "not a perturbation-flavor artifact.",
             ha="center", fontsize=8, style="italic", color=SITE_FG_MUTED)

    fig.tight_layout(rect=(0, 0.07, 1, 0.88))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    WEB_OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=150, facecolor=SITE_BG, bbox_inches="tight")
    fig.savefig(WEB_OUT, dpi=150, facecolor=SITE_BG, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {OUT}")
    print(f"Wrote {WEB_OUT}")


if __name__ == "__main__":
    main()
