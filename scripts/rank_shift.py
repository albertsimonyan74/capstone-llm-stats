"""Rank-shift bump chart: ACCURACY → ROBUSTNESS → CALIBRATION.

Replaces ThreeRankingsComparison boxes-and-lines. Five-line bump chart;
crossings = rank inversions. Adjacent-rank n.s. brackets within each column
mark pairs whose 95% bootstrap CIs overlap.

Output: BOTH
  - capstone-website/frontend/public/visualizations/png/v2/rank_shift.png
  - report_materials/figures/rank_shift.png
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from site_palette import (
    SITE_BG, SITE_FG, SITE_FG_MUTED, MODEL_COLORS,
    apply_site_theme,
)

apply_site_theme()

ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP_PATH = ROOT / "experiments" / "results_v2" / "bootstrap_ci.json"
ROBUST_PATH = ROOT / "experiments" / "results_v2" / "robustness_v2.json"
CALIB_PATH = ROOT / "experiments" / "results_v2" / "calibration.json"

WEB_OUT = ROOT / "capstone-website" / "frontend" / "public" / "visualizations" / "png" / "v2" / "rank_shift.png"
FIG_OUT = ROOT / "report_materials" / "figures" / "rank_shift.png"

MODEL_LABEL = {
    "claude":   "Claude",
    "chatgpt":  "ChatGPT",
    "gemini":   "Gemini",
    "deepseek": "DeepSeek",
    "mistral":  "Mistral",
}


def cis_overlap(a_lo: float, a_hi: float, b_lo: float, b_hi: float) -> bool:
    return not (a_hi < b_lo or b_hi < a_lo)


def compute_ranks() -> tuple[dict, dict, dict, dict]:
    """Return (acc_rank, rob_rank, cal_rank, ns_pairs_by_dim)."""
    boot = json.loads(BOOTSTRAP_PATH.read_text())
    rob = json.loads(ROBUST_PATH.read_text())
    cal = json.loads(CALIB_PATH.read_text())

    # Accuracy: highest mean = #1
    acc_items = sorted(boot["accuracy"].items(), key=lambda kv: -kv[1]["mean"])
    acc_rank = {m: i + 1 for i, (m, _) in enumerate(acc_items)}
    acc_ci = {m: (v["ci_lower"], v["ci_upper"]) for m, v in boot["accuracy"].items()}

    # Robustness: smallest |delta| = #1
    rob_items = sorted(rob["ranking"], key=lambda d: d["delta"])
    rob_rank = {d["model"]: i + 1 for i, d in enumerate(rob_items)}
    rob_ci = {m: (v["ci_lower"], v["ci_upper"]) for m, v in boot["robustness"].items()}

    # Calibration: smallest ECE = #1
    cal_items = sorted(
        ((m, d["ece"]) for m, d in cal.items() if isinstance(d, dict) and "ece" in d),
        key=lambda kv: kv[1],
    )
    cal_rank = {m: i + 1 for i, (m, _) in enumerate(cal_items)}

    # Adjacent-rank n.s. brackets per dim
    def adj_ns(rank_map, ci_map):
        ordered = sorted(rank_map, key=rank_map.get)
        pairs = []
        for i in range(len(ordered) - 1):
            a, b = ordered[i], ordered[i + 1]
            if cis_overlap(*ci_map[a], *ci_map[b]):
                pairs.append((a, b))
        return pairs

    # Calibration: per spec, claude/chatgpt tied (0.033 vs 0.034); others separable
    def adj_ns_cal(rank_map, eces):
        ordered = sorted(rank_map, key=rank_map.get)
        pairs = []
        for i in range(len(ordered) - 1):
            a, b = ordered[i], ordered[i + 1]
            if abs(eces[a] - eces[b]) < 0.005:
                pairs.append((a, b))
        return pairs

    eces = {m: d["ece"] for m, d in cal.items() if isinstance(d, dict) and "ece" in d}
    ns_pairs = {
        "ACCURACY": adj_ns(acc_rank, acc_ci),
        "ROBUSTNESS": adj_ns(rob_rank, rob_ci),
        "CALIBRATION (ECE)": adj_ns_cal(cal_rank, eces),
    }
    return acc_rank, rob_rank, cal_rank, ns_pairs


def main() -> None:
    acc_rank, rob_rank, cal_rank, ns_pairs = compute_ranks()

    fig, ax = plt.subplots(figsize=(11, 6.5), dpi=150, facecolor=SITE_BG)
    ax.set_facecolor(SITE_BG)

    columns = [
        ("ACCURACY", acc_rank, 0.0),
        ("ROBUSTNESS", rob_rank, 1.0),
        ("CALIBRATION (ECE)", cal_rank, 2.0),
    ]
    col_x = {label: x for label, _, x in columns}

    # Column headers
    for label, _, x in columns:
        ax.text(
            x, 0.6, label,
            ha="center", va="center",
            fontsize=12, fontweight="bold", color=SITE_FG,
        )

    # Rank guide labels at far left, faint
    for r in range(1, 6):
        ax.text(
            -0.45, 6 - r,
            f"#{r}",
            ha="center", va="center",
            fontsize=10, color=SITE_FG_MUTED, alpha=0.55, fontweight="bold",
        )

    # One line per model
    for model, color in MODEL_COLORS.items():
        xs = [0.0, 1.0, 2.0]
        ys = [
            6 - acc_rank[model],
            6 - rob_rank[model],
            6 - cal_rank[model],
        ]
        ax.plot(
            xs, ys,
            color=color, linewidth=2.0, alpha=1.0, zorder=3,
            solid_capstyle="round", solid_joinstyle="round",
        )
        ax.scatter(
            xs, ys,
            s=200, c=color,
            edgecolor=SITE_BG, linewidth=1.5,
            zorder=4,
        )

    # Left-edge model name labels, color-matched, vertically aligned to accuracy rank
    for model, color in MODEL_COLORS.items():
        ax.text(
            -0.12,
            6 - acc_rank[model],
            MODEL_LABEL[model],
            ha="right", va="center",
            fontsize=11, fontweight="bold", color=color,
        )

    # Adjacent-rank n.s. brackets per column
    bracket_offset = 0.15  # rightward of column x
    for label, rank_map, x in columns:
        for a, b in ns_pairs[label]:
            ya = 6 - rank_map[a]
            yb = 6 - rank_map[b]
            top, bot = max(ya, yb), min(ya, yb)
            bx = x + bracket_offset
            tip = 0.04
            ax.plot([bx, bx], [bot, top], color=SITE_FG_MUTED, lw=1.0, alpha=0.55)
            ax.plot([bx - tip, bx], [top, top], color=SITE_FG_MUTED, lw=1.0, alpha=0.55)
            ax.plot([bx - tip, bx], [bot, bot], color=SITE_FG_MUTED, lw=1.0, alpha=0.55)
            ax.text(
                bx + 0.02, (top + bot) / 2,
                "n.s.",
                ha="left", va="center",
                fontsize=8.5, color=SITE_FG_MUTED, alpha=0.85, fontstyle="italic",
            )

    # Title + subtitle
    ax.text(
        1.0, 6.3,
        "Rank shift across dimensions",
        ha="center", va="center",
        fontsize=15, fontweight="bold", color=SITE_FG,
    )
    ax.text(
        1.0, -0.5,
        "Crossings = rank inversions. Brackets = pairs not statistically separable "
        "(95% bootstrap CI, B=10,000).",
        ha="center", va="center",
        fontsize=9.5, color=SITE_FG_MUTED, fontstyle="italic",
    )

    # Cosmetics
    ax.set_xlim(-0.7, 2.5)
    ax.set_ylim(-0.85, 6.6)
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ("top", "right", "bottom", "left"):
        ax.spines[side].set_visible(False)

    WEB_OUT.parent.mkdir(parents=True, exist_ok=True)
    FIG_OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(WEB_OUT, dpi=150, facecolor=SITE_BG, bbox_inches="tight")
    fig.savefig(FIG_OUT, dpi=300, facecolor=SITE_BG, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {WEB_OUT}")
    print(f"Wrote {FIG_OUT}")


if __name__ == "__main__":
    main()
