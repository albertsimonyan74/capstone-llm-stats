"""Three-panel dimension leaderboard.

Replaces both three_rankings.png and rank_shift.png. Three horizontal-bar
panels share model identity colors but each panel sorts by its own metric,
making rank inversions visually explicit (Gemini wins accuracy, ChatGPT wins
robustness, Claude wins calibration — no model wins all three).

Sources (canonical, post-Phase-1.8):
  - bootstrap_ci.json          → accuracy.{model}.mean
  - robustness_v2.json         → per_model.{model}.delta
  - calibration.json           → {model}.ece (verbalized)

Output (dual-write per Tier 2A spec):
  - report_materials/figures/dimension_leaderboard.png
  - capstone-website/frontend/public/visualizations/png/v2/dimension_leaderboard.png
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
    SITE_BG, SITE_FG, SITE_FG_MUTED, MODEL_COLORS,
    apply_site_theme, dim_remaining_spines,
)

apply_site_theme()

BOOTSTRAP = ROOT / "experiments" / "results_v2" / "bootstrap_ci.json"
ROBUST = ROOT / "experiments" / "results_v2" / "robustness_v2.json"
CALIB = ROOT / "experiments" / "results_v2" / "calibration.json"

OUT = ROOT / "report_materials" / "figures" / "dimension_leaderboard.png"
WEB_OUT = ROOT / "capstone-website" / "frontend" / "public" / "visualizations" / "png" / "v2" / "dimension_leaderboard.png"

MODEL_LABEL = {
    "claude":   "Claude",
    "chatgpt":  "ChatGPT",
    "gemini":   "Gemini",
    "deepseek": "DeepSeek",
    "mistral":  "Mistral",
}
MODELS = ["claude", "chatgpt", "gemini", "deepseek", "mistral"]


def _draw_panel(ax, sorted_models, values, *, xlim, title, xlabel,
                value_fmt):
    """One horizontal-bar panel: sorted bars with end-of-bar value labels."""
    ax.set_facecolor(SITE_BG)
    y_pos = np.arange(len(sorted_models))

    for i, m in enumerate(sorted_models):
        ax.barh(y_pos[i], values[i], color=MODEL_COLORS[m], height=0.62)

    span = xlim[1] - xlim[0]
    label_offset = span * 0.012
    for i, v in enumerate(values):
        ax.text(v + label_offset, y_pos[i], value_fmt.format(v),
                va="center", ha="left",
                color=SITE_FG, fontsize=10, fontweight="700")

    ax.set_yticks(y_pos)
    ax.set_yticklabels([MODEL_LABEL[m] for m in sorted_models],
                       fontsize=11, fontweight="700")
    for tick, m in zip(ax.get_yticklabels(), sorted_models):
        tick.set_color(MODEL_COLORS[m])
    ax.invert_yaxis()  # rank #1 at top

    ax.set_xlim(*xlim)
    ax.set_xlabel(xlabel, color=SITE_FG_MUTED, fontsize=10)
    ax.set_title(title, fontsize=12.5, fontweight="700", color=SITE_FG,
                 pad=10, loc="left")
    dim_remaining_spines(ax)
    ax.grid(axis="x", linestyle="-", alpha=0.06, color="#ffffff")
    ax.set_axisbelow(True)


def main():
    bootstrap = json.loads(BOOTSTRAP.read_text())
    robust = json.loads(ROBUST.read_text())
    calib = json.loads(CALIB.read_text())

    accuracy = {m: bootstrap["accuracy"][m]["mean"] for m in MODELS}
    delta = {m: robust["per_model"][m]["delta"] for m in MODELS}
    ece = {m: calib[m]["ece"] for m in MODELS}

    acc_order = sorted(MODELS, key=lambda m: -accuracy[m])
    rob_order = sorted(MODELS, key=lambda m: delta[m])
    cal_order = sorted(MODELS, key=lambda m: ece[m])

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), dpi=150,
                             facecolor=SITE_BG)

    _draw_panel(axes[0], acc_order,
                [accuracy[m] for m in acc_order],
                xlim=(0.6, 0.78),
                title="Accuracy",
                xlabel="(A-30, R-25, M-20, C-15, N-10)",
                value_fmt="{:.3f}")

    _draw_panel(axes[1], rob_order,
                [delta[m] for m in rob_order],
                xlim=(0.0, 0.045),
                title="Robustness  ·  Δ (smaller = better)",
                xlabel="Δ score (base − perturbation)",
                value_fmt="{:+.4f}")

    _draw_panel(axes[2], cal_order,
                [ece[m] for m in cal_order],
                xlim=(0.0, 0.21),
                title="Calibration  ·  ECE (smaller = better)",
                xlabel="Verbalized ECE",
                value_fmt="{:.3f}")

    fig.suptitle("Performance leaderboard across three dimensions",
                 fontsize=15, fontweight="700", color=SITE_FG, y=1.02)
    fig.text(0.5, 0.925,
             "Each panel sorted by its own metric. No model wins all three.",
             ha="center", fontsize=10.5, color=SITE_FG_MUTED, style="italic")

    fig.tight_layout(rect=(0, 0.0, 1, 0.9))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    WEB_OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=150, facecolor=SITE_BG, bbox_inches="tight")
    fig.savefig(WEB_OUT, dpi=150, facecolor=SITE_BG, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {OUT}")
    print(f"Wrote {WEB_OUT}")


if __name__ == "__main__":
    main()
