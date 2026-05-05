"""Robustness heatmap PNG (RQ4 v2).

Reads canonical experiments/results_v2/robustness_v2.json (written by
scripts/recompute_downstream.py) and aggregates per-perturbation Δ
values to base task_type for the heatmap visualization.

Visualization convention follows BrittleBench (arxiv 2603.13285) and
ReasonBench (arxiv 2512.07795): cluster columns by task category,
annotate cells where |Δ| exceeds threshold. Category taxonomy matches
scripts/generate_group_a_figures.py.

Output:
- report_materials/figures/robustness_heatmap.png
"""
from __future__ import annotations

import json
import re
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from site_palette import (
    SITE_BG, SITE_FG, SITE_FG_MUTED, MODEL_COLORS,
    apply_site_theme, style_colorbar,
)

apply_site_theme()

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_JSON = ROOT / "experiments" / "results_v2" / "robustness_v2.json"
OUT_FIG = ROOT / "report_materials" / "figures" / "robustness_heatmap.png"
OUT_FIG_FULL = ROOT / "report_materials" / "figures" / "robustness_heatmap_full.png"
WEB_OUT = ROOT / "capstone-website" / "frontend" / "public" / "visualizations" / "png" / "v2" / "robustness_heatmap.png"
WEB_OUT_FULL = ROOT / "capstone-website" / "frontend" / "public" / "visualizations" / "png" / "v2" / "robustness_heatmap_full.png"

PERT_TT_RE = re.compile(
    r"^(?P<base>.+?)_\d+(?:_(?P<pt>rephrase|numerical|semantic))?(?:_v\d+)?$"
)

MODELS = ["claude", "chatgpt", "gemini", "deepseek", "mistral"]

# Same 6-group taxonomy as scripts/generate_group_a_figures.py
CATEGORY_ORDER = ["BAYESIAN_CORE", "MLE_FREQ", "MCMC", "REGRESSION", "CAUSAL_PRED", "ADVANCED"]
CATEGORY_LABEL = {
    "BAYESIAN_CORE": "Bayesian Core",
    "MLE_FREQ":      "MLE / Freq.",
    "MCMC":          "MCMC",
    "REGRESSION":    "Regression",
    "CAUSAL_PRED":   "Causal / Pred.",
    "ADVANCED":      "Advanced",
}


def category_of(task_type: str) -> str:
    t = task_type
    if any(k in t for k in ["MCMC", "METROPOLIS", "GIBBS", "HMC", "RJMCMC", "STATIONARY", "MH"]):
        return "MCMC"
    if any(k in t for k in ["MLE", "BIAS_VAR", "FISHER", "CRAMER", "SUFFICIENCY", "RC_BOUND", "UNIFORM"]):
        return "MLE_FREQ"
    if any(k in t for k in ["BAYES", "BETA", "DIRICHLET", "CONJUGATE", "POSTERIOR", "PRIOR",
                              "BINOM_FLAT", "GAMMA_POISSON", "NORMAL_GAMMA", "JEFFREYS",
                              "HPD", "CI_CREDIBLE", "PPC"]):
        return "BAYESIAN_CORE"
    if any(k in t for k in ["REGRESSION", "GLM", "LOGISTIC"]):
        return "REGRESSION"
    if any(k in t for k in ["CAUSAL", "PREDICTION", "MARKOV", "HMM"]):
        return "CAUSAL_PRED"
    return "ADVANCED"


def main():
    canonical = json.loads(CANONICAL_JSON.read_text())
    raw = canonical["per_task_type_heatmap"]

    # Aggregate per-perturbation cells (e.g. "ABC_01_rephrase_v2" → base "ABC")
    # by mean Δ across all perturbations of each base task type.
    agg: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for tt, per_model_cell in raw.items():
        m = PERT_TT_RE.match(tt)
        base = m.group("base") if m else tt
        for model, val in per_model_cell.items():
            if val is None:
                continue
            if isinstance(val, dict):
                v = val.get("delta")
            else:
                v = val
            if v is None:
                continue
            agg[base][model].append(float(v))

    base_task_types = sorted(agg.keys())
    heatmap = {
        m: {
            tt: ({"delta": statistics.fmean(agg[tt][m])} if agg[tt].get(m) else None)
            for tt in base_task_types
        }
        for m in MODELS
    }

    print(f"Read {CANONICAL_JSON}")
    print(f"  {len(raw)} per-perturbation cells → {len(base_task_types)} base task types")
    plot_heatmap(heatmap, base_task_types, MODELS)
    print(f"Wrote {OUT_FIG}")


