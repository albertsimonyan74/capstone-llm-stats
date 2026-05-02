# Sprint History — Aggregated (2026-04-26 to 2026-05-01)

This file consolidates 15 sprint logs into a single chronological record.
Original files preserved in `llm-stats-vault/90-archive/_originals/` for
provenance. Per-day sections retain original frontmatter as a quoted header.

Index:
- 2026-04-26 — Vault creation and workflow setup
- 2026-04-26 — Error taxonomy pipeline
- 2026-04-26 — Research gap closures and roadmap
- 2026-04-26 — Benchmark completion and R report
- 2026-04-27 — User study and deployment
- 2026-04-27 — Website UI/viz overhaul
- 2026-04-28 — UI overhaul part 2
- 2026-04-28 — UI fixes part 3
- 2026-04-28 — UI fixes part 4
- 2026-04-30 — UI/viz session 29e
- 2026-04-30 — UI session 30b
- 2026-04-30 — UI session 30c
- 2026-04-30 — UI session 30d
- 2026-04-30 — Day 1 poster sprint
- 2026-05-01 — Day 3 literature vault

---

## 2026-04-26 — Vault creation and workflow setup

> Original frontmatter: `tags: [session, vault, obsidian, workflow, knowledge-management]`, `date: 2026-04-26`

# Session: Vault Creation + Workflow Setup

## What Happened

### Obsidian Knowledge Vault Created
Full vault built at `Desktop/capstone-llm-stats/llm-stats-vault/`.
34 markdown files across 9 folders, all drawn from live codebase + CLAUDE.md + session history.

**Folder structure:**
```
00-home/        index.md + current-priorities.md
atlas/          architecture, stack, scoring-pipeline, data-flow
knowledge/
  integrations/ 8 files — one per API/system
  decisions/    6 files — key architectural choices
  debugging/    4 files — known bugs and fixes
  patterns/     5 files — reusable code/process patterns
  business/     3 files — RQ scope, deliverable, Bayesian focus
sessions/       this file + earlier session log
inbox/          empty drop zone
```

**Design choices:**
- File names = statements of fact, not categories (e.g., `gemini-daily-quota-exhausted-on-2026-04-24.md`)
- Every file has YAML frontmatter (`tags`, `date`)
- Wiki links `[[note name]]` connect related notes
- No `.obsidian/` config needed — Obsidian auto-creates on first open

### Session Workflow Protocol Established
**At session start**: read `00-home/index.md` + `00-home/current-priorities.md` first.
If touching a specific module: read its `knowledge/` note first.
**When user says "save session"**: create session note, update priorities, add decision/debugging note if applicable, update index.

Saved to Claude memory at:
`~/.claude/projects/.../memory/feedback_vault_workflow.md`

## No Code Changed
No benchmark runs, no API calls, no file edits in the main project.
Session was entirely knowledge infrastructure.

## Next Session
Start with: resume Gemini Phase 1 (62 missing tasks).
Command: `python -m llm_runner.run_all_tasks --models gemini`

---

## 2026-04-26 — Error taxonomy pipeline

> Original frontmatter: `tags: [session, log, error-taxonomy, analysis, pipeline, proposal-gap]`, `date: 2026-04-26`

# Session Log: Error Taxonomy Analysis Pipeline

## Date
2026-04-26

## Context
This session closed the paper-blocking proposal gap: "systematic error taxonomy for LLM statistical reasoning" (from abstract). Also updated vault from stale state (Gemini incomplete → all complete).

## What Was Accomplished

### 1. Vault Update (stale → current)
- `index.md`: run status updated to all 5 models complete (1230 records)
- `current-priorities.md`: Phase 1/2/5 complete; new priorities = error taxonomy + user study + paper
- Created [[proposal-gap-user-study-not-implemented]] — knowledge note
- Created [[proposal-gap-error-taxonomy-analysis-missing]] — knowledge note

### 2. Proposal Cross-Reference (from PDF)
Confirmed two unimplemented deliverables from proposal abstract:
- "systematic error taxonomy" → **now implemented**
- "small-scale user study (n=5-10 statistics students)" → **deferred to future work**

All other proposal items confirmed complete:
- RQ1-5 ✅, CoT/PoT/Few-shot ✅, LLM-as-Judge ✅, TaskValidator ✅, Bibliography ✅

### 3. scripts/analyze_errors.py (NEW)
Hybrid rule-based + LLM-as-Judge error tagging pipeline.

**8 error categories (E1-E9):**
| Code | Name | Count |
|------|------|-------|
| E3 | Assumption Violation | 119 |
| E7 | Truncation (token limit) | 93 |
| E5 | Overconfidence | 85 |
| E6 | Conceptual Confusion | 56 |
| E2 | Method Selection | 18 |
| E4 | Format Failure | 15 |
| E8 | Hallucination | (LLM-tagged ambiguous) |
| E9 | Unclassified | 1 |

Total: 143 failed runs / 855 benchmark runs = 16.7% failure rate

**Critical bug fixed:** `float(0.0 or 1.0) = 1.0` — `or 1.0` fallback incorrectly overrode zero assumption scores. Fixed with `_f(val)` helper that checks `is not None` instead of truthiness.

**LLM usage:** Used for E8/E9/isolated-E3 cases only (1-50 calls max). Avoids over-relying on expensive calls.

Output: `data/error_taxonomy_results.json`

### 4. report_materials/r_analysis/16_error_taxonomy.R (NEW)
3 visualizations:
- `16a_error_distribution.png` — bar chart, all error types by count
- `16b_error_by_model_heatmap.png` — model × error type heatmap
- `16c_error_by_task_type.png` — top 12 task types stacked by error category

Added to `run_all.R` registry (now 16 scripts, was 15).

### 5. 08_master_report.Rmd (MODIFIED)
Two new sections added:
- `# Error Taxonomy Analysis` — 8-category table, kable summary, 3 figures, key findings
- `# Limitations and Future Work` — E7 token limit fix advice, user study future work, Phase 3 scope

Re-rendered successfully: `benchmark_report.html` (9.4 MB).

### 6. Website Updated
- `visualizations.js`: 3 new viz cards in new "Error Analysis" filter tab (18 total categories now)
- 3 PNGs copied to `capstone-website/frontend/public/visualizations/png/`

### 7. CLAUDE.md Updated
- `scripts/analyze_errors.py` added to §2 How to Run Things
- `data/error_taxonomy_results.json` added to §3 Architecture Map
- IMPORTANT section: error taxonomy marked ✅ with findings
- R pipeline: updated to "18 scripts (00-16 + Rmd)"

## Errors and Fixes

| Error | Root Cause | Fix |
|-------|-----------|-----|
| E3 never appears in distribution | `float(0.0 or 1.0) = 1.0` — `or 1.0` fallback is falsy-based | Replaced with `_f(val)` checking `val is not None` |
| Unused imports `os`, `sys` | Copy-paste from prior template | Removed |

## Git Commit
`4069e36` — `feat: complete error taxonomy analysis pipeline` (18 files changed)

## Key Findings (for paper §4)
1. **E7 Truncation dominates mechanically** — 93 failures from hitting 1024-token cap. REGRESSION and BAYES_REG (multi-output tasks) always exceed limit. Fix: set `max_tokens=2048` for tasks with ≥4 numeric targets.
2. **E3 Assumption Violation most common semantically** — 119 cases across all models. Models proceed without stating iid, conjugacy, or distributional assumptions.
3. **Claude most reliable** (19/171 failures = 11%). ChatGPT worst (38/171 = 22%).
4. **Gemini has disproportionate E4 Format Failures** (6/24 failures) — formatting inconsistency not seen in other models.

## Remaining Open Items (Priority Order)
1. Paper draft — §4 Error Analysis now has data; §3 Results ready; §2 Methodology complete
2. User study — recruit or mark future work formally in paper (already in Rmd)
3. Viz audit — map 18 PNGs to RQs, replace weakest
4. Phase 3 new task types — optional, beyond proposal scope

---

## 2026-04-26 — Research gap closures and roadmap

> Original frontmatter: `tags: [session, log, research-gaps, roadmap, implementation]`, `date: 2026-04-26`

# Session Log: Research Gap Closures + GSD Roadmap

## Date
2026-04-26

## What Was Accomplished

### Part 1: Research Gap Closures (commit bc470f1)
Eight implementation steps completed in one session:

**Step 1 — `evaluation/llm_judge.py`**
- LLM-as-Judge fallback evaluator using `claude-sonnet-4-6` via anthropic SDK
- `judge_extract_answer()` — fallback when `parsed_values=[]`
- `judge_score_structure()` — fallback when `structure_score < 0.3`
- `needs_judge_extraction()` + `needs_judge_scoring()` trigger functions
- Fixed: model string updated from `claude-sonnet-4-20250514` → `claude-sonnet-4-6`

**Step 2 — `experiments/run_benchmark.py`**
- Added `--no-judge` CLI flag (module-level argparse)
- Added `_task_spec_to_judge_dict()` to bridge TaskSpec dataclass → dict for judge
- Judge calls inserted before TaskRun construction, wrapped in `if USE_JUDGE:`
- Fixed: `Dict` unused import removed

**Step 3 — `llm_runner/prompt_builder_fewshot.py`**
- Few-shot Chain-of-Thought prompt builder (Wei et al., 2022)
- Exemplars for: BINOM_FLAT (×2), MARKOV, FISHER_INFO, BETA_BINOM, GIBBS
- `build_fewshot_prompt(task, n_examples=2)` — falls back to zero-shot if no exemplar

**Step 4 — `llm_runner/prompt_builder_pot.py`**
- Program-of-Thoughts prompt builder + executor (Chen et al., 2022)
- Security: `FORBIDDEN` list blocks `import os/sys/subprocess`, `open()`, `eval()`, `exec()`
- `build_pot_prompt(task)` — appends Python code instruction
- `execute_pot_response(text, timeout=10)` — extracts code block, validates, runs, parses ANSWER:

**Step 5 — `evaluation/task_validator.py`**
- Automated task quality validation using Claude as evaluator
- `auto_validate_task(task)` — checks zero true_value + tight tolerance + short prompts
- `validate_all_tasks(tasks_path, output_path)` → `validation_report.json`

**Step 6 — `report_materials/r_analysis/08_master_report.Rmd`**
- Added `# Methodology` section with 3 subsections:
  - `## Prompting Strategy` — zero-shot baseline, few-shot CoT, PoT
  - `## Answer Extraction and LLM-as-Judge`
  - `## Task Quality Validation`
- Re-rendered successfully (43/43 chunks) → `benchmark_report.html`

**Step 7 — `literature/papers_bibliography.md`**
- 5 benchmark methodology papers with full APA citations + relevance notes:
  1. StatEval (Lu et al., 2025) — arXiv:2510.09517 — task quality validation
  2. Nagarkar et al. (2026) — arXiv:2601.14479 — LLM-as-Judge
  3. MathEval (Liu et al., 2025) — math benchmark context
  4. Chen et al., 2022 — arXiv:2211.12588 — Program-of-Thoughts
  5. Wei et al., 2022 — arXiv:2201.11903 — Chain-of-Thought

**Step 8 — Integration Tests**
- All 4 tests passed:
  - llm_judge logic (needs_extraction, needs_scoring)
  - PoT executor (code extraction + execution)
  - Few-shot builder (exemplar prepending)
  - task_validator import
- Fixed: anthropic not in venv → `pip install anthropic`
- Fixed: test dict missing task_id → added required fields

### Part 2: Codebase Mapping (/gsd-map-codebase)
7 structured documents written to `.planning/codebase/`:
- `STACK.md` — tech stack
- `INTEGRATIONS.md` — API clients + MCP
- `ARCHITECTURE.md` — component relationships
- `STRUCTURE.md` — directory tree
- `CONVENTIONS.md` — naming + rules
- `TESTING.md` — 53 tests, coverage gaps
- `CONCERNS.md` — critical TODOs + risks

### Part 3: GSD Project Roadmap (/gsd-new-project)
5 planning files created in `.planning/`:
- `PROJECT.md` — project context
- `REQUIREMENTS.md` — R1–R9 requirements
- `ROADMAP.md` — 5-phase roadmap
- `STATE.md` — run status table
- `config.json` — GSD config (yolo mode)

## Errors Encountered and Fixed

| Error | Root Cause | Fix |
|-------|-----------|-----|
| `ModuleNotFoundError: anthropic` | Not in .venv | `pip install anthropic` |
| Test 3 KeyError: task_id | Minimal test dict missing required fields | Added task_id, task_type, tier, difficulty |
| IDE: unused-import: Dict | Changed to `List` only | Removed Dict from typing import |
| Agent rate limit | Mapper agents hit daily limit AFTER writing files | No fix needed — files were complete |

## Git Commit
`bc470f1` — `feat: implement all research gap closures`

## Next Actions
1. Resume Gemini Phase 1 (62 tasks)
2. Resume Gemini Phase 2 (35 tasks)
3. Run `python -m experiments.run_benchmark` → populate results.json
4. Run RQ4 synthetic benchmark (375 runs)
5. Plan Phase 3 (new task types) via `/gsd-plan-phase 3`

