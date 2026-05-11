# Phase 2 — Proposed reorg plan (no execution)

This plan honors all constraints from the prompt. No moves yet. Read in order: §A new layout → §B per-path table → §C junk sweep → §D move sequence → §E risks.

> **Archival destination convention**: all moves-to-archive go under `llm-stats-vault/90-archive/<category>_legacy/`. Top-level `archive/` no longer exists (removed 2026-05-10).

---

## §A — New top-level layout

```
capstone-llm-stats/
├── paper/                        ← NEW. IEEEtran conference-format LaTeX.
│   ├── main.tex
│   ├── sections/
│   │   ├── 00_abstract.tex
│   │   ├── 01_introduction.tex
│   │   ├── 02_related_work.tex
│   │   ├── 03_methodology.tex
│   │   ├── 04_experimental_setup.tex
│   │   ├── 05_results.tex
│   │   ├── 06_discussion.tex
│   │   ├── 07_threats_to_validity.tex
│   │   └── 08_conclusion.tex
│   ├── figures/                  ← Fresh exports re-rendered from code/visualization/.
│   ├── tables/                   ← LaTeX tables produced from data/processed_data/results_v2/*.json.
│   └── bib/refs.bib
│
├── poster/                       ← UNCHANGED. Historical artifact, stays in place.
├── report_materials/             ← UNCHANGED. R pipeline canonical figure source.
│   └── r_analysis/               (R scripts assume cwd = this dir; do not move)
│
├── code/data_preprocessing/                     ← UNCHANGED. Bayesian/frequentist task generators + solvers.
├── code/capstone_mcp/                 ← UNCHANGED. FastMCP server.
├── code/analysis/                   ← UNCHANGED. Metrics, judge, rubrics, schemas.
├── code/models/                   ← UNCHANGED. 5 model clients + runner + parser.
├── code/scripts/                      ← UNCHANGED. Analysis pipeline (24 .py + 1 .sh).
│
├── data/                         ← UNCHANGED INTERNALLY. Path-stable for ~12 hard-coded callers.
│   ├── benchmark_v1/             (171 tasks)
│   ├── synthetic/                (perturbations: kept where it is)
│   ├── error_taxonomy_results.json   ← scheduled to MOVE → llm-stats-vault/90-archive/data_legacy/
│   └── README.md
│
├── experiments/                  ← UNCHANGED INTERNALLY. results_v1/ + results_v2/ stay path-stable.
│   ├── results_v1/               (runs.jsonl + results.json + rq4_analysis.json)
│   └── results_v2/               (24 result files; 100+ hardcoded callers — DO NOT MOVE)
│
├── capstone-website/             ← UNCHANGED INTERNALLY. Frontend + backend self-contained.
├── llm-stats-vault/              ← UNCHANGED. Obsidian vault.
├── literature/                   ← UNCHANGED. Lecture PDFs + textbooks (already gitignored).
├── llm-stats-vault/90-archive/audit/   ← Moved 2026-05-10 from repo root (was top-level audit/).
├── llm-stats-vault/90-archive/   ← Canonical archive root. Receives newly archived items in Phase 3a/3b.
│   ├── audit/                    (existing)
│   ├── experiments/              (existing)
│   ├── _originals/               (existing)
│   ├── audit_history/            (existing)
│   ├── intermediate_analyses/    (existing)
│   ├── legacy_flask_website/     (existing)
│   ├── phase_1c_superseded/      (existing)
│   ├── proposal_provenance/      (existing)
│   ├── superseded_scripts/       (existing)
│   ├── data_legacy/              ← NEW. data/error_taxonomy_results.json (v1 taxonomy) lands here.
│   ├── results_legacy/           ← NEW. runs.jsonl backups land here.
│   ├── scripts_legacy/           ← NEW. inspect_judge_strictness.py (post-poster, per CL-B6).
│   └── poster_prep_assets/       ← NEW. Random-named poster prep images + how-to PDFs.
├── llm-stats-vault/cleanup/                      ← Temporary planning dir. Survives until paper-ship.
├── llm-stats-vault/logs/                         ← UNCHANGED. self_consistency_full.log.
├── .planning/  .claude/  .vercel/
├── .venv/  .pytest_cache/  .ruff_cache/    ← STALE; .venv stays (gitignored), caches deleted.
├── CLAUDE.md  bayesian_scope.md  requirements.txt
├── .env  .env.example  .gitignore
└── README.md                     ← Optional new top-level README (out of scope here).
```

