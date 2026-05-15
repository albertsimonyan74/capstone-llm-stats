"""Per-model 2x2 keyword-vs-judge contingency on n=2,850 eligible pool.

Decomposes the §IV.C pooled disagreement (591 KW-PASS/J-FAIL vs 131
KW-FAIL/J-PASS, 4.5x asymmetry) into per-model contributions.

Eligibility: same predicate as combined_pass_flip_analysis.py —
tasks with non-empty required_assumption_checks, run_id-dedup
union of base+perturbation, v1 seeds filtered from base.

Run from repo root:
    python code/scripts/per_model_disagreement.py

Output:
    data/processed_data/results_v2/per_model_disagreement.json
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

BASE_RUNS = Path("data/processed_data/results_v1/runs.jsonl")
BASE_JUDGE = Path("data/processed_data/results_v2/llm_judge_scores_full.jsonl")
PERT_RUNS = Path("data/processed_data/results_v2/perturbation_runs.jsonl")
PERT_JUDGE = Path("data/processed_data/results_v2/perturbation_judge_scores.jsonl")
TASKS_PATH = Path("data/raw_data/benchmark_v1/tasks_all.json")
PERT_SPECS_PATH = Path("data/raw_data/synthetic/perturbations_all.json")
V1_PERT_PATH = Path("data/raw_data/synthetic/perturbations.json")

OUT_JSON = Path("data/processed_data/results_v2/per_model_disagreement.json")

MODELS = ["claude", "chatgpt", "gemini", "deepseek", "mistral"]
THRESHOLD = 0.5


def load_jsonl(p: Path):
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def main() -> None:
    elig = {spec["task_id"]: bool(spec.get("required_assumption_checks"))
            for spec in json.loads(TASKS_PATH.read_text())}
    if PERT_SPECS_PATH.exists():
        for spec in json.loads(PERT_SPECS_PATH.read_text()):
            elig[spec["task_id"]] = bool(spec.get("required_assumption_checks"))

    v1_pert_ids = (
        frozenset(s["task_id"] for s in json.loads(V1_PERT_PATH.read_text()))
        if V1_PERT_PATH.exists() else frozenset()
    )

    base_runs = [r for r in load_jsonl(BASE_RUNS)
                 if r.get("task_id") not in v1_pert_ids
                 and r.get("model_family") and "assumption_score" in r]
    base_judge = load_jsonl(BASE_JUDGE)
    pert_runs = load_jsonl(PERT_RUNS)
    pert_judge = load_jsonl(PERT_JUDGE)

    def join(runs, judges, base_field):
        j_by = {j["run_id"]: j for j in judges if not j.get("error")}
        rows = []
        for r in runs:
            j = j_by.get(r["run_id"])
            if j is None:
                continue
            kw = r.get("assumption_score")
            jd = (j.get("assumption_compliance") or {}).get("score")
            if kw is None or jd is None:
                continue
            lookup = r.get(base_field) or r["task_id"]
            rows.append({
                "run_id": r["run_id"],
                "kw": float(kw),
                "jd": float(jd),
                "eligible": bool(elig.get(lookup, False)),
                "model": r["model_family"],
            })
        return rows

    base_rows = join(base_runs, base_judge, "task_id")
    pert_rows = join(pert_runs, pert_judge, "base_task_id")

    seen = set()
    combined = []
    for r in base_rows + pert_rows:
        if r["run_id"] in seen:
            continue
        seen.add(r["run_id"])
        combined.append(r)

    eligible = [r for r in combined if r["eligible"]]

    by_model: dict[str, dict[str, int]] = defaultdict(lambda: {
        "n_both_pass": 0, "n_keyword_only": 0,
        "n_judge_only": 0, "n_both_fail": 0,
    })
    for r in eligible:
        kp = r["kw"] >= THRESHOLD
        jp = r["jd"] >= THRESHOLD
        b = by_model[r["model"]]
        if kp and jp:
            b["n_both_pass"] += 1
        elif kp and not jp:
            b["n_keyword_only"] += 1
        elif not kp and jp:
            b["n_judge_only"] += 1
        else:
            b["n_both_fail"] += 1

    out = {"per_model": {}, "totals": {}}
    sums = {"n_both_pass": 0, "n_keyword_only": 0,
            "n_judge_only": 0, "n_both_fail": 0, "n_total": 0}
    for m in MODELS:
        b = by_model[m]
        n_total = sum(b.values())
        ratio = b["n_keyword_only"] / max(b["n_judge_only"], 1)
        rec = dict(b)
        rec["n_total"] = n_total
        rec["asymmetry_ratio"] = round(ratio, 3)
        out["per_model"][m] = rec
        for k in ("n_both_pass", "n_keyword_only",
                  "n_judge_only", "n_both_fail"):
            sums[k] += b[k]
        sums["n_total"] += n_total

    out["totals"] = sums
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2))

    print(f"{'model':<10} {'both_pass':>10} {'kw_only':>9} {'judge_only':>11} "
          f"{'both_fail':>10} {'n':>5} {'ratio':>8}")
    for m in MODELS:
        b = out["per_model"][m]
        print(f"{m:<10} {b['n_both_pass']:>10} {b['n_keyword_only']:>9} "
              f"{b['n_judge_only']:>11} {b['n_both_fail']:>10} "
              f"{b['n_total']:>5} {b['asymmetry_ratio']:>8.2f}")
    print()
    print(f"sums:      n_keyword_only={sums['n_keyword_only']} (expect 591), "
          f"n_judge_only={sums['n_judge_only']} (expect 131), "
          f"n_total={sums['n_total']} (expect 2850)")


if __name__ == "__main__":
    main()