def plot_heatmap(heatmap, task_types, models):
    # Cluster rows by category, in CATEGORY_ORDER, alphabetical inside.
    grouped: dict[str, list[str]] = {c: [] for c in CATEGORY_ORDER}
    for tt in sorted(task_types):
        grouped.setdefault(category_of(tt), []).append(tt)
    ordered_types: list[str] = []
    cat_spans: list[tuple[str, int, int]] = []  # (cat, start_col, end_col)
    col = 0
    for cat in CATEGORY_ORDER:
        items = grouped.get(cat, [])
        if not items:
            continue
        cat_spans.append((cat, col, col + len(items) - 1))
        ordered_types.extend(items)
        col += len(items)

    # === HORIZONTAL VIEW (5 model rows × N task_type cols) — website card fit ===
    # Matrix shape: (n_models, n_task_types)
    M_h = np.full((len(models), len(ordered_types)), np.nan)
    for j, tt in enumerate(ordered_types):
        for i, m in enumerate(models):
            cell = heatmap.get(m, {}).get(tt)
            if cell is not None:
                M_h[i, j] = cell["delta"]

    vmax = float(np.nanmax(np.abs(M_h))) if np.isfinite(M_h).any() else 0.5
    vmax = max(vmax, 0.05)
    norm = mcolors.TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)
    cmap = plt.get_cmap("RdBu_r")

    # 15×8 → 1.875 aspect; after bbox_inches="tight" trim of padding +
    # colorbar gutter, final PNG lands ~1.6 (matches 16:10 site card).
    fig, ax = plt.subplots(figsize=(15, 8), dpi=150, facecolor=SITE_BG)
    ax.set_facecolor(SITE_BG)

    im = ax.imshow(M_h, cmap=cmap, norm=norm, aspect="auto", origin="upper")

    # Y-axis: models, color-coded.
    ax.set_yticks(range(len(models)))
    ax.set_yticklabels([m.upper() for m in models], fontsize=11, fontweight="bold")
    for tick, m in zip(ax.get_yticklabels(), models):
        tick.set_color(MODEL_COLORS.get(m, SITE_FG))
    ax.tick_params(axis="y", which="major", pad=4, length=0)

    # X-axis: task types rotated 80°, monospace, smaller.
    ax.set_xticks(range(len(ordered_types)))
    ax.set_xticklabels(ordered_types, fontsize=6.5, family="monospace",
                       color=SITE_FG_MUTED, rotation=80, ha="right")
    ax.tick_params(axis="x", which="major", length=0)

    # Cell labels — only |Δ| ≥ 0.10 to reduce crowding in horizontal layout.
    LABEL_THRESHOLD = 0.10
    for i in range(len(models)):
        for j in range(len(ordered_types)):
            v = M_h[i, j]
            if np.isnan(v):
                continue
            if abs(v) < LABEL_THRESHOLD:
                continue
            txt_color = "#fff" if abs(v) >= 0.18 else SITE_BG
            ax.text(j, i, f"{v:+.2f}", ha="center", va="center",
                    fontsize=6, color=txt_color, fontweight="bold")

    # Vertical dividers between category bands.
    for _, _, end_col in cat_spans[:-1]:
        ax.axvline(end_col + 0.5, color=SITE_FG_MUTED, linewidth=0.9, alpha=0.45)

    # Category headers above columns, staggered y-offsets to avoid overlap.
    y_above = -0.85
    y_above_alt = -1.45
    for idx, (cat, s, e) in enumerate(cat_spans):
        mid = (s + e) / 2
        # Stagger: alternate near/far above row so narrow neighbors don't collide.
        y_label = y_above if (idx % 2 == 0) else y_above_alt
        ax.text(mid, y_label, CATEGORY_LABEL.get(cat, cat),
                ha="center", va="bottom", rotation=0,
                fontsize=9.5, fontweight="bold", color=SITE_FG, clip_on=False)
        # Bracket connecting label to column range.
        ax.plot([s - 0.4, e + 0.4], [y_label + 0.15, y_label + 0.15],
                color=SITE_FG_MUTED, linewidth=1.0, alpha=0.5, clip_on=False)
        for x_cap in (s - 0.4, e + 0.4):
            ax.plot([x_cap, x_cap], [y_label + 0.15, y_label + 0.05],
                    color=SITE_FG_MUTED, linewidth=1.0, alpha=0.5, clip_on=False)

    ax.set_ylim(len(models) - 0.5, -1.95)

    ax.set_title(
        "Robustness Heatmap · Δ (base − perturbation) per task type × model",
        fontsize=12, fontweight="bold", color=SITE_FG, pad=44, loc="left")

    cbar = fig.colorbar(im, ax=ax, fraction=0.018, pad=0.015)
    style_colorbar(cbar, label="Δ score (positive = drop under perturbation)")

    ax.set_xticks(np.arange(-.5, len(ordered_types), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(models), 1), minor=True)
    ax.grid(which="minor", color=SITE_FG_MUTED, linewidth=0.3, alpha=0.15)
    ax.tick_params(which="minor", length=0)

    OUT_FIG.parent.mkdir(parents=True, exist_ok=True)
    WEB_OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_FIG, dpi=150, facecolor=SITE_BG, bbox_inches="tight")
    fig.savefig(WEB_OUT, dpi=150, facecolor=SITE_BG, bbox_inches="tight")
    plt.close(fig)

    # === FULL VERTICAL VIEW (preserved for §6 gallery + poster) ===
    _plot_heatmap_vertical(heatmap, models, ordered_types, cat_spans, cmap, norm)