**Why minimal**: 100+ hard-coded `data/processed_data/results_v2/` paths, 17+ `report_materials/figures/` paths, R pipeline cwd-dependent, backend Docker bundles `static_data/{experiments,data,llm-stats-vault}/`. Wholesale `results/accuracy/`, `results/calibration/`, `results/robustness/` reorg is **deferred to a refactor phase** — it would require touching every script + the website backend + the R pipeline + the Docker build. Not Phase 3.

The new directories that DO appear: `paper/` (entirely new, no path collisions); `llm-stats-vault/90-archive/{data_legacy,results_legacy,scripts_legacy,poster_prep_assets}/` (new sub-dirs receiving moved items). All other top-levels stay untouched.

---

## §B — Per-path action table

Actions: **KEEP-IN-PLACE / MOVE / ARCHIVE / DELETE / INVESTIGATE-FURTHER / NEW**.

### Top-level entries

| Current path | Action | New path | Rationale |
|---|---|---|---|
| `CLAUDE.md` | KEEP-IN-PLACE | — | Source of truth. |
| `requirements.txt` | KEEP-IN-PLACE | — | Build dep. |
| `bayesian_scope.md` | KEEP-IN-PLACE | — | Useful for paper §3 background. Could move to `paper/notes/` later. |
| `.env`, `.env.example`, `.gitignore` | KEEP-IN-PLACE | — | Standard. (`.env.example` needs `TOGETHER_API_KEY=` line — separate fix.) |
| `.Rhistory` | DELETE | — | Empty, junk. Phase 3a. |
| `.DS_Store` (root + `poster/` + `poster/figures/`) | DELETE | — | macOS junk. Phase 3a. |
| `.pytest_cache/` | DELETE | — | Test cache. Already gitignored via `.gitignore`? Verify. Phase 3a. |
| `.ruff_cache/` | DELETE | — | Lint cache. Phase 3a. |
| `.venv/` | KEEP-IN-PLACE | — | Local Python env, gitignored. |
| `.git/`, `.claude/`, `.planning/`, `.vercel/` | KEEP-IN-PLACE | — | Tooling. |
| `code/data_preprocessing/` | KEEP-IN-PLACE | — | Task generators. Path-stable. |
| `code/data_preprocessing/__pycache__/`, `code/data_preprocessing/{bayesian,frequentist}/__pycache__/` | DELETE | — | Phase 3a. |
| `code/capstone_mcp/` | KEEP-IN-PLACE | — | MCP server. |
| `code/capstone_mcp/__pycache__/`, `code/capstone_mcp/tools/__pycache__/` | DELETE | — | Phase 3a. |
| `code/analysis/` | KEEP-IN-PLACE | — | Path-stable. |
| `code/analysis/__pycache__/` | DELETE | — | Phase 3a. |
| `code/models/` | KEEP-IN-PLACE | — | Path-stable. |
| `code/models/__pycache__/` | DELETE | — | Phase 3a. |
| `code/scripts/` | KEEP-IN-PLACE | — | Many internal cross-refs. |
| `code/scripts/__pycache__/` | DELETE | — | Phase 3a. |
| `experiments/` | KEEP-IN-PLACE | — | 100+ hard-coded callers. |
| `experiments/__pycache__/` | DELETE | — | Phase 3a. |
| `data/` | KEEP-IN-PLACE | — | Path-stable. |
| `llm-stats-vault/90-archive/audit/` | KEEP-IN-PLACE | — | Moved 2026-05-10 from repo root. |
| `llm-stats-vault/90-archive/` | KEEP-IN-PLACE | — | Canonical archive root. Receives newly archived items via new sub-dirs `data_legacy/`, `results_legacy/`, `scripts_legacy/`, `poster_prep_assets/`. |
| `llm-stats-vault/cleanup/` | KEEP-IN-PLACE | — | Active planning dir. |
| `poster/` | KEEP-IN-PLACE | — | Historical artifact, do not merge with `paper/`. |
| `poster/scripts/__pycache__/` | DELETE | — | Phase 3a. |
| `report_materials/` | KEEP-IN-PLACE | — | R pipeline, working-dir-sensitive. |
| `literature/` | KEEP-IN-PLACE | — | Already gitignored. |
| `llm-stats-vault/` | KEEP-IN-PLACE | — | Obsidian vault, self-contained. |
| `capstone-website/` | KEEP-IN-PLACE | — | Confirm `frontend/{dist,node_modules}/` already gitignored (✓ — see §E). |
| `capstone-website/backend/__pycache__/` | DELETE | — | Phase 3a. |
| `llm-stats-vault/logs/` | KEEP-IN-PLACE | — | self_consistency_full.log. |
| `paper/` | NEW | — | Phase 4 will scaffold IEEE LaTeX project here. |

