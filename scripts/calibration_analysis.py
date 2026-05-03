"""Calibration analysis (RQ5): reliability diagrams + Expected Calibration Error.

Per-model: bucket runs by extracted confidence (high/medium/low/unstated),
compute mean accuracy per bucket, plot reliability diagram, compute ECE.

Confidence is re-extracted via `llm_runner.response_parser.extract_confidence`
from each run's `raw_response`. The `confidence_score` field stored in
runs.jsonl is the *calibration* score, not raw confidence — we want raw.

Accuracy:
- Numeric tasks: `numeric_score` field (already in runs.jsonl, 0..1)
- Conceptual / no numeric_score: judge's `reasoning_quality.score`

Outputs:
- experiments/results_v2/calibration.json
- report_materials/figures/calibration_reliability.png
- report_materials/figures/calibration_ece_ranking.png

Run:
    python scripts/calibration_analysis.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from llm_runner.response_parser import extract_confidence

RUNS_PATH = Path("experiments/results_v1/runs.jsonl")
# v1-pert specs (75 task_ids) — filter v1-pert rows out of base scope. Empty after B-2.
V1_PERT_PATH = Path("data/synthetic/perturbations.json")
JUDGE_PATH = Path("experiments/results_v2/llm_judge_scores_full.jsonl")
OUT_JSON = Path("experiments/results_v2/calibration.json")
FIG_RELIABILITY = Path("report_materials/figures/calibration_reliability.png")
FIG_ECE = Path("report_materials/figures/calibration_ece_ranking.png")

MODEL_COLORS = {
    "claude":   "#00CED1",
    "chatgpt":  "#7FFFD4",
    "gemini":   "#FF6B6B",
    "deepseek": "#4A90D9",
    "mistral":  "#A78BFA",
}

# Bucket → numeric confidence claim (per spec)
BUCKET_CONF = {"high": 0.9, "medium": 0.6, "low": 0.3, "unstated": 0.5}
BUCKETS = ["low", "medium", "high", "unstated"]


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def bucket_for(conf: float | None, raw: str) -> str:
    """Map raw extracted confidence (0.1..0.9) to bucket.

    extract_confidence default is 0.5 when no hedge/definitive words found.
    Treat exactly 0.5 as 'unstated'. Otherwise:
      conf >= 0.7 → high
      0.4 <= conf < 0.7 (excl 0.5) → medium
      conf < 0.4 → low
    """
    if conf is None:
        return "unstated"
    # Heuristic: if response is empty, unstated
    if not (raw or "").strip():
        return "unstated"
    if abs(conf - 0.5) < 1e-9:
        return "unstated"
    if conf >= 0.7:
        return "high"
    if conf < 0.4:
        return "low"
    return "medium"


def join_records(runs: list[dict], judge: list[dict]) -> list[dict]:
    judge_by_id = {j["run_id"]: j for j in judge if not j.get("error")}
    out = []
    for r in runs:
        if r.get("error"):
            continue
        raw = r.get("raw_response") or ""
        conf = extract_confidence(raw) if raw.strip() else None
        bucket = bucket_for(conf, raw)

        # Accuracy: numeric_score if non-null + task had numeric targets,
        # else fall back to judge.reasoning_quality.score
        acc: float | None = r.get("numeric_score")
        if acc is None or r.get("ground_truth") in (None, [], {}) and acc == 0:
            j = judge_by_id.get(r["run_id"])
            if j:
                rq = (j.get("reasoning_quality") or {}).get("score")
                if rq is not None:
                    acc = rq
        if acc is None:
            continue

        out.append({
            "run_id": r["run_id"],
            "model_family": r["model_family"],
            "raw_confidence": conf,
            "bucket": bucket,
            "bucket_confidence": BUCKET_CONF[bucket],
            "accuracy": float(acc),
        })
    return out


def compute_per_model(joined: list[dict]) -> dict:
    models = sorted({r["model_family"] for r in joined})
    out = {}
    for m in models:
        sub = [r for r in joined if r["model_family"] == m]
        n_total = len(sub)
        per_bucket = {}
        ece = 0.0
        for b in BUCKETS:
            in_b = [r for r in sub if r["bucket"] == b]
            n_b = len(in_b)
            mean_acc = float(np.mean([r["accuracy"] for r in in_b])) if n_b else None
            per_bucket[b] = {
                "n": n_b,
                "mean_accuracy": mean_acc,
                "claimed_confidence": BUCKET_CONF[b],
            }
            if n_b and mean_acc is not None:
                ece += (n_b / n_total) * abs(mean_acc - BUCKET_CONF[b])
        # Overall accuracy for ranking comparison
        overall_acc = float(np.mean([r["accuracy"] for r in sub])) if sub else 0.0
        out[m] = {
            "n_total": n_total,
            "per_bucket": per_bucket,
            "ece": float(ece),
            "overall_accuracy": overall_acc,
        }
    return out


def make_reliability_figure(per_model: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(11, 9), facecolor="none")
    ax.set_facecolor("#0a0a14")

    # diagonal
    ax.plot([0, 1], [0, 1], color="white", lw=1.4, ls="--", alpha=0.45,
            label="perfect calibration")

    # one polyline per model, points sized by bucket count
    for m, info in per_model.items():
        color = MODEL_COLORS.get(m, "#aaa")
        xs, ys, sizes = [], [], []
        for b in ["low", "medium", "high"]:  # exclude 'unstated' from line
            d = info["per_bucket"][b]
            if d["n"] == 0 or d["mean_accuracy"] is None:
                continue
            xs.append(d["claimed_confidence"])
            ys.append(d["mean_accuracy"])
            sizes.append(40 + d["n"] * 1.3)
        if xs:
            ax.plot(xs, ys, color=color, lw=2.5, alpha=0.9)
            ax.scatter(xs, ys, s=sizes, c=color, edgecolors="white",
                       linewidths=0.8, alpha=0.95,
                       label=f"{m}  (ECE={info['ece']:.3f})")

    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xlabel("Claimed confidence", fontsize=16, color="white")
    ax.set_ylabel("Empirical accuracy", fontsize=16, color="white")
    ax.set_title("Reliability diagram — per-model calibration",
                 fontsize=20, color="white", pad=14)
    ax.tick_params(colors="white", labelsize=12)
    for spine in ax.spines.values():
        spine.set_color("white"); spine.set_alpha(0.5)
    ax.grid(True, alpha=0.18, color="white")
    ax.legend(loc="lower right", fontsize=12, frameon=False, labelcolor="white")
    plt.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight", transparent=True)
    plt.close(fig)


def make_ece_figure(per_model: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    items = sorted(per_model.items(), key=lambda kv: kv[1]["ece"])
    models = [m for m, _ in items]
    eces = [info["ece"] for _, info in items]
    colors = [MODEL_COLORS.get(m, "#aaa") for m in models]

    fig, ax = plt.subplots(figsize=(12, 6.5), facecolor="none")
    ax.set_facecolor("#0a0a14")
    bars = ax.bar(models, eces, color=colors, edgecolor="white", linewidth=0.7)
    for bar, e in zip(bars, eces):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                f"{e:.3f}", ha="center", color="white", fontsize=13, fontweight="bold")
    ax.set_ylabel("Expected Calibration Error (lower is better)",
                  fontsize=15, color="white")
    ax.set_title("Calibration ranking — ECE per model",
                 fontsize=20, color="white", pad=14)
    ax.tick_params(colors="white", labelsize=13)
    for spine in ax.spines.values():
        spine.set_color("white"); spine.set_alpha(0.5)
    ax.grid(True, axis="y", alpha=0.18, color="white")
    ax.set_ylim(0, max(eces) * 1.18)
    plt.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight", transparent=True)
    plt.close(fig)


def main() -> int:
    runs_raw = load_jsonl(RUNS_PATH)
    judge_raw = load_jsonl(JUDGE_PATH)
    v1_pert_ids: frozenset[str] = (
        frozenset(p["task_id"] for p in json.loads(V1_PERT_PATH.read_text()))
        if V1_PERT_PATH.exists() else frozenset()
    )
    runs = [r for r in runs_raw if r.get("task_id") not in v1_pert_ids]
    judge = [j for j in judge_raw if j.get("task_id") not in v1_pert_ids]
    print(
        f"runs: raw {len(runs_raw)} → after v1-pert filter {len(runs)} "
        f"| judge: raw {len(judge_raw)} → {len(judge)}"
    )
    joined = join_records(runs, judge)
    print(f"joined (with accuracy + confidence): {len(joined)}")

    per_model = compute_per_model(joined)

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(per_model, indent=2))
    make_reliability_figure(per_model, FIG_RELIABILITY)
    make_ece_figure(per_model, FIG_ECE)

    # ── Console report ──
    print("\n=== PER-MODEL CALIBRATION ===")
    print(f"{'model':10s} {'high_acc':>10s} {'med_acc':>10s} {'low_acc':>10s} "
          f"{'unstated_acc':>13s} {'ECE':>8s} {'overall_acc':>12s}  "
          f"{'(n_high/med/low/uns)':<24s}")
    for m, info in per_model.items():
        b = info["per_bucket"]
        h = b["high"]; mb = b["medium"]; lo = b["low"]; un = b["unstated"]
        def fmt(x): return f"{x:.3f}" if x is not None else "  —  "
        print(f"{m:10s} {fmt(h['mean_accuracy']):>10s} {fmt(mb['mean_accuracy']):>10s} "
              f"{fmt(lo['mean_accuracy']):>10s} {fmt(un['mean_accuracy']):>13s} "
              f"{info['ece']:>8.3f} {info['overall_accuracy']:>12.3f}  "
              f"({h['n']}/{mb['n']}/{lo['n']}/{un['n']})")

    print("\n=== CALIBRATION RANKING (best → worst by ECE) ===")
    cal_rank = sorted(per_model.items(), key=lambda kv: kv[1]["ece"])
    for i, (m, info) in enumerate(cal_rank, 1):
        print(f"  {i}. {m:10s}  ECE={info['ece']:.3f}")

    print("\n=== ACCURACY RANKING (best → worst) ===")
    acc_rank = sorted(per_model.items(), key=lambda kv: -kv[1]["overall_accuracy"])
    for i, (m, info) in enumerate(acc_rank, 1):
        print(f"  {i}. {m:10s}  overall_accuracy={info['overall_accuracy']:.3f}")

    print(f"\nSaved: {OUT_JSON}")
    print(f"Saved: {FIG_RELIABILITY}")
    print(f"Saved: {FIG_ECE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
