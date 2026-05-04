"""
Phase 1B Step 3 — recompute downstream analyses under literature-derived NMACR weights.

Reads experiments/results_v2/nmacr_scores_v2.jsonl (produced by recompute_scores.py)
and updates:

3a. experiments/results_v2/bootstrap_ci.json
3b. experiments/results_v2/robustness_v2.json (Layer 1 + Layer 2 per-dim deltas)
3c. experiments/results_v2/per_dim_calibration.json (NEW)
3d. experiments/results_v2/calibration.json (append accuracy_calibration_correlation)

Figures (regenerated from the recomputed data):
3b. report_materials/figures/a4b_per_dim_robustness.png (NEW)
3c. report_materials/figures/a5b_per_dim_calibration.png (NEW)
3e. report_materials/figures/three_rankings.png
3f. report_materials/figures/a2_accuracy_by_category.png
3g. report_materials/figures/a3_failure_heatmap.png
3h. report_materials/figures/a6_aggregate_ranking.png
3i. formatting_failure_rate_per_model embedded in /api/v2/headline_numbers source
    (added as a key inside calibration.json — the headline_numbers endpoint
     reads multiple files, so we surface this metric on the literature_v1 side
     in nmacr_scores_v2.jsonl header AND in audit/recompute_log.md.
     Backend exposure happens in the v2_routes update, not in this script.)
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
NMACR = ROOT / "experiments" / "results_v2" / "nmacr_scores_v2.jsonl"
TASKS_ALL = ROOT / "data" / "benchmark_v1" / "tasks_all.json"
TAXONOMY = ROOT / "experiments" / "results_v2" / "error_taxonomy_v2.json"
# v1-pert specs — used to filter v1-pert task_ids out of nmacr_scores rows that
# carry perturbation=False (historical mislabel: v1-pert rows were loaded into
# base runs.jsonl). Empty after B-2 cleanup.
V1_PERT_PATH = ROOT / "data" / "synthetic" / "perturbations.json"

OUT_BOOT = ROOT / "experiments" / "results_v2" / "bootstrap_ci.json"
OUT_ROB = ROOT / "experiments" / "results_v2" / "robustness_v2.json"
OUT_PERDIM_CAL = ROOT / "experiments" / "results_v2" / "per_dim_calibration.json"
CALIB = ROOT / "experiments" / "results_v2" / "calibration.json"

FIG_DIR = ROOT / "report_materials" / "figures"

MODELS = ["claude", "chatgpt", "gemini", "deepseek", "mistral"]
DIMS = ["N", "M", "A", "C", "R"]
COLORS = {
    "claude": "#00CED1",
    "chatgpt": "#7FFFD4",
    "gemini": "#FF6B6B",
    "deepseek": "#4A90D9",
    "mistral": "#A78BFA",
}
B = 10_000
SEED = 42


# ─── helpers ──────────────────────────────────────────────────────
def load_records() -> List[Dict[str, Any]]:
    v1_pert_ids: frozenset[str] = (
        frozenset(p["task_id"] for p in json.loads(V1_PERT_PATH.read_text()))
        if V1_PERT_PATH.exists() else frozenset()
    )
    out: List[Dict[str, Any]] = []
    skipped_v1 = 0
    with NMACR.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if "_header" in r:
                continue
            if r.get("task_id") in v1_pert_ids:
                skipped_v1 += 1
                continue
            out.append(r)
    if skipped_v1:
        print(f"load_records: filtered {skipped_v1} v1-pert rows; kept {len(out)}")
    return out


def bootstrap_mean_ci(values: np.ndarray, B: int, rng: np.random.Generator) -> Tuple[float, float, float, int]:
    n = len(values)
    if n == 0:
        return 0.0, 0.0, 0.0, 0
    idx = rng.integers(0, n, size=(B, n))
    samples = values[idx].mean(axis=1)
    lo, hi = np.percentile(samples, [2.5, 97.5])
    return float(values.mean()), float(lo), float(hi), int(n)


def separability(ci_map: Dict[str, Tuple[float, float, float, int]]) -> List[List[Any]]:
    out = []
    keys = list(ci_map.keys())
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = keys[i], keys[j]
            _, lo_a, hi_a, _ = ci_map[a]
            _, lo_b, hi_b, _ = ci_map[b]
            sep = "separable" if (hi_a < lo_b or hi_b < lo_a) else "not_separable"
            out.append([a, b, sep])
    return out


# ─── 3a — accuracy bootstrap ──────────────────────────────────────
def step_3a(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    rng = np.random.default_rng(SEED)
    by_model_acc: Dict[str, List[float]] = defaultdict(list)
    for r in records:
        if r["perturbation"]:
            continue
        if r["aggregate_new"] is None:
            continue
        by_model_acc[r["model"]].append(r["aggregate_new"])

    acc_ci = {
        m: bootstrap_mean_ci(np.asarray(by_model_acc[m]), B, rng)
        for m in MODELS if by_model_acc[m]
    }

    # robustness on aggregate_new — delta = base_score - perturbation_score, paired by base_task_id
    base_scores: Dict[Tuple[str, str], float] = {}
    for r in records:
        if r["perturbation"]:
            continue
        if r["aggregate_new"] is None:
            continue
        base_scores[(r["model"], r["task_id"])] = r["aggregate_new"]

    by_model_rob: Dict[str, List[float]] = defaultdict(list)
    for r in records:
        if not r["perturbation"]:
            continue
        if r["aggregate_new"] is None:
            continue
        m = r["model"]
        bid = r["base_task_id"]
        bs = base_scores.get((m, bid))
        if bs is None:
            continue
        by_model_rob[m].append(bs - r["aggregate_new"])

    rob_ci = {
        m: bootstrap_mean_ci(np.asarray(by_model_rob[m]), B, rng)
        for m in MODELS if by_model_rob[m]
    }

    out = {
        "B": B,
        "seed": SEED,
        "weighting_scheme": "literature_v1",
        "method": "non-parametric bootstrap on per-run aggregate_new (literature-weighted NMACR); 95% percentile CI",
        "accuracy": {
            m: {"mean": round(mean, 6), "ci_lower": round(lo, 6), "ci_upper": round(hi, 6), "n": n}
            for m, (mean, lo, hi, n) in acc_ci.items()
        },
        "robustness": {
            m: {"mean_delta": round(mean, 6), "ci_lower": round(lo, 6), "ci_upper": round(hi, 6), "n": n}
            for m, (mean, lo, hi, n) in rob_ci.items()
        },
        "separability": {
            "accuracy": separability(acc_ci),
            "robustness": separability(rob_ci),
        },
        "calibration_note": (
            "ECE point estimates per model; bootstrap CI requires binned resampling (deferred). "
            "See per_dim_calibration.json for per-NMACR-dimension ECE."
        ),
        "calibration_ece_points": _calibration_ece_points(),
    }
    OUT_BOOT.write_text(json.dumps(out, indent=2))
    return out


def _calibration_ece_points() -> Dict[str, float]:
    if not CALIB.exists():
        return {}
    d = json.loads(CALIB.read_text())
    out: Dict[str, float] = {}
    per_model = d.get("per_model") if isinstance(d, dict) and "per_model" in d else d
    for m in MODELS:
        e = per_model.get(m) if isinstance(per_model, dict) else None
        if isinstance(e, dict) and "ece" in e:
            out[m] = float(e["ece"])
    return out


# ─── 3b — robustness Layer 1 + Layer 2 per-dim ────────────────────
def step_3b(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    base_aggs: Dict[Tuple[str, str], Dict[str, float]] = {}
    for r in records:
        if r["perturbation"]:
            continue
        base_aggs[(r["model"], r["task_id"])] = {
            "agg": r["aggregate_new"],
            "N": r["dim_N"], "M": r["dim_M"], "A": r["dim_A"], "C": r["dim_C"], "R": r["dim_R"],
        }

    # Layer 1 — aggregate
    by_model: Dict[str, Dict[str, Any]] = {m: {"n": 0, "base_sum": 0.0, "pert_sum": 0.0,
                                                "per_perturbation_type": defaultdict(lambda: {
                                                    "n": 0, "base_sum": 0.0, "pert_sum": 0.0,
                                                })} for m in MODELS}
    by_task_type_heatmap: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))

    # Layer 2 — per-dim
    per_dim: Dict[str, Dict[str, Dict[str, Any]]] = {
        m: {d: {"n": 0, "delta_sum": 0.0} for d in DIMS} for m in MODELS
    }

    for r in records:
        if not r["perturbation"]:
            continue
        m = r["model"]
        bid = r["base_task_id"]
        base = base_aggs.get((m, bid))
        if base is None or base["agg"] is None or r["aggregate_new"] is None:
            continue
        delta_agg = base["agg"] - r["aggregate_new"]
        by_model[m]["n"] += 1
        by_model[m]["base_sum"] += base["agg"]
        by_model[m]["pert_sum"] += r["aggregate_new"]
        pt = r["perturbation_type"] or "unknown"
        bucket = by_model[m]["per_perturbation_type"][pt]
        bucket["n"] += 1
        bucket["base_sum"] += base["agg"]
        bucket["pert_sum"] += r["aggregate_new"]

        tt = r["task_type"]
        if tt:
            by_task_type_heatmap[tt][m].append(delta_agg)

        # per-dim
        for d in DIMS:
            base_d = base.get(d)
            pert_d = r.get(f"dim_{d}")
            if base_d is None or pert_d is None:
                continue
            per_dim[m][d]["n"] += 1
            per_dim[m][d]["delta_sum"] += (base_d - pert_d)

    per_model_out: Dict[str, Any] = {}
    ranking: List[Dict[str, Any]] = []
    for m in MODELS:
        info = by_model[m]
        if info["n"] == 0:
            continue
        base_mean = info["base_sum"] / info["n"]
        pert_mean = info["pert_sum"] / info["n"]
        delta = base_mean - pert_mean
        robustness = pert_mean / base_mean if base_mean > 0 else 0.0
        ppt: Dict[str, Any] = {}
        for pt, bucket in info["per_perturbation_type"].items():
            n = bucket["n"]
            if n == 0:
                continue
            ppt[pt] = {
                "n": n,
                "base_mean": round(bucket["base_sum"] / n, 4),
                "pert_mean": round(bucket["pert_sum"] / n, 4),
                "delta": round(bucket["base_sum"] / n - bucket["pert_sum"] / n, 4),
            }
        per_model_out[m] = {
            "n": info["n"],
            "base_mean": round(base_mean, 4),
            "pert_mean": round(pert_mean, 4),
            "delta": round(delta, 4),
            "robustness": round(robustness, 4),
            "per_perturbation_type": ppt,
        }
        ranking.append({"model": m, "delta": round(delta, 4), "robustness": round(robustness, 4)})

    ranking.sort(key=lambda x: x["delta"])
    for i, e in enumerate(ranking, 1):
        e["rank"] = i

    # per-dim deltas — mean per (model, dim)
    per_dim_out: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for m, dim_block in per_dim.items():
        per_dim_out[m] = {}
        for d, info in dim_block.items():
            n = info["n"]
            if n == 0:
                continue
            per_dim_out[m][d] = {
                "n": n,
                "mean_delta": round(info["delta_sum"] / n, 4),
            }

    # task-type heatmap — sample sizes vary; only emit means
    heatmap_out: Dict[str, Dict[str, float]] = {}
    for tt, mdict in by_task_type_heatmap.items():
        row: Dict[str, float] = {}
        for m, deltas in mdict.items():
            if deltas:
                row[m] = round(float(np.mean(deltas)), 4)
        if row:
            heatmap_out[tt] = row

    out = {
        "weighting_scheme": "literature_v1",
        "n_perturbations": sum(by_model[m]["n"] for m in MODELS),
        "n_base_scores": sum(1 for r in records if not r["perturbation"] and r["aggregate_new"] is not None),
        "missing_base": sum(
            1 for r in records
            if r["perturbation"] and base_aggs.get((r["model"], r["base_task_id"])) is None
        ),
        "models": [m for m in MODELS if m in per_model_out],
        "task_types": sorted(heatmap_out.keys()),
        "perturbation_types": sorted({
            pt for m in MODELS for pt in by_model[m]["per_perturbation_type"].keys()
        }),
        "per_model": per_model_out,
        "ranking": ranking,
        "per_dim_delta": per_dim_out,
        "per_task_type_heatmap": heatmap_out,
        "notes": (
            "Layer 1: aggregate_new-based delta per (model, perturbation_type). "
            "Layer 2 (NEW): per-NMACR-dimension delta per (model, dimension). "
            "Robustness = pert_mean / base_mean. Lower delta = more robust."
        ),
    }
    OUT_ROB.write_text(json.dumps(out, indent=2))
    return out


def fig_a4b_per_dim_robustness(rob: Dict[str, Any]) -> None:
    M = [m for m in MODELS if m in rob["per_dim_delta"]]
    matrix = np.full((len(M), len(DIMS)), np.nan)
    for i, m in enumerate(M):
        for j, d in enumerate(DIMS):
            cell = rob["per_dim_delta"][m].get(d)
            if cell:
                matrix[i, j] = cell["mean_delta"]

    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    vmax = np.nanmax(np.abs(matrix))
    vmax = max(vmax, 0.05)
    im = ax.imshow(matrix, cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="auto")
    ax.set_xticks(range(len(DIMS)))
    ax.set_xticklabels(DIMS, fontsize=11, fontweight="bold")
    ax.set_yticks(range(len(M)))
    ax.set_yticklabels([m.upper() for m in M], fontsize=10, fontweight="bold")
    ax.set_xlabel("NMACR dimension", fontsize=10)
    ax.set_title("Per-dimension robustness Δ (base − perturbation)", fontsize=11, fontweight="bold")

    for i in range(len(M)):
        for j in range(len(DIMS)):
            v = matrix[i, j]
            if np.isnan(v):
                continue
            text = f"{v:+.03f}"
            if abs(v) > 0.03:
                text += "*"
            color = "white" if abs(v) > vmax * 0.55 else "#111"
            ax.text(j, i, text, ha="center", va="center", color=color, fontsize=9)

    cbar = plt.colorbar(im, ax=ax, fraction=0.04, pad=0.04)
    cbar.set_label("Δ (negative = robust gain)", fontsize=9)
    fig.tight_layout()
    out = FIG_DIR / "a4b_per_dim_robustness.png"
    fig.savefig(out, dpi=300, transparent=True, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {out}")


# ─── 3c — per-dim calibration ECE ─────────────────────────────────
def step_3c(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Per-dim ECE: bucket the dim score to {low<0.4, med<0.7, high} as a calibration
    proxy. ECE = mean |bucket_center − overall_dim_mean| weighted by bucket size.
    Multi-dimensional extension of FermiEval (2025)."""
    BUCKETS = [(0.0, 0.4, 0.2), (0.4, 0.7, 0.55), (0.7, 1.0, 0.85)]
    per_dim_ece: Dict[str, Dict[str, float]] = {d: {} for d in DIMS}
    for d in DIMS:
        for m in MODELS:
            scores = [r[f"dim_{d}"] for r in records if not r["perturbation"]
                      and r["model"] == m and r[f"dim_{d}"] is not None]
            if not scores:
                continue
            arr = np.asarray(scores)
            ece_terms: List[float] = []
            n_total = len(arr)
            for lo, hi, center in BUCKETS:
                in_bucket = arr[(arr >= lo) & (arr < hi)] if hi < 1.0 else arr[(arr >= lo) & (arr <= hi)]
                if len(in_bucket) == 0:
                    continue
                weight = len(in_bucket) / n_total
                gap = abs(center - float(in_bucket.mean()))
                ece_terms.append(weight * gap)
            per_dim_ece[d][m] = round(float(sum(ece_terms)), 4)

    out = {
        "_methodology_citation": (
            "Multi-dimensional calibration extension of FermiEval (2025). "
            "Per NMACR dimension, bucket scores into {low<0.4, med<0.7, high}; "
            "ECE = sum_b w_b * |bucket_center - bucket_mean|. Lower = better calibrated."
        ),
        "buckets": [{"lo": lo, "hi": hi, "center": c} for lo, hi, c in BUCKETS],
        "per_dim_ece": per_dim_ece,
    }
    OUT_PERDIM_CAL.write_text(json.dumps(out, indent=2))
    return out