### Subpaths flagged in `01_inventory.md` and resolved by 01a–01e

| Current path | Action | New path | Rationale |
|---|---|---|---|
| `data/error_taxonomy_results.json` | ARCHIVE | `llm-stats-vault/90-archive/data_legacy/error_taxonomy_results_v1.json` | Per `01c`: superseded by `data/processed_data/results_v2/error_taxonomy_v2.json`. No code reader except the script that writes it. |
| `data/raw_data/synthetic/perturbations.json` | KEEP-IN-PLACE | — | Per CLAUDE.md Phase 1.8: still required as v1-ID filter source by 5 scripts + website + R pipeline. |
| `data/raw_data/synthetic/perturbations_v2.json` | KEEP-IN-PLACE | — | Per `01e`: zero readers, but it IS the natural output of `code/scripts/generate_perturbations_full.py` (`DEFAULT_OUTPUT`). Leaving it lets the generator be re-run idempotently. Do not archive. |
| `data/raw_data/synthetic/perturbations_v2_sample.jsonl` | ARCHIVE | `llm-stats-vault/90-archive/data_legacy/perturbations_v2_sample.jsonl` | Sample/preview, no live consumer (per `llm-stats-vault/90-archive/audit/cleanup_audit_2026-05-02.md:202` — "Only consumer is inspect_judge_strictness.py"). |
| `data/raw_data/synthetic/perturbations_all.json` | KEEP-IN-PLACE | — | Per `01d`: canonical 473, complete. |
| `data/raw_data/synthetic/build_perturbations.py` | KEEP-IN-PLACE | — | Deprecated per CLAUDE.md but listed there as historical v1 generator; leave for traceability. |
| `data/processed_data/results_v1/runs.jsonl` | KEEP-IN-PLACE | — | Append-only canonical (CLAUDE.md). |
| `data/processed_data/results_v1/runs.jsonl.bak_20260426_211605` | ARCHIVE | `llm-stats-vault/90-archive/results_legacy/runs.jsonl.bak_20260426_211605` | Old backup. Never referenced by code. |
| `data/processed_data/results_v1/runs.jsonl.pre_tier1_20260503_195517` | ARCHIVE | `llm-stats-vault/90-archive/results_legacy/runs.jsonl.pre_tier1_20260503_195517` | Old backup. Never referenced by code. |
| `data/processed_data/results_v1/{results.json, rq4_analysis.json}` | KEEP-IN-PLACE | — | Path-stable. |
| `data/processed_data/results_v2/*` (24 files) | KEEP-IN-PLACE | — | Hard-coded paths in 100+ callers. Do not move. |
| `code/analysis/llm_judge_rubric.py` | KEEP-IN-PLACE | — | Per `01b`: not stale. Together AI Llama 3.3 70B Turbo, code matches docs. |
| `code/scripts/dedup_runs.py` | KEEP-IN-PLACE | — | Per `01e`: called by `refresh_pipeline.sh`. |
| `code/scripts/generate_group_a_figures.py` | KEEP-IN-PLACE | — | Per `01e`: canonical generator for `a1`–`a6` figures. |
| `code/scripts/site_palette.py` | KEEP-IN-PLACE | — | Per `01e`: imported by 14 scripts. |
| `code/scripts/inspect_judge_strictness.py` | ARCHIVE | `llm-stats-vault/90-archive/scripts_legacy/inspect_judge_strictness.py` | Per `01e` + audit `[CL-B6]`: post-poster, no callers, safe to archive. |
| `llm-stats-vault/90-archive/audit/tier1_baseline_20260503_195141/` (4.6M) | KEEP-IN-PLACE | — | Audit baseline (moved 2026-05-10). |
| `llm-stats-vault/90-archive/audit/v1_deprecation_baseline_20260504_001522/` (1.7M) | KEEP-IN-PLACE | — | Same. |
| `poster/IMG_9619.heic` | ARCHIVE | `llm-stats-vault/90-archive/poster_prep_assets/IMG_9619.heic` | Poster prep collateral (phone reference photo). Not paper material. |
| `poster/AUA_ML_RGB_ENG.webp` | ARCHIVE | `llm-stats-vault/90-archive/poster_prep_assets/AUA_ML_RGB_ENG.webp` | University logo asset, poster-prep only. |
| `poster/b7f387de8c767a6fd688a825217c69fc.webp` | ARCHIVE | `llm-stats-vault/90-archive/poster_prep_assets/b7f387de8c767a6fd688a825217c69fc.webp` | Random-named poster prep image. Not paper material. |
| `poster/Poster General rules.pdf` | ARCHIVE | `llm-stats-vault/90-archive/poster_prep_assets/Poster General rules.pdf` | Poster format how-to PDF. Not paper material. |
| `poster/How to prepare a poster By Dr. Sarvazyan.pdf` | ARCHIVE | `llm-stats-vault/90-archive/poster_prep_assets/How to prepare a poster By Dr. Sarvazyan.pdf` | Poster format how-to PDF. Not paper material. |
| `poster/tex/` (empty dir) | DELETE | — | Empty leftover. Phase 3a. |
| `capstone-website/frontend/dist/` (68M) | KEEP-IN-PLACE | — | Build output. Already gitignored (verify in §E). |
| `capstone-website/frontend/node_modules/` (196M) | KEEP-IN-PLACE | — | npm deps. Already gitignored. |

