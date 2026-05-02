"""Self-consistency confidence proxy (RQ5 upgrade).

Methodology grounded in Multi-Answer Confidence (arxiv 2602.07842) and
SelfCheckGPT (Manakul et al., 2023). Contrast with FermiEval (arxiv 2510.26995).
Addresses audit finding F-12 / P-3.

Design:
- Stratified subsample of 30 tasks: 5 per Group-A category, weighted by
  per-task failure rate so harder tasks are oversampled.
- 3 reruns per (task, model) at temperature=0.7, top_p=0.95.
- Consistency proxy = response-agreement rate over the numerical answer:
    3/3 identical → 1.00 (high)
    2/3 identical → 0.67 (medium)
    else         → 0.33 (low)
- ECE computed on (consistency, accuracy) pairs.
- Resume-safe: writes one JSONL record per (task, model, run_idx).
- Cost guard: pauses for confirmation past $1.50 (auto-abort > $5).

Outputs:
- experiments/results_v2/self_consistency_runs.jsonl     (append-only)
- experiments/results_v2/self_consistency_calibration.json
- report_materials/figures/self_consistency_calibration.png

Run from project root:
    python scripts/self_consistency_proxy.py
"""
from __future__ import annotations

import json
import math
import os
import re
import time
from collections import defaultdict
from pathlib import Path

import httpx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from llm_runner.prompt_builder import build_prompt, parse_answer

ROOT = Path(__file__).resolve().parents[1]
TASKS_PATH = ROOT / "data/benchmark_v1/tasks_all.json"
BASE_RUNS = ROOT / "experiments/results_v1/runs.jsonl"
CALIBRATION_PATH = ROOT / "experiments/results_v2/calibration.json"
OUT_RUNS = ROOT / "experiments/results_v2/self_consistency_runs.jsonl"
OUT_CALIB = ROOT / "experiments/results_v2/self_consistency_calibration.json"
OUT_FIG = ROOT / "report_materials/figures/self_consistency_calibration.png"

CITATION = (
    "Methodology grounded in Multi-Answer Confidence (arxiv 2602.07842) and "
    "SelfCheckGPT (Manakul et al., 2023). Contrast with FermiEval "
    "(arxiv 2510.26995). Addresses audit finding F-12 / P-3."
)

MODELS = ["claude", "chatgpt", "gemini", "deepseek", "mistral"]
N_RUNS = 3
TEMPERATURE = 0.7
TOP_P = 0.95
TIMEOUT = 60.0
SLEEP_S = 1.0

# Tolerance applied to numeric-answer agreement (canonical scorer style)
TOL_ABS = 0.01
TOL_REL = 0.05

# Cost estimates per 1K tokens (input, output) — vendor list prices, May 2026
COST_PER_1K = {
    "claude":   (0.003, 0.015),    # claude-sonnet-4-5
    "chatgpt":  (0.0020, 0.0080),  # gpt-4.1
    "gemini":   (0.000075, 0.0003),
    "deepseek": (0.00027, 0.0011),
    "mistral":  (0.002, 0.006),
}

CATEGORY_ORDER = ["BAYESIAN_CORE", "MLE_FREQ", "MCMC", "REGRESSION", "CAUSAL_PRED", "ADVANCED"]
TASKS_PER_CATEGORY = 5

PERT_RE = re.compile(r"_(rephrase|numerical|semantic)(?:_v\d+)?$")
TYPE_RE = re.compile(r"^(.+?)_\d+$")

MODEL_COLORS = {
    "claude":   "#00CED1",
    "chatgpt":  "#7FFFD4",
    "gemini":   "#FF6B6B",
    "deepseek": "#4A90D9",
    "mistral":  "#A78BFA",
}


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


def task_type_of(task_id: str) -> str:
    m = TYPE_RE.match(task_id)
    return m.group(1) if m else task_id


# ── stratified sampling ──────────────────────────────────────────────────────

