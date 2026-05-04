"""Hierarchical error taxonomy classifier (L1 buckets + L2 E1-E9 codes).

Re-classifies 143 base-run failures via Llama 3.3 70B (Together AI) into a
two-level taxonomy. Resume-safe: rerun re-judges only errored / missing
records.

Output:
    experiments/results_v2/error_taxonomy_v2.json
    report_materials/figures/error_taxonomy_hierarchical.png
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
RUNS_PATH = ROOT / "experiments/results_v1/runs.jsonl"
TASKS_PATH = ROOT / "data/benchmark_v1/tasks_all.json"
OUT_JSON = ROOT / "experiments/results_v2/error_taxonomy_v2.json"
JUDGE_JSONL = ROOT / "experiments/results_v2/error_taxonomy_v2_judge.jsonl"
FIG_PATH = ROOT / "report_materials/figures/error_taxonomy_hierarchical.png"

TOGETHER_URL = "https://api.together.xyz/v1/chat/completions"
JUDGE_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
TIMEOUT_S = 60.0
RETRY_BACKOFF_S = 5.0
RATE_LIMIT_BACKOFF_S = 30.0
MAX_TOKENS = 512

SYNTH_SUFFIX = ("_rephrase", "_numerical", "_semantic")
RESPONSE_HARD_CAP = 1024  # output_tokens >= → truncation

# L2: E1-E9 codes
L2_CODES = {
    "E1_NUMERICAL_COMPUTATION": "Correct method, wrong arithmetic / calculation",
    "E2_METHOD_SELECTION": "Wrong statistical method / distribution / estimator",
    "E3_ASSUMPTION_VIOLATION": "Required assumptions ignored or unstated",
    "E4_FORMAT_FAILURE": "Answer present in prose but ANSWER: line not parseable",
    "E5_OVERCONFIDENCE": "High expressed confidence despite low accuracy",
    "E6_CONCEPTUAL_CONFUSION": "Fundamental misunderstanding of statistical concept",
    "E7_TRUNCATION": "Response cut off at token limit before ANSWER:",
    "E8_HALLUCINATION": "Invented values / formulas / references",
    "E9_UNCLASSIFIED": "Failure not matching any rule heuristic",
}

# L1 → L2 mapping (each E-code rolls up to exactly one L1 bucket)
L1_TO_L2 = {
    "MATHEMATICAL_ERROR":   ["E1_NUMERICAL_COMPUTATION"],
    "CONCEPTUAL_ERROR":     ["E2_METHOD_SELECTION", "E6_CONCEPTUAL_CONFUSION"],
    "ASSUMPTION_VIOLATION": ["E3_ASSUMPTION_VIOLATION"],
    "FORMATTING_FAILURE":   ["E4_FORMAT_FAILURE", "E7_TRUNCATION"],
    "HALLUCINATION":        ["E5_OVERCONFIDENCE", "E8_HALLUCINATION", "E9_UNCLASSIFIED"],
}
L2_TO_L1 = {l2: l1 for l1, codes in L1_TO_L2.items() for l2 in codes}

# L1 fill palette: distinct from site model palette (teal/mint/pink/blue/lavender).
# Saturated, high-contrast hues that read on both light and dark slide backgrounds.
# HALLUCINATION omitted from visualization (0/143 across all models — see Limitations L1).
L1_COLORS = {
    "ASSUMPTION_VIOLATION": "#f59e0b",  # amber
    "MATHEMATICAL_ERROR":   "#ef4444",  # red
    "FORMATTING_FAILURE":   "#64748b",  # slate
    "CONCEPTUAL_ERROR":     "#a855f7",  # purple
}

# Model identity carried via x-axis tick label color (not bar border)
MODEL_BORDER = {
    "claude":   "#00CED1",
    "chatgpt":  "#7FFFD4",
    "gemini":   "#FF6B6B",
    "deepseek": "#4A90D9",
    "mistral":  "#A78BFA",
}
MODEL_ORDER = ["claude", "chatgpt", "gemini", "deepseek", "mistral"]

JUDGE_PROMPT = """You are an expert grader classifying a FAILED Bayesian-statistics LLM response into a hierarchical error taxonomy.

