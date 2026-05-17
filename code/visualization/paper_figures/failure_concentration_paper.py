"""Failure concentration by task type (Fig. 5).

10 x 5 horizontal heatmap: top-10 task types (rows) by 5 models
(columns). Sequential Blues colormap. n=143 total L1 failures.

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
    # d["top10"] is sorted by count desc; keep that order (rank 1 at top)
    top10 = d["top10"]
    labels = [t["task_type"] for t in top10]
    n = len(top10)

    # counts[row=task_type, col=model]
    counts = np.zeros((n, len(MODELS_ORDER)), dtype=int)
    for row, entry in enumerate(top10):
        for col, m in enumerate(MODELS_ORDER):
            counts[row, col] = entry["per_model"].get(m, 0)
    totals = counts.sum(axis=1)

    fig, ax = plt.subplots(figsize=(3.4, 3.2), dpi=300, facecolor=PRINT_BG)

    im = ax.imshow(counts, cmap="Blues", vmin=0, vmax=5, aspect="auto")

    # Cell annotations (blank for 0)
    for i in range(n):
        for j in range(len(MODELS_ORDER)):
            val = counts[i, j]
            if val == 0:
                continue
            text_color = "white" if val >= 3 else PRINT_FG
            ax.text(j, i, str(int(val)),
                    ha="center", va="center",
                    fontsize=7.5, fontweight="bold", color=text_color)

    # Right-margin totals
    for i, total in enumerate(totals):
        ax.text(len(MODELS_ORDER) - 0.30, i, f"{int(total)}",
                ha="left", va="center",
                fontsize=8, fontweight="bold", color=PRINT_FG,
                transform=ax.transData)

    ax.set_xticks(np.arange(len(MODELS_ORDER)))
    ax.set_xticklabels([MODEL_DISPLAY[m] for m in MODELS_ORDER],
                       rotation=30, ha="right", rotation_mode="anchor",
                       fontsize=7)
    ax.set_yticks(np.arange(n))
    ax.set_yticklabels(labels, fontsize=7, family="monospace")

    ax.tick_params(axis="both", which="both", length=0)
    for s in ax.spines.values():
        s.set_visible(False)

    cbar = fig.colorbar(im, ax=ax, shrink=0.7, pad=0.14)
    cbar.set_ticks([0, 1, 2, 3, 4, 5])
    cbar.set_label("L1 failures per cell (max 5)",
                   fontsize=6.5, color=PRINT_FG_MUTED)
    cbar.ax.tick_params(labelsize=6)

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
