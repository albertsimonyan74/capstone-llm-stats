"""Keyword-rubric vs LLM-judge agreement analysis.

Reads keyword scores from experiments/results_v1/runs.jsonl and judge scores
from experiments/results_v2/llm_judge_scores_full.jsonl. Joins by run_id.
Produces per-dimension correlations, per-model and per-task-type breakdowns,
top disagreements, and two PNG figures for the poster.

Run from project root:
    python scripts/keyword_vs_judge_agreement.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from sklearn.metrics import cohen_kappa_score

from baseline.utils_task_id import task_type_from_id as derive_task_type

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from site_palette import (
    SITE_BG, SITE_FG, SITE_FG_MUTED, MODEL_COLORS,
    ACCENT_TEAL, COLOR_GOOD, COLOR_BAD,
    apply_site_theme, color_code_model_ticks, dim_remaining_spines,
)

apply_site_theme()

RUNS_PATH = Path("experiments/results_v1/runs.jsonl")
JUDGE_PATH = Path("experiments/results_v2/llm_judge_scores_full.jsonl")
TASKS_PATH = Path("data/benchmark_v1/tasks_all.json")
PERT_PATH = Path("data/synthetic/perturbations_all.json")
# v1-pert specs (75 task_ids) — used to filter v1-pert rows out of base runs.jsonl
# (those rows were historically appended; not 'base'). Empty after B-2 cleanup.
V1_PERT_PATH = Path("data/synthetic/perturbations.json")
OUT_JSON = Path("experiments/results_v2/keyword_vs_judge_agreement.json")
TOP_JSON = Path("experiments/results_v2/top_disagreements_assumption.json")
FIG_SCATTER = Path("report_materials/figures/judge_validation_scatter.png")
FIG_BARS = Path("report_materials/figures/judge_validation_by_model.png")
WEB_SCATTER = Path("capstone-website/frontend/public/visualizations/png/v2/judge_validation_scatter.png")
WEB_BARS = Path("capstone-website/frontend/public/visualizations/png/v2/judge_validation_by_model.png")

# (label, keyword field, judge dimension key)
DIMS = [
    ("method_structure",       "structure_score",   "method_structure"),
    ("assumption_compliance",  "assumption_score",  "assumption_compliance"),
    ("reasoning_quality",      "reasoning_score",   "reasoning_quality"),
]


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def compute_metrics(pairs_kw: list[float], pairs_jd: list[float]) -> dict:
    if len(pairs_kw) < 2:
        return {"n": len(pairs_kw)}
    a = np.array(pairs_kw)
    b = np.array(pairs_jd)
    rho, _ = stats.spearmanr(a, b)
    pear, _ = stats.pearsonr(a, b)
    mad = float(np.mean(np.abs(a - b)))
    major = int(np.sum(np.abs(a - b) > 0.5))
    bin_a = (a >= 0.5).astype(int)
    bin_b = (b >= 0.5).astype(int)
    try:
        kappa = float(cohen_kappa_score(bin_a, bin_b))
    except ValueError:
        kappa = float("nan")
    return {
        "n": int(len(a)),
        "spearman_rho": float(rho) if not np.isnan(rho) else None,
        "pearson_r": float(pear) if not np.isnan(pear) else None,
        "cohen_kappa_pass_fail": kappa if not np.isnan(kappa) else None,
        "mean_abs_diff": mad,
        "major_disagreements_gt_0_5": major,
        "kw_mean": float(a.mean()),
        "judge_mean": float(b.mean()),
        "kw_pass_rate": float(bin_a.mean()),
        "judge_pass_rate": float(bin_b.mean()),
    }


def load_task_specs() -> dict[str, dict]:
    out = {t["task_id"]: t for t in json.loads(TASKS_PATH.read_text())}
    if PERT_PATH.exists():
        out.update({t["task_id"]: t for t in json.loads(PERT_PATH.read_text())})
    return out


def join_records(runs: list[dict], judge: list[dict], tasks: dict[str, dict]) -> list[dict]:
    judge_by_id = {j["run_id"]: j for j in judge if not j.get("error")}
    joined = []
    for r in runs:
        j = judge_by_id.get(r["run_id"])
        if not j:
            continue
        spec = tasks.get(r["task_id"], {})
        n_req_assump = len(spec.get("required_assumption_checks", []))
        n_req_struct = len(spec.get("required_structure_checks", []))
        joined.append({
            "n_required_assumption_checks": n_req_assump,
            "n_required_structure_checks": n_req_struct,
            "run_id": r["run_id"],
            "task_id": r["task_id"],
            "task_type": derive_task_type(r["task_id"]),
            "model_family": r["model_family"],
            "kw_structure": r.get("structure_score"),
            "kw_assumption": r.get("assumption_score"),
            "kw_reasoning": r.get("reasoning_score"),
            "judge_method": (j.get("method_structure") or {}).get("score"),
            "judge_assumption": (j.get("assumption_compliance") or {}).get("score"),
            "judge_reasoning": (j.get("reasoning_quality") or {}).get("score"),
            "judge_completeness": (j.get("reasoning_completeness") or {}).get("score"),
            "judge_assumption_just": (j.get("assumption_compliance") or {}).get("justification"),
            "raw_response": r.get("raw_response", ""),
        })
    return joined


def per_dim_metrics(joined: list[dict]) -> dict:
    out = {}
    for label, kw_key, jd_key in DIMS:
        kw_field = {"method_structure": "kw_structure",
                    "assumption_compliance": "kw_assumption",
                    "reasoning_quality": "kw_reasoning"}[label]
        jd_field = {"method_structure": "judge_method",
                    "assumption_compliance": "judge_assumption",
                    "reasoning_quality": "judge_reasoning"}[label]
        kws, jds = [], []
        for r in joined:
            if r[kw_field] is None or r[jd_field] is None:
                continue
            kws.append(r[kw_field])
            jds.append(r[jd_field])
        out[label] = compute_metrics(kws, jds)
    return out


def per_model_metrics(joined: list[dict]) -> dict:
    models = sorted({r["model_family"] for r in joined})
    out = {}
    for m in models:
        sub = [r for r in joined if r["model_family"] == m]
        out[m] = per_dim_metrics(sub)
    return out


def per_task_type_metrics(joined: list[dict]) -> dict:
    types = sorted({r["task_type"] for r in joined})
    out = {}
    for tt in types:
        sub = [r for r in joined if r["task_type"] == tt]
        out[tt] = per_dim_metrics(sub)
    return out


def top_disagreements(joined: list[dict], n: int = 30) -> list[dict]:
    cases = []
    for r in joined:
        kw = r["kw_assumption"]
        jd = r["judge_assumption"]
        if kw is None or jd is None:
            continue
        cases.append((abs(kw - jd), r))
    cases.sort(key=lambda x: x[0], reverse=True)
    out = []
    for diff, r in cases[:n]:
        out.append({
            "run_id": r["run_id"],
            "task_id": r["task_id"],
            "model_family": r["model_family"],
            "kw_assumption_score": r["kw_assumption"],
            "judge_assumption_score": r["judge_assumption"],
            "abs_diff": diff,
            "judge_justification": r["judge_assumption_just"],
            "response_excerpt": (r["raw_response"] or "")[:500],
        })
    return out


def make_scatter_figure(joined: list[dict], path: Path) -> None:
    """4-panel 2D bin heatmap of keyword rubric vs external judge scores.

    5×5 count grid per panel (bins centered at 0, 0.25, 0.5, 0.75, 1.0).
    Cell color encodes log(count+1) on viridis. Cells annotated with integer
    counts (white text + black stroke). Diagonal = perfect agreement.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    panels = [
        ("Method / Structure",      "kw_structure",  "judge_method"),
        ("Assumption Compliance",   "kw_assumption", "judge_assumption"),
        ("Reasoning Quality",       "kw_reasoning",  "judge_reasoning"),
        ("Reasoning Completeness",  "kw_reasoning",  "judge_completeness"),
    ]
    bin_centers = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
    bin_edges = np.array([-0.125, 0.125, 0.375, 0.625, 0.875, 1.125])

    fig, axes = plt.subplots(1, 4, figsize=(15, 4.5), dpi=150, facecolor=SITE_BG)
    cmap = mcolors.LinearSegmentedColormap.from_list(
        "teal_seq", [SITE_BG, "#2dd4bf", "#5eead4", "#a7f3d0"]
    )

    for ax, (title, kw_field, jd_field) in zip(axes, panels):
        ax.set_facecolor(SITE_BG)
        xs, ys = [], []
        for r in joined:
            kw = r.get(kw_field)
            jd = r.get(jd_field)
            if kw is None or jd is None:
                continue
            xs.append(kw)
            ys.append(jd)
        xs = np.array(xs)
        ys = np.array(ys)

        H, _, _ = np.histogram2d(ys, xs, bins=[bin_edges, bin_edges])
        total = int(H.sum())
        diag_total = float(np.trace(H)) if H.shape[0] == H.shape[1] else 0.0
        off_pct = (1.0 - diag_total / total) * 100.0 if total > 0 else 0.0

        norm = mcolors.PowerNorm(gamma=0.5, vmin=0.0, vmax=max(H.max(), 1.0))
        ax.imshow(H, cmap=cmap, norm=norm, origin="lower",
                  aspect="auto",
                  extent=(-0.5, len(bin_centers) - 0.5,
                          -0.5, len(bin_centers) - 0.5))

        for i in range(H.shape[0]):
            for j in range(H.shape[1]):
                count = int(H[i, j])
                if count == 0:
                    continue
                ax.text(j, i, str(count), ha="center", va="center",
                        fontsize=11, color="black", fontweight="700")

        # Diagonal cells: green border. Off-diag w/ count>50: red border.
        for i in range(H.shape[0]):
            for j in range(H.shape[1]):
                count = int(H[i, j])
                if i == j:
                    rect = plt.Rectangle((j - 0.5, i - 0.5), 1, 1,
                                         fill=False, edgecolor=COLOR_GOOD,
                                         linewidth=2.0, zorder=4)
                    ax.add_patch(rect)
                elif count > 50:
                    rect = plt.Rectangle((j - 0.5, i - 0.5), 1, 1,
                                         fill=False, edgecolor=COLOR_BAD,
                                         linewidth=1.5, zorder=4)
                    ax.add_patch(rect)

        ax.text(0.97, 0.97,
                f"off-diagonal: {off_pct:.1f}%",
                transform=ax.transAxes, ha="right", va="top",
                fontsize=10, fontweight="700", color=SITE_FG,
                bbox=dict(boxstyle="round,pad=0.4", facecolor=SITE_BG,
                          edgecolor=ACCENT_TEAL, lw=1),
                zorder=5)
        ax.text(0.97, 0.04, f"n = {total}",
                transform=ax.transAxes, ha="right", va="bottom",
                fontsize=8, color=SITE_FG_MUTED, fontweight="600")

        ax.set_xticks(range(len(bin_centers)))
        ax.set_yticks(range(len(bin_centers)))
        ax.set_xticklabels([f"{c:.2f}" for c in bin_centers], fontsize=8)
        ax.set_yticklabels([f"{c:.2f}" for c in bin_centers], fontsize=8)
        ax.set_title(title, fontsize=12, color=SITE_FG, pad=8, fontweight="700")
        ax.set_xlabel("Keyword rubric", fontsize=9, color=SITE_FG_MUTED)
        ax.set_ylabel("LLM judge", fontsize=9, color=SITE_FG_MUTED)
        ax.tick_params(colors=SITE_FG_MUTED, labelsize=8)
        dim_remaining_spines(ax)

    fig.suptitle("Keyword rubric vs external LLM judge — agreement heatmaps",
                 fontsize=14, color=SITE_FG, y=1.02, fontweight="700")
    plt.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=SITE_BG)
    WEB_SCATTER.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(WEB_SCATTER, dpi=150, bbox_inches="tight", facecolor=SITE_BG)
    plt.close(fig)