# Task given to the model
{task_prompt}

# Required structural elements
{required_structure}

# Required assumptions
{required_assumptions}

# Expected numeric answer keys
{numeric_keys}

# Model's response (truncated to 1500 chars)
{response_text}

# Computed scores
numeric_score={numeric_score}, structure_score={structure_score}, assumption_score={assumption_score}, output_tokens={output_tokens}

# Hierarchy

Top-level (L1) — pick exactly ONE:
- MATHEMATICAL_ERROR: wrong computation, algebra, arithmetic
- ASSUMPTION_VIOLATION: failed to state or check required assumptions
- CONCEPTUAL_ERROR: wrong method, wrong distribution, wrong framework
- FORMATTING_FAILURE: right idea, unreadable / incomplete / truncated output
- HALLUCINATION: fabricated distributions, theorems, or values

Sub-level (L2) — pick exactly ONE E-code consistent with the L1 above:
- E1_NUMERICAL_COMPUTATION  → MATHEMATICAL_ERROR
- E2_METHOD_SELECTION       → CONCEPTUAL_ERROR
- E3_ASSUMPTION_VIOLATION   → ASSUMPTION_VIOLATION
- E4_FORMAT_FAILURE         → FORMATTING_FAILURE
- E5_OVERCONFIDENCE         → HALLUCINATION
- E6_CONCEPTUAL_CONFUSION   → CONCEPTUAL_ERROR
- E7_TRUNCATION             → FORMATTING_FAILURE
- E8_HALLUCINATION          → HALLUCINATION
- E9_UNCLASSIFIED           → HALLUCINATION (only if nothing else fits)

Rules:
- Pick the SINGLE dominant failure mode. If multiple apply, choose the one most causally responsible.
- E7_TRUNCATION only when output_tokens >= 1024 AND response cuts off mid-sentence.
- E1 only when method is correct (structure_score > 0.6) but numeric is wrong.
- E3 only when assumptions are the dominant gap (assumption_score == 0 with method correct).
- E8 for invented formulas / values not derivable from the prompt.

