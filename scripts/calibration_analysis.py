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

# Canonical site palette (single source of truth).
sys.path.insert(0, str(Path(__file__).resolve().parent))
from site_palette import (
    SITE_BG, SITE_FG, SITE_FG_MUTED, MODEL_COLORS,
    apply_site_theme, dim_remaining_spines,
)

apply_site_theme()

RUNS_PATH = Path("experiments/results_v1/runs.jsonl")
# v1-pert specs (75 task_ids) — filter v1-pert rows out of base scope. Empty after B-2.
V1_PERT_PATH = Path("data/synthetic/perturbations.json")
JUDGE_PATH = Path("experiments/results_v2/llm_judge_scores_full.jsonl")
OUT_JSON = Path("experiments/results_v2/calibration.json")
FIG_RELIABILITY = Path("report_materials/figures/calibration_reliability.png")
FIG_RELIABILITY_WEB = Path(
    "capstone-website/frontend/public/visualizations/png/v2/calibration_reliability.png"
)
FIG_RELIABILITY_SM = Path(
    "report_materials/figures/calibration_reliability_smallmultiples.png"
)
FIG_RELIABILITY_SM_WEB = Path(
    "capstone-website/frontend/public/visualizations/png/v2/calibration_reliability_smallmultiples.png"
)
FIG_ECE = Path("report_materials/figures/calibration_ece_ranking.png")
FIG_ECE_WEB = Path(
    "capstone-website/frontend/public/visualizations/png/v2/calibration_ece_ranking.png"
)

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


def make_reliability_figure(per_model: dict, paths: list[Path]) -> None:
    """Reliability diagram: per-model accuracy vs claimed-confidence buckets.

    Dark site theme (Tier 2A): SITE_BG figure background, site palette per
    model, subtle over/underconfidence shading. Active buckets across
    canonical: low (0.3), unstated (0.5), medium (0.6). `high` (0.9) is
    empty for every model — omitted automatically. Points below y=x
    diagonal = overconfident; above = underconfident.
    """
    from site_palette import COLOR_GOOD, COLOR_BAD

    # 11×6.875 → 1.6 aspect, fits 16:10 website card without crop.
    fig, ax = plt.subplots(figsize=(11, 6.875), dpi=150, facecolor=SITE_BG)
    ax.set_facecolor(SITE_BG)

    # over/underconfidence shaded regions (subtle, site-coordinated)
    ax.fill_between([0, 1], [0, 0], [0, 1], color=COLOR_BAD, alpha=0.04, zorder=0)
    ax.fill_between([0, 1], [0, 1], [1, 1], color=COLOR_GOOD, alpha=0.04, zorder=0)

    # corner annotation replaces the rotated diagonal labels (less clutter)
    ax.text(0.265, 0.78,
            "Above diagonal: under-confident\nBelow diagonal: over-confident",
            fontsize=8, color=SITE_FG_MUTED, alpha=0.85, va="top", ha="left")

    # perfect-calibration diagonal
    ax.plot([0, 1], [0, 1],
            color=SITE_FG_MUTED, lw=1.4, ls="--", alpha=0.7,
            label="Perfect calibration", zorder=2)

    # per-model line + scatter; size ∝ bucket sample count.
    # Claude line highlighted (zorder=5, lw=2.4, full alpha); others muted to
    # focus the eye on the best-calibrated model.
    bucket_order = ["low", "unstated", "medium", "high"]
    endpoint_records = []
    for m in ["claude", "chatgpt", "gemini", "deepseek", "mistral"]:
        info = per_model.get(m)
        if not info:
            continue
        color = MODEL_COLORS.get(m, "#94a3b8")
        pts = []
        for b in bucket_order:
            d = info["per_bucket"].get(b, {})
            if d.get("n", 0) > 0 and d.get("mean_accuracy") is not None:
                pts.append((d["claimed_confidence"], d["mean_accuracy"], d["n"]))
        pts.sort(key=lambda p: p[0])
        if not pts:
            continue
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        sizes = [max(80, p[2] * 1.6) for p in pts]
        is_claude = (m == "claude")
        line_lw = 2.4 if is_claude else 1.3
        line_alpha = 1.0 if is_claude else 0.55
        line_zorder = 5 if is_claude else 3
        if len(pts) >= 2:
            ax.plot(xs, ys, color=color, lw=line_lw, alpha=line_alpha,
                    zorder=line_zorder)
        ax.scatter(xs, ys, s=sizes, c=color, edgecolors=SITE_BG,
                   linewidths=2.0, alpha=0.95, zorder=line_zorder + 1,
                   label=f"{m.upper()}  (ECE={info['ece']:.3f})")
        # rightmost data point → endpoint label (drawn after loop so labels
        # overlay all lines)
        endpoint_records.append((m, color, xs[-1], ys[-1], info["ece"]))

    for m, color, xr, yr, ece in endpoint_records:
        ax.text(xr + 0.005, yr,
                f"{m.title()} · {ece:.3f}",
                fontsize=8, color=color, va="center", ha="left", zorder=6)

    ax.set_xlim(0.25, 0.65)
    ax.set_ylim(0.2, 0.8)
    ax.set_xticks([0.3, 0.4, 0.5, 0.6])
    ax.set_yticks([0.2, 0.4, 0.5, 0.6, 0.8])
    ax.set_xlabel("Claimed confidence (verbalized bucket)",
                  fontsize=11, color=SITE_FG_MUTED)
    ax.set_ylabel("Empirical accuracy", fontsize=11, color=SITE_FG_MUTED)
    ax.set_title(
        "Calibration Reliability · Verbalized",
        fontsize=13, fontweight="700", color=SITE_FG, pad=14, loc="left")
    ax.tick_params(colors=SITE_FG_MUTED, labelsize=10)
    dim_remaining_spines(ax)
    ax.grid(True, alpha=0.06, linestyle="-", linewidth=0.5, color="#ffffff")
    ax.set_axisbelow(True)
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0),
              frameon=False, fontsize=9.5, labelcolor=SITE_FG_MUTED)

    plt.tight_layout()
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=SITE_BG)
    plt.close(fig)


