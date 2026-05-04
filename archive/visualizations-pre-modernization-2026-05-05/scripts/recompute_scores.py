"""
Recompute all scores in experiments/results_v1/runs.jsonl using the
current full_score() implementation (5-component equal weights).

No API calls made — uses stored raw_response text.

Usage:
    python scripts/recompute_scores.py
    python scripts/summarize_results.py   # regenerate results_summary.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Run from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_runner.response_parser import full_score

RUNS_PATH  = Path("experiments/results_v1/runs.jsonl")
TASKS_PATH = Path("data/benchmark_v1/tasks_all.json")
PERTS_PATH = Path("data/synthetic/perturbations_all.json")


def main() -> None:
    # Load tasks index keyed by task_id (171 canonical + v1 perturbations
    # referenced in runs.jsonl). Phase 2 (tasks_advanced) and v1 perturbation
    # task_ids must resolve here or full_score() is skipped, leaving
    # reasoning_score / confidence_score as None.
    tasks_list = json.loads(TASKS_PATH.read_text())
    tasks: dict = {t["task_id"]: t for t in tasks_list}
    if PERTS_PATH.exists():
        for p in json.loads(PERTS_PATH.read_text()):
            tasks.setdefault(p["task_id"], p)

    # Load all runs
    raw_lines = [l for l in RUNS_PATH.read_text().splitlines() if l.strip()]
    runs = [json.loads(l) for l in raw_lines]

    n_recomputed = 0
    n_skipped    = 0
    n_missing    = 0

    recomputed: list[dict] = []

    for run in runs:
        task_id      = run.get("task_id", "")
        raw_response = run.get("raw_response", "") or ""
        error        = run.get("error")

        # Skip error records — no response to score
        if error or not raw_response:
            run["confidence_score"] = None
            run["reasoning_score"]  = None
            recomputed.append(run)
            n_skipped += 1
            continue

        task = tasks.get(task_id)
        if task is None:
            # Placeholder or unknown task — keep original scores
            run["confidence_score"] = None
            run["reasoning_score"]  = None
            recomputed.append(run)
            n_missing += 1
            continue

        # Inject task_type from run record if missing from task dict
        if not task.get("task_type") and run.get("task_type"):
            task = {**task, "task_type": run["task_type"]}

        scores = full_score(raw_response, task)

        run["numeric_score"]    = scores["numeric"]["numeric_score"]
        run["structure_score"]  = scores["structure"]["structure_score"]
        run["assumption_score"] = scores["assumptions"]["assumption_score"]
        run["confidence_score"] = scores["confidence_score"]
        run["reasoning_score"]  = scores["reasoning_score"]
        run["final_score"]      = scores["final_score"]
        run["pass"]             = scores["pass"]

        recomputed.append(run)
        n_recomputed += 1

    # Write back (overwrite)
    with RUNS_PATH.open("w") as f:
        for r in recomputed:
            f.write(json.dumps(r) + "\n")

    print(f"Recomputed: {n_recomputed}  |  skipped (errors): {n_skipped}  |  missing task: {n_missing}")
    print(f"Total runs: {len(recomputed)}")
    print(f"Written to {RUNS_PATH}")


if __name__ == "__main__":
    main()
