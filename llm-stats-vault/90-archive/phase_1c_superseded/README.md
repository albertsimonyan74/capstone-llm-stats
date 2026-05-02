---
tags: [archive, phase-1c, calibration, self-consistency]
date: 2026-05-01
---

# Phase 1C — superseded B3 self-consistency artefacts

The B3 stratified self-consistency result is superseded by the Phase 1C
full-task expansion (161 numeric tasks × 5 models × 3 reruns at T=0.7).
Preserved here for provenance only.

## Files
- `self_consistency_calibration_b3_stratified.json` — original calibration
  output for the 30-task stratified subsample.
- `self_consistency_runs_b3_stratified.jsonl` — raw runs for the 30-task
  stratified subsample (450 records).

## Successor
The full-coverage equivalent is now the canonical
`experiments/results_v2/self_consistency_calibration.json` and
`experiments/results_v2/self_consistency_runs.jsonl`. See
[`audit/recompute_log.md`](../../../audit/recompute_log.md) §Phase 1C and
[`llm-stats-vault/00-home/research-narrative.md`](../../00-home/research-narrative.md)
RQ5 section for the methodology rationale and findings.
