"""Failure concentration by task type (Fig. 5).

Horizontal stacked bar chart: top-10 task types by L1 failure count,
stacked by the 5 models. n=143 total.

Counts from data/processed_data/results_v2/failure_concentration.json.

Run from repo root:
    python code/visualization/paper_figures/failure_concentration_paper.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data" / "processed_data" / "results_v2" / "failure_concentration.json"
OUT_PNG = ROOT / "paper" / "figures" / "failure_concentration.png"
OUT_SVG = ROOT / "paper" / "figures" / "failure_concentration.svg"

PRINT_BG = "#ffffff"
PRINT_FG = "#0f172a"
PRINT_FG_MUTED = "#475569"

MODELS_ORDER = ["claude", "chatgpt", "gemini", "deepseek", "mistral"]
MODEL_DISPLAY = {
    "claude": "Claude",
    "chatgpt": "GPT-4.1",
    "gemini": "Gemini",
    "deepseek": "DeepSeek",
    "mistral": "Mistral",
}
MODEL_COLORS = {
    "claude":   "#0d9488",
    "chatgpt":  "#16a34a",
    "gemini":   "#e11d48",
    "deepseek": "#2563eb",
    "mistral":  "#7c3aed",
}


def _apply_theme():
    plt.rcParams.update({
        "figure.facecolor":  PRINT_BG,
        "axes.facecolor":    PRINT_BG,
        "savefig.facecolor": PRINT_BG,
        "text.color":        PRINT_FG,
        "axes.labelcolor":   PRINT_FG,
        "axes.edgecolor":    PRINT_FG_MUTED,
        "xtick.color":       PRINT_FG,
        "ytick.color":       PRINT_FG,
        "font.family":       "sans-serif",
        "font.sans-serif":   ["Helvetica", "Arial", "DejaVu Sans"],
        "font.size":         9,
    })


def main():
    _apply_theme()
    d = json.loads(DATA.read_text())
    top10 = d["top10"]
    # reverse so highest is at top of horizontal chart
    top10 = list(reversed(top10))
    labels = [t["task_type"] for t in top10]
    n = len(top10)

    counts = np.zeros((len(MODELS_ORDER), n), dtype=int)
    for col, entry in enumerate(top10):
        for row, m in enumerate(MODELS_ORDER):
            counts[row, col] = entry["per_model"].get(m, 0)

    fig, ax = plt.subplots(figsize=(3.2, 3.0), dpi=300, facecolor=PRINT_BG)
    y = np.arange(n)
    left = np.zeros(n)
    for row, m in enumerate(MODELS_ORDER):
        ax.barh(y, counts[row], left=left,
                color=MODEL_COLORS[m], edgecolor="none",
                label=MODEL_DISPLAY[m], height=0.7)
        left += counts[row]

    totals = counts.sum(axis=0)
    for i, total in enumerate(totals):
        ax.text(total + 0.6, i, str(total),
                va="center", ha="left",
                fontsize=7, fontweight="bold", color=PRINT_FG)

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=7)

    ax.set_xlabel("L1 failures (count)", color=PRINT_FG_MUTED, fontsize=7.5)
    ax.tick_params(axis="x", labelsize=7)
    ax.set_xlim(0, totals.max() * 1.15)

    leg = ax.legend(loc="lower right", fontsize=6.5, frameon=False,
                    handlelength=1.0, borderaxespad=0.2, labelspacing=0.3,
                    ncol=1)
    for txt in leg.get_texts():
        txt.set_color(PRINT_FG)

    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("bottom", "left"):
        ax.spines[side].set_alpha(0.3)

    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(OUT_PNG), format="png", dpi=300,
                bbox_inches="tight", pad_inches=0.05)
    fig.savefig(str(OUT_SVG), format="svg",
                bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)

    size_kb = OUT_PNG.stat().st_size / 1024
    print(f"  Wrote {OUT_PNG}  ({size_kb:.1f} KB)")
    print(f"  Wrote {OUT_SVG}")


if __name__ == "__main__":
    main()
