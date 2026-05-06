"""Paired ECE (verbalized vs self-consistency) — print theme.

Sources:
  experiments/results_v2/calibration.json:[model].ece
    → verbalized ECE (claimed-confidence buckets)
  experiments/results_v2/self_consistency_calibration.json:per_model.[model].ece_consistency
    → self-consistency ECE (3-run agreement-based)

Two-panel layout mirrors the website calibration figure: vertical bars,
fixed model order, vivid -400 colors, white background. Right panel
includes a 0.6 reference line and a "severe overconfidence" callout.
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
    apply_print_theme, dim_remaining_spines, dual_save,
)

apply_print_theme()

VERB_FILE = ROOT / "experiments" / "results_v2" / "calibration.json"
SC_FILE   = ROOT / "experiments" / "results_v2" / "self_consistency_calibration.json"
OUT_DIR   = ROOT / "poster" / "figures"

# Fixed model order matching the website panel
MODELS = ["claude", "chatgpt", "gemini", "deepseek", "mistral"]
MODEL_LABEL = {
    "claude":   "claude",
    "chatgpt":  "chatgpt",
    "gemini":   "gemini",
    "deepseek": "deepseek",
    "mistral":  "mistral",
}

# Vivid model colors (tailwind -400) — readable on white, mirror the
# website's panel hue family at higher saturation than -300 pastels.
MODEL_COLORS_VIVID = {
    "claude":   "#2dd4bf",  # teal-400
    "chatgpt":  "#4ade80",  # green-400
    "gemini":   "#fb7185",  # rose-400
    "deepseek": "#60a5fa",  # blue-400
    "mistral":  "#a78bfa",  # violet-400
}


def _bar_panel(ax, values, ymax, ylabel, title_main, title_sub):
    n = len(MODELS)
    x = np.arange(n)
    colors = [MODEL_COLORS_VIVID[m] for m in MODELS]

    ax.bar(x, [values[m] for m in MODELS], width=0.74,
           color=colors, edgecolor="none", zorder=2)

    # Numeric labels above each bar
    for i, m in enumerate(MODELS):
        v = values[m]
        ax.text(i, v + ymax * 0.018, f"{v:.3f}",
                ha="center", va="bottom",
                fontsize=11, fontweight="bold", color=PRINT_FG, zorder=3)

    ax.set_xticks(x)
    ax.set_xticklabels([MODEL_LABEL[m] for m in MODELS],
                       fontsize=11, fontweight="bold")
    for tick, m in zip(ax.get_xticklabels(), MODELS):
        tick.set_color(MODEL_COLORS_VIVID[m])

    ax.set_ylim(0, ymax)
    ax.set_ylabel(ylabel, fontsize=11, color=PRINT_FG_MUTED)

    # Two-line panel title
    ax.set_title(f"{title_main}\n{title_sub}",
                 fontsize=13, fontweight="bold", color=PRINT_FG, pad=16)

    ax.grid(axis="y", color="#e2e8f0", linewidth=0.8, alpha=0.7, zorder=0)
    ax.tick_params(axis="y", labelsize=10, color=PRINT_FG_MUTED)
    ax.tick_params(axis="x", length=0)
    dim_remaining_spines(ax)
    ax.set_axisbelow(True)


def main():
    verb = json.loads(VERB_FILE.read_text())
    sc   = json.loads(SC_FILE.read_text())

    verb_ece = {m: float(verb[m]["ece"]) for m in MODELS}
    sc_ece   = {m: float(sc["per_model"][m]["ece_consistency"]) for m in MODELS}

    fig, (ax_l, ax_r) = plt.subplots(
        1, 2, figsize=(14, 6.4), dpi=150, facecolor=PRINT_BG,
        gridspec_kw={"wspace": 0.18},
    )
    for ax in (ax_l, ax_r):
        ax.set_facecolor(PRINT_BG)

    # ── Left panel: verbalized ───────────────────────────────────────
    _bar_panel(
        ax_l, verb_ece,
        ymax=0.27,
        ylabel="ECE (verbalized)",
        title_main="Verbalized extraction",
        title_sub="(keyword, n=855 truly-base runs)",
    )

    # ── Right panel: self-consistency ────────────────────────────────
    _bar_panel(
        ax_r, sc_ece,
        ymax=1.0,
        ylabel="ECE (consistency)",
        title_main="Self-consistency extraction",
        title_sub="(3-rerun, T=0.7, n=2,415 reruns)",
    )

    # 0.6 dashed reference line + label
    ax_r.axhline(0.6, color=PRINT_FG_MUTED, linestyle=(0, (1, 3)),
                 linewidth=1.2, zorder=1)
    ax_r.text(-0.45, 0.6, "0.6",
              ha="left", va="center",
              fontsize=10, color=PRINT_FG_MUTED, zorder=2)

    # Callout box: "all models > 0.6 — severe overconfidence"
    callout_text = "all models > 0.6 — severe overconfidence"
    ax_r.text(
        0.5, 0.92, callout_text,
        transform=ax_r.transAxes,
        ha="center", va="center",
        fontsize=11, color=PRINT_FG, fontweight="bold",
        bbox=dict(
            boxstyle="round,pad=0.5,rounding_size=0.35",
            facecolor="white", edgecolor=PRINT_FG_MUTED, linewidth=1.0,
        ),
        zorder=5,
    )

    fig.tight_layout()
    dual_save(fig, "calibration_ece_paired", out_dir=str(OUT_DIR))
    plt.close(fig)


if __name__ == "__main__":
    main()
