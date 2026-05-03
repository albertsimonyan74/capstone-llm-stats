#!/usr/bin/env python3
# llm_runner/run_all_tasks.py
"""
Core benchmark runner.

Queries Claude, Gemini, ChatGPT, DeepSeek, and/or Mistral against all 136 tasks and
logs results to experiments/results_v1/runs.jsonl.

Usage examples:
  # Dry-run (no API calls): print prompts for first 3 tasks
  python llm_runner/run_all_tasks.py --models claude --dry-run --limit 3

  # Live run, specific task types only
  python llm_runner/run_all_tasks.py --models claude gemini \\
      --task-types DISC_MEDIAN MARKOV REGRESSION

  # Full benchmark, all models
  python llm_runner/run_all_tasks.py --models claude gemini chatgpt deepseek mistral

  # Single model, first 5 tasks
  python llm_runner/run_all_tasks.py --models claude --limit 5

  # Run perturbation tasks (RQ4 robustness)
  python llm_runner/run_all_tasks.py --models claude --synthetic --dry-run --limit 5
  python llm_runner/run_all_tasks.py --models claude gemini --synthetic
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from collections import defaultdict
from typing import Any, Dict, List, Optional

from llm_runner.logger import log_jsonl, now_iso
from llm_runner.model_clients import get_client, GeminiQuotaExhausted
from llm_runner.prompt_builder import build_prompt
from llm_runner.response_parser import full_score

from dotenv import load_dotenv
load_dotenv()

# ── Helpers ───────────────────────────────────────────────────────────────────

_SYNTHETIC_PATH = "data/synthetic/perturbations_all.json"


def _task_prefix(task_id: str) -> str:
    """'DISC_MEDIAN_03' → 'DISC_MEDIAN'"""
    parts = task_id.rsplit("_", 1)
    return parts[0] if len(parts) == 2 and parts[1].isdigit() else task_id


def _load_tasks(path: str) -> List[Dict[str, Any]]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _load_completed(output_path: str) -> set:
    """Return set of (model_family, task_id) tuples already in runs.jsonl."""
    completed: set = set()
    if not os.path.exists(output_path):
        return completed
    with open(output_path, encoding="utf-8") as f:
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
                # Only count as completed if we got a real response (no error, non-empty)
                if fam and tid and raw and not err:
                    completed.add((fam, tid))
            except json.JSONDecodeError:
                pass
    return completed


def _load_perturbations(
    path: str,
    pert_types: Optional[List[str]],
) -> List[Dict[str, Any]]:
    """Load perturbations.json; optionally filter by perturbation_type."""
    with open(path, encoding="utf-8") as f:
        records = json.load(f)
    if pert_types:
        types_lower = [t.lower() for t in pert_types]
        records = [r for r in records if r["perturbation_type"] in types_lower]
    return records


def _filter_tasks(
    tasks: List[Dict[str, Any]],
    task_types: Optional[List[str]],
    limit: Optional[int],
) -> List[Dict[str, Any]]:
    if task_types:
        types_upper = [t.upper() for t in task_types]
        tasks = [t for t in tasks if _task_prefix(t["task_id"]) in types_upper]
    if limit:
        tasks = tasks[:limit]
    return tasks


def _make_run_record(
    task: Dict[str, Any],
    model_result: Dict[str, Any],
    prompt: str,
    scores: Dict[str, Any],
) -> Dict[str, Any]:
    num  = scores["numeric"]
    stru = scores["structure"]
    assu = scores["assumptions"]
    return {
        "run_id":           str(uuid.uuid4()),
        "timestamp":        now_iso(),
        "task_id":          task["task_id"],
        "task_type":        _task_prefix(task["task_id"]),
        "tier":             task["tier"],
        "difficulty":       task["difficulty"],
        "model":            model_result["model"],
        "model_family":     model_result["model_family"],
        "prompt":           prompt,
        "raw_response":     model_result["raw_response"],
        "parsed_values":    num["parsed_values"],
        "ground_truth":     num["ground_truth"],
        "numeric_score":    num["numeric_score"],
        "structure_score":  stru["structure_score"],
        "assumption_score": assu["assumption_score"],
        "final_score":      scores["final_score"],
        "pass":             scores["pass"],
        "answer_found":     num["answer_found"],
        "length_match":     num["length_match"],
        "input_tokens":     model_result["input_tokens"],
        "output_tokens":    model_result["output_tokens"],
        "latency_ms":       model_result["latency_ms"],
        "error":            model_result["error"],
    }


# ── Dry-run ───────────────────────────────────────────────────────────────────

def _dry_run(tasks: List[Dict[str, Any]], models: List[str]) -> None:
    print(f"\n{'='*70}")
    print(f"DRY RUN — {len(tasks)} tasks × {len(models)} model(s)  "
          f"(no API calls will be made)")
    print(f"{'='*70}")
    for task in tasks:
        prompt = task.get("prompt") or build_prompt(task)
        print(f"\n{'─'*70}")
        print(f"Task: {task['task_id']}  |  Tier {task['tier']}  |  {task['difficulty']}")
        if "perturbation_type" in task:
            print(f"Perturbation: {task['perturbation_type']}  |  Base: {task['base_task_id']}")
        print(f"{'─'*70}")
        print(prompt)
        print(f"\nExpected ANSWER keys: "
              f"{[nt['key'] for nt in task['numeric_targets']]}")
    print(f"\n{'='*70}")
    print(f"Dry run complete. Would have made {len(tasks)*len(models)} API calls.")
    print(f"{'='*70}\n")


# ── Summary printing ──────────────────────────────────────────────────────────

def _print_summary(records: List[Dict[str, Any]]) -> None:
    if not records:
        print("\n(No records to summarise.)")
        return

    # Per-model aggregates
    by_model: Dict[str, List[Dict]] = defaultdict(list)
    for r in records:
        by_model[r["model_family"]].append(r)

    print(f"\n{'='*68}")
    print("SUMMARY BY MODEL")
    print(f"{'='*68}")
    hdr = f"{'Model':<12} | {'Tasks':>5} | {'Pass':>4} | {'Avg Score':>9} | {'Avg Latency':>11}"
    print(hdr)
    print("-" * len(hdr))
    for family in sorted(by_model):
        recs = by_model[family]
        n       = len(recs)
        n_pass  = sum(1 for r in recs if r["pass"])
        avg_s   = sum(r["final_score"] for r in recs) / n
        avg_lat = sum(r["latency_ms"]  for r in recs) / n
        print(f"{family:<12} | {n:>5} | {n_pass:>4} | {avg_s:>9.3f} | {avg_lat:>9.0f}ms")

    # Per-task-type breakdown
    task_types = sorted({r["task_type"] for r in records})
    families   = sorted(by_model.keys())
    if len(families) > 0:
        print(f"\n{'='*68}")
        print("SCORE BY TASK TYPE")
        print(f"{'='*68}")
        col_w = 8
        header = f"{'Task Type':<14} | " + " | ".join(f"{f:<{col_w}}" for f in families)
        print(header)
        print("-" * len(header))
        by_type_model: Dict[tuple, List[float]] = defaultdict(list)
        for r in records:
            by_type_model[(r["task_type"], r["model_family"])].append(r["final_score"])
        for tt in task_types:
            row = f"{tt:<14} | "
            cols = []
            for fam in families:
                scores = by_type_model.get((tt, fam), [])
                cols.append(f"{sum(scores)/len(scores):.3f}" if scores else "  — ")
            row += " | ".join(f"{c:<{col_w}}" for c in cols)
            print(row)

    print(f"{'='*68}\n")


# ── Main runner ───────────────────────────────────────────────────────────────

def run(
    models: List[str],
    tasks_path: str,
    output_path: str,
    task_types: Optional[List[str]],
    limit: Optional[int],
    dry_run: bool,
    synthetic: bool = False,
    pert_types: Optional[List[str]] = None,
    delay: float = 3.0,
) -> None:
    if synthetic:
        tasks = _load_perturbations(_SYNTHETIC_PATH, pert_types)
        if limit:
            tasks = tasks[:limit]
        source_label = _SYNTHETIC_PATH
    else:
        tasks = _load_tasks(tasks_path)
        tasks = _filter_tasks(tasks, task_types, limit)
        source_label = tasks_path

    if not tasks:
        print("No tasks matched the given filters. Exiting.")
        return

    print(f"\nLoaded {len(tasks)} task(s) from {source_label}")
    if synthetic:
        print("Mode: SYNTHETIC (perturbation tasks, RQ4)")
    print(f"Models: {models}")
    if not synthetic and task_types:
        print(f"Filtered to types: {task_types}")

    if dry_run:
        _dry_run(tasks, models)
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Load already-completed (model_family, task_id) pairs for resume support
    completed = _load_completed(output_path)
    if completed:
        print(f"Resume mode: {len(completed)} task(s) already completed — will skip.")

    all_records: List[Dict[str, Any]] = []
    total_calls = len(models) * len(tasks)
    call_n = 0

    for family in models:
        client = get_client(family)
        if family == "gemini" and hasattr(client, "delay"):
            client.delay = delay
            print(f"  Gemini inter-request delay: {delay}s  |  retries: 5 (10→20→40→80→160s)")
        print(f"\n{'─'*60}")
        print(f"Model: {family.upper()} ({client.model})")
        print(f"{'─'*60}")

        for task in tasks:
            call_n += 1
            task_id = task["task_id"]

            if (family, task_id) in completed:
                print(f"  [{call_n:>3}/{total_calls}] [SKIP] {family:<10} | {task_id} — already completed")
                continue

            # Perturbation records carry a pre-built prompt; base tasks use builder.
            prompt = task.get("prompt") or build_prompt(task)

            try:
                model_result = client.query(prompt, task_id)
            except GeminiQuotaExhausted as exc:
                print(f"\n  *** {exc}")
                print(f"  *** Stopping Gemini run. Resume tomorrow after quota resets.")
                print(f"  *** Progress saved — {len(all_records)} new records written.\n")
                break
            raw = model_result["raw_response"]

            # Score (even if empty — will score 0)
            scores = full_score(raw, task)

            record = _make_run_record(task, model_result, prompt, scores)
            all_records.append(record)
            log_jsonl(output_path, record)

            # Live progress line
            status = "✓ PASS" if record["pass"] else "✗ FAIL"
            err_tag = f"  [ERROR: {model_result['error'][:40]}]" if model_result["error"] else ""
            print(
                f"  [{call_n:>3}/{total_calls}] {family:<10} | {task_id:<20} | "
                f"score={record['final_score']:.3f} | {status}{err_tag}"
            )

    _print_summary(all_records)
    print(f"Results appended → {output_path}  ({len(all_records)} new records)")


# ── CLI ───────────────────────────────────────────────────────────────────────

def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Run LLM benchmark against tasks.json",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument(
        "--models", nargs="+",
        choices=["claude", "gemini", "chatgpt", "deepseek", "mistral"],
        default=["claude"],
        help="Model families to query (default: claude)",
    )
    p.add_argument(
        "--tasks", default="data/benchmark_v1/tasks.json",
        help="Path to tasks.json (default: data/benchmark_v1/tasks.json)",
    )
    p.add_argument(
        "--output", default="experiments/results_v1/runs.jsonl",
        help="Output JSONL path (default: experiments/results_v1/runs.jsonl)",
    )
    p.add_argument(
        "--task-types", nargs="*", dest="task_types",
        help="Restrict to specific task type prefixes e.g. DISC_MEDIAN MARKOV",
    )
    p.add_argument(
        "--limit", type=int, default=None,
        help="Process only the first N tasks (after type filter)",
    )
    p.add_argument(
        "--dry-run", action="store_true", dest="dry_run",
        help="Print prompts without making any API calls",
    )
    p.add_argument(
        "--synthetic", action="store_true",
        help=(
            "Run perturbation tasks from data/synthetic/perturbations.json "
            "instead of the main benchmark (RQ4 robustness evaluation)"
        ),
    )
    p.add_argument(
        "--pert-types", nargs="*", dest="pert_types",
        choices=["rephrase", "numerical", "semantic"],
        help="Filter perturbations by type (default: all three types)",
    )
    p.add_argument(
        "--delay", type=float, default=3.0,
        help="Inter-request delay in seconds for Gemini (default: 3.0). "
             "Gemini 429s use separate exponential backoff: 10→20→40→80→160s, 5 retries.",
    )
    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    args = _parse_args(argv)
    run(
        models     = args.models,
        tasks_path = args.tasks,
        output_path= args.output,
        task_types = args.task_types,
        limit      = args.limit,
        dry_run    = args.dry_run,
        synthetic  = args.synthetic,
        pert_types = args.pert_types,
        delay      = args.delay,
    )


if __name__ == "__main__":
    main()
