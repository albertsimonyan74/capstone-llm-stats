"""Derive per-task-type failure category counts for poster.

Source: experiments/results_v2/error_taxonomy_v2.json:records
  Each record has task_type and l1 (one of ASSUMPTION_VIOLATION,
  MATHEMATICAL_ERROR, FORMATTING_FAILURE, CONCEPTUAL_ERROR).
  L1 HALLUCINATION is defined in mapping but never assigned.

Output category mapping (collapsed to 4 for the figure):
  ASSUMPTION_VIOLATION → "assumption"
  MATHEMATICAL_ERROR   → "math"
  HALLUCINATION        → "hallucination"  (always 0; included for
                                            visual consistency)
  CONCEPTUAL_ERROR + FORMATTING_FAILURE → "other"

Headline assertions (must hold to publish):
  total              == 143
  assumption pct     ≈ 46.85% (67/143)
  math pct           ≈ 33.57% (48/143)
  hallucination pct  == 0.00%

Output: poster/figures/derived/failure_taxonomy_per_task.json
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC  = ROOT / "experiments" / "results_v2" / "error_taxonomy_v2.json"
OUT  = ROOT / "poster" / "figures" / "derived" / "failure_taxonomy_per_task.json"

L1_TO_CATEGORY = {
    "ASSUMPTION_VIOLATION": "assumption",
    "MATHEMATICAL_ERROR":   "math",
    "HALLUCINATION":        "hallucination",
    "CONCEPTUAL_ERROR":     "other",
    "FORMATTING_FAILURE":   "other",
}

CATEGORIES = ["assumption", "math", "hallucination", "other"]

EXPECTED_TOTAL = 143
TOL = 0.001  # absolute tol on percentages


def main() -> int:
    data = json.loads(SRC.read_text())
    records = data["records"]
    total = len(records)

    per_task: dict[str, dict[str, int]] = defaultdict(
        lambda: {c: 0 for c in CATEGORIES}
    )
    overall: dict[str, int] = {c: 0 for c in CATEGORIES}

    for r in records:
        l1 = r["l1"]
        task = r["task_type"]
        cat = L1_TO_CATEGORY.get(l1, "other")
        per_task[task][cat] += 1
        overall[cat] += 1

    # Hard assertions
    assert total == EXPECTED_TOTAL, (
        f"total drift: got {total}, expected {EXPECTED_TOTAL}"
    )
    assumption_pct = overall["assumption"] / total
    math_pct       = overall["math"]       / total
    hallucination_pct = overall["hallucination"] / total
    assert abs(assumption_pct - 67/143) < TOL, (
        f"assumption pct drift: got {assumption_pct:.4f}, expected {67/143:.4f}"
    )
    assert abs(math_pct - 48/143) < TOL, (
        f"math pct drift: got {math_pct:.4f}, expected {48/143:.4f}"
    )
    assert hallucination_pct == 0.0, (
        f"hallucination pct drift: got {hallucination_pct}, expected 0"
    )

    # Sort task types descending by total failures
    task_totals = {t: sum(c.values()) for t, c in per_task.items()}
    sorted_tasks = sorted(task_totals, key=lambda t: -task_totals[t])

    out = {
        "_methodology": (
            "Per-task-type failure category counts from "
            "error_taxonomy_v2.json:records (n=143 audited). L1 categories "
            "collapsed to 4 for visualization: assumption / math / "
            "hallucination / other (formatting + conceptual)."
        ),
        "_pipeline_source": "error_taxonomy_v2.json:records",
        "category_mapping_l1_to_category": L1_TO_CATEGORY,
        "categories":   CATEGORIES,
        "total":        total,
        "overall":      overall,
        "overall_pct": {
            c: 100.0 * overall[c] / total for c in CATEGORIES
        },
        "per_task":     {t: per_task[t] for t in sorted_tasks},
        "task_totals":  {t: task_totals[t] for t in sorted_tasks},
        "task_order_desc_total": sorted_tasks,
        "assertions_passed": {
            "total_143":             total == EXPECTED_TOTAL,
            "assumption_pct_46.85":  abs(assumption_pct - 67/143) < TOL,
            "math_pct_33.57":        abs(math_pct - 48/143) < TOL,
            "hallucination_pct_0":   hallucination_pct == 0.0,
        },
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))
    print(f"\nWrote {OUT}")
    print(f"total: {total}")
    print(f"overall: {overall}")
    print(
        f"pcts: assumption={100*assumption_pct:.2f}% "
        f"math={100*math_pct:.2f}% "
        f"hallucination={100*hallucination_pct:.2f}%"
    )
    print("All 4 assertions passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
