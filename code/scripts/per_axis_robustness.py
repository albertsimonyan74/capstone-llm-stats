"""Per-(model, axis) robustness decomposition (Section IV.F.3).

Mirrors the canonical robustness computation in
code/scripts/recompute_downstream.py:step_3b() — same NMACR pairing,
same v2-only scope (v1 seeds filtered).

Output: 5 models x 3 axes = 15 cells of R = mean_pert / mean_base.

Run from repo root:
    python code/scripts/per_axis_robustness.py

Output:
    data/processed_data/results_v2/per_axis_robustness.json
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

NMACR = Path("data/processed_data/results_v2/nmacr_scores_v2.jsonl")
V1_PERT_PATH = Path("data/raw_data/synthetic/perturbations.json")
OUT_JSON = Path("data/processed_data/results_v2/per_axis_robustness.json")

MODELS = ["claude", "chatgpt", "gemini", "deepseek", "mistral"]
AXES = ["rephrase", "semantic", "numerical"]


def main() -> None:
    v1_pert_ids = (
        frozenset(s["task_id"] for s in json.loads(V1_PERT_PATH.read_text()))
        if V1_PERT_PATH.exists() else frozenset()
    )

    records = []
    with NMACR.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if "_header" in r:
                continue
            if r.get("task_id") in v1_pert_ids:
                continue
            records.append(r)

    # Base lookup: (model, task_id) -> aggregate_new
    base = {}
    for r in records:
        if r["perturbation"]:
            continue
        if r["aggregate_new"] is None:
            continue
        base[(r["model"], r["task_id"])] = r["aggregate_new"]

    # Per (model, axis) accumulators
    paired: dict[tuple[str, str], list[tuple[float, float]]] = defaultdict(list)
    for r in records:
        if not r["perturbation"]:
            continue
        if r["aggregate_new"] is None:
            continue
        m = r["model"]
        bid = r["base_task_id"]
        ax = r["perturbation_type"]
        if ax not in AXES:
            continue
        bs = base.get((m, bid))
        if bs is None:
            continue
        paired[(m, ax)].append((bs, r["aggregate_new"]))

    out = {"per_model_axis": {}, "per_model_overall": {}, "per_axis_overall": {}}
    sums_check = 0
    for m in MODELS:
        rec_m = {}
        all_pairs = []
        for ax in AXES:
            pairs = paired[(m, ax)]
            n = len(pairs)
            sums_check += n
            if n == 0:
                rec_m[ax] = {"n_paired": 0}
                continue
            base_vals = [b for b, _ in pairs]
            pert_vals = [p for _, p in pairs]
            mean_base = sum(base_vals) / n
            mean_pert = sum(pert_vals) / n
            ratio = mean_pert / mean_base if mean_base else 0.0
            rec_m[ax] = {
                "n_paired": n,
                "mean_base": round(mean_base, 4),
                "mean_pert": round(mean_pert, 4),
                "delta": round(mean_base - mean_pert, 4),
                "ratio_R": round(ratio, 4),
            }
            all_pairs.extend(pairs)
        # Overall (sanity vs Table I)
        if all_pairs:
            mb = sum(b for b, _ in all_pairs) / len(all_pairs)
            mp = sum(p for _, p in all_pairs) / len(all_pairs)
            out["per_model_overall"][m] = {
                "n_paired": len(all_pairs),
                "mean_base": round(mb, 4),
                "mean_pert": round(mp, 4),
                "ratio_R": round(mp / mb if mb else 0, 4),
            }
        out["per_model_axis"][m] = rec_m

    # Per-axis overall (across models)
    for ax in AXES:
        all_pairs = []
        for m in MODELS:
            all_pairs.extend(paired[(m, ax)])
        if all_pairs:
            mb = sum(b for b, _ in all_pairs) / len(all_pairs)
            mp = sum(p for _, p in all_pairs) / len(all_pairs)
            out["per_axis_overall"][ax] = {
                "n_paired": len(all_pairs),
                "mean_base": round(mb, 4),
                "mean_pert": round(mp, 4),
                "ratio_R": round(mp / mb if mb else 0, 4),
            }

    # Variance decomposition
    # ratio[m][ax]
    ratios = {m: {ax: out["per_model_axis"][m].get(ax, {}).get("ratio_R")
                  for ax in AXES} for m in MODELS}
    # variance across axes (within each model), then averaged across models
    import statistics
    axis_var_within_model = []
    for m in MODELS:
        vals = [ratios[m][ax] for ax in AXES if ratios[m][ax] is not None]
        if len(vals) > 1:
            axis_var_within_model.append(statistics.pvariance(vals))
    model_var_within_axis = []
    for ax in AXES:
        vals = [ratios[m][ax] for m in MODELS if ratios[m][ax] is not None]
        if len(vals) > 1:
            model_var_within_axis.append(statistics.pvariance(vals))
    out["variance_decomposition"] = {
        "mean_axis_variance_within_model": round(
            sum(axis_var_within_model) / len(axis_var_within_model), 6),
        "mean_model_variance_within_axis": round(
            sum(model_var_within_axis) / len(model_var_within_axis), 6),
    }
    out["_cross_check"] = {
        "total_paired": sums_check,
        "expected": 1990,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2))

    # Print
    print(f"=== Cross-check ===")
    print(f"  total paired: {sums_check} (expect 1990)")
    print()
    print(f"=== Per-(model, axis) robustness R ===")
    header = f"{'model':<10}" + "".join(f"{ax:>13}" for ax in AXES) + f"{'overall':>13}"
    print(header)
    for m in MODELS:
        row = f"{m:<10}"
        for ax in AXES:
            r = out["per_model_axis"][m].get(ax, {}).get("ratio_R")
            n = out["per_model_axis"][m].get(ax, {}).get("n_paired", 0)
            row += f"  {r:>.4f}({n:>3})" if r is not None else f"{'n/a':>13}"
        ov = out["per_model_overall"][m]["ratio_R"]
        row += f"      {ov:.4f}"
        print(row)
    print()
    print(f"=== Per-axis overall (across models) ===")
    for ax in AXES:
        r = out["per_axis_overall"][ax]
        print(f"  {ax:<11} n={r['n_paired']:4d}  R={r['ratio_R']:.4f}  "
              f"delta={r['mean_base'] - r['mean_pert']:.4f}")
    print()
    print(f"=== Variance decomposition ===")
    print(f"  mean axis-variance within model: "
          f"{out['variance_decomposition']['mean_axis_variance_within_model']:.6f}")
    print(f"  mean model-variance within axis: "
          f"{out['variance_decomposition']['mean_model_variance_within_axis']:.6f}")


if __name__ == "__main__":
    main()
