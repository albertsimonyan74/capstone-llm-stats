# Group A Completion Report

Day 4 — Group A (Mechanical Foundation). Generated 2026-05-02.

## Files refreshed in static_data

9 files copied from `experiments/results_v2/` to
`capstone-website/backend/static_data/experiments/results_v2/`:

- bootstrap_ci.json
- robustness_v2.json
- calibration.json
- error_taxonomy_v2.json
- keyword_vs_judge_agreement.json
- krippendorff_agreement.json
- self_consistency_calibration.json
- judge_dimension_means.json
- tolerance_sensitivity.json

Note: 5 of these files were byte-identical to the prior committed copy and
showed no diff after `cp`; the remaining 4 (bootstrap_ci, calibration,
robustness_v2, self_consistency_calibration) carried genuine Phase 1B/1C
content changes and registered as modified.

## Files added to static_data

4 NEW files (not previously present in static_data):

- nmacr_scores_v2.jsonl
- per_dim_calibration.json
- combined_pass_flip_analysis.json
- keyword_degradation_check.json

Total static_data/experiments/results_v2/ post-copy: 13 files.

## Canonical results_v2 refresh (Render reads from repo root, not static_data)

Discovery during smoke test: commit `016c40a` documents that Render is
deployed as `env=python`, NOT Docker, so `DATA_ROOT` defaults to repo root
in `v2_routes.py`. Production therefore reads
`experiments/results_v2/*.json` directly, not the static_data mirror.

To make the refresh actually visible to the deployed backend, an
additional commit (`c033e8e`) was added that mirrors the same 8 files at
the canonical repo path:

- M experiments/results_v2/bootstrap_ci.json
- M experiments/results_v2/calibration.json
- M experiments/results_v2/robustness_v2.json
- M experiments/results_v2/self_consistency_calibration.json
- A experiments/results_v2/combined_pass_flip_analysis.json
- A experiments/results_v2/keyword_degradation_check.json
- A experiments/results_v2/nmacr_scores_v2.jsonl
- A experiments/results_v2/per_dim_calibration.json

JSONL log files (perturbation_judge_scores.jsonl, perturbation_runs.jsonl,
self_consistency_runs.jsonl, error_taxonomy_v2_judge.jsonl) were left
untracked — they are not API-served and would inflate the Render deploy
artifact unnecessarily.

## Figures mirrored to frontend

8 figures into `capstone-website/frontend/public/visualizations/png/v2/`:

Re-mirrored (5 stale per audit F8.03):
- a2_accuracy_by_category.png
- a3_failure_heatmap.png
- a6_aggregate_ranking.png
- self_consistency_calibration.png
- three_rankings.png

Added (3 new):
- a4b_per_dim_robustness.png
- a5b_per_dim_calibration.png
- combined_pass_flip_comparison.png

Total v2 PNGs in frontend: 18 files. visualizations.js manifest NOT
modified (deferred to Group C).

## Backend code changes

`capstone-website/backend/v2_routes.py`:

1. Two ECE-comparison reads switched to a fallback pattern that prefers
   the Phase 1C canonical key `ece_comparison_full` and falls back to
   `ece_comparison` for backward compat with any older B3-stratified
   file:
   - line 314 (`/api/v2/rankings`): `sc.get("ece_comparison_full") or sc.get("ece_comparison", {})`
   - line 412 (`/api/v2/calibration`): `cons.get("ece_comparison_full") or cons.get("ece_comparison", {})`
2. V2_FILES dict gained two entries: `pass_flip` and `keyword_degradation`.
3. HEALTH_REQUIRED expanded from 6 to 11 entries (added
   calibration_consistency, judge_dimension_means, tolerance_sensitivity,
   pass_flip, keyword_degradation).
4. New endpoint `@router.get("/pass_flip")` added before the literature
   parser block. Returns `{base, perturbation, combined, comparison,
   keyword_degradation}` per spec.

## New endpoint

`/api/v2/pass_flip` — production-live status: NO (see deploy lag below).

Local validation via `uvicorn --port 8765/8766` with
`DATA_ROOT=/Users/albertsimonyan/Desktop/capstone-llm-stats` confirmed:
- `/api/v2/health` → ok=true, 11 files all exist+parse
- `/api/v2/pass_flip` → combined.n_pass_flip=708, combined.pct_pass_flip=0.2216
- `/api/v2/calibration` → consistency.ece_comparison populated with all 5 models
- `/api/v2/rankings` → calibration.consistency_ece populated (ece_comparison_full
  fallback verified)

## Production smoke test

Polled https://bayes-benchmark.onrender.com for ~45 minutes after push.
Backend CODE updated successfully (HEALTH_REQUIRED returns 11 entries —
proof the new v2_routes.py is live). However, the canonical-path DATA
files have not been redeployed by Render free-tier within the polling
window. The 4 NEW files (combined_pass_flip_analysis.json,
keyword_degradation_check.json, nmacr_scores_v2.jsonl,
per_dim_calibration.json) and the 4 MODIFIED files (bootstrap_ci.json,
calibration.json, robustness_v2.json, self_consistency_calibration.json)
are not yet visible on production — Render is still serving the
pre-Phase-1B/1C versions.