def make_reliability_smallmultiples(per_model: dict, paths: list[Path]) -> None:
    """5×3 calibration-gap heatmap: empirical accuracy − claimed confidence.

    Replaces the prior 1×5 reliability-diagram small-multiples. Filename
    preserved so manifest paths stay valid.
    """
    import matplotlib.colors as mcolors

    bucket_order = ["low", "unstated", "medium"]
    bucket_labels = ["0.3", "0.5", "0.6"]
    models = ["claude", "chatgpt", "gemini", "deepseek", "mistral"]
    DISPLAY = {
        "claude":   "Claude",
        "chatgpt":  "ChatGPT",
        "gemini":   "Gemini",
        "deepseek": "DeepSeek",
        "mistral":  "Mistral",
    }

    M = np.full((len(models), len(bucket_order)), np.nan)
    for i, m in enumerate(models):
        info = per_model.get(m)
        if not info:
            continue
        for j, b in enumerate(bucket_order):
            d = info["per_bucket"].get(b, {})
            if d.get("n", 0) > 0 and d.get("mean_accuracy") is not None:
                M[i, j] = d["mean_accuracy"] - d["claimed_confidence"]

    norm = mcolors.TwoSlopeNorm(vcenter=0.0, vmin=-0.25, vmax=0.25)
    cmap = plt.get_cmap("RdBu_r")

    fig, ax = plt.subplots(figsize=(11, 4), dpi=150, facecolor=SITE_BG)
    ax.set_facecolor(SITE_BG)

    # Mask NaNs so imshow paints them transparent; gray fill drawn separately.
    im = ax.imshow(np.ma.masked_invalid(M), cmap=cmap, norm=norm,
                   aspect="auto", origin="upper")

    for i in range(len(models)):
        for j in range(len(bucket_order)):
            v = M[i, j]
            if np.isnan(v):
                ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1,
                                           facecolor="#3a3f4b", edgecolor=SITE_BG,
                                           linewidth=0.5, zorder=2))
                ax.text(j, i, "n/a", ha="center", va="center",
                        fontsize=10, color=SITE_FG_MUTED, fontweight="600",
                        zorder=3)
                continue
            sign = "+" if v >= 0 else "−"
            ax.text(j, i, f"{sign}{abs(v):.2f}", ha="center", va="center",
                    fontsize=11, color="black", fontweight="700")

    ax.set_xticks(range(len(bucket_order)))
    ax.set_xticklabels(bucket_labels, fontsize=10, color=SITE_FG)
    ax.xaxis.tick_top()
    ax.tick_params(axis="x", which="major", pad=6, length=0)
    ax.set_xlabel("Claimed confidence bucket", fontsize=9,
                  color=SITE_FG_MUTED, labelpad=8)
    ax.xaxis.set_label_position("top")

    ax.set_yticks(range(len(models)))
    ax.set_yticklabels([DISPLAY[m] for m in models],
                       fontsize=11, fontweight="700")
    for tick, m in zip(ax.get_yticklabels(), models):
        tick.set_color(MODEL_COLORS.get(m, SITE_FG))
    ax.tick_params(axis="y", which="major", length=0)

    for spine in ax.spines.values():
        spine.set_color(SITE_FG_MUTED)
        spine.set_alpha(0.3)
        spine.set_linewidth(0.8)

    ax.set_title("Calibration gap · empirical accuracy − claimed confidence",
                 fontsize=13, fontweight="700", color=SITE_FG, pad=28, loc="left")
    fig.text(0.02, 0.90,
             "Negative = overconfident · zero = calibrated · positive = underconfident",
             ha="left", fontsize=9, style="italic", color=SITE_FG_MUTED)

    cbar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.012)
    cbar.set_ticks([-0.25, -0.125, 0.0, 0.125, 0.25])
    cbar.ax.tick_params(labelsize=8, colors=SITE_FG_MUTED)
    if cbar.outline is not None:
        cbar.outline.set_edgecolor(SITE_FG_MUTED)
        cbar.outline.set_alpha(0.3)

    fig.tight_layout(rect=(0, 0.03, 1, 0.92))
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=SITE_BG)
    plt.close(fig)


