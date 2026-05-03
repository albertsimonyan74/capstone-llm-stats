# Superseded Scripts

Scripts archived (not deleted) when their functionality was migrated into
canonical runtime paths. Preserved here for provenance and as
regression-test references — running them against current data should
produce byte-identical output to the runtime aggregation.

## recompute_nmacr.py

**Archived:** 2026-05-03 (Approach A)

**Original purpose:** Phase 1B post-hoc application of literature-derived
NMACR weights to per-dimension scores stored in
`experiments/results_v1/runs.jsonl` and judge dimensions in
`experiments/results_v2/llm_judge_scores_full.jsonl`. Produced
`experiments/results_v2/nmacr_scores_v2.jsonl` as the single source of
truth for downstream analyses (bootstrap CI, robustness, calibration).

**Why archived:** Approach A migrated literature-derived NMACR weights
into the runtime aggregation paths (`evaluation/metrics.py`,
`llm_runner/response_parser.py`), making the post-hoc reweighting step
redundant. Verified byte-identical regeneration of all canonical
surfaces post-migration.

**As regression-test reference:** If a future divergence between runtime
and post-hoc aggregation is suspected, this script can be temporarily
unarchived and run against current data; its output should still match
the runtime-produced `nmacr_scores_v2.jsonl` modulo the
`_header.generated_at` timestamp.

**See:**
- `audit/recompute_log.md` §"Phase 1.6 — Approach A"
- `audit/aggregation_locus.md`
- `audit/methodology_continuity.md` §"NMACR weighting"
