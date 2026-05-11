# capstone_mcp/tools/results.py
"""Tool implementations for querying benchmark results."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

_RESULTS_FILE = Path(__file__).parent.parent.parent.parent / "data" / "processed_data" / "results_v1" / "results.json"
_RUNS_FILE    = Path(__file__).parent.parent.parent.parent / "data" / "processed_data" / "results_v1" / "runs.jsonl"

_results_cache: Optional[Dict[str, Any]] = None


def _load_results() -> Dict[str, Any]:
    global _results_cache
    if _results_cache is None:
        with open(_RESULTS_FILE) as f:
            _results_cache = json.load(f)
    return _results_cache


def _load_runs() -> List[Dict[str, Any]]:
    runs: List[Dict[str, Any]] = []
    with open(_RUNS_FILE) as f:
        for line in f:
            line = line.strip()
            if line:
                runs.append(json.loads(line))
    return runs


def get_results(
    model_name: Optional[str] = None,
    task_id: Optional[str] = None,
    min_score: Optional[float] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """Query task-level scores from results.json."""
    data = _load_results()
    task_scores = data.get("task_scores", [])
    out = []
    for ts in task_scores:
        if model_name is not None and ts.get("model_name") != model_name:
            continue
        if task_id is not None and ts.get("task_id") != task_id:
            continue
        if min_score is not None and ts.get("final_weighted_score", 0.0) < min_score:
            continue
        out.append(ts)
        if len(out) >= limit:
            break
    return out


def get_summary(group_by: str = "model") -> Dict[str, Any]:
    """Aggregate results grouped by model, tier, or difficulty."""
    data = _load_results()
    task_scores = data.get("task_scores", [])
    model_aggs = data.get("model_aggregates", [])

    runs = _load_runs()
    meta = {
        "total_tasks": len(task_scores),
        "total_runs": len(runs),
    }

    if group_by == "model":
        return {**meta, "model_aggregates": model_aggs}

    groups: Dict[str, List[float]] = {}
    for ts in task_scores:
        key = str(ts.get(group_by, "unknown"))
        groups.setdefault(key, []).append(ts.get("final_weighted_score", 0.0))

    summary = {}
    for key, scores in groups.items():
        summary[key] = {
            "count": len(scores),
            "mean_score": sum(scores) / len(scores),
            "min_score": min(scores),
            "max_score": max(scores),
        }
    return {**meta, f"by_{group_by}": summary}


def compare_models(
    task_id: Optional[str] = None,
    tier: Optional[int] = None,
) -> Dict[str, Any]:
    """Side-by-side model comparison for a specific task or tier."""
    data = _load_results()
    task_scores = data.get("task_scores", [])

    filtered = []
    for ts in task_scores:
        if task_id is not None and ts.get("task_id") != task_id:
            continue
        if tier is not None and ts.get("tier") != tier:
            continue
        filtered.append(ts)

    # Group by model
    by_model: Dict[str, List[Dict[str, Any]]] = {}
    for ts in filtered:
        m = ts.get("model_name", "unknown")
        by_model.setdefault(m, []).append(ts)

    comparison: Dict[str, Any] = {}
    for model, scores in by_model.items():
        vals = [s.get("final_weighted_score", 0.0) for s in scores]
        comparison[model] = {
            "n_tasks": len(vals),
            "mean_score": sum(vals) / len(vals) if vals else 0.0,
            "task_scores": scores,
        }
    return {"comparison": comparison, "filters": {"task_id": task_id, "tier": tier}}


def get_failures(
    model_name: Optional[str] = None,
    threshold: float = 0.5,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """Get failed tasks (score < threshold) for a given model."""
    data = _load_results()
    task_scores = data.get("task_scores", [])
    failures = []
    for ts in task_scores:
        if model_name is not None and ts.get("model_name") != model_name:
            continue
        if ts.get("final_weighted_score", 1.0) >= threshold:
            continue
        failures.append(ts)
        if len(failures) >= limit:
            break
    return sorted(failures, key=lambda x: x.get("final_weighted_score", 0.0))