### Top-level code/scripts/ status (post-`01e` resolution)

All 24 `.py` + 1 `.sh` files in `code/scripts/` keep their current paths. None are orphaned except `inspect_judge_strictness.py` (action: ARCHIVE).

---

## §C — Phase 3a: junk sweep (separate sub-plan)

### Files / dirs to delete

```text
# Project __pycache__ (12 dirs)
./code/data_preprocessing/__pycache__/
./code/data_preprocessing/bayesian/__pycache__/
./code/data_preprocessing/frequentist/__pycache__/
./code/capstone_mcp/__pycache__/
./code/capstone_mcp/tools/__pycache__/
./capstone-website/backend/__pycache__/
./code/analysis/__pycache__/
./experiments/__pycache__/
./code/models/__pycache__/
./poster/scripts/__pycache__/
./scripts/__pycache__/
# .venv/ pycaches stay — that's the local env, gitignored.

# Tool caches
./.pytest_cache/
./.ruff_cache/

# macOS junk
./.DS_Store
./poster/.DS_Store
./poster/figures/.DS_Store

# Empty / stale
./.Rhistory                       (empty 0B)
./poster/tex/                     (empty dir)
```

### `.gitignore` additions

Add at top, replacing platform-specific lines that already exist (consolidate):

```gitignore
# macOS
.DS_Store
**/.DS_Store

# Tool caches
.pytest_cache/
.ruff_cache/

# R
.Rhistory
.RData

# Python (already present, ensure global)
__pycache__/
*.pyc
*.pyo
```