def fig_a5b_per_dim_calibration(cal: Dict[str, Any]) -> None:
    matrix = np.full((len(MODELS), len(DIMS)), np.nan)
    for i, m in enumerate(MODELS):
        for j, d in enumerate(DIMS):
            v = cal["per_dim_ece"].get(d, {}).get(m)
            if v is not None:
                matrix[i, j] = v

    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    vmax = np.nanmax(matrix)
    vmax = max(vmax, 0.1)
    im = ax.imshow(matrix, cmap="Greens_r", vmin=0.0, vmax=vmax, aspect="auto")
    ax.set_xticks(range(len(DIMS)))
    ax.set_xticklabels(DIMS, fontsize=11, fontweight="bold")
    ax.set_yticks(range(len(MODELS)))
    ax.set_yticklabels([m.upper() for m in MODELS], fontsize=10, fontweight="bold")
    ax.set_xlabel("NMACR dimension", fontsize=10)
    ax.set_title("Per-dimension calibration ECE (lower = better)", fontsize=11, fontweight="bold")

    for i in range(len(MODELS)):
        for j in range(len(DIMS)):
            v = matrix[i, j]
            if np.isnan(v):
                continue
            color = "white" if v < vmax * 0.4 else "#111"
            ax.text(j, i, f"{v:.03f}", ha="center", va="center", color=color, fontsize=9)

    cbar = plt.colorbar(im, ax=ax, fraction=0.04, pad=0.04)
    cbar.set_label("ECE", fontsize=9)
    fig.tight_layout()
    out = FIG_DIR / "a5b_per_dim_calibration.png"
    fig.savefig(out, dpi=300, transparent=True, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {out}")


# ─── 3d — accuracy-calibration correlation ───────────────────────
def step_3d(records: List[Dict[str, Any]]) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for m in MODELS:
        xs: List[float] = []
        ys: List[float] = []
        for r in records:
            if r["perturbation"]:
                continue
            if r["model"] != m:
                continue
            if r["aggregate_new"] is None or r["dim_C"] is None:
                continue
            xs.append(r["aggregate_new"])
            ys.append(r["dim_C"])
        if len(xs) < 3:
            continue
        x = np.asarray(xs)
        y = np.asarray(ys)
        if np.std(x) == 0 or np.std(y) == 0:
            out[m] = 0.0
            continue
        out[m] = round(float(np.corrcoef(x, y)[0, 1]), 4)

    # Append into calibration.json
    if CALIB.exists():
        d = json.loads(CALIB.read_text())
    else:
        d = {}
    d["accuracy_calibration_correlation"] = out
    d["accuracy_calibration_correlation_note"] = (
        "Pearson r between per-task aggregate_new (literature-weighted NMACR) "
        "and per-task confidence proxy (dim_C). Positive = well-calibrated "
        "answers tend to be accurate; negative = overconfident wrong / "
        "underconfident right."
    )
    d["formatting_failure_rate_per_model"] = _formatting_failure_rate(records)
    CALIB.write_text(json.dumps(d, indent=2))
    return out


def _formatting_failure_rate(records: List[Dict[str, Any]]) -> Dict[str, float]:
    counts: Dict[str, Dict[str, int]] = defaultdict(lambda: {"fail": 0, "total": 0})
    for r in records:
        if r["perturbation"]:
            continue
        m = r["model"]
        counts[m]["total"] += 1
        if r["formatting_failure"]:
            counts[m]["fail"] += 1
    return {
        m: round(c["fail"] / c["total"] * 100.0, 2) if c["total"] else 0.0
        for m, c in counts.items()
    }


# ─── 3e — three rankings ─────────────────────────────────────────
def fig_three_rankings(boot: Dict[str, Any], _rob: Dict[str, Any]) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5), dpi=300)
    fig.patch.set_alpha(0)

    # ACCURACY
    ax = axes[0]
    ax.patch.set_alpha(0)
    items = sorted(boot["accuracy"].items(), key=lambda kv: -kv[1]["mean"])
    xs = np.arange(len(items))
    means = [v["mean"] for _, v in items]
    los = [val["ci_lower"] for _, val in items]
    his = [val["ci_upper"] for _, val in items]
    err_lo = [mu - lo for mu, lo in zip(means, los)]
    err_hi = [hi - mu for hi, mu in zip(his, means)]
    for i, (m, _) in enumerate(items):
        ax.errorbar(xs[i], means[i], yerr=[[err_lo[i]], [err_hi[i]]], fmt="o",
                    color=COLORS[m], elinewidth=2.4, capsize=6, capthick=2,
                    markersize=10, markeredgecolor="#111", markeredgewidth=0.6)
    ax.set_xticks(xs)
    ax.set_xticklabels([m.upper() for m, _ in items], fontsize=9, fontweight="bold")
    ax.set_title("Accuracy (NMACR aggregate)", fontsize=10, fontweight="bold")
    ax.set_ylabel("mean aggregate_new", fontsize=9)
    ax.grid(axis="y", linestyle=":", linewidth=0.5, alpha=0.4)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)

    # ROBUSTNESS — lowest |delta| best
    ax = axes[1]
    ax.patch.set_alpha(0)
    items = sorted(boot["robustness"].items(), key=lambda kv: kv[1]["mean_delta"])
    xs = np.arange(len(items))
    means = [v["mean_delta"] for _, v in items]
    los = [val["ci_lower"] for _, val in items]
    his = [val["ci_upper"] for _, val in items]
    err_lo = [mu - lo for mu, lo in zip(means, los)]
    err_hi = [hi - mu for hi, mu in zip(his, means)]
    for i, (m, _) in enumerate(items):
        ax.errorbar(xs[i], means[i], yerr=[[err_lo[i]], [err_hi[i]]], fmt="s",
                    color=COLORS[m], elinewidth=2.4, capsize=6, capthick=2,
                    markersize=10, markeredgecolor="#111", markeredgewidth=0.6)
    ax.axhline(0, color="#666", linewidth=0.6)
    ax.set_xticks(xs)
    ax.set_xticklabels([m.upper() for m, _ in items], fontsize=9, fontweight="bold")
    ax.set_title("Robustness Δ (lower = robust)", fontsize=10, fontweight="bold")
    ax.set_ylabel("mean(base − perturbed)", fontsize=9)
    ax.grid(axis="y", linestyle=":", linewidth=0.5, alpha=0.4)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)

    # CALIBRATION (ECE — independent of weighting)
    ax = axes[2]
    ax.patch.set_alpha(0)
    eces = boot.get("calibration_ece_points", {})
    items = sorted(eces.items(), key=lambda kv: kv[1])
    xs = np.arange(len(items))
    for i, (m, ece) in enumerate(items):
        ax.bar(xs[i], ece, color=COLORS[m], edgecolor="#111", linewidth=0.5, width=0.7)
    ax.set_xticks(xs)
    ax.set_xticklabels([m.upper() for m, _ in items], fontsize=9, fontweight="bold")
    ax.set_title("Calibration ECE (lower = better)", fontsize=10, fontweight="bold")
    ax.set_ylabel("ECE (3-bucket weighted MAE)", fontsize=9)
    ax.grid(axis="y", linestyle=":", linewidth=0.5, alpha=0.4)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)

    fig.suptitle("Three rankings — accuracy ≠ robustness ≠ calibration",
                 fontsize=12, fontweight="bold", y=1.02)
    fig.text(0.5, -0.03,
             "NMACR weighted A=0.30, R=0.25, M=0.20, C=0.15, N=0.10 (literature-derived)",
             ha="center", fontsize=8, color="#666")
    fig.tight_layout()
    out = FIG_DIR / "three_rankings.png"
    fig.savefig(out, dpi=300, transparent=True, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {out}")


# ─── 3f — accuracy by category ────────────────────────────────────
TASK_CATEGORY: Dict[str, str] = {
    # Frequentist Estimation Theory
    "BIAS_VAR": "FREQUENTIST", "FISHER_INFO": "FREQUENTIST", "MSE_COMPARE": "FREQUENTIST",
    "OPT_SCALED": "FREQUENTIST", "RC_BOUND": "FREQUENTIST", "UNIFORM_MLE": "FREQUENTIST",
    "MLE_EFFICIENCY": "FREQUENTIST", "ORDER_STAT": "FREQUENTIST", "RANGE_DIST": "FREQUENTIST",
    # Conjugate Bayesian
    "BETA_BINOM": "CONJUGATE", "BINOM_FLAT": "CONJUGATE", "GAMMA_POISSON": "CONJUGATE",
    "NORMAL_GAMMA": "CONJUGATE", "DIRICHLET": "CONJUGATE", "JEFFREYS": "CONJUGATE",
    # Bayesian estimation / decision theory
    "DISC_MEDIAN": "BAYES_EST", "HPD": "BAYES_EST", "BAYES_RISK": "BAYES_EST",
    "MINIMAX": "BAYES_EST", "MLE_MAP": "BAYES_EST", "CI_CREDIBLE": "BAYES_EST",
    "PPC": "BAYES_EST", "BAYES_FACTOR": "BAYES_EST", "LOG_ML": "BAYES_EST",
    # Regression
    "REGRESSION": "REGRESSION", "BAYES_REG": "REGRESSION",
    # Markov chains / stochastic
    "MARKOV": "MARKOV", "STATIONARY": "MARKOV", "GAMBLER": "MARKOV", "BOX_MULLER": "MARKOV",
    # Phase 2 — Computational Bayes
    "GIBBS": "MCMC", "MH": "MCMC", "HMC": "MCMC", "RJMCMC": "MCMC",
    "VB": "ADVANCED", "ABC": "ADVANCED", "HIERARCHICAL": "ADVANCED",
    "CONCEPTUAL": "CONCEPTUAL",
}
CATEGORY_ORDER = ["CONJUGATE", "BAYES_EST", "FREQUENTIST", "REGRESSION", "MARKOV", "MCMC", "ADVANCED", "CONCEPTUAL"]


def fig_a2_by_category(records: List[Dict[str, Any]]) -> None:
    matrix = np.full((len(MODELS), len(CATEGORY_ORDER)), np.nan)
    for i, m in enumerate(MODELS):
        for j, cat in enumerate(CATEGORY_ORDER):
            vals = [r["aggregate_new"] for r in records
                    if not r["perturbation"]
                    and r["model"] == m
                    and r["aggregate_new"] is not None
                    and TASK_CATEGORY.get(r["task_type"]) == cat]
            if vals:
                matrix[i, j] = float(np.mean(vals))

    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=300)
    fig.patch.set_alpha(0); ax.patch.set_alpha(0)
    im = ax.imshow(matrix, cmap="viridis", vmin=0.0, vmax=1.0, aspect="auto")
    ax.set_xticks(range(len(CATEGORY_ORDER)))
    ax.set_xticklabels(CATEGORY_ORDER, fontsize=9, fontweight="bold", rotation=20, ha="right")
    ax.set_yticks(range(len(MODELS)))
    ax.set_yticklabels([m.upper() for m in MODELS], fontsize=10, fontweight="bold")
    ax.set_title("Mean aggregate_new by Bayesian category (literature-weighted)",
                 fontsize=11, fontweight="bold")
    for i in range(len(MODELS)):
        for j in range(len(CATEGORY_ORDER)):
            v = matrix[i, j]
            if np.isnan(v):
                continue
            color = "white" if v < 0.55 else "#111"
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", color=color, fontsize=9)
    plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02, label="mean aggregate_new")
    fig.tight_layout()
    out = FIG_DIR / "a2_accuracy_by_category.png"
    fig.savefig(out, dpi=300, transparent=True, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {out}")


# ─── 3g — failure heatmap (model × task_type fail rate) ─────────
def fig_a3_failure_heatmap(records: List[Dict[str, Any]]) -> None:
    types = sorted({r["task_type"] for r in records if not r["perturbation"] and r["task_type"]})
    matrix = np.full((len(MODELS), len(types)), np.nan)
    for i, m in enumerate(MODELS):
        for j, tt in enumerate(types):
            vals = [r["aggregate_new"] for r in records
                    if not r["perturbation"]
                    and r["model"] == m
                    and r["task_type"] == tt
                    and r["aggregate_new"] is not None]
            if vals:
                # failure rate at threshold 0.5
                fail = sum(1 for v in vals if v < 0.5) / len(vals)
                matrix[i, j] = fail

    fig, ax = plt.subplots(figsize=(max(11, 0.34 * len(types)), 4.5), dpi=300)
    fig.patch.set_alpha(0); ax.patch.set_alpha(0)
    im = ax.imshow(matrix, cmap="Reds", vmin=0.0, vmax=1.0, aspect="auto")
    ax.set_xticks(range(len(types)))
    ax.set_xticklabels(types, fontsize=8, rotation=70, ha="right")
    ax.set_yticks(range(len(MODELS)))
    ax.set_yticklabels([m.upper() for m in MODELS], fontsize=10, fontweight="bold")
    ax.set_title("Failure rate (aggregate_new < 0.5) per model × task_type",
                 fontsize=11, fontweight="bold")
    plt.colorbar(im, ax=ax, fraction=0.025, pad=0.02, label="failure rate")
    fig.tight_layout()
    out = FIG_DIR / "a3_failure_heatmap.png"
    fig.savefig(out, dpi=300, transparent=True, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {out}")


# ─── 3h — aggregate ranking dotplot + formatting_failure_rate column ─
def fig_a6_aggregate_ranking(records: List[Dict[str, Any]],
                              boot: Dict[str, Any]) -> None:
    fmt_rates = _formatting_failure_rate(records)
    items = sorted(boot["accuracy"].items(), key=lambda kv: -kv[1]["mean"])
    M = [m for m, _ in items]
    means = [v["mean"] for _, v in items]
    cis = [(v["ci_lower"], v["ci_upper"]) for _, v in items]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.0), dpi=300,
                             gridspec_kw={"width_ratios": [3, 1]})
    fig.patch.set_alpha(0)

    # Aggregate ranking
    ax = axes[0]
    ax.patch.set_alpha(0)
    ys = np.arange(len(M))[::-1]
    for i, m in enumerate(M):
        lo, hi = cis[i]
        ax.errorbar(means[i], ys[i], xerr=[[means[i] - lo], [hi - means[i]]],
                    fmt="o", color=COLORS[m], elinewidth=2.4, capsize=6,
                    capthick=2, markersize=11, markeredgecolor="#111", markeredgewidth=0.6)
        ax.text(means[i] + 0.005, ys[i] + 0.18, f"{means[i]:.3f}",
                fontsize=9, color="#111")
    ax.set_yticks(ys)
    ax.set_yticklabels([m.upper() for m in M], fontsize=10, fontweight="bold")
    ax.set_xlabel("Aggregate score (literature-weighted NMACR)", fontsize=10)
    ax.set_title("Aggregate ranking with 95% bootstrap CI", fontsize=11, fontweight="bold")
    ax.grid(axis="x", linestyle=":", linewidth=0.5, alpha=0.4)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)

    # formatting_failure_rate column
    ax = axes[1]
    ax.patch.set_alpha(0)
    for i, m in enumerate(M):
        rate = fmt_rates.get(m, 0.0)
        ax.barh(ys[i], rate, color=COLORS[m], edgecolor="#111", linewidth=0.5)
        ax.text(rate + 0.05, ys[i], f"{rate:.2f}%", va="center", fontsize=9)
    ax.set_yticks([])
    ax.set_xlabel("formatting_failure_rate (%)", fontsize=10)
    ax.set_title("Pre-rubric exclusions", fontsize=11, fontweight="bold")
    ax.set_xlim(0, max(max(fmt_rates.values(), default=0.0) * 1.5, 3.0))
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)

    fig.tight_layout()
    out = FIG_DIR / "a6_aggregate_ranking.png"
    fig.savefig(out, dpi=300, transparent=True, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {out}")


# ─── orchestrator ────────────────────────────────────────────────
def main() -> None:
    records = load_records()
    print(f"Loaded {len(records)} NMACR records "
          f"({sum(1 for r in records if not r['perturbation'])} base, "
          f"{sum(1 for r in records if r['perturbation'])} perturbation)")

    boot = step_3a(records)
    print(f"Wrote {OUT_BOOT}")

    rob = step_3b(records)
    print(f"Wrote {OUT_ROB}")
    fig_a4b_per_dim_robustness(rob)

    cal = step_3c(records)
    print(f"Wrote {OUT_PERDIM_CAL}")
    fig_a5b_per_dim_calibration(cal)

    corr = step_3d(records)
    print(f"accuracy_calibration_correlation: {corr}")
    print(f"Wrote {CALIB} (appended correlation + formatting_failure_rate)")

    fig_three_rankings(boot, rob)
    fig_a2_by_category(records)
    fig_a3_failure_heatmap(records)
    fig_a6_aggregate_ranking(records, boot)


if __name__ == "__main__":
    main()
