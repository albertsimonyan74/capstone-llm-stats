"""Per-model keyword-vs-judge disagreement bar chart (Fig. 4).

Two bars per model: keyword-PASS / judge-FAIL (over-credit) and
keyword-FAIL / judge-PASS (under-credit), on the n=2,850 eligible
pool (570 per model).

Counts from data/processed_data/results_v2/per_model_disagreement.json.

Run from repo root:
    python code/visualization/paper_figures/per_model_disagreement_paper.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data" / "processed_data" / "results_v2" / "per_model_disagreement.json"
OUT_PNG = ROOT / "paper" / "figures" / "per_model_disagreement.png"
OUT_SVG = ROOT / "paper" / "figures" / "per_model_disagreement.svg"

PRINT_BG = "#ffffff"
PRINT_FG = "#0f172a"
PRINT_FG_MUTED = "#475569"

MODEL_COLORS = {
    "Claude":   "#0d9488",
    "GPT-4.1":  "#16a34a",
    "Gemini":   "#e11d48",
    "DeepSeek": "#2563eb",
    "Mistral":  "#7c3aed",
}

DISPLAY_NAMES = {
    "claude": "Claude",
    "chatgpt": "GPT-4.1",
    "gemini": "Gemini",
    "deepseek": "DeepSeek",
    "mistral": "Mistral",
}

# Bar colors: over-credit (lighter neutral) vs under-credit (darker neutral)
OVERCREDIT_COLOR = "#e11d48"   # rose -- "fake pass" warning
UNDERCREDIT_COLOR = "#94a3b8"  # slate -- benign


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
    order = ["claude", "chatgpt", "gemini", "deepseek", "mistral"]
    labels = [DISPLAY_NAMES[m] for m in order]
    kw_only = [d["per_model"][m]["n_keyword_only"] for m in order]
    judge_only = [d["per_model"][m]["n_judge_only"] for m in order]

    fig, ax = plt.subplots(figsize=(3.2, 2.4), dpi=300, facecolor=PRINT_BG)
    x = np.arange(len(order))
    w = 0.38
    b1 = ax.bar(x - w/2, kw_only, w, color=OVERCREDIT_COLOR,
                edgecolor="none", label="KW-PASS / Judge-FAIL")
    b2 = ax.bar(x + w/2, judge_only, w, color=UNDERCREDIT_COLOR,
                edgecolor="none", label="KW-FAIL / Judge-PASS")

    for bars in (b1, b2):
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, h + 2,
                    f"{int(h)}", ha="center", va="bottom",
                    fontsize=6.5, fontweight="bold", color=PRINT_FG)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right",
                       rotation_mode="anchor",
                       fontsize=7, fontweight="bold")
    for tick_label, m in zip(ax.get_xticklabels(), order):
        tick_label.set_color(MODEL_COLORS[DISPLAY_NAMES[m]])

    ax.set_ylabel("Disagreement count\n(n=570 per model)",
                  color=PRINT_FG_MUTED, fontsize=7.5)
    ax.tick_params(axis="y", labelsize=7)
    ax.set_ylim(0, max(kw_only) * 1.18)

    leg = ax.legend(loc="upper right", fontsize=6.5, frameon=False,
                    handlelength=1.2, borderaxespad=0.2, labelspacing=0.3)
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