def make_bar_figure(per_model: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    dims = [d[0] for d in DIMS]
    models = sorted(per_model.keys())
    fig, ax = plt.subplots(figsize=(14, 7), facecolor=SITE_BG)
    ax.set_facecolor(SITE_BG)
    width = 0.15
    x = np.arange(len(dims))
    for i, m in enumerate(models):
        rhos = []
        for d in dims:
            rho = per_model[m][d].get("spearman_rho")
            rhos.append(rho if rho is not None else 0.0)
        ax.bar(x + i*width - width*(len(models)-1)/2, rhos, width=width,
               color=MODEL_COLORS.get(m, SITE_FG_MUTED), label=m, edgecolor="none")
    ax.axhline(0, color=SITE_FG_MUTED, lw=0.7, alpha=0.6)
    ax.set_xticks(x); ax.set_xticklabels(dims, fontsize=14, color=SITE_FG_MUTED)
    ax.set_ylabel("Spearman ρ (keyword vs judge)", fontsize=15, color=SITE_FG_MUTED)
    ax.set_title("Per-model agreement between keyword rubric and external judge",
                 fontsize=18, color=SITE_FG, pad=14)
    ax.set_ylim(-0.6, 1.0)
    ax.tick_params(colors=SITE_FG_MUTED, labelsize=12)
    dim_remaining_spines(ax)
    ax.grid(True, axis="y", alpha=0.06, color="#ffffff")
    ax.legend(loc="upper right", fontsize=12, frameon=False, labelcolor=SITE_FG_MUTED, ncol=5)
    plt.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor=SITE_BG)
    plt.close(fig)


