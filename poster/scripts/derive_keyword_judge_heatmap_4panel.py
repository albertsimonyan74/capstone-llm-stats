"""Derive 4-panel 5×5 keyword × judge crosstabs for poster.

Population (n=1230):
  experiments/results_v1/runs.jsonl × experiments/results_v2/llm_judge_scores_full.jsonl
  inner-joined on run_id, judge errors dropped. NO v1-pert filter applied
  (1230 = 855 non-v1pert base runs + 375 v1-pert base runs). NO eligibility
  filter on required_assumption_checks. Matches the website's published
  off-diagonal percentages exactly (28.9 / 43.3 / 70.5 / 77.9).

Four dimensions, with judge field ↔ keyword field pairing:
  1. method_structure       ↔ structure_score
  2. assumption_compliance  ↔ assumption_score
  3. reasoning_quality      ↔ reasoning_score
  4. reasoning_completeness ↔ reasoning_score   (see pairing_notes)

Quantization: both axes ∈ {0.0, 0.25, 0.5, 0.75, 1.0} (exact in source data).

Hard assertions (must hold to publish):
  off_diag_method                == 356
  off_diag_assumption            == 533
  off_diag_reasoning_quality     == 867
  off_diag_reasoning_completeness == 958
  n_total                        == 1230

Output: poster/figures/derived/keyword_judge_heatmap_4panel.json
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

BASE_RUNS  = ROOT / "experiments" / "results_v1" / "runs.jsonl"
BASE_JUDGE = ROOT / "experiments" / "results_v2" / "llm_judge_scores_full.jsonl"

OUT_JSON = ROOT / "poster" / "figures" / "derived" / "keyword_judge_heatmap_4panel.json"

LEVELS = [0.0, 0.25, 0.5, 0.75, 1.0]

DIMENSIONS = [
    {
        "key":             "method_structure",
        "panel_label":     "Method Structure",
        "judge_field":     "method_structure",
        "keyword_field":   "structure_score",
        "expected_offdiag": 356,
    },
    {
        "key":             "assumption_compliance",
        "panel_label":     "Assumption Compliance",
        "judge_field":     "assumption_compliance",
        "keyword_field":   "assumption_score",
        "expected_offdiag": 533,
    },
    {
        "key":             "reasoning_quality",
        "panel_label":     "Reasoning Quality",
        "judge_field":     "reasoning_quality",
        "keyword_field":   "reasoning_score",
        "expected_offdiag": 867,
    },
    {
        "key":             "reasoning_completeness",
        "panel_label":     "Reasoning Completeness",
        "judge_field":     "reasoning_completeness",
        "keyword_field":   "reasoning_score",
        "expected_offdiag": 958,
    },
]

EXPECTED_N_TOTAL = 1230


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def quantize(x: float) -> float:
    """Round to nearest 0.25 step."""
    return round(round(float(x) * 4) / 4, 2)


def crosstab(rows: list[tuple[float, float]]) -> dict:
    """Return 5×5 nested dict[kw_level][judge_level] = count, plus totals."""
    grid: dict[float, dict[float, int]] = {k: {j: 0 for j in LEVELS} for k in LEVELS}
    on_diag = 0
    off_diag = 0
    for kw, jd in rows:
        grid[kw][jd] += 1
        if abs(kw - jd) < 1e-9:
            on_diag += 1
        else:
            off_diag += 1
    return {"grid": grid, "on_diag": on_diag, "off_diag": off_diag}


def main() -> int:
    runs_by_id = {r["run_id"]: r for r in load_jsonl(BASE_RUNS)}
    judges = load_jsonl(BASE_JUDGE)

    joined: list[tuple[dict, dict]] = []
    for j in judges:
        if j.get("error"):
            continue
        r = runs_by_id.get(j["run_id"])
        if r is None:
            continue
        joined.append((r, j))

    n_total = len(joined)
    print(f"joined: {n_total}")

    results: dict[str, dict] = {}
    for dim in DIMENSIONS:
        rows: list[tuple[float, float]] = []
        for r, j in joined:
            jobj = j.get(dim["judge_field"]) or {}
            jv = jobj.get("score")
            kv = r.get(dim["keyword_field"])
            if jv is None or kv is None:
                continue
            kq = quantize(kv)
            jq = quantize(jv)
            if kq not in LEVELS or jq not in LEVELS:
                continue
            rows.append((kq, jq))

        ct = crosstab(rows)
        n_dim = ct["on_diag"] + ct["off_diag"]
        results[dim["key"]] = {
            "panel_label":     dim["panel_label"],
            "judge_field":     dim["judge_field"],
            "keyword_field":   dim["keyword_field"],
            "n":               n_dim,
            "on_diag":         ct["on_diag"],
            "off_diag":        ct["off_diag"],
            "off_diag_pct":    100.0 * ct["off_diag"] / n_dim if n_dim else 0.0,
            "grid":            {
                f"{k:.2f}": {f"{j:.2f}": v for j, v in row.items()}
                for k, row in ct["grid"].items()
            },
        }
        print(
            f"  {dim['panel_label']}: n={n_dim}  off-diag={ct['off_diag']}  "
            f"({100*ct['off_diag']/n_dim:.1f}%)"
        )

    # Hard assertions — fail loudly on drift
    off_diag_method                 = results["method_structure"]["off_diag"]
    off_diag_assumption             = results["assumption_compliance"]["off_diag"]
    off_diag_reasoning_quality      = results["reasoning_quality"]["off_diag"]
    off_diag_reasoning_completeness = results["reasoning_completeness"]["off_diag"]

    assert off_diag_method == 356, (
        f"Method off-diag drift: got {off_diag_method}, expected 356"
    )
    assert off_diag_assumption == 533, (
        f"Assumption off-diag drift: got {off_diag_assumption}, expected 533"
    )
    assert off_diag_reasoning_quality == 867, (
        f"Reasoning Quality off-diag drift: got {off_diag_reasoning_quality}, expected 867"
    )
    assert off_diag_reasoning_completeness == 958, (
        f"Reasoning Completeness off-diag drift: "
        f"got {off_diag_reasoning_completeness}, expected 958"
    )
    assert n_total == EXPECTED_N_TOTAL, (
        f"n_total drift: got {n_total}, expected {EXPECTED_N_TOTAL}"
    )

    out = {
        "_methodology": (
            "4-panel 5×5 keyword×judge crosstab for poster Phase 2. "
            "Population: base runs.jsonl × llm_judge_scores_full.jsonl, "
            "inner-joined on run_id, judge errors dropped. NO v1-pert filter. "
            "NO eligibility filter on required_assumption_checks. "
            "Quantization: both scores ∈ {0.0, 0.25, 0.5, 0.75, 1.0}."
        ),
        "_pipeline_source": "derive_keyword_judge_heatmap_4panel.py",
        "pairing_notes": {
            "reasoning_completeness_vs_reasoning_score": (
                "reasoning_completeness is a judge-only dimension (no direct "
                "keyword counterpart in the rubric). It is paired against "
                "reasoning_score — the same keyword field used for "
                "reasoning_quality — to visualize how much keyword reasoning "
                "signal aligns with the completeness facet the judge "
                "evaluates separately. Both judge dimensions therefore share "
                "the x-axis (keyword reasoning_score) but read different "
                "y-axes (judge reasoning_quality vs. reasoning_completeness)."
            ),
            "scope_no_v1_pert_filter": (
                "n=1230 includes 75 v1-pert task_ids × 5 models = 375 base "
                "runs that the canonical Phase-1.8 pipelines exclude. Kept "
                "here because the website's published 28.9 / 43.3 / 70.5 / "
                "77.9 percentages reproduce only at this scope."
            ),
            "no_eligibility_filter": (
                "required_assumption_checks filter not applied — all 1230 "
                "joined rows kept regardless of whether the task spec "
                "declares assumption checks. Matches the website figure."
            ),
        },
        "n_total":          n_total,
        "levels":           LEVELS,
        "panel_order_ascending_off_diag": [
            d["key"] for d in sorted(DIMENSIONS, key=lambda d: d["expected_offdiag"])
        ],
        "dimensions":       results,
        "assertions_passed": {
            "n_total_1230":                   n_total == EXPECTED_N_TOTAL,
            "off_diag_method_356":            off_diag_method == 356,
            "off_diag_assumption_533":        off_diag_assumption == 533,
            "off_diag_reasoning_quality_867": off_diag_reasoning_quality == 867,
            "off_diag_reasoning_completeness_958":
                off_diag_reasoning_completeness == 958,
        },
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2))
    print(f"\nWrote {OUT_JSON}")
    print("All 5 assertions passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
