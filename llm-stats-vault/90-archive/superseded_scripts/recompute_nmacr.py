"""
Phase 1B — recompute NMACR aggregate scores under literature-derived weights.

Old weights: A=R=M=C=N=0.20 (equal — Path A in llm_runner/response_parser.py
and Path B in evaluation/metrics.py, both LOCKED for v1 reproducibility).

New weights (locked, literature-derived):
- A (Assumption Compliance) = 0.30  ← Du 2025, Boye 2025, Yamauchi 2025
- R (Reasoning Quality)     = 0.25  ← Yamauchi 2025, Boye 2025, ReasonBench 2025
- M (Method Selection)      = 0.20  ← Wei 2022, Chen 2022, Bishop 2006
- C (Confidence Calibration)= 0.15  ← Nagarkar 2026, FermiEval 2025, Multi-Answer 2026
- N (Numerical Correctness) = 0.10  ← Liu 2025, Boye 2025

Per-run dimension sourcing (judge supersedes keyword for the 3 judge dims):
- N: keyword (numeric_score)                        — judge does not score
- M: judge.method_structure.score (else keyword)
- A: judge.assumption_compliance.score (else keyword)
- C: keyword (confidence_score)                     — judge does not score
- R: mean(judge.reasoning_quality.score,
          judge.reasoning_completeness.score) (else keyword)

FORMATTING_FAILURE handling: NOT a rubric dimension. Tagged per-run via
the L1 column of error_taxonomy_v2.json (records[].l1 == 'FORMATTING_FAILURE').
Reported separately as `formatting_failure_rate` per model.

CONCEPTUAL tasks: Path A scored these on rubric only (no numeric).
We mirror that here — when stored numeric_score is None / missing, the
N dimension is dropped and the remaining 4 weights are renormalized to 1.0.

Outputs:
- experiments/results_v2/nmacr_scores_v2.jsonl (one record per run, base + perturbation)
- audit/recompute_log.md initial section

Usage:
    python scripts/recompute_nmacr.py
"""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

# ─── Locked weights (literature-derived) ──────────────────────────
NMACR_WEIGHTS: Dict[str, float] = {
    "A": 0.30,
    "R": 0.25,
    "M": 0.20,
    "C": 0.15,
    "N": 0.10,
}
assert abs(sum(NMACR_WEIGHTS.values()) - 1.0) < 1e-9, "NMACR weights must sum to 1.0"

OLD_WEIGHTS: Dict[str, float] = {d: 0.20 for d in NMACR_WEIGHTS}

WEIGHTING_SCHEME = "literature_v1"

# ─── Paths ────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
BASE_RUNS = ROOT / "experiments" / "results_v1" / "runs.jsonl"
PERT_RUNS = ROOT / "experiments" / "results_v2" / "perturbation_runs.jsonl"
JUDGE_BASE = ROOT / "experiments" / "results_v2" / "llm_judge_scores_full.jsonl"
JUDGE_PERT = ROOT / "experiments" / "results_v2" / "perturbation_judge_scores.jsonl"
TAXONOMY = ROOT / "experiments" / "results_v2" / "error_taxonomy_v2.json"
OUT = ROOT / "experiments" / "results_v2" / "nmacr_scores_v2.jsonl"
LOG = ROOT / "audit" / "recompute_log.md"


def load_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def load_judge_index(path: Path) -> Dict[str, Dict[str, Any]]:
    """Index judge scores by run_id."""
    out: Dict[str, Dict[str, Any]] = {}
    for r in load_jsonl(path):
        rid = r.get("run_id")
        if rid:
            out[rid] = r
    return out


def load_formatting_failures() -> set:
    """run_ids classified as FORMATTING_FAILURE in the L1 taxonomy."""
    if not TAXONOMY.exists():
        return set()
    d = json.loads(TAXONOMY.read_text())
    return {
        rec["run_id"] for rec in d.get("records", [])
        if rec.get("l1") == "FORMATTING_FAILURE" and rec.get("run_id")
    }


