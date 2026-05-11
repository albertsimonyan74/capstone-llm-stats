# evaluation/task_spec_schema.py
"""
Define TaskSpec via JSON so you can store tasks in data/raw_data/benchmark_v1/tasks.json

This loader converts JSON to TaskSpec objects used by metrics.py.

Example tasks.json structure:
[
  {
    "task_id": "BETA_BINOM_01",
    "tier": 1,
    "difficulty": "basic",
    "required_structure_checks": ["states_prior", "states_likelihood", "updates_hyperparameters_correctly"],
    "required_assumption_checks": ["states_iid", "states_distributional_assumption"],
    "numeric_targets": [
      {"key": "posterior_mean", "true_value": 0.6, "full_credit_tol": 0.001, "zero_credit_scale": 0.1}
    ],
    "notes": {"topic": "beta-binomial", "format": "numeric"}
  }
]
"""

from __future__ import annotations
import json
from typing import Dict, List
from analysis.metrics import TaskSpec, NumericTarget


def load_tasks_from_json(path: str) -> Dict[str, TaskSpec]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    tasks: Dict[str, TaskSpec] = {}
    for item in data:
        nts: List[NumericTarget] = []
        for nt in item.get("numeric_targets", []):
            nts.append(
                NumericTarget(
                    key=nt["key"],
                    true_value=float(nt["true_value"]),
                    full_credit_tol=float(nt.get("full_credit_tol", 1e-3)),
                    zero_credit_scale=float(nt.get("zero_credit_scale", 1e-1)),
                )
            )

        spec = TaskSpec(
            task_id=item["task_id"],
            tier=int(item["tier"]),
            difficulty=item["difficulty"],
            required_structure_checks=item.get("required_structure_checks", []),
            required_assumption_checks=item.get("required_assumption_checks", []),
            numeric_targets=nts,
            notes=item.get("notes", {}),
        )
        tasks[spec.task_id] = spec

    return tasks