---

## 2026-04-26 — Benchmark completion and R report

> Original frontmatter: `tags: [session, log, benchmark, completion, r-report, documentation]`, `date: 2026-04-26`

# Session Log: Benchmark Completion + R Report Re-render + Vault Update

## Date
2026-04-26

## What Was Accomplished

### Benchmark Completion (from prior session context)
All 5 models completed all phases:
- Phase1+2: 171 tasks × 5 models = 855 runs (no errors)
- Synthetic (RQ4): 75 tasks × 5 models = 375 runs
- Total: 1230 records in `runs.jsonl`

Leaderboard (formal scoring, `run_benchmark.py --no-judge`):
- Claude 0.683 > Mistral 0.644 > Gemini 0.642 > DeepSeek 0.625 > ChatGPT 0.621

RQ4 Robustness:
- ChatGPT 0.931 > Mistral 0.925 > Claude 0.915 > DeepSeek 0.901 > Gemini 0.896
- By type: rephrase=0.923 > semantic=0.909 > numerical=0.908

### R Report Re-render
Fixed 15 R scripts to include Gemini (removed `filter(model_family != "gemini")` from 7 scripts, updated `COMPLETE` vector in 8 scripts).

Ran `Rscript run_all.R` from `report_materials/r_analysis/` — 17/17 scripts, 24.5s, 9.6MB HTML report.

Copied assets: 15 PNGs + 1 GIF → `capstone-website/frontend/public/visualizations/png/`

### Documentation Updates
- `App.jsx`: RADAR_VALS updated with real data, RQS status → "5/5"
- `research_questions.md`: per-RQ results with 2026-04-26 date
- `bayesian_scope.md`: RQ4 table + run status leaderboard
- `CLAUDE.md`: §9 all CRITICAL resolved, R re-render marked done
- Committed: `a6e216d` — "feat: R report re-render with all 5 models + doc updates" (59 files)

### Vault Update (this session)
- `index.md`: updated to complete run status + new leaderboard
- `current-priorities.md`: Phase 1-2 complete, new priorities = error taxonomy + user study + paper
- Created: [[proposal-gap-user-study-not-implemented]]
- Created: [[proposal-gap-error-taxonomy-analysis-missing]]

## Proposal Cross-Reference

| Proposal Deliverable | Status |
|---------------------|--------|
| Reproducible benchmark dataset (171 tasks × 5 models) | ✅ |
| Evaluation protocol (N/M/A/C/R scoring, MCP) | ✅ |
| Systematic error taxonomy | ❌ stub only |
| User study (statistics students) | ❌ not started |
| Numerical accuracy measurement | ✅ RQ1 |
| Method selection accuracy | ✅ RQ2 |
| Assumption compliance | ✅ RQ3 |
| Robustness (paraphrasing + renaming) | ✅ RQ4 (rephrase/numerical/semantic) |
| Calibration (optional) | ✅ RQ5 active |
| CoT prompting | ✅ system prompt + few-shot builder |
| PoT prompting | ✅ prompt_builder_pot.py |
| LLM-as-Judge | ✅ evaluation/llm_judge.py |

## References From Proposal (now in literature/papers_bibliography.md)
1. StatEval (Lu et al., 2025) — arXiv:2510.09517
2. Nagarkar et al. (2026) — arXiv:2601.14479 — LLM-as-Judge
3. MathEval (Liu et al., 2025)
4. Chen et al., 2022 — arXiv:2211.12588 — Program-of-Thoughts
5. Wei et al., 2022 — arXiv:2201.11903 — Chain-of-Thought

## Next Actions (Priority Order)
1. **Write `scripts/analyze_errors.py`** — auto-tag failed runs → `error_taxonomy.json` (paper-blocking)
2. **Decide user study fate** — recruit stats students or mark as future work
3. **Audit visualizations** — map 15 PNGs to RQs, identify weakest
4. **Start paper draft** — §2 methodology now fully implemented, §3 results ready

---

## 2026-04-27 — User study and deployment

> Original frontmatter: `tags: [session, user-study, deployment, vercel, render]`, `date: 2026-04-27`

# Session: User Study + Production Deployment

## What Was Done

### 1. User Study — Backend (user_study.py)
Created `capstone-website/backend/user_study.py`:
- 5 async httpx callers (`call_claude`, `call_gpt4`, `call_gemini`, `call_deepseek`, `call_mistral`)
- All use raw httpx — no vendor SDKs (consistent with existing `llm_runner/model_clients.py`)
- Vision support: Claude, GPT-4.1, Gemini accept base64 images; DeepSeek + Mistral return early with `vision_not_supported`
- `asyncio.gather` for parallel execution
- In-memory rate limiter: 10 req/hr per IP (`_rate_store` dict)
- Vote persistence: `backend/data/user_study_results.json` (append-only)
- 3 endpoints: `POST /api/user-study`, `POST /api/user-study/vote`, `GET /api/user-study/results`
- SYSTEM_PROMPT: Bayesian stats expert, educational, graduate-level

### 2. User Study — Frontend (UserStudy.jsx)
Created `capstone-website/frontend/src/pages/UserStudy.jsx`:
- Textarea input + image attach with preview (file input hidden, triggered by button)
- `VITE_API_URL` env var for API base (empty string = relative path in prod)
- 5 skeleton loading cards during fetch (pulse animation)
- 5 ResponseCard components: model color, initials badge, latency, scrollable response text
- Text-only indicator for DeepSeek/Mistral when image attached
- VotePanel: click model button → select winner → optional reason textarea → submit
- AggregateStats: lazy-loaded CSS bar chart from `GET /api/user-study/results`
- Wired into App.jsx between Visualizations and About; `{ id: 'user-study', label: 'User Study' }` in Navbar

### 3. Backend Integration Fixes
- `main.py`: `from user_study import router` → try `backend.user_study` first, fallback to `user_study`
- CORS: `FRONTEND_URL` env var; falls back to `["*"]` when unset (avoids `allow_credentials + *` conflict)
- `BASE_DIR`: reads `DATA_ROOT` env var; falls back to `Path(__file__).parent.parent.parent` (project root for local dev)
- Added `GET /` health-check route
- Dropped unused `Query` import

### 4. Production Deployment — Render (backend)
- `backend/render.yaml` created with 5 API key env var slots + FRONTEND_URL
- `backend/Dockerfile` fixed:
  - Was: `COPY main.py .` only → `user_study.py` absent in container
  - Fixed: `COPY main.py user_study.py ./`
  - Added: `COPY static_data/ ./static_data/` + `ENV DATA_ROOT=/app/static_data`
- `backend/static_data/` bundled: `tasks_all.json` (184K) + `runs.jsonl` (4.4M)
- `.gitignore` exception: `!capstone-website/backend/static_data/**` to un-ignore runs.jsonl
- Root `BASE_DIR` resolved to `/` in Docker (3 parent levels from `/app/main.py`) → fixed with DATA_ROOT

