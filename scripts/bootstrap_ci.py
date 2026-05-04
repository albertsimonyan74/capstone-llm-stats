"""Bootstrap 95% CIs on accuracy + robustness deltas (RQ4 rigor, audit P-2 / F-3).

Accuracy: per-model bootstrap of base run final_score means (n=171 per model).
Robustness: per-model bootstrap of paired (base - pert) deltas (n=473 per model).
Calibration: ECE point estimates only — bootstrap requires binned resampling, deferred.

Inputs:
- experiments/results_v1/runs.jsonl
- experiments/results_v2/perturbation_runs.jsonl

Outputs:
- experiments/results_v2/bootstrap_ci.json
- report_materials/figures/bootstrap_ci.png
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from site_palette import (
    SITE_BG, SITE_FG, SITE_FG_MUTED, MODEL_COLORS,
    apply_site_theme, color_code_model_ticks, dim_remaining_spines,
)

apply_site_theme()

ROOT = Path(__file__).resolve().parents[1]
BASE_RUNS = ROOT / "experiments" / "results_v1" / "runs.jsonl"
PERT_RUNS = ROOT / "experiments" / "results_v2" / "perturbation_runs.jsonl"
CALIB = ROOT / "experiments" / "results_v2" / "calibration.json"
OUT_JSON = ROOT / "experiments" / "results_v2" / "bootstrap_ci.json"
OUT_FIG = ROOT / "report_materials" / "figures" / "bootstrap_ci.png"

MODELS = ["claude", "chatgpt", "gemini", "deepseek", "mistral"]
COLORS = MODEL_COLORS
PERT_SUFFIX_RE = re.compile(r"_(rephrase|numerical|semantic)(?:_v\d+)?$")
B = 10_000
SEED = 42


def load_jsonl(path: Path):
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def is_perturbation(tid: str) -> bool:
    return bool(PERT_SUFFIX_RE.search(tid))


def bootstrap_mean_ci(values: np.ndarray, B: int, rng: np.random.Generator):
    n = len(values)
    idx = rng.integers(0, n, size=(B, n))
    samples = values[idx].mean(axis=1)
    lo, hi = np.percentile(samples, [2.5, 97.5])
    return float(values.mean()), float(lo), float(hi), int(n)


def collect_base_scores() -> dict[str, np.ndarray]:
    by_model: dict[str, list[float]] = defaultdict(list)
    for r in load_jsonl(BASE_RUNS):
        tid = r.get("task_id", "")
        if not tid or is_perturbation(tid):
            continue
        score = r.get("final_score")
        mf = r.get("model_family")
        if score is None or not mf:
            continue
        by_model[mf].append(float(score))
    return {m: np.asarray(by_model[m], dtype=float) for m in MODELS if by_model[m]}


def collect_pert_deltas() -> dict[str, np.ndarray]:
    base_scores: dict[tuple[str, str], float] = {}
    for r in load_jsonl(BASE_RUNS):
        tid = r.get("task_id", "")
        if not tid or is_perturbation(tid):
            continue
        score = r.get("final_score")
        mf = r.get("model_family")
        if score is None or not mf:
            continue
        base_scores[(mf, tid)] = float(score)

    by_model: dict[str, list[float]] = defaultdict(list)
    for r in load_jsonl(PERT_RUNS):
        if r.get("error"):
            continue
        mf = r.get("model_family")
        base_tid = r.get("base_task_id")
        score = r.get("final_score")
        if mf is None or base_tid is None or score is None:
            continue
        bs = base_scores.get((mf, base_tid))
        if bs is None:
            continue
        by_model[mf].append(bs - float(score))
    return {m: np.asarray(by_model[m], dtype=float) for m in MODELS if by_model[m]}


def separability(ci_map: dict[str, tuple[float, float, float, int]]):
    out = []
    keys = list(ci_map.keys())
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = keys[i], keys[j]
            _, lo_a, hi_a, _ = ci_map[a]
            _, lo_b, hi_b, _ = ci_map[b]
            sep = "separable" if (hi_a < lo_b or hi_b < lo_a) else "not_separable"
            out.append([a, b, sep])
    return out


def main():
    rng = np.random.default_rng(SEED)

    acc = collect_base_scores()
    rob = collect_pert_deltas()

    acc_ci = {m: bootstrap_mean_ci(acc[m], B, rng) for m in MODELS if m in acc}
    rob_ci = {m: bootstrap_mean_ci(rob[m], B, rng) for m in MODELS if m in rob}

    # ECE point estimates from calibration.json (no CI — see note).
    calib_data = json.loads(CALIB.read_text())
    ece_points = {}
    if isinstance(calib_data, dict):
        per_model = calib_data.get("per_model") or calib_data
        for m in MODELS:
            entry = per_model.get(m) if isinstance(per_model, dict) else None
            if isinstance(entry, dict) and "ece" in entry:
                ece_points[m] = float(entry["ece"])

    out = {
        "B": B,
        "seed": SEED,
        "method": "non-parametric bootstrap on per-run final_score (accuracy) and per-run paired delta (robustness); 95% percentile CI",
        "accuracy": {
            m: {"mean": round(mean, 6), "ci_lower": round(lo, 6), "ci_upper": round(hi, 6), "n": n}
            for m, (mean, lo, hi, n) in acc_ci.items()
        },
        "robustness": {
            m: {"mean_delta": round(mean, 6), "ci_lower": round(lo, 6), "ci_upper": round(hi, 6), "n": n}
            for m, (mean, lo, hi, n) in rob_ci.items()
        },
        "separability": {
            "accuracy": separability(acc_ci),
            "robustness": separability(rob_ci),
        },
        "calibration_note": (
            "ECE is a per-model point estimate using 4 fixed confidence buckets. "
            "A bootstrap CI requires binned resampling (resample within each bucket "
            "and re-aggregate). Deferred to paper scope. Point ECE values reported "
            "as-is from calibration.json."
        ),
        "calibration_ece_points": ece_points,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2))
    print(f"Wrote {OUT_JSON}")

    plot_ci(acc_ci, rob_ci)
    print(f"Wrote {OUT_FIG}")
    print_summary(acc_ci, rob_ci, out["separability"])


def plot_ci(acc_ci, rob_ci):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), dpi=300, facecolor=SITE_BG)

    # Accuracy panel — sort high→low
    order_a = sorted(acc_ci.keys(), key=lambda m: -acc_ci[m][0])
    means_a = [acc_ci[m][0] for m in order_a]
    los_a = [acc_ci[m][1] for m in order_a]
    his_a = [acc_ci[m][2] for m in order_a]
    err_lo_a = [m - lo for m, lo in zip(means_a, los_a)]
    err_hi_a = [hi - m for m, hi in zip(means_a, his_a)]
    ax = axes[0]
    ax.set_facecolor(SITE_BG)
    x = np.arange(len(order_a))
    for i, m in enumerate(order_a):
        ax.errorbar(
            x[i], means_a[i],
            yerr=[[err_lo_a[i]], [err_hi_a[i]]],
            fmt="o", color=COLORS[m], ecolor=COLORS[m],
            elinewidth=2.4, capsize=6, capthick=2, markersize=10,
            markeredgecolor=SITE_BG, markeredgewidth=0.6,
        )
    ax.set_xticks(x)
    ax.set_xticklabels([m.upper() for m in order_a], fontsize=10, fontweight="bold")
    color_code_model_ticks(ax)
    ax.set_ylabel("Accuracy (mean final_score)", fontsize=10, color=SITE_FG_MUTED)
    ax.set_title("Accuracy — 95% bootstrap CI (n=171/model, B=10k)",
                 fontsize=11, fontweight="bold", color=SITE_FG)
    ax.grid(axis="y", linestyle="-", linewidth=0.5, alpha=0.06, color="#ffffff")
    dim_remaining_spines(ax)

    # Robustness panel — sort low→high delta (best→worst)
    order_r = sorted(rob_ci.keys(), key=lambda m: rob_ci[m][0])
    means_r = [rob_ci[m][0] for m in order_r]
    los_r = [rob_ci[m][1] for m in order_r]
    his_r = [rob_ci[m][2] for m in order_r]
    err_lo_r = [m - lo for m, lo in zip(means_r, los_r)]
    err_hi_r = [hi - m for m, hi in zip(means_r, his_r)]
    ax = axes[1]
    ax.set_facecolor(SITE_BG)
    x = np.arange(len(order_r))
    ax.axhline(0, color=SITE_FG_MUTED, linestyle="--", linewidth=1, alpha=0.6, zorder=0)
    for i, m in enumerate(order_r):
        ax.errorbar(
            x[i], means_r[i],
            yerr=[[err_lo_r[i]], [err_hi_r[i]]],
            fmt="o", color=COLORS[m], ecolor=COLORS[m],
            elinewidth=2.4, capsize=6, capthick=2, markersize=10,
            markeredgecolor=SITE_BG, markeredgewidth=0.6,
        )
    ax.set_xticks(x)
    ax.set_xticklabels([m.upper() for m in order_r], fontsize=10, fontweight="bold")
    color_code_model_ticks(ax)
    ax.set_ylabel("Robustness Δ (base − pert; lower = more robust)",
                  fontsize=10, color=SITE_FG_MUTED)
    ax.set_title("Robustness Δ — 95% bootstrap CI (n=473/model, B=10k)",
                 fontsize=11, fontweight="bold", color=SITE_FG)
    ax.grid(axis="y", linestyle="-", linewidth=0.5, alpha=0.06, color="#ffffff")
    dim_remaining_spines(ax)

    fig.tight_layout()
    OUT_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_FIG, dpi=300, facecolor=SITE_BG, bbox_inches="tight")
    plt.close(fig)


def print_summary(acc_ci, rob_ci, sep):
    print("\n=== Accuracy 95% CI ===")
    for m in sorted(acc_ci, key=lambda k: -acc_ci[k][0]):
        mean, lo, hi, n = acc_ci[m]
        print(f"  {m:9s} mean={mean:.4f}  CI=[{lo:.4f}, {hi:.4f}]  n={n}")
    print("\n=== Robustness Δ 95% CI ===")
    for m in sorted(rob_ci, key=lambda k: rob_ci[k][0]):
        mean, lo, hi, n = rob_ci[m]
        print(f"  {m:9s} delta={mean:+.4f}  CI=[{lo:+.4f}, {hi:+.4f}]  n={n}")
    print("\n=== Separability (non-overlapping 95% CIs) ===")
    print("Accuracy:")
    for a, b, s in sep["accuracy"]:
        print(f"  {a:9s} vs {b:9s} -> {s}")
    print("Robustness:")
    for a, b, s in sep["robustness"]:
        print(f"  {a:9s} vs {b:9s} -> {s}")

    print("\n=== Plain-English summary ===")
    sep_acc = [(a, b) for a, b, s in sep["accuracy"] if s == "separable"]
    notsep_acc = [(a, b) for a, b, s in sep["accuracy"] if s == "not_separable"]
    sep_rob = [(a, b) for a, b, s in sep["robustness"] if s == "separable"]
    notsep_rob = [(a, b) for a, b, s in sep["robustness"] if s == "not_separable"]
    print(f"Accuracy: {len(sep_acc)}/{len(sep_acc)+len(notsep_acc)} pairs separable (non-overlapping 95% CIs).")
    if notsep_acc:
        print("  Not separable: " + "; ".join(f"{a} vs {b}" for a, b in notsep_acc))
    print(f"Robustness: {len(sep_rob)}/{len(sep_rob)+len(notsep_rob)} pairs separable.")
    if notsep_rob:
        print("  Not separable (within noise): " + "; ".join(f"{a} vs {b}" for a, b in notsep_rob))


if __name__ == "__main__":
    main()
