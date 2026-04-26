#!/usr/bin/env python3
"""
summarize_results.py
Reads experiments/results_v1/runs.jsonl → generates
capstone-website/frontend/src/data/results_summary.json

Run from project root: python scripts/summarize_results.py
"""
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from statistics import mean, stdev

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS_PATH   = os.path.join(ROOT, 'experiments', 'results_v1', 'runs.jsonl')
OUTPUT_PATH = os.path.join(ROOT, 'capstone-website', 'frontend', 'src', 'data', 'results_summary.json')

EXPECTED_TASKS = 171   # Phase 1 (136) + Phase 2 (35) benchmark tasks
SYNTHETIC_SUFFIX = ("_rephrase", "_numerical", "_semantic")

def safe_mean(lst):
    return mean(lst) if lst else 0.0

def is_synthetic(task_id: str) -> bool:
    return any(task_id.endswith(s) for s in SYNTHETIC_SUFFIX)

def load_runs():
    runs = []
    with open(RUNS_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
                # Skip old placeholder records that lack key fields
                if not r.get('model_family') or not r.get('task_type'):
                    continue
                runs.append(r)
            except json.JSONDecodeError:
                pass
    return runs

def build_summary(runs):
    # Split benchmark (Phase1+2) vs synthetic runs
    bench_runs = [r for r in runs if not is_synthetic(r.get('task_id', ''))]
    synth_runs = [r for r in runs if is_synthetic(r.get('task_id', ''))]

    # Group by model (benchmark only for completeness check)
    by_model = defaultdict(list)
    for r in bench_runs:
        by_model[r['model_family']].append(r)

    # Also group synthetic
    by_model_synth = defaultdict(list)
    for r in synth_runs:
        by_model_synth[r['model_family']].append(r)

    # Classify models based on benchmark tasks only
    complete, partial, pending = [], [], []
    all_known = ['claude', 'chatgpt', 'deepseek', 'mistral', 'gemini']
    for m in all_known:
        n = len(by_model.get(m, []))
        if n >= EXPECTED_TASKS:
            complete.append(m)
        elif n > 0:
            partial.append(m)
        else:
            pending.append(m)

    # Per-model stats (benchmark runs only)
    by_model_out = {}
    for m, records in by_model.items():
        scores     = [r.get('final_score', 0) or 0 for r in records]
        latencies  = [r.get('latency_ms',  0) or 0 for r in records]
        passes     = [1 if r.get('pass') else 0 for r in records]
        num_scores = [r.get('numeric_score', 0) or 0 for r in records]
        str_scores = [r.get('structure_score', 0) or 0 for r in records]
        ass_scores = [r.get('assumption_score', 0) or 0 for r in records]

        # By task type
        by_type = defaultdict(list)
        for r in records:
            by_type[r['task_type']].append(r.get('final_score', 0) or 0)

        # By tier
        by_tier = defaultdict(list)
        for r in records:
            by_tier[str(r.get('tier', '?'))].append(r.get('final_score', 0) or 0)

        # Best / worst 5 task types
        type_avgs = {tt: safe_mean(sc) for tt, sc in by_type.items()}
        sorted_types = sorted(type_avgs.items(), key=lambda x: x[1])
        worst5 = [t for t, _ in sorted_types[:5]]
        best5  = [t for t, _ in sorted_types[-5:]]

        # Answer found rate
        answer_found = [1 if r.get('answer_found') else 0 for r in records]

        by_model_out[m] = {
            'tasks':              len(records),
            'pass':               sum(passes),
            'avg_score':          round(safe_mean(scores),    4),
            'avg_numeric_score':  round(safe_mean(num_scores),4),
            'avg_structure_score':round(safe_mean(str_scores),4),
            'avg_assumption_score':round(safe_mean(ass_scores),4),
            'pass_rate':          round(safe_mean(passes),    4),
            'avg_latency':        round(safe_mean(latencies), 1),
            'answer_found_rate':  round(safe_mean(answer_found), 4),
            'score_std':          round(stdev(scores) if len(scores) > 1 else 0, 4),
            'score_distribution': [round(s, 4) for s in sorted(scores)],
            'by_type': {tt: round(safe_mean(sc), 4) for tt, sc in by_type.items()},
            'by_tier': {tier: round(safe_mean(sc), 4) for tier, sc in by_tier.items()},
            'best_task_types':  best5,
            'worst_task_types': worst5,
        }

    # Task-type-level stats (benchmark runs only)
    by_type_all = defaultdict(lambda: defaultdict(list))
    for r in bench_runs:
        by_type_all[r['task_type']][r['model_family']].append(r.get('final_score', 0) or 0)

    task_type_stats = {}
    for tt, model_map in by_type_all.items():
        all_scores = [s for lst in model_map.values() for s in lst]
        task_type_stats[tt] = {
            'avg':    round(safe_mean(all_scores), 4),
            'count':  len(all_scores),
            'models': {m: round(safe_mean(sc), 4) for m, sc in model_map.items()},
        }

    # Tier-level stats (benchmark runs only)
    by_tier_all = defaultdict(lambda: defaultdict(list))
    for r in bench_runs:
        by_tier_all[str(r.get('tier', '?'))][r['model_family']].append(r.get('final_score', 0) or 0)

    tier_stats = {}
    for tier, model_map in by_tier_all.items():
        all_scores = [s for lst in model_map.values() for s in lst]
        tier_stats[tier] = {
            'avg':    round(safe_mean(all_scores), 4),
            'count':  len(all_scores),
            'models': {m: round(safe_mean(sc), 4) for m, sc in model_map.items()},
        }

    # Synthetic (RQ4) summary
    synth_by_model: dict = {}
    for m, records in by_model_synth.items():
        scores = [r.get('final_score', 0) or 0 for r in records]
        passes = [1 if r.get('pass') else 0 for r in records]
        synth_by_model[m] = {
            'tasks':      len(records),
            'avg_score':  round(safe_mean(scores), 4),
            'pass_rate':  round(safe_mean(passes),  4),
        }

    return {
        'generated_at':     datetime.now(timezone.utc).isoformat(),
        'total_runs':       len(runs),
        'benchmark_runs':   len(bench_runs),
        'synthetic_runs':   len(synth_runs),
        'models_complete':  complete,
        'models_partial':   partial,
        'models_pending':   pending,
        'by_model':         by_model_out,
        'synthetic_by_model': synth_by_model,
        'task_type_stats':  task_type_stats,
        'tier_stats':       tier_stats,
    }

def main():
    print(f'Reading {RUNS_PATH}...')
    runs = load_runs()
    print(f'Loaded {len(runs)} valid run records.')

    summary = build_summary(runs)

    complete_models = summary['models_complete']
    partial_models  = summary['models_partial']
    print(f'Complete models ({len(complete_models)}): {complete_models}')
    print(f'Partial models  ({len(partial_models)}): {partial_models}')

    for m, d in summary['by_model'].items():
        print(f'  {m}: n={d["tasks"]} avg_score={d["avg_score"]} pass_rate={d["pass_rate"]} avg_latency={d["avg_latency"]}ms')

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f'\nWrote {OUTPUT_PATH}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