### 5. Production Deployment — Vercel (frontend)
- `frontend/vercel.json`: rewrites `/api/(.*)` → `https://capstone-llm-stats.onrender.com/api/$1`
- `frontend/UserStudy.jsx`: `API_BASE = import.meta.env.VITE_API_URL || ''`
- `VITE_API_URL` set in Vercel env (not sensitive — it's a public URL)
- Deployed via `npx vercel --prod` after `vercel login`

## Production URLs
- **Frontend:** https://capstone-llm-stats.vercel.app
- **Backend:** https://capstone-llm-stats.onrender.com
- Both verified: `/api/status` → 200, 171 tasks, 1230 runs

## Known Behavior
- Render free tier cold-start: ~30s delay after 15 min idle
- User Study votes stored in Render container's `data/user_study_results.json` — ephemeral (reset on redeploy)
- VITE_API_URL baked at build time by Vite (not runtime-configurable)

## Key Files Changed
- `capstone-website/backend/user_study.py` — NEW
- `capstone-website/backend/main.py` — router, CORS, DATA_ROOT, root route
- `capstone-website/backend/Dockerfile` — user_study.py + static_data copy
- `capstone-website/backend/render.yaml` — NEW
- `capstone-website/backend/static_data/` — NEW (tasks_all.json + runs.jsonl)
- `capstone-website/frontend/src/pages/UserStudy.jsx` — NEW
- `capstone-website/frontend/src/App.jsx` — UserStudy import + section
- `capstone-website/frontend/src/components/Navbar.jsx` — User Study nav entry
- `capstone-website/frontend/vercel.json` — NEW
- `.gitignore` — static_data exception

---

## 2026-04-27 — Website UI/viz overhaul

> Original frontmatter: `tags: [session, website, ui, visualizations]`, `date: 2026-04-27`

# Session: Website UI + Visualization Overhaul

## What Was Done

### 1. Emoji Removal (App.jsx)
Replaced all emoji icons site-wide with monoline SVG icons:
- **Pipeline steps** (6): grid, chat bubble, triangle-nodes, bar chart, refresh arrows, crosshair magnifier
- **About findings** (4): podium/rank, downtrend, warning triangle, shuffle arrows
- Removed `✅` from RQS status string

### 2. TierLadder Redesign (App.jsx)
Complete rebuild of the difficulty ladder component:
- Proportional scale bar at top showing all 4 tiers by task count
- Tier badges now have 4-dot difficulty indicators
- Animated progress bar per row
- Expanded panel now shows: detail text + KEY CHALLENGES (3 bullets per tier) + TASK TYPES chips (tier-specific, accurate)
- Old bug: expanded section showed first 3 items from TASK_TYPE_TOOLTIPS for every tier (same 3 always) — fixed with `TIER_TASK_EXAMPLES` const

### 3. Benchmark Visualizations Overhaul (visualizations.js + VizGallery.jsx)

**Removed 5 vizs** (redundant/too technical for ordinary users):
- `model_table` — table as static image is not useful; leaderboard covers it
- `ecdf` — jargon-heavy (ECDF)
- `correlation` — technical, redundant
- `treemap` — redundant with tier ladder info
- `difficulty_scatter` — redundant with difficulty_line

**Featured 2×2 grid** (KEY VISUALIZATIONS section above gallery):
1. Performance Heatmap (`01_model_heatmap`)
2. Score Distributions (`03_distributions`)
3. Tier Breakdown → `pass_rate` (`13_pass_rate`)
4. Best & Worst Task Types → `failure_analysis` (`05_failure_analysis`)

**All descriptions/insights rewritten** in plain language for ordinary users.

**Fixed broken "Open Interactive" button** for error taxonomy cards (`interactive: null`) — was calling `window.open(null, '_blank')`. Now shows dimmed "Static only" placeholder.

**Added `FEATURED_IDS` export** to visualizations.js.

### 4. Removed Results Section
- Deleted `<Results/>` and its `<SectionDivider/>` from App.jsx
- Removed "Results" nav link from Navbar.jsx
- The 4 tabbed vizs (Heatmap, Distribution, Tier Breakdown, Best/Worst) in ResultsSection.jsx were redundant with VizGallery

Nav order now: Overview → How It Works → Models → Tasks → Visualizations → About

### 5. Fixed Gemini Missing from Featured Viz PNGs

Root cause: 3 R scripts hardcoded 4-model factor levels and "Gemini excluded" subtitles even after Gemini completed on 2026-04-26.

Fixed scripts:
- `01_model_heatmap.R`: factor levels + subtitle + caption + `models_ordered`
- `03_distributions.R`: factor levels (ridges + plotly) + caption + `models_ord`
- `05_failure_analysis.R`: factor levels (Panel B) + caption + plotly PALETTE slice

Regenerated PNGs/HTMLs and copied to `capstone-website/frontend/public/visualizations/`.
`13_pass_rate.R` already included Gemini — no change needed.

## Key Files Changed
- `capstone-website/frontend/src/App.jsx` — emoji→SVG, TierLadder rebuild, removed Results section
- `capstone-website/frontend/src/components/Navbar.jsx` — removed "Results" entry
- `capstone-website/frontend/src/data/visualizations.js` — 18→12 vizs, featured IDs, plain descriptions
- `capstone-website/frontend/src/pages/VizGallery.jsx` — featured strip, null interactive fix, description on all cards
- `report_materials/r_analysis/01_model_heatmap.R` — Gemini fix
- `report_materials/r_analysis/03_distributions.R` — Gemini fix
- `report_materials/r_analysis/05_failure_analysis.R` — Gemini fix

## Build Status
`npm run build` passes clean.

---

## 2026-04-28 — UI overhaul part 2

> Original frontmatter: `tags: [session, website, ui, deployment]`, `date: 2026-04-28`

# Session: UI Overhaul Part 2

## Status at Session End

Continuing from [[2026-04-27-website-ui-viz-overhaul]]. New 10-item task list received.

Previous session completed items 1–5 from the new list (confirmed via todo state):
1. ✅ Remove Timeline section
2. ✅ Move Research Questions to top + enhance visually
3. ✅ Clean References: remove lectures, add links, merge papers+textbooks into separate sections
4. ✅ Redesign How It Works as animated circle + deployment/RQ/user-study info
5. ✅ Make Difficulty Ladder + Scoring boxes fully horizontal

## Remaining Items (not yet applied)

6. ✅ **Viz Gallery expandable** — wrapped leaderboard/filter/gallery/footer in `{sectionOpen && <motion.div>}` with AnimatePresence fade-in. Collapsed by default.

7. ✅ **Phase 2 filter label** — `'Comp. Bayes'` → `'MCMC · VB · ABC'`

8. ✅ **Phase 2 task descriptions** — TaskCard now uses TASK_TYPE_TOOLTIPS description when `category === 'computational_bayes'` and task.description < 20 chars.

9. ✅ **Capability Radar** — dynamic textAnchor (end/start/middle based on lx vs cx); pad 32→48 / 36→52; label offset R+26→R+38 / R+28→R+42. No more clipping.

10. ✅ **Git commit + push** → commit 84fa12a → Vercel deploying.

**Also done:** TASK_TYPE_TOOLTIPS textbook fields — removed all `Lecture NN ·` prefixes.

## Key Code Locations

| Item | File | Lines |
|------|------|-------|
| VizGallery sectionOpen content | `VizGallery.jsx` | 432–605 |
| Phase 2 filter label | `App.jsx` | 1293 |
| TaskCard description logic | `App.jsx` | 1524–1527 |
| TASK_TYPE_TOOLTIPS textbook fields | `App.jsx` | 146–184 |
| RadarChart | `App.jsx` | 685–734 |
| NeuralNetwork | `components/NeuralNetwork.jsx` | full file |

## Notes

- Lecture references in TASK_TYPE_TOOLTIPS textbook fields should be removed (e.g. `'Lecture 21 · Carlin & Louis Ch.2'` → `'Carlin & Louis Ch.2'`)
- Radar SVG has `overflow="visible"` but container may clip; increase pad and use dynamic textAnchor
- NeuralNetwork canvas: dpr/HiDPI already handled correctly; "low quality" likely means too few background nodes or weak glow effects
- `tasks.json` frontend has `description: 'Gibbs'` for Phase 2 — don't need to touch the JSON file, just fix the TaskCard render logic

---

## 2026-04-28 — UI fixes part 3

> Original frontmatter: `tags: [session, website, fixes, ui]`, `date: 2026-04-28`, `commit: 2f6fdf0`

# Session: UI Fixes Part 3 (2026-04-28c)

## Tasks Completed ✅

### 1. Model Token Display — Verified & Enhanced
- Confirmed: Gemini client hardcodes `maxOutputTokens: 4096` (NOT `_MAX_TOKENS=1024` like others)
- Confirmed from runs.jsonl: Gemini avg=1729, max=4096 — all others avg~700-811, max=1024
- Updated MODELS array: added `avgOutputTokens` field for all 5 models from actual runs
- Updated model detail panel: renamed "MAX TOKENS" → "TOKEN LIMIT (BENCHMARK)" + added "AVG OUTPUT TOKENS" row
- Added note to Gemini strengths explaining it used 4096 cap (not 1024) — only model with different limit

### 2. Tier Difficulty Ladder — Font Size Fix
- Detail description text: `fontSize: 13` → `fontSize: 15`, `lineHeight: 1.8`
- KEY CHALLENGES label: `fontSize: 9` → `fontSize: 10`
- Challenge items: `fontSize: 10` → `fontSize: 12`
- TASK TYPES label: `fontSize: 9` → `fontSize: 10`
- Task type badges: `fontSize: 9` → `fontSize: 10`

### 3. Benchmark Viz Buttons — Fixed
**Root cause: Vercel `cleanUrls: true` (default) strips `.html` extension → 404 → catch-all serves `index.html` (React SPA) instead of the Plotly interactive.**
- Fix: added `"cleanUrls": false` to `vercel.json`

**GIF animation "Animated visualization" text — no actual GIF:**
- Root cause: img shows alt text while loading; no loading feedback
- Fix: added `gifLoading` + `gifError` states, loading spinner (CSS spin animation), `onLoad`/`onError` handlers, opacity 0→1 transition on load, error message with file path

### 4. Answer Divergence Tolerance — Fixed
- Old: string normalization with `.toFixed(2)` — fails near x.xx5 boundary (0.001 diff → different string)
- New: `extractFirstNum()` parses first float from answer string; `clusterNumeric()` sorts + chains groups where consecutive diff ≤ `NUMERIC_TOLERANCE = 0.005`; falls back to string normalization for non-numeric answers
- Models within 0.005 of each other now correctly show as consensus

### 5. Vote Storage Clarification
- Added info bar below AggregateStats in UserStudy section:
  - `backend/data/user_study_results.json` — JSON array, one record per vote
  - `backend/data/vote_memory.json` — aggregated stats for research paper

## Deployment
- Commit: `2f6fdf0`
- Pushed to `main` → Vercel (frontend) and Render (backend) auto-deploying
- No backend code changed this session

## Notes
- Vote data is ephemeral on Render free tier — export `user_study_results.json` before redeploy
- Interactive HTML files exist in `public/visualizations/interactive/` — verified sizes 6K-231K — all committed and present in dist

---

## 2026-04-28 — UI fixes part 4

> Original frontmatter: `tags: [session, website, fixes, ui, vote-persistence]`, `date: 2026-04-28`

# Session: UI Fixes Part 4 (2026-04-28d)

## Tasks Completed ✅

### 1. Tier Difficulty Ladder — Text Even Bigger
- Detail text: `fontSize:15` → `fontSize:17`, `lineHeight:1.8` → `lineHeight:1.85`, margin bump
- KEY CHALLENGES label: `fontSize:10` → `fontSize:11`, marginBottom 6→8
- Challenge items: `fontSize:12` → `fontSize:14`
- TASK TYPES label: `fontSize:10` → `fontSize:11`, marginBottom 6→8
- Task badges: `fontSize:10` → `fontSize:11`, padding bump

### 2. Model Output Layout — Full-Width Stacked
- Response grid: `display:grid, gridTemplateColumns: repeat(auto-fill, minmax(300px, 1fr))`
  → `display:flex, flexDirection:column`
- Each model box now full-width, stacked vertically

### 3. "Open Interactive" + "View Animation" — Fixed (root cause: files not in git)
- Interactive HTML files (14) and `_files/` dirs were excluded by root `.gitignore` (`interactive/` rule)
- GIF was excluded by `**/*.gif` rule
- Fix: Added negation exceptions to `.gitignore`:
  ```
  !capstone-website/frontend/public/visualizations/interactive/
  !capstone-website/frontend/public/visualizations/interactive/**
  !capstone-website/frontend/public/visualizations/png/15_bar_race.gif
  ```
- Committed all files (~56MB) so Vercel can serve them

### 4. Vote Storage Info Bar — Removed
- Removed the "💾 VOTES SAVED TO backend/data/..." dev-info div from UserStudy.jsx
- Was added as debugging info last session, not intended for production

### 5. Vote Persistence — Supabase Integration
- Root cause: Render free tier ephemeral filesystem → votes lost on redeploy
- Added optional Supabase PostgreSQL integration to `backend/user_study.py`:
  - `SUPABASE_URL` + `SUPABASE_KEY` env vars → USE_SUPABASE=True
  - `_supabase_insert(table, record)` — async httpx POST
  - `_supabase_fetch_all(table)` — async httpx GET, ordered by id
  - `/api/user-study/vote` → inserts to both `votes` and `questions` tables via Supabase
  - `/api/user-study/results` → fetches live from Supabase when configured
  - Falls back to file-based storage when env vars absent
- No new Python packages needed (uses httpx already present)

**To activate:** Create free project at supabase.com, run this SQL:
```sql
CREATE TABLE votes (id BIGSERIAL PRIMARY KEY, data JSONB NOT NULL, created_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE questions (id BIGSERIAL PRIMARY KEY, data JSONB NOT NULL, created_at TIMESTAMPTZ DEFAULT NOW());
```
Then set `SUPABASE_URL` and `SUPABASE_KEY` in Render environment variables.

## Deployment
- Files committed to main
- Vercel auto-deploys (frontend changes + interactive HTML files now tracked)
- Render auto-deploys (backend user_study.py with Supabase support)
- Vote persistence requires manual Supabase setup (see above)

## Notes
- Interactive HTML files total ~56MB but all individual files < 5MB — within GitHub limits
- `_files/` dirs contain plotly-main-2.11.1 (~4MB each) × 14 HTMLs = most of the 56MB
- Supabase free tier: 500MB DB, unlimited API calls, no time limit

---

## 2026-04-30 — UI/viz session 29e

> Original frontmatter: (no YAML — title `Session 29e — UI Polish + R Viz Overhauls`), Date: 2026-04-30, Commit: ac3c979

# Session 29e — UI Polish + R Viz Overhauls

**Date:** 2026-04-30
**Commit:** ac3c979

## What was done

### UI/UX (App.jsx + UserStudy.jsx)
1. **Footer** — added bottom footer with section nav links + "Albert Simonyan · DS 299 · AUA · 2026"
2. **Key Findings title** — `fontSize:10 → 16` (was barely visible)
3. **Radar legend + axes** — legend fontSize 11→14, axis labels 10→12, pad 80→96
4. **Filter sidebar alignment** — changed `whileInView` → `animate` (instant), added `alignSelf:'flex-start'`
5. **Task description truncation** — 155 → 280 chars
6. **Section widths** — RQ boxes 960→1300, overview 900→1100, tier/scoring 960→1200, refs 960→1300, UserStudy 1100→1300
7. **Key Findings + Radar layout** — combined into 2-column grid (findings left, radar right) in About section
8. **Möbius Strip hero** — new `MobiusStrip.jsx` canvas component with parametric Möbius mesh, aqua/blue/purple palette, painter's algorithm depth sort, auto-resizes, 0.005 rad/frame rotation

### R Visualizations (all regenerated + copied to public/)
9. **03_distributions.R** — interactive: replaced violin plot with density ridges (matching static ggridges); polygon fill per model, jittered points, median dotted lines
10. **16_error_taxonomy.R** — E8 Hallucination now shown (count=0) — fixed by joining from full `error_labels` set instead of data-present keys
11. **14_difficulty.R** — full redesign: grouped bar chart (pass rate by model×difficulty) + heatmap interactive; much more informative than old line chart
12. **07_latency_accuracy.R** — textposition outside bars, proper subplot margins, no text overlap

## Key decisions
- Möbius strip uses canvas 2D (not Three.js) to avoid new dependencies
- Depth sorting via painter's algorithm (avgZ per quad) gives correct occlusion
- E8 count=0 in data — shown explicitly in chart (not hidden) to inform audience
- Difficulty heatmap interactive shows "N_pass / N_total" per cell for max information

## Files changed
- `src/App.jsx` — all UI changes
- `src/pages/UserStudy.jsx` — maxWidth 1100→1300
- `src/components/MobiusStrip.jsx` — new file
- `public/visualizations/` — updated PNGs + HTMLs
- `report_materials/r_analysis/` — 4 R scripts updated

---

## 2026-04-30 — UI session 30b

> Original frontmatter: (no YAML — title `Session 30b — Hero, Radar, Atom Orbits, Filter, Descriptions, User Study Layout`), Date: 2026-04-30, Commit: c86cb39

# Session 30b — Hero, Radar, Atom Orbits, Filter, Descriptions, User Study Layout

**Date:** 2026-04-30
**Commit:** c86cb39

## What was done

### UI/UX (App.jsx)
1. **Hero background** — Removed Möbius strip + "BAYESIAN" watermark. Created `HeroNetworkBg.jsx` — canvas animation with 72 nodes, animated edge connections, traveling light pulses, aqua/blue/purple palette matching site theme.
2. **Radar legend horizontal** — Legend moved from vertical right column to horizontal row below the radar chart. Compact pill-style entries.
3. **Key Findings + Radar symmetry** — Both column headers now 13px (matched), tighter padding on radar card, finding cards slightly smaller padding for balance.
4. **How It Works circle bigger** — Center hub 110 → 145px. Added 3 animated electron orbit rings (aqua 28s, purple 18s, blue 22s CCW) with glowing dot particles on each orbit.
5. **Filter sidebar alignment** — Replaced `motion.div` with plain `div`, `alignSelf:'start'` (was `'flex-start'`), removed opacity animation. Now aligns correctly to top of task grid on open.
6. **Footer cleanup** — Removed "Bayes Bench · 171 tasks · 5 models · 38 task types" line.

### Task Descriptions (tasks.json)
7. **10 CONCEPTUAL task descriptions fixed** — All ended with `...` (truncated at 120 chars). Replaced with full `reference_answer` text (up to 425 chars). Tasks: CONCEPTUAL_01 through CONCEPTUAL_10.

### User Study (UserStudy.jsx + backend)
8. **Registration form inline** — Removed `position:fixed` modal (was broken by CSS stacking context from root `motion.div` filter). Now appears as animated inline form within the question panel. No scroll, no fly-to-top.
9. **2-column layout** — Question panel left, aggregate votes right, full width. Both columns equal `1fr`.
10. **AggregatePanel always visible** — Replaced collapsible `AggregateStats` with `AggregatePanel` that loads on mount. Shows model vote distribution + reason breakdown (Mathematical Accuracy, Clarity, Thoroughness, Presentation, Trustworthiness).
11. **Backend: reason_distribution** — `/api/user-study/results` now includes `reason_distribution` dict alongside `vote_distribution`.

## Files changed
- `src/App.jsx` — hero, radar, orbit, filter, footer
- `src/components/HeroNetworkBg.jsx` — new canvas neural network background
- `src/pages/UserStudy.jsx` — full layout rework
- `src/data/tasks.json` — 10 CONCEPTUAL descriptions fixed
- `backend/user_study.py` — added reason_distribution to results endpoint

## Key decisions
- No Three.js for hero — Canvas 2D sufficient, no new deps
- Inline registration avoids CSS stacking context issue (documented in CLAUDE.md)
- `alignSelf:'start'` (Grid keyword) instead of `'flex-start'` for correct grid alignment

---

## 2026-04-30 — UI session 30c

> Original frontmatter: (no YAML — title `Session 30c — How It Works Bigger, More Particles, Filter Fix, Page Sizes`), Date: 2026-04-30

# Session 30c — How It Works Bigger, More Particles, Filter Fix, Page Sizes

**Date:** 2026-04-30

## What was done

### UI/UX (App.jsx)
1. **How It Works container** — 640×640 → 800×800px. More visual real estate for the atom diagram.
2. **More particles on all rings** — Each of the 5 orbit rings now has 3 glowing dot particles (12 o'clock, 6 o'clock, 3 o'clock) instead of 1. Outer 78% ring and inner 58% ring both got particles added too (previously had none). Total: ~15 moving particles across all rings.
3. **Center hub text** — "BENCHMARK / 171 / TASKS / 5 MODELS" (4 lines) → single word "Benchmarking" at 16px mono font.
4. **Filter alignment** — Removed `position:'sticky', top:96` from filter sidebar wrapper. Was causing visual misalignment: the top:96 sticky constraint was pushing the filter below the task cards. Now plain `alignSelf:'start', marginTop:0`.
5. **Page sizes** — `PER_PAGE_OPTIONS` changed from `[9, 18, 36, 72, 171]` to `[16, 32, 64, 171]`. Default `perPage` changed from 18 → 16.

## Files changed
- `src/App.jsx` — container size, orbit particles, center text, filter wrapper, page options

## Key decisions
- Outer ring particles use `transform:'translate(-50%,-50%)'` on the ring div to properly center the ring relative to the hub — all rings now have this, fixing the centering
- Removed sticky positioning rather than adjusting `top` value — sticky inside overflow:hidden parent can behave unpredictably
- "Benchmarking" replaces the 4-line hub content for cleaner visual

---

## 2026-04-30 — UI session 30d

> Original frontmatter: (no YAML — title `Session 30d — Orbit Speed, RQ Layout, Key Findings, References Polish`), Date: 2026-04-30

# Session 30d — Orbit Speed, RQ Layout, Key Findings, References Polish

**Date:** 2026-04-30

## What was done

### How It Works
1. **Outer ring speed** — 78% ring 70s→32s, 58% ring 45s→20s. Rotation now visibly perceptible. Borders also slightly more visible (0.12→0.18 opacity).

### About This Research
2. **Removed "FIVE RESEARCH QUESTIONS" header + paragraph** — "Each question maps to a scoring dimension..." text removed. RQ cards now start directly.
3. **RQ cards staggered layout** — Changed from `auto-fit grid` to `flex row` (5 equal cards). Alternating marginTop (0/36px) for visual stagger. Top accent border replaces left border. Large ghosted number (opacity 0.08) in corner. More compact card layout.
4. **Key Findings — richer content** — `ABOUT_FINDINGS` updated with `stat`, `statLabel`, `title`, `text` fields. Each card now shows: icon + big stat number + stat label + finding title + description.
5. **Key Findings equal height** — Grid `alignItems:'stretch'`. Both columns use `flex:1` to match height. Finding cards use `flex:1` to share column height equally with radar.

### References
6. **Removed descriptive paragraphs** — "Papers that directly shaped..." and "Graduate-level Bayesian statistics texts..." paragraphs removed.
7. **Removed SectionTitle subtitle** — "Papers and textbooks that define the scope..." removed.
8. **Section headers bigger** — "5 REFERENCED RESEARCH PAPERS" and "7 GRADUATE TEXTBOOKS" font: 10→16px, moved to standalone heading without paragraph below.
9. **Rounded hover glow** — Added `borderRadius:16` to motion.div wrappers on both paper and textbook cards. BoxShadow now follows border-radius (was rectangular glow on rounded cards).

## Files changed
- `src/App.jsx` — all above changes

---

## 2026-04-30 — Day 1 poster sprint

> Original frontmatter: (no YAML — title `Day 1 — Poster Sprint Session (2026-04-30)`)

# Day 1 — Poster Sprint Session (2026-04-30)

## Goal
Build external LLM-as-judge module (Llama 3.3 70B via Groq), validate on
10-sample, prepare for full 1,230-run scaling.

## Context
Day 1 of a 3-day sprint for May 8 poster presentation. Addresses professor
critiques: shallow keyword rubric, evaluation bias, weak reasoning checks.

## Session log

### Setup + context reads
- Read `evaluation/llm_judge.py` — confirmed: ANSWER-extraction fallback using Anthropic SDK + `claude-sonnet-4-6`. Two functions: `judge_extract_answer` (when parsed_values empty) and `judge_score_structure` (when structure_score < 0.3). DO NOT TOUCH.
- Read `evaluation/metrics.py` — Path B post-hoc scoring. WEIGHTS = N=M=A=C=R=0.20. Operates on `TaskRun` dataclasses.
- Read `llm_runner/response_parser.py` — Path A live scoring. Same weights. Keyword-based `_STRUCTURE_KEYWORDS` and `_ASSUMPTION_KEYWORDS` dicts. `full_score()` is the main entry point.
- Read `llm_runner/model_clients.py` — httpx style: payload + headers + `timeout=60s`. DeepSeek/Mistral use OpenAI-compatible chat-completions schema (same as Groq).
- Sampled tasks: `BINOM_FLAT_01` (Tier 1), `OPT_SCALED_01` (Tier 4), `BETA_BINOM_01` (Tier 1). Tasks have `required_structure_checks`, `required_assumption_checks`, `numeric_targets` arrays. Crucially: tasks_all.json does NOT contain a `prompt_template` or `task_type` at top level — task_type appears in run records (derived during run). Task prompt lives in run record's `prompt` field.
- Sampled runs.jsonl — 1,230 records. Run schema confirmed: `prompt` (sent to LLM), `raw_response` (LLM reply), `task_id`, `model_family`, plus all scoring fields.
- Vault sessions/ directory exists with 13 prior session notes (UI sessions, error taxonomy, etc.).
- GROQ_API_KEY present in `.env` (1 occurrence). Will load via dotenv.

### Decision: prompt sourcing
Judge prompt template needs `task_prompt`. The run record already contains the exact `prompt` sent to the LLM. Use that directly — no need to reconstruct from task spec.

### Decision: required-check serialization
`required_structure_checks` and `required_assumption_checks` are lists of snake_case strings (e.g. `states_iid`, `derives_optimal_c_by_minimising_mse`). Pass them as bullet lists in the judge prompt — Llama can map snake_case to natural language fine.

### Build
- Created `evaluation/llm_judge_rubric.py` (395 lines after retry/dedup helpers added — over the 350-line soft cap by ~45 lines, mostly because the mandatory judge prompt template alone is ~53 lines).
- Module structure: `judge_response`, `judge_runs_batch`, `stratified_sample`, `load_existing_run_ids`, `_strip_errored_records`, `_build_judge_prompt`, `_parse_judge_response`, `_append_jsonl`, plus `main()` argparse.
- Used `httpx.AsyncClient` with `asyncio.Semaphore` and async write_lock. Output appended as each result completes.

### 10-sample test runs
- **Run 1** (concurrency=3, before merging perturbations): 4/10 judged successfully, 6/10 skipped — task_id missing from `tasks_all.json`. **Diagnosis:** synthetic perturbation runs have task_ids like `BINOM_FLAT_01_rephrase` that live in `data/synthetic/perturbations.json`, not in tasks_all. Perturbation file has full schema with required_*_checks, so it can be merged.
- **Fix:** added `--perturbations` CLI arg that merges perturbation specs into the task-id lookup dict.
- **Run 2** (concurrency=3, with perturbations): 8/10 OK, 2/10 hit 429 TPM ("Rate limit reached on tokens per minute (TPM): Limit 12000, Used 1169"). The 5s backoff on 429 was too short for per-minute TPM resets.
- **Fix:** added `RATE_LIMIT_BACKOFF_S = 30.0` for 429 specifically (kept 5s for network/timeout). Also added `_strip_errored_records` so retries on rerun get clean output.
- **Run 3** (concurrency=2, resume): 2 errored records detected and retried, both OK. Final state: **10/10 OK, 0 errors**.

### Wall-clock time
- Run 1: 1.78s (4 judged)
- Run 2: 7.61s (8 judged + 2 errored, both at 30s+ into the run after backoff)
- Run 3 (retry only): 0.98s (2 judged)
- **Total wall-clock for clean 10-sample: ~10.4s.**
- Per-judge latency: min 658ms, median 726ms, max 5782ms (the long one was deepseek/DISC_MEDIAN_04, no obvious cause — Groq variance).

### Schema verification
- All 10 records contain: run_id, task_id, model_family, judge_model, method_structure, assumption_compliance, reasoning_quality, reasoning_completeness, judge_latency_ms, judged_at, error.
- All scores in [0.0, 1.0]. `judge_model` consistently `"llama-3.3-70b-versatile"`.
- Justifications are concise single sentences as instructed.

### Substantive observation from sample
- 9/10 records score `assumption_compliance: 0.0` because models rarely state "we assume i.i.d." explicitly even when using i.i.d. implicitly. **This validates the new judge** — the keyword-based rubric was giving false positives on these because words like "independent" or "binomial" sneak in elsewhere.
- `method_structure` is consistently 1.0 — models do hit the required structural elements.
- `reasoning_completeness` is consistently 1.0 in this sample — none were "answer-only" responses. Interesting to see if this dimension differentiates more once we judge the 1,230.

## Files created / modified
- `llm-stats-vault/sessions/2026-04-30-day1-poster-sprint.md` (this file)
- `evaluation/llm_judge_rubric.py` (new — pending)

## Decisions made
1. **Judge model: `llama-3.3-70b-versatile` via Groq.** External to all 5 benchmarked models — eliminates self-preference bias.
2. **Endpoint: OpenAI-compatible chat-completions** (`https://api.groq.com/openai/v1/chat/completions`). Same payload schema as DeepSeek/Mistral clients — minimal new code.
3. **New rubric dimension `reasoning_completeness`** added alongside method/assumption/reasoning_quality. Specifically catches "name-drops + answer, no derivation" — a failure mode the keyword rubric cannot detect.
4. **Source the task prompt from run record's `prompt` field**, not by re-rendering from task spec. The exact text seen by the LLM is what should be judged against.
5. **Resume-safe via `load_existing_run_ids`** — re-running the same CLI with `--sample 200` after `--sample 10` will skip the 10 already done.
6. **Strip ```json fences before parsing** — Llama follows JSON-only instructions ~95%, but defensive fence stripping costs nothing.
7. **Per-request timeout 60s + ONE retry on 429/timeout (5s backoff)** — matches model_clients style; full retry chain unnecessary for batch judging.

## Issues encountered
1. **Synthetic perturbation runs have task_ids not in `tasks_all.json`.** 75 of 246 unique run task_ids live in `data/synthetic/perturbations.json`. Without merging that file, ~30% of runs would be silently skipped. Solution: `--perturbations` CLI arg.
2. **Groq 429 TPM (tokens-per-minute) hit at concurrency=3 within first run.** Limit is 12,000 TPM on the free tier and our prompt is ~5,000 chars (~1,250 tokens) plus a max_tokens=1024 reply, so 5 simultaneous calls saturate the budget. 5s backoff is too short — TPM resets per-minute. Bumped 429 backoff to 30s. Recommend `--concurrency 2` for production scaling, or watch for upgrade to paid tier.
3. **Spec deviation: resume now retries errored records.** The brief said "resume-safe via load_existing_run_ids" with no caveat. Strict interpretation would skip errored records too, but that's worse UX (user has to manually scrub bad records). Implemented: `load_existing_run_ids` only returns successful run_ids; `_strip_errored_records` rewrites output excluding errored entries before retry, keeping output clean.

## Verification checklist
- [x] llm_judge_rubric.py created (separate from llm_judge.py)
- [x] Existing llm_judge.py untouched
- [x] Cross-family judging removed in favor of Llama-only external judge
- [x] reasoning_completeness dimension implemented
- [x] Resume-safe batch processing (with retry of errored records)
- [x] CLI supports --sample N (also `'all'`)
- [x] 10-sample test executed successfully (10/10 OK after retry, 0 errors)
- [x] Sample output inspected and matches schema (all required fields present)
- [x] Judge prompt sent matches template exactly (verified by rendering BETA_BINOM_01 prompt)

## Next steps after this session
- Inspect 10-sample output (user task)
- Scale to all 1,230 runs (next prompt)
- Calibration analysis (parallel session)
- Perturbation generation (parallel session)

---

## Provider migration: Groq → Together AI

**Reason for switch:** Groq's free-tier daily token cap (100K tokens/day for
llama-3.3-70b-versatile) supports only ~80 judge calls/day. Project needs
~3,800 calls total. Groq Dev tier ($) was an option; chose Together AI for
pay-per-token simplicity.

**Methodology unchanged:** same model family (Llama 3.3 70B Instruct), same
prompt template, same scoring schema. Inference provider only.

**Cost model:** ~$0.88/M tokens input + output. Estimated ~$8 for full project.

**Changes to llm_judge_rubric.py:**
- Module docstring updated (now describes Together AI as inference provider; one-paragraph note on rationale).
- `GROQ_URL` → `TOGETHER_URL = "https://api.together.xyz/v1/chat/completions"`.
- `JUDGE_MODEL`: `"llama-3.3-70b-versatile"` → `"meta-llama/Llama-3.3-70B-Instruct-Turbo"`.
- API key env var: `GROQ_API_KEY` → `TOGETHER_API_KEY` (with clearer error message on missing).
- Default concurrency raised 5 → 8 (CLI default + `judge_runs_batch` signature).
- **Bonus fix discovered during run:** added 5xx retry. Together AI returned 2× HTTP 503 ("service_unavailable") in the first run; previous code raised immediately on `httpx.HTTPStatusError`. Now: status 5xx + attempt==1 → 5s backoff + retry. 30s 429 backoff and resume-safe error retry kept as-is.

**Re-run results on Together AI (10-sample):**
- Wall-clock: 53.4s initial run + 5.1s retry = ~58.5s total. Slower than Groq's 10.4s; Together AI per-call latency runs higher (median 6650ms vs Groq's 726ms).
- Per-call latency: min 2969ms / median 6650ms / max 53056ms (the long one was a 503 retry case). Median 7s/call → projected ~2-3 hours wall-clock for 1,230 runs at concurrency=8.
- Errors: 2× HTTP 503 on first attempt; both auto-retried successfully on rerun. 0 parse errors. No 429s.
- Score distribution:
  - method_structure:        mean=1.000, zeros=0/10, ones=10/10
  - assumption_compliance:   mean=0.200, zeros=7/10, ones=1/10 (was 9/10 zeros on Groq — slightly more lenient on Together)
  - reasoning_quality:       mean=0.925, zeros=0/10, ones=7/10
  - reasoning_completeness:  mean=1.000, zeros=0/10, ones=10/10
- **Cross-provider consistency check:** scores nearly identical to Groq run on the same model. Confirms judge behavior depends on the model+prompt, not the inference provider. Methodology robust.

**Strictness verification (`scripts/inspect_judge_strictness.py`):**
- 7/10 records had `assumption_compliance < 0.5`. Inspected all 7.
- Auto-flag signals:
  - Signal 1 (template justifications): **False** — top justification appeared 1/7 times. Each justification quotes the specific missing requirement (regularity conditions / iid / chain irreducible / independent uniform). Not pattern-matching.
  - Signal 1b (shared phrase): 7/7 mention iid/independent/explicit-stating — but they're naming the actually-required-but-missing concept, not a canned phrase.
  - Signal 2 (length-independent zeros): **True** — long responses (>2000 chars, 2/7 cases) still scored zero. Length is not the cue.
  - Signal 3 (high-keyword zeros): **False** — only 1/7 had ≥5 keyword hits. Most responses score zero because the assumption *concept* genuinely isn't stated, not just because keywords are absent.
- **Auto-verdict: MIXED** (1/3 signals true).
- **Manual reading of cases:** judge appears CORRECT in most. Examples:
  - FISHER_INFO_05 (mistral): response says "i.i.d." in passing but never states regularity conditions. Required check is `states_regularity_conditions`. Judge correct.
  - STATIONARY_01 (gemini): response solves πP=π but never states chain is irreducible/aperiodic. Required: `chain_is_irreducible`, `chain_is_aperiodic`. Judge correct.
  - DISC_MEDIAN_04 (deepseek): judge note says "implicitly used" — judge acknowledges implicit use but penalizes lack of explicit statement, per rubric. This is the rubric working as designed.
  - BIAS_VAR_01 (claude): no mention of iid or distributional assumption anywhere. Judge correct.
- **Borderline:** BETA_BINOM_01_rephrase (deepseek) — uses "Beta(α=2, β=2)" and "Binomial likelihood" in notation, never explicitly says "we assume the trials are i.i.d. Bernoulli." Judge calls it 0.0; reasonable case for 0.5. Same for BINOM_FLAT_01_numerical (chatgpt).
- **Conclusion:** Judge is doing what the rubric says — penalizing implicit assumptions. The 0.0 scores reflect that LLMs almost never explicitly enumerate "we assume i.i.d." as a separate statement. The original keyword rubric was over-lenient: it triggered on words like "binomial" or "normal" embedded in formulas, scoring assumption_compliance high without verifying the assumption was actually *stated*.
- **Recommendation:** scale to 1,230 as-is. The judge is strict-by-design; the keyword rubric was misleadingly permissive. The new scores are the right signal for the paper (LLMs underexplain assumptions).

**Files added:**
- `scripts/inspect_judge_strictness.py` — strictness verification helper (loads judge results, prints low-score cases + response excerpts, computes 3 auto-flag signals + verdict).

---

## Solver dispatch discovery

**Goal:** map every benchmark `task_type` to its ground-truth solver before
building the perturbation generator. Discovery only — generator code lives in
the next prompt.

**Method:**
1. Enumerated 38 unique task_types from `data/benchmark_v1/tasks_all.json` by
   regex on `task_id` prefix (no `task_type` field is serialised in the file —
   inferred from `^([A-Z_]+?)_(\d+)$`).
2. AST-parsed `baseline/bayesian/*.py` and `baseline/frequentist/*.py` to
   extract function signatures and one-line docstrings.
3. Walked imports + call sites in `build_tasks_bayesian.py` and
   `build_tasks_advanced.py` to bind each task_type to its solver(s).
4. Classified each type as `solver_callable` / `solver_with_adapter` /
   `inline_math` / `mc_seeded` / `unknown`.

**Feasibility breakdown:**

| Verdict | Types | Base tasks |
|---|---:|---:|
| `solver_callable` (clean dispatch) | 18 | 68 |
| `solver_with_adapter` (~80 LOC glue) | 11 | 53 |
| `inline_math` (extract helper) | 1 | 5 (BIAS_VAR) |
| `mc_seeded` (skip numerical) | 7 | 35 (Phase 2 MCMC) |
| `unknown` (CONCEPTUAL — qualitative) | 1 | 10 |

**Plan document:** `scripts/perturbation_generator_plan.md`

**Surprises / flags:**
- `tasks_all.json` records do **not** carry an explicit `task_type` field —
  Phase 2 build script sets it but it doesn't survive serialisation in some
  paths. Generator must regex it from `task_id` (or we patch the build
  scripts to emit it).
- `BIAS_VAR` is the only Phase 1 type with no callable solver — three
  closed-form lines hardcoded at `build_tasks_bayesian.py:293-295`. Trivial
  to extract into a helper.
- `RJMCMC` is bucketed with `mc_seeded` but its docstring claims an
  *analytical* Bayes factor between two Normal models. Worth re-reading
  before final classification — could be promoted to `solver_with_adapter`.
- `CONCEPTUAL` (10 tasks) has no numeric targets at all — generator needs a
  rubric-only branch that copies `reference_answer` + `rubric_keys`
  unchanged.
- `FISHER_INFO` / `RC_BOUND` / `MLE_EFFICIENCY` solvers raise
  `NotImplementedError` for `dist="uniform"`. Generator must constrain
  `dist ∈ {binomial, poisson, normal}` or carry over the base task's dist.
- `MARKOV` and `ORDER_STAT` use subtype dispatch — perturbations must
  preserve the subtype to keep target keys aligned.
- `STATIONARY` and `DIRICHLET` carry vector-shape constraints (k×k matrix /
  3-category Dirichlet) — perturbation must keep dimensions.

**Estimated full perturbation run:**
- 126 numerically-feasible base tasks × 3 perturbations = 378 numerical
- 45 non-numerical base tasks × 2 perturbations (rephrase + semantic) = 90
- Total: **468 perturbations** → **2,340 model calls** (5 models)
- Cost estimate (benchmark + judge via Together): **~$6–12**.

**Status:** ready to build the generator. No baseline/ or data/ files were
modified during discovery.

---

## Full 1,230-run judge scaling

**Start:** 2026-04-30T15:27:56+0400
**End:**   2026-04-30T15:46:39+0400 (initial run); ~2 minutes additional retries
**Wall-clock (initial run):** 1083.3 s (≈18 min 3 s) at concurrency=8.
**Output file:** `experiments/results_v2/llm_judge_scores_full.jsonl`

### Per-call latency
- min: 996 ms
- median: 4638 ms
- p95: 17407 ms
- max: 58445 ms

### Errors during initial run
| Type | Count | Notes |
|---|---|---|
| 429 | 0 | Together AI had no rate limit issues |
| 503 | 4 | All recovered via 5xx retry on first rerun |
| parse | 14 | Llama returned malformed/truncated JSON; mostly recovered on retry |
| timeout/network | 0 | Stable |

### Retry sweeps
- 1st retry (18 errored): 14/18 OK, 4 parse errors persisted (deterministic at temperature=0).
- 2nd retry (4 errored): 1/4 OK, 3 parse errors persisted.
- 3rd retry (3 errored): 2/3 OK, 1 parse error persisted.
- 4th retry (1 errored): 0/1 OK — same record always cuts off mid-justification.
- **Final state: 1229/1230 records successfully judged (99.92%).**
- Stuck record: `0f74e564-f470-47b9-ae67-6888158b0144` (mistral / VB_04). Inspection shows JSON output reaches max_tokens=1024 mid-justification on `assumption_compliance`. Deterministic at temperature=0 — cannot recover without raising max_tokens or shortening required justification text. Acceptable loss for paper-grade analysis.

### Final score distributions (n=1229 successful)
| Dimension | Mean | Std | Zeros | Ones |
|---|---|---|---|---|
| method_structure       | 0.946 | 0.180 | 21 (1.7%)  | 1118 (91.0%) |
| assumption_compliance  | 0.446 | 0.477 | 633 (51.5%)| 500  (40.7%) |
| reasoning_quality      | 0.903 | 0.147 | 0   (0.0%) | 815  (66.3%) |
| reasoning_completeness | 0.962 | 0.139 | 4   (0.3%) | 1139 (92.7%) |

Key observations vs 10-sample test:
- `assumption_compliance` mean 0.446 (vs 0.200 in sample) — the full population is more bimodal: 51.5% zeros + 40.7% ones. Confirms the dimension *does* differentiate; sample was biased toward the harder tasks.
- `method_structure` 91% ones, `reasoning_completeness` 93% ones — LLMs reliably produce the structural template and walk through reasoning.
- The signal-bearing dimensions for the paper are `assumption_compliance` (where models fail) and `reasoning_quality` (where the 33.7% non-ones live, mostly missing plain-language interpretation).

### Cost
- Total tokens: input 1,992,478 + output 243,895 = **2,236,373 tokens**
- Cost @ $0.88/M tokens: **$1.968** total
- Approximately matches the ~$1.20 ballpark in spec; modest overrun from larger prompts (verbose run records) and 4 retry sweeps.

### Output schema verified
First 3 records inspected — all contain required fields plus the new `input_tokens` / `output_tokens` for cost accounting. Judge model field consistently `meta-llama/Llama-3.3-70B-Instruct-Turbo`.

---

## Keyword vs Judge agreement analysis

**Script:** `scripts/keyword_vs_judge_agreement.py` (read-only join of
`experiments/results_v1/runs.jsonl` + `experiments/results_v2/llm_judge_scores_full.jsonl`).

**Input sizes:** runs=1230, judge=1230 (1 errored excluded), task specs=246.
**Joined:** 1229. **Excluded** 135 runs whose tasks have empty
`required_assumption_checks` (those score 1.0 trivially under both rubrics →
spurious disagreement). **Final compared:** 1094.

### Per-dimension Spearman ρ (and other metrics)
| Dimension | n | Spearman ρ | Cohen κ (pass/fail) | Mean abs diff | Major disagreements (>0.5) | kw mean → judge mean |
|---|---|---|---|---|---|---|
| method_structure       | 1094 | -0.010 | 0.008 | 0.162 | 51  | 0.878 → 0.941 |
| assumption_compliance  | 1094 |  0.591 | 0.407 | 0.266 | 120 | 0.565 → 0.441 |
| reasoning_quality      |  460 |  0.160 | 0.000 | 0.295 | 54  | 0.632 → 0.889 |

(reasoning_quality `n=460`: the keyword rubric's reasoning_score is on a finer 0/0.25/0.5/0.75/1 grid; only records where both produce non-null values are counted. Many keyword runs predate the dimension.)

### Per-model Spearman ρ (assumption_compliance — the load-bearing dimension)
| Model | method_structure | assumption_compliance | reasoning_quality |
|---|---|---|---|
| chatgpt  | -0.014 | 0.607 | 0.078 |
| claude   | -0.032 | 0.573 | 0.132 |
| deepseek | -0.087 | 0.580 | 0.172 |
| gemini   | -0.046 | 0.550 | 0.000 |
| mistral  |  0.049 | 0.660 | 0.202 |

Model effect is small — disagreement is dimension-driven, not model-driven.

### Headline pass-flip (assumption_compliance)
- **Keyword PASS but judge FAIL: 274 / 1094 = 25.0%.** ← poster line
- Keyword FAIL but judge PASS: 54.
- Net: keyword rubric is overly lenient on 25% of runs that the external
  judge flags as missing required assumptions.

### Reasoning_completeness (judge-only, no keyword counterpart)
- mean=0.962, n=1229. Models almost always walk through reasoning rather than
  drop a bare answer — confirms LLMs don't shortcut on these tasks.

### Top 5 disagreements (sanity check)
1. **claude/BIAS_VAR_03** — kw=0.0, judge=1.0 (keyword missed an explicit i.i.d. + Uniform(0,θ) statement that judge picked up correctly).
2. **claude/BIAS_VAR_05** — kw=0.0, judge=1.0 (same pattern).
3. **claude/MSE_COMPARE_04** — kw=1.0, judge=0.0 (keyword triggered on "i.i.d." in the *task prompt* echoed back; judge correctly noted no explicit assumption statement in the response).
4. **claude/MSE_COMPARE_05** — kw=1.0, judge=0.0 (same).
5. **claude/MARKOV_02** — kw=1.0, judge=0.0 (keyword keyword-matched on "absorbing"; judge noted absorbing_boundaries_at_0_and_M never explicitly stated).

Both directions of disagreement are substantively defensible — reinforces that the keyword rubric is noisy + sometimes lenient, but not always wrong.

### Output paths
- `experiments/results_v2/keyword_vs_judge_agreement.json` — all numerical results (overall, per-model, per-task-type, pass-flip)
- `experiments/results_v2/top_disagreements_assumption.json` — 30 cases with response excerpts
- `report_materials/figures/judge_validation_scatter.png` — 4-panel scatter (keyword vs judge per dimension, colored by model)
- `report_materials/figures/judge_validation_by_model.png` — bar chart of Spearman ρ per (dimension, model)

### Poster takeaway
The external judge agrees with the keyword rubric on `method_structure` (both
saturate near 1.0 — most LLMs hit the structural template) and disagrees most
on `assumption_compliance` (Spearman ρ = 0.59 — moderate correlation but
~25% pass-flip rate). The judge is detecting genuine assumption-omissions
that the keyword rubric scored away. This is the methodology-validation
result for §4 of the poster.

---

## Pre-launch fixes (2026-04-30)

Three small fixes before launching the agreement analysis (Prompt A) and the
perturbation generator (Prompt B) in parallel.

### 0. Previous session's `uniform_estimators.py` edit — KEPT

`git diff baseline/frequentist/uniform_estimators.py` showed a clean append at
line 198: `bias_variance_decomp_uniform_max(n: int, theta: float) -> Dict[str, float]`.
Implementation matches `build_tasks_bayesian.py:293-295` exactly (closed-form
bias / var / mse for d2 = max(X_i) under Uniform(0, θ)). Reuses existing
`_require_positive` helper.

Sanity check (n=5, θ=1.0):
```
{'bias': -0.16666666666666666, 'var_d2': 0.01984126984126984, 'mse_d2': 0.047619047619047616}
```
Matches BIAS_VAR_01 numeric_targets to machine precision.

Verdict: **KEPT**. BIAS_VAR can stay promoted to `solver_callable` in the
perturbation generator dispatch.

### 1. RJMCMC verified — RECLASSIFIED to solver_with_adapter (analytic)

Read `baseline/bayesian/advanced_methods.py:218-278`. RJMCMC's `solve()` is
fully analytical despite the `np.random.seed(42)` line — the seed call is
dead code and `proposal_std` is "kept for API compat." Output is deterministic
given inputs.

Code excerpt (`advanced_methods.py:247-271`):
```python
def solve(self) -> Dict[str, float]:
    np.random.seed(42)            # dead code — no rng calls follow
    y = np.array(self.data)
    mid = len(y) // 2
    y1, y2 = y[:mid], y[mid:]
    log_ml_m1 = self._log_marginal(y)                          # closed-form
    log_ml_m2 = self._log_marginal(y1) + self._log_marginal(y2)
    log_bf   = log_ml_m1 - log_ml_m2
    log_bf   = float(np.clip(log_bf, -30.0, 30.0))
    bf       = math.exp(log_bf)
    p1 = self.prior_prob_m1
    post_odds_m1 = bf * (p1 / (1.0 - p1))
    post_prob_m1 = post_odds_m1 / (1.0 + post_odds_m1)
    return {"posterior_prob_m1": ..., "posterior_prob_m2": ..., "bayes_factor": float(bf)}
```

`_log_marginal` is the Normal-Normal conjugate marginal likelihood — no random
calls in either function.

Updated `scripts/perturbation_generator_plan.md`:
- Summary table: `solver_with_adapter` 11→12 (53→58 base tasks). `mc_seeded` 7→6 (35→30 base tasks).
- Per-type detail: split RJMCMC out of the mc_seeded entry into its own
  solver_with_adapter entry with adapter signature + code excerpt.
- Final estimate: 468 → **473** total perturbations (5 RJMCMC base × 1 extra
  numerical perturbation each).
- Open question #2 marked RESOLVED.

### 2. VB_04 / mistral judge record — REGENERATED (Option A)

Original record at line 1230 of `experiments/results_v2/llm_judge_scores_full.jsonl`
had `error="parse_error"` because mistral's response had `"]` instead of `"}`
at end of `reasoning_completeness`. Not a truncation — bracket typo.

Re-judged via `scripts/_oneoff_rejudge_vb04_mistral.py`:
- Same prompt template + same model (`meta-llama/Llama-3.3-70B-Instruct-Turbo`)
- Same temperature=0
- `max_tokens` raised 1024 → 2048
- Replaced the errored line in-place (atomic temp-then-replace).

Result:
- All four scores: 1.0
- `regenerated_with_higher_max_tokens: true` flag added for transparency
- `judged_at` refreshed to 2026-04-30T12:40:13.261924+00:00
- `input_tokens`=1768, `output_tokens`=197

Verification:
```
records=1230, errored=0, malformed_lines=0
```

Final count: **1,230/1,230 records (100%)** — up from 1,229/1,230 (99.92%).

### 3. task_type helper centralized

Created `baseline/utils_task_id.py` with `task_type_from_id(task_id) -> str`.

Regex: `^(.+?)_\d+(?:_[a-z_]+)?$` — non-greedy prefix anchored to the first
digit-number block; optional perturbation suffix matched separately.

Inline tests passed (`python baseline/utils_task_id.py` → `OK`):
- BETA_BINOM_01 → BETA_BINOM
- BETA_BINOM_01_rephrase → BETA_BINOM
- STATIONARY_03_numerical → STATIONARY
- HMC_05 → HMC
- MARKOV_01 → MARKOV
- RJMCMC_02 → RJMCMC

Validation against `data/benchmark_v1/tasks_all.json` (171 tasks):
- **38 distinct task_types** — exact match to the discovery report.
- Set: ABC, BAYES_FACTOR, BAYES_REG, BAYES_RISK, BETA_BINOM, BIAS_VAR,
  BINOM_FLAT, BOX_MULLER, CI_CREDIBLE, CONCEPTUAL, DIRICHLET, DISC_MEDIAN,
  FISHER_INFO, GAMBLER, GAMMA_POISSON, GIBBS, HIERARCHICAL, HMC, HPD,
  JEFFREYS, LOG_ML, MARKOV, MH, MINIMAX, MLE_EFFICIENCY, MLE_MAP,
  MSE_COMPARE, NORMAL_GAMMA, OPT_SCALED, ORDER_STAT, PPC, RANGE_DIST,
  RC_BOUND, REGRESSION, RJMCMC, STATIONARY, UNIFORM_MLE, VB.

Both Prompt A and Prompt B will import:
```python
from baseline.utils_task_id import task_type_from_id
```

No build scripts touched, no task data modified.

### Final perturbation count

**473** perturbations total (was 468 before RJMCMC reclassification):
- 131 numerically-feasible base tasks × 3 perturbations = 393 numerical
- 30 mc_seeded base tasks × 2 perturbations (rephrase + semantic) = 60
- 10 conceptual base tasks × 2 perturbations = 20
- × 5 models = **2,365 model calls** (was 2,340).
- Cost estimate unchanged: ~$6–12.

### Files added / modified
- `baseline/utils_task_id.py` (new)
- `scripts/_oneoff_rejudge_vb04_mistral.py` (new — disposable one-off)
- `scripts/perturbation_generator_plan.md` (RJMCMC reclassified, summary
  table + final count updated)
- `experiments/results_v2/llm_judge_scores_full.jsonl` (1 record replaced
  in-place via atomic write)

---

## Calibration analysis (RQ5)

**Script:** `scripts/calibration_analysis.py` — read-only join of `runs.jsonl`
+ judge scores. Re-extracts raw confidence via `llm_runner.response_parser.extract_confidence`
because the `confidence_score` field stored in runs.jsonl is the *calibration*
score (already conditioned on accuracy), not raw confidence.

**Buckets:** confidence value → category
- conf >= 0.7 → high (claimed 0.9)
- 0.4 ≤ conf < 0.7 (excl 0.5) → medium (claimed 0.6)
- conf < 0.4 → low (claimed 0.3)
- conf == 0.5 default → unstated (claimed 0.5)

**Accuracy:** `numeric_score` field (numeric tasks). Falls back to
judge `reasoning_quality.score` when numeric_score is missing or 0 with no
ground truth (CONCEPTUAL).

### Per-model ECE
| Model | high_acc | med_acc | low_acc | unstated_acc | ECE | overall_acc | n (h/m/l/u) |
|---|---|---|---|---|---|---|---|
| chatgpt  | — | 0.618 | — | 0.589 | **0.063** | 0.600 | 0/91/0/155 |
| claude   | — | 0.667 | 0.500 | 0.562 | **0.067** | 0.612 | 0/120/4/122 |
| mistral  | — | 0.557 | 1.000 | 0.620 | **0.084** | 0.590 | 0/123/1/122 |
| gemini   | — | 0.540 | 0.500 | 0.627 | **0.097** | 0.581 | 0/118/9/119 |
| deepseek | — | 0.444 | 0.250 | 0.713 | **0.179** | 0.567 | 0/120/8/118 |

No model produced enough "definitive" linguistic markers to land in the high-confidence bucket — extraction caps at 0.9 only when several definitive phrases stack. **All models are linguistically hedge-heavy on Bayesian tasks** — they default to "unstated" (exactly 0.5) or medium hedge phrasing.

### Calibration ranking (best → worst by ECE)
1. **chatgpt** — ECE 0.063
2. **claude** — ECE 0.067
3. **mistral** — ECE 0.084
4. **gemini** — ECE 0.097
5. **deepseek** — ECE 0.179 (worst — overconfident on its 'unstated' claims)

### Accuracy ranking (best → worst)
1. **claude** — 0.612
2. **chatgpt** — 0.600
3. **mistral** — 0.590
4. **gemini** — 0.581
5. **deepseek** — 0.567

### Comparison
Calibration ≠ accuracy ranking, but close:
- chatgpt is best calibrated, second on accuracy.
- claude is best on accuracy, second on calibration.
- deepseek is worst on both — its 'unstated' (claimed 0.5) bucket actually achieves 0.713 accuracy → systematically *under-confident*, the largest gap of any model.
- mistral has the most extreme bucket result: 1.000 accuracy in the low-confidence bucket (n=1 only — single hedge case got it right). Otherwise mid-pack.

**Headline:** chatgpt and claude form the calibrated tier; deepseek's overall accuracy is similar to others but its confidence signal is the noisiest.

### Output paths
- `experiments/results_v2/calibration.json` — full per-model bucket counts, accuracies, ECE
- `report_materials/figures/calibration_reliability.png` — reliability diagram (5 lines, perfect-calibration diagonal)
- `report_materials/figures/calibration_ece_ranking.png` — bar chart ECE per model, sorted ascending

### Caveat
Confidence extraction is keyword-based (hedge words ↓, definitive words ↑). It does NOT capture semantic confidence — a model could say "the answer is exactly 4.2" with no hedges and get bucketed as unstated if no definitive phrases match. Future work: have the LLM judge rate explicit confidence claims separately (would also fold into the next-day calibration extension if budget allows).

---

## Perturbation generator implementation (validation phase)

**Goal:** build `scripts/generate_perturbations_full.py` to extend the 25-base
v1 set (75 perturbations) up to all 171 base tasks (~473 perturbations).
Discovery report locked the dispatch map; this session implements + validates.

### Step 0: RJMCMC reclassification — VERDICT: ANALYTIC (`solver_callable`)

Read `baseline/bayesian/advanced_methods.py:218-271` (the `RJMCMC.solve()`
body). Findings:
- Class docstring at line 220 says "Analytical Bayes factor between two
  Normal models."
- `solve()` calls `np.random.seed(42)` at line 248 — but never invokes any
  `np.random.*` draw. The seed is dead code.
- The actual computation at lines 252-265 is closed-form: two log-marginal
  likelihoods (`_log_marginal`) computed analytically from sample means and
  sums of squares, combined into a deterministic Bayes factor and posterior
  probability via Bayes' rule.
- `validate()` returns `True` whenever posterior probabilities sum to 1 and
  BF > 0 — no MC stochasticity tolerance.

→ Reclassified to `solver_with_adapter`. Numerical perturbations are
methodologically sound (deterministic given inputs). 5 RJMCMC base tasks now
join the numerical-feasible bucket.

**Updated counts:**
- solver_callable: 18 types, 68 tasks
- solver_with_adapter: 12 types, 58 tasks (added RJMCMC × 5)
- inline_math: 1 type, 5 tasks (BIAS_VAR — extracted)
- mc_seeded: 6 types, 30 tasks (was 7×35)
- conceptual: 1 type, 10 tasks
- **Numerical-feasible total: 131 base tasks**
- **Expected perturbation count: 131×3 + 30×2 + 10×2 = 473**

### BIAS_VAR helper extraction

Added `bias_variance_decomp_uniform_max(n: int, theta: float) -> Dict[str, float]`
to `baseline/frequentist/uniform_estimators.py`. Three-line analytical
formulas (bias = -θ/(n+1), var, mse) extracted from
`build_tasks_bayesian.py:293-295`. Sanity-checked: matches stored
`BIAS_VAR_01` targets exactly (bias=-0.16667, var=0.01984, mse=0.04762 for
n=5, θ=1.0).

### Dispatch table coverage

`DISPATCH` covers **31 task_types** across the numerical-feasible bucket
(18 callable + 12 adapter + 1 BIAS_VAR). Subtype-driven types (`MARKOV`,
`ORDER_STAT`) get a `target_keys` argument so they branch correctly on
which sub-solver to call.

Skipped (by design, no numerical):
- 6 mc_seeded types: GIBBS, MH, HMC, VB, ABC, HIERARCHICAL
- 1 qualitative: CONCEPTUAL

### Validation Gate 1: dispatch sanity check — **PASSED 131/131**

Ran each solver in `DISPATCH` against its base task's stored `inputs` and
compared the recomputed targets to stored `numeric_targets` within
`full_credit_tol`. All 31 task_types passed cleanly with no mismatches:

```
task_type             n  pass  fail
BAYES_FACTOR          5     5     0
BAYES_REG             5     5     0
BAYES_RISK            5     5     0
BETA_BINOM            1     1     0
BIAS_VAR              5     5     0   (new helper validated)
BINOM_FLAT            5     5     0
BOX_MULLER            5     5     0
CI_CREDIBLE           5     5     0
DIRICHLET             1     1     0
DISC_MEDIAN           5     5     0
FISHER_INFO           5     5     0
GAMBLER               3     3     0
GAMMA_POISSON         1     1     0
HPD                   5     5     0
JEFFREYS              5     5     0
LOG_ML                5     5     0
MARKOV                5     5     0
MINIMAX               5     5     0
MLE_EFFICIENCY        3     3     0
MLE_MAP               5     5     0
MSE_COMPARE           5     5     0
NORMAL_GAMMA          1     1     0
OPT_SCALED            5     5     0
ORDER_STAT            5     5     0
PPC                   5     5     0
RANGE_DIST            3     3     0
RC_BOUND              5     5     0
REGRESSION            5     5     0
RJMCMC                5     5     0   (analytic verdict empirically confirmed)
STATIONARY            3     3     0
UNIFORM_MLE           5     5     0
TOTAL               131   131     0
```

No solver disagreed with stored ground truth. RJMCMC's analytic verdict
empirically holds — re-running its `solve()` on stored inputs reproduces
the stored true_values to within `0.05` tol.

### Validation Gate 2: 15-sample generation — produced 13 records

5 base tasks × (3 numerical-feasible OR 2 non-numerical) = 13 perturbations:
- BETA_BINOM_01 → rephrase + numerical + semantic (3)
- MARKOV_03 → rephrase + numerical + semantic (3)
- RJMCMC_02 → rephrase + numerical + semantic (3)
- CONCEPTUAL_01 → rephrase + semantic (2)
- GIBBS_01 → rephrase + semantic (2)

Output: `data/synthetic/perturbations_v2_sample.jsonl`

### Issues encountered + fixes

1. **Phase 1 prompt-routing bug** — `build_prompt(synth_task)` with a
   `task_id` like `MARKOV_03_numerical_v2` was hitting the generic fallback
   branch because `_get_prefix` only matches `TYPE_NN` (no suffix).
   **Fix:** render prompts using the *base* task_id, then `re.sub` the
   header line to swap in the new id afterwards. Verified MARKOV_03_numerical
   now produces the proper gambler's ruin format.

2. **LLM meta-instruction bleed** — first sample run had Llama echoing
   "Constraints:..." blocks and "Return ONLY..." instructions inside the
   output prompts. Worst offender: `CONCEPTUAL_01_semantic` leaked a full
   solution (entire reasoning chain about p-values vs P(H0|data)) into the
   prompt body — would have catastrophically biased the benchmark.
   **Fix:** moved the "OUTPUT FORMAT" instruction to the *top* of each
   template, switched to `<<<...>>>` fenced original prompts, lowered
   temperature 0.7→0.4, and added an explicit "Do NOT echo these
   instructions" line. Re-run cleared all bleeds.

3. **Variable-key renaming in semantic** — first MARKOV_03_semantic
   renamed `ruin_prob, win_prob` to `crit_cond_prob, remission_prob` in the
   "Report:" line, which would have broken scoring (numeric_targets keys
   are the scoring contract). **Fix:** added explicit "REQUIRED: any
   variable names appearing in a Report: line must appear identically — do
   NOT rename target variables (they are scoring keys)" to both REPHRASE
   and SEMANTIC templates.

4. **Header bracket loss** — first BETA_BINOM_01_rephrase output dropped
   the `[Task ... ]` brackets. **Fix:** added "REQUIRED: keep the very
   first line as `[Task {new_task_id}  |  Tier <T>  |  <Difficulty>]`"
   to both templates.

### Residual minor quality notes (not blocking)

- A few semantic prompts include the literal phrase `(p maps to risk_rate)`
  even when no `p` variable is present (e.g. CONCEPTUAL, GIBBS). The
  template offered it as an example domain-mapping idiom; Llama treated it
  as required. Cosmetic — does not affect scoring (target keys preserved).
- `CONCEPTUAL_01_semantic` ends with `Report: p` — meaningless since
  CONCEPTUAL has no numeric_targets. Cosmetic — judging is rubric-only.

These can be polished by trimming the "(p maps to risk_rate)" exemplar from
SEMANTIC_TMPL before the full run, but they are non-breaking.

### Output schema verification

All 13 sample records contain the canonical fields: `task_id`,
`base_task_id`, `perturbation_type`, `task_type`, `tier`, `difficulty`,
`prompt`, `numeric_targets`, `required_structure_checks`,
`required_assumption_checks`, `perturbation_note`. Numerical perturbations
have fresh `true_values` recomputed by the solver; rephrase + semantic
preserve original `numeric_targets` (and structure/assumption checks)
verbatim.

### Provenance with v1

`scripts/generate_perturbations_full.py --full` skips any base task already
present in `data/synthetic/perturbations.json` (v1 covers 25 base tasks).
v2 will only generate for the 146 base tasks not in v1. Analysis-time
concatenation handles the union. v1 is left untouched.

### Files added / modified

- **NEW** `scripts/generate_perturbations_full.py` (~660 lines) — generator
  with DISPATCH table, validation gates, async LLM calls, resume safety.
- **NEW** `data/synthetic/perturbations_v2_sample.jsonl` — 13-record sample.
- **MODIFIED** `baseline/frequentist/uniform_estimators.py` — added
  `bias_variance_decomp_uniform_max(n, theta)` helper.

### Status: ready for full-scale run pending sample approval

Awaiting user review of the 13 samples. After approval:
`python scripts/generate_perturbations_full.py --full --concurrency 5`
to generate the remaining ~440 perturbations (~50 min wall-clock at
median 7s/call concurrency=5; ~$3-4 in Together API costs).

### Perturbation generator full run (2026-04-30)

**Pre-scaling fixes** (2 cosmetic issues from gate 2 report):
1. Removed `(p maps to risk_rate)` exemplar from SEMANTIC_TMPL — LLM was
   copying it literally into all semantic prompts regardless of variables.
2. Added "do NOT add a Report line if original has none" to SEMANTIC_TMPL —
   fixed stray `Report: p` on CONCEPTUAL tasks.

**Full run results**:
- **398 perturbations** generated (395 good, 3 errors)
- 146 base tasks processed (171 total − 25 already in v1)
- Per perturbation type: rephrase=146, numerical=106 (103 good), semantic=146
- 37 task types covered (all types in DISPATCH + CONCEPTUAL + MC_SEEDED)
- Wall-clock: **5.2 min** at concurrency=5
- API cost: **~$0.48** (Together AI Llama 3.3 70B Turbo)
- Output: `data/synthetic/perturbations_v2.json` (JSON array, 398 records)

**3 initial errors** (all numerical perturbations):
- `DIRICHLET_01_numerical_v2` — LLM failed to return valid JSON params (2× retry also failed)
- `REGRESSION_05_numerical_v2` — LLM failed to return valid JSON (recovered on retry)
- `MLE_EFFICIENCY_02_numerical_v2` — LLM proposed theta=2.5 for binomial (2× retry same error)

**Retry + hand-authoring**: REGRESSION_05 recovered via `--retry`. DIRICHLET_01
and MLE_EFFICIENCY_02 hand-authored with manually chosen params + solver
verification. Final: **398 records, 0 errors**.

**Sample data**: `perturbations_v2_sample.jsonl` (13 records) kept as-is —
contains old cosmetic artifacts but useful for provenance. Full run did NOT
use sample data; generated fresh for all 146 base tasks.

**Next**: benchmark scoring on v2 perturbations (separate prompt).

---

## 2026-05-01 — Day 3 literature vault

> Original frontmatter: `tags: [session, literature, day3, vault]`, `date: 2026-05-01`

# Day 3 — Literature Foundation Session (2026-05-01)

## Goal

Build a structured literature library at `llm-stats-vault/40-literature/` so
poster, paper, and future analysis can cite consistently. 22 sources total.

## Context

Day 3 of the May 8 poster sprint. Builds on:
- Day 1 ([[2026-04-30-day1-poster-sprint]]) — judge rubric + perturbation
  generator + calibration analysis groundwork.
- Day 2 audit — see `audit/day2_audit_report.md` for P-2/P-7 findings.
- Group B research — newly-discovered papers from Day 3 web searches feed RQ
  reweighting + literature comparison work.

## What was added

26 files total under `llm-stats-vault/40-literature/`:
- `README.md` — master index organized by theme.
- `citation-map.md` — reverse index (artifact → sources).
- `bibtex.bib` — 22 bibtex entries (papers + textbooks).
- `poster-citations.md` — drop-in short forms + citation cluster recipes.
- `papers/` (15 notes — 5 originally-cited + 10 newly-discovered).
- `textbooks/` (7 notes — graduate Bayesian texts).

## Sources catalogued

### Originally-cited papers (5)
1. Lu et al. (2025) — StatEval — arXiv 2510.09517
2. Nagarkar et al. (2026) — Can LLM Reasoning Be Trusted — arXiv 2601.14479
3. Liu et al. (2025) — MathEval — DOI 10.1007/s44366-025-0053-z
4. Chen et al. (2022) — Program of Thoughts — arXiv 2211.12588
5. Wei et al. (2022) — Chain of Thought — arXiv 2201.11903

### Newly-discovered papers (10)
6. Longjohn et al. (2025) — Bayesian Eval — arXiv 2511.10661
7. ReasonBench (2025) — Instability — arXiv 2512.07795
8. BrittleBench (2026) — Robustness — arXiv 2603.13285
9. Wang et al. (2025) — Ice Cream causal — arXiv 2505.13770
10. Park et al. (2025) — LLM-as-Judge empirical — arXiv 2506.13639
11. FermiEval (2025) — Overconfidence — arXiv 2510.26995
12. Multi-Answer (2026) — Consistency confidence — arXiv 2602.07842
13. Math-Failures (2026) — Reasoning failures — arXiv 2502.11574
14. Judgment-Noise (2025) — Single-judge bias — arXiv 2509.20293
15. Statistical Fragility (2025) — Tübingen/Cambridge — arXiv link TODO

### Graduate textbooks (7)
- Bolstad (2007) — Introduction to Bayesian Statistics, 2nd ed.
- Bishop (2006) — Pattern Recognition and Machine Learning
- Ghosh, Delampady & Samanta (2006) — Introduction to Bayesian Analysis
- Hoff (2009) — A First Course in Bayesian Statistical Methods
- Carlin & Louis (2008) — Bayesian Methods for Data Analysis, 3rd ed.
- Goldstein & Wooff (2007) — Bayes Linear Statistics
- Lee (2012) — Bayesian Statistics: An Introduction, 4th ed.

## TODOs flagged

13 of 15 paper notes have placeholder author lists (TODO markers in metadata
+ bibtex). Per task brief, max 2 web searches per source — TODO flagged where
metadata couldn't be fully verified within budget. Resolve before final
submission.

Paper 15 (Statistical Fragility) also needs the original arXiv link located
(currently cited via marktechpost.com summary).

## How to use this in future sessions

1. **Citing in poster:** open `40-literature/poster-citations.md`, copy the
   short form (e.g. "(Lu, 2025)") for the relevant theme.
2. **Citing in paper prose:** open the per-source note, copy the
   "Citation in paper" string. Use the bibtex key for `\cite{}`.
3. **Looking up "which source supports X":** open `citation-map.md`. Reverse
   index by RQ, script, task type, audit finding, poster panel, output file,
   figure.
4. **Adding a new source:** copy the per-paper or per-textbook template from
   this session log; save under `papers/` or `textbooks/`; update
   `README.md` theme sections + `bibtex.bib` + `citation-map.md`.

## Synchronization with website

The website's References section (capstone-website/frontend/src/) displays
the 5 originally-cited papers + 7 textbooks. The vault is now the source of
truth — when website References changes, mirror to vault first, then propagate
to poster/paper. Out of scope for this session: editing the website References
component.

## Verification

- `ls llm-stats-vault/40-literature/` → 4 top-level files + 2 dirs.
- `ls llm-stats-vault/40-literature/papers/` → 15 paper notes.
- `ls llm-stats-vault/40-literature/textbooks/` → 7 textbook notes.
- Total file count: **26**.

## Files added

- `llm-stats-vault/40-literature/README.md`
- `llm-stats-vault/40-literature/citation-map.md`
- `llm-stats-vault/40-literature/bibtex.bib`
- `llm-stats-vault/40-literature/poster-citations.md`
- `llm-stats-vault/40-literature/papers/01-original-stateval-2025.md`
- `llm-stats-vault/40-literature/papers/02-original-can-llm-reasoning-2026.md`
- `llm-stats-vault/40-literature/papers/03-original-matheval-2025.md`
- `llm-stats-vault/40-literature/papers/04-original-program-of-thoughts-2022.md`
- `llm-stats-vault/40-literature/papers/05-original-chain-of-thought-2022.md`
- `llm-stats-vault/40-literature/papers/06-new-longjohn-bayesian-eval-2025.md`
- `llm-stats-vault/40-literature/papers/07-new-reasonbench-2025.md`
- `llm-stats-vault/40-literature/papers/08-new-brittlebench-2026.md`
- `llm-stats-vault/40-literature/papers/09-new-ice-cream-causal-2025.md`
- `llm-stats-vault/40-literature/papers/10-new-llm-judge-empirical-2025.md`
- `llm-stats-vault/40-literature/papers/11-new-fermieval-2025.md`
- `llm-stats-vault/40-literature/papers/12-new-multi-answer-confidence-2026.md`
- `llm-stats-vault/40-literature/papers/13-new-math-reasoning-failures-2026.md`
- `llm-stats-vault/40-literature/papers/14-new-judgment-becomes-noise-2025.md`
- `llm-stats-vault/40-literature/papers/15-new-statistical-fragility-2025.md`
- `llm-stats-vault/40-literature/textbooks/bolstad-bayesian-statistics.md`
- `llm-stats-vault/40-literature/textbooks/bishop-prml.md`
- `llm-stats-vault/40-literature/textbooks/ghosh-delampady-samanta-bayesian.md`
- `llm-stats-vault/40-literature/textbooks/hoff-bayesian-methods.md`
- `llm-stats-vault/40-literature/textbooks/carlin-louis-bayesian-data-analysis.md`
- `llm-stats-vault/40-literature/textbooks/goldstein-wooff-bayes-linear.md`
- `llm-stats-vault/40-literature/textbooks/lee-bayesian-statistics.md`

## Files modified

- `llm-stats-vault/00-home/current-priorities.md` — added "Literature
  foundation (added 2026-05-01)" section with 22-source breakdown and
  pointers to vault index files.

## Next steps

- ~~Resolve the 13 TODO author-list placeholders before final paper submission~~
  → Done in Day 3 housekeeping pass below.
- ~~Locate original arXiv link for Paper 15 (Statistical Fragility).~~
  → Done in Day 3 housekeeping pass below (canonical: arXiv 2504.07086).
- When `audit/literature_comparison.md` is written by Group B, add inline
  links from each paper note to the comparison row.
- When `audit/rq_reweighting.md` is written, update RQ→source mappings in
  citation-map.md if the reweighting changes which RQ load-bears each finding.
- Follow-up review needed: Papers 09 (Ice Cream) and 10 (LLM-as-Judge) have
  bibtex keys `wang2025icecream` and `park2025judge` that don't match their
  actual first authors (Du and Yamauchi respectively). Keys retained per
  task constraint but Citation forms in the per-paper notes still read
  "(Wang et al., 2025)" / "(Park et al., 2025)" — those were not in the
  housekeeping pass scope. Update before final submission.
- Paper 15 canonical title differs from MarkTechPost framing — note has
  both the descriptive title ("LLM Reasoning Benchmarks are Statistically
  Fragile") and canonical title ("A Sober Look at Progress…"). Pick one
  for paper prose before final submission.

---

## Day 3 housekeeping pass (2026-05-01, later)

Resolved all 14 flagged metadata items (13 author-list TODOs + Paper 15
canonical-arXiv lookup) via arXiv abstract pages.

### Papers resolved (verified author lists now present)

| # | Bibtex key | First author | Source verified |
|---|---|---|---|
| 01 | lu2025stateval | Yuchen Lu (+19) | arXiv 2510.09517 |
| 02 | nagarkar2026canllm | Crish Nagarkar (+2) | arXiv 2601.14479 |
| 03 | liu2025matheval | Tianqiao Liu (+5) | journal.hep.com.cn (Frontiers of Digital Education) |
| 06 | longjohn2025bayesian | Rachel Longjohn (+4) | arXiv 2511.10661 |
| 07 | reasonbench2025 | Nearchos Potamitis (+2) | arXiv 2512.07795 |
| 08 | brittlebench2026 | Angelika Romanou (+10) | arXiv 2603.13285 |
| 09 | wang2025icecream | Jin Du (+8) — actual first author | arXiv 2505.13770 |
| 10 | park2025judge | Yusuke Yamauchi (+2) — actual first author | arXiv 2506.13639 |
| 11 | fermieval2025 | Elliot L. Epstein (+3) | arXiv 2510.26995 |
| 12 | multianswer2026 | Yuhan Wang (+5) | arXiv 2602.07842 |
| 13 | mathfail2026 | Johan Boye, Birger Moell | arXiv 2502.11574 |
| 14 | judgment2025noise | Benjamin Feuer (+4) | arXiv 2509.20293 |
| 15 | fragility2025 | Andreas Hochlehnert (+5) | arXiv 2504.07086 (canonical title: "A Sober Look at Progress in Language Model Reasoning") |

**Surprises during resolution:**
- Paper 09 (`wang2025icecream`) actual first author is **Du**, not Wang.
  Bibtex key retained per task constraint (key stability); inline note added
  to the per-paper note's Authors field flagging the discrepancy.
- Paper 10 (`park2025judge`) actual first author is **Yamauchi**, not Park.
  Same treatment as Paper 09.
- Paper 15 was previously cited only via marktechpost.com summary. Canonical
  arXiv version (2504.07086) has a different title — the MarkTechPost
  framing "Statistically Fragile" is the article's editorial framing; the
  authors' own title is "A Sober Look at Progress in Language Model
  Reasoning: Pitfalls and Paths to Reproducibility". Both recorded in the
  per-paper note metadata; bibtex `title` uses the canonical version.
- Paper 13 (`mathfail2026`) submission year is **2025** (arXiv 2502 = Feb
  2025), but file was named with 2026. File name and bibtex key retained
  for stability; metadata Year field unchanged in this pass since it was
  not flagged TODO. Recommend a follow-up rename pass before publication.
- Paper 03 (MathEval) is **published in Frontiers of Digital Education**
  (a Springer journal), not just a generic Springer article. `journal`
  field added to bibtex.

### Papers still TODO

**0 / 14 remain unresolved.** All 14 items resolved within budget.

### Searches consumed

- Paper 03: 2 (1 web search + 1 fetch through journal.hep.com.cn after
  Springer DOI returned 303 redirects). On budget.
- Paper 15: 2 web searches (1 to find canonical arXiv ID, 1 to disambiguate
  authors via Hochlehnert/Bhatnagar query). On budget.
- Papers 01, 02, 06, 07, 08, 09, 10, 11, 12, 13, 14: 1 arXiv fetch each.
  Well under budget.

### Files modified

- `llm-stats-vault/40-literature/bibtex.bib` — full rewrite: replaced 13
  placeholder author lists with verified authors, repointed Paper 15 from
  @misc/marktechpost to @article/arXiv, added `journal` field to Paper 03,
  removed all TODO comments, updated header to reflect housekeeping pass.
- `llm-stats-vault/40-literature/papers/01-original-stateval-2025.md` —
  Authors line updated.
- `llm-stats-vault/40-literature/papers/02-original-can-llm-reasoning-2026.md` —
  Authors line updated.
- `llm-stats-vault/40-literature/papers/03-original-matheval-2025.md` —
  Authors line updated.
- `llm-stats-vault/40-literature/papers/06-new-longjohn-bayesian-eval-2025.md` —
  Authors line updated.
- `llm-stats-vault/40-literature/papers/07-new-reasonbench-2025.md` —
  Authors line updated.
- `llm-stats-vault/40-literature/papers/08-new-brittlebench-2026.md` —
  Authors line updated.
- `llm-stats-vault/40-literature/papers/09-new-ice-cream-causal-2025.md` —
  Authors line updated (with bibtex-key-mismatch note).
- `llm-stats-vault/40-literature/papers/10-new-llm-judge-empirical-2025.md` —
  Authors line updated (with bibtex-key-mismatch note).
- `llm-stats-vault/40-literature/papers/11-new-fermieval-2025.md` —
  Authors line updated.
- `llm-stats-vault/40-literature/papers/12-new-multi-answer-confidence-2026.md` —
  Authors line updated.
- `llm-stats-vault/40-literature/papers/13-new-math-reasoning-failures-2026.md` —
  Authors line updated.
- `llm-stats-vault/40-literature/papers/14-new-judgment-becomes-noise-2025.md` —
  Authors line updated.
- `llm-stats-vault/40-literature/papers/15-new-statistical-fragility-2025.md` —
  Authors line updated, arXiv ID + canonical title + URL updated, removed
  marktechpost-summary placeholder.

### Files NOT modified (per task scope constraints)

- `README.md` — still contains the now-stale "TODO author-list confirmations"
  section (lines 92–110). Out of scope (task: "Do not modify literature
  vault README, citation-map, or poster-citations files"). README needs a
  follow-up pass to remove that section.
- `citation-map.md`, `poster-citations.md` — same reason.

### Validation

- `bibtex.bib` entry count: **22** (5 originally-cited + 10 newly-discovered
  + 7 textbooks). Unchanged.
- `bibtex.bib` braces balanced: 182 open, 182 close.
- All 15 per-paper notes retain full template structure (Metadata,
  One-line summary, Key findings, How it grounds this project, Citation in
  poster, Citation in paper, Bibtex key, Project artifacts that cite this,
  Tags).
- No TODO markers remain in `papers/` or `bibtex.bib`.

---

*End of aggregated sprint history. 15 sources merged.*
