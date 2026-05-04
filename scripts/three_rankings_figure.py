"""Three-rankings comparison figure: accuracy | robustness | calibration.

Poster centerpiece — visualizes that single-number leaderboards mislead.
Bootstrap CIs (B=10,000) used to mark statistically non-separable ranks.
Output: report_materials/figures/three_rankings.png (300 DPI, transparent).
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from site_palette import (
    SITE_BG, SITE_FG, SITE_FG_MUTED, MODEL_COLORS,
    apply_site_theme,
)

apply_site_theme()

ROOT = Path(__file__).resolve().parents[1]
CALIB_PATH = ROOT / "experiments" / "results_v2" / "calibration.json"
ROBUST_PATH = ROOT / "experiments" / "results_v2" / "robustness_v2.json"
BOOTSTRAP_PATH = ROOT / "experiments" / "results_v2" / "bootstrap_ci.json"
OUT_PATH = ROOT / "report_materials" / "figures" / "three_rankings.png"
MODEL_LABEL = {
    "claude": "Claude",
    "chatgpt": "ChatGPT",
    "gemini": "Gemini",
    "deepseek": "DeepSeek",
    "mistral": "Mistral",
}

ROBUSTNESS_PENDING = False

ACC_TOP_TIER = {"claude", "gemini"}
ACC_BOTTOM_TIER = {"chatgpt", "deepseek", "mistral"}
ROB_NS_MODELS = {"chatgpt", "deepseek"}


def load_calibration_ranking() -> list[tuple[str, float]]:
    data = json.loads(CALIB_PATH.read_text())
    items = [(m, d["ece"]) for m, d in data.items()]
    items.sort(key=lambda x: x[1])
    return items


def load_bootstrap() -> dict:
    return json.loads(BOOTSTRAP_PATH.read_text())


def load_accuracy_ranking(bootstrap: dict) -> list[tuple[str, float]]:
    items = [(m, d["mean"]) for m, d in bootstrap["accuracy"].items()]
    items.sort(key=lambda x: -x[1])
    return items


def load_robustness_ranking(bootstrap: dict) -> list[tuple[str, float]]:
    items = [(m, d["mean_delta"]) for m, d in bootstrap["robustness"].items()]
    items.sort(key=lambda x: x[1])
    return items


def draw_column(ax, x_center, ranking, header, score_fmt, *, pending=False,
                annotations=None):
    box_w = 0.22
    box_h = 0.105
    y_top = 0.78
    dy = 0.135
    annotations = annotations or {}

    ax.text(
        x_center,
        0.94,
        header,
        ha="center",
        va="center",
        fontsize=15,
        fontweight="bold",
        color=SITE_FG,
    )

    rank_centers = {}
    for rank, (model, score) in enumerate(ranking, start=1):
        y = y_top - (rank - 1) * dy
        color = MODEL_COLORS[model]
        face = color if not pending else "#cccccc"
        edge = SITE_BG if not pending else SITE_FG_MUTED
        alpha = 1.0 if not pending else 0.45

        box = FancyBboxPatch(
            (x_center - box_w / 2, y - box_h / 2),
            box_w,
            box_h,
            boxstyle="round,pad=0.005,rounding_size=0.012",
            linewidth=1.4,
            facecolor=face,
            edgecolor=edge,
            alpha=alpha,
        )
        ax.add_patch(box)

        ax.text(
            x_center - box_w / 2 - 0.018,
            y,
            f"#{rank}",
            ha="right",
            va="center",
            fontsize=12,
            fontweight="bold",
            color=SITE_FG_MUTED if not pending else "#888",
        )

        ax.text(
            x_center,
            y + 0.012,
            MODEL_LABEL[model],
            ha="center",
            va="center",
            fontsize=12,
            fontweight="bold",
            color=SITE_BG,
            alpha=alpha,
        )
        score_txt = score_fmt(score) if score is not None else "—"
        ax.text(
            x_center,
            y - 0.022,
            score_txt,
            ha="center",
            va="center",
            fontsize=9.5,
            color=SITE_BG,
            alpha=alpha,
        )

        ann = annotations.get(model)
        if ann:
            ax.text(
                x_center + box_w / 2 + 0.012,
                y,
                ann,
                ha="left",
                va="center",
                fontsize=9.5,
                fontweight="bold",
                color="#f87171",
            )

        rank_centers[model] = (x_center + box_w / 2, x_center - box_w / 2, y)

    if pending:
        ax.text(
            x_center,
            (y_top + (y_top - 4 * dy)) / 2,
            "PENDING",
            ha="center",
            va="center",
            fontsize=34,
            fontweight="bold",
            color=SITE_FG_MUTED,
            alpha=0.28,
            rotation=20,
        )

    return rank_centers


def draw_tier_bracket(ax, x_left, y_top, y_bot, label, *, color=None):
    if color is None:
        color = SITE_FG_MUTED
    """Vertical bracket on the left side spanning rows; label sits beside it."""
    tip = 0.012
    bx = x_left
    ax.plot([bx, bx], [y_bot, y_top], color=color, lw=1.4, solid_capstyle="round")
    ax.plot([bx, bx + tip], [y_top, y_top], color=color, lw=1.4)
    ax.plot([bx, bx + tip], [y_bot, y_bot], color=color, lw=1.4)
    ax.text(
        bx - 0.008,
        (y_top + y_bot) / 2,
        label,
        ha="right",
        va="center",
        fontsize=8.5,
        color=color,
        fontweight="bold",
        rotation=90,
    )


def draw_arrow(ax, start_xy, end_xy, color, *, lw=1.6, alpha=0.85, highlight=False):
    style = "->,head_width=4,head_length=5"
    arrow = FancyArrowPatch(
        start_xy,
        end_xy,
        arrowstyle=style,
        connectionstyle="arc3,rad=0.0",
        color=color,
        linewidth=lw if not highlight else 3.2,
        alpha=alpha,
        mutation_scale=14,
        zorder=5 if not highlight else 10,
    )
    ax.add_patch(arrow)


def main():
    fig, ax = plt.subplots(figsize=(10, 8), dpi=300, facecolor=SITE_BG)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_axis_off()
    ax.set_facecolor(SITE_BG)

    bootstrap = load_bootstrap()
    accuracy_ranking = load_accuracy_ranking(bootstrap)
    robust_ranking = load_robustness_ranking(bootstrap)
    calib_ranking = load_calibration_ranking()

    x_acc, x_rob, x_cal = 0.16, 0.50, 0.84

    rob_annotations = {m: "n.s." for m in ROB_NS_MODELS}

    acc_pos = draw_column(
        ax, x_acc, accuracy_ranking, "ACCURACY", lambda s: f"{s:.3f}",
    )
    rob_pos = draw_column(
        ax, x_rob, robust_ranking, "ROBUSTNESS (Δ)",
        lambda s: f"{s:+.4f}",
        pending=ROBUSTNESS_PENDING,
        annotations=rob_annotations,
    )
    cal_pos = draw_column(
        ax, x_cal, calib_ranking, "CALIBRATION (ECE)", lambda s: f"{s:.3f}",
    )

    box_h = 0.105
    bracket_x = x_acc - 0.22 / 2 - 0.052
    top_y_top = acc_pos[accuracy_ranking[0][0]][2] + box_h / 2
    top_y_bot = acc_pos[accuracy_ranking[1][0]][2] - box_h / 2
    bot_y_top = acc_pos[accuracy_ranking[2][0]][2] + box_h / 2
    bot_y_bot = acc_pos[accuracy_ranking[4][0]][2] - box_h / 2
    draw_tier_bracket(ax, bracket_x, top_y_top, top_y_bot, "tied top tier")
    draw_tier_bracket(ax, bracket_x, bot_y_top, bot_y_bot, "tied bottom tier")

    acc_rank = {m: i for i, (m, _) in enumerate(accuracy_ranking, start=1)}
    rob_rank = {m: i for i, (m, _) in enumerate(robust_ranking, start=1)}
    cal_rank = {m: i for i, (m, _) in enumerate(calib_ranking, start=1)}

    for model in MODEL_COLORS:
        a_right = acc_pos[model][0]
        a_y = acc_pos[model][2]
        r_left = rob_pos[model][1]
        r_right = rob_pos[model][0]
        r_y = rob_pos[model][2]
        c_left = cal_pos[model][1]
        c_y = cal_pos[model][2]
        moved_ar = acc_rank[model] != rob_rank[model]
        moved_rc = rob_rank[model] != cal_rank[model]
        highlight = model in {"claude", "chatgpt"}
        color = MODEL_COLORS[model]
        draw_arrow(
            ax,
            (a_right + 0.005, a_y),
            (r_left - 0.005, r_y),
            color,
            lw=1.4 if moved_ar else 0.9,
            alpha=0.9 if moved_ar else 0.35,
            highlight=highlight,
        )
        draw_arrow(
            ax,
            (r_right + 0.005, r_y),
            (c_left - 0.005, c_y),
            color,
            lw=1.4 if moved_rc else 0.9,
            alpha=0.9 if moved_rc else 0.35,
            highlight=highlight,
        )

    ax.text(
        0.5,
        0.075,
        "Single-number leaderboards mislead: rank changes across dimensions.",
        ha="center",
        va="center",
        fontsize=11,
        style="italic",
        color=SITE_FG,
    )
    ax.text(
        0.5,
        0.043,
        "Highlighted: ChatGPT moves from Accuracy #5 to Calibration #1; Claude leads Accuracy but #2 on Calibration.",
        ha="center",
        va="center",
        fontsize=9.5,
        color=SITE_FG_MUTED,
    )
    ax.text(
        0.5,
        0.012,
        "Brackets indicate statistically non-separable ranks (95% bootstrap CI, B=10,000); "
        "n.s. = Δ not separable from zero.",
        ha="center",
        va="center",
        fontsize=8.5,
        style="italic",
        color=SITE_FG_MUTED,
    )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PATH, dpi=300, facecolor=SITE_BG, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
