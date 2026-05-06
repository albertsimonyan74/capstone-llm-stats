"""Derive per-task-type failure category counts + failure rate for poster.

Mirrors the website's failure-rate-by-task-type figure
(visualizations.js:failure_by_tasktype, R-generated PNG via
report_materials/r_analysis/05_failure_analysis.R).

Numerator (per task_type): count of records in
experiments/results_v2/error_taxonomy_v2.json:records, broken down by L1
bucket. The four real L1 buckets (no HALLUCINATION, no "other"
collapse):

  ASSUMPTION_VIOLATION   → assumption_violation
  MATHEMATICAL_ERROR     → mathematical_error
  FORMATTING_FAILURE     → formatting_failure
  CONCEPTUAL_ERROR       → conceptual_error

Denominator (per task_type): total runs in experiments/results_v1/runs.jsonl
for that task_type (matches R script `05_failure_analysis.R` Panel A,
which uses df_complete with no v1-pert filter).

failure_rate_pct = 100 * total_failures / total_runs

Hard assertions (must hold to publish):
  - 4 buckets only (assumption_violation, mathematical_error,
    formatting_failure, conceptual_error)
  - sum across all task_types == 143
  - REGRESSION  failure_rate_pct == 100.0
  - BAYES_REG   failure_rate_pct == 100.0
  - BOX_MULLER  failure_rate_pct == 76.0

Output: poster/figures/derived/failure_taxonomy_per_task.json
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "baseline"))
from utils_task_id import task_type_from_id  # noqa: E402

TAX_FILE  = ROOT / "experiments" / "results_v2" / "error_taxonomy_v2.json"
RUNS_FILE = ROOT / "experiments" / "results_v1" / "runs.jsonl"
OUT       = ROOT / "poster" / "figures" / "derived" / "failure_taxonomy_per_task.json"

L1_TO_BUCKET = {
    "ASSUMPTION_VIOLATION": "assumption_violation",
    "MATHEMATICAL_ERROR":   "mathematical_error",
    "FORMATTING_FAILURE":   "formatting_failure",
    "CONCEPTUAL_ERROR":     "conceptual_error",
}

BUCKETS = [
    "assumption_violation",
    "mathematical_error",
    "formatting_failure",
    "conceptual_error",
]

EXPECTED_TOTAL = 143
EXPECTED_RATES_PCT = {
    "REGRESSION":  100.0,
    "BAYES_REG":   100.0,
    "BOX_MULLER":   76.0,
}


def main() -> int:
    tax = json.loads(TAX_FILE.read_text())
    records = tax["records"]

    # Numerator: per-task-type bucket counts
    per_task: dict[str, dict[str, int]] = defaultdict(
        lambda: {b: 0 for b in BUCKETS}
    )
    overall: dict[str, int] = {b: 0 for b in BUCKETS}
    for r in records:
        bucket = L1_TO_BUCKET.get(r["l1"])
        if bucket is None:
            sys.exit(f"unexpected L1 in record: {r['l1']}")
        tt = r["task_type"]
        per_task[tt][bucket] += 1
        overall[bucket]      += 1

    # Denominator: total runs per task_type from runs.jsonl
    total_runs: dict[str, int] = defaultdict(int)
    for line in RUNS_FILE.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        if not rec.get("model_family"):
            continue
        tt = rec.get("task_type") or task_type_from_id(rec["task_id"])
        total_runs[tt] += 1

    # Assemble per-task structure
    per_task_full: dict[str, dict[str, float | int]] = {}
    for tt, counts in per_task.items():
        total_failures = sum(counts.values())
        denom = total_runs.get(tt, 0)
        rate_pct = 100.0 * total_failures / denom if denom else 0.0
        per_task_full[tt] = {
            **counts,
            "total_failures":   total_failures,
            "total_runs":       denom,
            "failure_rate_pct": rate_pct,
        }

    grand_total = sum(overall.values())

    # ── Hard assertions ─────────────────────────────────────────────
    assert grand_total == EXPECTED_TOTAL, (
        f"total drift: got {grand_total}, expected {EXPECTED_TOTAL}"
    )
    for tt, expected_pct in EXPECTED_RATES_PCT.items():
        got = per_task_full.get(tt, {}).get("failure_rate_pct")
        assert got is not None, f"{tt} missing from per_task_full"
        assert abs(got - expected_pct) < 0.01, (
            f"{tt} rate drift: got {got:.2f}%, expected {expected_pct:.2f}%"
        )

    # Sort task types desc by total_failures (matches website panel A
    # ordering: REGRESSION, BAYES_REG, BOX_MULLER, FISHER_INFO, ...)
    ordered = sorted(
        per_task_full,
        key=lambda t: (-per_task_full[t]["total_failures"], t),
    )

    out = {
        "_methodology": (
            "Per-task-type failure category counts + failure rate. "
            "Numerator: error_taxonomy_v2.json:records L1-bucketed counts. "
            "Denominator: total runs in runs.jsonl for that task_type "
            "(matches R script report_materials/r_analysis/"
            "05_failure_analysis.R Panel A)."
        ),
        "_pipeline_source": (
            "error_taxonomy_v2.json:records (counts) × runs.jsonl (denom)"
        ),
        "buckets":      BUCKETS,
        "l1_to_bucket": L1_TO_BUCKET,
        "total":        grand_total,
        "overall":      overall,
        "per_task":     {t: per_task_full[t] for t in ordered},
        "task_order_desc_total": ordered,
        "assertions_passed": {
            "total_143":            grand_total == EXPECTED_TOTAL,
            "REGRESSION_rate_100":  abs(per_task_full["REGRESSION"]["failure_rate_pct"] - 100.0) < 0.01,
            "BAYES_REG_rate_100":   abs(per_task_full["BAYES_REG"]["failure_rate_pct"] - 100.0) < 0.01,
            "BOX_MULLER_rate_76":   abs(per_task_full["BOX_MULLER"]["failure_rate_pct"] - 76.0) < 0.01,
            "four_buckets_only":    set(BUCKETS) == set(L1_TO_BUCKET.values()),
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))
    print(f"\nWrote {OUT}")
    print(f"total: {grand_total}")
    print(f"overall: {overall}")
    print(f"REGRESSION: {per_task_full['REGRESSION']}")
    print(f"BAYES_REG:  {per_task_full['BAYES_REG']}")
    print(f"BOX_MULLER: {per_task_full['BOX_MULLER']}")
    print("All 5 assertions passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
