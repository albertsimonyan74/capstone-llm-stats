#!/usr/bin/env python3
"""Score 473 perturbations × 5 models — keyword rubric only.

Loads the canonical merged perturbation set from data/synthetic/perturbations_all.json
(473 records: the 75 historical hand-authored task_ids preserved verbatim plus 398
generated v2 perturbations), queries each model, scores via keyword rubric
(`response_parser.full_score`), appends to
`experiments/results_v2/perturbation_runs.jsonl`. Resume-safe: skips any
(model_family, task_id) pair already present with non-empty raw_response and
no error. After this completes, run the external Llama judge via:

    python -m evaluation.llm_judge_rubric \\
        --runs experiments/results_v2/perturbation_runs.jsonl \\
        --tasks data/synthetic/perturbations_all.json \\
        --output experiments/results_v2/perturbation_judge_scores.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List

# allow direct invocation: `python scripts/score_perturbations.py`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv()

from llm_runner.logger import log_jsonl, now_iso
from llm_runner.model_clients import get_client, GeminiQuotaExhausted
from llm_runner.response_parser import full_score
from baseline.utils_task_id import task_type_from_id

COMBINED = Path("data/synthetic/perturbations_all.json")
DEFAULT_OUTPUT = Path("experiments/results_v2/perturbation_runs.jsonl")
ALL_MODELS = ["claude", "gemini", "chatgpt", "deepseek", "mistral"]


def load_perturbations() -> List[Dict[str, Any]]:
    """Load the canonical 473-record merged perturbation set."""
    return json.loads(COMBINED.read_text())


def load_completed(output_path: Path) -> set:
    completed: set = set()
    if not output_path.exists():
        return completed
    with output_path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
                fam = r.get("model_family")
                tid = r.get("task_id")
                raw = r.get("raw_response", "")
                err = r.get("error")
                if fam and tid and raw and not err:
                    completed.add((fam, tid))
            except json.JSONDecodeError:
                pass
    return completed


def make_record(task: Dict[str, Any], model_result: Dict[str, Any],
                prompt: str, scores: Dict[str, Any]) -> Dict[str, Any]:
    num = scores["numeric"]
    stru = scores["structure"]
    assu = scores["assumptions"]
    return {
        "run_id":            str(uuid.uuid4()),
        "timestamp":         now_iso(),
        "task_id":           task["task_id"],
        "task_type":         task_type_from_id(task["task_id"]),
        "base_task_id":      task.get("base_task_id"),
        "perturbation_type": task.get("perturbation_type"),
        "tier":              task["tier"],
        "difficulty":        task["difficulty"],
        "model":             model_result["model"],
        "model_family":      model_result["model_family"],
        "prompt":            prompt,
        "raw_response":      model_result["raw_response"],
        "parsed_values":     num["parsed_values"],
        "ground_truth":      num["ground_truth"],
        "numeric_score":     num["numeric_score"],
        "structure_score":   stru["structure_score"],
        "assumption_score":  assu["assumption_score"],
        "confidence_score":  scores["confidence_score"],
        "reasoning_score":   scores["reasoning_score"],
        "final_score":       scores["final_score"],
        "pass":              scores["pass"],
        "answer_found":      num["answer_found"],
        "length_match":      num["length_match"],
        "input_tokens":      model_result["input_tokens"],
        "output_tokens":     model_result["output_tokens"],
        "latency_ms":        model_result["latency_ms"],
        "error":             model_result["error"],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--models", nargs="+", choices=ALL_MODELS, default=ALL_MODELS)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    ap.add_argument("--limit", type=int, default=None,
                    help="Only score the first N perturbations.")
    ap.add_argument("--delay", type=float, default=3.0,
                    help="Inter-request delay for Gemini.")
    args = ap.parse_args()

    perts = load_perturbations()
    print(f"Loaded {len(perts)} perturbations from {COMBINED}")
    if args.limit:
        perts = perts[:args.limit]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    completed = load_completed(args.output)
    if completed:
        print(f"Resume: {len(completed)} (model, task_id) pairs already scored.")

    total = len(args.models) * len(perts)
    n_call = new_records = err_count = 0
    in_tok = out_tok = 0
    t0 = time.monotonic()

    for family in args.models:
        client = get_client(family)
        if family == "gemini" and hasattr(client, "delay"):
            client.delay = args.delay
        print(f"\n{'─'*64}\nModel: {family.upper()} ({client.model})\n{'─'*64}")

        for task in perts:
            n_call += 1
            tid = task["task_id"]
            if (family, tid) in completed:
                continue

            prompt = task["prompt"]
            try:
                model_result = client.query(prompt, tid)
            except GeminiQuotaExhausted as exc:
                print(f"\n  *** {exc} — stopping {family}, resume after quota reset.")
                break
            raw = model_result["raw_response"]
            scores = full_score(raw, task)
            rec = make_record(task, model_result, prompt, scores)
            log_jsonl(str(args.output), rec)
            new_records += 1
            in_tok += int(rec.get("input_tokens") or 0)
            out_tok += int(rec.get("output_tokens") or 0)
            if model_result.get("error"):
                err_count += 1
            status = "PASS" if rec["pass"] else "FAIL"
            err_tag = f" [ERR:{model_result['error'][:32]}]" if model_result.get("error") else ""
            print(f"  [{n_call:>4}/{total}] {family:<10} {tid:<32} "
                  f"score={rec['final_score']:.3f} {status}{err_tag}", flush=True)

    dt = time.monotonic() - t0
    print(f"\n{'='*64}\nDONE")
    print(f"  New records:   {new_records}")
    print(f"  Errors:        {err_count}")
    print(f"  Wall-clock:    {dt:.1f}s ({dt/60:.2f} min)")
    print(f"  Tokens:        in={in_tok:,}  out={out_tok:,}  total={in_tok+out_tok:,}")
    print(f"  Output:        {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
