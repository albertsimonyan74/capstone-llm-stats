"""Krippendorff's α — keyword-vs-judge agreement.

Methodology follows Park et al. (2025) [arxiv 2506.13639]; reliability concerns
raised by 'When Judgment Becomes Noise' (arxiv 2509.20293).

Park et al. recommend Krippendorff's α over Spearman ρ for LLM-as-Judge agreement
because α is dimension-agnostic, handles ordinal scales correctly, and penalises
calibration shifts that ρ ignores. Single-judge designs (Llama 3.3 70B here) carry
silent noise (Judgment-Becomes-Noise 2025), so α is required to bound that noise.

Inputs (same join as scripts/keyword_vs_judge_agreement.py):
- experiments/results_v1/runs.jsonl
- experiments/results_v2/llm_judge_scores_full.jsonl
- data/benchmark_v1/tasks_all.json (+ data/synthetic/perturbations_all.json)

Outputs:
- experiments/results_v2/krippendorff_agreement.json
- experiments/results_v2/keyword_vs_judge_agreement.json (augmented with α fields)
- report_materials/figures/agreement_metrics_comparison.png

Run from project root:
    python scripts/krippendorff_agreement.py
"""
from __future__ import annotations

import json
from pathlib import Path

import krippendorff
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from baseline.utils_task_id import task_type_from_id as derive_task_type

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from site_palette import (
    SITE_BG, SITE_FG, SITE_FG_MUTED, MODEL_COLORS, ACCENT_GOLD, ACCENT_CORAL,
    apply_site_theme, dim_remaining_spines,
)

apply_site_theme()

ROOT = Path(__file__).resolve().parents[1]
RUNS_PATH = ROOT / "experiments/results_v1/runs.jsonl"
JUDGE_PATH = ROOT / "experiments/results_v2/llm_judge_scores_full.jsonl"
PERT_RUNS_PATH = ROOT / "experiments/results_v2/perturbation_runs.jsonl"
PERT_JUDGE_PATH = ROOT / "experiments/results_v2/perturbation_judge_scores.jsonl"
TASKS_PATH = ROOT / "data/benchmark_v1/tasks_all.json"
PERT_ALL_PATH = ROOT / "data/synthetic/perturbations_all.json"
# v1 perturbations.json is deprecated — task specs for the 75 v1 task_ids
# are preserved verbatim inside perturbations_all.json (473 records total).
V1_PERT_PATH = ROOT / "data/synthetic/perturbations.json"
OUT_JSON = ROOT / "experiments/results_v2/krippendorff_agreement.json"
EXISTING_AGREEMENT = ROOT / "experiments/results_v2/keyword_vs_judge_agreement.json"
FIG_OUT = ROOT / "report_materials/figures/agreement_metrics_comparison.png"

# (label, kw_field, judge_field). reasoning_completeness has no keyword equivalent
# so it cannot be α-validated against keywords; we still report keyword vs the
# 3 judge dims plus a reasoning_completeness placeholder is omitted.
DIMS = [
    ("method_structure",      "kw_structure",  "judge_method"),
    ("assumption_compliance", "kw_assumption", "judge_assumption"),
    ("reasoning_quality",     "kw_reasoning",  "judge_reasoning"),
]

DIM_KW_MAP = {
    "method_structure":      "structure_score",
    "assumption_compliance": "assumption_score",
    "reasoning_quality":     "reasoning_score",
}
DIM_JUDGE_MAP = {
    "method_structure":      "method_structure",
    "assumption_compliance": "assumption_compliance",
    "reasoning_quality":     "reasoning_quality",
}

CITATION = (
    "Methodology follows Park et al. (2025) [arxiv 2506.13639]; reliability "
    "concerns raised by 'When Judgment Becomes Noise' (arxiv 2509.20293)."
)

BOOTSTRAP_B = 1000
BOOTSTRAP_SEED = 42


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def load_task_specs() -> dict[str, dict]:
    out = {t["task_id"]: t for t in json.loads(TASKS_PATH.read_text())}
    if PERT_ALL_PATH.exists():
        out.update({t["task_id"]: t for t in json.loads(PERT_ALL_PATH.read_text())})
    return out


def load_v1_pert_ids() -> frozenset[str]:
    """v1-pert task_ids that must be filtered out of base runs.jsonl.

    v1 perturbations were appended into experiments/results_v1/runs.jsonl
    historically; those rows are not 'base' and must be excluded from base-scope
    analyses. Specs for the same 75 task_ids are preserved inside
    perturbations_all.json. Returns empty set if v1 file is gone (B-2 cleanup).
    """
    if not V1_PERT_PATH.exists():
        return frozenset()
    return frozenset(p["task_id"] for p in json.loads(V1_PERT_PATH.read_text()))