Current `.gitignore` already has `__pycache__/`, `.DS_Store`, `.Rhistory` at the top level — but a few `.DS_Store` files slipped into nested dirs. The **`/` nesting matters for git**: `.DS_Store` (no slash) already matches at any depth. Re-confirm by `git check-ignore -v poster/.DS_Store` before deleting.

---

## §D — Phase 3b: reorg moves (ordered)

Each block below is **one git commit**. Use `git mv` only — never `rm -rf`.

### Commit 1 — junk sweep (Phase 3a)

```bash
# Delete __pycache__ dirs (untracked anyway; git rm -r --cached only if tracked)
find . -type d -name __pycache__ -not -path './.venv/*' -exec rm -rf {} +

# Delete tool caches
rm -rf .pytest_cache .ruff_cache

# Delete .DS_Store
rm -f .DS_Store poster/.DS_Store poster/figures/.DS_Store

# Delete empty/stale
rm -f .Rhistory
rmdir poster/tex

# Update .gitignore (manual edit — see §C)

git add .gitignore
git commit -m "chore: sweep __pycache__/.DS_Store/.pytest_cache/.ruff_cache, tighten gitignore"
```

### Commit 2 — create vault archive sub-directories

```bash
mkdir -p llm-stats-vault/90-archive/data_legacy \
         llm-stats-vault/90-archive/results_legacy \
         llm-stats-vault/90-archive/scripts_legacy \
         llm-stats-vault/90-archive/poster_prep_assets
# (No git commit yet — empty dirs aren't tracked. Combined with Commit 3.)
```

### Commit 3 — archive superseded data

```bash
git mv data/error_taxonomy_results.json \
       llm-stats-vault/90-archive/data_legacy/error_taxonomy_results_v1.json
git mv data/raw_data/synthetic/perturbations_v2_sample.jsonl \
       llm-stats-vault/90-archive/data_legacy/perturbations_v2_sample.jsonl

git commit -m "chore(archive): move v1 error taxonomy + perturbation sample to vault/90-archive/data_legacy/

- error_taxonomy_results.json superseded by data/processed_data/results_v2/error_taxonomy_v2.json
  (v1: rule-based 9-class flat; v2: Llama 3.3 70B 4-class hierarchical, n=143 both)
  See llm-stats-vault/cleanup/01c_error_taxonomy_diff.md.
- perturbations_v2_sample.jsonl was a sample preview, no live consumer.
  See llm-stats-vault/cleanup/01e_script_callers.md."
```

### Commit 4 — archive runs.jsonl backups

```bash
git mv data/processed_data/results_v1/runs.jsonl.bak_20260426_211605 \
       llm-stats-vault/90-archive/results_legacy/
git mv data/processed_data/results_v1/runs.jsonl.pre_tier1_20260503_195517 \
       llm-stats-vault/90-archive/results_legacy/

git commit -m "chore(archive): move runs.jsonl backups to vault/90-archive/results_legacy/

Canonical data/processed_data/results_v1/runs.jsonl is append-only and untouched.
Two old timestamped backups (Apr 26, May 03) moved out of the live tree."
```

### Commit 5 — archive post-poster diagnostic script

```bash
git mv code/scripts/inspect_judge_strictness.py \
       llm-stats-vault/90-archive/scripts_legacy/

git commit -m "chore(archive): retire inspect_judge_strictness.py post-poster delivery

No code callers. Per llm-stats-vault/90-archive/audit/cleanup_audit_2026-05-02.md [CL-B6]: keep until poster
delivered; poster shipped 2026-05-07. Destination: vault/90-archive/scripts_legacy/.
See llm-stats-vault/cleanup/01e_script_callers.md."
```

### Commit 6 — archive poster prep collateral