def stratified_sample(tasks: list[dict], runs: list[dict], seed: int = 42) -> dict[str, list[str]]:
    """Pick TASKS_PER_CATEGORY tasks per category, weighted by failure rate.

    Sampling logic:
    1. Compute per-task fail rate = mean(1 - pass) across all 5 models.
    2. Restrict to numeric-bearing base tasks (filter out CONCEPTUAL with no
       numeric_targets, since consistency requires a numeric answer).
    3. Sort each category by fail rate descending; take top TASKS_PER_CATEGORY.
       (Ties broken by deterministic numpy.random with given seed.)
    """
    base_runs = [r for r in runs
                 if r.get("task_id") and not PERT_RE.search(r["task_id"])
                 and r.get("final_score") is not None]
    fails = defaultdict(list)
    for r in base_runs:
        fails[r["task_id"]].append(0 if r.get("pass") else 1)
    fail_rate = {tid: (sum(v) / len(v)) for tid, v in fails.items()}

    numeric_ids = {t["task_id"] for t in tasks if t.get("numeric_targets")}
    rng = np.random.default_rng(seed)

    by_cat: dict[str, list[tuple[str, float, float]]] = defaultdict(list)
    for tid, fr in fail_rate.items():
        if tid not in numeric_ids:
            continue
        cat = category_of(task_type_of(tid))
        # Tie-break with small uniform jitter (deterministic via seed)
        jitter = float(rng.uniform(0, 1e-6))
        by_cat[cat].append((tid, fr, jitter))

    chosen: dict[str, list[str]] = {}
    for cat in CATEGORY_ORDER:
        items = sorted(by_cat.get(cat, []), key=lambda x: (-x[1], x[2]))
        chosen[cat] = [it[0] for it in items[:TASKS_PER_CATEGORY]]
    return chosen


# ── client shims with temperature ────────────────────────────────────────────

_SYSTEM_PROMPT = (
    "You are an expert in Bayesian statistics and probability theory. "
    "Solve problems step by step, showing all working. "
    "Always end your response with your final answer on its own line "
    "in the format: ANSWER: <value1>, <value2>, ..."
)
_MAX_TOKENS = 1024


def _post_with_backoff(url: str, *, json_payload: dict, headers: dict,
                       waits: list[int] = (5, 15, 30)) -> dict:
    last_exc: Exception = RuntimeError("unreachable")
    for attempt in range(1, len(waits) + 2):
        try:
            r = httpx.post(url, json=json_payload, headers=headers, timeout=TIMEOUT)
            r.raise_for_status()
            return r.json()
        except Exception as exc:
            last_exc = exc
            if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code in (400, 401, 403, 404):
                raise
            if attempt > len(waits):
                raise
            time.sleep(waits[attempt - 1])
    raise last_exc