def make_ece_figure(per_model: dict, paths: list[Path]) -> None:
    """Horizontal ECE leaderboard with green/yellow/red calibration zones.

    Tier 2A.6 promotion: this becomes the PRIMARY §5 calibration chart on the
    site (smallmultiples reliability diagram drops to secondary detail view).
    Sorted ascending by verbalized ECE; bands flag well/mildly/severely
    miscalibrated regions.
    """
    from site_palette import COLOR_GOOD, COLOR_BAD

    items = sorted(per_model.items(), key=lambda kv: kv[1]["ece"])
    models = [m for m, _ in items]
    eces = [info["ece"] for _, info in items]
    colors = [MODEL_COLORS.get(m, SITE_FG_MUTED) for m in models]

    fig, ax = plt.subplots(figsize=(11, 4), dpi=150, facecolor=SITE_BG)
    ax.set_facecolor(SITE_BG)

    x_max = max(max(eces) * 1.18, 0.22)

    # Calibration-quality zones — drawn first, behind bars.
    zones = [
        (0.00, 0.05, COLOR_GOOD,    "well-calibrated"),
        (0.05, 0.10, "#fbbf24",      "mildly miscalibrated"),
        (0.10, x_max, COLOR_BAD,     "severely miscalibrated"),
    ]
    for lo, hi, color, _label in zones:
        ax.axvspan(lo, min(hi, x_max), color=color, alpha=0.08, zorder=0)
    # Zone labels along the top of the plot area.
    for lo, hi, color, label in zones:
        mid = (lo + min(hi, x_max)) / 2
        ax.text(mid, len(models) - 0.35, label,
                ha="center", va="center", fontsize=8.5,
                color=color, fontweight="700", alpha=0.85)

    y_pos = np.arange(len(models))
    ax.barh(y_pos, eces, color=colors, edgecolor=SITE_BG, linewidth=0.7,
            height=0.62, zorder=2)
    for i, e in enumerate(eces):
        ax.text(e + x_max * 0.012, y_pos[i], f"{e:.3f}",
                va="center", ha="left",
                color=SITE_FG, fontsize=11, fontweight="700")

    ax.set_yticks(y_pos)
    ax.set_yticklabels([m.title() for m in models], fontsize=11, fontweight="700")
    for tick, m in zip(ax.get_yticklabels(), models):
        tick.set_color(MODEL_COLORS.get(m, SITE_FG))
    ax.invert_yaxis()  # rank #1 at top

    ax.set_xlabel("Expected Calibration Error (verbalized · lower = better)",
                  fontsize=10, color=SITE_FG_MUTED)
    ax.set_xlim(0, x_max)
    ax.set_title("Calibration · ECE leaderboard",
                 fontsize=13, color=SITE_FG, pad=12, fontweight="700", loc="left")
    ax.tick_params(colors=SITE_FG_MUTED, labelsize=10)
    dim_remaining_spines(ax)
    ax.grid(True, axis="x", alpha=0.06, color="#ffffff")
    ax.set_axisbelow(True)

    plt.tight_layout()
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=SITE_BG)
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
    # Tier 2A.6: smallmultiples is the §5 canonical view on the website.
    # The single-panel `calibration_reliability.png` is poster-only — emit
    # only to report_materials/, not to public/v2 (orphan was archived).
    make_reliability_figure(per_model, [FIG_RELIABILITY])
    make_reliability_smallmultiples(per_model, [FIG_RELIABILITY_SM, FIG_RELIABILITY_SM_WEB])
    make_ece_figure(per_model, [FIG_ECE, FIG_ECE_WEB])

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
    print(f"Saved: {FIG_RELIABILITY_WEB}")
    print(f"Saved: {FIG_ECE}")

    # Auto-heal: this script overwrites calibration.json with per-bucket
    # ECE/accuracy only — recompute_downstream.py adds the derived fields
    # (accuracy_calibration_correlation, formatting_failure_rate_per_model)
    # that the website + backend depend on. Always re-run after the canonical
    # write so the deployed copy never goes stale.
    print("[INFO] calibration.json overwritten — chaining recompute_downstream.py to restore derived fields")
    import subprocess
    subprocess.run(["python", "scripts/recompute_downstream.py"], check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
