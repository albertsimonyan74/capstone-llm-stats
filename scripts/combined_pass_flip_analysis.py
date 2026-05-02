"""Combined base + perturbation pass-flip analysis on assumption_compliance.

Phase 1.5 audit-driven extension of the canonical
`keyword_vs_judge_agreement.py` analysis. The original script reports a
pass-flip headline (keyword PASS, judge FAIL) on the 1,095 eligible base runs
only. This script extends the same methodology to the 2,365 perturbation runs
and reports the union (run-ID deduplicated) for a complete picture.

Methodology:
  - Eligibility: tasks with non-empty `required_assumption_checks` (Phase 1A
    convention; matches `keyword_vs_judge_agreement.py`).
  - Binarization at 0.5 (>=0.5 = PASS, <0.5 = FAIL) on both keyword and judge
    scores for the assumption_compliance dimension.
  - Pass-flip = keyword PASS AND judge FAIL.
  - Inverse-flip = keyword FAIL AND judge PASS.
  - Combined population = run-ID deduplicated set union of base + pert runs.

Citations:
  - Yamauchi et al. (2025) "Evaluating Self-Generated Documentation"
    (arxiv:2506.13639) — keyword/judge agreement methodology.
  - User direction (Day 4 Phase 1.5): combined population with run_id dedup.

Outputs:
  - experiments/results_v2/combined_pass_flip_analysis.json
  - report_materials/figures/combined_pass_flip_comparison.png

Constraints:
  - Deterministic. No randomness. No model API calls.
  - Does NOT modify the canonical `keyword_vs_judge_agreement.json` (kept as
    base-only baseline for backward compatibility).

Run from project root:
    python scripts/combined_pass_flip_analysis.py
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_RUNS = Path("experiments/results_v1/runs.jsonl")
BASE_JUDGE = Path("experiments/results_v2/llm_judge_scores_full.jsonl")
PERT_RUNS = Path("experiments/results_v2/perturbation_runs.jsonl")
PERT_JUDGE = Path("experiments/results_v2/perturbation_judge_scores.jsonl")

TASKS_PATH = Path("data/benchmark_v1/tasks_all.json")
PERT_SPECS_PATH = Path("data/synthetic/perturbations.json")

OUT_JSON = Path("experiments/results_v2/combined_pass_flip_analysis.json")
OUT_FIG = Path("report_materials/figures/combined_pass_flip_comparison.png")

# ── Constants ────────────────────────────────────────────────────────────────
THRESHOLD = 0.5
MODELS = ["claude", "chatgpt", "gemini", "deepseek", "mistral"]
PERT_TYPES = ["rephrase", "numerical", "semantic"]

MODEL_COLORS = {
    "claude":   "#00CED1",
    "chatgpt":  "#7FFFD4",
    "gemini":   "#FF6B6B",
    "deepseek": "#4A90D9",
    "mistral":  "#A78BFA",
}


# ── Loaders ──────────────────────────────────────────────────────────────────
def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def load_eligibility() -> dict[str, bool]:
    """task_id -> has non-empty required_assumption_checks."""
    elig: dict[str, bool] = {}
    for spec in json.loads(TASKS_PATH.read_text()):
        elig[spec["task_id"]] = bool(spec.get("required_assumption_checks"))
    if PERT_SPECS_PATH.exists():
        for spec in json.loads(PERT_SPECS_PATH.read_text()):
            elig[spec["task_id"]] = bool(spec.get("required_assumption_checks"))
    return elig


# ── Joining ──────────────────────────────────────────────────────────────────
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
    """Inner-join keyword runs with judge scores by run_id.

    `base_lookup_field` is "task_id" for the base population, "base_task_id"
    for the perturbation population. Eligibility uses that field for lookup.
    """
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
        rows.append(
            {
                "run_id": r["run_id"],
                "task_id": r["task_id"],
                "base_task_id": lookup_id,
                "model_family": r["model_family"],
                "perturbation_type": r.get("perturbation_type"),
                "kw_assumption": float(kw),
                "judge_assumption": jd,
                "eligible": bool(elig.get(lookup_id, False)),
            }
        )
    return rows


# ── Aggregations ─────────────────────────────────────────────────────────────
def classify(row: dict) -> tuple[bool, bool]:
    kw_pass = row["kw_assumption"] >= THRESHOLD
    jd_pass = row["judge_assumption"] >= THRESHOLD
    return kw_pass, jd_pass


def aggregate(rows: Iterable[dict]) -> dict:
    rows = list(rows)
    n_total = len(rows)
    eligible = [r for r in rows if r["eligible"]]
    n_elig = len(eligible)
    n_pf = 0  # keyword PASS, judge FAIL
    n_if = 0  # keyword FAIL, judge PASS
    for r in eligible:
        kw_pass, jd_pass = classify(r)
        if kw_pass and not jd_pass:
            n_pf += 1
        elif not kw_pass and jd_pass:
            n_if += 1
    return {
        "n_total": n_total,
        "n_eligible": n_elig,
        "n_pass_flip": n_pf,
        "n_inverse_flip": n_if,
        "pct_pass_flip": (n_pf / n_elig) if n_elig else 0.0,
        "pct_inverse_flip": (n_if / n_elig) if n_elig else 0.0,
    }


def per_model(rows: list[dict]) -> dict:
    out = {}
    for m in MODELS:
        sub = [r for r in rows if r["model_family"] == m]
        agg = aggregate(sub)
        out[m] = {
            "n_total": agg["n_total"],
            "n_eligible": agg["n_eligible"],
            "n_pass_flip": agg["n_pass_flip"],
            "pct": agg["pct_pass_flip"],
        }
    return out


def per_pert_type(rows: list[dict]) -> dict:
    out = {}
    for pt in PERT_TYPES:
        sub = [r for r in rows if r["perturbation_type"] == pt]
        agg = aggregate(sub)
        out[pt] = {
            "n_total": agg["n_total"],
            "n_eligible": agg["n_eligible"],
            "n_pass_flip": agg["n_pass_flip"],
            "pct": agg["pct_pass_flip"],
        }
    return out


# ── Figure ───────────────────────────────────────────────────────────────────
def make_figure(
    base_rows: list[dict],
    pert_rows: list[dict],
    combined_rows: list[dict],
    *,
    n_base_elig: int,
    n_pert_elig: int,
    n_comb_elig: int,
    path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), facecolor="none")
    panels = [
        ("Base", base_rows, n_base_elig),
        ("Perturbation", pert_rows, n_pert_elig),
        ("Combined", combined_rows, n_comb_elig),
    ]
    for ax, (title, rows, n_elig_panel) in zip(axes, panels):
        ax.set_facecolor("#0a0a14")
        per_m = per_model(rows)
        rates = [per_m[m]["pct"] for m in MODELS]
        bars = ax.bar(
            np.arange(len(MODELS)),
            rates,
            color=[MODEL_COLORS[m] for m in MODELS],
            edgecolor="none",
            width=0.7,
        )
        for bar, rate in zip(bars, rates):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                rate + 0.01,
                f"{100*rate:.1f}%",
                ha="center", va="bottom",
                color="white", fontsize=11,
            )
        # Overall rate dashed line
        agg = aggregate(rows)
        overall = agg["pct_pass_flip"]
        ax.axhline(overall, color="white", lw=1.2, ls="--", alpha=0.55)
        ax.text(
            len(MODELS) - 0.5,
            overall + 0.012,
            f"overall = {100*overall:.1f}%",
            ha="right", va="bottom",
            color="white", fontsize=11, alpha=0.85,
        )
        ax.set_xticks(np.arange(len(MODELS)))
        ax.set_xticklabels(MODELS, color="white", fontsize=12)
        ax.set_ylim(0, max(0.5, max(rates) * 1.25))
        ax.set_ylabel("Pass-flip rate", color="white", fontsize=13)
        ax.set_title(
            f"{title}  (n_eligible = {n_elig_panel})",
            color="white", fontsize=15, pad=10,
        )
        ax.tick_params(colors="white", labelsize=11)
        for spine in ax.spines.values():
            spine.set_color("white"); spine.set_alpha(0.5)
        ax.grid(True, axis="y", alpha=0.15, color="white")
    fig.suptitle(
        "Pass-flip rate (keyword PASS, judge FAIL) on assumption_compliance",
        color="white", fontsize=18, y=1.02,
    )
    fig.text(
        0.5, -0.05,
        "Eligibility: tasks with non-empty required_assumption_checks. "
        f"n_base_eligible={n_base_elig}, n_pert_eligible={n_pert_elig}, "
        f"n_combined_eligible={n_comb_elig}.",
        ha="center", color="white", fontsize=10, alpha=0.85,
    )
    plt.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight", transparent=True)
    plt.close(fig)


# ── Main ─────────────────────────────────────────────────────────────────────
def main() -> int:
    elig = load_eligibility()
    print(f"task specs loaded: {len(elig)} (eligible={sum(elig.values())})")

    base_runs = load_jsonl(BASE_RUNS)
    base_judge = load_jsonl(BASE_JUDGE)
    pert_runs = load_jsonl(PERT_RUNS)
    pert_judge = load_jsonl(PERT_JUDGE)
    print(
        f"base runs={len(base_runs)} judge={len(base_judge)} | "
        f"pert runs={len(pert_runs)} judge={len(pert_judge)}"
    )

    base_rows = join_population(
        base_runs, base_judge, elig, base_lookup_field="task_id"
    )
    pert_rows = join_population(
        pert_runs, pert_judge, elig, base_lookup_field="base_task_id"
    )
    print(f"joined: base={len(base_rows)} pert={len(pert_rows)}")

    # ── Combined: run_id dedup union ────────────────────────────────────────
    seen_ids: set[str] = set()
    combined_rows: list[dict] = []
    collisions = 0
    for r in base_rows + pert_rows:
        rid = r["run_id"]
        if rid in seen_ids:
            collisions += 1
            continue
        seen_ids.add(rid)
        combined_rows.append(r)
    print(f"combined: {len(combined_rows)} (collisions removed: {collisions})")

    base_agg = aggregate(base_rows)
    pert_agg = aggregate(pert_rows)
    comb_agg = aggregate(combined_rows)

    out = {
        "_methodology": (
            "Combined base + perturbation pass-flip analysis on "
            "assumption_compliance dimension. Run-id deduplicated set union. "
            "Eligibility: tasks with non-empty required_assumption_checks."
        ),
        "_methodology_citation": (
            "Yamauchi et al. 2025 (arxiv 2506.13639) — methodology baseline; "
            "Phase 1.5 audit-driven extension to perturbation population."
        ),
        "_supersedes_field": (
            "keyword_vs_judge_agreement.json:pass_flip_assumption "
            "(base-only original retained for backward compat)"
        ),
        "base": {
            "n_total": base_agg["n_total"],
            "n_eligible": base_agg["n_eligible"],
            "n_pass_flip": base_agg["n_pass_flip"],
            "n_inverse_flip": base_agg["n_inverse_flip"],
            "pct_pass_flip": base_agg["pct_pass_flip"],
            "pct_inverse_flip": base_agg["pct_inverse_flip"],
            "per_model": per_model(base_rows),
        },
        "perturbation": {
            "n_total": pert_agg["n_total"],
            "n_eligible": pert_agg["n_eligible"],
            "n_pass_flip": pert_agg["n_pass_flip"],
            "n_inverse_flip": pert_agg["n_inverse_flip"],
            "pct_pass_flip": pert_agg["pct_pass_flip"],
            "pct_inverse_flip": pert_agg["pct_inverse_flip"],
            "per_model": per_model(pert_rows),
            "per_perturbation_type": per_pert_type(pert_rows),
        },
        "combined": {
            "n_total": comb_agg["n_total"],
            "n_eligible": comb_agg["n_eligible"],
            "n_pass_flip": comb_agg["n_pass_flip"],
            "n_inverse_flip": comb_agg["n_inverse_flip"],
            "pct_pass_flip": comb_agg["pct_pass_flip"],
            "pct_inverse_flip": comb_agg["pct_inverse_flip"],
            "n_runid_collisions": collisions,
            "per_model": per_model(combined_rows),
        },
        "comparison": {
            "base_vs_perturbation_diff_pp": (
                100.0 * (pert_agg["pct_pass_flip"] - base_agg["pct_pass_flip"])
            ),
            "interpretation": (
                _interpret(base_agg["pct_pass_flip"], pert_agg["pct_pass_flip"])
            ),
        },
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2))

    make_figure(
        base_rows, pert_rows, combined_rows,
        n_base_elig=base_agg["n_eligible"],
        n_pert_elig=pert_agg["n_eligible"],
        n_comb_elig=comb_agg["n_eligible"],
        path=OUT_FIG,
    )

    # ── Report ──────────────────────────────────────────────────────────────
    print("\n=== BASE ===")
    print(
        f"pass-flip {base_agg['n_pass_flip']} / {base_agg['n_eligible']} "
        f"= {100*base_agg['pct_pass_flip']:.2f}%  "
        f"(canonical reconciliation target: 274 / 1095 = 25.02%)"
    )
    print("\n=== PERTURBATION ===")
    print(
        f"pass-flip {pert_agg['n_pass_flip']} / {pert_agg['n_eligible']} "
        f"= {100*pert_agg['pct_pass_flip']:.2f}%"
    )
    for pt, vals in out["perturbation"]["per_perturbation_type"].items():
        print(
            f"  {pt:10s}: {vals['n_pass_flip']:>4d} / {vals['n_eligible']:>4d} "
            f"= {100*vals['pct']:.2f}%"
        )
    print("\n=== COMBINED ===")
    print(
        f"pass-flip {comb_agg['n_pass_flip']} / {comb_agg['n_eligible']} "
        f"= {100*comb_agg['pct_pass_flip']:.2f}%  "
        f"(collisions={collisions})"
    )
    print("\nPer-model combined pass-flip:")
    for m, v in out["combined"]["per_model"].items():
        print(
            f"  {m:10s}: {v['n_pass_flip']:>4d} / {v['n_eligible']:>4d} "
            f"= {100*v['pct']:.2f}%"
        )

    print(f"\nSaved: {OUT_JSON}")
    print(f"Saved: {OUT_FIG}")
    return 0


def _interpret(base_pct: float, pert_pct: float) -> str:
    diff_pp = 100.0 * (pert_pct - base_pct)
    if abs(diff_pp) < 1.0:
        return (
            "Pass-flip rate is essentially unchanged on perturbations "
            "(<1pp shift), indicating the keyword-vs-judge disagreement is a "
            "stable property of the rubric, not an artefact of the base task "
            "wording."
        )
    direction = "higher" if diff_pp > 0 else "lower"
    return (
        f"Pass-flip rate is {abs(diff_pp):.1f}pp {direction} on perturbations "
        f"vs base, indicating the keyword/judge disagreement "
        f"{'amplifies' if diff_pp > 0 else 'attenuates'} when surface form "
        "changes while underlying mathematics stays fixed."
    )


if __name__ == "__main__":
    raise SystemExit(main())