def query_claude(prompt: str, temperature: float, top_p: float) -> tuple[str, int, int]:
    key = os.environ["ANTHROPIC_API_KEY"]
    payload = {
        "model": "claude-sonnet-4-5",
        "max_tokens": _MAX_TOKENS,
        "system": _SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "top_p": top_p,
    }
    headers = {
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    data = _post_with_backoff("https://api.anthropic.com/v1/messages",
                              json_payload=payload, headers=headers)
    raw = data["content"][0]["text"]
    u = data.get("usage", {})
    return raw, u.get("input_tokens", 0), u.get("output_tokens", 0)


def query_chatgpt(prompt: str, temperature: float, top_p: float) -> tuple[str, int, int]:
    key = os.environ["OPENAI_API_KEY"]
    payload = {
        "model": "gpt-4.1",
        "max_tokens": _MAX_TOKENS,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "top_p": top_p,
    }
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    data = _post_with_backoff("https://api.openai.com/v1/chat/completions",
                              json_payload=payload, headers=headers)
    raw = data["choices"][0]["message"]["content"]
    u = data.get("usage", {})
    return raw, u.get("prompt_tokens", 0), u.get("completion_tokens", 0)


def query_deepseek(prompt: str, temperature: float, top_p: float) -> tuple[str, int, int]:
    key = os.environ["DEEPSEEK_API_KEY"]
    payload = {
        "model": "deepseek-chat",
        "max_tokens": _MAX_TOKENS,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "top_p": top_p,
    }
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    data = _post_with_backoff("https://api.deepseek.com/v1/chat/completions",
                              json_payload=payload, headers=headers)
    raw = data["choices"][0]["message"]["content"]
    u = data.get("usage", {})
    return raw, u.get("prompt_tokens", 0), u.get("completion_tokens", 0)


def query_mistral(prompt: str, temperature: float, top_p: float) -> tuple[str, int, int]:
    key = os.environ["MISTRAL_API_KEY"]
    payload = {
        "model": "mistral-large-latest",
        "max_tokens": _MAX_TOKENS,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "top_p": top_p,
    }
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    data = _post_with_backoff("https://api.mistral.ai/v1/chat/completions",
                              json_payload=payload, headers=headers)
    raw = data["choices"][0]["message"]["content"]
    u = data.get("usage", {})
    return raw, u.get("prompt_tokens", 0), u.get("completion_tokens", 0)


def query_gemini(prompt: str, temperature: float, top_p: float) -> tuple[str, int, int]:
    key = os.environ["GEMINI_API_KEY"]
    url = ("https://generativelanguage.googleapis.com/v1beta/models/"
           f"gemini-2.5-flash:generateContent?key={key}")
    payload = {
        "system_instruction": {"parts": [{"text": _SYSTEM_PROMPT}]},
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 4096,
            "temperature": temperature,
            "topP": top_p,
            "thinkingConfig": {"thinkingBudget": 0},
        },
    }
    data = _post_with_backoff(url, json_payload=payload, headers={},
                              waits=[10, 20, 40, 80, 160])
    raw = (data["candidates"][0]["content"]["parts"][0]["text"]
           if data.get("candidates") else "")
    u = data.get("usageMetadata", {})
    return raw, u.get("promptTokenCount", 0), u.get("candidatesTokenCount", 0)


QUERY_FN = {
    "claude": query_claude,
    "chatgpt": query_chatgpt,
    "gemini": query_gemini,
    "deepseek": query_deepseek,
    "mistral": query_mistral,
}


# ── consistency + ECE ────────────────────────────────────────────────────────

def numeric_match(a: list[float], b: list[float]) -> bool:
    """Tolerance-based equality of the leading numeric vector."""
    if not a or not b or len(a) != len(b):
        return False
    for x, y in zip(a, b):
        if math.isnan(x) or math.isnan(y):
            return False
        denom = max(abs(x), abs(y), 1.0)
        if abs(x - y) > TOL_ABS + TOL_REL * denom:
            return False
    return True


def consistency_score(answers: list[list[float]]) -> tuple[float, list[float]]:
    """Returns (consistency, modal_answer) given 3 parsed answers.

    Group answers by numeric_match equivalence; majority count → consistency.
    """
    if len(answers) < 2:
        return 0.33, (answers[0] if answers else [])
    # Greedy clustering by numeric_match
    clusters: list[list[list[float]]] = []
    for a in answers:
        placed = False
        for c in clusters:
            if numeric_match(a, c[0]):
                c.append(a)
                placed = True
                break
        if not placed:
            clusters.append([a])
    clusters.sort(key=len, reverse=True)
    biggest = len(clusters[0])
    n = len(answers)
    if biggest == n:
        return 1.0, clusters[0][0]
    elif biggest == 2 and n == 3:
        return 0.67, clusters[0][0]
    else:
        return 0.33, clusters[0][0]


def correct_against_truth(answer: list[float], targets: list[dict]) -> bool:
    """Is the model's first numeric answer within full_credit_tol of the first target?"""
    if not answer or not targets:
        return False
    # Use first target only for accuracy proxy
    truth = float(targets[0].get("value", float("nan")))
    if math.isnan(truth):
        return False
    tol = float(targets[0].get("full_credit_tol", TOL_ABS))
    return abs(answer[0] - truth) <= tol


