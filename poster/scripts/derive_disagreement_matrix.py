"""Derive 2×2 keyword × judge confusion matrix on the combined eligible set.

Replicates the exact eligibility / join / dedup pipeline from
scripts/combined_pass_flip_analysis.py to produce a 2×2 crosstab on the
assumption_compliance dimension.

Eligibility filter (must reproduce 591 pass_flip / 131 inverse_flip /
n=2850):
  1. Load tasks_all.json + perturbations_all.json → eligibility map
     (task_id has non-empty required_assumption_checks).
  2. Filter base runs/judges by removing v1-pert task_ids
     (perturbations.json).
  3. Inner-join runs.jsonl + llm_judge_scores_full.jsonl on run_id
     (skip judge errors).
  4. Inner-join perturbation_runs.jsonl + perturbation_judge_scores.jsonl
     similarly. Eligibility lookup uses base_task_id for perturbations.
  5. Drop rows missing either assumption_score (keyword) or judge
     assumption_compliance.score.
  6. Run-id deduplicated set union of base + perturbation rows.
  7. Filter to eligible == True.

Binarization at 0.5: ≥0.5 = PASS, <0.5 = FAIL. 4 cells:
  - kw_pass + judge_pass (agreement positive)
  - kw_pass + judge_fail (pass_flip — must equal 591)
  - kw_fail + judge_pass (inverse_flip — must equal 131)
  - kw_fail + judge_fail (agreement negative)

Asserts: pass_flip == 591, inverse_flip == 131, total == 2850.
Writes poster/figures/derived/disagreement_matrix_2x2.json.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

BASE_RUNS  = ROOT / "experiments" / "results_v1" / "runs.jsonl"
BASE_JUDGE = ROOT / "experiments" / "results_v2" / "llm_judge_scores_full.jsonl"
PERT_RUNS  = ROOT / "experiments" / "results_v2" / "perturbation_runs.jsonl"
PERT_JUDGE = ROOT / "experiments" / "results_v2" / "perturbation_judge_scores.jsonl"

TASKS_PATH      = ROOT / "data" / "benchmark_v1" / "tasks_all.json"
PERT_SPECS_PATH = ROOT / "data" / "synthetic" / "perturbations_all.json"
V1_PERT_PATH    = ROOT / "data" / "synthetic" / "perturbations.json"

OUT_JSON = ROOT / "poster" / "figures" / "derived" / "disagreement_matrix_2x2.json"

THRESHOLD = 0.5
EXPECTED_TOTAL = 2850
EXPECTED_PASS_FLIP = 591
EXPECTED_INVERSE_FLIP = 131


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def load_eligibility() -> dict[str, bool]:
    elig: dict[str, bool] = {}
    for spec in json.loads(TASKS_PATH.read_text()):
        elig[spec["task_id"]] = bool(spec.get("required_assumption_checks"))
    if PERT_SPECS_PATH.exists():
        for spec in json.loads(PERT_SPECS_PATH.read_text()):
            elig[spec["task_id"]] = bool(spec.get("required_assumption_checks"))
    return elig


def _judge_assumption(j: dict) -> float | None:
    obj = j.get("assumption_compliance") or {}
    s = obj.get("score")
    return None if s is None else float(s)


def join_population(
    runs: list[dict],
    judges: list[dict],
    elig: dict[str, bool],
    *,
    base_lookup_field: str,
) -> list[dict]:
    judge_by_id = {j["run_id"]: j for j in judges if not j.get("error")}
    rows: list[dict] = []
    for r in runs:
        j = judge_by_id.get(r["run_id"])
        if j is None:
            continue
        kw = r.get("assumption_score")
        jd = _judge_assumption(j)
        if kw is None or jd is None:
            continue
        lookup_id = r.get(base_lookup_field) or r["task_id"]
        rows.append({
            "run_id":           r["run_id"],
            "kw_assumption":    float(kw),
            "judge_assumption": jd,
            "eligible":         bool(elig.get(lookup_id, False)),
        })
    return rows


def main() -> int:
    elig = load_eligibility()

    base_runs_raw  = load_jsonl(BASE_RUNS)
    base_judge_raw = load_jsonl(BASE_JUDGE)
    pert_runs      = load_jsonl(PERT_RUNS)
    pert_judge     = load_jsonl(PERT_JUDGE)

    v1_pert_ids: frozenset[str] = (
        frozenset(p["task_id"] for p in json.loads(V1_PERT_PATH.read_text()))
        if V1_PERT_PATH.exists() else frozenset()
    )
    base_runs  = [r for r in base_runs_raw  if r.get("task_id") not in v1_pert_ids]
    base_judge = [j for j in base_judge_raw if j.get("task_id") not in v1_pert_ids]

    base_rows = join_population(base_runs, base_judge, elig, base_lookup_field="task_id")
    pert_rows = join_population(pert_runs, pert_judge, elig, base_lookup_field="base_task_id")

    seen: set[str] = set()
    combined: list[dict] = []
    for r in base_rows + pert_rows:
        if r["run_id"] in seen:
            continue
        seen.add(r["run_id"])
        combined.append(r)

    eligible_rows = [r for r in combined if r["eligible"]]

    # 2×2 crosstab
    kw_pass_judge_pass = 0
    kw_pass_judge_fail = 0  # pass_flip
    kw_fail_judge_pass = 0  # inverse_flip
    kw_fail_judge_fail = 0
    for r in eligible_rows:
        kw_p = r["kw_assumption"]    >= THRESHOLD
        jd_p = r["judge_assumption"] >= THRESHOLD
        if kw_p and jd_p:
            kw_pass_judge_pass += 1
        elif kw_p and not jd_p:
            kw_pass_judge_fail += 1
        elif not kw_p and jd_p:
            kw_fail_judge_pass += 1
        else:
            kw_fail_judge_fail += 1

    total = (
        kw_pass_judge_pass + kw_pass_judge_fail
        + kw_fail_judge_pass + kw_fail_judge_fail
    )

    print(
        f"kw_pass × judge_pass = {kw_pass_judge_pass}\n"
        f"kw_pass × judge_fail = {kw_pass_judge_fail}  (pass_flip)\n"
        f"kw_fail × judge_pass = {kw_fail_judge_pass}  (inverse_flip)\n"
        f"kw_fail × judge_fail = {kw_fail_judge_fail}\n"
        f"total = {total}"
    )

    assert total == EXPECTED_TOTAL, (
        f"total {total} != expected {EXPECTED_TOTAL} — eligibility filter diverges"
    )
    assert kw_pass_judge_fail == EXPECTED_PASS_FLIP, (
        f"pass_flip {kw_pass_judge_fail} != expected {EXPECTED_PASS_FLIP} — "
        "binarization or join diverges"
    )
    assert kw_fail_judge_pass == EXPECTED_INVERSE_FLIP, (
        f"inverse_flip {kw_fail_judge_pass} != expected {EXPECTED_INVERSE_FLIP} — "
        "binarization or join diverges"
    )

    kw_pass_total = kw_pass_judge_pass + kw_pass_judge_fail
    kw_fail_total = kw_fail_judge_pass + kw_fail_judge_fail
    judge_pass_total = kw_pass_judge_pass + kw_fail_judge_pass
    judge_fail_total = kw_pass_judge_fail + kw_fail_judge_fail
    disagreement = kw_pass_judge_fail + kw_fail_judge_pass

    out = {
        "_methodology": (
            "Combined base + perturbation 2×2 crosstab on assumption_compliance "
            "dimension. Run-id deduplicated set union. Eligibility: tasks with "
            "non-empty required_assumption_checks. Binarization at 0.5."
        ),
        "_pipeline_source": "scripts/combined_pass_flip_analysis.py",
        "threshold": THRESHOLD,
        "n_total": total,
        "cells": {
            "kw_pass_judge_pass": kw_pass_judge_pass,
            "kw_pass_judge_fail": kw_pass_judge_fail,
            "kw_fail_judge_pass": kw_fail_judge_pass,
            "kw_fail_judge_fail": kw_fail_judge_fail,
        },
        "row_totals": {
            "kw_pass": kw_pass_total,
            "kw_fail": kw_fail_total,
        },
        "col_totals": {
            "judge_pass": judge_pass_total,
            "judge_fail": judge_fail_total,
        },
        "disagreement": {
            "n": disagreement,
            "pct": disagreement / total,
        },
        "assertions_passed": {
            "total_2850": total == EXPECTED_TOTAL,
            "pass_flip_591": kw_pass_judge_fail == EXPECTED_PASS_FLIP,
            "inverse_flip_131": kw_fail_judge_pass == EXPECTED_INVERSE_FLIP,
        },
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2))
    print(f"\nWrote {OUT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
