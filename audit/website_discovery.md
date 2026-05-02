# Website Discovery Audit — Day 3 (2026-05-01)

Read-only inventory of `capstone-website/` ahead of the Day 3-5 overhaul.
No frontend or backend files were modified during this audit.

`day1_handoff.md` was **not found** in the repo (`audit/`, project root, or
nested directories). Continuity drawn from `audit/methodology_continuity.md`,
`audit/personal_todo_status.md`, and `audit/rq_restructuring.md` instead.

---

## 1. Repository structure

Single repo, two apps under `capstone-website/`:

| Path | App |
|---|---|
| `capstone-website/frontend/` | Vite + React 19 SPA (deploys to Vercel) |
| `capstone-website/backend/` | FastAPI app (deploys to Render via `render.yaml` + `Dockerfile`) |
| `capstone-website/nginx/` | Optional reverse-proxy config (unused by Vercel/Render path) |
| `capstone-website/docker-compose.yml` | Local full-stack compose |
| `website/` (project root, sibling) | **Legacy** Flask app (`app.py`, `templates/`, `static/`). Not deployed. Ignore. |

Frontend → Vercel rewrite proxy at [frontend/vercel.json](capstone-website/frontend/vercel.json#L5-L9):
```
/api/(.*) → https://bayes-benchmark.onrender.com/api/$1
```
Backend host: `bayes-benchmark.onrender.com` (Render). Public site:
`capstone-llm-stats.vercel.app`.

---

## 2. Frontend tech stack

| Concern | Choice |
|---|---|
| Framework | **Vite 8 + React 19** (SPA) — [package.json:6-32](capstone-website/frontend/package.json#L6-L32) |
| Routing | **None.** Single-page scroll, IntersectionObserver in [Navbar.jsx:25-38](capstone-website/frontend/src/components/Navbar.jsx#L25-L38). Footer anchors `#overview`, `#about`, `#benchmark`, `#models`, `#tasks`, `#visualizations`, `#user-study`, `#references`. |
| Styling | **Plain CSS** with custom-properties theme — [App.css](capstone-website/frontend/src/App.css), [index.css](capstone-website/frontend/src/index.css). No Tailwind, no CSS-in-JS lib. Heavy use of inline-style props inside JSX (every component). |
| Component library | **None.** Hand-rolled cards, tooltips, modals, radar SVGs. |
| Animation | `motion` (Framer Motion) v12 |
| Markdown / math | `react-markdown` 9 + `remark-math` 6 + `rehype-katex` 7 + KaTeX 0.16 |
| Build/output | `vite build → dist/`; `cleanUrls:false`, SPA rewrite to `/index.html` |
| Env | `VITE_API_URL` (UserStudy uses fallback `''` → relative `/api/*` paths) |

---

## 3. Current page inventory

The site is a single scrolling page (`App.jsx` 2531 lines). "Pages" below are
the eight `<section id="…">` blocks the navbar scrolls between.

| Section id | Component | Purpose | Figures shown | Key copy / hardcoded data |
|---|---|---|---|---|
| `overview` | `Overview()` [App.jsx:845-937](capstone-website/frontend/src/App.jsx#L845-L937) | Hero. Title, AUA + supervisor, Bayes 1763 quote, 3 CTAs. | None (just `<HeroNetworkBg/>`). | Hero subtitle, supervisor links. |
| `about` | `About()` [App.jsx:1999-2150](capstone-website/frontend/src/App.jsx#L1999-L2150) | RQ cards (5), 5-stat CountUp, Key Findings + multi-model radar. | `<MultiModelRadar/>` (inline SVG). | `RQS` array [App.jsx:1893-1939](capstone-website/frontend/src/App.jsx#L1893-L1939) — RQ1-5 with equal weight. `ABOUT_FINDINGS` [App.jsx:1941-1946](capstone-website/frontend/src/App.jsx#L1941-L1946). `RADAR_VALS` [App.jsx:137-143](capstone-website/frontend/src/App.jsx#L137-L143) (manual 0.6-0.95 numbers). |
| `benchmark` | `BenchmarkSection()` [App.jsx:986-1235](capstone-website/frontend/src/App.jsx#L986-L1235) | "How It Works" — 6 pipeline nodes in a circle + 4 inner-ring extras + Tier Ladder + Scoring Bars + LiveResults panel. | None (decorative SVG only). | `PIPELINE` [App.jsx:74-93](capstone-website/frontend/src/App.jsx#L74-L93), `HOW_EXTRA` [App.jsx:940-981](capstone-website/frontend/src/App.jsx#L940-L981), `TIER_INFO` [App.jsx:33-46](capstone-website/frontend/src/App.jsx#L33-L46), `LiveResults` reads `results_summary.json`. |
| `models` | `Models()` [App.jsx:1240-1309](capstone-website/frontend/src/App.jsx#L1240-L1309) | 5-model neural-network selector → expanded card with per-model radar. | `<RadarChart/>` per model (inline SVG). | `MODELS` array [App.jsx:49-70](capstone-website/frontend/src/App.jsx#L49-L70) — names, providers, token caps, hardcoded "strengths" string. |
| `tasks` | `Tasks()` [App.jsx:1314-1656](capstone-website/frontend/src/App.jsx#L1314-L1656) | Filterable 171-task gallery. Tier checkboxes, category, page-size {16,32,64,All}, grid/grouped views, ID + topic search, modal per task. | None (cards). | `TASK_TYPE_TOOLTIPS` [App.jsx:146-186](capstone-website/frontend/src/App.jsx#L146-L186), `TIER_TASK_EXAMPLES` + `TIER_CHALLENGES` [App.jsx:568-579](capstone-website/frontend/src/App.jsx#L568-L579). Reads `tasksData = tasks.json` and `statsData = stats.json` bundled into the JS. |
| `visualizations` | `VizGallery` [pages/VizGallery.jsx](capstone-website/frontend/src/pages/VizGallery.jsx) | Collapsible. Top: 5-card model leaderboard (rank-coloured). Bottom: gallery of 9 R figures, each with PNG static + interactive Plotly HTML or GIF. | All 9 entries from [data/visualizations.js](capstone-website/frontend/src/data/visualizations.js) — old R analysis figures (see §5). | Hardcoded "insight" copy per chart in `visualizations.js`. |
| `user-study` | `UserStudy` [pages/UserStudy.jsx](capstone-website/frontend/src/pages/UserStudy.jsx) | Live 5-model query + vote UI. Markdown / KaTeX rendering, divergence detector, vote panel. | None. | `MODEL_META` [UserStudy.jsx:9-15](capstone-website/frontend/src/pages/UserStudy.jsx#L9-L15) **stale** — labels "Claude Sonnet 4.6" while benchmark uses 4.5. `VOTE_REASONS` [UserStudy.jsx:21-27](capstone-website/frontend/src/pages/UserStudy.jsx#L21-L27). |
| `references` | `References()` [App.jsx:2155-2206](capstone-website/frontend/src/App.jsx#L2155-L2206) | "5 referenced research papers" header + 5 paper cards, then "7 graduate textbooks" + 7 cards. | None. | `ABOUT_REFS` [App.jsx:1974-1990](capstone-website/frontend/src/App.jsx#L1974-L1990) — 5 papers. `TEXTBOOKS` [App.jsx:1869-1891](capstone-website/frontend/src/App.jsx#L1869-L1891) — 7 books. |

**Dead code:** `Results()` [App.jsx:1847-1853](capstone-website/frontend/src/App.jsx#L1847-L1853) and the entire `pages/ResultsSection.jsx` (419 lines) are defined but **not rendered** in the root tree at [App.jsx:2228-2254](capstone-website/frontend/src/App.jsx#L2228-L2254). Safe to delete or repurpose during overhaul.

---

## 4. Current backend endpoints

| Route | Method | Purpose | Data file(s) read |
|---|---|---|---|
| `/` | GET | Health / endpoint list | — |
| `/api/status` | GET | Total tasks/runs, models seen, tier counts | `tasks_all.json`, `experiments/results_v1/runs.jsonl` |
| `/api/tasks` | GET | Filtered task list (tier, category, type, search) | `tasks_all.json` |
| `/api/task/{task_id}` | GET | Single task + built prompt | `tasks_all.json` + `llm_runner.prompt_builder` |
| `/api/results/summary` | GET | Per-model `avg_score` / `pass_rate` / `avg_latency` / `n_tasks` | `runs.jsonl` |
| `/api/leaderboard` | GET | Sorted ranking from summary | `runs.jsonl` |
| `/api/results/by_type` | GET | task_type × model average scores | `runs.jsonl` |
| `/api/register-user` | POST | User-study registration (form data) | `user_study_results.json` |
| `/api/user-study` | POST | Run question against all 5 live models, return responses | live API calls (5 model clients) |
| `/api/user-study/vote` | POST | Persist vote (5 reasons × winner) | `user_study_results.json`, `vote_memory.json` |
| `/api/user-study/results` | GET | Vote tally + per-question history | `user_study_results.json` |
| `/api/user-study/questions` | GET | Saved questions list | `user_study_results.json` |

CORS [main.py:16-26](capstone-website/backend/main.py#L16-L26): `localhost:5173`, `localhost:3000`, plus `FRONTEND_URL` env (defaults to `*` if missing). `allow_methods=*`, `allow_headers=*`.

**Result file references — v1 only.** [main.py:30-32](capstone-website/backend/main.py#L30-L32) hard-codes
`experiments/results_v1/runs.jsonl`. **None of the v2 outputs are wired up:**
`results_v2/bootstrap_ci.json`, `robustness_v2.json`, `error_taxonomy_v2.json`,
`krippendorff_agreement.json`, `judge_dimension_means.json`,
`tolerance_sensitivity.json`, `self_consistency_calibration.json` — all sit on
disk in `experiments/results_v2/` but the backend has no endpoints for them.

---

## 5. Gap analysis

### 5.1 RQ framing — full rewrite required

Current site treats RQ1-5 as equal weight (0.20 each). [App.jsx:1893-1939](capstone-website/frontend/src/App.jsx#L1893-L1939) labels them:

| Site label (current) | New label per `audit/rq_restructuring.md` |
|---|---|
| RQ1 — Numerical & Statistical Accuracy | **RQ1 PRIMARY (40%) — How does external-judge validation differ from keyword scoring?** |
| RQ2 — Method Selection Accuracy | RQ2 SUPPORTING (15%) — Which Bayesian categories are hardest? (REGRESSION ~0.30) |
| RQ3 — Assumption Compliance | RQ3 SUPPORTING (15%) — Dominant failure mode = ASSUMPTION_VIOLATION 46.9% |
| RQ4 — Robustness | RQ4 SUPPORTING (15%) — Three rankings disagree (accuracy ≠ robustness ≠ calibration) |
| RQ5 — Confidence Calibration | RQ5 SUPPORTING (15%) — Zero high-confidence verbalised; hedge-heavy contrast with FermiEval |

Every `expandedStats` block in `RQS` references stale numbers (`Claude N-score 0.683`, `375 synthetic runs`, `119/143 E3`, etc.) — must be replaced with v2 numbers from `audit/rq_restructuring.md` and `experiments/results_v2/`.

### 5.2 Figures — site shows old R figures, new v2 figures unused

**Currently on site** ([visualizations.js](capstone-website/frontend/src/data/visualizations.js)) — 9 entries, all from `public/visualizations/png/`:

```
01_model_heatmap.png, 02_tier_radar_bar.png, 03_distributions.png,
05_failure_analysis.png, 07_latency_accuracy.png, 13_pass_rate.png,
14_difficulty.png, 15_bar_race.png/.gif, 16a_error_distribution.png
```

(Plus `04`, `06`, `08-12`, `16b`, `16c` PNGs exist on disk but are not in the manifest.)

**New figures in `report_materials/figures/` not on the site:**

| New figure | Status on site | Suggested home |
|---|---|---|
| `three_rankings.png` | NOT on site | RQ4 panel — replaces `02_tier_radar_bar.png` headline |
| `robustness_heatmap.png` | NOT on site | RQ4 panel companion |
| `error_taxonomy_hierarchical.png` | NOT on site | RQ3 panel — replaces `16a_error_distribution.png` |
| `bootstrap_ci.png` | NOT on site | About / Key Findings — accuracy ranking with CIs |
| `agreement_metrics_comparison.png` | NOT on site | **RQ1 panel (PRIMARY)** — α=0.55 visual |
| `self_consistency_calibration.png` | NOT on site | RQ5 panel |
| `judge_validation_scatter.png` | NOT on site | RQ1 panel (PRIMARY) |
| `judge_validation_by_model.png` | NOT on site | RQ1 panel (PRIMARY) |
| `calibration_reliability.png` | NOT on site | RQ5 panel |
| `calibration_ece_ranking.png` | NOT on site | RQ5 panel |
| `tolerance_sensitivity.png` | NOT on site | Methodology / RQ2 |
| `a1_failure_by_tasktype.png` | NOT on site | RQ3 panel |
| `a2_accuracy_by_category.png` | NOT on site | **RQ2 panel — REGRESSION ~0.30 evidence** |
| `a3_failure_heatmap.png` | NOT on site | RQ3 panel |
| `a4_robustness_by_perttype.png` | NOT on site | RQ4 panel |
| `a5_calibration_reliability.png` | NOT on site | RQ5 panel (or duplicate of `calibration_reliability.png`) |
| `a6_aggregate_ranking.png` | NOT on site | About / Key Findings |

**Delta:** site shows 9 charts → poster-ready library has **17 new figures**. None of the new ones are wired into `visualizations.js`. None of the figures are copied into `capstone-website/frontend/public/visualizations/png/` yet — they live in `report_materials/figures/`. Overhaul must `cp` (or symlink) and extend the manifest.

### 5.3 Headline numbers to update

| Current site copy | New headline (v2) |
|---|---|
| `1,230 total runs` (About CountUp) | Add: 2365 perturbation runs, 1229/1230 judge-scored, 473 perturbations |
| `0.683 Claude avg · 14.6% gap` (ABOUT_FINDINGS) | `claude 0.679 [0.655, 0.702]` (bootstrap CI from `bootstrap_ci.json`); separability resolved [F-3] |
| `E3 Assumption Violation 119/143 = 83%` (RQ3) | **`ASSUMPTION_VIOLATION 67/143 = 46.9%`** (Wang 2025-aligned). Old 119 figure is from a different L1 mapping — must replace. |
| `375 synthetic runs · ChatGPT 0.931 robustness` (RQ4) | **2365 perturbation runs · three rankings disagree · ChatGPT/DeepSeek noise-equivalent (Δ≈0)** |
| `RQ4 ≈ 0.91` (RQ4 metric badge) | Replace with three-rankings statement; ChatGPT Δ=−0.0007, DeepSeek Δ=+0.0006, claude Δ=0.0194, mistral Δ=+0.0135, gemini Δ=0.016 |
| `8 error categories E1-E8` (About CountUp + RQ3) | 4 L1 buckets × 9 L2 codes; only 4 L2 codes (E1, E3, E6, E7) actually hit. Disclose empties. |
| `Total calibration scores 1,230` (RQ5) | Empty high-confidence bucket (verbalized) → overconfidence reappears (consistency); contrast with FermiEval |
| (no mention) | **NEW headline:** 25% pass-flip on `assumption_compliance` (274/1094 runs); Krippendorff α=0.55 (Park 2025 questionable threshold); Spearman ρ=0.59 |

### 5.4 References — 10 papers to add

Site shows **5 papers + 7 textbooks**. Vault `40-literature/papers/` has **15 papers + 7 textbooks**. Already on site (5): Lu 2025, Nagarkar 2026, Liu 2025, Chen 2022, Wei 2022.

**10 new papers to add to `ABOUT_REFS`:**

| File | Citation | Why |
|---|---|---|
| `06-new-longjohn-bayesian-eval-2025.md` | Longjohn et al. (2025) | Bootstrap-CI motivation |
| `07-new-reasonbench-2025.md` | ReasonBench (2025) | Variance-as-first-class; three-rankings framing |
| `08-new-brittlebench-2026.md` | BrittleBench (2026) | Perturbation taxonomy adopted directly |
| `09-new-ice-cream-causal-2025.md` | Wang et al. (2025) "Ice Cream" | Independent ~47% assumption-violation reproduction |
| `10-new-llm-judge-empirical-2025.md` | Park et al. (2025), arXiv:2506.13639 | **RQ1 PRIMARY** — α-over-ρ for inter-rater reliability |
| `11-new-fermieval-2025.md` | FermiEval (2025) | RQ5 overconfidence contrast |
| `12-new-multi-answer-confidence-2026.md` | Multi-Answer (2026) | Consistency-based confidence (RQ5 future work) |
| `13-new-math-reasoning-failures-2026.md` | Math-Failures (2026) | Rubric-design validation; assumption-violation cluster |
| `14-new-judgment-becomes-noise-2025.md` | Judgment-Noise (2025) | Single-judge limitation (Limitations panel) |
| `15-new-statistical-fragility-2025.md` | Statistical Fragility (2025) | Separability tests motivation |

The "5 REFERENCED RESEARCH PAPERS" header on [App.jsx:2162](capstone-website/frontend/src/App.jsx#L2162) hardcodes the count — must change to "15".

### 5.5 Other content drift to fix

- [UserStudy.jsx:10](capstone-website/frontend/src/pages/UserStudy.jsx#L10): says **"Claude Sonnet 4.6"**, benchmark uses **4.5**. Inconsistent — pick one.
- [App.jsx:50](capstone-website/frontend/src/App.jsx#L50): `claude-sonnet-4-5` listed correctly here (good — UserStudy is the divergent one).
- [visualizations.js:111](capstone-website/frontend/src/data/visualizations.js#L111): "E7 Truncation 93 cases from 1024-token cap" — this was the v1 narrative; v2 token caps now `1024/2048/4096` per model and v2 taxonomy says `FORMATTING_FAILURE 18`. Update.
- `LiveResults` panel reads `results_summary.json` generated `2026-04-26` — already pre-v2; needs regeneration.
- "375 synthetic runs" appears twice (PIPELINE step 5 + RQ4) — both stale.
- Footer year "2026" is fine; AUA attribution looks correct.
- No Methodology page, no Limitations page, no Poster Companion page exist — would need to be created.

---

## 6. Mobile responsiveness assessment

**Status: ALREADY RESPONSIVE (good baseline).**

[index.css:91-184](capstone-website/frontend/src/index.css#L91-L184) carries a comprehensive mobile block at `@media (max-width: 900px)` and a tighter one at `@media (max-width: 480px)`, plus pointer-coarse handling at line 75. [App.css:613-631](capstone-website/frontend/src/App.css#L613-L631) adds nav + section padding rules at 1100/900/640.

What already works:
- Nav links collapse to hamburger; drawer in `Navbar.jsx`.
- All `1fr 1fr` and `250px 1fr` grids fall back to `1fr`.
- Task cards (`minmax(290px,1fr)`) collapse to single column.
- Pipeline circle scales 0.7 on mobile.
- Tier and scoring grids drop from 4-col to 2-col then 1-col.
- Heatmap rows allow horizontal scroll.
- Hero orbs hidden under 640.
- Custom global cursor disabled on touch.
- `prefers-reduced-motion` honoured.

Risk areas (worth manual QA on a phone):
- The 800px-wide circular pipeline diagram — scale 0.7 may still overflow narrow viewports.
- `MultiModelRadar` is 320+96+96 = 512px viewBox SVG; relies on `<svg>` intrinsic scaling — verify text legibility.
- `motion.div` filter:'blur(0px)' wrapper at root creates a stacking context (CLAUDE.md gotcha) — already mitigated by hoisting modals outside.
- Tasks sidebar at 250px may render under the grid on very narrow phones (works per the rule on line 116-119).

Verdict: existing site is **mostly responsive**. STANDARD overhaul should add a manual QA pass + tighten the few overflow risks.

---

## 7. Recommended overhaul scope

### MINIMAL — figure swaps + headline-number patching (~6h)

Files to modify:
- `frontend/src/data/visualizations.js` — replace 9 entries with the 17-figure v2 set
- `frontend/src/App.jsx` — RQS array (line 1893), ABOUT_FINDINGS (line 1941), PIPELINE (line 74), MODELS strengths copy (line 49), CountUp targets (line 2092), `LiveResults` text
- `frontend/src/pages/VizGallery.jsx` — `MODEL_META` Sonnet version, leaderboard caption
- `frontend/src/pages/UserStudy.jsx` — fix Sonnet 4.6 → 4.5
- `frontend/src/data/results_summary.json` — regenerate from v2 runs
- `frontend/src/data/stats.json` — add v2 counts (`perturbation_runs`, `judge_runs`)

Files to create:
- `frontend/public/visualizations/png_v2/` — copy 17 figures from `report_materials/figures/`

Out of scope: new pages, new endpoints, references update.

### STANDARD — figures + new pages + references + mobile QA (~16-20h, fits May 8)

Everything in MINIMAL plus:

Files to create:
- `frontend/src/pages/Methodology.jsx` — judge validation, bootstrap-CI separability, perturbation taxonomy, scoring-paths section. Pulls from `audit/methodology_continuity.md`.
- `frontend/src/pages/Limitations.jsx` — single-judge caveat (Park, Judgment-Noise), keyword-confidence weakness (MAC 2026), HALLUCINATION/E5/E8/E9 empties. Pulls from `audit/limitations_disclosures.md`.
- `frontend/src/pages/PosterCompanion.jsx` — embed poster figures with full captions; "click any panel for evidence trail". One-page abstract + RQ-by-RQ evidence dump.
- `frontend/src/data/references.js` — split out the 15-paper + 7-textbook list (currently inline in App.jsx)

Files to modify:
- `App.jsx` — restructure RQS to RQ1-PRIMARY framing; reorder About so RQ1 is the largest block. Add nav links for the three new pages (or three new sections). Replace 5-paper References block with 15-paper version + add Park 2025 as the load-bearing citation.
- `Navbar.jsx` — extend `NAV_SECTIONS` with `methodology`, `limitations`, `poster`.
- `backend/main.py` — add 4 endpoints: `/api/results/v2/bootstrap_ci`, `/api/results/v2/error_taxonomy`, `/api/results/v2/robustness`, `/api/results/v2/judge_agreement`. Each just `json.load` from `experiments/results_v2/`.

Plus: 30-min phone QA pass; tighten any overflow that surfaces.

### AMBITIOUS — STANDARD + interactives (~28-34h, risk for May 8)

Everything in STANDARD plus:

- Sortable + filterable rankings table (accuracy / robustness / reasoning toggle from `three_rankings.png` data)
- Filterable error taxonomy treemap with model + L1 + L2 facets
- Reliability-diagram interactive selector (5 models × 10 bins)
- Judge-vs-keyword scatter with hover-to-reveal task_id + delta
- Live demo of perturbation: pick base task → see 3 perturbations side by side with scores
- Methodology page becomes an interactive walkthrough (numbered steps with reveal-on-scroll)

The interactive components multiply the amount of D3/SVG work and would push past May 8. **Not recommended unless the May 8 deliverable is the static poster + a Day 5 buffer is reserved purely for this.**

---

## Recommendation given May 8 deadline

**STANDARD scope.** The existing site is already mobile-responsive and the
component machinery (cards, modals, radar, gallery) is solid — the bottleneck
is **content drift**, not engineering. Days 3-5 should be spent on:

1. Figure swap + manifest rewrite (Day 3 PM — half day)
2. RQ1-PRIMARY rewrite + reference expansion to 15 papers (Day 4)
3. Methodology + Limitations + Poster-Companion pages (Day 4-5)
4. Phone QA + last-pass content review (Day 5 PM)

Skip AMBITIOUS interactives — the static poster is the May 8 deliverable, and
the existing visualisation gallery already provides interactive Plotly HTMLs
for anyone who wants to dig deeper.

---

## Quick stats (for the Print block)

- Frontend framework + styling: **Vite 8 + React 19 SPA, plain CSS, no UI lib**
- Current page count: **8 anchored sections in 1 SPA** (Overview, About, Benchmark, Models, Tasks, Visualizations, UserStudy, References) + 1 dead `Results()` component not rendered
- Figure count delta: **9 on site → 17 new in `report_materials/figures/` not yet wired up** (net +8 to surface, with several swaps for stale ones)
- Recommended scope: **STANDARD** (~16-20h, fits May 8)
- Mobile responsive already: **YES** — `index.css` 900/480 + `App.css` 1100/900/640 breakpoints; nav drawer, grid collapse, pipeline scale, modal hoisting all in place
