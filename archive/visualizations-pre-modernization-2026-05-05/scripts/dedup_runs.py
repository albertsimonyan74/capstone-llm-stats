#!/usr/bin/env python3
"""
dedup_runs.py
Deduplicate runs.jsonl by (model_family, task_id), keeping the latest record
(by timestamp) when multiple records exist for the same pair.

Run from project root: python scripts/dedup_runs.py
"""
from __future__ import annotations
import json
import os
import sys

ROOT       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS_PATH  = os.path.join(ROOT, "experiments", "results_v1", "runs.jsonl")


def main() -> int:
    with open(RUNS_PATH) as f:
        lines = [l.strip() for l in f if l.strip()]

    recs: list[dict] = []
    for l in lines:
        try:
            recs.append(json.loads(l))
        except json.JSONDecodeError:
            pass

    # Build winner index: keep latest timestamp per (model_family, task_id)
    winners: dict[tuple, dict] = {}
    for r in recs:
        fam = r.get("model_family")
        tid = r.get("task_id")
        if fam and tid:
            key = (fam, tid)
            if key not in winners or r.get("timestamp", "") > winners[key].get("timestamp", ""):
                winners[key] = r

    # Replay: emit first occurrence of the winner, skip all others
    emitted: set[tuple] = set()
    out_lines: list[str] = []
    removed = 0
    for r in recs:
        fam = r.get("model_family")
        tid = r.get("task_id")
        if fam and tid:
            key = (fam, tid)
            if key in emitted:
                removed += 1
                continue
            if winners.get(key) is r or (winners.get(key) or {}).get("run_id") == r.get("run_id"):
                emitted.add(key)
                out_lines.append(json.dumps(r))
            else:
                removed += 1
        else:
            out_lines.append(json.dumps(r))

    if removed == 0:
        print(f"runs.jsonl: {len(recs)} records, no duplicates found.")
        return 0

    with open(RUNS_PATH, "w") as f:
        f.write("\n".join(out_lines) + "\n")

    print(f"runs.jsonl: {len(recs)} → {len(out_lines)} records ({removed} duplicates removed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
