"""Three-panel dimension leaderboard — print theme version for poster.

Mirrors scripts/dimension_leaderboard.py but uses print_theme (light bg,
dark text, darker model colors) and dual-saves SVG + PNG@600dpi to
poster/figures/.

Sources (canonical, post-Phase-1.8):
  - bootstrap_ci.json          → accuracy.{model}.mean
  - robustness_v2.json         → per_model.{model}.delta
  - calibration.json           → {model}.ece (verbalized)
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
    PRINT_BG, PRINT_FG, PRINT_FG_MUTED, MODEL_COLORS_PRINT,
    apply_print_theme, dim_remaining_spines, dual_save,
)

apply_print_theme()

BOOTSTRAP = ROOT / "experiments" / "results_v2" / "bootstrap_ci.json"
ROBUST = ROOT / "experiments" / "results_v2" / "robustness_v2.json"
CALIB = ROOT / "experiments" / "results_v2" / "calibration.json"

OUT_DIR = ROOT / "poster" / "figures"

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
    ax.set_facecolor(PRINT_BG)
    y_pos = np.arange(len(sorted_models))

    for i, m in enumerate(sorted_models):
        ax.barh(y_pos[i], values[i], color=MODEL_COLORS_PRINT[m], height=0.62)

    span = xlim[1] - xlim[0]
    label_offset = span * 0.012
    for i, v in enumerate(values):
        ax.text(v + label_offset, y_pos[i], value_fmt.format(v),
                va="center", ha="left",
                color=PRINT_FG, fontsize=10, fontweight="bold")

    ax.set_yticks(y_pos)
    ax.set_yticklabels([MODEL_LABEL[m] for m in sorted_models],
                       fontsize=11, fontweight="bold")
    for tick, m in zip(ax.get_yticklabels(), sorted_models):
        tick.set_color(MODEL_COLORS_PRINT[m])
    ax.invert_yaxis()  # rank #1 at top

    ax.set_xlim(*xlim)
    ax.set_xlabel(xlabel, color=PRINT_FG_MUTED, fontsize=10)
    ax.set_title(title, fontsize=12.5, fontweight="bold", color=PRINT_FG,
                 pad=10, loc="left")
    dim_remaining_spines(ax)
    ax.grid(False)
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

    fig, axes = plt.subplots(1, 3, figsize=(14, 6), dpi=150,
                             facecolor=PRINT_BG)

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
                 fontsize=15, fontweight="bold", color=PRINT_FG, y=1.02)
    fig.text(0.5, 0.925,
             "Each panel sorted by its own metric. No model wins all three.",
             ha="center", fontsize=10.5, color=PRINT_FG_MUTED, style="italic")

    fig.tight_layout(rect=(0, 0.0, 1, 0.9))

    dual_save(fig, "dimension_leaderboard", out_dir=str(OUT_DIR))
    plt.close(fig)


if __name__ == "__main__":
    main()
