"""External LLM-as-judge rubric scoring via Llama 3.3 70B (Together AI).

Validates the keyword-based rubric in response_parser.py / metrics.py by
re-scoring each (task, response) pair with an external judge. Llama 3.3 70B
was chosen because it is NOT in the benchmark — eliminates self-preference
bias.

Inference provider: Together AI (`meta-llama/Llama-3.3-70B-Instruct-Turbo`).
External to all 5 benchmarked models. Open-weights model (reproducible).
Pay-per-token (~$0.88/M tokens) — no daily token cap blocking full-scale
runs. Estimated ~$8 for the full ~3,800-run project. Migrated from Groq's
free tier (100K tokens/day) which capped scaling at ~80 calls/day.

This module is SEPARATE from evaluation/llm_judge.py (the ANSWER-extraction
fallback). Do not confuse them.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
import re
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

TOGETHER_URL = "https://api.together.xyz/v1/chat/completions"
JUDGE_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
TIMEOUT_S = 60.0
RETRY_BACKOFF_S = 5.0
RATE_LIMIT_BACKOFF_S = 30.0  # 429 TPM resets per-minute, 5s is too short
MAX_TOKENS = 1024

JUDGE_PROMPT_TEMPLATE = """You are an impartial expert grader for Bayesian statistics responses. You are
NOT one of the models being evaluated — score objectively based only on what
the response demonstrates.

# Task given to the student
{task_prompt}

# Required structural elements (the response should contain these substantively)
{required_structure_checks}

# Required assumptions (the response should explicitly state these)
{required_assumption_checks}

# Student response
{response_text}

# Scoring rubric — score each dimension 0.0 to 1.0

1. METHOD_STRUCTURE: Does the response contain the required structural
   elements above, used substantively (not just keyword presence)?
   1.0 = all required elements present and used substantively
   0.5 = partially present or used vaguely
   0.0 = missing or wrong

2. ASSUMPTION_COMPLIANCE: Are the required assumptions explicitly stated and
   correct? "We assume independence" satisfies an iid check; using
   independence implicitly does not.
   1.0 = all required assumptions explicitly stated and correct
   0.5 = mentioned but vague or partially correct
   0.0 = missing or incorrect

3. REASONING_QUALITY: Score is the fraction of these four sub-criteria
   satisfied:
   (a) shows mathematical work step by step
   (b) identifies the model/distribution being used
   (c) states the relevant formula
   (d) interprets the result in plain language
   Possible scores: 0.0, 0.25, 0.5, 0.75, 1.0

4. REASONING_COMPLETENESS: Does the response actually walk through the
   reasoning, or just name-drop concepts and produce a number?
   1.0 = full derivation with intermediate steps
   0.5 = partial derivation, some steps skipped
   0.0 = answer-only or suspiciously brief