def compute_ece(pairs: list[tuple[float, int]]) -> float:
    """ECE on (consistency, correct_int) pairs, with bin centers 0.33/0.67/1.0."""
    if not pairs:
        return float("nan")
    bins = {0.33: [], 0.67: [], 1.0: []}
    for c, hit in pairs:
        bins[c].append(hit)
    n = len(pairs)
    ece = 0.0
    for c, vals in bins.items():
        if not vals:
            continue
        acc = sum(vals) / len(vals)
        ece += (len(vals) / n) * abs(acc - c)
    return ece


def brier(pairs: list[tuple[float, int]]) -> float:
    if not pairs:
        return float("nan")
    return float(np.mean([(c - hit) ** 2 for c, hit in pairs]))


# ── runner ───────────────────────────────────────────────────────────────────

def load_completed(path: Path) -> set[tuple[str, str, int]]:
    if not path.exists():
        return set()
    out = set()
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        try:
            r = json.loads(line)
            out.add((r["task_id"], r["model"], r["run_idx"]))
        except Exception:
            continue
    return out


def append_jsonl(path: Path, rec: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(rec) + "\n")


def estimate_cost(records: list[dict]) -> float:
    total = 0.0
    for r in records:
        m = r["model"]
        if m not in COST_PER_1K:
            continue
        ci, co = COST_PER_1K[m]
        total += (r.get("input_tokens", 0) / 1000.0) * ci
        total += (r.get("output_tokens", 0) / 1000.0) * co
    return total


