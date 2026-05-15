"""Failure concentration by task type (Section IV.F.2).

Decomposes the n=143 judge-classified L1 failures across the 38 task
types, with phase split (Phase 1 closed-form vs Phase 2 computational).

Run from repo root:
    python code/scripts/failure_concentration_by_tasktype.py

Output:
    data/processed_data/results_v2/failure_concentration.json
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

P_TAXONOMY = Path("data/processed_data/results_v2/error_taxonomy_v2_judge.jsonl")
P_TASKS = Path("data/raw_data/benchmark_v1/tasks_all.json")
OUT_JSON = Path("data/processed_data/results_v2/failure_concentration.json")

MODELS = ["claude", "chatgpt", "gemini", "deepseek", "mistral"]

PHASE2_TYPES = {"GIBBS", "MH", "HMC", "RJMCMC", "HIERARCHICAL", "VB", "ABC"}


def main() -> None:
    records = [json.loads(l) for l in P_TAXONOMY.read_text().splitlines()
               if l.strip()]
    assert len(records) == 143, f"expected 143 L1 failures, got {len(records)}"

    tasks = json.loads(P_TASKS.read_text())

    def task_type_of(task_id: str) -> str:
        # Strip trailing _NN (e.g. BETA_BINOM_01 -> BETA_BINOM)
        parts = task_id.rsplit("_", 1)
        return parts[0] if len(parts) == 2 and parts[1].isdigit() else task_id

    n_tasks_per_type: dict[str, int] = Counter(
        task_type_of(t["task_id"]) for t in tasks
    )
    all_types = sorted(n_tasks_per_type.keys())

    # Aggregations
    by_type: Counter[str] = Counter()
    by_type_model: dict[str, Counter[str]] = defaultdict(Counter)
    by_phase: dict[int, int] = {1: 0, 2: 0}
    by_model: Counter[str] = Counter()

    for r in records:
        tt = r["task_type"]
        m = r["model_family"]
        by_type[tt] += 1
        by_type_model[tt][m] += 1
        by_model[m] += 1
        phase = 2 if tt in PHASE2_TYPES else 1
        by_phase[phase] += 1

    n_phase1_tasks = sum(n for tt, n in n_tasks_per_type.items()
                        if tt not in PHASE2_TYPES)
    n_phase2_tasks = sum(n for tt, n in n_tasks_per_type.items()
                        if tt in PHASE2_TYPES)
    assert n_phase1_tasks == 136
    assert n_phase2_tasks == 35

    n_phase1_responses = n_phase1_tasks * 5
    n_phase2_responses = n_phase2_tasks * 5

    rate1 = by_phase[1] / n_phase1_responses
    rate2 = by_phase[2] / n_phase2_responses
    ratio = rate2 / rate1 if rate1 > 0 else float("inf")

    # Top-10 task types
    top10 = by_type.most_common(10)

    # Types with zero failures
    zero_types = [tt for tt in all_types if by_type[tt] == 0]

    # Output
    out = {
        "_cross_check": {
            "total_failures": sum(by_type.values()),
            "expected": 143,
            "per_model": dict(by_model),
            "per_phase_total": dict(by_phase),
        },
        "phase_summary": {
            "phase1": {
                "n_tasks": n_phase1_tasks,
                "n_responses": n_phase1_responses,
                "n_failures": by_phase[1],
                "failure_rate": round(rate1, 4),
            },
            "phase2": {
                "n_tasks": n_phase2_tasks,
                "n_responses": n_phase2_responses,
                "n_failures": by_phase[2],
                "failure_rate": round(rate2, 4),
            },
            "phase2_to_phase1_ratio": round(ratio, 2),
        },
        "per_task_type": {
            tt: {
                "phase": 2 if tt in PHASE2_TYPES else 1,
                "n_tasks": n_tasks_per_type[tt],
                "total_failures": by_type[tt],
                "per_model": dict(by_type_model[tt]),
            }
            for tt in all_types
        },
        "top10": [
            {
                "task_type": tt,
                "count": cnt,
                "phase": 2 if tt in PHASE2_TYPES else 1,
                "per_model": dict(by_type_model[tt]),
            }
            for tt, cnt in top10
        ],
        "n_types_with_failures": sum(1 for tt in all_types if by_type[tt] > 0),
        "n_types_zero_failures": len(zero_types),
        "zero_failure_types": zero_types,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2))

    print(f"=== Cross-check ===")
    print(f"  total: {out['_cross_check']['total_failures']} (expect 143)")
    print(f"  per_model: {dict(by_model)}")
    print(f"  phase1+phase2: {by_phase[1] + by_phase[2]}")
    print()
    print(f"=== Phase summary ===")
    print(f"  Phase 1 (closed-form): {by_phase[1]}/{n_phase1_responses} = "
          f"{rate1*100:.2f}%")
    print(f"  Phase 2 (computational): {by_phase[2]}/{n_phase2_responses} = "
          f"{rate2*100:.2f}%")
    print(f"  ratio Phase2/Phase1: {ratio:.2f}x")
    print()
    print(f"=== Top-10 task types ===")
    for i, (tt, cnt) in enumerate(top10, 1):
        phase = "P2" if tt in PHASE2_TYPES else "P1"
        per_m = ", ".join(f"{m}={by_type_model[tt].get(m,0)}"
                          for m in MODELS if by_type_model[tt].get(m, 0))
        print(f"  {i:2d}. {tt:<22} [{phase}] count={cnt:3d}  ({per_m})")
    print()
    print(f"=== Concentration ===")
    print(f"  {out['n_types_with_failures']} of 38 types have any failures")
    print(f"  {out['n_types_zero_failures']} failure-free types")


if __name__ == "__main__":
    main()