def _plot_heatmap_vertical(heatmap, models, ordered_types, cat_spans, cmap, norm):
    """Full 38-row portrait version for poster + gallery — preserves
    individual task_type readability when card width isn't a constraint.
    """
    M = np.full((len(ordered_types), len(models)), np.nan)
    for i, tt in enumerate(ordered_types):
        for j, m in enumerate(models):
            cell = heatmap.get(m, {}).get(tt)
            if cell is not None:
                M[i, j] = cell["delta"]

    fig, ax = plt.subplots(figsize=(11, 14), dpi=150, facecolor=SITE_BG)
    ax.set_facecolor(SITE_BG)
    im = ax.imshow(M, cmap=cmap, norm=norm, aspect="auto", origin="upper")

    ax.set_xticks(range(len(models)))
    ax.set_xticklabels([m.upper() for m in models], fontsize=11, fontweight="bold")
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position("top")
    ax.tick_params(axis="x", which="major", pad=6)
    for tick, m in zip(ax.get_xticklabels(), models):
        tick.set_color(MODEL_COLORS.get(m, SITE_FG))

    ax.set_yticks(range(len(ordered_types)))
    ax.set_yticklabels(ordered_types, fontsize=8.5, family="monospace",
                       color=SITE_FG_MUTED)

    for i in range(len(ordered_types)):
        for j in range(len(models)):
            v = M[i, j]
            if np.isnan(v):
                ax.text(j, i, "—", ha="center", va="center", fontsize=6, color=SITE_FG_MUTED)
                continue
            if v == 0:
                continue
            txt_color = "#fff" if abs(v) >= 0.18 else SITE_BG
            ax.text(j, i, f"{v:+.2f}", ha="center", va="center",
                    fontsize=7, color=txt_color, fontweight="bold")

    for _, _, end_row in cat_spans[:-1]:
        ax.axhline(end_row + 0.5, color=SITE_FG_MUTED, linewidth=1.0, alpha=0.5)

    bracket_x = -1.95
    label_horiz_x = -3.55
    label_vert_x = -3.30
    for cat, s, e in cat_spans:
        span = e - s + 1
        mid = (s + e) / 2
        if span <= 2:
            ax.text(label_horiz_x, mid, CATEGORY_LABEL.get(cat, cat),
                    ha="left", va="center", rotation=0,
                    fontsize=10, fontweight="bold", color=SITE_FG, clip_on=False)
        else:
            ax.text(label_vert_x, mid, CATEGORY_LABEL.get(cat, cat),
                    ha="center", va="center", rotation=90,
                    fontsize=11, fontweight="bold", color=SITE_FG, clip_on=False)
        ax.plot([bracket_x, bracket_x], [s - 0.4, e + 0.4],
                color=SITE_FG_MUTED, linewidth=1.4, alpha=0.5, clip_on=False)
        for y_cap in (s - 0.4, e + 0.4):
            ax.plot([bracket_x, bracket_x + 0.20], [y_cap, y_cap],
                    color=SITE_FG_MUTED, linewidth=1.4, alpha=0.5, clip_on=False)

    ax.set_xlim(-4.0, len(models) - 0.5)
    ax.set_title(
        "Robustness Heatmap (full) · Δ (base − perturbation) per task type × model",
        fontsize=12, fontweight="bold", color=SITE_FG, pad=24)
    cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
    style_colorbar(cbar, label="Δ score (positive = drop under perturbation)")

    ax.set_xticks(np.arange(-.5, len(models), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(ordered_types), 1), minor=True)
    ax.grid(which="minor", color=SITE_FG_MUTED, linewidth=0.3, alpha=0.15)
    ax.tick_params(which="minor", length=0)
    ax.tick_params(which="major", length=0)

    OUT_FIG_FULL.parent.mkdir(parents=True, exist_ok=True)
    WEB_OUT_FULL.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_FIG_FULL, dpi=150, facecolor=SITE_BG, bbox_inches="tight")
    fig.savefig(WEB_OUT_FULL, dpi=150, facecolor=SITE_BG, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
