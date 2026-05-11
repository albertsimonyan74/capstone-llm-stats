# capstone_mcp/tools/tasks.py
"""Tool implementations for task retrieval and listing."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

_TASKS_FILE = Path(__file__).parent.parent.parent.parent / "data" / "raw_data" / "benchmark_v1" / "tasks.json"

_tasks_cache: Optional[List[Dict[str, Any]]] = None


def _load_tasks() -> List[Dict[str, Any]]:
    global _tasks_cache
    if _tasks_cache is None:
        with open(_TASKS_FILE) as f:
            _tasks_cache = json.load(f)
    return _tasks_cache


def get_task(task_id: str) -> Dict[str, Any]:
    """Fetch a single task by its task_id."""
    tasks = _load_tasks()
    for t in tasks:
        if t["task_id"] == task_id:
            return t
    raise KeyError(f"Task '{task_id}' not found")


def list_tasks(
    task_type: Optional[str] = None,
    tier: Optional[int] = None,
    difficulty: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """List tasks with optional filters."""
    tasks = _load_tasks()
    results = []
    for t in tasks:
        if task_type is not None and t.get("task_type", "numeric") != task_type:
            continue
        if tier is not None and t.get("tier") != tier:
            continue
        if difficulty is not None and t.get("difficulty") != difficulty:
            continue
        results.append(t)
        if len(results) >= limit:
            break
    return results
