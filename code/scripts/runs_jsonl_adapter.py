# experiments/runs_jsonl_adapter.py
"""
Adapter: convert runs.jsonl (run_all_tasks.py schema) → TaskRun (metrics.py schema).

Field mapping
─────────────
  obj["model_family"]    → TaskRun.model_name
  obj["raw_response"]    → TaskRun.output_text
  obj["parsed_values"]   → TaskRun.extracted_numbers   (List → Dict, keyed by task)
  obj["structure_score"] → synthetic structure_flags    (preserves score exactly)
  obj["assumption_score"]→ synthetic assumption_flags   (preserves score exactly)
  obj["confidence_score"]→ TaskRun.confidence_calib_score
  obj["reasoning_score"] → TaskRun.reasoning_qual_score

Skipped records
───────────────
  - obj["error"] is truthy                      (failed API call)
  - obj["task_id"] not in tasks dict            (old placeholder / perturbation)
  - missing task_id or model identifier         (malformed line)
"""
from __future__ import annotations

import json
from typing import Dict, List, Optional

from analysis.metrics import TaskRun, TaskSpec


# ── helpers ───────────────────────────────────────────────────────────────────

def _fake_flags(checks: List[str], score: float) -> Dict[str, bool]:
    """
    Reconstruct boolean flags so checklist_score(checks, flags) == score.

    Sets the first round(score * n) checks to True, remainder to False.
    Works exactly for any score that is an integer fraction k/n.
    """
    n = len(checks)
    if n == 0:
        return {}
    n_true = round(score * n)
    return {c: (i < n_true) for i, c in enumerate(checks)}


# ── core adapter ──────────────────────────────────────────────────────────────

def adapt_record(obj: dict, task: Optional[TaskSpec] = None) -> Optional[TaskRun]:
    """
    Convert one runs.jsonl record → TaskRun.

    Returns None for error records or records missing required fields.
    The caller is responsible for skipping records whose task_id is absent
    from the tasks dict (they will arrive with task=None and be skipped below
    only if they also lack model/task identity).
    """
    # Skip failed API calls
    if obj.get("error"):
        return None

    task_id = obj.get("task_id", "").strip()
    # Support both schemas: current uses model_family, old used model_name
    model_name = (
        obj.get("model_family") or obj.get("model_name") or ""
    ).strip()

    if not task_id or not model_name:
        return None

    # ── parsed_values (List[float]) → extracted_numbers (Dict[str, float]) ──
    extracted_numbers: Dict[str, float] = {}
    parsed = obj.get("parsed_values")

    if isinstance(parsed, list) and task and task.numeric_targets:
        for i, tgt in enumerate(task.numeric_targets):
            if i < len(parsed):
                try:
                    extracted_numbers[tgt.key] = float(parsed[i])
                except (TypeError, ValueError):
                    pass
    elif isinstance(obj.get("extracted_numbers"), dict):
        # Future-proof: already in keyed format
        extracted_numbers = {
            k: float(v) for k, v in obj["extracted_numbers"].items()
        }

    # ── Reconstruct boolean flags from pre-computed aggregate scores ──────────
    # This bypasses keyword re-matching and preserves the original scores.
    structure_score  = float(obj.get("structure_score")  or 1.0)
    assumption_score = float(obj.get("assumption_score") or 1.0)

    s_checks: List[str] = list(task.required_structure_checks)  if task else []
    a_checks: List[str] = list(task.required_assumption_checks) if task else []

    structure_flags  = _fake_flags(s_checks, structure_score)
    assumption_flags = _fake_flags(a_checks, assumption_score)

    return TaskRun(
        model_name=model_name,
        task_id=task_id,
        run_id=obj.get("run_id", "base"),
        perturbation_group=obj.get("perturbation_group"),
        output_text=(obj.get("raw_response") or obj.get("output_text") or ""),
        extracted_numbers=extracted_numbers,
        structure_flags=structure_flags,
        assumption_flags=assumption_flags,
        conceptual_rubric_score_0to2=obj.get("conceptual_rubric_score_0to2"),
        confidence=obj.get("confidence"),
        confidence_calib_score=float(obj.get("confidence_score") or 0.5),
        reasoning_qual_score=float(obj.get("reasoning_score")    or 0.5),
    )


# ── public loader ─────────────────────────────────────────────────────────────

def load_runs_jsonl(
    path: str,
    tasks: Optional[Dict[str, TaskSpec]] = None,
) -> List[TaskRun]:
    """
    Load runs.jsonl using the schema adapter.

    Args:
        path:  Path to runs.jsonl.
        tasks: TaskSpec dict (from load_tasks_from_json). When provided:
               - maps parsed_values → extracted_numbers by key name
               - reconstructs structure/assumption flags from stored scores
               - silently skips records whose task_id is not in the dict

    Returns:
        List of TaskRun objects, ready for score_all_models().
        Error records and unknown-task records are silently skipped.
    """
    runs: List[TaskRun] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            task_id = obj.get("task_id", "")

            # Skip records not in the current tasks dict
            if tasks is not None and task_id not in tasks:
                continue

            task = tasks.get(task_id) if tasks else None
            run  = adapt_record(obj, task)
            if run is not None:
                runs.append(run)

    return runs
