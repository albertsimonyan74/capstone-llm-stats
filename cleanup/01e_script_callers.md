# Investigation 5 — orphan-script caller greps

**Verdict: 3 of 5 candidates are NOT orphans (have active code callers). 2 are true orphans.**

Excluded from grep: `.venv/`, `node_modules/`, `.git/`, `archive/`, `llm-stats-vault/90-archive/`. Vault markdown documentation references (`llm-stats-vault/40-literature/...`, `llm-stats-vault/sessions/...`) are documentation, not code callers — listed but not counted as live callers.

---

## 1. `data/synthetic/perturbations_v2.json` — TRUE ORPHAN (read side)

**Code readers**: 0
**Code writer**: 1

| File:line | Direction |
|---|---|
| [scripts/generate_perturbations_full.py:13](scripts/generate_perturbations_full.py#L13) | doc-comment |
| [scripts/generate_perturbations_full.py:106](scripts/generate_perturbations_full.py#L106) | `DEFAULT_OUTPUT = ROOT / "data" / "synthetic" / "perturbations_v2.json"` (writer only) |

No script `json.load`s `perturbations_v2.json`. The merged `perturbations_all.json` is the canonical input for everything downstream. **Safe to archive `perturbations_v2.json`** — but note: re-running `generate_perturbations_full.py` will regenerate it. Action: archive snapshot AND retarget `DEFAULT_OUTPUT` if archiving permanently. Or simply leave in place since it's the natural generator output.

Vault doc references (not code):
- `llm-stats-vault/40-literature/papers/08-new-brittlebench-2026.md:22, 37`
- `capstone-website/backend/static_data/llm-stats-vault/...:22, 37` (bundled mirror)

---

## 2. `scripts/dedup_runs.py` — NOT ORPHAN

**Active caller**: 1

| File:line | Caller |
|---|---|
| [scripts/refresh_pipeline.sh:21](scripts/refresh_pipeline.sh#L21) | `python scripts/dedup_runs.py` |

Called as part of `refresh_pipeline.sh`, the documented refresh entry point. **Keep.**

---

## 3. `scripts/generate_group_a_figures.py` — NOT ORPHAN

**Active callers**: 2 (cross-referenced internally by other scripts; standalone generator)

| File:line | Reference |
|---|---|
| [scripts/robustness_analysis.py:10, 47](scripts/robustness_analysis.py) | doc-comment + "Same 6-group taxonomy as `scripts/generate_group_a_figures.py`" — copies taxonomy from this file |
| [llm-stats-vault/90-archive/audit/personal_todo_status.md:167](llm-stats-vault/90-archive/audit/personal_todo_status.md#L167), [llm-stats-vault/90-archive/audit/tier2a6_dual_write_fix.md](llm-stats-vault/90-archive/audit/tier2a6_dual_write_fix.md), [llm-stats-vault/90-archive/audit/cleanup_audit_2026-05-02.md:181](llm-stats-vault/90-archive/audit/cleanup_audit_2026-05-02.md#L181) | documented as the canonical figure generator for `a1`–`a6` PNGs in `report_materials/figures/` |
| [llm-stats-vault/sessions/2026-05-05-day5-tier2a5.md:31, 46](llm-stats-vault/sessions/2026-05-05-day5-tier2a5.md) | session notes describe `figure_a6`, `figure_a2` as canonical |

Outputs `a1_failure_by_tasktype.png`, `a2_accuracy_by_category.png`, `a3_failure_heatmap.png`, `a4_robustness_by_perttype.png`, `a5_calibration_reliability.png`, `a6_aggregate_ranking.png` — all paper-relevant figures. **Keep.**

---

## 4. `scripts/site_palette.py` — NOT ORPHAN (heavily depended on)

**Active callers**: 14 Python files import it.

| File:line | Import |
|---|---|
| [scripts/recompute_downstream.py:37](scripts/recompute_downstream.py#L37) | `from site_palette import (...)` |
| [scripts/rank_shift.py:20](scripts/rank_shift.py#L20) | `from site_palette import (...)` |
| [scripts/robustness_analysis.py:29](scripts/robustness_analysis.py#L29) | ... |
| [scripts/combined_pass_flip_analysis.py:55](scripts/combined_pass_flip_analysis.py#L55) | ... |
| [scripts/bootstrap_ci.py:27](scripts/bootstrap_ci.py#L27) | ... |
| [scripts/tolerance_sensitivity.py:32](scripts/tolerance_sensitivity.py#L32) | ... |
| [scripts/error_taxonomy.py:30](scripts/error_taxonomy.py#L30) | ... |
| [scripts/generate_group_a_figures.py:28](scripts/generate_group_a_figures.py#L28) | ... |
| [scripts/dimension_leaderboard.py:28](scripts/dimension_leaderboard.py#L28) | ... |
| [scripts/disagreement_by_perttype.py:27](scripts/disagreement_by_perttype.py#L27) | ... |
| [scripts/three_rankings_figure.py:17](scripts/three_rankings_figure.py#L17) | ... |
| [scripts/calibration_analysis.py:38, 169, 260, 384](scripts/calibration_analysis.py) | ... |
| [scripts/krippendorff_agreement.py:39](scripts/krippendorff_agreement.py#L39) | ... |
| [scripts/plot_self_consistency_calibration.py:19](scripts/plot_self_consistency_calibration.py#L19) | ... |
| [scripts/keyword_vs_judge_agreement.py:28](scripts/keyword_vs_judge_agreement.py#L28) | ... |

Mirror of frontend `capstone-website/frontend/src/data/sitePalette.js` (kept in sync per `poster/DESIGN_AUDIT.md:59` and `poster/scripts/print_theme.py:3`). **Keep — core shared utility.** My Phase 1 inventory misclassified it.

---

## 5. `scripts/inspect_judge_strictness.py` — TRUE ORPHAN (no code callers)

**Active code callers**: 0

| File:line | Reference |
|---|---|
| [scripts/inspect_judge_strictness.py:9](scripts/inspect_judge_strictness.py#L9) | self-docstring |
| [llm-stats-vault/90-archive/audit/cleanup_audit_2026-05-02.md:162, 202, 207, 500, 731](llm-stats-vault/90-archive/audit/cleanup_audit_2026-05-02.md) | catalogued as "[CL-B6] keep until poster delivered" |
| [llm-stats-vault/90-archive/audit/discovery_audit_2026-05-02.md:323](llm-stats-vault/90-archive/audit/discovery_audit_2026-05-02.md#L323) | mentioned alongside `Methodology.jsx` Groq spot-check |
| [llm-stats-vault/90-archive/audit/recompute_log.md:583](llm-stats-vault/90-archive/audit/recompute_log.md#L583) | listed among 11 scripts re-pointed during a refactor |

Standalone diagnostic, never imported. **Archive candidate** — poster has been delivered (per session 2026-05-07-poster-defense-prep.md). Per audit note CL-B6, archive is now safe.

---

## Summary table

| Candidate | True orphan? | Action |
|---|---|---|
| `data/synthetic/perturbations_v2.json` | ✅ orphan as data input | Archive (or leave if generator output path retained) |
| `scripts/dedup_runs.py` | ❌ — called by `refresh_pipeline.sh` | **KEEP** |
| `scripts/generate_group_a_figures.py` | ❌ — canonical figure generator for `a1`–`a6` | **KEEP** |
| `scripts/site_palette.py` | ❌ — imported by 14 scripts | **KEEP** |
| `scripts/inspect_judge_strictness.py` | ✅ orphan, post-poster | Archive |

Phase 1 inventory's [UNCLEAR] block on these scripts is now resolved. Reorg plan should reflect KEEP-CORE for `dedup_runs.py`, `generate_group_a_figures.py`, `site_palette.py`.
