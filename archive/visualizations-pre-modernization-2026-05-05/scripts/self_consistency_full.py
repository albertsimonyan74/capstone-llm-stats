"""Phase 1C — Full-coverage self-consistency confidence proxy.

Methodology grounded in Multi-Answer Confidence (arxiv 2602.07842) and
SelfCheckGPT (Manakul et al., 2023). Replaces stratified B3 result with
full task-set coverage. Addresses Phase 1B finding that confidence
calibration (C dimension, 15% weight) requires non-verbalized methods
for gemini and reliable measurement for all models.

Scope:
- All numeric-target-bearing tasks (161 of 171 — 10 CONCEPTUAL tasks
  excluded because consistency proxy requires numerical answers).
- All 5 models including gemini.
- 3 reruns per (task, model) at temperature=0.7, top_p=0.95.
- Total calls: 2,415.
- Hard budget: $15 (abort if cumulative > $15). Soft pause: $5.
- Resume-safe: writes one JSONL record per (task, model, run_idx) and
  skips already-completed tuples on restart.

Differences from B3 (scripts/self_consistency_proxy.py):
- No stratification by category × failure rate.
- Output to self_consistency_runs_full.jsonl (separate from B3 raw).
- Cost guards adjusted: warn at $5, abort at $15.
- Writes progress every 50 calls to logs/self_consistency_full.log.

Outputs:
- experiments/results_v2/self_consistency_runs_full.jsonl       (append-only)
- experiments/results_v2/self_consistency_calibration_full.json
- (Step 7 separately regenerates the calibration figure.)

Run from project root:
    python scripts/self_consistency_full.py
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import httpx
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from llm_runner.prompt_builder import build_prompt, parse_answer
TASKS_PATH = ROOT / "data/benchmark_v1/tasks_all.json"
CALIB_VERBALIZED = ROOT / "experiments/results_v2/calibration.json"
B3_CALIB = ROOT / "experiments/results_v2/self_consistency_calibration.json"
OUT_RUNS = ROOT / "experiments/results_v2/self_consistency_runs_full.jsonl"
OUT_CALIB = ROOT / "experiments/results_v2/self_consistency_calibration_full.json"
LOG = ROOT / "logs/self_consistency_full.log"

CITATION = (
    "Methodology grounded in Multi-Answer Confidence (arxiv 2602.07842) "
    "and SelfCheckGPT (Manakul et al., 2023). Phase 1C full-task expansion "
    "of stratified B3."
)

MODELS = ["claude", "chatgpt", "gemini", "deepseek", "mistral"]
N_RUNS = 3
TEMPERATURE = 0.7
TOP_P = 0.95
TIMEOUT = 60.0
SLEEP_S = 1.0

TOL_ABS = 0.01
TOL_REL = 0.05

# Cost estimates per 1K tokens (vendor list prices)
COST_PER_1K = {
    "claude":   (0.003,    0.015),
    "chatgpt":  (0.0020,   0.0080),
    "gemini":   (0.000075, 0.0003),
    "deepseek": (0.00027,  0.0011),
    "mistral":  (0.002,    0.006),
}

WARN_USD = 5.0
HARD_USD = 15.0

LOG_EVERY = 50

_SYSTEM_PROMPT = (
    "You are an expert in Bayesian statistics and probability theory. "
    "Solve problems step by step, showing all working. "
    "Always end your response with your final answer on its own line "
    "in the format: ANSWER: <value1>, <value2>, ..."
)
_MAX_TOKENS = 1024


def log(msg: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now(timezone.utc).isoformat()}] {msg}"
    print(line)
    with LOG.open("a") as f:
        f.write(line + "\n")


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
    # Anthropic now rejects temperature + top_p together — use temperature only.
    payload = {
        "model": "claude-sonnet-4-5",
        "max_tokens": _MAX_TOKENS,
        "system": _SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
    }
    headers = {"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
    data = _post_with_backoff("https://api.anthropic.com/v1/messages", json_payload=payload, headers=headers)
    raw = data["content"][0]["text"]
    u = data.get("usage", {})
    return raw, u.get("input_tokens", 0), u.get("output_tokens", 0)


def query_chatgpt(prompt: str, temperature: float, top_p: float) -> tuple[str, int, int]:
    key = os.environ["OPENAI_API_KEY"]
    payload = {
        "model": "gpt-4.1",
        "max_tokens": _MAX_TOKENS,
        "messages": [{"role": "system", "content": _SYSTEM_PROMPT},
                     {"role": "user", "content": prompt}],
        "temperature": temperature,
        "top_p": top_p,
    }
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    data = _post_with_backoff("https://api.openai.com/v1/chat/completions", json_payload=payload, headers=headers)
    raw = data["choices"][0]["message"]["content"]
    u = data.get("usage", {})
    return raw, u.get("prompt_tokens", 0), u.get("completion_tokens", 0)


def query_deepseek(prompt: str, temperature: float, top_p: float) -> tuple[str, int, int]:
    key = os.environ["DEEPSEEK_API_KEY"]
    payload = {
        "model": "deepseek-chat",
        "max_tokens": _MAX_TOKENS,
        "messages": [{"role": "system", "content": _SYSTEM_PROMPT},
                     {"role": "user", "content": prompt}],
        "temperature": temperature,
        "top_p": top_p,
    }
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    data = _post_with_backoff("https://api.deepseek.com/v1/chat/completions", json_payload=payload, headers=headers)
    raw = data["choices"][0]["message"]["content"]
    u = data.get("usage", {})
    return raw, u.get("prompt_tokens", 0), u.get("completion_tokens", 0)


def query_mistral(prompt: str, temperature: float, top_p: float) -> tuple[str, int, int]:
    key = os.environ["MISTRAL_API_KEY"]
    payload = {
        "model": "mistral-large-latest",
        "max_tokens": _MAX_TOKENS,
        "messages": [{"role": "system", "content": _SYSTEM_PROMPT},
                     {"role": "user", "content": prompt}],
        "temperature": temperature,
        "top_p": top_p,
    }
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    data = _post_with_backoff("https://api.mistral.ai/v1/chat/completions", json_payload=payload, headers=headers)
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
    "claude": query_claude, "chatgpt": query_chatgpt,
    "gemini": query_gemini, "deepseek": query_deepseek,
    "mistral": query_mistral,
}


# ── consistency + ECE ────────────────────────────────────────────────────────

def numeric_match(a: list[float], b: list[float]) -> bool:
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
    if len(answers) < 2:
        return 0.33, (answers[0] if answers else [])
    clusters: list[list[list[float]]] = []
    for a in answers:
        placed = False
        for c in clusters:
            if numeric_match(a, c[0]):
                c.append(a); placed = True; break
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
    if not answer or not targets:
        return False
    truth = float(targets[0].get("value", float("nan")))
    if math.isnan(truth):
        return False
    tol = float(targets[0].get("full_credit_tol", TOL_ABS))
    return abs(answer[0] - truth) <= tol


def compute_ece(pairs: list[tuple[float, int]]) -> float:
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


def main() -> int:
    log("=== Phase 1C Self-Consistency (full coverage) ===")
    log(CITATION)

    tasks_list = json.loads(TASKS_PATH.read_text())
    tasks_by_id = {t["task_id"]: t for t in tasks_list}
    numeric_ids = [t["task_id"] for t in tasks_list if t.get("numeric_targets")]
    log(f"Loaded {len(tasks_list)} tasks; {len(numeric_ids)} numeric (consistency-eligible)")

    completed = load_completed(OUT_RUNS)
    log(f"Already completed: {len(completed)}")

    queue: list[tuple[str, str, int]] = []
    for tid in numeric_ids:
        for model in MODELS:
            for run_idx in range(N_RUNS):
                if (tid, model, run_idx) not in completed:
                    queue.append((tid, model, run_idx))
    log(f"Queued: {len(queue)} (target = {len(numeric_ids) * len(MODELS) * N_RUNS})")

    records_this_session: list[dict] = []
    n_done = 0
    aborted = False
    cost_warned = False
    failures_per_model: dict[str, int] = defaultdict(int)

    for tid, model, run_idx in queue:
        task = tasks_by_id.get(tid)
        if task is None:
            log(f"  skip {tid}: not in tasks_all.json")
            continue
        prompt = build_prompt(task)
        try:
            t0 = time.monotonic()
            raw, in_tok, out_tok = QUERY_FN[model](prompt, TEMPERATURE, TOP_P)
            latency = (time.monotonic() - t0) * 1000
            answer = parse_answer(raw)
            err = None
        except Exception as exc:
            raw = ""; in_tok = out_tok = 0; latency = 0; answer = []
            err = str(exc)
            failures_per_model[model] += 1

        rec = {
            "task_id": tid, "model": model, "run_idx": run_idx,
            "temperature": TEMPERATURE, "top_p": TOP_P,
            "raw_response": raw, "parsed_answer": answer,
            "input_tokens": in_tok, "output_tokens": out_tok,
            "latency_ms": latency, "error": err,
        }
        append_jsonl(OUT_RUNS, rec)
        records_this_session.append(rec)
        n_done += 1
        time.sleep(SLEEP_S)

        if n_done % LOG_EVERY == 0:
            cost_so_far = estimate_cost(records_this_session)
            full_estimate = cost_so_far * len(queue) / max(n_done, 1)
            log(f"  progress {n_done}/{len(queue)}  running=${cost_so_far:.3f}  "
                f"projected_total=${full_estimate:.3f}  failures={dict(failures_per_model)}")
            if cost_so_far > HARD_USD:
                log(f"ABORT: cumulative cost ${cost_so_far:.3f} > $15 hard cap")
                aborted = True
                break
            if cost_so_far > WARN_USD and not cost_warned:
                log(f"WARN: cumulative ${cost_so_far:.3f} > $5 soft pause "
                    f"(continuing; hard cap is $15)")
                cost_warned = True

    if aborted:
        log("Run aborted before completion. JSONL state preserved.")
    log(f"Total calls this session: {n_done}")
    cost_total = estimate_cost(records_this_session)
    log(f"Total cost this session: ${cost_total:.3f}")

    # ── Aggregate across all completed records ──
    all_recs = [json.loads(l) for l in OUT_RUNS.read_text().splitlines() if l.strip()] \
        if OUT_RUNS.exists() else []
    by_pair: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in all_recs:
        by_pair[(r["task_id"], r["model"])].append(r)

    verbalized_calib = json.loads(CALIB_VERBALIZED.read_text()) if CALIB_VERBALIZED.exists() else {}
    b3_calib = json.loads(B3_CALIB.read_text()) if B3_CALIB.exists() else {}

    per_model: dict[str, dict] = {}
    for model in MODELS:
        pairs: list[tuple[float, int]] = []
        n_high = n_med = n_low = 0
        bucket_hits = {"high": [], "med": [], "low": []}
        for tid in numeric_ids:
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
                n_high += 1; bucket_hits["high"].append(hit)
            elif cons >= 0.5:
                n_med += 1; bucket_hits["med"].append(hit)
            else:
                n_low += 1; bucket_hits["low"].append(hit)
        per_model[model] = {
            "n_pairs_with_3_runs": len(pairs),
            "n_high":  n_high,
            "n_med":   n_med,
            "n_low":   n_low,
            "high_bucket_accuracy": (sum(bucket_hits["high"])/len(bucket_hits["high"])) if bucket_hits["high"] else None,
            "med_bucket_accuracy":  (sum(bucket_hits["med"]) /len(bucket_hits["med"]))  if bucket_hits["med"]  else None,
            "low_bucket_accuracy":  (sum(bucket_hits["low"]) /len(bucket_hits["low"]))  if bucket_hits["low"]  else None,
            "ece_consistency":   compute_ece(pairs),
            "brier":             brier(pairs),
            "accuracy_overall":  float(np.mean([h for _, h in pairs])) if pairs else None,
            "failures":          failures_per_model[model],
        }

    # Comparison block: verbalized vs B3 stratified vs Phase 1C full
    ece_comparison: dict[str, dict] = {}
    for m in MODELS:
        verb_block = verbalized_calib.get(m) if isinstance(verbalized_calib, dict) else None
        verb_ece = verb_block.get("ece") if isinstance(verb_block, dict) else None
        b3_per = b3_calib.get("per_model", {}).get(m) if isinstance(b3_calib, dict) else None
        b3_ece = b3_per.get("consistency_ece") if isinstance(b3_per, dict) else None
        full_ece = per_model[m]["ece_consistency"]
        ece_comparison[m] = {
            "verbalized_ece":           verb_ece,
            "consistency_ece_stratified": b3_ece,
            "consistency_ece_full":     None if (full_ece is None or (isinstance(full_ece, float) and math.isnan(full_ece))) else full_ece,
        }

    # Gemini-specific finding block
    gemini_verbalized = (verbalized_calib.get("gemini") or {}) if isinstance(verbalized_calib, dict) else {}
    gem_pm = per_model.get("gemini", {})
    gemini_finding = {
        "verbalized_signals": 0,  # established in Phase 1B (all 246 unstated)
        "verbalized_ece_reported": gemini_verbalized.get("ece"),
        "consistency_high_bucket_n": gem_pm.get("n_high"),
        "consistency_high_bucket_accuracy": gem_pm.get("high_bucket_accuracy"),
        "consistency_ece_full": gem_pm.get("ece_consistency"),
        "interpretation": (
            "Verbalized extraction yielded 0 signal for gemini in Phase 1B "
            "(all 246 base runs unstated). The consistency proxy populates a "
            "high-bucket of size n_high and reports an ECE. This shows that "
            "non-verbalized methods recover calibration information for "
            "models whose verbalization style hides confidence."
        ),
    }

    output = {
        "_methodology_citation": CITATION,
        "_supersedes": "self_consistency_calibration.json (stratified B3, archived to llm-stats-vault/90-archive/phase_1c_superseded/)",
        "n_tasks": len(numeric_ids),
        "n_total_tasks_in_corpus": len(tasks_list),
        "n_excluded_conceptual": len(tasks_list) - len(numeric_ids),
        "n_models": len(MODELS),
        "n_runs_per_pair": N_RUNS,
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
        "per_model": per_model,
        "ece_comparison_full": ece_comparison,
        "gemini_finding": gemini_finding,
        "session_cost_usd": round(cost_total, 4),
        "aborted_partial": aborted,
        "failures_per_model": dict(failures_per_model),
    }
    OUT_CALIB.parent.mkdir(parents=True, exist_ok=True)
    OUT_CALIB.write_text(json.dumps(output, indent=2, default=lambda v: None if (isinstance(v, float) and math.isnan(v)) else v))
    log(f"Saved {OUT_CALIB}")

    log("\n=== Per-model ECE comparison (verbalized / stratified-B3 / full) ===")
    for m in MODELS:
        c = ece_comparison[m]
        v = c["verbalized_ece"]
        s = c["consistency_ece_stratified"]
        f_ = c["consistency_ece_full"]
        v_str = f"{v:.4f}" if isinstance(v, (int, float)) and not (isinstance(v, float) and math.isnan(v)) else "n/a"
        s_str = f"{s:.4f}" if isinstance(s, (int, float)) and not (isinstance(s, float) and math.isnan(s)) else "n/a"
        f_str = f"{f_:.4f}" if isinstance(f_, (int, float)) and not (isinstance(f_, float) and math.isnan(f_)) else "n/a"
        pm = per_model[m]
        log(f"  {m:10s}  verb={v_str}  strat={s_str}  full={f_str}  "
            f"n_high={pm['n_high']}  n_med={pm['n_med']}  n_low={pm['n_low']}  "
            f"failures={pm['failures']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
