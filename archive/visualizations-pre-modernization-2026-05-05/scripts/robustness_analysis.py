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

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_JSON = ROOT / "experiments" / "results_v2" / "robustness_v2.json"
OUT_FIG = ROOT / "report_materials" / "figures" / "robustness_heatmap.png"

PERT_TT_RE = re.compile(
    r"^(?P<base>.+?)_\d+(?:_(?P<pt>rephrase|numerical|semantic))?(?:_v\d+)?$"
)

MODELS = ["claude", "chatgpt", "gemini", "deepseek", "mistral"]

MODEL_COLORS = {
    "claude":   "#00CED1",
    "chatgpt":  "#7FFFD4",
    "gemini":   "#FF6B6B",
    "deepseek": "#4A90D9",
    "mistral":  "#A78BFA",
}

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
    cat_spans: list[tuple[str, int, int]] = []  # (cat, start_row, end_row)
    row = 0
    for cat in CATEGORY_ORDER:
        items = grouped.get(cat, [])
        if not items:
            continue
        cat_spans.append((cat, row, row + len(items) - 1))
        ordered_types.extend(items)
        row += len(items)

    # Matrix shape: (n_task_types, n_models) — transposed from horizontal layout.
    M = np.full((len(ordered_types), len(models)), np.nan)
    for i, tt in enumerate(ordered_types):
        for j, m in enumerate(models):
            cell = heatmap.get(m, {}).get(tt)
            if cell is not None:
                M[i, j] = cell["delta"]

    fig, ax = plt.subplots(figsize=(11, 14), dpi=150)
    fig.patch.set_alpha(0)

    vmax = float(np.nanmax(np.abs(M))) if np.isfinite(M).any() else 0.5
    vmax = max(vmax, 0.05)
    norm = mcolors.TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)
    cmap = plt.get_cmap("RdBu_r")

    im = ax.imshow(M, cmap=cmap, norm=norm, aspect="auto", origin="upper")

    # Models on TOP x-axis
    ax.set_xticks(range(len(models)))
    ax.set_xticklabels([m.upper() for m in models], fontsize=11, fontweight="bold")
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position("top")
    ax.tick_params(axis="x", which="major", pad=6)
    for tick, m in zip(ax.get_xticklabels(), models):
        tick.set_color(MODEL_COLORS.get(m, "#111"))

    # Task types on Y-axis, full row, monospace, no rotation
    ax.set_yticks(range(len(ordered_types)))
    ax.set_yticklabels(ordered_types, fontsize=8.5, family="monospace")

    for i in range(len(ordered_types)):
        for j in range(len(models)):
            v = M[i, j]
            if np.isnan(v):
                ax.text(j, i, "—", ha="center", va="center", fontsize=6, color="#888")
                continue
            if v == 0:
                continue
            txt_color = "#fff" if abs(v) >= 0.18 else "#1a1a1a"
            ax.text(j, i, f"{v:+.2f}", ha="center", va="center",
                    fontsize=7, color=txt_color, fontweight="bold")

    # Horizontal dividers between category bands
    for _, _, end_row in cat_spans[:-1]:
        ax.axhline(end_row + 0.5, color="#222", linewidth=1.4, alpha=0.85)

    # Category labels in left margin: horizontal text + vertical bracket.
    # Narrow categories (span ≤ 2 rows) use rotation=0 for legibility;
    # wider spans rotate 90° to anchor visually with the bracket.
    # All labels live left of the y-tick labels in axes-fraction coords
    # so they don't overlap monospace task-type names.
    n_models = len(models)
    bracket_x = -1.95
    label_horiz_x = -3.55
    label_vert_x = -3.30
    for cat, s, e in cat_spans:
        span = e - s + 1
        mid = (s + e) / 2
        if span <= 2:
            ax.text(label_horiz_x, mid, CATEGORY_LABEL.get(cat, cat),
                    ha="left", va="center", rotation=0,
                    fontsize=10, fontweight="bold", color="#222",
                    clip_on=False)
        else:
            ax.text(label_vert_x, mid, CATEGORY_LABEL.get(cat, cat),
                    ha="center", va="center", rotation=90,
                    fontsize=11, fontweight="bold", color="#222",
                    clip_on=False)
        ax.plot([bracket_x, bracket_x], [s - 0.4, e + 0.4],
                color="#444", linewidth=1.4, clip_on=False)
        for y_cap in (s - 0.4, e + 0.4):
            ax.plot([bracket_x, bracket_x + 0.20], [y_cap, y_cap],
                    color="#444", linewidth=1.4, clip_on=False)

    ax.set_xlim(-4.0, n_models - 0.5)

    ax.set_title(
        "Robustness Heatmap · Δ (base − perturbation) per task type × model",
        fontsize=12, fontweight="bold", pad=24,
    )
    cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
    cbar.set_label("Δ score (base − perturbation)\npositive = drop under perturbation",
                   fontsize=9)
    cbar.ax.tick_params(labelsize=8)

    ax.set_xticks(np.arange(-.5, len(models), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(ordered_types), 1), minor=True)
    ax.grid(which="minor", color="#ddd", linewidth=0.4)
    ax.tick_params(which="minor", length=0)
    ax.tick_params(which="major", length=0)

    OUT_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_FIG, dpi=150, transparent=True, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
