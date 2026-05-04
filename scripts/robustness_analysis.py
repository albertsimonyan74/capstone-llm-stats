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
    # Cluster columns by category, in CATEGORY_ORDER, then alphabetical inside.
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

    M = np.full((len(models), len(ordered_types)), np.nan)
    for i, m in enumerate(models):
        for j, tt in enumerate(ordered_types):
            cell = heatmap.get(m, {}).get(tt)
            if cell is not None:
                M[i, j] = cell["delta"]

    fig, ax = plt.subplots(figsize=(20, 6.5), dpi=150)
    fig.patch.set_alpha(0)

    vmax = float(np.nanmax(np.abs(M))) if np.isfinite(M).any() else 0.5
    vmax = max(vmax, 0.05)
    cmap = plt.get_cmap("RdBu_r")

    im = ax.imshow(M, cmap=cmap, vmin=-vmax, vmax=vmax, aspect="auto")

    ax.set_xticks(range(len(ordered_types)))
    ax.set_xticklabels(ordered_types, rotation=60, ha="right", fontsize=7)
    ax.set_yticks(range(len(models)))
    ax.set_yticklabels([m.upper() for m in models], fontsize=11, fontweight="bold")
    for tick, m in zip(ax.get_yticklabels(), models):
        tick.set_color(MODEL_COLORS.get(m, "#111"))

    SIGNIFICANCE_THRESHOLD = 0.08
    for i in range(len(models)):
        for j in range(len(ordered_types)):
            v = M[i, j]
            if np.isnan(v):
                ax.text(j, i, "—", ha="center", va="center", fontsize=6, color="#888")
            elif abs(v) >= SIGNIFICANCE_THRESHOLD:
                txt_color = "#fff" if abs(v) > vmax * 0.55 else "#111"
                ax.text(j, i, f"{v:+.2f}", ha="center", va="center",
                        fontsize=8, color=txt_color, fontweight="bold")

    for _, _, end_col in cat_spans[:-1]:
        ax.axvline(end_col + 0.5, color="#222", linewidth=1.4, alpha=0.85)
    n_rows = len(models)
    band_y_low, band_y_high = -1.15, -1.95
    last_y = None
    last_end = None
    for cat, s, e in cat_spans:
        # Stagger when adjacent header would visually overlap (heuristic: gap < 4 cols
        # between current midpoint and previous label end column).
        prefer_low = True
        if last_y == band_y_low and last_end is not None and (s - last_end) < 4:
            prefer_low = False
        elif last_y == band_y_high and last_end is not None and (s - last_end) < 4:
            prefer_low = True
        band_y = band_y_low if prefer_low else band_y_high
        mid = (s + e) / 2
        ax.text(mid, band_y, CATEGORY_LABEL.get(cat, cat),
                ha="center", va="center", fontsize=11, fontweight="bold",
                color="#222")
        ax.plot([s - 0.4, e + 0.4], [band_y + 0.42, band_y + 0.42],
                color="#222", linewidth=1.0, transform=ax.transData)
        last_y = band_y
        last_end = e

    ax.set_ylim(n_rows - 0.5, -2.5)

    ax.set_title(
        "Robustness Heatmap · Δ (base − perturbation) per model × task type",
        fontsize=13, fontweight="bold", pad=18,
    )
    cbar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.01)
    cbar.set_label("Δ score (base − perturbation)\npositive = drop under perturbation",
                   fontsize=9)
    cbar.ax.tick_params(labelsize=8)

    ax.set_xticks(np.arange(-.5, len(ordered_types), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(models), 1), minor=True)
    ax.grid(which="minor", color="#ddd", linewidth=0.4)
    ax.tick_params(which="minor", length=0)

    OUT_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_FIG, dpi=150, transparent=True, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