def main() -> int:
    runs_raw = load_jsonl(RUNS_PATH)
    judge_raw = load_jsonl(JUDGE_PATH)
    tasks = load_task_specs()

    v1_pert_ids: frozenset[str] = (
        frozenset(p["task_id"] for p in json.loads(V1_PERT_PATH.read_text()))
        if V1_PERT_PATH.exists() else frozenset()
    )
    runs = [r for r in runs_raw if r.get("task_id") not in v1_pert_ids]
    judge = [j for j in judge_raw if j.get("task_id") not in v1_pert_ids]
    print(
        f"runs.jsonl: raw {len(runs_raw)} → base after v1-pert filter {len(runs)} "
        f"| judge: raw {len(judge_raw)} → {len(judge)} | task specs: {len(tasks)}"
    )
    joined_all = join_records(runs, judge, tasks)
    print(f"joined (judge OK + run match): {len(joined_all)}")
    # Exclude tasks that have NO required_assumption_checks — those score 1.0 trivially
    # under both rubrics' design intent, so they create spurious disagreement.
    joined = [r for r in joined_all if r["n_required_assumption_checks"] > 0]
    excluded = len(joined_all) - len(joined)
    print(f"excluded {excluded} runs whose tasks have empty required_assumption_checks")

    overall = per_dim_metrics(joined)
    by_model = per_model_metrics(joined)
    by_task_type = per_task_type_metrics(joined)
    top = top_disagreements(joined, n=30)

    # Pass-flip count: keyword passes (>=0.5), judge fails (<0.5) on assumption
    pass_kw_fail_judge = sum(
        1 for r in joined
        if r["kw_assumption"] is not None and r["judge_assumption"] is not None
        and r["kw_assumption"] >= 0.5 and r["judge_assumption"] < 0.5
    )
    pass_judge_fail_kw = sum(
        1 for r in joined
        if r["kw_assumption"] is not None and r["judge_assumption"] is not None
        and r["judge_assumption"] >= 0.5 and r["kw_assumption"] < 0.5
    )
    n_with_both = sum(
        1 for r in joined
        if r["kw_assumption"] is not None and r["judge_assumption"] is not None
    )

    output = {
        "n_joined": len(joined),
        "n_with_both_assumption_scores": n_with_both,
        "overall_per_dimension": overall,
        "per_model": by_model,
        "per_task_type": by_task_type,
        "pass_flip_assumption": {
            "keyword_pass_judge_fail": pass_kw_fail_judge,
            "keyword_fail_judge_pass": pass_judge_fail_kw,
            "n_compared": n_with_both,
            "kw_pass_judge_fail_pct": 100.0 * pass_kw_fail_judge / max(1, n_with_both),
        },
        "judge_completeness_alone": {
            "mean": float(np.mean([r["judge_completeness"] for r in joined
                                   if r["judge_completeness"] is not None])),
            "n": sum(1 for r in joined if r["judge_completeness"] is not None),
        },
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(output, indent=2))
    TOP_JSON.write_text(json.dumps(top, indent=2))

    make_scatter_figure(joined, FIG_SCATTER)
    make_bar_figure(by_model, FIG_BARS)

    # ── Console report ──
    print("\n=== OVERALL PER-DIMENSION ===")
    print(f"{'dim':25s} {'n':>6s} {'spearman':>9s} {'pearson':>9s} {'kappa':>7s} {'MAD':>7s} {'major>0.5':>10s}  kw_mean→judge_mean  kw_pass→jd_pass")
    for d, m in overall.items():
        print(f"{d:25s} {m['n']:>6d} {m['spearman_rho']:>9.3f} {m['pearson_r']:>9.3f} "
              f"{m['cohen_kappa_pass_fail']:>7.3f} {m['mean_abs_diff']:>7.3f} "
              f"{m['major_disagreements_gt_0_5']:>10d}  {m['kw_mean']:.3f}→{m['judge_mean']:.3f}  "
              f"{m['kw_pass_rate']:.3f}→{m['judge_pass_rate']:.3f}")

    print("\n=== PER MODEL — Spearman ρ ===")
    print(f"{'model':10s} " + " ".join(f"{d[:18]:>20s}" for d in [d[0] for d in DIMS]))
    for m, dims_metrics in by_model.items():
        row = f"{m:10s} "
        for d in [d[0] for d in DIMS]:
            r = dims_metrics[d].get("spearman_rho")
            row += f"{(r if r is not None else 0):>20.3f}"
        print(row)

    print("\n=== PASS FLIP (assumption_compliance) ===")
    pf = output["pass_flip_assumption"]
    print(f"  Compared: {pf['n_compared']}")
    print(f"  Keyword PASS but judge FAIL: {pf['keyword_pass_judge_fail']} "
          f"({pf['kw_pass_judge_fail_pct']:.1f}%)  ← headline poster line")
    print(f"  Keyword FAIL but judge PASS: {pf['keyword_fail_judge_pass']}")

    print("\n=== TOP 5 DISAGREEMENTS (assumption_compliance) ===")
    for i, t in enumerate(top[:5], 1):
        print(f"\n  [{i}] {t['model_family']}/{t['task_id']}  "
              f"kw={t['kw_assumption_score']}  judge={t['judge_assumption_score']}  "
              f"diff={t['abs_diff']:.2f}")
        print(f"      justification: {t['judge_justification'][:160]}")
        print(f"      response[:200]: {t['response_excerpt'][:200]!r}")

    print(f"\nSaved: {OUT_JSON}")
    print(f"Saved: {TOP_JSON}")
    print(f"Saved: {FIG_SCATTER}")
    print(f"Saved: {FIG_BARS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