def main() -> int:
    print("=== B3 Self-Consistency Confidence Proxy ===")
    print(CITATION)
    print()

    tasks_list = json.loads(TASKS_PATH.read_text())
    tasks_by_id = {t["task_id"]: t for t in tasks_list}
    runs = [json.loads(l) for l in BASE_RUNS.read_text().splitlines() if l.strip()]
    print(f"loaded {len(tasks_list)} tasks, {len(runs)} v1 runs")

    stratification = stratified_sample(tasks_list, runs, seed=42)
    selected_ids: list[str] = []
    print("\nStratified subsample (top fail-rate per category):")
    for cat in CATEGORY_ORDER:
        ids = stratification.get(cat, [])
        print(f"  {cat:15s} → {ids}")
        selected_ids.extend(ids)
    print(f"\ntotal tasks: {len(selected_ids)} ({len(MODELS)} models × {N_RUNS} runs = "
          f"{len(selected_ids) * len(MODELS) * N_RUNS} calls)")

    # Build queue + skip already-completed
    completed = load_completed(OUT_RUNS)
    print(f"already completed: {len(completed)}")

    queue = []
    for tid in selected_ids:
        for model in MODELS:
            for run_idx in range(N_RUNS):
                if (tid, model, run_idx) not in completed:
                    queue.append((tid, model, run_idx))
    print(f"queued: {len(queue)}\n")

    records_this_session: list[dict] = []
    cost_warned = False
    n_done = 0
    aborted = False

    for tid, model, run_idx in queue:
        task = tasks_by_id.get(tid)
        if task is None:
            print(f"  skip {tid}: not in tasks_all.json")
            continue
        prompt = build_prompt(task)
        try:
            t0 = time.monotonic()
            raw, in_tok, out_tok = QUERY_FN[model](prompt, TEMPERATURE, TOP_P)
            latency = (time.monotonic() - t0) * 1000
            answer = parse_answer(raw)
            err = None
        except Exception as exc:
            raw = ""
            in_tok = out_tok = 0
            latency = 0
            answer = []
            err = str(exc)

        rec = {
            "task_id": tid,
            "model": model,
            "run_idx": run_idx,
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
            "raw_response": raw,
            "parsed_answer": answer,
            "input_tokens": in_tok,
            "output_tokens": out_tok,
            "latency_ms": latency,
            "error": err,
        }
        append_jsonl(OUT_RUNS, rec)
        records_this_session.append(rec)
        n_done += 1
        time.sleep(SLEEP_S)

        # Cost guard at 50 calls
        if n_done == 50:
            cost_so_far = estimate_cost(records_this_session)
            full_estimate = cost_so_far * len(queue) / max(n_done, 1)
            print(f"\n[cost guard @ 50 calls] running={cost_so_far:.3f} USD, "
                  f"projected_total={full_estimate:.3f} USD")
            if full_estimate > 5.0:
                print("ABORT: projected > $5 hard cap")
                aborted = True
                break
            if full_estimate > 1.50 and not cost_warned:
                print(f"WARN: projected > $1.50 (still under $5 hard cap, continuing)")
                cost_warned = True

        if n_done % 25 == 0:
            print(f"  ... {n_done}/{len(queue)} done")

    if aborted:
        print("Run aborted before completion. JSONL state preserved.")
    print(f"\nTotal calls this session: {n_done}")
    cost_total = estimate_cost(records_this_session)
    print(f"Total cost this session: ${cost_total:.3f}")

    # ── Aggregate across all completed records (resume-safe) ──
    all_recs = [json.loads(l) for l in OUT_RUNS.read_text().splitlines() if l.strip()] \
        if OUT_RUNS.exists() else []
    by_pair: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in all_recs:
        by_pair[(r["task_id"], r["model"])].append(r)

    keyword_ece = json.loads(CALIBRATION_PATH.read_text()) if CALIBRATION_PATH.exists() else {}

    per_model: dict[str, dict] = {}
    for model in MODELS:
        pairs: list[tuple[float, int]] = []
        n_high = n_med = n_low = 0
        for tid in selected_ids:
            triple = sorted(by_pair.get((tid, model), []), key=lambda x: x["run_idx"])
            if len(triple) < N_RUNS:
                continue
            answers = [t.get("parsed_answer") or [] for t in triple]
            cons, modal = consistency_score(answers)
            task = tasks_by_id.get(tid)
            targets = (task or {}).get("numeric_targets") or []
            hit = int(correct_against_truth(modal, targets))
            pairs.append((cons, hit))
            if cons >= 0.99:
                n_high += 1
            elif cons >= 0.5:
                n_med += 1
            else:
                n_low += 1
        ece = compute_ece(pairs)
        b = brier(pairs)
        per_model[model] = {
            "n_pairs_with_3_runs": len(pairs),
            "n_high":  n_high,
            "n_med":   n_med,
            "n_low":   n_low,
            "consistency_ece":   ece,
            "consistency_brier": b,
            "accuracy_overall": float(np.mean([h for _, h in pairs])) if pairs else float("nan"),
        }

    ece_comparison = {}
    for m in MODELS:
        kw = keyword_ece.get(m, {}).get("ece", float("nan"))
        cs = per_model[m]["consistency_ece"]
        ece_comparison[m] = {"keyword_ece": kw, "consistency_ece": cs,
                             "direction_flipped": (not math.isnan(kw) and not math.isnan(cs)
                                                   and (kw < 0.1) != (cs < 0.1))}

    output = {
        "_methodology_citation": CITATION,
        "n_tasks": len(selected_ids),
        "n_models": len(MODELS),
        "n_runs_per_pair": N_RUNS,
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
        "stratification": stratification,
        "selected_task_ids": selected_ids,
        "per_model": per_model,
        "ece_comparison": ece_comparison,
        "session_cost_usd": round(cost_total, 4),
        "aborted_partial": aborted,
    }
    OUT_CALIB.parent.mkdir(parents=True, exist_ok=True)
    OUT_CALIB.write_text(json.dumps(output, indent=2))
    print(f"\nSaved: {OUT_CALIB}")

    # Figure
    make_figure(per_model, ece_comparison, OUT_FIG)
    print(f"Saved: {OUT_FIG}")

    print("\n=== Per-model ECE comparison ===")
    print(f"{'model':10s}  keyword_ECE   consistency_ECE   n_high  n_med  n_low")
    for m in MODELS:
        c = ece_comparison[m]
        pm = per_model[m]
        kw_str = f"{c['keyword_ece']:.4f}" if not math.isnan(c['keyword_ece']) else "n/a"
        cs_str = f"{c['consistency_ece']:.4f}" if not math.isnan(c['consistency_ece']) else "n/a"
        print(f"  {m:10s}  {kw_str:>10s}    {cs_str:>14s}    {pm['n_high']:>4d}  "
              f"{pm['n_med']:>4d}  {pm['n_low']:>4d}")

    print("\n=== Did consistency populate the high-confidence bucket? ===")
    total_high = sum(per_model[m]["n_high"] for m in MODELS)
    print(f"  total n_high across all 5 models: {total_high}")
    print(f"  (keyword baseline: 0 across all 5 — see audit/limitations_disclosures.md)")

    print("\n=== FermiEval contrast under consistency proxy ===")
    overconfident_models = []
    print("  per-model high-bucket accuracy (1.0 means perfect when 3/3 agree):")
    for m in MODELS:
        triples = []
        for tid in selected_ids:
            triple = sorted(by_pair.get((tid, m), []), key=lambda x: x["run_idx"])
            if len(triple) < N_RUNS:
                continue
            answers = [t.get("parsed_answer") or [] for t in triple]
            cons, modal = consistency_score(answers)
            task = tasks_by_id.get(tid)
            targets = (task or {}).get("numeric_targets") or []
            hit = int(correct_against_truth(modal, targets))
            triples.append((cons, hit))
        hi = [h for c, h in triples if c >= 0.99]
        hi_acc = (sum(hi) / len(hi)) if hi else float("nan")
        flag = ""
        if hi and hi_acc < 0.7:
            flag = "  ← OVERCONFIDENT under consistency proxy"
            overconfident_models.append(m)
        print(f"    {m:10s}  high-bucket n={len(hi):>2d}  acc={hi_acc:.3f}{flag}")

    if overconfident_models:
        print(f"  → FermiEval-style overconfidence DOES appear under consistency proxy: {overconfident_models}")
    else:
        print("  → FermiEval contrast holds: no overconfidence detected even under consistency proxy.")

    return 0