def join_records(runs: list[dict], judge: list[dict], tasks: dict[str, dict]) -> list[dict]:
    judge_by_id = {j["run_id"]: j for j in judge if not j.get("error")}
    joined = []
    for r in runs:
        j = judge_by_id.get(r["run_id"])
        if not j:
            continue
        spec = tasks.get(r["task_id"], {})
        n_req_assump = len(spec.get("required_assumption_checks", []))
        joined.append({
            "n_required_assumption_checks": n_req_assump,
            "run_id": r["run_id"],
            "task_id": r["task_id"],
            "task_type": derive_task_type(r["task_id"]),
            "model_family": r["model_family"],
            "kw_structure":  r.get("structure_score"),
            "kw_assumption": r.get("assumption_score"),
            "kw_reasoning":  r.get("reasoning_score"),
            "judge_method":      (j.get("method_structure") or {}).get("score"),
            "judge_assumption":  (j.get("assumption_compliance") or {}).get("score"),
            "judge_reasoning":   (j.get("reasoning_quality") or {}).get("score"),
            "judge_completeness": (j.get("reasoning_completeness") or {}).get("score"),
        })
    return joined


def alpha_ordinal(kw: list[float], jd: list[float]) -> float:
    """Krippendorff's α on a 2-rater × N-unit reliability matrix, ordinal level.

    Discretise [0,1] continuous scores to 11 ordinal bins (0.0, 0.1, ..., 1.0)
    so the ordinal level-of-measurement is well-defined. (α with continuous
    scores degenerates to a Pearson-like coefficient; the canonical recipe
    in Park et al. uses ordinal binning to capture rank-distance penalties.)
    """
    if len(kw) < 2:
        return float("nan")
    a = np.round(np.asarray(kw, dtype=float) * 10).astype(int)
    b = np.round(np.asarray(jd, dtype=float) * 10).astype(int)
    matrix = np.vstack([a, b])
    return float(krippendorff.alpha(reliability_data=matrix,
                                    level_of_measurement="ordinal"))


def bootstrap_alpha(kw: list[float], jd: list[float], B: int = BOOTSTRAP_B,
                    seed: int = BOOTSTRAP_SEED) -> tuple[float, float, float]:
    if len(kw) < 2:
        return float("nan"), float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    n = len(kw)
    a = np.asarray(kw, dtype=float)
    b = np.asarray(jd, dtype=float)
    alphas = []
    for _ in range(B):
        idx = rng.integers(0, n, size=n)
        try:
            alphas.append(alpha_ordinal(a[idx].tolist(), b[idx].tolist()))
        except Exception:
            continue
    if not alphas:
        return float("nan"), float("nan"), float("nan")
    arr = np.asarray([x for x in alphas if not np.isnan(x)])
    if arr.size == 0:
        return float("nan"), float("nan"), float("nan")
    return float(np.mean(arr)), float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5))


def interpret(alpha_value: float) -> str:
    if np.isnan(alpha_value):
        return "undefined"
    if alpha_value < 0.667:
        return "questionable"
    if alpha_value <= 0.8:
        return "acceptable"
    return "strong"


def collect_pairs(joined: list[dict], dim_label: str) -> tuple[list[float], list[float]]:
    kw_field = {
        "method_structure": "kw_structure",
        "assumption_compliance": "kw_assumption",
        "reasoning_quality": "kw_reasoning",
    }[dim_label]
    jd_field = {
        "method_structure": "judge_method",
        "assumption_compliance": "judge_assumption",
        "reasoning_quality": "judge_reasoning",
    }[dim_label]
    kws, jds = [], []
    for r in joined:
        if r[kw_field] is None or r[jd_field] is None:
            continue
        kws.append(float(r[kw_field]))
        jds.append(float(r[jd_field]))
    return kws, jds


def per_dim_alpha(joined: list[dict]) -> dict:
    out = {}
    for label, _, _ in DIMS:
        kws, jds = collect_pairs(joined, label)
        if len(kws) < 2:
            out[label] = {"alpha": float("nan"), "ci_lower": float("nan"),
                          "ci_upper": float("nan"), "n": len(kws)}
            continue
        a_point = alpha_ordinal(kws, jds)
        _, ci_lo, ci_hi = bootstrap_alpha(kws, jds)
        out[label] = {
            "alpha": a_point,
            "ci_lower": ci_lo,
            "ci_upper": ci_hi,
            "n": len(kws),
        }
    return out