```bash
git mv poster/IMG_9619.heic \
       llm-stats-vault/90-archive/poster_prep_assets/
git mv poster/AUA_ML_RGB_ENG.webp \
       llm-stats-vault/90-archive/poster_prep_assets/
git mv poster/b7f387de8c767a6fd688a825217c69fc.webp \
       llm-stats-vault/90-archive/poster_prep_assets/
git mv "poster/Poster General rules.pdf" \
       llm-stats-vault/90-archive/poster_prep_assets/
git mv "poster/How to prepare a poster By Dr. Sarvazyan.pdf" \
       llm-stats-vault/90-archive/poster_prep_assets/

git commit -m "Archive poster prep collateral (images + how-to PDFs) to vault

Five files moved out of poster/:
  - IMG_9619.heic                              (phone reference photo)
  - AUA_ML_RGB_ENG.webp                        (university logo)
  - b7f387de8c767a6fd688a825217c69fc.webp      (random-named prep image)
  - Poster General rules.pdf                   (format how-to)
  - How to prepare a poster By Dr. Sarvazyan.pdf (format how-to)

Destination: llm-stats-vault/90-archive/poster_prep_assets/. Poster figures,
LaTeX, scripts, web-visuals, and design audits stay in poster/."
```

### Commit 7 — scaffold paper/

(Executes during Phase 4; listed here for completeness.)

```bash
mkdir -p paper/sections paper/figures paper/tables paper/bib
# Create main.tex, IEEEtran.cls, refs.bib stub, 9 section stubs.
git add paper/
git commit -m "feat(paper): scaffold IEEEtran conference paper (stubs only, compiles)"
```

---

## §E — Risks and verification steps