Return ONLY this JSON object — no preamble, no markdown fences, no commentary:
{{
  "method_structure":       {{"score": <float>, "justification": "<one sentence>"}},
  "assumption_compliance":  {{"score": <float>, "justification": "<one sentence>"}},
  "reasoning_quality":      {{"score": <float>, "justification": "<one sentence>"}},
  "reasoning_completeness": {{"score": <float>, "justification": "<one sentence>"}}
}}"""


def _format_checks(items: list[str]) -> str:
    if not items:
        return "(none)"
    return "\n".join(f"- {it}" for it in items)


def _build_judge_prompt(task: dict, run_record: dict) -> str:
    return JUDGE_PROMPT_TEMPLATE.format(
        task_prompt=run_record.get("prompt", "") or "(prompt missing)",
        required_structure_checks=_format_checks(task.get("required_structure_checks", [])),
        required_assumption_checks=_format_checks(task.get("required_assumption_checks", [])),
        response_text=run_record.get("raw_response", "") or "(empty response)",
    )


def _parse_judge_response(text: str) -> dict[str, Any] | None:
    """Strip ```json fences if present, parse JSON. Falls back to first {...} block."""
    t = re.sub(r"\s*```\s*$", "", re.sub(r"^```(?:json)?\s*", "", text.strip())).strip()
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", t, re.DOTALL)
        if not m:
            return None
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            return None


def _empty_result(run_record: dict, error: str, judge_latency_ms: int = 0,
                  raw_judge: str | None = None) -> dict[str, Any]:
    nf = {"score": None, "justification": None}
    out: dict[str, Any] = {
        "run_id": run_record.get("run_id"),
        "task_id": run_record.get("task_id"),
        "model_family": run_record.get("model_family"),
        "judge_model": JUDGE_MODEL,
        "method_structure": nf, "assumption_compliance": nf,
        "reasoning_quality": nf, "reasoning_completeness": nf,
        "judge_latency_ms": judge_latency_ms,
        "judged_at": datetime.now(timezone.utc).isoformat(),
        "error": error,
    }
    if raw_judge is not None:
        out["raw_judge_response"] = raw_judge
    return out


async def judge_response(
    task: dict,
    run_record: dict,
    client: httpx.AsyncClient,
    api_key: str,
) -> dict[str, Any]:
    """Score one (task, run) pair via the external judge. Catches errors, never raises."""
    prompt = _build_judge_prompt(task, run_record)
    payload = {
        "model": JUDGE_MODEL,
        "max_tokens": MAX_TOKENS,
        "temperature": 0.0,
        "messages": [{"role": "user", "content": prompt}],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    last_err: str | None = None
    raw_judge_text: str | None = None
    t0 = time.monotonic()

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
            raw_judge_text = data["choices"][0]["message"]["content"]
            usage = data.get("usage") or {}
            input_tokens = int(usage.get("prompt_tokens", 0) or 0)
            output_tokens = int(usage.get("completion_tokens", 0) or 0)
            parsed = _parse_judge_response(raw_judge_text)
            judge_latency_ms = int((time.monotonic() - t0) * 1000)

            if parsed is None:
                rec = _empty_result(run_record, "parse_error", judge_latency_ms, raw_judge_text)
                rec["input_tokens"] = input_tokens
                rec["output_tokens"] = output_tokens
                return rec
            nf = {"score": None, "justification": None}
            return {
                "run_id": run_record.get("run_id"),
                "task_id": run_record.get("task_id"),
                "model_family": run_record.get("model_family"),
                "judge_model": JUDGE_MODEL,
                "method_structure": parsed.get("method_structure", nf),
                "assumption_compliance": parsed.get("assumption_compliance", nf),
                "reasoning_quality": parsed.get("reasoning_quality", nf),
                "reasoning_completeness": parsed.get("reasoning_completeness", nf),
                "judge_latency_ms": judge_latency_ms,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "judged_at": datetime.now(timezone.utc).isoformat(),
                "error": None,
            }
        except (httpx.TimeoutException, httpx.ConnectError, httpx.NetworkError) as exc:
            last_err = f"network: {exc}"
            if attempt == 1:
                await asyncio.sleep(RETRY_BACKOFF_S)
                continue
        except httpx.HTTPStatusError as exc:
            body = ""
            try:
                body = exc.response.text[:200]
            except Exception:
                pass
            last_err = f"http {exc.response.status_code}: {body}"
            break
        except Exception as exc:
            last_err = f"unexpected: {exc}"
            break

    return _empty_result(
        run_record,
        error=last_err or "unknown",
        judge_latency_ms=int((time.monotonic() - t0) * 1000),
        raw_judge=raw_judge_text,
    )


def load_existing_run_ids(output_path: Path) -> set[str]:
    """Read output JSONL, return run_ids already judged successfully.
    Errored records are NOT counted — they will be retried on rerun."""
    if not output_path.exists():
        return set()
    seen: set[str] = set()
    with output_path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                rid = rec.get("run_id")
                if rid and not rec.get("error"):
                    seen.add(rid)
            except json.JSONDecodeError:
                continue
    return seen


def stratified_sample(runs: list[dict], n: int = 200, seed: int = 42) -> list[dict]:
    """Stratify by (model_family, task_type). Guarantee at least 1 per stratum."""
    if n >= len(runs):
        return list(runs)
    rng = random.Random(seed)
    strata: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in runs:
        key = (r.get("model_family") or "?", r.get("task_type") or "?")
        strata[key].append(r)

    selected: list[dict] = []
    for key, items in strata.items():
        pick = rng.choice(items)
        selected.append(pick)

    if len(selected) >= n:
        rng.shuffle(selected)
        return selected[:n]

    selected_ids = {r.get("run_id") for r in selected}
    remaining = [r for r in runs if r.get("run_id") not in selected_ids]
    rng.shuffle(remaining)
    needed = n - len(selected)
    selected.extend(remaining[:needed])
    rng.shuffle(selected)
    return selected


def _append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(record) + "\n")


def _strip_errored_records(path: Path, keep_run_ids: set[str]) -> None:
    """Rewrite output keeping only successfully-judged records (those in keep_run_ids).
    Drops errored records so they get retried cleanly on resume."""
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
                if rec.get("run_id") in keep_run_ids:
                    kept.append(line)
            except json.JSONDecodeError:
                continue
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text("\n".join(kept) + ("\n" if kept else ""))
    os.replace(tmp, path)


async def judge_runs_batch(
    runs: list[dict],
    tasks_by_id: dict[str, dict],
    output_path: Path,
    concurrency: int = 8,
) -> None:
    """Score many runs concurrently. Append each result as JSONL as it completes."""
    api_key = os.environ.get("TOGETHER_API_KEY")
    if not api_key:
        raise RuntimeError(
            "TOGETHER_API_KEY not set in environment. Add to .env: "
            "TOGETHER_API_KEY=<your key from api.together.xyz>"
        )

    already = load_existing_run_ids(output_path)
    _strip_errored_records(output_path, keep_run_ids=already)
    todo = [r for r in runs if r.get("run_id") not in already and r.get("task_id") in tasks_by_id]
    skipped_no_task = sum(1 for r in runs if r.get("task_id") not in tasks_by_id)

    print(f"Total runs: {len(runs)} | already judged: {len(already)} | "
          f"missing task spec: {skipped_no_task} | to judge: {len(todo)}")
    if not todo:
        print("Nothing to do.")
        return

    sem = asyncio.Semaphore(concurrency)
    write_lock = asyncio.Lock()
    completed = 0
    err_429 = 0
    err_503 = 0
    err_parse = 0
    err_timeout = 0
    err_other = 0
    total_in_tok = 0
    total_out_tok = 0
    t_start = time.monotonic()
    cost_per_mtok = 0.88  # $/M tokens (input + output combined for Llama 3.3 70B Turbo)
    PROGRESS_EVERY = 100

    async with httpx.AsyncClient() as client:
        async def worker(run_record: dict) -> None:
            nonlocal completed, err_429, err_503, err_parse, err_timeout, err_other
            nonlocal total_in_tok, total_out_tok
            async with sem:
                task = tasks_by_id[run_record["task_id"]]
                result = await judge_response(task, run_record, client, api_key)
                async with write_lock:
                    _append_jsonl(output_path, result)
                    completed += 1
                    total_in_tok += int(result.get("input_tokens") or 0)
                    total_out_tok += int(result.get("output_tokens") or 0)
                    err = result.get("error")
                    if err:
                        if "429" in err:
                            err_429 += 1
                        elif "503" in err or "5" == (err.split()[1][0] if "http " in err else "_"):
                            err_503 += 1
                        elif err == "parse_error":
                            err_parse += 1
                        elif "network" in err or "timeout" in err.lower():
                            err_timeout += 1
                        else:
                            err_other += 1
                    if completed % PROGRESS_EVERY == 0 or completed == len(todo):
                        elapsed = time.monotonic() - t_start
                        rate = completed / elapsed if elapsed > 0 else 0
                        remaining = len(todo) - completed
                        eta_s = remaining / rate if rate > 0 else 0
                        cost = ((total_in_tok + total_out_tok) / 1_000_000) * cost_per_mtok
                        print(
                            f"[progress] {completed}/{len(todo)} | "
                            f"elapsed={elapsed:.1f}s | "
                            f"rate={rate:.2f}/s | "
                            f"ETA={eta_s:.0f}s | "
                            f"errors 429={err_429} 503={err_503} parse={err_parse} timeout={err_timeout} other={err_other} | "
                            f"tokens in/out={total_in_tok}/{total_out_tok} | "
                            f"cost~${cost:.3f}",
                            file=sys.stderr, flush=True,
                        )

        await asyncio.gather(*(worker(r) for r in todo))


def _load_runs(path: Path) -> list[dict]:
    runs: list[dict] = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                if rec.get("run_id"):
                    runs.append(rec)
            except json.JSONDecodeError:
                continue
    return runs


def _load_tasks(path: Path) -> dict[str, dict]:
    tasks = json.loads(path.read_text())
    return {t["task_id"]: t for t in tasks if "task_id" in t}


def main() -> int:
    p = argparse.ArgumentParser(description="External LLM-as-judge rubric scoring (Groq Llama 3.3 70B)")
    p.add_argument("--runs", type=Path, required=True, help="Path to runs.jsonl")
    p.add_argument("--tasks", type=Path, required=True, help="Path to tasks_all.json")
    p.add_argument("--perturbations", type=Path, default=None,
                   help="Optional path to perturbations_all.json (merged into task spec lookup)")
    p.add_argument("--output", type=Path, required=True, help="Output JSONL path (append-safe)")
    p.add_argument("--sample", default="all",
                   help="Number of runs to sample, or 'all' (default: all). Stratified by model+task_type.")
    p.add_argument("--concurrency", type=int, default=8, help="Max concurrent judge calls (default 8)")
    p.add_argument("--seed", type=int, default=42, help="RNG seed for stratified sampling")
    args = p.parse_args()

    runs = _load_runs(args.runs)
    tasks_by_id = _load_tasks(args.tasks)
    if args.perturbations and args.perturbations.exists():
        pert_by_id = _load_tasks(args.perturbations)
        tasks_by_id.update(pert_by_id)
        print(f"Merged {len(pert_by_id)} perturbation specs.")
    print(f"Loaded {len(runs)} runs and {len(tasks_by_id)} task specs.")

    if args.sample == "all":
        sampled = runs
    else:
        try:
            n = int(args.sample)
        except ValueError:
            print(f"--sample must be int or 'all', got {args.sample!r}", file=sys.stderr)
            return 2
        sampled = stratified_sample(runs, n=n, seed=args.seed)
        print(f"Stratified sample: {len(sampled)} runs (requested {n})")

    asyncio.run(judge_runs_batch(sampled, tasks_by_id, args.output, args.concurrency))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
