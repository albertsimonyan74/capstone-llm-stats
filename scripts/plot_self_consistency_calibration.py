"""Two-panel calibration figure: verbalized ECE vs self-consistency ECE.

Left panel: Verbalized ECE per model (post-Phase-1.8 truly-base, n=855).
Right panel: Consistency ECE per model (Phase 1C full coverage, 161 numeric tasks).

Verbalized values come from canonical `calibration.json` (post-Phase-1.8).
Consistency values come from `self_consistency_calibration.json` (Phase 1C full).
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from site_palette import (
    SITE_BG, SITE_FG, SITE_FG_MUTED, MODEL_COLORS,
    apply_site_theme, color_code_model_ticks, dim_remaining_spines,
)

apply_site_theme()

ROOT = Path(__file__).resolve().parent.parent
VERB_CAL = ROOT / "experiments" / "results_v2" / "calibration.json"
SC_CAL = ROOT / "experiments" / "results_v2" / "self_consistency_calibration.json"
OUT = ROOT / "report_materials" / "figures" / "self_consistency_calibration.png"
WEB_OUT = ROOT / "capstone-website" / "frontend" / "public" / "visualizations" / "png" / "v2" / "self_consistency_calibration.png"

MODEL_ORDER = ["claude", "chatgpt", "gemini", "deepseek", "mistral"]


def main() -> None:
    verb_data = json.loads(VERB_CAL.read_text())
    sc_data = json.loads(SC_CAL.read_text())
    sc_cmp = sc_data["ece_comparison_full"]

    verb = [verb_data[m]["ece"] for m in MODEL_ORDER]
    cons = [sc_cmp[m]["consistency_ece_full"] for m in MODEL_ORDER]
    colors = [MODEL_COLORS[m] for m in MODEL_ORDER]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5.5), facecolor=SITE_BG)
    x = np.arange(len(MODEL_ORDER))

    # === LEFT: Verbalized ECE ===
    ax1.set_facecolor(SITE_BG)
    bars1 = ax1.bar(x, verb, color=colors, edgecolor=SITE_BG, linewidth=1.5)
    ax1.set_xticks(x)
    ax1.set_xticklabels(MODEL_ORDER, fontsize=10)
    color_code_model_ticks(ax1)
    ax1.set_ylabel("ECE (verbalized)", fontsize=11, color=SITE_FG_MUTED)
    ax1.set_ylim(0, max(verb) * 1.30)
    ax1.set_title("Verbalized extraction\n(keyword, n=855 truly-base runs)",
                  fontsize=11, fontweight="bold", color=SITE_FG, pad=10)
    ax1.grid(axis="y", linestyle="-", alpha=0.06, color="#ffffff")
    ax1.set_axisbelow(True)
    dim_remaining_spines(ax1)
    for bar, val in zip(bars1, verb):
        ax1.text(bar.get_x() + bar.get_width() / 2, val + max(verb) * 0.025,
                 f"{val:.3f}", ha="center", va="bottom",
                 fontsize=9, fontweight="600", color=SITE_FG)

    # === RIGHT: Consistency ECE ===
    ax2.set_facecolor(SITE_BG)
    bars2 = ax2.bar(x, cons, color=colors, edgecolor=SITE_BG, linewidth=1.5)
    ax2.axhline(0.6, color=SITE_FG_MUTED, linestyle=":", linewidth=1.2, alpha=0.7, zorder=0)
    ax2.text(-0.45, 0.605, "0.6", fontsize=8, color=SITE_FG_MUTED,
             ha="left", va="bottom", style="italic")
    ax2.text(2, 0.93,
             "all models > 0.6 — severe overconfidence",
             fontsize=9, color=SITE_FG, style="italic",
             ha="center", va="center",
             bbox=dict(facecolor="rgba(15,19,28,0.96)" if False else SITE_BG,
                       edgecolor=SITE_FG_MUTED,
                       boxstyle="round,pad=0.4", alpha=0.9))
    ax2.set_xticks(x)
    ax2.set_xticklabels(MODEL_ORDER, fontsize=10)
    color_code_model_ticks(ax2)
    ax2.set_ylabel("ECE (consistency)", fontsize=11, color=SITE_FG_MUTED)
    ax2.set_ylim(0, 1.0)
    ax2.set_title("Self-consistency extraction\n(3-rerun, T=0.7, n=2,415 reruns)",
                  fontsize=11, fontweight="bold", color=SITE_FG, pad=10)
    ax2.grid(axis="y", linestyle="-", alpha=0.06, color="#ffffff")
    ax2.set_axisbelow(True)
    dim_remaining_spines(ax2)
    for bar, val in zip(bars2, cons):
        ax2.text(bar.get_x() + bar.get_width() / 2, val + 0.015,
                 f"{val:.3f}", ha="center", va="bottom",
                 fontsize=9, fontweight="600", color=SITE_FG)

    footer = (
        "Verbalized: keyword extraction across 855 truly-base runs (171 tasks × 5 models, post-Phase-1.8 scope).  "
        "Self-consistency: 3-rerun agreement at T=0.7 across 161 numeric-target tasks "
        "(Phase 1C full coverage; 10 CONCEPTUAL tasks excluded — self-consistency requires numerical answers).\n"
        "Method dichotomy follows Multi-Answer Confidence (2026)."
    )
    fig.text(0.5, -0.02, footer, ha="center", va="top", fontsize=8,
             style="italic", color=SITE_FG_MUTED, wrap=True)

    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=300, bbox_inches="tight", facecolor=SITE_BG)
    WEB_OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(WEB_OUT, dpi=300, bbox_inches="tight", facecolor=SITE_BG)
    print(f"wrote {OUT}")
    print(f"wrote {WEB_OUT}")


if __name__ == "__main__":
    main()