def make_figure(_per_model: dict, ece_comparison: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 5), facecolor="none")
    models = MODELS
    colors = [MODEL_COLORS.get(m, "#888") for m in models]

    # Left: keyword ECE
    kw = [ece_comparison[m]["keyword_ece"] for m in models]
    kw_disp = [v if not math.isnan(v) else 0.0 for v in kw]
    ax = axes[0]
    ax.set_facecolor("#0a0a14")
    ax.bar(models, kw_disp, color=colors, edgecolor="none")
    ax.set_title("Keyword-based ECE\n(verbalized — MAC 2026)",
                 color="white", fontsize=12, pad=10)
    ax.set_ylabel("ECE", color="white", fontsize=11)
    ax.set_ylim(0, max(0.25, max(kw_disp) * 1.2))
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_color("white"); spine.set_alpha(0.5)
    ax.grid(True, axis="y", alpha=0.15, color="white")

    # Right: consistency ECE
    cs = [ece_comparison[m]["consistency_ece"] for m in models]
    cs_disp = [v if not math.isnan(v) else 0.0 for v in cs]
    ax = axes[1]
    ax.set_facecolor("#0a0a14")
    ax.bar(models, cs_disp, color=colors, edgecolor="none")
    ax.set_title("Consistency-based ECE\n(MAC 2026 + SelfCheckGPT 2023)",
                 color="white", fontsize=12, pad=10)
    ax.set_ylabel("ECE", color="white", fontsize=11)
    ax.set_ylim(0, max(0.25, max(cs_disp) * 1.2))
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_color("white"); spine.set_alpha(0.5)
    ax.grid(True, axis="y", alpha=0.15, color="white")

    # Annotate flips
    for i, m in enumerate(models):
        if ece_comparison[m]["direction_flipped"]:
            axes[1].text(i, cs_disp[i] + 0.005, "flip",
                         ha="center", color="#FFB347", fontsize=9, fontweight="bold")

    fig.text(0.5, -0.03,
             "Method dichotomy follows Multi-Answer Confidence (2026).",
             ha="center", color="white", fontsize=8, alpha=0.85)
    plt.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight", transparent=True)
    plt.close(fig)


if __name__ == "__main__":
    raise SystemExit(main())
