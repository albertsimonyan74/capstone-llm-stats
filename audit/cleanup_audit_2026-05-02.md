# Cleanup Audit — 2026-05-02

READ-ONLY inventory. No file movements performed by this audit. Execution
deferred until after Group C verification completes.

## Executive summary

- Total findings: 35
- SAFE to archive: 8
- LIKELY_SAFE: 11
- UNCERTAIN (needs review): 6
- DO_NOT_TOUCH: 10
- Estimated total disk space recoverable (SAFE + LIKELY_SAFE): ~600 KB
  active text/scripts + ~370 KB logs + ~55 KB stale figures = **~1.0 MB
  in code/text/figs**, plus the optional 1.6 MB Render workaround mirror
  (deferred, gated on D-5)

Disk-space recovery is modest — the highest value of this audit is
**reducing cognitive surface area** (fewer stale audit docs and superseded
scripts to wade through) rather than freeing disk.

---

## Findings by category

### Category A — audit/ folder

**[CL-A1] audit/headline_numbers_500_diagnosis.md**
Type: INTERMEDIATE
Severity: SAFE
Reason: One-shot diagnostic for a bug already fixed in commit 21be1d4
("Fix /api/v2/headline_numbers 500: isinstance guard"). Content is purely
diagnostic — no remaining consumer.
Replacement: bug fix already in main; comprehensive_audit_2026-05-01.md
references the fix obliquely.
Recommended action: ARCHIVE (intermediate_analyses/)
Estimated saved: 2.9 KB

**[CL-A2] audit/day2_audit_report.md**
Type: SUPERSEDED
Severity: LIKELY_SAFE
Reason: Day-2 specific audit. Comprehensive audit 2026-05-01 absorbs the
load-bearing findings. day2 still records useful detail not folded
elsewhere (e.g., D-7 keyword vs judge breakdown, D-8 tolerance sweep).
Replacement: audit/comprehensive_audit_2026-05-01.md
Recommended action: ARCHIVE (audit_history/) — preserve as historical
record; if any unique finding has not been folded into comprehensive,
fold it before archive.
Estimated saved: 27.7 KB

