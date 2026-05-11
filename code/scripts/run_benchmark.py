"""
Runner skeleton:
- loads TaskSpecs from JSON
- loads TaskRuns from a JSONL file (produced by your LLM runner)
- scores tasks + aggregates models
- writes results to data/processed_data/results_v1/results.json

This runner assumes you've already created TaskRun logs (JSONL).
Pass --no-judge to skip LLM-as-Judge fallback (faster, less accurate).
"""

from __future__ import annotations
import argparse
import json
import os
from typing import List

from analysis.task_spec_schema import load_tasks_from_json
from analysis.metrics import TaskRun, score_all_models

# ── CLI flags (parsed once at module load) ────────────────────────────────────
_parser = argparse.ArgumentParser(add_help=False)
_parser.add_argument(
    "--no-judge",
    action="store_true",
    help="Skip LLM-as-Judge fallback (faster, less accurate)",
)
_args, _ = _parser.parse_known_args()
USE_JUDGE = not _args.no_judge

if USE_JUDGE:
    from analysis.llm_judge import (
        judge_extract_answer,
        judge_score_structure,
        needs_judge_extraction,
        needs_judge_scoring,
    )


def _fake_flags(score: float, task_checks: list) -> dict:
    n = len(task_checks)
    n_true = round(score * n)
    return {k: (i < n_true) for i, k in enumerate(task_checks)}


def _task_spec_to_judge_dict(task, obj: dict) -> dict:
    """Build minimal task dict for llm_judge functions from a TaskSpec + run obj."""
    return {
        "task_type": obj.get("task_type", ""),
        "numeric_targets": [{"key": t.key} for t in task.numeric_targets],
        "required_structure_checks": task.required_structure_checks,
        "required_assumption_checks": task.required_assumption_checks,
    }


def load_runs_jsonl(path: str, tasks_by_id: dict) -> List[TaskRun]:
    runs = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            # skip error records
            if obj.get("error"):
                continue
            task_id = obj.get("task_id")
            # skip unknown task_id
            if task_id not in tasks_by_id:
                continue
            task = tasks_by_id[task_id]

            # ── LLM-as-Judge fallbacks ────────────────────────────────────────
            if USE_JUDGE:
                task_for_judge = _task_spec_to_judge_dict(task, obj)
                raw = obj.get("raw_response", "")

                if needs_judge_extraction(obj):
                    judge_result = judge_extract_answer(raw, task_for_judge)
                    if judge_result["parsed_values"]:
                        obj["parsed_values"] = judge_result["parsed_values"]
                        obj["judge_assisted"] = True

                if needs_judge_scoring(obj):
                    judge_scores = judge_score_structure(raw, task_for_judge)
                    obj["structure_score"] = judge_scores["structure_score"]
                    obj["assumption_score"] = judge_scores["assumption_score"]
                    obj["judge_reasoning"] = judge_scores.get("judge_reasoning", "")
                    obj["judge_assisted"] = True

            # ── Build TaskRun ─────────────────────────────────────────────────
            keys = [t.key for t in task.numeric_targets]
            vals = obj.get("parsed_values") or []
            extracted = dict(zip(keys, vals))

            struct_flags = _fake_flags(
                obj.get("structure_score", 0.5),
                task.required_structure_checks,
            )
            assump_flags = _fake_flags(
                obj.get("assumption_score", 0.5),
                task.required_assumption_checks,
            )
            runs.append(TaskRun(
                model_name=obj["model_family"],
                task_id=task_id,
                output_text=obj.get("raw_response", ""),
                extracted_numbers=extracted,
                structure_flags=struct_flags,
                assumption_flags=assump_flags,
                confidence_calib_score=obj.get("confidence_score", 0.5),
                reasoning_qual_score=obj.get("reasoning_score", 0.5),
            ))
    return runs


def main() -> None:
    tasks_path = "data/raw_data/benchmark_v1/tasks_all.json"  # 171 tasks (Phase 1 + Phase 2)
    runs_path  = "data/processed_data/results_v1/runs.jsonl"
    out_path   = "data/processed_data/results_v1/results.json"

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    tasks = load_tasks_from_json(tasks_path)
    runs  = load_runs_jsonl(runs_path, tasks)

    judge_label = "enabled" if USE_JUDGE else "disabled (--no-judge)"
    print(f"Loaded {len(tasks)} tasks, {len(runs)} valid runs. LLM-as-Judge: {judge_label}")

    task_scores, model_aggs = score_all_models(tasks, runs)

    out = {
        "model_aggregates": [
            {
                "model_name":       m.model_name,
                "normalized_score": m.normalized_score,
                "by_tier":          m.by_tier,
                "by_difficulty":    m.by_difficulty,
            }
            for m in model_aggs
        ],
        "task_scores": [
            {
                "task_id":              ts.task_id,
                "model_name":           ts.model_name,
                "tier":                 ts.tier,
                "difficulty":           ts.difficulty,
                "components":           ts.component_scores.__dict__,
                "base_score":           ts.base_score,
                "multiplier":           ts.multiplier,
                "final_weighted_score": ts.final_weighted_score,
                "per_run_base_scores":  ts.per_run_base_scores,
            }
            for ts in task_scores
        ],
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"Saved results -> {out_path}")
    print(f"  {len(model_aggs)} models, {len(task_scores)} task scores")
    for m in model_aggs:
        print(f"  {m.model_name:<12}: {m.normalized_score:.4f}")


if __name__ == "__main__":
    main()
