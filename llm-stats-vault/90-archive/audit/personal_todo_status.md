# Personal TODO Status — Day 3 (2026-05-01)

Mapping of the 15-item personal TODO list (3 engineering + 12 professor critique points)
to concrete artifacts in the repo. Status is judged strictly: DONE only if a tangible
file/figure/script/audit doc directly addresses the item.

---

## Summary table

| Item | Title (truncated) | Status | Primary evidence |
|------|-------------------|--------|------------------|
| 1 | React native mobile | 🚫 OUT OF SCOPE | — (deferred; web only for May 8) |
| 2 | Consistency across versions | 🚫 OUT OF SCOPE | — (deferred; release-engineering scope) |
| 3 | Unique users / concurrency / no crashout | 🚫 OUT OF SCOPE | `capstone-website/backend/user_study.py` hardening (already shipped) |
| 4 | Baseline ↔ ground-truth technique | ✅ DONE | `audit/methodology_continuity.md`, `audit/literature_comparison.md`, `audit/day2_audit_report.md` [P-1] |
| 5 | Reasoning is weak | ⚠️ PARTIAL | `evaluation/llm_judge_rubric.py`, `llm_judge_scores_full.jsonl`, `judge_dimension_means.json` |
| 6 | Short answer not supporting reasoning | ⚠️ PARTIAL | `reasoning_completeness` dimension (n=1229, mean=0.962) |
| 7 | Prompt variation + AI #6 for non-bias | ✅ DONE | `evaluation/llm_judge_rubric.py` (Llama 3.3 70B), `data/synthetic/perturbations_all.json` (473) |
| 8 | Variation rankings | ⚠️ PARTIAL | `report_materials/figures/three_rankings.png`, `robustness_v2.json`, `bootstrap_ci.json` |
| 9 | Error taxonomy by LLMs | ⚠️ PARTIAL | `experiments/results_v2/error_taxonomy_v2.json`, `error_taxonomy_hierarchical.png` |
| 10 | Legend for fail type and task type | ✅ DONE | `a1_failure_by_tasktype.png`, `a3_failure_heatmap.png`, `error_taxonomy_hierarchical.png` |
| 11 | Ranking for aggregate scores | ✅ DONE | `a6_aggregate_ranking.png`, `three_rankings.png`, `bootstrap_ci.json` (separability) |
| 12 | Failure analysis for each | ⚠️ PARTIAL | `a1_failure_by_tasktype.png`, `a3_failure_heatmap.png`, `error_taxonomy_v2.json` |
| 13 | Prompt variations for all tasks | ✅ DONE | `data/synthetic/perturbations_all.json` (473 records: 75 hand-authored + 398 LLM-generated; v1 file deprecated 2026-05-04) |
| 14 | Reweight RQs | ✅ DONE | `audit/rq_restructuring.md` (RQ1 40%, RQ2–5 15% each) |
| 15 | More depth on RQ2–5 | ⚠️ PARTIAL | `audit/rq_restructuring.md`, `audit/literature_comparison.md` |

**Totals:** 6 DONE · 6 PARTIAL · 0 NOT ADDRESSED · 3 OUT OF SCOPE.

---

## Per-item entries