Return ONLY this JSON — no markdown fences, no preamble:
{{
  "l1": "<one of the L1 labels>",
  "l2": "<one of the E-codes>",
  "evidence": "<one short sentence quoting or paraphrasing the smoking-gun part of the response>"
}}"""


def load_failures() -> list[dict]:
    fails: list[dict] = []
    with RUNS_PATH.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            tid = r.get("task_id", "")
            if any(tid.endswith(s) for s in SYNTH_SUFFIX):
                continue
            if not r.get("task_type"):
                continue
            if r.get("error"):
                continue
            score = r.get("final_score")
            if score is None:
                continue
            if float(score) < 0.5:
                fails.append(r)
    return fails


def load_tasks() -> dict[str, dict]:
    tasks = json.loads(TASKS_PATH.read_text())
    return {t["task_id"]: t for t in tasks if "task_id" in t}


def _format_list(items: list[str]) -> str:
    if not items:
        return "(none)"
    return "\n".join(f"- {it}" for it in items)


def _build_prompt(run: dict, task: dict) -> str:
    raw = (run.get("raw_response") or "")[:1500]
    keys = [t.get("key") for t in task.get("numeric_targets", [])]
    return JUDGE_PROMPT.format(
        task_prompt=run.get("prompt", "(missing)"),
        required_structure=_format_list(task.get("required_structure_checks", [])),
        required_assumptions=_format_list(task.get("required_assumption_checks", [])),
        numeric_keys=keys or "(none — qualitative task)",
        response_text=raw or "(empty)",
        numeric_score=run.get("numeric_score"),
        structure_score=run.get("structure_score"),
        assumption_score=run.get("assumption_score"),
        output_tokens=run.get("output_tokens", 0),
    )


def _parse_judge(text: str) -> dict | None:
    t = re.sub(r"\s*```\s*$", "", re.sub(r"^```(?:json)?\s*", "", text.strip())).strip()
    for candidate in (t, (re.search(r"\{.*\}", t, re.DOTALL).group(0) if re.search(r"\{.*\}", t, re.DOTALL) else "")):
        if not candidate:
            continue
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass
        # Repair pass: escape stray backslashes from LaTeX (\( \sum \Sigma etc.)
        repaired = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', candidate)
        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            pass
    # Fallback: regex-extract l1 / l2 / evidence directly
    l1_m = re.search(r'"l1"\s*:\s*"([^"]+)"', t)
    l2_m = re.search(r'"l2"\s*:\s*"([^"]+)"', t)
    if l1_m and l2_m:
        ev_m = re.search(r'"evidence"\s*:\s*"((?:[^"\\]|\\.)*)"', t, re.DOTALL)
        return {
            "l1": l1_m.group(1),
            "l2": l2_m.group(1),
            "evidence": ev_m.group(1) if ev_m else None,
        }
    return None


def _validate_pair(l1: str, l2: str) -> tuple[str, str, str | None]:
    """Repair invalid L1/L2 pairs. Returns (l1, l2, repair_note or None)."""
    if l2 not in L2_CODES:
        return ("HALLUCINATION", "E9_UNCLASSIFIED", f"unknown_l2={l2}")
    canonical_l1 = L2_TO_L1[l2]
    if l1 != canonical_l1:
        return (canonical_l1, l2, f"l1_remapped_from={l1}")
    return (l1, l2, None)


async def judge_one(
    run: dict, task: dict, client: httpx.AsyncClient, api_key: str
) -> dict[str, Any]:
    prompt = _build_prompt(run, task)
    payload = {
        "model": JUDGE_MODEL,
        "max_tokens": MAX_TOKENS,
        "temperature": 0.0,
        "messages": [{"role": "user", "content": prompt}],
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    t0 = time.monotonic()
    last_err: str | None = None
    raw_text: str | None = None

    for attempt in (1, 2):
        try:
            resp = await client.post(TOGETHER_URL, json=payload, headers=headers, timeout=TIMEOUT_S)
            if resp.status_code == 429 and attempt == 1:
                await asyncio.sleep(RATE_LIMIT_BACKOFF_S)
                continue
            if 500 <= resp.status_code < 600 and attempt == 1:
                await asyncio.sleep(RETRY_BACKOFF_S)
                continue
            resp.raise_for_status()
            data = resp.json()
            raw_text = data["choices"][0]["message"]["content"]
            usage = data.get("usage") or {}
            parsed = _parse_judge(raw_text)
            latency_ms = int((time.monotonic() - t0) * 1000)
            if parsed is None:
                return {
                    "run_id": run.get("run_id"),
                    "task_id": run.get("task_id"),
                    "model_family": run.get("model_family"),
                    "l1": None, "l2": None, "evidence": None,
                    "judge_latency_ms": latency_ms,
                    "input_tokens": int(usage.get("prompt_tokens", 0) or 0),
                    "output_tokens": int(usage.get("completion_tokens", 0) or 0),
                    "judged_at": datetime.now(timezone.utc).isoformat(),
                    "error": "parse_error",
                    "raw_judge": raw_text,
                }
            l1_raw = parsed.get("l1", "")
            l2_raw = parsed.get("l2", "")
            l1, l2, repair = _validate_pair(l1_raw, l2_raw)
            return {
                "run_id": run.get("run_id"),
                "task_id": run.get("task_id"),
                "model_family": run.get("model_family"),
                "task_type": run.get("task_type"),
                "final_score": run.get("final_score"),
                "l1": l1, "l2": l2,
                "evidence": parsed.get("evidence"),
                "repair_note": repair,
                "judge_latency_ms": latency_ms,
                "input_tokens": int(usage.get("prompt_tokens", 0) or 0),
                "output_tokens": int(usage.get("completion_tokens", 0) or 0),
                "judged_at": datetime.now(timezone.utc).isoformat(),
                "error": None,
            }
        except (httpx.TimeoutException, httpx.ConnectError, httpx.NetworkError) as exc:
            last_err = f"network: {exc}"
            if attempt == 1:
                await asyncio.sleep(RETRY_BACKOFF_S)
                continue
        except httpx.HTTPStatusError as exc:
            try:
                body = exc.response.text[:200]
            except Exception:
                body = ""
            last_err = f"http {exc.response.status_code}: {body}"
            break
        except Exception as exc:
            last_err = f"unexpected: {exc}"
            break

    return {
        "run_id": run.get("run_id"),
        "task_id": run.get("task_id"),
        "model_family": run.get("model_family"),
        "l1": None, "l2": None, "evidence": None,
        "judge_latency_ms": int((time.monotonic() - t0) * 1000),
        "judged_at": datetime.now(timezone.utc).isoformat(),
        "error": last_err or "unknown",
    }


def load_existing(path: Path) -> dict[str, dict]:
    """Return run_id → record for successfully classified runs."""
    if not path.exists():
        return {}
    out = {}
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            rid = rec.get("run_id")
            if rid and not rec.get("error") and rec.get("l1"):
                out[rid] = rec
    return out


def append_jsonl(path: Path, rec: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(rec) + "\n")


def strip_errored(path: Path, keep_ids: set[str]) -> None:
    if not path.exists():
        return
    kept = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                if rec.get("run_id") in keep_ids:
                    kept.append(line)
            except json.JSONDecodeError:
                continue
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text("\n".join(kept) + ("\n" if kept else ""))
    os.replace(tmp, path)


async def classify_all(concurrency: int = 8) -> list[dict]:
    api_key = os.environ.get("TOGETHER_API_KEY")
    if not api_key:
        raise RuntimeError("TOGETHER_API_KEY not set in .env")

    fails = load_failures()
    tasks_by_id = load_tasks()

    existing = load_existing(JUDGE_JSONL)
    strip_errored(JUDGE_JSONL, keep_ids=set(existing.keys()))
    todo = [r for r in fails if r.get("run_id") not in existing and r.get("task_id") in tasks_by_id]
    skipped_no_task = sum(1 for r in fails if r.get("task_id") not in tasks_by_id)

    print(f"Failures: {len(fails)} | already classified: {len(existing)} | "
          f"missing task: {skipped_no_task} | to judge: {len(todo)}")

    if todo:
        sem = asyncio.Semaphore(concurrency)
        write_lock = asyncio.Lock()
        completed = 0
        errs = Counter()
        t_start = time.monotonic()

        async with httpx.AsyncClient() as client:
            async def worker(run: dict) -> None:
                nonlocal completed
                async with sem:
                    task = tasks_by_id[run["task_id"]]
                    rec = await judge_one(run, task, client, api_key)
                    async with write_lock:
                        append_jsonl(JUDGE_JSONL, rec)
                        completed += 1
                        if rec.get("error"):
                            errs[rec["error"].split(":")[0]] += 1
                        if completed % 25 == 0 or completed == len(todo):
                            elapsed = time.monotonic() - t_start
                            rate = completed / elapsed if elapsed > 0 else 0
                            print(f"[{completed}/{len(todo)}] {elapsed:.1f}s rate={rate:.2f}/s errors={dict(errs)}",
                                  file=sys.stderr, flush=True)

            await asyncio.gather(*(worker(r) for r in todo))

    return list(load_existing(JUDGE_JSONL).values())


def aggregate(records: list[dict]) -> dict:
    by_model_l1: dict[str, Counter] = defaultdict(Counter)
    by_model_l2: dict[str, Counter] = defaultdict(Counter)
    l1_total: Counter = Counter()
    l2_total: Counter = Counter()
    repairs = []

    for r in records:
        m = r.get("model_family")
        l1, l2 = r.get("l1"), r.get("l2")
        if not (m and l1 and l2):
            continue
        by_model_l1[m][l1] += 1
        by_model_l2[m][l2] += 1
        l1_total[l1] += 1
        l2_total[l2] += 1
        if r.get("repair_note"):
            repairs.append({"run_id": r["run_id"], "note": r["repair_note"]})

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "judge_model": JUDGE_MODEL,
        "n_failures_classified": sum(l1_total.values()),
        "l1_to_l2_mapping": L1_TO_L2,
        "l2_definitions": L2_CODES,
        "l1_totals": dict(l1_total.most_common()),
        "l2_totals": dict(l2_total.most_common()),
        "by_model_l1": {m: dict(c.most_common()) for m, c in by_model_l1.items()},
        "by_model_l2": {m: dict(c.most_common()) for m, c in by_model_l2.items()},
        "repaired_pairs": repairs,
        "records": records,
    }


def make_chart(summary: dict) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    by_model = summary["by_model_l1"]
    # Only iterate over populated L1 buckets (HALLUCINATION = 0/143; hidden from
    # visualization — see Limitations L1 for methodological disclosure).
    l1_order = list(L1_COLORS.keys())
    models = [m for m in MODEL_ORDER if m in by_model]

    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    fig.patch.set_alpha(0)

    x = np.arange(len(models))
    bottoms = np.zeros(len(models))

    for l1 in l1_order:
        heights = np.array([by_model.get(m, {}).get(l1, 0) for m in models], dtype=float)
        ax.bar(
            x, heights, bottom=bottoms,
            color=L1_COLORS[l1],
            edgecolor="white",
            linewidth=1.0,
            label=l1.replace("_", " ").title(),
        )
        for i, h in enumerate(heights):
            if h >= 1:
                ax.text(x[i], bottoms[i] + h / 2, str(int(h)),
                        ha="center", va="center", fontsize=10,
                        color="white", fontweight="bold")
        bottoms += heights

    # Per-model totals above bars (cohort header line, neutral charcoal so
    # it does not compete with model-color tick labels below the axis).
    for i in range(len(models)):
        total = int(bottoms[i])
        ax.text(x[i], total + 0.6, str(total), ha="center", va="bottom",
                fontsize=11, fontweight="bold", color="#222")

    # X-axis labels: model identity carried via tick color (matches site palette).
    ax.set_xticks(x)
    ax.set_xticklabels([m.upper() for m in models], fontsize=11, fontweight="bold")
    for tick, m in zip(ax.get_xticklabels(), models):
        tick.set_color(MODEL_BORDER.get(m, "#222"))

    ax.set_ylabel("Failure count", fontsize=11)
    ax.set_title("Hierarchical error taxonomy across models (n=143 base failures)",
                 fontsize=13, fontweight="bold", pad=14)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.set_ylim(0, max(bottoms) * 1.18)

    # Legend below chart, horizontal, 4 columns — out of bar-tops collision zone.
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.10),
        ncol=4,
        frameon=False,
        fontsize=10,
        title="L1 failure bucket",
        title_fontsize=10,
    )

    FIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.18)
    fig.savefig(FIG_PATH, dpi=150, transparent=True, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--concurrency", type=int, default=8)
    p.add_argument("--no-classify", action="store_true",
                   help="Skip Llama calls; aggregate + chart from existing JSONL only")
    args = p.parse_args()

    if args.no_classify:
        records = list(load_existing(JUDGE_JSONL).values())
    else:
        records = asyncio.run(classify_all(concurrency=args.concurrency))

    summary = aggregate(records)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(summary, indent=2))
    print(f"\nSummary written: {OUT_JSON}")
    print(f"L1 distribution: {summary['l1_totals']}")
    print(f"L2 distribution: {summary['l2_totals']}")

    make_chart(summary)
    print(f"Chart written: {FIG_PATH}")

    err_count = 0
    if JUDGE_JSONL.exists():
        with JUDGE_JSONL.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if rec.get("error"):
                    err_count += 1
    if err_count:
        print(f"Judge errors remaining: {err_count} (rerun to retry)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