**[CL-A3] audit/deployment_report.md**
Type: SUPERSEDED
Severity: LIKELY_SAFE
Reason: Day-3 deploy report. Group A completion report contains the
current production smoke-test status; this Day-3 snapshot is now stale
(predates Phase 1B/1C/1.5 refresh).
Replacement: audit/group_a_completion.md (sections "Production smoke
test" + "Final re-poll").
Recommended action: ARCHIVE (audit_history/)
Estimated saved: 6.7 KB

**[CL-A4] audit/gemini_verification.md**
Type: INTERMEDIATE
Severity: LIKELY_SAFE
Reason: One-shot diagnostic answering "why does Gemini lead reasoning_quality
under literature weights?" Findings folded into recompute_log.md §"Per-model
base aggregate" + "Reading" notes. Diagnostic complete.
Replacement: audit/recompute_log.md
Recommended action: ARCHIVE (intermediate_analyses/)
Estimated saved: 12.8 KB

**[CL-A5] audit/website_discovery.md**
Type: SUPERSEDED
Severity: UNCERTAIN
Reason: Website discovery audit. Mostly absorbed by discovery_audit_2026-05-02.md
+ comprehensive_audit_2026-05-01.md, but contains the canonical site-label
mapping table (line 102) that may not have been folded elsewhere.
Replacement: partial — discovery_audit_2026-05-02.md + comprehensive_audit_2026-05-01.md
Recommended action: NEEDS_REVIEW — diff against discovery_audit_2026-05-02.md
to confirm site-label table preserved before archive.
Estimated saved: 21.7 KB

**[CL-A6] audit/aggregation_locus.md**
Type: KEEP
Severity: DO_NOT_TOUCH
Reason: Compact (2.6 KB) reference doc explicitly cited by
recompute_log.md and load-bearing for the "two-paths must stay in sync"
gotcha. Not superseded.
Recommended action: KEEP

**[CL-A7] audit/comprehensive_audit_2026-05-01.md**
Recommended action: KEEP — latest comprehensive audit (65 KB, May 2 mtime).

**[CL-A8] audit/discovery_audit_2026-05-02.md**
Recommended action: KEEP — latest discovery audit (103 KB).

**[CL-A9] audit/group_a_completion.md, recompute_log.md, rq_restructuring.md, methodology_continuity.md, literature_comparison.md, limitations_disclosures.md, personal_todo_status.md**
Recommended action: KEEP — all live deliverables (poster-ready text or
active trackers).

**[CL-A10] audit/cleanup_audit_2026-05-02.md** (this file)
Recommended action: KEEP — execution input for the archival pass.

### Category B — scripts/ folder

**[CL-B1] scripts/__pycache__/**
Type: BUILD_ARTIFACT
Severity: SAFE
Reason: Python bytecode cache. Should be gitignored already (`__pycache__/`
is in .gitignore). Local-only artifact.
Recommended action: ARCHIVE → just `rm -rf` (no archive needed; reproducible).
Estimated saved: variable (~50 KB)

**[CL-B2] scripts/_oneoff_rejudge_vb04_mistral.py**
Type: OBSOLETE (intentionally)
Severity: UNCERTAIN
Reason: Self-documents as "One-off: re-judge VB_04/mistral". Day-2 audit
recommends adapting it for a NEW errored record (STATIONARY_01_numerical).
If that adaptation has been done elsewhere — archive. If still needed as
a template for the new fix — keep.
Replacement: none if pending; depends on whether STATIONARY_01_numerical
re-judge has been performed.
Recommended action: NEEDS_REVIEW — check whether the STATIONARY_01_numerical
errored record has been re-judged (search perturbation_judge_scores.jsonl
for run_id ea451f6b…). If yes, archive both this script + day2 audit's
[H-3] item. If no, KEEP.
Estimated saved: 5.0 KB

**[CL-B3] scripts/combined_pass_flip_inventory.md**
Type: INTERMEDIATE
Severity: SAFE
Reason: Pre-flight inventory document for combined_pass_flip_analysis.py.
The analysis is complete and shipped (Phase 1.5). Inventory was a planning
artifact, not a consumer-facing doc.
Replacement: none required (work product).
Recommended action: ARCHIVE (intermediate_analyses/)
Estimated saved: 2.6 KB

**[CL-B4] scripts/perturbation_generator_plan.md**
Type: INTERMEDIATE
Severity: LIKELY_SAFE
Reason: Planning doc for generate_perturbations_full.py, completed work.
Still cited in vault sprint log — citation will rot on archive but is
acceptable provenance loss.
Replacement: scripts/generate_perturbations_full.py (the implementation).
Recommended action: ARCHIVE (intermediate_analyses/)
Estimated saved: 21.3 KB

**[CL-B5] scripts/self_consistency_proxy.py**
Type: SUPERSEDED
Severity: LIKELY_SAFE
Reason: B3-stratified self-consistency analysis. Phase 1C explicitly
supersedes this with self_consistency_full.py; B3 outputs already moved
to llm-stats-vault/90-archive/phase_1c_superseded/. The proxy script
itself was left behind.
Replacement: scripts/self_consistency_full.py (canonical).
Recommended action: ARCHIVE — move alongside the existing
phase_1c_superseded/ directory inside vault, OR to scripts/_archive/ if
preferred.
Estimated saved: 25.6 KB

**[CL-B6] scripts/inspect_judge_strictness.py**
Type: INTERMEDIATE
Severity: UNCERTAIN
Reason: One-shot judge-strictness verifier used in Day-1. Reads
llm_judge_scores_sample.jsonl (also a candidate for archive). Could be
needed again if judge methodology is challenged in poster review.
Recommended action: NEEDS_REVIEW — keep until poster delivered (May 8),
then archive.
Estimated saved: 7.1 KB

**[CL-B7] scripts/recompute_scores.py**
Type: KEEP (legacy v1 path)
Severity: DO_NOT_TOUCH
Reason: Backfills v1 runs.jsonl C+R scores. Still referenced by vault
patterns ("Adding a new task type") and decision notes. Reproducibility
guard: deleting it would break the documented workflow.
Recommended action: KEEP

**[CL-B8] All other scripts (analyze_errors, bootstrap_ci, calibration_analysis,
combined_pass_flip_analysis, dedup_runs, error_taxonomy, generate_group_a_figures,
generate_perturbations_full, keyword_degradation_check, keyword_vs_judge_agreement,
krippendorff_agreement, plot_self_consistency_calibration, recompute_downstream,
recompute_nmacr, refresh_pipeline.sh, robustness_analysis, score_perturbations,
self_consistency_full, summarize_results, three_rankings_figure, tolerance_sensitivity,
analyze_perturbations)**
Recommended action: DO_NOT_TOUCH — canonical research pipeline.

### Category C — experiments/results_v2/ folder

**[CL-C1] experiments/results_v2/llm_judge_scores_full.log**
Type: BUILD_ARTIFACT
Severity: SAFE
Reason: 2.1 KB log output from the judge run. No code consumer.
Replacement: judge results captured in llm_judge_scores_full.jsonl.
Recommended action: ARCHIVE (intermediate_analyses/) or simply delete.
Estimated saved: 2.1 KB

**[CL-C2] experiments/results_v2/llm_judge_scores_sample.jsonl**
Type: SUPERSEDED
Severity: LIKELY_SAFE
Reason: Sample subset (11 KB). Only consumer is inspect_judge_strictness.py
(also flagged UNCERTAIN at CL-B6). Full file (llm_judge_scores_full.jsonl)
contains the canonical 1230 records.
Replacement: llm_judge_scores_full.jsonl.
Recommended action: ARCHIVE (intermediate_analyses/) — bundled with
inspect_judge_strictness.py decision.
Estimated saved: 11.2 KB

**[CL-C3] experiments/results_v2/top_disagreements_assumption.json**
Type: INTERMEDIATE
Severity: UNCERTAIN
Reason: 29 KB. Generated by keyword_vs_judge_agreement.py. Not consumed
by any /api/v2 endpoint or frontend. May be useful as appendix for poster
discussion of disagreement examples. No active consumer found.
Recommended action: NEEDS_REVIEW — confirm no poster section pulls
specific examples from it; if not, archive.
Estimated saved: 28.5 KB

**[CL-C4] experiments/results_v2/llm_judge_scores_full.jsonl, nmacr_scores_v2.jsonl,
per_dim_calibration.json, perturbation_judge_scores.jsonl, perturbation_runs.jsonl,
self_consistency_runs.jsonl, error_taxonomy_v2_judge.jsonl, all V2_FILES dict entries**
Recommended action: DO_NOT_TOUCH — canonical research data; consumed by
v2_routes endpoints, recompute scripts, or frontend MethodologyPanels.

### Category D — report_materials/figures/ folder

**[CL-D1] report_materials/figures/calibration_ece_ranking.png**
Type: SUPERSEDED
Severity: LIKELY_SAFE
Reason: Not in capstone-website/frontend/public/visualizations/png/v2/
mirror, not referenced by visualizations.js. Older calibration view
superseded by self_consistency_calibration.png + a5b_per_dim_calibration.png.
Replacement: self_consistency_calibration.png (verbalized + consistency
two-panel layout).
Recommended action: ARCHIVE (intermediate_analyses/)
Estimated saved: 119 KB (modest)

**[CL-D2] report_materials/figures/tolerance_sensitivity.png**
Type: PAPER_ONLY
Severity: UNCERTAIN
Reason: Not mirrored to frontend, not in visualizations.js. Could be
deliberately paper-only (tolerance sweep is a methodology robustness
check appropriate for paper appendix, not website).
Recommended action: NEEDS_REVIEW — confirm whether poster/main.tex pulls
this figure. If yes KEEP; if no archive.
Estimated saved: 132 KB

**[CL-D3] All other report_materials/figures/*.png**
Recommended action: DO_NOT_TOUCH — mirrored to frontend or referenced in
visualizations.js (verified by `diff`).

### Category E — capstone-website/backend/static_data/

**[CL-E1] static_data/experiments/results_v2/ (13 files)**
Recommended action: DO_NOT_TOUCH — Group A refresh just rewrote these.
All files mirror canonical results_v2/ files. No backups, no .old, no
phase-1A leftovers. Healthy.

**[CL-E2] static_data/data/benchmark_v1/tasks_all.json + static_data/data/synthetic/perturbations_all.json**
Recommended action: DO_NOT_TOUCH — Render Docker bundle inputs.

**[CL-E3] static_data/llm-stats-vault/40-literature/papers/ (15 papers)**
Recommended action: DO_NOT_TOUCH — Render bundle for /api/v2/literature.

### Category F — vault consolidation

#### F-merge: sprint logs to consolidate

**[CL-F1] llm-stats-vault/sessions/ (13 sprint files, 38 KB total)**
- 2026-04-26-benchmark-completion-and-r-report.md (3.2 KB)
- 2026-04-26-error-taxonomy-pipeline.md (4.5 KB)
- 2026-04-26-research-gap-closures-and-roadmap.md (4.6 KB)
- 2026-04-26-vault-creation-and-workflow-setup.md (1.9 KB)
- 2026-04-27-user-study-and-deployment.md (4.2 KB)
- 2026-04-27-website-ui-viz-overhaul.md (3.6 KB)
- 2026-04-28-ui-fixes-part3.md (2.7 KB)
- 2026-04-28-ui-fixes-part4.md (3.1 KB)
- 2026-04-28-ui-overhaul-part2.md (2.4 KB)
- 2026-04-30-ui-session30b.md (2.8 KB)
- 2026-04-30-ui-session30c.md (1.5 KB)
- 2026-04-30-ui-session30d.md (1.8 KB)
- 2026-04-30-ui-viz-session29e.md (2.3 KB)

**[CL-F2] llm-stats-vault/90-archive/ existing sprint logs (2 files, 55 KB)**
- 2026-04-30-day1-poster-sprint.md (42 KB — heaviest)
- 2026-05-01-day3-literature-vault.md (13 KB)

**Sprint-log merge plan:**
- Source files to merge: 15 (13 sessions/ + 2 90-archive/)
- Total source size: ~93 KB
- Target: llm-stats-vault/90-archive/sprint-history-aggregated.md
- Structure: chronological by date, each source file becomes one
  `## YYYY-MM-DD — <topic>` section with original frontmatter line preserved.
- After merge verification, originals get archived to
  llm-stats-vault/90-archive/_originals/ (preserved for provenance) OR
  deleted if user prefers (per "aggressive consolidation" direction).

#### F-duplicates

**[CL-F3] llm-stats-vault/00-home/index.md**
Type: STALE
Severity: UNCERTAIN
Reason: Contains stale leaderboard ("Claude 0.683 > Mistral 0.644")
which is the equal-weight Phase 1A ranking. Phase 1B literature-weighted
ranking is gemini → claude → chatgpt → mistral → deepseek. Not a
duplicate per se but actively misleading.
Recommended action: NEEDS_REVIEW — refresh leaderboard table to Phase 1B
numbers OR collapse into research-narrative.md and archive index.md.

**[CL-F4] llm-stats-vault/00-home/current-priorities.md**
Type: STALE
Severity: UNCERTAIN
Reason: Roadmap status as of 2026-04-27. Phase 1B/1C/1.5 work post-dates it.
Recommended action: NEEDS_REVIEW — refresh OR mark as historical and
archive.

**[CL-F5] llm-stats-vault/knowledge/decisions/all-scoring-weights-are-equal-at-0.20.md**
Type: PARTIALLY_SUPERSEDED
Severity: UNCERTAIN
Reason: Decision note still describes equal weighting as canonical.
Phase 1B introduced literature_v1 weighting in a parallel script
(recompute_nmacr.py). The two are reconciled per recompute_log.md §"Scope
and rationale" — equal weights remain authoritative for the two canonical
paths (response_parser.py + metrics.py); literature weights are post-hoc
in recompute_nmacr.py. Note is technically correct but invites confusion.
Recommended action: NEEDS_REVIEW — append a "See also: Phase 1B
literature_v1 reweighting" pointer instead of archiving.

#### F-empty / stub

**[CL-F6] llm-stats-vault/inbox/README.md**
Recommended action: KEEP — legitimate workflow stub (615 bytes).

**[CL-F7] llm-stats-vault/.obsidian/**
Recommended action: KEEP (DO_NOT_TOUCH) — Obsidian config.

**[CL-F8] llm-stats-vault/knowledge/{patterns,debugging,business,decisions,integrations}/ (24 small note files, ~40 KB)**
Recommended action: KEEP — all small atomic knowledge notes.

**[CL-F9] llm-stats-vault/atlas/ (4 architecture notes)**
Recommended action: KEEP — system architecture reference.

**[CL-F10] llm-stats-vault/40-literature/ (citation-map, README, poster-citations + 15 paper notes + textbooks)**
Recommended action: KEEP — active deliverables.

### Category G — repo root cleanup

**[CL-G1] /website/ (legacy Flask app)**
Type: SUPERSEDED
Severity: LIKELY_SAFE
Reason: Flask backend predating capstone-website/ FastAPI rewrite. Last
touched April 17, untouched since the React migration. Self-described as
"Flask backend for the LLM Bayesian Benchmark website" — superseded by
capstone-website/backend/.
Replacement: capstone-website/backend/ (FastAPI) + capstone-website/frontend/
(React + Vite).
Recommended action: ARCHIVE (90-archive/legacy_flask_website/) — keep as
provenance.
Estimated saved: ~30 KB (app.py + static/ + templates/)

**[CL-G2] /research_questions.md**
Type: SUPERSEDED
Severity: LIKELY_SAFE
Reason: Original RQ definitions. Phase 1B reframed RQ structure
(rq_restructuring.md + research-narrative.md §3). Original kept around
for proposal-trace provenance.
Replacement: audit/rq_restructuring.md + llm-stats-vault/00-home/research-narrative.md.
Recommended action: ARCHIVE (90-archive/proposal_provenance/) — preserve
for IEEE paper history.
Estimated saved: 3.1 KB

**[CL-G3] /bayesian_scope.md**
Type: STALE
Severity: UNCERTAIN
Reason: Phase 1+2 scope doc. Content overlaps with research-narrative.md
§1 + CLAUDE.md §Tasks. May still be useful as a short scope reference.
Recommended action: NEEDS_REVIEW — decide whether to fold into
research-narrative.md or keep as a focused scope doc.
Estimated saved: 5.1 KB if archived

**[CL-G4] /logs/self_consistency_full.stdout.log**
Type: DUPLICATE
Severity: SAFE
Reason: Byte-identical to logs/self_consistency_full.log (verified via
diff -q — files match). One is a redirect of the other.
Replacement: keep logs/self_consistency_full.log (canonical name).
Recommended action: ARCHIVE or rm — pure duplicate.
Estimated saved: 7.4 KB

**[CL-G5] /logs/self_consistency_full.log**
Recommended action: KEEP one copy (small, useful run trace).

**[CL-G6] /logs/score_perts/ (6 model logs, ~370 KB total)**
Type: BUILD_ARTIFACT
Severity: LIKELY_SAFE
Reason: Per-model run logs from score_perturbations.py. Useful for debug
in the day they were generated; not consumed by any pipeline. Already
predate the Group A refresh.
Recommended action: ARCHIVE (intermediate_analyses/run_logs/) or rm.
Estimated saved: ~370 KB

**[CL-G7] /poster/main.tex + /poster/literature_comparison.tex + /poster/README.md**
Recommended action: KEEP — ACTIVE poster deliverable (May 8 deadline).

**[CL-G8] /experiments/results_v2/{combined_pass_flip_analysis.json,
keyword_degradation_check.json, nmacr_scores_v2.jsonl, per_dim_calibration.json}**
(repo-root mirror added in commit c033e8e for Render workaround)
Type: WORKAROUND
Severity: DO_NOT_TOUCH (until D-5 resolves canonical path)
Reason: These are not duplicates per se — they ARE the canonical files
that Render reads (per Group A discovery: env=python so DATA_ROOT defaults
to repo root, not static_data/). Removing them would break production.
Replacement: gated on D-5 design decision (canonical = static_data/ vs
repo-root experiments/).
Recommended action: KEEP for now. ARCHIVE_TO_HISTORY in
90-archive/repo_root_data_mirror/ ONLY AFTER D-5 reconciles paths.
Disk size when eventually moved: 1.6 MB.

**[CL-G9] /.DS_Store, /.Rhistory**
Recommended action: KEEP — gitignored already; harmless local files.

**[CL-G10] /.planning/, /.pytest_cache/, /.ruff_cache/, /.venv/, /.vercel/, /.claude/, /.vscode/, /.idea/**
Recommended action: KEEP — gitignored config / build dirs.

**[CL-G11] /CLAUDE.md, /requirements.txt, /.env.example, /.gitignore**
Recommended action: KEEP — canonical project files.

---

## Recommended archive structure

```
llm-stats-vault/90-archive/
├── _originals/                      (pre-merge sprint logs, post-merge)
├── repo_root_data_mirror/           (Group G CL-G8: Render workaround
│                                     files — moved AFTER D-5 only)
├── audit_history/                   (CL-A2 day2_audit, CL-A3 deployment_report,
│                                     CL-A5 website_discovery if reviewed,
│                                     potentially CL-F4 current-priorities)
├── intermediate_analyses/           (CL-A1 headline_500_diagnosis,
│                                     CL-A4 gemini_verification, CL-B3
│                                     combined_pass_flip_inventory, CL-B4
│                                     perturbation_generator_plan, CL-B5
│                                     self_consistency_proxy, CL-C1
│                                     llm_judge_scores_full.log, CL-C2
│                                     llm_judge_scores_sample.jsonl,
│                                     CL-D1 calibration_ece_ranking.png,
│                                     CL-G6 run_logs/)
├── legacy_flask_website/            (CL-G1)
├── proposal_provenance/             (CL-G2 research_questions.md)
├── phase_1c_superseded/             (already exists)
├── sprint-history-aggregated.md     (merged CL-F1 + CL-F2)
└── README.md                        (existing — update to explain new
                                     subdirs)
```

## Execution sequence (run AFTER Group C verification)

1. Create archive subdirectory structure under
   llm-stats-vault/90-archive/.
2. Merge sprint logs (CL-F1 + CL-F2) into
   llm-stats-vault/90-archive/sprint-history-aggregated.md, preserving
   chronological order and original frontmatter as section dividers.
3. Verify merged content covers all 15 source files (count headings,
   spot-check a few decisions are preserved).
4. Move SAFE items to archive subdirs in this order:
   - CL-A1 → audit_history/intermediate_analyses/
   - CL-A2, CL-A3 → audit_history/
   - CL-A4, CL-B3, CL-B4, CL-B5, CL-C1, CL-C2, CL-D1 → intermediate_analyses/
   - CL-G1 → legacy_flask_website/
   - CL-G2 → proposal_provenance/
   - CL-G4 → just rm (duplicate)
   - CL-G6 → intermediate_analyses/run_logs/
   - CL-B1 (__pycache__) → just rm
5. Move LIKELY_SAFE items only after spot-checking each.
6. Move CL-F1 + CL-F2 originals to _originals/ AFTER merge target verified.
7. Update llm-stats-vault/90-archive/README.md to explain new subdirs.
8. Verify no broken references after archival:
   ```
   for f in <archived files>; do
     grep -rn "$(basename $f)" --include="*.py" --include="*.js" \
       --include="*.jsx" --include="*.md" --include="*.json" \
       --exclude-dir=90-archive 2>/dev/null
   done
   ```
9. Commit + push:
   ```
   git commit -m "Cleanup: archive superseded audit docs, intermediate
   analyses, legacy flask website, and merged sprint logs (saves ~1 MB,
   reduces cognitive surface area)"
   ```

## Items deferred to manual review (UNCERTAIN bucket)

- **CL-A5** website_discovery.md — diff against discovery_audit_2026-05-02.md
  before archive; site-label table may be unique.
- **CL-B2** _oneoff_rejudge_vb04_mistral.py — gated on whether
  STATIONARY_01_numerical re-judge has happened.
- **CL-B6** inspect_judge_strictness.py — keep until poster delivered;
  archive after May 8.
- **CL-C3** top_disagreements_assumption.json — confirm no poster section
  references specific examples.
- **CL-D2** tolerance_sensitivity.png — confirm whether poster/main.tex
  pulls this figure.
- **CL-F3** vault index.md — refresh leaderboard OR collapse into
  research-narrative.md.
- **CL-F4** current-priorities.md — refresh post-Phase-1B/1C/1.5 OR
  archive as historical.
- **CL-F5** all-scoring-weights-are-equal-at-0.20.md — append "See also"
  pointer, do not archive (still factually correct for canonical paths).
- **CL-G3** bayesian_scope.md — fold into research-narrative.md or keep
  as focused scope doc.

## Items NOT touched (DO_NOT_TOUCH bucket)

- All canonical research scripts (CL-B7, CL-B8) — reproducibility guard.
- All V2_FILES-referenced JSONs in experiments/results_v2/ — production
  endpoints depend on them.
- llm_judge_scores_full.jsonl — input to 6 scripts.
- nmacr_scores_v2.jsonl + per_dim_calibration.json — Phase 1B canonical
  outputs consumed by frontend Methodology panels.
- All static_data/ files (CL-E1, CL-E2, CL-E3) — Render bundle.
- All report_materials/figures/ files mirrored to frontend or referenced
  in visualizations.js (CL-D3) except the two flagged in CL-D1, CL-D2.
- repo-root experiments/results_v2/ Render workaround mirror (CL-G8) —
  gated on D-5 path cleanup (deferred design decision).
- Vault knowledge/, atlas/, 40-literature/, .obsidian/ — active reference.
- /poster/ — May 8 deliverable.
- /.gitignore, /CLAUDE.md, /requirements.txt — canonical config.

---

## Cross-checks performed

- v2_routes.py V2_FILES dict cross-checked against experiments/results_v2/
  contents — confirmed 13 entries; nmacr_scores_v2.jsonl + per_dim_calibration.json
  not in V2_FILES but consumed by frontend MethodologyPanels.jsx static data.
- visualizations.js manifest cross-checked against frontend mirror —
  18/18 PNGs match.
- frontend mirror cross-checked against report_materials/figures/ —
  exactly 2 figures present in source not mirrored
  (calibration_ece_ranking.png + tolerance_sensitivity.png — both
  flagged).
- All scripts cross-checked for cross-references via `grep` —
  6 SUPERSEDED/INTERMEDIATE candidates surfaced.
- Sprint log inventory: 13 in sessions/ + 2 in 90-archive/ = 15 source
  files for merge.
- Logs duplicate-detection via `diff -q` confirmed
  self_consistency_full.log == self_consistency_full.stdout.log.

---

## Pre-archival verification results — 2026-05-02

Verifies the four LIKELY_SAFE / UNCERTAIN candidates flagged in this audit
before the archival execution pass. Read-only; no files moved.

### CL-A2 (audit/day2_audit_report.md)

- **D-7 fold status:** PARTIALLY covered in comprehensive. F1.01 carries
  the headline 274/1095 = 25.022% keyword-judge disagreement number and explicitly notes
  the 274/1094 off-by-one in day2; F2.01 covers the 135-task
  CONCEPTUAL/MINIMAX/BAYES_RISK exclusion pattern (P-6 in day2). However,
  D-7's Spearman ρ=0.59 on assumption + near-zero on method_structure
  with the saturation-effect note is NOT in comprehensive — comprehensive
  uses the methodologically-stronger Krippendorff α (0.55) per Park et al.
  (2025) recommendation. Spearman ρ is now superseded by Krippendorff α
  as the canonical inter-rater metric (see methodology_continuity.md).
- **D-8 fold status:** REFERENCE-ONLY in comprehensive. tolerance_sensitivity.json
  is mentioned (lines 533, 1069, 1134) as a data file requiring deploy
  parity, but the analytical specifics (1180 numeric runs, three tolerance
  levels tight/default/loose, `ranking_stable_across_levels=false` finding)
  are NOT folded into comprehensive — only the file's existence is tracked.
- **VERDICT:** **FOLD_FIRST_THEN_ARCHIVE** — D-8's tolerance-sweep finding
  (ranking instability across tolerance levels) is a useful methodology
  disclosure not yet captured in comprehensive. Fold a single sentence
  into comprehensive (e.g., as a new INFO-severity note under Category 5
  or methodology continuity) before archiving day2_audit_report.md. D-7
  is superseded; no fold needed.
- **Content to fold:** "Tolerance sensitivity sweep (tolerance_sensitivity.json):
  1180 numeric-bearing runs across three tolerance levels (tight 0.005/0.025,
  default 0.010/0.050, loose 0.020/0.100). `ranking_stable_across_levels=false`
  — Gemini swings from worst at tight to mid at loose. Cited in
  Methodology page §5 as a methodology-disclosure point; original
  evidence in day2_audit_report.md [D-8]."

### CL-A3 (audit/deployment_report.md)

- **Unique content vs group_a_completion.md:**
  - Day 3 production smoke matrix (8 backend endpoints + 6 frontend assets
    + 1 v1 regression check) — group_a covers Day 4 smoke against
    different commits.
  - **QR code generation runbook** (target URL, file paths for source +
    labeled + site copy, 900×900 px size, version 5, error correction H,
    box size 20 px, 4-module border, 2-inch print recommendation) — not
    in group_a or anywhere else.
  - Bundle size budget (1118.12 kB / gzip 323.55 kB; "acceptable for
    May 8" decision; deferred chunk-split note).
  - Issue 1/2/3 root-cause writeups (env=python vs Docker discovery,
    Render free-tier deploy coalescing, Dockerfile COPY gap) — group_a
    references Issue 1's resolution (commit 016c40a) but does NOT capture
    the diagnostic narrative.
  - Final state table (HEAD commits, figures live counts, References live
    count, Render warm latency).
- **VERDICT:** **KEEP** — deployment_report.md is the canonical Day 3
  deployment runbook + QR generation reference. group_a_completion.md is
  Day 4-specific and does not replace it. Promote out of LIKELY_SAFE bucket.

### CL-G1 (legacy /website/ Flask app)

- **Imports from capstone-website/:** 0
- **Imports from scripts/ + evaluation/ + baseline/:** 0
- **requirements.txt / pyproject.toml / setup.py references:** 0
  (requirements.txt does not exist at repo root; no pyproject.toml; no
  setup.py.)
- **Last git touch:** 2026-04-24 23:27 +0400 ("Initial commit") — never
  modified after initial repo creation. 8 days dormant. Tracked files:
  app.py, static/, templates/.
- **VERDICT:** **SAFE_TO_ARCHIVE** — zero importers across the active
  codebase, untouched since initial commit, fully superseded by
  capstone-website/ stack.

### CL-B2 (scripts/_oneoff_rejudge_vb04_mistral.py)

- **STATIONARY_01_numerical / mistral judge records in
  perturbation_judge_scores.jsonl:** 1 (run_id 4eb425d8…) with
  populated method_structure, assumption_compliance, reasoning_quality,
  reasoning_completeness scores. All 5 STATIONARY_01_numerical records
  (one per model_family) have valid scoring; the deepseek run mentioned
  in the audit (run_id ea451f6b…) is also present and scored.
- **STATIONARY_01_numerical in llm_judge_scores_full.jsonl:** 5 records
  (base benchmark scoring complete).
- **VB_04 / mistral re-judge state:** original errored run_id 0f74e564…
  is present in llm_judge_scores_full.jsonl + nmacr_scores_v2.jsonl —
  the script's own target was successfully re-judged.
- **Script's stated purpose:** one-shot replacement of the VB_04/mistral
  errored judge record with max_tokens=2048 retry. Targeted record is
  fixed; STATIONARY_01_numerical never required re-judge (all 5 model
  records scored cleanly on first pass).
- **VERDICT:** **SAFE_TO_ARCHIVE** — both the script's original target
  (VB_04/mistral) and the candidate "next victim" (STATIONARY_01_numerical)
  are fully scored. Script can be archived as historical one-off; if a
  similar re-judge is needed in future, the pattern is preserved in
  archive.

---

## Updated archival approval list (post-verification)

| Item | Pre-verification status | Post-verification status |
|---|---|---|
| CL-A2 day2_audit_report.md | LIKELY_SAFE | **FOLD_FIRST_THEN_ARCHIVE** (fold D-8 tolerance specifics into comprehensive first) |
| CL-A3 deployment_report.md | LIKELY_SAFE | **KEEP** (unique QR runbook + bundle budget + Day 3 deploy narrative) |
| CL-G1 /website/ | LIKELY_SAFE | **SAFE_TO_ARCHIVE** (0 importers, 8-day dormant) |
| CL-B2 _oneoff_rejudge_vb04_mistral.py | UNCERTAIN | **SAFE_TO_ARCHIVE** (both VB_04 and STATIONARY targets cleanly scored) |

Net effect on Execution sequence (cleanup_audit_2026-05-02.md §"Execution
sequence"):

- Step 4 ("Move SAFE items to archive subdirs"): unchanged — CL-A1 still
  goes to audit_history/intermediate_analyses/.
- Step 4 substep "CL-A2, CL-A3 → audit_history/": REVISE to
  "CL-A2 → audit_history/ AFTER fold; CL-A3 stays in audit/."
- Step 5 ("LIKELY_SAFE items only after spot-checking"): CL-G1 confirmed
  safe; CL-B2 promoted from UNCERTAIN to SAFE.
- Updated archival counts:
  - SAFE / approved for archive this pass: 9 (was 8 SAFE; +CL-B2 from
    UNCERTAIN; -CL-A3 retained; CL-A2 deferred pending fold)
  - Pending FOLD_FIRST: 1 (CL-A2)
  - Promoted to KEEP: 1 (CL-A3)
  - Still UNCERTAIN: 5 (CL-A5, CL-B6, CL-C3, CL-D2, CL-F3, CL-F4 — minus
    CL-B2 which moved to SAFE)

---

## Cleanup Execution Complete — 2026-05-02

### Items archived (preserve in 90-archive/)
- Auto-archive (10):
  - headline_numbers_500_diagnosis.md → intermediate_analyses/
  - gemini_verification.md → intermediate_analyses/
  - combined_pass_flip_inventory.md → intermediate_analyses/
  - perturbation_generator_plan.md → intermediate_analyses/
  - self_consistency_proxy.py → intermediate_analyses/scripts/
  - _oneoff_rejudge_vb04_mistral.py → intermediate_analyses/scripts/
  - llm_judge_scores_full.log → intermediate_analyses/
  - calibration_ece_ranking.png → intermediate_analyses/figures/
  - research_questions.md → proposal_provenance/
  - logs/score_perts/ → intermediate_analyses/run_logs/score_perts/
- Verify-then-archive (2):
  - day2_audit_report.md → audit_history/ (D-8 tolerance folded into comprehensive)
  - website/ → legacy_flask_website/

### Items deleted (no archive)
- scripts/__pycache__/ (build artifact, regeneratable)
- logs/self_consistency_full.stdout.log (verified byte-identical duplicate)

### Sprint logs merged
- 15 source files → llm-stats-vault/90-archive/sprint-history-aggregated.md
- Originals preserved in llm-stats-vault/90-archive/_originals/
- Section count verification: 15/15

### Vault refreshes
- llm-stats-vault/00-home/index.md: leaderboard updated to Phase 1B literature-weighted
- llm-stats-vault/00-home/current-priorities.md: refreshed for May 2 state
- llm-stats-vault/knowledge/decisions/all-scoring-weights-are-equal-at-0.20.md: appended See also pointer to literature_v1

### Cross-reference verification
- Files searched for: 11 archived basenames
- Broken references found in active vault docs: 3 (citation-map.md ×2, paper 12 ×1)
- Broken references fixed: 3 (annotated with archive location)
- References preserved as historical / dated artifacts: comprehensive_audit_2026-05-01.md,
  discovery_audit_2026-05-02.md, website_discovery.md, recompute_log.md, audit/day2 (now archived).
- References in active producer scripts left untouched (calibration_analysis.py
  still writes calibration_ece_ranking.png to its original location — DO_NOT_TOUCH script
  per cleanup_audit CL-B8). The PNG file is archived but will be regenerated if the
  script runs; consumers should rely on self_consistency_calibration.png +
  a5b_per_dim_calibration.png.

### D-8 tolerance fold into comprehensive_audit
- Verified: 2 grep hits in audit/comprehensive_audit_2026-05-01.md.
- Inserted as **[F2.09] Tolerance sensitivity** at end of Category 2 (MAJOR severity).
- Executive summary counts updated: Total findings 32→33; MAJOR 13→14.

### Items deferred
- D-5 Render path cleanup (gated on path resolution design decision)
- CL-G8 repo-root data mirror archival (gated on D-5)
- 5 post-poster UNCERTAIN reviews:
  - CL-A5 (website_discovery.md)
  - CL-B6 (inspect_judge_strictness.py)
  - CL-C2 (llm_judge_scores_sample.jsonl)
  - CL-C3 (top_disagreements_assumption.json)
  - CL-D2 (tolerance_sensitivity.png)
  - CL-G3 (bayesian_scope.md)

### Commit
- Hash: pending (single commit at end of execution)
- Files added/moved/modified: large set (see git status)
- Bytes recovered (approx): ~600 KB active text/scripts + ~370 KB run logs +
  ~120 KB stale figure ≈ ~1.0 MB cognitive surface area reclaimed.