def _safe_float(v: Any) -> Optional[float]:
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def derive_dims(run: Dict[str, Any], judge: Optional[Dict[str, Any]]) -> Dict[str, Optional[float]]:
    """Pick judge dim where available; fall back to keyword scoring fields."""
    # Keyword-side
    kw_N = _safe_float(run.get("numeric_score"))
    kw_M = _safe_float(run.get("structure_score"))
    kw_A = _safe_float(run.get("assumption_score"))
    kw_C = _safe_float(run.get("confidence_score"))
    kw_R = _safe_float(run.get("reasoning_score"))

    # Judge-side (when present)
    j_M = j_A = j_R = None
    if judge and not judge.get("error"):
        ms = judge.get("method_structure") or {}
        ac = judge.get("assumption_compliance") or {}
        rq = judge.get("reasoning_quality") or {}
        rc = judge.get("reasoning_completeness") or {}
        j_M = _safe_float(ms.get("score"))
        j_A = _safe_float(ac.get("score"))
        rq_s = _safe_float(rq.get("score"))
        rc_s = _safe_float(rc.get("score"))
        if rq_s is not None and rc_s is not None:
            j_R = (rq_s + rc_s) / 2.0
        elif rq_s is not None:
            j_R = rq_s
        elif rc_s is not None:
            j_R = rc_s

    return {
        "N": kw_N,
        "M": j_M if j_M is not None else kw_M,
        "A": j_A if j_A is not None else kw_A,
        "C": kw_C,
        "R": j_R if j_R is not None else kw_R,
    }


def aggregate(dims: Dict[str, Optional[float]], weights: Dict[str, float]) -> Optional[float]:
    """Weighted sum. Drops missing dims and renormalises remaining weights."""
    present = {d: v for d, v in dims.items() if v is not None}
    if not present:
        return None
    w_total = sum(weights[d] for d in present)
    if w_total <= 0:
        return None
    return sum(weights[d] * present[d] for d in present) / w_total


def process(run_iter: Iterable[Dict[str, Any]],
            judge_index: Dict[str, Dict[str, Any]],
            formatting_run_ids: set,
            perturbation: bool) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for run in run_iter:
        if run.get("error"):
            continue
        rid = run.get("run_id")
        if not rid:
            continue
        judge = judge_index.get(rid)
        dims = derive_dims(run, judge)
        agg_old = aggregate(dims, OLD_WEIGHTS)
        agg_new = aggregate(dims, NMACR_WEIGHTS)
        rec = {
            "run_id": rid,
            "task_id": run.get("task_id"),
            "task_type": run.get("task_type"),
            "model": run.get("model_family"),
            "perturbation": perturbation,
            "perturbation_type": run.get("perturbation_type") if perturbation else None,
            "base_task_id": run.get("base_task_id") if perturbation else None,
            "dim_N": dims["N"],
            "dim_M": dims["M"],
            "dim_A": dims["A"],
            "dim_C": dims["C"],
            "dim_R": dims["R"],
            "judge_used_for": [
                d for d in ("M", "A", "R")
                if judge and not judge.get("error")
            ],
            "aggregate_old": round(agg_old, 6) if agg_old is not None else None,
            "aggregate_new": round(agg_new, 6) if agg_new is not None else None,
            "formatting_failure": rid in formatting_run_ids,
            "weighting_scheme": WEIGHTING_SCHEME,
        }
        out.append(rec)
    return out


def write_jsonl(records: List[Dict[str, Any]], header: Dict[str, Any]) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w") as f:
        f.write(json.dumps({"_header": header}) + "\n")
        for r in records:
            f.write(json.dumps(r) + "\n")


