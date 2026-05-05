"""Derive per-base-task-type × model robustness Δ heatmap for poster.

Source: experiments/results_v2/robustness_v2.json, field
per_task_type_heatmap (per-perturbation-task × model). Aggregate by
base task type (mean Δ across all perturbation suffixes for each
base type × model).

Family groupings are inferred from canonical statistical-method
conventions (no source-of-truth file in repo). Mapping documented in
the derived JSON `family_mapping` field.

Output: poster/figures/derived/robustness_heatmap_data.json
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "baseline"))
from utils_task_id import task_type_from_id  # noqa: E402

ROBUST = ROOT / "experiments" / "results_v2" / "robustness_v2.json"
TASKS  = ROOT / "data" / "benchmark_v1" / "tasks_all.json"
OUT    = ROOT / "poster" / "figures" / "derived" / "robustness_heatmap_data.json"

MODELS = ["claude", "chatgpt", "gemini", "deepseek", "mistral"]

# ── Family groupings (manually curated; documented in derived JSON) ───────
FAMILY_OF = {
    # Bayesian core (conjugate / closed-form posterior reasoning)
    "BETA_BINOM":      "Bayesian Core",
    "GAMMA_POISSON":   "Bayesian Core",
    "NORMAL_GAMMA":    "Bayesian Core",
    "BAYES_FACTOR":    "Bayesian Core",
    "DIRICHLET":       "Bayesian Core",
    "JEFFREYS":        "Bayesian Core",
    "BINOM_FLAT":      "Bayesian Core",
    "DISC_MEDIAN":     "Bayesian Core",
    "HPD":             "Bayesian Core",
    "CI_CREDIBLE":     "Bayesian Core",
    "PPC":             "Bayesian Core",

    # MLE / frequentist
    "MLE_MAP":         "MLE / Freq.",
    "MLE_EFFICIENCY":  "MLE / Freq.",
    "FISHER_INFO":     "MLE / Freq.",
    "UNIFORM_MLE":     "MLE / Freq.",
    "BIAS_VAR":        "MLE / Freq.",
    "MSE_COMPARE":     "MLE / Freq.",

    # MCMC
    "GIBBS":           "MCMC",
    "MH":              "MCMC",
    "HMC":             "MCMC",
    "RJMCMC":          "MCMC",
    "STATIONARY":      "MCMC",

    # Regression
    "REGRESSION":      "Regression",

    # Causal / predictive
    "BAYES_REG":       "Causal / Pred.",

    # Advanced (computational, decision theory, niche)
    "ABC":             "Advanced",
    "VB":              "Advanced",
    "HIERARCHICAL":    "Advanced",
    "BAYES_RISK":      "Advanced",
    "MINIMAX":         "Advanced",
    "RC_BOUND":        "Advanced",
    "LOG_ML":          "Advanced",
    "GAMBLER":         "Advanced",
    "MARKOV":          "Advanced",
    "ORDER_STAT":      "Advanced",
    "RANGE_DIST":      "Advanced",
    "BOX_MULLER":      "Advanced",
    "OPT_SCALED":      "Advanced",
    "CONCEPTUAL":      "Advanced",
}

FAMILY_ORDER = [
    "Bayesian Core",
    "MLE / Freq.",
    "MCMC",
    "Regression",
    "Causal / Pred.",
    "Advanced",
]

PERT_SUFFIXES = ("_rephrase_v2", "_numerical_v2", "_semantic_v2",
                 "_rephrase",    "_numerical",    "_semantic", "_v2")


def base_type(tid: str) -> str:
    s = tid
    for suf in PERT_SUFFIXES:
        if s.endswith(suf):
            s = s[: -len(suf)]
            break
    return task_type_from_id(s)


def main() -> int:
    robust = json.loads(ROBUST.read_text())
    ph = robust["per_task_type_heatmap"]

    all_types = sorted({task_type_from_id(t["task_id"])
                        for t in json.loads(TASKS.read_text())})
    print(f"task_types in benchmark: {len(all_types)}")

    # Aggregate Δ per (base_type, model)
    bucket: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: {m: [] for m in MODELS}
    )
    for tid, mdict in ph.items():
        bt = base_type(tid)
        for m, v in mdict.items():
            if m in MODELS:
                bucket[bt][m].append(float(v))

    cells: dict[str, dict[str, float | None]] = {}
    n_pert: dict[str, dict[str, int]] = {}
    for bt in all_types:
        cells[bt]  = {m: (mean(bucket[bt][m]) if bucket[bt][m] else None) for m in MODELS}
        n_pert[bt] = {m: len(bucket[bt][m]) for m in MODELS}

    # Verify family map covers everything
    missing = [t for t in all_types if t not in FAMILY_OF]
    if missing:
        sys.exit(f"FAMILY_OF missing types: {missing}")

    # Spot-check assertions on three website-published values
    spot = [
        ("DIRICHLET",  "deepseek", -0.25),
        ("ORDER_STAT", "deepseek", +0.32),
        ("BIAS_VAR",   "chatgpt",  -0.12),
    ]
    for bt, m, expected in spot:
        got = cells[bt][m]
        assert got is not None, f"{bt}/{m} missing"
        assert abs(got - expected) <= 0.01, (
            f"{bt}/{m}: got {got:+.4f}, expected ≈{expected:+.2f}"
        )

    out = {
        "_methodology": (
            "Per-base-task-type × model robustness Δ heatmap. Aggregated "
            "from robustness_v2.json:per_task_type_heatmap by mean Δ across "
            "all perturbation suffixes (_rephrase_v2 / _numerical_v2 / "
            "_semantic_v2) for each (base_type, model) pair. Sign convention: "
            "positive Δ = drop under perturbation (worse); negative Δ = "
            "improvement (rare)."
        ),
        "_pipeline_source": "robustness_v2.json:per_task_type_heatmap",
        "models": MODELS,
        "task_types": all_types,
        "family_mapping": FAMILY_OF,
        "family_order":   FAMILY_ORDER,
        "cells":  cells,
        "n_pert": n_pert,
        "spot_check_passed": [
            {"task": bt, "model": m, "expected": e, "got": cells[bt][m]}
            for bt, m, e in spot
        ],
        "task_types_with_no_perturbation_data": [
            bt for bt in all_types if all(v == 0 for v in n_pert[bt].values())
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))
    print(f"\nWrote {OUT}")
    print(f"types with no pert data: {out['task_types_with_no_perturbation_data']}")
    print("Spot-check assertions all passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