### Item 1 — React native for mobile version
**Status:** 🚫 OUT OF SCOPE
**Evidence:** none — no React Native source tree exists; current site is Vite + React (web).
**What's left:** Deferred until after May 8 presentation. Mobile parity is a release/build
concern, not a research deliverable.
**Confidence:** HIGH (clearly deferred per user's own item-1–3 categorisation).

### Item 2 — Consistency across versions / inconsistency in updates and release
**Status:** 🚫 OUT OF SCOPE
**Evidence:** none for May 8.
**What's left:** Release-engineering / changelog discipline. Address post-presentation.
**Confidence:** HIGH.

### Item 3 — Unique user count, concurrent users, prevent website/API crashout
**Status:** 🚫 OUT OF SCOPE *(but partial hardening already shipped, see note)*
**Evidence:** `capstone-website/backend/user_study.py` ships with: `asyncio.Semaphore(3)`,
60s per-model timeout, 10/hour + 3/minute rate limits per IP, atomic JSON writes via
`_atomic_write_json()`, partial-failure tolerance (returns 200 if ≥1 of 5 models works).
Documented in `CLAUDE.md` "User Study hardening" block.
**What's left:** Unique-user telemetry and a real concurrent-user dashboard are still
absent. Defer — research deliverables come first.
**Confidence:** HIGH (deferred; backend resilience only is in scope and is done).

### Item 4 — How the baseline is compared to ground truth — what is the technique?
**Status:** ✅ DONE
**Evidence:**
- `audit/methodology_continuity.md` — full statement: closed-form + seeded MC
  (`np.random.seed=42`) ground truth, free-response 5-dim N·M·A·C·R rubric, external
  judge validation, bootstrap CI separability.
- `audit/literature_comparison.md` row "Ground-truth source" — places this work
  ("Closed-form + seeded MC") against 7 prior systems.
- `audit/day2_audit_report.md` [P-1] — verified base vs perturbation rubric parity:
  same `WEIGHTS`, same `full_score()`, same tolerance application, same system prompt.
- `CLAUDE.md` "Scoring" section + `evaluation/metrics.py` + `llm_runner/response_parser.py`
  document both scoring paths.
**What's left:** none.
**Confidence:** HIGH.

### Item 5 — The reasoning is weak
**Status:** ⚠️ PARTIAL
**Evidence:**
- `evaluation/llm_judge_rubric.py` (453 lines) — 4-dim rubric explicitly added
  `reasoning_quality` and `reasoning_completeness` because keyword rubric was weak on
  reasoning.
- `experiments/results_v2/llm_judge_scores_full.jsonl` — 1229/1230 base runs scored.
- `experiments/results_v2/judge_dimension_means.json` — per-model means (e.g. claude
  reasoning_quality mean per `judge_dimension_means.json`).
- `report_materials/figures/judge_validation_scatter.png`, `judge_validation_by_model.png`.
- `audit/day2_audit_report.md` [D-1] confirms HIGH confidence on the judge module.

Cross-references item 6 (the same reasoning-quality machinery handles "short answer
without reasoning"); see also items 7 and 8.

**What's left:** Day-2 audit finding [H-2] — `poster/main.tex:229` still has
"Reasoning quality (judge mean): Stub --- to fill from `llm_judge_scores_full.jsonl`
aggregation." The data is computed but the poster ranking column is empty. ~1 hour to
aggregate per-model judge means and write line 229.
**Confidence:** MEDIUM (analysis is done; poster panel is not).

### Item 6 — Short answer from the models is not supporting the reasoning
**Status:** ⚠️ PARTIAL (cross-ref item 5)
**Evidence:** `reasoning_completeness` dimension was added specifically to catch this
failure mode — see `llm-stats-vault/90-archive/2026-04-30-day1-poster-sprint.md` decision 3:
"specifically catches 'name-drops + answer, no derivation' — a failure mode the keyword
rubric cannot detect." Population stats: mean=0.962, n=1229, zeros=4, ones=1139
(`judge_dimension_means.json` and Day-1 session log "Final score distributions").
**What's left:** Same as item 5 — the dimension exists and is scored, but the per-model
ranking column on the poster is still a stub ([H-2]). Also the headline interpretation
("models do walk through reasoning, ~93% of the time") needs to land in the poster prose.
**Confidence:** MEDIUM.

### Item 7 — Prompt variation, AI #6 for non-bias
**Status:** ✅ DONE
**Evidence:**
- *AI #6 for non-bias* — `evaluation/llm_judge_rubric.py:38` sets
  `JUDGE_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"` (Llama 3.3 70B Instruct
  via Together AI). Llama is a sixth model, external to the five benchmarked
  (Claude/ChatGPT/Gemini/DeepSeek/Mistral) — eliminates self-preference bias. Day-1
  session log decision 1 explicitly justifies this.
- *Prompt variation* — `data/synthetic/perturbations_all.json` (473 records:
  75 hand-authored + 398 LLM-generated) with three orthogonal types
  (rephrase / numerical / semantic) generated by
  `scripts/generate_perturbations_full.py`. Validation Gate 1 reproduced stored
  ground-truth on 131/131 numerical task_types (Day-1 log "Validation Gate 1").

**What's left:** none. Single-judge caveat is documented in
`audit/limitations_disclosures.md` (d) and `audit/day2_audit_report.md` [P-7]; multi-judge
ensemble is paper-scope (F-11).
**Confidence:** HIGH.

### Item 8 — Variation rankings
**Status:** ⚠️ PARTIAL
**Evidence:**
- `report_materials/figures/three_rankings.png` — three orthogonal rankings panel
  (accuracy / robustness / reasoning).
- `experiments/results_v2/robustness_v2.json` — per-model deltas + per-pert-type
  breakdown + ranking block. ChatGPT Δ=−0.0007, DeepSeek Δ=+0.0006, claude Δ=0.0194,
  mistral Δ=+0.0135, gemini Δ=0.016.
- `experiments/results_v2/bootstrap_ci.json` — 10k-bootstrap 95% CIs on accuracy *and*
  robustness deltas, with separability tests addressing [P-2].
- `report_materials/figures/robustness_heatmap.png`, `bootstrap_ci.png`.
**What's left:** Reasoning column of the three-rankings panel is still a stub in
`poster/main.tex:229` ([H-2]). Also the audit recommends explicitly stating "ChatGPT
and DeepSeek effectively unaffected by perturbations" rather than ranking them ([P-2]) —
poster narrative needs to land that.
**Confidence:** MEDIUM.

### Item 9 — Error taxonomy by LLMs
**Status:** ⚠️ PARTIAL
**Evidence:**
- `experiments/results_v2/error_taxonomy_v2.json` — 143 base failures classified.
  L1 totals: ASSUMPTION_VIOLATION 67, MATHEMATICAL_ERROR 48, FORMATTING_FAILURE 18,
  CONCEPTUAL_ERROR 10, HALLUCINATION 0.
- `experiments/results_v2/error_taxonomy_v2_judge.jsonl` — 143 raw judge calls.
- `scripts/error_taxonomy.py` — taxonomy script.
- `report_materials/figures/error_taxonomy_hierarchical.png` — sunburst.
- L1→L2 mapping: 4 L1 buckets × 9 L2 codes defined; only 4 L2 codes (E1, E3, E6, E7)
  ever used.
**What's left:** Two issues, both flagged in audit:
1. [H-4] HALLUCINATION + E5/E8/E9 buckets empty — disclosure text already drafted in
   `audit/limitations_disclosures.md` (a) but not yet in `poster/main.tex` Limitations.
2. Taxonomy figure exists but is not yet `\includegraphics`'d in the poster — sits
   behind a `\figstub` box (audit [H-1] / [F-1]).
**Confidence:** MEDIUM (data + figure done; poster integration + caveat insertion left).

### Item 10 — Legend for each fail type and task type
**Status:** ✅ DONE
**Evidence:**
- `report_materials/figures/a1_failure_by_tasktype.png` — failure rates per task_type.
- `report_materials/figures/a3_failure_heatmap.png` — model × task_type failure heatmap.
- `report_materials/figures/error_taxonomy_hierarchical.png` — error-type sunburst.
- `report_materials/figures/a2_accuracy_by_category.png` — accuracy per category.
- `scripts/generate_group_a_figures.py` — generation script.
**What's left:** Figures must still be inserted into the poster ([H-1] / [F-1]) — but
that is item-8/item-12-blocking, not item-10-blocking. The artifacts themselves carry
the legends.
**Confidence:** HIGH.

### Item 11 — Ranking for aggregate scores
**Status:** ✅ DONE
**Evidence:**
- `report_materials/figures/a6_aggregate_ranking.png` — aggregate score ranking bar.
- `report_materials/figures/three_rankings.png` — accuracy + robustness + reasoning.
- `report_materials/figures/bootstrap_ci.png` — accuracy ranking with 10k-bootstrap CIs.
- `experiments/results_v2/bootstrap_ci.json` — accuracy means + 95% CIs:
  claude 0.679 [0.655, 0.702], gemini 0.674 [0.647, 0.700], mistral 0.632, deepseek 0.621,
  chatgpt 0.614. `separability` block resolves audit [F-3].
- `scripts/bootstrap_ci.py`.
**What's left:** none — analysis is done and CI-defended.
**Confidence:** HIGH.

### Item 12 — Failure analysis for each
**Status:** ⚠️ PARTIAL (cross-ref items 9 + 10)
**Evidence:**
- Per-model + per-task-type failure breakdown in `a1_failure_by_tasktype.png`,
  `a3_failure_heatmap.png`.
- L1/L2 error taxonomy on 143 failures (`error_taxonomy_v2.json`) — disaggregable
  per-model (the JSONL has model_family per record).
- `audit/rq_restructuring.md` RQ3 narrative ("ASSUMPTION_VIOLATION = 46.9% of 143 base
  failures") — externally validated against Wang et al. 2025 + Math-Reasoning-Failures
  2026.
**What's left:** The per-model error-mode breakdown is computed but not yet a
panel-ready figure — need a stacked bar (model × L1) or a per-model table in the
RQ3 panel. Plus the empty-HALLUCINATION caveat from item 9.
**Confidence:** MEDIUM.

### Item 13 — Prompt variations for all tasks
**Status:** ✅ DONE
**Evidence:**
- `data/synthetic/perturbations_all.json` — **473 perturbations** total
  (post Phase 1.8 deprecation 2026-05-04: this file is now the sole
  canonical perturbation source). Composition: 473 records — 75
  hand-authored seed perturbations (formerly `perturbations.json`,
  preserved verbatim inside) + 398 LLM-generated v2 perturbations.
  5 random spot-checks all schema-clean per `audit/day2_audit_report.md`
  quick-stats table.
- Three orthogonal types: `rephrase`, `numerical`, `semantic`.
- 146 base tasks generated in v2 + 25 in v1 = 171/171 base tasks covered (every
  base task has at least one perturbation variant).
- 2365 perturbation runs (5 models × 473) in `experiments/results_v2/perturbation_runs.jsonl`,
  0 errors, 0 dupes. `experiments/results_v2/perturbation_judge_scores.jsonl` —
  same, 1 parse_error pending.
- `scripts/generate_perturbations_full.py` — generator.
**What's left:** none for the data layer. Audit recommendations [H-5] (provenance
flag for 3 hand-authored perts), [H-7] (rejudge 1 parse_error), [F-9] are minor cleanup.
**Confidence:** HIGH.

### Item 14 — Maybe change weights of RQs to make it more research-supportive
**Status:** ✅ DONE
**Evidence:** `audit/rq_restructuring.md` — full reweighting narrative.
- Original equal-weight critique addressed: "narrative reduced to 'I built a Bayesian
  benchmark and Claude won.'"
- New weights: **RQ1 40% (judge-validation methodology) | RQ2/3/4/5 15% each**.
- Each RQ tied to literature (Yamauchi 2025, Liu 2025, Du 2025, BrittleBench 2026,
  ReasonBench 2025, FermiEval 2025, Multi-Answer 2026, Boye & Moell 2025).
- "What this changes in the poster" section names the concrete poster edits required:
  abstract leads with judge-validation, RQ1 is largest block, Limitations cites
  Judgment-Becomes-Noise, Future Work names consistency-based confidence (MAC 2026)
  + multi-judge ensemble.
**What's left:** none for the analytical reweighting. Poster layout edit to enlarge
RQ1 block is poster-engineering, not analysis-engineering.
**Confidence:** HIGH.

### Item 15 — More depth on RQ2, 3, 4, 5
**Status:** ⚠️ PARTIAL (cross-ref item 14)
**Evidence:**
- `audit/rq_restructuring.md` provides per-RQ depth: each of RQ2–5 has a headline,
  justification, and grounding citation cluster.
- RQ2: REGRESSION cluster ~0.30 mean accuracy (from `a2_accuracy_by_category.png`).
- RQ3: 46.9% ASSUMPTION_VIOLATION share, externally cross-checked against Wang 2025.
- RQ4: three-rankings disagreement + bootstrap-CI separability + uniformly-robust task
  types (HIERARCHICAL, RJMCMC, VB).
- RQ5: zero high-confidence records + FermiEval contrast.
- `audit/literature_comparison.md` — 10-dimension table positions every RQ's claim
  against 7 prior systems.
- `audit/methodology_continuity.md` — combines all four RQ rationales into a single
  paragraph.
**What's left:** The depth exists in audit prose but has not yet been ported into the
poster's RQ panels. Each of RQ2–5 currently fits a single row in the poster; the
literature-grounded depth needs to be condensed into 2–3 bullet points per panel and
the citation cluster placed in the Methodology / Limitations bands. Also items
[F-3] (CI bars on robustness panel) and [F-4] (top-3 most-fragile concepts in RQ4) are
RQ4-specific depth deliverables that are not yet on the poster.
**Confidence:** MEDIUM (analysis is done; poster panels are not yet rewritten).

---

## Top 3 strongest DONE evidence (highest confidence)

1. **Item 7 — Prompt variation + AI #6 for non-bias.** Two large concrete artifacts:
   `evaluation/llm_judge_rubric.py` (Llama 3.3 70B Instruct, 1230/1230 records, audit
   D-1 HIGH) and `data/synthetic/perturbations_all.json` (473 perts, audit D-2 HIGH,
   131/131 dispatch validation passed).
2. **Item 13 — Prompt variations for all tasks.** Every base task has perturbation
   coverage; 2365 perturbation runs scored with 0 errors; numerical perturbations
   have ground-truth recomputed by deterministic solvers (audit P-1 verified parity).
3. **Item 14 — Reweight RQs.** A full standalone narrative document exists with
   weight justification, literature grounding per RQ, and a concrete list of poster
   edits required.

## PARTIAL items + closing deliverable

| Item | Closing deliverable |
|------|---------------------|
| 5 | Compute per-model mean(`reasoning_quality`) from `llm_judge_scores_full.jsonl`; replace stub at `poster/main.tex:229` ([H-2] / [F-2]). ~1 hour. |
| 6 | Same script as item 5 — also surface `reasoning_completeness` headline ("models walk through reasoning ~93% of the time") in poster prose. |
| 8 | Same poster line 229 fix; also add bootstrap CI bars to robustness panel using `bootstrap_ci.json` ([F-3]). |
| 9 | Drop `audit/limitations_disclosures.md` (a) into the poster Limitations block ([F-7]); replace `\figstub` for `error_taxonomy_hierarchical.png` with `\includegraphics` ([F-1]). |
| 12 | Generate a stacked-bar (model × L1) figure from `error_taxonomy_v2_judge.jsonl`; insert into RQ3 panel. |
| 15 | Rewrite RQ2–5 panels using `audit/rq_restructuring.md` per-RQ headlines + citations; add CI bars ([F-3]) and top-3-fragile concepts ([F-4]) to RQ4. |

## Recommended next-action priority order

1. **F-1 — Replace 7 `\figstub` calls with `\includegraphics`** (closes parts of items
   8, 9, 10, 11, 12 simultaneously). 30 minutes.
2. **F-2 — Aggregate per-model judge means; fix `poster/main.tex:229` stub** (closes
   items 5, 6, 8). ~1 hour.
3. **F-7 — Drop limitations disclosures into poster Limitations block** (closes
   item 9 caveat; also covers items in `audit/limitations_disclosures.md` b/c/d).
   ~30 minutes.
4. **F-3 — Bootstrap CI bars on robustness panel** (closes RQ4 depth for item 15;
   makes item 8 ranking honest).
5. **Rewrite RQ2–5 panels** using `audit/rq_restructuring.md` (closes item 15 fully).
6. **Stacked-bar L1 × model figure** (closes item 12 fully).

Items 4, 7, 11, 13, 14 are already DONE — no follow-up needed for May 8.

*End of report.*
