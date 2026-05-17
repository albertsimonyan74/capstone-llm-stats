"""Per-(model, axis) robustness heatmap (Fig. 6).

5 models x 3 axes heatmap of R = mean_pert / mean_base.

Data from data/processed_data/results_v2/per_axis_robustness.json.

Run from repo root:
    python code/visualization/paper_figures/per_axis_robustness_paper.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data" / "processed_data" / "results_v2" / "per_axis_robustness.json"
OUT_PNG = ROOT / "paper" / "figures" / "per_axis_robustness.png"
OUT_SVG = ROOT / "paper" / "figures" / "per_axis_robustness.svg"

PRINT_BG = "#ffffff"
PRINT_FG = "#0f172a"
PRINT_FG_MUTED = "#475569"

# Rows in Table I order (accuracy rank)
MODELS_ORDER = ["gemini", "claude", "chatgpt", "deepseek", "mistral"]
MODEL_DISPLAY = {
    "claude":   "Claude",
    "chatgpt":  "GPT-4.1",
    "gemini":   "Gemini",
    "deepseek": "DeepSeek",
    "mistral":  "Mistral",
}
AXES = ["rephrase", "semantic", "numerical"]
AXIS_DISPLAY = {
    "rephrase":  "Rephrasing",
    "semantic":  "Semantic",
    "numerical": "Numerical",
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

    grid = np.zeros((len(MODELS_ORDER), len(AXES)))
    for i, m in enumerate(MODELS_ORDER):
        for j, ax in enumerate(AXES):
            grid[i, j] = d["per_model_axis"][m][ax]["ratio_R"]

    fig, ax = plt.subplots(figsize=(3.0, 2.4), dpi=300, facecolor=PRINT_BG)

    # Diverging colormap centered at 1.0, tight range
    norm = mcolors.TwoSlopeNorm(vmin=0.90, vcenter=1.0, vmax=1.10)
    im = ax.imshow(grid, cmap="RdBu_r", norm=norm, aspect="auto")

    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            v = grid[i, j]
            # text color: dark on light cells, light on dark
            r, g, b, _ = im.cmap(im.norm(v))
            brightness = 0.299 * r + 0.587 * g + 0.114 * b
            tc = "white" if brightness < 0.4 else PRINT_FG
            ax.text(j, i, f"{v:.3f}",
                    ha="center", va="center",
                    fontsize=7.5, fontweight="bold", color=tc)

    ax.set_xticks(np.arange(len(AXES)))
    ax.set_xticklabels([AXIS_DISPLAY[a] for a in AXES],
                       fontsize=7, rotation=0)
    ax.set_yticks(np.arange(len(MODELS_ORDER)))
    ax.set_yticklabels([MODEL_DISPLAY[m] for m in MODELS_ORDER],
                       fontsize=7, fontweight="bold")

    ax.set_xlabel("Perturbation axis",
                  color=PRINT_FG_MUTED, fontsize=7.5)
    ax.tick_params(axis="both", which="both", length=0)
    for s in ax.spines.values():
        s.set_visible(False)

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_ticks([0.90, 0.94, 0.98, 1.02, 1.06, 1.10])
    cbar.set_label("R (1.0 = perfect)", fontsize=6.5,
                   color=PRINT_FG_MUTED)
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
