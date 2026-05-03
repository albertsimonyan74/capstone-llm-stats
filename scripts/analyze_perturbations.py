#!/usr/bin/env python3
"""
analyze_perturbations.py  — RQ4 robustness analysis

Compares LLM scores on perturbed tasks vs. their base tasks.
Outputs experiments/results_v1/rq4_analysis.json

Metrics per model × perturbation_type:
  sensitivity       mean |score_pert - score_base|
  robustness        1 - sensitivity
  pass_consistency  fraction where pass(base) == pass(pert)
  pass_degradation  fraction where base passed but pert failed
  avg_delta         mean (score_pert - score_base)   [signed]

Run from project root: python scripts/analyze_perturbations.py
"""
from __future__ import annotations

import json
import os
import sys
from collections import defaultdict
from statistics import mean, stdev
from datetime import datetime, timezone

ROOT          = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS_PATH     = os.path.join(ROOT, "experiments", "results_v1", "runs.jsonl")
PERT_PATH     = os.path.join(ROOT, "data", "synthetic", "perturbations_all.json")
OUTPUT_PATH   = os.path.join(ROOT, "experiments", "results_v1", "rq4_analysis.json")


def load_runs() -> list[dict]:
    runs = []
    with open(RUNS_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
                if r.get("model_family") and r.get("task_id"):
                    runs.append(r)
            except json.JSONDecodeError:
                pass
    return runs


def load_perturbations() -> dict[str, dict]:
    """Return {task_id: perturbation_record}."""
    with open(PERT_PATH) as f:
        pert = json.load(f)
    return {p["task_id"]: p for p in pert}


def safe_mean(lst: list[float]) -> float:
    return mean(lst) if lst else 0.0


def analyze() -> dict:
    runs = load_runs()
    pert_map = load_perturbations()
    pert_ids = set(pert_map)

    # Index: (model_family, task_id) → run record
    run_index: dict[tuple[str, str], dict] = {}
    for r in runs:
        key = (r["model_family"], r["task_id"])
        if key not in run_index or not run_index[key].get("error"):
            run_index[key] = r

    # Collect all (model, base_task_id, pert_type) triples
    # Structure: {model: {base_task_id: {pert_type: run}}}
    by_model_base_type: dict[str, dict[str, dict[str, dict]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    for tid, p in pert_map.items():
        base_id = p["base_task_id"]
        ptype   = p["perturbation_type"]
        for model in set(r["model_family"] for r in runs):
            key = (model, tid)
            if key in run_index:
                by_model_base_type[model][base_id][ptype] = run_index[key]

    # Also index base task runs
    base_run_index: dict[tuple[str, str], dict] = {}
    for r in runs:
        if r["task_id"] not in pert_ids:
            key = (r["model_family"], r["task_id"])
            if key not in base_run_index or not base_run_index[key].get("error"):
                base_run_index[key] = r

    PERT_TYPES = ["rephrase", "numerical", "semantic"]

    # ── Per-model analysis ─────────────────────────────────────────────────────

    model_summaries: dict[str, dict] = {}
    global_by_type: dict[str, list[float]] = defaultdict(list)   # abs deltas across models
    per_task_rows: list[dict] = []

    for model, base_map in by_model_base_type.items():
        # per_type accumulates for this model
        per_type: dict[str, dict[str, list]] = {
            pt: {"sensitivity": [], "delta": [], "pass_consistent": [], "pass_degrade": []}
            for pt in PERT_TYPES
        }
        overall_sensitivity: list[float] = []

        for base_id, type_runs in base_map.items():
            base_key = (model, base_id)
            base_run = base_run_index.get(base_key)
            if base_run is None or base_run.get("error"):
                continue

            base_score = base_run.get("final_score") or 0.0
            base_pass  = bool(base_run.get("pass"))

            for ptype in PERT_TYPES:
                prun = type_runs.get(ptype)
                if prun is None or prun.get("error"):
                    continue
                pert_score = prun.get("final_score") or 0.0
                pert_pass  = bool(prun.get("pass"))
                delta      = pert_score - base_score
                abs_delta  = abs(delta)

                per_type[ptype]["sensitivity"].append(abs_delta)
                per_type[ptype]["delta"].append(delta)
                per_type[ptype]["pass_consistent"].append(int(base_pass == pert_pass))
                per_type[ptype]["pass_degrade"].append(int(base_pass and not pert_pass))
                overall_sensitivity.append(abs_delta)
                global_by_type[ptype].append(abs_delta)

                per_task_rows.append({
                    "model":            model,
                    "base_task_id":     base_id,
                    "perturbation_type": ptype,
                    "base_score":       round(base_score, 4),
                    "pert_score":       round(pert_score, 4),
                    "delta":            round(delta,       4),
                    "abs_delta":        round(abs_delta,   4),
                    "base_pass":        base_pass,
                    "pert_pass":        pert_pass,
                    "pass_consistent":  base_pass == pert_pass,
                    "pass_degraded":    base_pass and not pert_pass,
                })

        # Build model summary
        type_breakdown: dict[str, dict] = {}
        for pt in PERT_TYPES:
            d = per_type[pt]
            n = len(d["sensitivity"])
            if n == 0:
                continue
            type_breakdown[pt] = {
                "n":                n,
                "sensitivity":      round(safe_mean(d["sensitivity"]), 4),
                "robustness":       round(1 - safe_mean(d["sensitivity"]), 4),
                "avg_delta":        round(safe_mean(d["delta"]),       4),
                "pass_consistency": round(safe_mean(d["pass_consistent"]), 4),
                "pass_degradation": round(safe_mean(d["pass_degrade"]),   4),
            }

        overall_n    = len(overall_sensitivity)
        overall_sens = safe_mean(overall_sensitivity)
        model_summaries[model] = {
            "n_triplets":        overall_n,
            "sensitivity":       round(overall_sens,        4),
            "robustness":        round(1 - overall_sens,    4),
            "sensitivity_std":   round(stdev(overall_sensitivity) if len(overall_sensitivity) > 1 else 0.0, 4),
            "by_perturbation_type": type_breakdown,
        }

    # ── Cross-model summary by perturbation type ───────────────────────────────

    cross_model_by_type: dict[str, dict] = {}
    for pt in PERT_TYPES:
        deltas = global_by_type[pt]
        cross_model_by_type[pt] = {
            "n":           len(deltas),
            "sensitivity": round(safe_mean(deltas), 4),
            "robustness":  round(1 - safe_mean(deltas), 4),
        }

    # ── Hardest / easiest base tasks ──────────────────────────────────────────

    # Group per_task_rows by base_task_id to find most/least sensitive
    base_sens: dict[str, list[float]] = defaultdict(list)
    for row in per_task_rows:
        base_sens[row["base_task_id"]].append(row["abs_delta"])

    base_sens_avg = {bid: safe_mean(vals) for bid, vals in base_sens.items()}
    sorted_base = sorted(base_sens_avg.items(), key=lambda x: x[1])
    most_robust_tasks   = [b for b, _ in sorted_base[:5]]
    least_robust_tasks  = [b for b, _ in sorted_base[-5:]]

    return {
        "generated_at":           datetime.now(timezone.utc).isoformat(),
        "description":            "RQ4 robustness analysis — perturbation sensitivity across 3 types (rephrase/numerical/semantic)",
        "n_base_tasks":           len({r["base_task_id"] for r in per_task_rows}),
        "n_perturbation_types":   3,
        "models":                 sorted(model_summaries),
        "by_model":               model_summaries,
        "cross_model_by_type":    cross_model_by_type,
        "most_robust_tasks":      most_robust_tasks,
        "least_robust_tasks":     least_robust_tasks,
        "per_task_detail":        per_task_rows,
    }


def main() -> int:
    print(f"Loading runs from {RUNS_PATH}")
    result = analyze()
    n_rows = len(result["per_task_detail"])
    print(f"Analyzed {n_rows} (model, base_task, pert_type) triples")
    print(f"Base tasks: {result['n_base_tasks']} | Models: {result['models']}")
    print()
    for model, s in result["by_model"].items():
        print(f"  {model:<12} robustness={s['robustness']:.3f}  sensitivity={s['sensitivity']:.3f}  n={s['n_triplets']}")
    print()
    for pt, d in result["cross_model_by_type"].items():
        print(f"  {pt:<12} robustness={d['robustness']:.3f}  n={d['n']}")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nWrote {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
