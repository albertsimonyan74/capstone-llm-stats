"""Two-panel calibration figure for Phase 1C self-consistency expansion.

Left panel: Verbalized ECE per model (gemini hatched - 0 signals).
Right panel: Consistency ECE per model (full-coverage, 161 numeric tasks).
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
CAL = ROOT / "experiments" / "results_v2" / "self_consistency_calibration.json"
OUT = ROOT / "report_materials" / "figures" / "self_consistency_calibration.png"

MODEL_ORDER = ["claude", "chatgpt", "gemini", "deepseek", "mistral"]
MODEL_COLORS = {
    "claude":   "#C9663C",
    "chatgpt":  "#10A37F",
    "gemini":   "#4285F4",
    "deepseek": "#5B6CFF",
    "mistral":  "#F97316",
}


def main() -> None:
    data = json.loads(CAL.read_text())
    cmp = data["ece_comparison_full"]

    verb = [cmp[m]["verbalized_ece"] for m in MODEL_ORDER]
    cons = [cmp[m]["consistency_ece_full"] for m in MODEL_ORDER]
    colors = [MODEL_COLORS[m] for m in MODEL_ORDER]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
    x = np.arange(len(MODEL_ORDER))

    bars1 = ax1.bar(x, verb, color=colors, edgecolor="black", linewidth=0.6)
    gemini_idx = MODEL_ORDER.index("gemini")
    bars1[gemini_idx].set_hatch("///")
    bars1[gemini_idx].set_alpha(0.55)
    ax1.text(
        gemini_idx, verb[gemini_idx] + 0.008,
        "N/A\n(0 verbalized\nsignals)",
        ha="center", va="bottom", fontsize=8, style="italic",
    )
    ax1.set_xticks(x)
    ax1.set_xticklabels(MODEL_ORDER, fontsize=10)
    ax1.set_ylabel("ECE (verbalized)", fontsize=11)
    ax1.set_ylim(0, 0.25)
    ax1.set_title("Verbalized extraction\n(keyword, n=1,230 base runs)",
                  fontsize=11)
    ax1.grid(axis="y", linestyle="--", alpha=0.35)
    for bar, val in zip(bars1, verb):
        if bar is bars1[gemini_idx]:
            continue
        ax1.text(bar.get_x() + bar.get_width() / 2, val + 0.005,
                 f"{val:.3f}", ha="center", va="bottom", fontsize=9)

    bars2 = ax2.bar(x, cons, color=colors, edgecolor="black", linewidth=0.6)
    ax2.axhline(0.6, color="grey", linestyle=":", linewidth=0.8)
    ax2.text(len(MODEL_ORDER) - 0.4, 0.605, "all models > 0.6",
             fontsize=8, color="grey", style="italic")
    ax2.set_xticks(x)
    ax2.set_xticklabels(MODEL_ORDER, fontsize=10)
    ax2.set_ylabel("ECE (consistency)", fontsize=11)
    ax2.set_ylim(0, 1.0)
    ax2.set_title("Consistency extraction\n(3-rerun, T=0.7, n=2,415)",
                  fontsize=11)
    ax2.grid(axis="y", linestyle="--", alpha=0.35)
    for bar, val in zip(bars2, cons):
        ax2.text(bar.get_x() + bar.get_width() / 2, val + 0.012,
                 f"{val:.3f}", ha="center", va="bottom", fontsize=9)

    footer = (
        "Verbalized: keyword extraction (n=1,230 base runs).  "
        "Consistency: 3-rerun agreement at T=0.7 across 161 numeric-target tasks "
        "(Phase 1C full coverage; 10 CONCEPTUAL tasks excluded — "
        "self-consistency requires numerical answers).\n"
        "Method dichotomy follows Multi-Answer Confidence (2026)."
    )
    fig.text(0.5, -0.02, footer, ha="center", va="top", fontsize=8,
             style="italic", wrap=True)

    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=300, bbox_inches="tight", transparent=True)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
