"""One-off: re-judge VB_04/mistral with max_tokens=2048 and replace errored record.

Reason: the original judge call returned malformed JSON ("]" instead of "}"
at end of reasoning_completeness). Same prompt + temperature=0; only
max_tokens raised. Methodology unchanged.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evaluation.llm_judge_rubric import (  # noqa: E402
    JUDGE_MODEL,
    TOGETHER_URL,
    _build_judge_prompt,
    _parse_judge_response,
)

load_dotenv(ROOT / ".env")

TARGET_RUN_ID = "0f74e564-f470-47b9-ae67-6888158b0144"
TARGET_TASK = "VB_04"
TARGET_MODEL = "mistral"

JUDGE_OUT = ROOT / "experiments/results_v2/llm_judge_scores_full.jsonl"
RUNS_FILE = ROOT / "experiments/results_v1/runs.jsonl"
TASKS_FILE = ROOT / "data/benchmark_v1/tasks_all.json"

MAX_TOKENS_NEW = 2048


def _load_run(path: Path, run_id: str) -> dict:
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("run_id") == run_id:
                return rec
    raise SystemExit(f"run_id {run_id} not found in {path}")


def _load_task(path: Path, task_id: str) -> dict:
    tasks = json.loads(path.read_text())
    for t in tasks:
        if t.get("task_id") == task_id:
            return t
    raise SystemExit(f"task_id {task_id} not found in {path}")


async def _call_judge(task: dict, run: dict, api_key: str) -> tuple[dict | None, str | None, dict]:
    prompt = _build_judge_prompt(task, run)
    payload = {
        "model": JUDGE_MODEL,
        "max_tokens": MAX_TOKENS_NEW,
        "temperature": 0.0,
        "messages": [{"role": "user", "content": prompt}],
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    async with httpx.AsyncClient() as client:
        resp = await client.post(TOGETHER_URL, json=payload, headers=headers, timeout=60.0)
        resp.raise_for_status()
        data = resp.json()
        raw = data["choices"][0]["message"]["content"]
        usage = data.get("usage") or {}
        parsed = _parse_judge_response(raw)
        return parsed, raw, {
            "input_tokens": int(usage.get("prompt_tokens", 0) or 0),
            "output_tokens": int(usage.get("completion_tokens", 0) or 0),
        }


def _replace_record(path: Path, run_id: str, new_record: dict) -> None:
    lines_out: list[str] = []
    replaced = False
    with path.open() as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue
            try:
                rec = json.loads(stripped)
            except json.JSONDecodeError:
                lines_out.append(stripped)
                continue
            if rec.get("run_id") == run_id:
                lines_out.append(json.dumps(new_record))
                replaced = True
            else:
                lines_out.append(stripped)
    if not replaced:
        raise SystemExit(f"run_id {run_id} not found in {path}")
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text("\n".join(lines_out) + "\n")
    os.replace(tmp, path)


async def main() -> int:
    api_key = os.environ.get("TOGETHER_API_KEY")
    if not api_key:
        raise SystemExit("TOGETHER_API_KEY missing")

    run = _load_run(RUNS_FILE, TARGET_RUN_ID)
    task = _load_task(TASKS_FILE, TARGET_TASK)
    assert run.get("task_id") == TARGET_TASK
    assert run.get("model_family") == TARGET_MODEL

    parsed, raw, usage = await _call_judge(task, run, api_key)
    if parsed is None:
        print("[FAIL] still unparseable. Raw response:")
        print(raw)
        return 2

    new_rec = {
        "run_id": run["run_id"],
        "task_id": run["task_id"],
        "model_family": run["model_family"],
        "judge_model": JUDGE_MODEL,
        "method_structure": parsed.get("method_structure", {"score": None, "justification": None}),
        "assumption_compliance": parsed.get("assumption_compliance", {"score": None, "justification": None}),
        "reasoning_quality": parsed.get("reasoning_quality", {"score": None, "justification": None}),
        "reasoning_completeness": parsed.get("reasoning_completeness", {"score": None, "justification": None}),
        "judge_latency_ms": 0,
        "input_tokens": usage["input_tokens"],
        "output_tokens": usage["output_tokens"],
        "judged_at": datetime.now(timezone.utc).isoformat(),
        "error": None,
        "regenerated_with_higher_max_tokens": True,
    }
    _replace_record(JUDGE_OUT, TARGET_RUN_ID, new_rec)
    print("[OK] replaced record:")
    print(json.dumps(new_rec, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
