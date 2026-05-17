"""Per-(model, phase) NMACR (Section IV.F.4).

Phase 1: 31 closed-form conjugate task types (136 tasks).
Phase 2: 7 computational-methods task types (35 tasks).

Cross-checks: (136*P1_mean + 35*P2_mean) / 171 == Table I accuracy
per model within 0.001.

Run from repo root:
    python code/scripts/per_phase_performance.py

Output:
    data/processed_data/results_v2/per_phase_performance.json
"""
from __future__ import annotations

import json
import statistics
from collections import defaultdict
from pathlib import Path

NMACR = Path("data/processed_data/results_v2/nmacr_scores_v2.jsonl")
TASKS = Path("data/raw_data/benchmark_v1/tasks_all.json")
V1_PERT_PATH = Path("data/raw_data/synthetic/perturbations.json")
OUT_JSON = Path("data/processed_data/results_v2/per_phase_performance.json")

MODELS = ["claude", "chatgpt", "gemini", "deepseek", "mistral"]
PHASE2_TYPES = {"GIBBS", "MH", "HMC", "RJMCMC", "HIERARCHICAL", "VB", "ABC"}
DIMS = ["N", "M", "A", "C", "R"]
# Expected Table I accuracy (literature_v1 weights)
TABLE_I_ACCURACY = {
    "gemini":   0.7305,
    "claude":   0.7011,
    "chatgpt":  0.6661,
    "deepseek": 0.6703,
    "mistral":  0.6715,
}


def task_type_of(task_id: str) -> str:
    parts = task_id.rsplit("_", 1)
    return parts[0] if len(parts) == 2 and parts[1].isdigit() else task_id


def main() -> None:
    v1_pert_ids = (
        frozenset(s["task_id"] for s in json.loads(V1_PERT_PATH.read_text()))
        if V1_PERT_PATH.exists() else frozenset()
    )

    # Phase per task_id
    tasks = json.loads(TASKS.read_text())
    phase_of: dict[str, int] = {}
    for t in tasks:
        tid = t["task_id"]
        tt = task_type_of(tid)
        phase_of[tid] = 2 if tt in PHASE2_TYPES else 1

    n_p1 = sum(1 for v in phase_of.values() if v == 1)
    n_p2 = sum(1 for v in phase_of.values() if v == 2)
    assert n_p1 == 136 and n_p2 == 35, f"phase mapping wrong: {n_p1}/{n_p2}"

    # Load base NMACR
    records = []
    with NMACR.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if "_header" in r:
                continue
            if r.get("task_id") in v1_pert_ids:
                continue
            if r["perturbation"]:
                continue
            records.append(r)

    # Per (model, phase)
    cells: dict[tuple[str, int], list[float]] = defaultdict(list)
    dims_cells: dict[tuple[str, int], dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for r in records:
        if r["aggregate_new"] is None:
            continue
        m = r["model"]
        ph = phase_of.get(r["task_id"])
        if ph is None:
            continue
        cells[(m, ph)].append(r["aggregate_new"])
        for d in DIMS:
            v = r.get(f"dim_{d}")
            if v is not None:
                dims_cells[(m, ph)][d].append(v)

    out = {"per_model_phase": {}, "rankings": {}, "cross_check": {}}
    for m in MODELS:
        rec = {}
        for ph in (1, 2):
            vals = cells[(m, ph)]
            if not vals:
                rec[f"phase{ph}"] = {"n_tasks": 0}
                continue
            mean = statistics.mean(vals)
            sd = statistics.stdev(vals) if len(vals) > 1 else 0.0
            per_dim = {d: round(statistics.mean(dims_cells[(m, ph)][d]), 4)
                       for d in DIMS if dims_cells[(m, ph)][d]}
            rec[f"phase{ph}"] = {
                "n_tasks": len(vals),
                "mean_nmacr": round(mean, 4),
                "std_nmacr": round(sd, 4),
                "per_dim_mean": per_dim,
            }
        # Weighted overall + residual check
        if (cells[(m, 1)] and cells[(m, 2)]):
            wa = (rec["phase1"]["mean_nmacr"] * rec["phase1"]["n_tasks"]
                  + rec["phase2"]["mean_nmacr"] * rec["phase2"]["n_tasks"]) / 171
            expected = TABLE_I_ACCURACY[m]
            resid = wa - expected
            rec["weighted_avg"] = round(wa, 4)
            rec["table_I_expected"] = expected
            rec["residual"] = round(resid, 5)
        out["per_model_phase"][m] = rec

    # Rankings
    p1 = sorted(MODELS, key=lambda m: -out["per_model_phase"][m]["phase1"]["mean_nmacr"])
    p2 = sorted(MODELS, key=lambda m: -out["per_model_phase"][m]["phase2"]["mean_nmacr"])
    out["rankings"]["phase1_best_to_worst"] = p1
    out["rankings"]["phase2_best_to_worst"] = p2
    out["rankings"]["rank_shift"] = {
        m: f"{p1.index(m) + 1} -> {p2.index(m) + 1}" for m in MODELS
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2))

    # Print
    print(f"=== Per-(model, phase) NMACR ===")
    print(f"{'model':<10} {'P1 mean':>9} {'P1 sd':>7} {'P2 mean':>9} {'P2 sd':>7} "
          f"{'delta':>7} {'wavg':>7} {'resid':>8}")
    for m in MODELS:
        r = out["per_model_phase"][m]
        p1m = r["phase1"]["mean_nmacr"]
        p2m = r["phase2"]["mean_nmacr"]
        print(f"{m:<10} {p1m:>9.4f} {r['phase1']['std_nmacr']:>7.4f} "
              f"{p2m:>9.4f} {r['phase2']['std_nmacr']:>7.4f} "
              f"{p1m - p2m:>+7.4f} {r['weighted_avg']:>7.4f} "
              f"{r['residual']:>+8.5f}")
    print()
    print(f"=== Phase 1 ranking: {' > '.join(p1)}")
    print(f"=== Phase 2 ranking: {' > '.join(p2)}")
    print(f"=== Rank shift: {out['rankings']['rank_shift']}")
    print()
    print(f"=== Per-dim P1 vs P2 means ===")
    print(f"{'model':<10} " + "".join(f"{f'{d}_P1':>7}{f'{d}_P2':>7}" for d in DIMS))
    for m in MODELS:
        row = f"{m:<10} "
        for d in DIMS:
            p1d = out["per_model_phase"][m]["phase1"]["per_dim_mean"].get(d, 0)
            p2d = out["per_model_phase"][m]["phase2"]["per_dim_mean"].get(d, 0)
            row += f"{p1d:>7.3f}{p2d:>7.3f}"
        print(row)


if __name__ == "__main__":
    main()