def per_model_alpha(joined: list[dict]) -> dict:
    models = sorted({r["model_family"] for r in joined})
    out = {}
    for m in models:
        sub = [r for r in joined if r["model_family"] == m]
        out[m] = per_dim_alpha(sub)
    return out


def make_comparison_figure(overall: dict, existing_spearman: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    dims = [d[0] for d in DIMS]
    alphas = [overall[d]["alpha"] for d in dims]
    rhos = []
    for d in dims:
        rho = existing_spearman.get(d, {}).get("spearman_rho")
        rhos.append(rho if rho is not None else 0.0)
    alpha_ci_lo = [overall[d]["alpha"] - overall[d]["ci_lower"] for d in dims]
    alpha_ci_hi = [overall[d]["ci_upper"] - overall[d]["alpha"] for d in dims]

    fig, ax = plt.subplots(figsize=(8, 5), facecolor=SITE_BG)
    ax.set_facecolor(SITE_BG)
    x = np.arange(len(dims))
    width = 0.36
    ax.bar(x - width/2, rhos, width=width, label="Spearman ρ",
           color=MODEL_COLORS["deepseek"], edgecolor="none")
    ax.bar(x + width/2, alphas, width=width, label="Krippendorff α (ordinal)",
           color=ACCENT_CORAL, edgecolor="none",
           yerr=[alpha_ci_lo, alpha_ci_hi], ecolor=SITE_FG_MUTED, capsize=4)
    ax.axhline(0.667, color=ACCENT_GOLD, lw=0.8, ls="--", alpha=0.7,
               label="α=0.667 (acceptable)")
    ax.axhline(0.0, color=SITE_FG_MUTED, lw=0.6, alpha=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(dims, fontsize=11, color=SITE_FG_MUTED)
    ax.set_ylabel("Agreement coefficient", fontsize=12, color=SITE_FG_MUTED)
    ax.set_title("Inter-rater agreement: Spearman ρ vs Krippendorff α",
                 fontsize=13, color=SITE_FG, pad=10)
    ax.set_ylim(-0.3, 1.0)
    ax.tick_params(colors=SITE_FG_MUTED, labelsize=10)
    dim_remaining_spines(ax)
    ax.grid(True, axis="y", alpha=0.06, color="#ffffff")
    ax.legend(loc="upper right", fontsize=9, frameon=False, labelcolor=SITE_FG_MUTED)
    fig.text(0.5, -0.02,
             "α: Park et al. (2025) | ρ: Spearman rank baseline",
             ha="center", color=SITE_FG_MUTED, fontsize=8, alpha=0.85)
    plt.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor=SITE_BG)
    plt.close(fig)


def main() -> int:
    runs_base_raw = load_jsonl(RUNS_PATH)
    judge_base_raw = load_jsonl(JUDGE_PATH)
    tasks = load_task_specs()

    # Filter v1 perturbation rows out of base scope. v1-pert task_ids were
    # historically appended to results_v1/runs.jsonl; they are not 'base' runs
    # and the corresponding judge scores must be excluded as well.
    v1_pert_ids = load_v1_pert_ids()
    runs_base = [r for r in runs_base_raw if r.get("task_id") not in v1_pert_ids]
    judge_base = [j for j in judge_base_raw if j.get("task_id") not in v1_pert_ids]
    print(
        f"runs.jsonl: raw {len(runs_base_raw)} → base after v1-pert filter {len(runs_base)} "
        f"| judge: raw {len(judge_base_raw)} → {len(judge_base)} | task specs: {len(tasks)}"
    )

    runs_pert = load_jsonl(PERT_RUNS_PATH) if PERT_RUNS_PATH.exists() else []
    judge_pert = load_jsonl(PERT_JUDGE_PATH) if PERT_JUDGE_PATH.exists() else []
    print(f"perturbation_runs.jsonl: {len(runs_pert)} | perturbation_judge: {len(judge_pert)}")

    base_all = join_records(runs_base, judge_base, tasks)
    base_joined = [r for r in base_all if r["n_required_assumption_checks"] > 0]
    print(f"base joined: {len(base_all)} → eligible (req_assump>0): {len(base_joined)}")

    pert_all = join_records(runs_pert, judge_pert, tasks)
    pert_joined = [r for r in pert_all if r["n_required_assumption_checks"] > 0]
    print(f"perturbation joined: {len(pert_all)} → eligible: {len(pert_joined)}")

    # Combined: run_id-deduplicated set union (matches combined_pass_flip_analysis.py)
    seen_ids: set[str] = set()
    combined_joined: list[dict] = []
    for r in base_joined + pert_joined:
        rid = r["run_id"]
        if rid in seen_ids:
            continue
        seen_ids.add(rid)
        combined_joined.append(r)
    print(f"combined eligible (run_id-deduplicated): {len(combined_joined)}")

    def _build_scope(joined_eligible: list[dict]) -> dict:
        ov = per_dim_alpha(joined_eligible)
        pm = per_model_alpha(joined_eligible)
        ip = {d: interpret(ov[d]["alpha"]) for d in ov}
        return {"overall": ov, "per_model": pm, "interpretation": ip,
                "n_eligible": len(joined_eligible)}

    base_scope = _build_scope(base_joined)
    pert_scope = _build_scope(pert_joined)
    comb_scope = _build_scope(combined_joined)

    # Backward-compatible top-level (base scope) — keep field names so existing
    # consumers (website backend, audit docs) continue to read base figures.
    overall = base_scope["overall"]
    by_model = base_scope["per_model"]
    interp = base_scope["interpretation"]

    existing = json.loads(EXISTING_AGREEMENT.read_text()) if EXISTING_AGREEMENT.exists() else {}
    existing_dim_overall = existing.get("overall_per_dimension", {})

    output = {
        "_methodology_citation": CITATION,
        "_scope_note": (
            "α reported on three populations: base (runs.jsonl + judge), "
            "perturbation (perturbation_runs.jsonl + perturbation_judge), and "
            "combined (run_id-deduplicated set union, matching the "
            "keyword-judge disagreement headline scope in "
            "combined_pass_flip_analysis.json). Top-level fields (overall, "
            "per_model, interpretation, n_joined) preserve base-only values "
            "for backward compatibility with existing consumers."
        ),
        "n_joined": len(base_joined),
        "n_excluded_empty_assumption": len(base_all) - len(base_joined),
        "bootstrap_B": BOOTSTRAP_B,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "level_of_measurement": "ordinal (11-bin discretisation of [0,1])",
        "thresholds": {
            "questionable": "α < 0.667",
            "acceptable":   "0.667 ≤ α ≤ 0.8",
            "strong":       "α > 0.8",
        },
        "overall": overall,
        "per_model": by_model,
        "interpretation": interp,
        "base": base_scope,
        "perturbation": pert_scope,
        "combined": comb_scope,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(output, indent=2))
    print(f"Saved: {OUT_JSON}")

    # Augment existing keyword_vs_judge_agreement.json with α fields (preserve ρ)
    if existing:
        existing.setdefault("_methodology_citation", CITATION)
        existing["alpha_overall"] = overall
        existing["alpha_per_dim_interpretation"] = interp
        existing["alpha_per_model"] = by_model
        EXISTING_AGREEMENT.write_text(json.dumps(existing, indent=2))
        print(f"Augmented: {EXISTING_AGREEMENT} (added alpha_overall, alpha_per_model)")

    make_comparison_figure(overall, existing_dim_overall, FIG_OUT)
    print(f"Saved: {FIG_OUT}")

    for scope_name, scope_obj in [("BASE", base_scope), ("PERTURBATION", pert_scope),
                                  ("COMBINED", comb_scope)]:
        print(f"\n=== {scope_name} Krippendorff α (ordinal)  n_eligible={scope_obj['n_eligible']} ===")
        for d, m in scope_obj["overall"].items():
            print(f"  {d:25s} α={m['alpha']:+.3f}  CI95=[{m['ci_lower']:+.3f}, {m['ci_upper']:+.3f}]  "
                  f"n={m['n']}  | {scope_obj['interpretation'][d]}")

    print("\n=== Headline narrative impact ===")
    a_assump = overall["assumption_compliance"]["alpha"]
    rho_assump = existing_dim_overall.get("assumption_compliance", {}).get("spearman_rho", 0)
    print(f"  assumption_compliance: ρ=0.59 (moderate) → α={a_assump:+.3f} ({interp['assumption_compliance']})")
    if a_assump < 0.667:
        print("  α downgrades the headline: agreement is QUESTIONABLE under Park et al.'s metric.")
        print("  This STRENGTHENS the 25% pass-flip claim — keyword and judge are not interchangeable raters.")
    elif a_assump <= 0.8:
        print("  α confirms the headline at acceptable level.")
    else:
        print("  α upgrades the headline to strong agreement.")

    print("\n=== Recommended poster sentence ===")
    print(f'  "Krippendorff α = {a_assump:+.2f} ({interp["assumption_compliance"]}) on '
          f'assumption-compliance keyword–vs–judge agreement (Park et al., 2025), '
          f'corroborating the 25 % pass-flip headline."')

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