### R1. R pipeline working-directory dependence
- **Risk**: [code/visualization/00_load_data.R:20](code/visualization/00_load_data.R#L20) uses `dirname(dirname(getwd()))` to find project root. Assumes cwd = `code/visualization/`. None of our planned moves change `report_materials/` or `data/processed_data/results_v1/runs.jsonl`.
- **Verification**: After Phase 3, `cd code/visualization/ && Rscript 00_load_data.R` should still produce `data/benchmark_clean.{csv,rds}` in that same dir.

### R2. Backend Docker static bundle
- **Risk**: [capstone-website/backend/Dockerfile:6, 8](capstone-website/backend/Dockerfile) does `COPY static_data/ ./static_data/` and sets `ENV DATA_ROOT=/app/static_data`. The bundle includes copies of `data/`, `experiments/`, `llm-stats-vault/`. We are NOT moving anything that the bundle copies (perturbations.json, perturbations_all.json, runs.jsonl, results.json, results_v2/* all stay put).
- **Verification**: Before Phase 3 ship, `cd capstone-website/backend && docker build -t capstone-backend . && docker run --rm capstone-backend ls /app/static_data/data/processed_data/results_v1/` should show `runs.jsonl + results.json + rq4_analysis.json` (no backups now, since they moved out — but the bundle script copies whatever's in `static_data/data/processed_data/results_v1/` so the prior baked-in copy stays valid). Resync `static_data/` only if backend redeploys.

### R3. Hard-coded `data/processed_data/results_v2/` paths (100+)
- **Risk**: Any move of `data/processed_data/results_v2/` would break: 14+ analysis scripts, `code/analysis/llm_judge_rubric.py`, `capstone-website/backend/v2_routes.py`, R pipeline, llm-stats-vault/90-archive/audit/recompute_log.md cross-refs.
- **Mitigation**: Plan does NOT move these. Future refactor only.
- **Verification**: After Phase 3, dry-run `bash code/scripts/refresh_pipeline.sh --help` (if it has --help) or read its top to ensure no path it touches has moved. `code/scripts/refresh_pipeline.sh` calls `dedup_runs.py` (unmoved), and downstream pipelines all read `experiments/results_v{1,2}/` (unmoved).

### R4. Hard-coded `report_materials/figures/` paths (17+)
- **Risk**: Each figure-generator script writes to `report_materials/figures/<name>.png`.
- **Mitigation**: `report_materials/` not moved.
- **Verification**: `python code/scripts/three_rankings_figure.py` (or similar) should still write to the same path.

### R5. Frontend `dist/` and `node_modules/` gitignore
- **Risk**: `dist/` 68M and `node_modules/` 196M committed by accident.
- **Verification**: `.gitignore` line 31 has `node_modules/`; line 39+ unignores `capstone-website/frontend/public/visualizations/...` but does NOT unignore `dist/`. **`dist/` is implicitly NOT covered by the existing gitignore**, since there's no `dist/` rule. ⚠️ **Need to add `capstone-website/frontend/dist/` to `.gitignore`** as part of Phase 3a junk sweep. Verify with `git check-ignore -v capstone-website/frontend/dist/index.html`.

### R6. Poster scripts output paths
- **Risk**: [poster/scripts/*.py](poster/scripts/) write to `poster/figures/`. We are not moving `poster/`.
- **Verification**: `python poster/scripts/dimension_leaderboard_print.py` should produce `poster/figures/dimension_leaderboard.png` unchanged.

### R7. `data/raw_data/synthetic/perturbations_v2.json` regeneration
- **Risk**: If user later runs `python code/scripts/generate_perturbations_full.py`, it overwrites `data/raw_data/synthetic/perturbations_v2.json`. Plan keeps file in place — not affected.
- **Verification**: N/A — KEEP-IN-PLACE.

### R8. `paper/` collision
- **Risk**: None. `paper/` does not currently exist.
- **Verification**: `ls paper/ 2>&1` returns no such file/directory.

### R9. Audit cross-references to moved files
- **Risk**: `llm-stats-vault/90-archive/audit/recompute_log.md`, `llm-stats-vault/90-archive/audit/cleanup_audit_2026-05-02.md`, etc., reference moved file paths.
- **Mitigation**: Audit docs are historical narratives; broken links inside them are acceptable since they describe past state. NOT updating audit docs in this phase.

### Pre-Phase-3 verification checklist

```bash
# Run after junk sweep, before Phase 3b moves
pytest code/data_preprocessing/frequentist/test_frequentist.py code/capstone_mcp/test_server.py -v   # should pass (53 tests)

# After every Phase 3b commit
git status                                                                       # confirm clean
git log --oneline -5                                                             # confirm new commit present
ls llm-stats-vault/90-archive/{data_legacy,results_legacy,scripts_legacy,poster_prep_assets}/   # confirm files moved

# After all of Phase 3
ruff check .                                                                     # lint stays green
python -c "import json; json.load(open('data/raw_data/synthetic/perturbations_all.json'))" # canonical readable
python -c "import json; json.load(open('data/processed_data/results_v2/error_taxonomy_v2.json'))" # canonical readable

# Optional, expensive
bash code/scripts/refresh_pipeline.sh                                                 # full pipeline dry, only if confidence needed
```

---

## §F — What this plan does NOT do (deferred)

- Top-level `archive/` was removed 2026-05-10. Pre-modernization viz snapshots (`archive/visualizations-pre-*`) were superseded by the v2 results pipeline and not retained in vault; provenance preserved at `llm-stats-vault/cleanup/pre_deletion_archive_snapshot_2026-05-10.tar.gz`. See archival convention note above. (`audit/` moved to `llm-stats-vault/90-archive/audit/` 2026-05-10; pre-move snapshot at `llm-stats-vault/cleanup/pre_audit_migration_snapshot_2026-05-10.tar.gz`.)
- Does not move `data/processed_data/results_v2/` or `report_materials/` contents (would require a 100+-line path refactor across scripts, R pipeline, and backend).
- Does not consolidate `data/raw_data/synthetic/perturbations*.json` filenames (per CLAUDE.md, hard-coded callers exist).
- Does not refactor `code/analysis/llm_judge_rubric.py` Groq → Together docstring lag (cosmetic).
- ~~Does not add `TOGETHER_API_KEY=` to `.env.example`~~ — addressed in pre-Phase-3 adjustments commit (2026-05-10).
- Does not write a top-level `README.md` (out of scope here; will accompany `paper/` in Phase 4 if you want one).

---

End of plan. Awaiting "go" to execute Phase 3a + 3b.
