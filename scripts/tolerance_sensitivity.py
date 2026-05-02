"""
Tolerance sensitivity analysis.

Re-scores stored base runs at three (absolute, relative) tolerance levels and
reports per-model accuracy + ranking stability.

Correctness rule per numeric target:
    |parsed - true| <= max(absolute, relative * |true|)

A run is "correct" iff length matches AND every numeric target is within
tolerance (run-level all-targets accuracy). Runs without numeric targets
(CONCEPTUAL) are excluded from accuracy denominators.

Inputs (read-only):
    experiments/results_v1/runs.jsonl

Outputs:
    experiments/results_v2/tolerance_sensitivity.json
    report_materials/figures/tolerance_sensitivity.png
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
RUNS_PATH = ROOT / "experiments" / "results_v1" / "runs.jsonl"
OUT_JSON = ROOT / "experiments" / "results_v2" / "tolerance_sensitivity.json"
OUT_FIG = ROOT / "report_materials" / "figures" / "tolerance_sensitivity.png"

TOLERANCE_LEVELS: Dict[str, Tuple[float, float]] = {
    "tight":   (0.005, 0.025),
    "default": (0.010, 0.050),
    "loose":   (0.020, 0.100),
}

MODELS = ["claude", "chatgpt", "gemini", "deepseek", "mistral"]


def is_run_correct(parsed: List[float], gt: List[float],
                   abs_tol: float, rel_tol: float) -> bool:
    if not gt or len(parsed) != len(gt):
        return False
    for p, g in zip(parsed, gt):
        if abs(p - g) > max(abs_tol, rel_tol * abs(g)):
            return False
    return True


def score_runs(runs, abs_tol: float, rel_tol: float) -> Dict[str, Dict]:
    per_model = {m: {"n_correct": 0, "n_total": 0} for m in MODELS}
    for r in runs:
        gt = r.get("ground_truth") or []
        if not gt:
            continue
        m = r.get("model_family")
        if m not in per_model:
            continue
        parsed = r.get("parsed_values") or []
        per_model[m]["n_total"] += 1
        if is_run_correct(parsed, gt, abs_tol, rel_tol):
            per_model[m]["n_correct"] += 1
    for m in per_model:
        n_t = per_model[m]["n_total"]
        per_model[m]["accuracy"] = (per_model[m]["n_correct"] / n_t) if n_t else 0.0
    return per_model


def plot_grouped_bars(results: Dict[str, Dict[str, Dict]], path: Path) -> None:
    levels = list(TOLERANCE_LEVELS.keys())
    x = np.arange(len(MODELS))
    width = 0.27
    colors = {"tight": "#3b6dd0", "default": "#888888", "loose": "#d06b3b"}

    fig, ax = plt.subplots(figsize=(8.5, 4.6), dpi=300)
    fig.patch.set_alpha(0.0)
    ax.set_facecolor((0, 0, 0, 0))

    for i, lvl in enumerate(levels):
        accs = [results[lvl][m]["accuracy"] for m in MODELS]
        offset = (i - 1) * width
        bars = ax.bar(x + offset, accs, width,
                      label=f"{lvl} (abs={TOLERANCE_LEVELS[lvl][0]}, rel={TOLERANCE_LEVELS[lvl][1]})",
                      color=colors[lvl], edgecolor="black", linewidth=0.5)
        for b, a in zip(bars, accs):
            ax.text(b.get_x() + b.get_width() / 2, a + 0.005,
                    f"{a:.2f}", ha="center", va="bottom", fontsize=7)

    ax.set_xticks(x)
    ax.set_xticklabels([m.capitalize() for m in MODELS])
    ax.set_ylabel("Accuracy (all numeric targets within tolerance)")
    ax.set_title("Tolerance Sensitivity — Per-Model Accuracy at 3 Tolerance Levels")
    ax.set_ylim(0, max(0.6, max(
        results[lvl][m]["accuracy"] for lvl in levels for m in MODELS
    ) + 0.08))
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.legend(loc="upper right", fontsize=8, framealpha=0.85)

    plt.tight_layout()
    plt.savefig(path, dpi=300, transparent=True, bbox_inches="tight")
    plt.close(fig)


def rank(per_model: Dict[str, Dict]) -> List[str]:
    return sorted(MODELS, key=lambda m: per_model[m]["accuracy"], reverse=True)


def main() -> None:
    runs = [json.loads(l) for l in RUNS_PATH.read_text().splitlines() if l.strip()]
    print(f"loaded {len(runs)} runs from {RUNS_PATH}")

    results: Dict[str, Dict[str, Dict]] = {}
    for lvl, (a, r) in TOLERANCE_LEVELS.items():
        results[lvl] = score_runs(runs, a, r)
        print(f"\n[{lvl}] abs={a}  rel={r}")
        for m in MODELS:
            d = results[lvl][m]
            print(f"  {m:8s}  acc={d['accuracy']:.4f}  ({d['n_correct']}/{d['n_total']})")

    rankings = {lvl: rank(results[lvl]) for lvl in TOLERANCE_LEVELS}
    print("\nRankings:")
    for lvl in TOLERANCE_LEVELS:
        print(f"  {lvl}: {rankings[lvl]}")
    stable = len({tuple(v) for v in rankings.values()}) == 1

    payload = {
        "tolerance_levels": {k: {"absolute": a, "relative": r}
                             for k, (a, r) in TOLERANCE_LEVELS.items()},
        "results": results,
        "rankings": rankings,
        "ranking_stable_across_levels": stable,
        "n_runs_total": len(runs),
        "n_runs_scored_per_level": {
            lvl: sum(results[lvl][m]["n_total"] for m in MODELS)
            for lvl in TOLERANCE_LEVELS
        },
        "rule": "|parsed - true| <= max(absolute, relative * |true|); run correct iff length matches and all targets within tolerance",
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2))
    print(f"\nwrote {OUT_JSON}")

    OUT_FIG.parent.mkdir(parents=True, exist_ok=True)
    plot_grouped_bars(results, OUT_FIG)
    print(f"wrote {OUT_FIG}")

    print(f"\nranking stable across all 3 tolerance levels: {stable}")


if __name__ == "__main__":
    main()
