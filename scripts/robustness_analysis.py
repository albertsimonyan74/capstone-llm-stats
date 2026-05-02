"""Robustness analysis (RQ4 v2).

Visualization convention follows BrittleBench (arxiv 2603.13285) and
ReasonBench (arxiv 2512.07795): cluster columns by task category,
annotate cells where |Δ| exceeds threshold, label colorbar with the Δ
definition. Category taxonomy matches scripts/generate_group_a_figures.py
so robustness aligns with Group A's accuracy-by-category figure.

Computes per-model robustness as mean(base_score) - mean(perturbation_score)
across the 473 v2 perturbations (rephrase / numerical / semantic).

Inputs:
- experiments/results_v1/runs.jsonl       (base scores; filter to non-pert task_ids)
- experiments/results_v2/perturbation_runs.jsonl  (perturbation scores)

Outputs:
- experiments/results_v2/robustness_v2.json
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
BASE_RUNS = ROOT / "experiments" / "results_v1" / "runs.jsonl"
PERT_RUNS = ROOT / "experiments" / "results_v2" / "perturbation_runs.jsonl"
OUT_JSON = ROOT / "experiments" / "results_v2" / "robustness_v2.json"
OUT_FIG = ROOT / "report_materials" / "figures" / "robustness_heatmap.png"

PERT_SUFFIX_RE = re.compile(r"_(rephrase|numerical|semantic)(?:_v\d+)?$")
TASK_TYPE_RE = re.compile(r"^(.+?)_\d+$")

MODELS = ["claude", "chatgpt", "gemini", "deepseek", "mistral"]
PERT_TYPES = ["rephrase", "numerical", "semantic"]

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


def task_type_from_id(tid: str) -> str:
    m = TASK_TYPE_RE.match(tid)
    return m.group(1) if m else tid


def load_jsonl(path: Path):
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def is_perturbation(task_id: str) -> bool:
    return bool(PERT_SUFFIX_RE.search(task_id))


def main():
    base_scores: dict[tuple[str, str], float] = {}
    for r in load_jsonl(BASE_RUNS):
        tid = r.get("task_id", "")
        if not tid or is_perturbation(tid):
            continue
        score = r.get("final_score")
        if score is None:
            continue
        mf = r.get("model_family")
        if not mf:
            continue
        base_scores[(mf, tid)] = float(score)

    pert_records = []
    missing_base = 0
    for r in load_jsonl(PERT_RUNS):
        if r.get("error"):
            continue
        mf = r.get("model_family")
        base_tid = r.get("base_task_id")
        score = r.get("final_score")
        ptype = r.get("perturbation_type")
        if mf is None or base_tid is None or score is None or ptype is None:
            continue
        key = (mf, base_tid)
        if key not in base_scores:
            missing_base += 1
            continue
        pert_records.append(
            {
                "model": mf,
                "base_task_id": base_tid,
                "task_type": task_type_from_id(base_tid),
                "perturbation_type": ptype,
                "base_score": base_scores[key],
                "pert_score": float(score),
                "delta": base_scores[key] - float(score),
            }
        )

    by_model: dict[str, list[dict]] = defaultdict(list)
    for rec in pert_records:
        by_model[rec["model"]].append(rec)

    per_model = {}
    for m in MODELS:
        recs = by_model.get(m, [])
        if not recs:
            continue
        base_mean = statistics.fmean(r["base_score"] for r in recs)
        pert_mean = statistics.fmean(r["pert_score"] for r in recs)
        delta = base_mean - pert_mean
        per_pert = {}
        for pt in PERT_TYPES:
            sub = [r for r in recs if r["perturbation_type"] == pt]
            if not sub:
                continue
            bm = statistics.fmean(r["base_score"] for r in sub)
            pm = statistics.fmean(r["pert_score"] for r in sub)
            per_pert[pt] = {
                "n": len(sub),
                "base_mean": round(bm, 4),
                "pert_mean": round(pm, 4),
                "delta": round(bm - pm, 4),
            }
        per_model[m] = {
            "n": len(recs),
            "base_mean": round(base_mean, 4),
            "pert_mean": round(pert_mean, 4),
            "delta": round(delta, 4),
            "robustness": round(1.0 - delta, 4),
            "per_perturbation_type": per_pert,
        }

    ranking = sorted(per_model.items(), key=lambda kv: kv[1]["delta"])
    ranking_out = [
        {"rank": i + 1, "model": m, "delta": v["delta"], "robustness": v["robustness"]}
        for i, (m, v) in enumerate(ranking)
    ]

    task_types = sorted({r["task_type"] for r in pert_records})
    heatmap = {}
    for m in MODELS:
        row = {}
        for tt in task_types:
            sub = [r for r in by_model.get(m, []) if r["task_type"] == tt]
            if not sub:
                row[tt] = None
                continue
            bm = statistics.fmean(r["base_score"] for r in sub)
            pm = statistics.fmean(r["pert_score"] for r in sub)
            row[tt] = {"n": len(sub), "delta": round(bm - pm, 4)}
        heatmap[m] = row

    out = {
        "n_perturbations": len(pert_records),
        "n_base_scores": len(base_scores),
        "missing_base": missing_base,
        "per_model": per_model,
        "ranking": ranking_out,
        "per_task_type_heatmap": heatmap,
        "task_types": task_types,
        "models": MODELS,
        "perturbation_types": PERT_TYPES,
        "notes": (
            "robustness = 1 - delta where delta = mean(base_score) - mean(pert_score). "
            "Lower delta = more robust. Base scores from experiments/results_v1/runs.jsonl. "
            "Pert scores from experiments/results_v2/perturbation_runs.jsonl."
        ),
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2))
    print(f"Wrote {OUT_JSON}  (n={len(pert_records)}, missing_base={missing_base})")
    print("Ranking (best -> worst):")
    for r in ranking_out:
        print(f"  #{r['rank']} {r['model']:10s} delta={r['delta']:+.4f}  robustness={r['robustness']:.4f}")

    plot_heatmap(heatmap, task_types, MODELS)
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

    fig, ax = plt.subplots(figsize=(max(14, 0.34 * len(ordered_types)), 5.0), dpi=300)
    fig.patch.set_alpha(0)

    vmax = float(np.nanmax(np.abs(M))) if np.isfinite(M).any() else 0.5
    vmax = max(vmax, 0.05)
    cmap = plt.get_cmap("RdBu_r")

    im = ax.imshow(M, cmap=cmap, vmin=-vmax, vmax=vmax, aspect="auto")

    ax.set_xticks(range(len(ordered_types)))
    ax.set_xticklabels(ordered_types, rotation=60, ha="right", fontsize=7.5)
    ax.set_yticks(range(len(models)))
    ax.set_yticklabels([m.upper() for m in models], fontsize=11, fontweight="bold")
    # Color row labels by model color
    for tick, m in zip(ax.get_yticklabels(), models):
        tick.set_color(MODEL_COLORS.get(m, "#111"))

    for i in range(len(models)):
        for j in range(len(ordered_types)):
            v = M[i, j]
            if np.isnan(v):
                ax.text(j, i, "—", ha="center", va="center", fontsize=6, color="#888")
            elif abs(v) > 0.05:
                # Annotate only cells where |Δ| > 0.05
                txt_color = "#fff" if abs(v) > vmax * 0.55 else "#111"
                ax.text(j, i, f"{v:+.2f}", ha="center", va="center",
                        fontsize=7.0, color=txt_color, fontweight="bold")

    # Vertical separators between category groups + category band header
    for _, _, end_col in cat_spans[:-1]:
        ax.axvline(end_col + 0.5, color="#222", linewidth=1.4, alpha=0.85)
    n_rows = len(models)
    band_y = -0.85
    for cat, s, e in cat_spans:
        mid = (s + e) / 2
        ax.text(mid, band_y, CATEGORY_LABEL.get(cat, cat),
                ha="center", va="bottom", fontsize=10, fontweight="bold",
                color="#222")
        # underline
        ax.plot([s - 0.4, e + 0.4], [band_y - 0.08, band_y - 0.08],
                color="#222", linewidth=1.2, transform=ax.transData)

    ax.set_ylim(n_rows - 0.5, -1.4)  # extend top to fit category band

    ax.set_title(
        "Robustness Heatmap — Δ score (base − perturbation), clustered by category",
        fontsize=12, fontweight="bold", pad=24,
    )
    cbar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.01)
    cbar.set_label("Δ score (base − perturbation)\npositive = drop under perturbation",
                   fontsize=9)
    cbar.ax.tick_params(labelsize=8)

    ax.set_xticks(np.arange(-.5, len(ordered_types), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(models), 1), minor=True)
    ax.grid(which="minor", color="#ddd", linewidth=0.4)
    ax.tick_params(which="minor", length=0)

    fig.text(0.5, -0.02,
             "Category clustering follows BrittleBench (2026) + ReasonBench (2025); "
             "categories aligned with Group A figure conventions.",
             ha="center", fontsize=8, color="#444", alpha=0.85)

    OUT_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_FIG, dpi=300, transparent=True, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
