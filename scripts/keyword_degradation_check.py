"""Phase 1.5 quick check: does keyword scoring degrade more under perturbation
than judge scoring on the assumption_compliance dimension?

Uses the same eligibility filter and joining logic as
`scripts/combined_pass_flip_analysis.py` so denominators (1,095 base,
2,100 pert) match exactly.

Output: experiments/results_v2/keyword_degradation_check.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Make sibling script importable when running from project root
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

# Reuse loaders + joiners from the combined pass-flip analysis
from combined_pass_flip_analysis import (  # noqa: E402
    BASE_RUNS,
    BASE_JUDGE,
    PERT_RUNS,
    PERT_JUDGE,
    load_jsonl,
    load_eligibility,
    join_population,
    THRESHOLD,
    PERT_TYPES,
)


OUT_JSON = Path("experiments/results_v2/keyword_degradation_check.json")


def pass_rates(rows: list[dict]) -> tuple[float, float, int]:
    """Return (kw_pass_rate, judge_pass_rate, n_eligible) on eligible rows only."""
    eligible = [r for r in rows if r["eligible"]]
    n = len(eligible)
    if n == 0:
        return 0.0, 0.0, 0
    kw_pass = sum(1 for r in eligible if r["kw_assumption"] >= THRESHOLD)
    jd_pass = sum(1 for r in eligible if r["judge_assumption"] >= THRESHOLD)
    return kw_pass / n, jd_pass / n, n


def verdict_for(differential_pp: float) -> str:
    if differential_pp >= 2.0:
        return "SUPPORTED"
    if differential_pp > 0.0:
        return "WEAK"
    if differential_pp == 0.0:
        return "NOT_SUPPORTED"
    # differential < 0
    if abs(differential_pp) >= 2.0:
        return "OPPOSITE_SUPPORTED"
    # small negative ~= 0
    if abs(differential_pp) < 0.5:
        return "NOT_SUPPORTED"
    return "OPPOSITE_SUPPORTED"


def main() -> int:
    elig = load_eligibility()
    base_runs = load_jsonl(BASE_RUNS)
    base_judge = load_jsonl(BASE_JUDGE)
    pert_runs = load_jsonl(PERT_RUNS)
    pert_judge = load_jsonl(PERT_JUDGE)

    base_rows = join_population(
        base_runs, base_judge, elig, base_lookup_field="task_id"
    )
    pert_rows = join_population(
        pert_runs, pert_judge, elig, base_lookup_field="base_task_id"
    )

    base_kw, base_jd, n_base = pass_rates(base_rows)
    pert_kw, pert_jd, n_pert = pass_rates(pert_rows)

    base_kw_pp = 100.0 * base_kw
    base_jd_pp = 100.0 * base_jd
    pert_kw_pp = 100.0 * pert_kw
    pert_jd_pp = 100.0 * pert_jd

    keyword_drop_pp = base_kw_pp - pert_kw_pp
    judge_drop_pp = base_jd_pp - pert_jd_pp
    differential_pp = keyword_drop_pp - judge_drop_pp

    # Per-perturbation-type
    per_type: dict[str, dict] = {}
    for pt in PERT_TYPES:
        sub = [r for r in pert_rows if r["perturbation_type"] == pt]
        sub_kw, sub_jd, _ = pass_rates(sub)
        sub_kw_pp = 100.0 * sub_kw
        sub_jd_pp = 100.0 * sub_jd
        kw_drop = base_kw_pp - sub_kw_pp
        jd_drop = base_jd_pp - sub_jd_pp
        per_type[pt] = {
            "keyword_pass_rate_pert": sub_kw,
            "judge_pass_rate_pert": sub_jd,
            "keyword_drop_pp": kw_drop,
            "judge_drop_pp": jd_drop,
            "differential_pp": kw_drop - jd_drop,
        }

    overall_verdict = verdict_for(differential_pp)

    if overall_verdict == "SUPPORTED":
        rec_text = (
            f"Across the 3,195 eligible runs that share the assumption-compliance "
            f"rubric, keyword scoring degrades faster than the LLM-judge under "
            f"perturbation: keyword PASS rate drops {keyword_drop_pp:.1f}pp "
            f"(from {base_kw_pp:.1f}% on base to {pert_kw_pp:.1f}% on perturbation), "
            f"while judge PASS rate drops only {judge_drop_pp:.1f}pp "
            f"(from {base_jd_pp:.1f}% to {pert_jd_pp:.1f}%). The "
            f"{differential_pp:.1f}pp differential indicates that surface-form "
            f"changes — rephrasing, numerical reseeding, semantic reframing — "
            f"disproportionately break the keyword regex, whereas the judge "
            f"rubric tracks the underlying mathematical content more robustly. "
            f"This is direct empirical support for using LLM-as-a-judge "
            f"scoring as the canonical assumption-compliance metric on "
            f"perturbation-evaluated tasks."
        )
    elif overall_verdict == "WEAK":
        rec_text = (
            f"do not publish (differential is {differential_pp:.1f}pp — "
            "below the 2pp threshold for a defensible claim)."
        )
    elif overall_verdict == "OPPOSITE_SUPPORTED":
        rec_text = (
            f"do not publish original claim. The data shows the OPPOSITE: "
            f"judge scoring degrades faster than keyword by "
            f"{abs(differential_pp):.1f}pp (keyword drop {keyword_drop_pp:.1f}pp, "
            f"judge drop {judge_drop_pp:.1f}pp)."
        )
    else:
        rec_text = (
            f"do not publish (differential is {differential_pp:.2f}pp — "
            "essentially zero; both scorers degrade at the same rate)."
        )

    out = {
        "_methodology": (
            "Direct test of whether keyword scoring degrades more than judge "
            "scoring under perturbation. Pre-registered for inclusion in "
            "Phase 1.5 combined pass-flip findings."
        ),
        "base": {
            "keyword_pass_rate": base_kw,
            "judge_pass_rate": base_jd,
            "n_eligible": n_base,
        },
        "perturbation": {
            "keyword_pass_rate": pert_kw,
            "judge_pass_rate": pert_jd,
            "n_eligible": n_pert,
        },
        "drops": {
            "keyword_drop_pp": keyword_drop_pp,
            "judge_drop_pp": judge_drop_pp,
            "differential_pp": differential_pp,
        },
        "per_perturbation_type": {
            pt: {
                "keyword_drop_pp": per_type[pt]["keyword_drop_pp"],
                "judge_drop_pp": per_type[pt]["judge_drop_pp"],
                "differential_pp": per_type[pt]["differential_pp"],
            }
            for pt in PERT_TYPES
        },
        "verdict": overall_verdict,
        "recommended_methodology_page_text": rec_text,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2))

    # Verdict block
    print()
    print("KEYWORD-DEGRADATION CHECK")
    print()
    print("Base:")
    print(f"  keyword PASS rate: {base_kw_pp:.2f}%")
    print(f"  judge PASS rate: {base_jd_pp:.2f}%")
    print(f"  n_eligible: {n_base}")
    print()
    print("Perturbation:")
    print(f"  keyword PASS rate: {pert_kw_pp:.2f}%")
    print(f"  judge PASS rate: {pert_jd_pp:.2f}%")
    print(f"  n_eligible: {n_pert}")
    print()
    print("Drops:")
    print(f"  keyword drop: {keyword_drop_pp:+.2f}pp")
    print(f"  judge drop: {judge_drop_pp:+.2f}pp")
    print(f"  differential: {differential_pp:+.2f}pp")
    print()
    print("Per-perturbation-type differentials:")
    for pt in PERT_TYPES:
        d = per_type[pt]["differential_pp"]
        print(
            f"  {pt:10s}: kw_drop={per_type[pt]['keyword_drop_pp']:+.2f}pp  "
            f"jd_drop={per_type[pt]['judge_drop_pp']:+.2f}pp  "
            f"diff={d:+.2f}pp"
        )
    print()
    print(f"VERDICT: {overall_verdict}")
    print()
    print("Recommended Methodology page text:")
    print(f'"{rec_text}"')
    print()
    print(f"Saved: {OUT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