| Endpoint | Expected | Actual (production) | Pass |
|---|---|---|---|
| /api/v2/health | 11 files ok:true | 11 files listed, ok:false (2 new files missing) | NO (deploy lag) |
| /api/v2/headline_numbers | pass_flip present | pass_flip_rate=0.2502, n=274/1095 (base only, OLD source) | PARTIAL |
| /api/v2/rankings | gemini #1 acc, mistral #1 rob | claude #1 acc 0.679, chatgpt #1 rob (OLD data) | NO (deploy lag) |
| /api/v2/calibration | consistency_ece populated | populated, all 5 models present (ece_comparison_full fallback works) | YES |
| /api/v2/pass_flip | combined 22.16%, verdict SUPPORTED | 404 "Data file missing: combined_pass_flip_analysis.json" | NO (deploy lag) |

## Frontend smoke test

| Asset | URL | Status |
|---|---|---|
| combined_pass_flip_comparison.png | bayes-benchmark.vercel.app | HTTP 200 |
| a4b_per_dim_robustness.png | bayes-benchmark.vercel.app | HTTP 200 |

Vercel frontend deploy succeeded; new figure files are reachable.

## Deploy issues

Render free-tier deploy lag: ~45 minutes after `git push origin main`,
the repo-root canonical data files (notably the 1.5MB
nmacr_scores_v2.jsonl) had not propagated to the deployed backend even
though the code had. Code-side change confirmed live via the expanded
HEALTH_REQUIRED count (11 entries) and the now-correct
`ece_comparison_full` fallback in /api/v2/calibration response.

Recommended remediation (out of Group A scope):
- Verify Render dashboard for the most recent build status
- If the build is stuck, manually trigger a redeploy from the Render UI
- If the build keeps failing on the 1.5MB nmacr jsonl, consider gzipping
  it server-side or switching to env=docker to use the static_data path
  whose file sizes are smaller in aggregate

Three commits pushed to main this session:
- `def9237` — Refresh static_data + add /api/v2/pass_flip + ece_comparison_full fallback
- `af0da3b` — Refresh figures with Phase 1B/1C/1.5 renders
- `c033e8e` — Mirror canonical files at repo root for Render

## Open items for Group B/C/D

Group B (frontend prose):
- Methodology.jsx hardcoded Claude 0.679 values
- Limitations.jsx hardcoded Phase 1A pair + B3 caveat
- KeyFindings.jsx static fallback Phase 1A
- App.jsx PRIMARY/SUPPORTING percentage badges
- visualizations.js stale captions
- Methodology paragraph for keyword-degradation finding

Group C (new panels):
- Per-dim robustness panel
- Per-dim calibration panel
- Accuracy-calibration correlation panel
- Per-model keyword-judge disagreement card
- Keyword-degradation visualization integration
- visualizations.js entries for a4b/a5b/combined_pass_flip

Group D (housekeeping):
- 2 cross-reference fixes in audit docs
- 274/1094 → 274/1095 in two doc instances
- After Render redeploy completes, re-run smoke test to confirm
  /api/v2/pass_flip returns combined=22.16% with verdict SUPPORTED

## Final re-poll (post-wait)

Re-polled production after additional wait window. Status unchanged:

| Endpoint | Status | Detail |
|---|---|---|
| /api/v2/health | ok=false | 9/11 files exist; combined_pass_flip_analysis.json + keyword_degradation_check.json still missing |
| /api/v2/rankings | STALE | claude acc=0.679092 #1, chatgpt #1 robustness — Phase 1A values |
| /api/v2/headline_numbers | STALE | pass_flip_rate=0.2502 n=274/1095, krippendorff α=0.5502 — Phase 1A |
| /api/v2/calibration | PASS | ece_comparison_full fallback works |
| /api/v2/pass_flip | 404 | "Data file missing: combined_pass_flip_analysis.json" |

Verified `origin/main` contains canonical Phase 1B data
(`weighting_scheme: "literature_v1"` in bootstrap_ci.json) — the lag is
strictly in Render's deploy pipeline, not in git state.

Possible causes:
- Render free-tier auto-deploy stuck/queued on the c033e8e commit
  (1.5MB nmacr_scores_v2.jsonl + 4429-line robustness_v2.json diff may
  exceed free-tier build window)
- Render mtime cache in v2_routes.py persists across worker restart
- Render service paused due to inactivity; needs manual wake

Recommended action (user):
1. Open Render dashboard → bayes-benchmark service → check build log
2. If build queued/failed, click "Manual Deploy" → "Clear build cache & deploy"
3. Re-run smoke test once dashboard shows successful deploy

Group A code/data layer is COMPLETE on git side. Production propagation
is a Render operational issue independent of code correctness.
