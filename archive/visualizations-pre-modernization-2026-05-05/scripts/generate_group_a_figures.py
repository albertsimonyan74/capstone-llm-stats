"""Group A figures for poster — A1..A6.

Reads existing artifacts (no model API calls). Writes 6 PNGs at 300 DPI,
transparent background, to report_materials/figures/.

Usage:
    python scripts/generate_group_a_figures.py
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from baseline.utils_task_id import task_type_from_id  # noqa: E402

plt.rcParams["font.size"] = 11

FIG_DIR = ROOT / "report_materials" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Data paths
RUNS_V1 = ROOT / "experiments" / "results_v1" / "runs.jsonl"
PERT_RUNS = ROOT / "experiments" / "results_v2" / "perturbation_runs.jsonl"
TAXONOMY = ROOT / "experiments" / "results_v2" / "error_taxonomy_v2.json"
ROBUST = ROOT / "experiments" / "results_v2" / "robustness_v2.json"
CALIB = ROOT / "experiments" / "results_v2" / "calibration.json"
BOOTSTRAP = ROOT / "experiments" / "results_v2" / "bootstrap_ci.json"
JUDGE_DIM_MEANS = ROOT / "experiments" / "results_v2" / "judge_dimension_means.json"

MODEL_COLORS = {
    "claude":   "#00CED1",
    "chatgpt":  "#7FFFD4",
    "gemini":   "#FF6B6B",
    "deepseek": "#4A90D9",
    "mistral":  "#A78BFA",
}
MODEL_LABEL = {
    "claude":   "Claude",
    "chatgpt":  "ChatGPT",
    "gemini":   "Gemini",
    "deepseek": "DeepSeek",
    "mistral":  "Mistral",
}
MODELS = ["claude", "chatgpt", "gemini", "deepseek", "mistral"]

# 4 populated L1 buckets. HALLUCINATION omitted — 0/143 across all models
# (canonical experiments/results_v2/error_taxonomy_v2.json). See Limitations L1
# for methodological framing on the empty bucket.
L1_COLORS = {
    "ASSUMPTION_VIOLATION": "#fbbf24",  # amber/gold
    "MATHEMATICAL_ERROR":   "#f87171",  # coral red
    "FORMATTING_FAILURE":   "#94a3b8",  # slate
    "CONCEPTUAL_ERROR":     "#a78bfa",  # lavender
}
L1_ORDER = list(L1_COLORS.keys())

# Site theme (matches capstone-website/frontend/src/App.css :root vars).
SITE_BG = "#0A0F1E"        # bg-primary
SITE_FG = "#E8F4F8"        # text-primary
SITE_FG_MUTED = "#8BAFC0"  # text-secondary
SITE_GRID_ALPHA = 0.08

PERT_SUFFIX_RE = re.compile(r"_(rephrase|numerical|semantic)(?:_v\d+)?$")

# ─────────────────────────────────────────────────────────────────────────────
# Loaders
# ─────────────────────────────────────────────────────────────────────────────

def load_jsonl(path: Path):
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def load_base_runs():
    """Yield only base runs (no perturbation suffix), no errored records."""
    for r in load_jsonl(RUNS_V1):
        tid = r.get("task_id", "")
        if PERT_SUFFIX_RE.search(tid):
            continue
        if r.get("error"):
            continue
        if r.get("final_score") is None:
            continue
        yield r


def load_taxonomy():
    return json.loads(TAXONOMY.read_text())


def load_robustness():
    return json.loads(ROBUST.read_text())


def load_calibration():
    return json.loads(CALIB.read_text())


def load_bootstrap():
    return json.loads(BOOTSTRAP.read_text())


def load_judge_dim_means():
    return json.loads(JUDGE_DIM_MEANS.read_text())


# ─────────────────────────────────────────────────────────────────────────────
# Category mapping (A2)
# ─────────────────────────────────────────────────────────────────────────────

def category_of(task_type: str) -> str:
    t = task_type
    if any(k in t for k in ["MCMC", "METROPOLIS", "GIBBS", "HMC", "RJMCMC", "STATIONARY", "MH"]):
        return "MCMC"
    if any(k in t for k in ["MLE", "BIAS_VAR", "FISHER", "CRAMER", "SUFFICIENCY", "RC_BOUND", "UNIFORM"]):
        return "MLE_FREQ"
    if any(k in t for k in ["BAYES", "BETA", "DIRICHLET", "CONJUGATE", "POSTERIOR", "PRIOR",
                              "BINOM_FLAT", "GAMMA_POISSON", "NORMAL_GAMMA", "JEFFREYS",
                              "HPD", "CI_CREDIBLE", "PPC"]):
        return "BAYESIAN_CORE"
    if any(k in t for k in ["REGRESSION", "GLM", "LOGISTIC"]):
        return "REGRESSION"
    if any(k in t for k in ["CAUSAL", "PREDICTION", "MARKOV", "HMM"]):
        return "CAUSAL_PRED"
    return "ADVANCED"


CATEGORY_ORDER = ["BAYESIAN_CORE", "MLE_FREQ", "MCMC", "REGRESSION", "CAUSAL_PRED", "ADVANCED"]
CATEGORY_LABEL = {
    "BAYESIAN_CORE": "Bayesian Core",
    "MLE_FREQ":      "MLE / Freq.",
    "MCMC":          "MCMC",
    "REGRESSION":    "Regression",
    "CAUSAL_PRED":   "Causal / Pred.",
    "ADVANCED":      "Advanced",
}


def bootstrap_ci_mean(values: list[float], B: int = 1000, seed: int = 42, alpha: float = 0.05):
    if len(values) == 0:
        return 0.0, 0.0, 0.0
    rng = np.random.default_rng(seed)
    arr = np.asarray(values, dtype=float)
    n = len(arr)
    means = np.empty(B)
    for b in range(B):
        idx = rng.integers(0, n, size=n)
        means[b] = arr[idx].mean()
    lo = float(np.percentile(means, 100 * alpha / 2))
    hi = float(np.percentile(means, 100 * (1 - alpha / 2)))
    return float(arr.mean()), lo, hi


# ─────────────────────────────────────────────────────────────────────────────
# A1 — Per-task-type failure breakdown by L1 taxonomy
# ─────────────────────────────────────────────────────────────────────────────

def figure_a1():
    out = FIG_DIR / "a1_failure_by_tasktype.png"

    base_runs = list(load_base_runs())
    runs_by_tt: dict[str, int] = defaultdict(int)
    for r in base_runs:
        runs_by_tt[task_type_from_id(r["task_id"])] += 1

    tax = load_taxonomy()
    counts: dict[str, Counter] = defaultdict(Counter)
    for rec in tax["records"]:
        tt = rec.get("task_type") or task_type_from_id(rec["task_id"])
        l1 = rec.get("l1")
        if l1:
            counts[tt][l1] += 1

    task_types = sorted(counts.keys(), key=lambda tt: -sum(counts[tt].values()))
    totals = [sum(counts[tt].values()) for tt in task_types]

    fig, ax = plt.subplots(figsize=(14, 7), dpi=300, facecolor=SITE_BG)
    ax.set_facecolor(SITE_BG)

    x = np.arange(len(task_types))
    bottoms = np.zeros(len(task_types))
    for l1 in L1_ORDER:
        heights = np.array([counts[tt].get(l1, 0) for tt in task_types], dtype=float)
        ax.bar(x, heights, bottom=bottoms, color=L1_COLORS[l1],
               edgecolor=SITE_BG, linewidth=1.5,
               label=l1.replace("_", " ").title())
        bottoms += heights

    # Failure RATE labels above each bar (failures / runs), site-light text.
    for i, tt in enumerate(task_types):
        n_runs = runs_by_tt.get(tt, 0)
        rate = totals[i] / n_runs if n_runs else 0.0
        ax.text(x[i], totals[i] + 0.4,
                f"{rate*100:.0f}%",
                ha="center", va="bottom",
                fontsize=8.5, color=SITE_FG, fontweight="bold")

    # X-axis: task types in muted monospace.
    ax.set_xticks(x)
    ax.set_xticklabels(task_types, rotation=45, ha="right",
                       fontsize=8.5, color=SITE_FG_MUTED, family="monospace")

    # Y-axis muted.
    ax.set_ylabel("Failure count (stacked)", fontsize=11, color=SITE_FG_MUTED)
    ax.set_xlabel("Task type (sorted by total failures)",
                  fontsize=10, color=SITE_FG_MUTED)
    ax.tick_params(axis="y", colors=SITE_FG_MUTED, labelsize=9)

    # Clean spines.
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(SITE_FG_MUTED)
        ax.spines[side].set_alpha(0.3)

    ax.grid(axis="y", alpha=SITE_GRID_ALPHA, linestyle="-", linewidth=0.5,
            color=SITE_FG)
    ax.set_axisbelow(True)
    ax.set_ylim(0, max(totals) * 1.20)

    ax.set_title("Failure rate by task type · sorted by total failures",
                 fontsize=13, fontweight="bold", color=SITE_FG,
                 pad=18, loc="left")

    legend = ax.legend(loc="upper right", title="L1 failure bucket",
                       frameon=False, fontsize=10, labelcolor=SITE_FG_MUTED)
    legend.get_title().set_color(SITE_FG_MUTED)

    ax.text(0.005, 0.96,
            "% labels show failure RATE per task_type (failures / runs).",
            transform=ax.transAxes, fontsize=9, color=SITE_FG_MUTED, style="italic")

    fig.tight_layout()
    fig.savefig(out, dpi=300, facecolor=SITE_BG, bbox_inches="tight")
    plt.close(fig)

    top3 = task_types[:3]
    return out, f"top-3 hardest task_types: {', '.join(top3)}; ASSUMPTION_VIOLATION dominant in BAYES_REG / REGRESSION clusters"


# ─────────────────────────────────────────────────────────────────────────────
# A2 — RQ2 accuracy by task category
# ─────────────────────────────────────────────────────────────────────────────

def figure_a2():
    out = FIG_DIR / "a2_accuracy_by_category.png"

    base_runs = list(load_base_runs())

    by_model_cat: dict[tuple[str, str], list[float]] = defaultdict(list)
    overall: list[float] = []
    for r in base_runs:
        m = r.get("model_family")
        cat = category_of(task_type_from_id(r["task_id"]))
        sc = float(r["final_score"])
        if m in MODEL_COLORS:
            by_model_cat[(m, cat)].append(sc)
            overall.append(sc)

    overall_mean = float(np.mean(overall)) if overall else 0.0

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    fig.patch.set_alpha(0)

    n_cat = len(CATEGORY_ORDER)
    n_mod = len(MODELS)
    width = 0.85 / n_mod
    x = np.arange(n_cat)

    for i, m in enumerate(MODELS):
        means, los, his = [], [], []
        for cat in CATEGORY_ORDER:
            vals = by_model_cat.get((m, cat), [])
            mean, lo, hi = bootstrap_ci_mean(vals, B=1000, seed=42)
            means.append(mean)
            los.append(mean - lo)
            his.append(hi - mean)
        offset = (i - (n_mod - 1) / 2) * width
        ax.bar(x + offset, means, width=width,
               color=MODEL_COLORS[m], edgecolor="white", linewidth=0.5,
               label=MODEL_LABEL[m],
               yerr=[los, his], ecolor="#333", capsize=2)

    ax.axhline(overall_mean, color="#444", lw=1.2, ls="--", alpha=0.7,
               label=f"Overall mean = {overall_mean:.3f}")

    ax.set_xticks(x)
    ax.set_xticklabels([CATEGORY_LABEL[c] for c in CATEGORY_ORDER], fontsize=10)
    ax.set_ylabel("Accuracy (final_score)")
    ax.set_xlabel("Task category")
    ax.set_ylim(0, 1.0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.legend(loc="upper right", frameon=False, ncol=2, fontsize=9)

    fig.tight_layout()
    fig.savefig(out, dpi=300, transparent=True, bbox_inches="tight")
    plt.close(fig)

    cat_means = {cat: np.mean([by_model_cat[(m, cat)] for m in MODELS for _ in [0]
                               if by_model_cat[(m, cat)]] or [0]) for cat in CATEGORY_ORDER}
    best = max(cat_means, key=cat_means.get)
    worst = min(cat_means, key=cat_means.get)
    return out, f"easiest category: {CATEGORY_LABEL[best]}; hardest: {CATEGORY_LABEL[worst]}"


# ─────────────────────────────────────────────────────────────────────────────
# A3 — RQ3 failure-rate heatmap
# ─────────────────────────────────────────────────────────────────────────────

def figure_a3():
    """Failure heatmap — portrait (task_types as rows, models as columns).

    Site-palette dark theme: figure background SITE_BG (#0f1118), custom
    site-harmonized colormap (dark→coral gradient), cell labels in decimal
    format (0.30, 0.66 — not raw integers). Category bands on left with
    bracket connectors, model labels at top color-coded, significance-
    thresholded labels (cells with failure rate ≥0.15 labeled).
    """
    import matplotlib.colors as mcolors

    out = FIG_DIR / "a3_failure_heatmap.png"

    SITE_BG = "#0f1118"
    SITE_FG = "#e2e8f0"
    SITE_FG_MUTED = "#94a3b8"

    # Site-harmonized colormap: dark (blends with bg) → coral-red
    custom_cmap = mcolors.LinearSegmentedColormap.from_list(
        "site_failure",
        [
            (0.00, "#1a1f2e"),  # near site bg — no failure
            (0.15, "#2a1f2e"),  # subtle dark coral tint
            (0.35, "#7c2d3d"),  # muted coral
            (0.60, "#dc2626"),  # red
            (1.00, "#ef4444"),  # bright coral-red
        ],
    )

    base_runs = list(load_base_runs())
    cell_scores: dict[tuple[str, str], list[float]] = defaultdict(list)
    for r in base_runs:
        m = r.get("model_family")
        if m not in MODEL_COLORS:
            continue
        tt = task_type_from_id(r["task_id"])
        cell_scores[(m, tt)].append(float(r["final_score"]))

    task_types_all = sorted({tt for _, tt in cell_scores.keys()})

    # Cluster rows by category (CATEGORY_ORDER), alphabetical inside.
    grouped: dict[str, list[str]] = {c: [] for c in CATEGORY_ORDER}
    for tt in task_types_all:
        grouped.setdefault(category_of(tt), []).append(tt)
    ordered_types: list[str] = []
    cat_spans: list[tuple[str, int, int]] = []
    row = 0
    for cat in CATEGORY_ORDER:
        items = grouped.get(cat, [])
        if not items:
            continue
        cat_spans.append((cat, row, row + len(items) - 1))
        ordered_types.extend(items)
        row += len(items)

    # Matrix shape: (n_task_types, n_models) — failure rate = 1 − mean(final_score)
    M = np.full((len(ordered_types), len(MODELS)), np.nan)
    for i, tt in enumerate(ordered_types):
        for j, m in enumerate(MODELS):
            scores = cell_scores.get((m, tt), [])
            if scores:
                M[i, j] = 1.0 - float(np.mean(scores))

    fig, ax = plt.subplots(figsize=(8, 14), dpi=150, facecolor=SITE_BG)
    ax.set_facecolor(SITE_BG)

    im = ax.imshow(M, cmap=custom_cmap, vmin=0.0, vmax=1.0, aspect="auto", origin="upper")

    # Models on TOP x-axis, color-coded
    ax.set_xticks(range(len(MODELS)))
    ax.set_xticklabels([MODEL_LABEL[m] for m in MODELS], fontsize=11, fontweight="bold")
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position("top")
    ax.tick_params(axis="x", which="major", pad=6, colors=SITE_FG)
    for tick, m in zip(ax.get_xticklabels(), MODELS):
        tick.set_color(MODEL_COLORS.get(m, SITE_FG))

    # Task types on Y-axis, monospace
    ax.set_yticks(range(len(ordered_types)))
    ax.set_yticklabels(ordered_types, fontsize=8.5, family="monospace",
                       color=SITE_FG_MUTED)
    ax.tick_params(axis="y", colors=SITE_FG_MUTED)

    # Significance-thresholded labels — DECIMAL format (0.30, 0.66, etc.)
    SIG_THRESHOLD = 0.15
    for i in range(len(ordered_types)):
        for j in range(len(MODELS)):
            v = M[i, j]
            if np.isnan(v):
                ax.text(j, i, "—", ha="center", va="center", fontsize=7,
                        color=SITE_FG_MUTED)
            elif v >= SIG_THRESHOLD:
                txt_color = "#fff" if v >= 0.45 else SITE_FG
                ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                        fontsize=7.5, color=txt_color, fontweight="600")

    # Horizontal dividers between category bands
    for _, _, end_row in cat_spans[:-1]:
        ax.axhline(end_row + 0.5, color=SITE_FG_MUTED, linewidth=0.8, alpha=0.3)

    # Category labels in left margin: bracket + label (mirrors robustness_heatmap)
    n_models = len(MODELS)
    bracket_x = -1.95
    label_horiz_x = -3.55
    label_vert_x = -3.30
    for cat, s, e in cat_spans:
        span = e - s + 1
        mid = (s + e) / 2
        if span <= 2:
            ax.text(label_horiz_x, mid, CATEGORY_LABEL.get(cat, cat),
                    ha="left", va="center", rotation=0,
                    fontsize=10, fontweight="bold", color=SITE_FG,
                    clip_on=False)
        else:
            ax.text(label_vert_x, mid, CATEGORY_LABEL.get(cat, cat),
                    ha="center", va="center", rotation=90,
                    fontsize=11, fontweight="bold", color=SITE_FG,
                    clip_on=False)
        ax.plot([bracket_x, bracket_x], [s - 0.4, e + 0.4],
                color=SITE_FG_MUTED, linewidth=1.0, alpha=0.5, clip_on=False)
        for y_cap in (s - 0.4, e + 0.4):
            ax.plot([bracket_x, bracket_x + 0.20], [y_cap, y_cap],
                    color=SITE_FG_MUTED, linewidth=1.0, alpha=0.5, clip_on=False)

    ax.set_xlim(-4.0, n_models - 0.5)

    # Spines site-coordinated
    for spine in ax.spines.values():
        spine.set_color(SITE_FG_MUTED)
        spine.set_alpha(0.3)
        spine.set_linewidth(0.8)

    ax.set_title(
        "Failure Heatmap · per-model failure rate by task type",
        fontsize=12, fontweight="bold", pad=24, color=SITE_FG,
    )
    cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
    cbar.set_label("Failure rate (1 − mean(final_score))",
                   fontsize=9, color=SITE_FG_MUTED, rotation=270, labelpad=22)
    cbar.set_ticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    cbar.ax.tick_params(labelsize=8, colors=SITE_FG_MUTED)
    cbar.outline.set_edgecolor(SITE_FG_MUTED)
    cbar.outline.set_alpha(0.3)

    # Footnote: significance threshold annotation
    fig.text(0.5, 0.01, f"Labels shown for cells ≥{SIG_THRESHOLD:.2f}",
             ha="center", va="bottom", fontsize=8, color=SITE_FG_MUTED,
             style="italic")

    ax.set_xticks(np.arange(-.5, len(MODELS), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(ordered_types), 1), minor=True)
    ax.grid(which="minor", color=SITE_FG_MUTED, linewidth=0.3, alpha=0.15)
    ax.tick_params(which="minor", length=0)
    ax.tick_params(which="major", length=0)

    fig.savefig(out, dpi=150, facecolor=SITE_BG, bbox_inches="tight")
    plt.close(fig)

    fail_rate_by_tt = {
        tt: float(np.nanmean(M[i])) for i, tt in enumerate(ordered_types)
    }
    sorted_hard = sorted(fail_rate_by_tt, key=lambda tt: -fail_rate_by_tt[tt])
    hardest = sorted_hard[0]
    return out, f"hardest task_type: {hardest} (mean failure {fail_rate_by_tt[hardest]:.2f}); top-3 hardest: {', '.join(sorted_hard[:3])}"


# ─────────────────────────────────────────────────────────────────────────────
# A4 — RQ4 robustness Δ by perturbation type
# ─────────────────────────────────────────────────────────────────────────────

def figure_a4():
    out = FIG_DIR / "a4_robustness_by_perttype.png"

    rob = load_robustness()
    pert_types = ["rephrase", "numerical", "semantic"]
    pert_label = {"rephrase": "Rephrase", "numerical": "Numerical", "semantic": "Semantic"}

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    fig.patch.set_alpha(0)

    n_grp = len(pert_types)
    n_mod = len(MODELS)
    width = 0.85 / n_mod
    x = np.arange(n_grp)

    deltas: dict[tuple[str, str], float] = {}
    for m in MODELS:
        per = rob["per_model"][m]["per_perturbation_type"]
        for pt in pert_types:
            deltas[(m, pt)] = per[pt]["delta"]

    for i, m in enumerate(MODELS):
        ys = [deltas[(m, pt)] for pt in pert_types]
        offset = (i - (n_mod - 1) / 2) * width
        ax.bar(x + offset, ys, width=width,
               color=MODEL_COLORS[m], edgecolor="white", linewidth=0.5,
               label=MODEL_LABEL[m])

    ax.axhline(0.0, color="#222", lw=1.0, ls="--", alpha=0.7)

    max_key = max(deltas, key=lambda k: deltas[k])
    mi = MODELS.index(max_key[0])
    pi = pert_types.index(max_key[1])
    offset = (mi - (n_mod - 1) / 2) * width
    ax.annotate(
        f"largest fragility:\n{MODEL_LABEL[max_key[0]]}, {pert_label[max_key[1]]} ({deltas[max_key]:+.3f})",
        xy=(x[pi] + offset, deltas[max_key]),
        xytext=(x[pi] + offset + 0.18, deltas[max_key] + 0.008),
        fontsize=9, ha="left", color="#222", fontweight="bold",
        arrowprops=dict(arrowstyle="->", color="#444", lw=0.8),
    )

    ax.set_xticks(x)
    ax.set_xticklabels([pert_label[p] for p in pert_types])
    ax.set_ylabel("Δ score (base − perturbation)")
    ax.set_xlabel("Perturbation type")
    ax.set_ylim(-0.04, max(deltas.values()) * 1.85)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.legend(loc="lower left", frameon=False, ncol=5, fontsize=9)

    fig.tight_layout()
    fig.savefig(out, dpi=300, transparent=True, bbox_inches="tight")
    plt.close(fig)

    biggest_drop = max(deltas, key=lambda k: deltas[k])
    return out, f"largest fragility: {MODEL_LABEL[biggest_drop[0]]} on {pert_label[biggest_drop[1]]} (Δ={deltas[biggest_drop]:+.4f})"


# ─────────────────────────────────────────────────────────────────────────────
# A5 — RQ5 calibration reliability diagram
# ─────────────────────────────────────────────────────────────────────────────

def figure_a5():
    out = FIG_DIR / "a5_calibration_reliability.png"

    calib = load_calibration()

    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    fig.patch.set_alpha(0)

    ax.plot([0, 1], [0, 1], color="#444", lw=1.2, ls="--", alpha=0.6,
            label="perfect calibration")

    MIN_N = 3
    for m in MODELS:
        info = calib[m]
        xs, ys = [], []
        for b in ["low", "medium", "high"]:
            d = info["per_bucket"][b]
            if d["n"] < MIN_N or d["mean_accuracy"] is None:
                continue
            xs.append(d["claimed_confidence"])
            ys.append(d["mean_accuracy"])
        if not xs:
            continue
        color = MODEL_COLORS[m]
        ax.plot(xs, ys, color=color, lw=2.0, marker="o", markersize=10,
                markeredgecolor="white", markeredgewidth=1.0,
                label=f"{MODEL_LABEL[m]} (ECE={info['ece']:.3f})")
        ax.annotate(
            f"{MODEL_LABEL[m]}",
            xy=(xs[-1], ys[-1]),
            xytext=(xs[-1] + 0.012, ys[-1] + 0.012),
            fontsize=8.5, color=color, fontweight="bold",
        )

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Claimed confidence (bucket midpoint)")
    ax.set_ylabel("Empirical accuracy")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, alpha=0.25)
    ax.legend(loc="upper left", frameon=False, fontsize=9)

    fig.text(0.5, 0.02,
             "High confidence bucket (claimed ≥ 0.9) empty for all models — keyword extractor never triggered. "
             "Buckets with n < 3 hidden. ECE is a 3-bucket weighted MAE.",
             ha="center", fontsize=8.5, style="italic", color="#666", wrap=True)

    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(out, dpi=300, transparent=True, bbox_inches="tight")
    plt.close(fig)

    best_model = min(MODELS, key=lambda m: calib[m]["ece"])
    return out, f"best calibrated: {MODEL_LABEL[best_model]} (ECE={calib[best_model]['ece']:.3f}); high-confidence bucket empty for all"


# ─────────────────────────────────────────────────────────────────────────────
# A6 — Aggregate ranking dot plot
# ─────────────────────────────────────────────────────────────────────────────

def _bracket_pairs(separability: list, ranked_models: list[str]) -> list[tuple[int, int]]:
    """From bootstrap separability triples, return list of (i, j) index pairs in ranked order
    that are 'not_separable' and adjacent in the rank order."""
    ns = {tuple(sorted([a, b])) for (a, b, verdict) in separability if verdict == "not_separable"}
    pairs = []
    for i in range(len(ranked_models) - 1):
        a, b = ranked_models[i], ranked_models[i + 1]
        if tuple(sorted([a, b])) in ns:
            pairs.append((i, i + 1))
    return pairs


def _draw_bracket_horizontal(ax, x0, x1, y, color="#666"):
    """Bracket below a horizontal axis; spans x0..x1 at y, tips downward."""
    tip = (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.04
    ax.plot([x0, x1], [y, y], color=color, lw=1.2, solid_capstyle="round")
    ax.plot([x0, x0], [y, y - tip], color=color, lw=1.2)
    ax.plot([x1, x1], [y, y - tip], color=color, lw=1.2)


def figure_a6():
    out = FIG_DIR / "a6_aggregate_ranking.png"

    bootstrap = load_bootstrap()
    calib = load_calibration()
    judge_means = load_judge_dim_means()

    rank_order = sorted(MODELS, key=lambda m: -bootstrap["accuracy"][m]["mean"])
    label_map = [MODEL_LABEL[m] for m in rank_order]

    fig, axes = plt.subplots(4, 1, figsize=(8, 7), dpi=300, sharey=False)
    fig.patch.set_alpha(0)

    panels = [
        ("Accuracy (mean)", "accuracy_mean"),
        ("Robustness Δ (base − pert)", "robustness_delta"),
        ("Calibration (ECE)", "ece"),
        ("Reasoning Quality (judge mean)", "reasoning_quality"),
    ]

    for ax, (title, key) in zip(axes, panels):
        ys = list(range(len(rank_order)))
        xs, los_minus, his_plus = [], [], []
        for m in rank_order:
            if key == "accuracy_mean":
                d = bootstrap["accuracy"][m]
                xs.append(d["mean"])
                los_minus.append(d["mean"] - d["ci_lower"])
                his_plus.append(d["ci_upper"] - d["mean"])
            elif key == "robustness_delta":
                d = bootstrap["robustness"][m]
                xs.append(d["mean_delta"])
                los_minus.append(d["mean_delta"] - d["ci_lower"])
                his_plus.append(d["ci_upper"] - d["mean_delta"])
            elif key == "ece":
                xs.append(calib[m]["ece"])
                los_minus.append(0); his_plus.append(0)
            elif key == "reasoning_quality":
                xs.append(judge_means["base"][m]["reasoning_quality"]["mean"])
                los_minus.append(0); his_plus.append(0)

        for y, x, lo, hi, m in zip(ys, xs, los_minus, his_plus, rank_order):
            ax.errorbar(x, y, xerr=[[lo], [hi]] if (lo or hi) else None,
                        fmt="o", markersize=10, color=MODEL_COLORS[m],
                        markeredgecolor="white", markeredgewidth=1.0,
                        ecolor="#444", elinewidth=1.0, capsize=3)

        ax.set_yticks(ys)
        ax.set_yticklabels(label_map, fontsize=10)
        for tick, m in zip(ax.get_yticklabels(), rank_order):
            tick.set_color(MODEL_COLORS[m])
            tick.set_fontweight("bold")
        ax.invert_yaxis()
        ax.set_xlabel(title)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="x", linestyle="--", alpha=0.3)

        if key == "robustness_delta":
            ax.axvline(0.0, color="#222", lw=0.8, ls="--", alpha=0.6)

        if key in ("accuracy_mean", "robustness_delta"):
            sep_key = "accuracy" if key == "accuracy_mean" else "robustness"
            sep = bootstrap["separability"][sep_key]
            ns_pairs = _bracket_pairs(sep, rank_order)
            xmin, xmax = ax.get_xlim()
            x_anchor = xmin - (xmax - xmin) * 0.06
            for (i, j) in ns_pairs:
                ax.annotate(
                    "",
                    xy=(x_anchor, j), xytext=(x_anchor, i),
                    arrowprops=dict(arrowstyle="-", color="#888", lw=1.4),
                    annotation_clip=False,
                )
                ax.text(x_anchor - (xmax - xmin) * 0.02, (i + j) / 2,
                        "n.s.", ha="right", va="center", fontsize=8.5,
                        color="#888", fontweight="bold")

    fig.text(0.5, 0.005,
             "Models sorted by Accuracy. n.s. = adjacent ranks not statistically separable (95% bootstrap CI, B=10,000).",
             ha="center", fontsize=8.5, style="italic", color="#666")

    fig.tight_layout(rect=(0, 0.025, 1, 1))
    fig.savefig(out, dpi=300, transparent=True, bbox_inches="tight")
    plt.close(fig)

    return out, f"top by accuracy: {MODEL_LABEL[rank_order[0]]}; rankings disagree across panels — see arrows on three_rankings figure for visualization"


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    findings = []
    for fn in (figure_a1, figure_a2, figure_a3, figure_a4, figure_a5, figure_a6):
        path, finding = fn()
        size = path.stat().st_size
        findings.append((path, size, finding))
        print(f"  wrote {path}  ({size:,} bytes)")

    print("\n=== KEY FINDINGS ===")
    for path, size, finding in findings:
        print(f"  {path.name}: {finding}")


if __name__ == "__main__":
    main()