def write_log(records: List[Dict[str, Any]],
              n_base: int,
              n_pert: int,
              missing_dims: int,
              formatting_per_model: Dict[str, Dict[str, int]]) -> None:
    """Initial Step 2 log section. Step 6e expands."""
    by_model_old: Dict[str, List[float]] = defaultdict(list)
    by_model_new: Dict[str, List[float]] = defaultdict(list)
    deltas: List[Dict[str, Any]] = []
    for r in records:
        if r["perturbation"]:
            continue
        m = r["model"]
        if r["aggregate_old"] is not None:
            by_model_old[m].append(r["aggregate_old"])
        if r["aggregate_new"] is not None:
            by_model_new[m].append(r["aggregate_new"])
        if r["aggregate_old"] is not None and r["aggregate_new"] is not None:
            deltas.append({
                "run_id": r["run_id"],
                "task_id": r["task_id"],
                "model": m,
                "delta": r["aggregate_new"] - r["aggregate_old"],
            })
    deltas.sort(key=lambda x: abs(x["delta"]), reverse=True)
    top5 = deltas[:5]

    rows_old = [(m, sum(v) / len(v)) for m, v in by_model_old.items()]
    rows_new = [(m, sum(v) / len(v)) for m, v in by_model_new.items()]
    rows_old.sort(key=lambda x: -x[1])
    rows_new.sort(key=lambda x: -x[1])

    lines = [
        "# Recompute Log — Phase 1B",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"Weighting scheme: `{WEIGHTING_SCHEME}` (A=0.30, R=0.25, M=0.20, C=0.15, N=0.10)",
        "",
        "## Scope",
        f"- Base runs processed: **{n_base}**",
        f"- Perturbation runs processed: **{n_pert}**",
        f"- Total records emitted: **{len(records)}**",
        f"- Records with at least one missing dimension: {missing_dims}",
        "",
        "## Per-model base aggregate — old (equal) weights",
        "| Rank | Model | mean aggregate_old |",
        "|------|-------|---------------------|",
    ]
    for i, (m, v) in enumerate(rows_old, 1):
        lines.append(f"| {i} | {m} | {v:.4f} |")

    lines += [
        "",
        "## Per-model base aggregate — new (literature-derived) weights",
        "| Rank | Model | mean aggregate_new |",
        "|------|-------|---------------------|",
    ]
    for i, (m, v) in enumerate(rows_new, 1):
        lines.append(f"| {i} | {m} | {v:.4f} |")

    lines += ["", "## Top-5 largest per-run aggregate deltas (|new − old|)",
              "| Rank | run_id | task_id | model | Δ |",
              "|------|--------|---------|-------|---|"]
    for i, d in enumerate(top5, 1):
        lines.append(f"| {i} | {d['run_id'][:8]}… | {d['task_id']} | {d['model']} | {d['delta']:+.4f} |")

    lines += ["", "## formatting_failure_rate per model (base runs only)",
              "| Model | formatting failures | total runs | rate |",
              "|-------|---------------------|------------|------|"]
    for m, info in sorted(formatting_per_model.items()):
        rate = (info["fail"] / info["total"] * 100.0) if info["total"] else 0.0
        lines.append(f"| {m} | {info['fail']} | {info['total']} | {rate:.2f}% |")
    lines.append("")

    LOG.parent.mkdir(parents=True, exist_ok=True)
    LOG.write_text("\n".join(lines))


def main() -> None:
    judge_base = load_judge_index(JUDGE_BASE)
    judge_pert = load_judge_index(JUDGE_PERT)
    fmt_run_ids = load_formatting_failures()

    base_records = process(load_jsonl(BASE_RUNS), judge_base, fmt_run_ids, perturbation=False)
    pert_records = process(load_jsonl(PERT_RUNS), judge_pert, fmt_run_ids, perturbation=True)
    records = base_records + pert_records

    missing_dims = sum(
        1 for r in records
        if any(r[k] is None for k in ("dim_N", "dim_M", "dim_A", "dim_C", "dim_R"))
    )

    # formatting_failure_rate per model (base only — paper-relevant denominator)
    fmt_per_model: Dict[str, Dict[str, int]] = defaultdict(lambda: {"fail": 0, "total": 0})
    for r in base_records:
        m = r["model"]
        fmt_per_model[m]["total"] += 1
        if r["formatting_failure"]:
            fmt_per_model[m]["fail"] += 1

    header = {
        "weighting_scheme": WEIGHTING_SCHEME,
        "weights": NMACR_WEIGHTS,
        "old_weights": OLD_WEIGHTS,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "n_base": len(base_records),
        "n_perturbation": len(pert_records),
        "judge_dims_used": ["M", "A", "R"],
        "keyword_only_dims": ["N", "C"],
        "notes": (
            "Judge dims supersede keyword when judge record exists; otherwise keyword. "
            "Missing dimensions trigger renormalisation across remaining weights "
            "(mirrors response_parser.py CONCEPTUAL handling)."
        ),
    }
    write_jsonl(records, header)
    write_log(records, len(base_records), len(pert_records), missing_dims, fmt_per_model)

    print(f"Wrote {OUT}")
    print(f"Base: {len(base_records)}  Perturbation: {len(pert_records)}  Total: {len(records)}")
    print(f"Missing-dim records: {missing_dims}")
    print(f"Wrote {LOG}")


if __name__ == "__main__":
    main()
