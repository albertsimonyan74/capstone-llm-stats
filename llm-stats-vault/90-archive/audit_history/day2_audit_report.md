# Day 2 Audit Report — DS 299 Capstone (Bayesian Stats Benchmark)

Read-only audit. No data, scripts, figures, or commits modified.

Date: 2026-04-30 (end of Day 2). Poster sprint Day 3 = 2026-05-01..05-07. Presentation = 2026-05-08.

`day1_handoff.md` does not exist at repo root. Day-1 context sourced from `llm-stats-vault/90-archive/2026-04-30-day1-poster-sprint.md` (referenced in CLAUDE.md vault workflow memory).

---

## Quick stats verified during audit

| Artifact | Records | Errors | Notes |
|---|---:|---:|---|
| `data/synthetic/perturbations_all.json` | 473 | 0 | 75 v1 + 398 v2; 5 random spot-checks all schema-clean |
| `experiments/results_v2/perturbation_runs.jsonl` | 2365 | 0 | unique run_ids=2365, unique (model,task_id)=2365, no dupes |
| `experiments/results_v2/perturbation_judge_scores.jsonl` | 2365 | 1 | parse_error on `STATIONARY_01_numerical` |
| `experiments/results_v2/llm_judge_scores_full.jsonl` | 1230 | 0 | (per Day-1 log; not re-counted line-by-line) |
| `experiments/results_v2/error_taxonomy_v2_judge.jsonl` | 143 | 0 | only 4 of 9 E-codes used |
| `experiments/results_v2/calibration.json` | 5 models | — | every model has `high` bucket = 0 records |
| `experiments/results_v2/robustness_v2.json` | 2365 | 0 | n_perturbations matches pert_runs |
| `experiments/results_v2/tolerance_sensitivity.json` | 1180/1230 | — | 50 runs unscored (CONCEPTUAL has no numeric_targets) |
| `report_materials/figures/` | 8 PNGs | — | all referenced files present |

---

# 1. DONE — fully implemented and validated

**[D-1] External LLM judge (Llama 3.3 70B / Together AI) — 4-dimension rubric**
Confidence: HIGH
Finding: 1230/1230 base runs scored 100%. Schema clean, score ranges in [0,1], all 4 dimensions populated. Cross-provider consistency check (Groq vs Together) showed scores nearly identical → judge behavior depends on model+prompt, not provider. Strictness verification done on 7 borderline cases (`scripts/inspect_judge_strictness.py`). Resume-safe + retries on 429/503/parse.
Evidence: `evaluation/llm_judge_rubric.py` (453 lines); `experiments/results_v2/llm_judge_scores_full.jsonl` (Day-1 log §"Full 1,230-run judge scaling"); 1 originally-stuck record regenerated with max_tokens=2048 (Day-1 §"Pre-launch fixes 2.").

**[D-2] Perturbation generator + numerical solver dispatch**
Confidence: HIGH
Finding: 473 perturbations generated (75 v1 + 398 v2). Validation Gate 1 reproduced stored ground-truth across all 31 numerical task_types (131/131 pass). Three failures (DIRICHLET_01, REGRESSION_05, MLE_EFFICIENCY_02) hand-recovered via solver verification.
Evidence: `scripts/generate_perturbations_full.py` referenced in Day-1 log §"Perturbation generator"; `data/synthetic/perturbations_all.json` 473 records, all required fields present.

**[D-3] Perturbation benchmark scoring (5 models × 473 perts)**
Confidence: HIGH
Finding: 2365 runs, 0 errors, 0 dupes. Same `full_score` (Path A keyword rubric) used as base benchmark — identical weights, tolerances, structure-keyword logic. Same `_SYSTEM_PROMPT` via shared `model_clients.py` clients.
Evidence: `scripts/score_perturbations.py:170` calls `full_score(raw, task)`; `llm_runner/model_clients.py:24` shared `_SYSTEM_PROMPT`.

**[D-4] Perturbation judge scoring**
Confidence: HIGH
Finding: 2365 records, 1 parse_error, 4 dimensions populated, score distribution mirrors base-judge means (method=0.93, assumption=0.44, reasoning=0.89, completeness=0.96).
Evidence: `experiments/results_v2/perturbation_judge_scores.jsonl`.

**[D-5] Robustness analysis (RQ4)**
Confidence: HIGH
Finding: Per-model deltas + per-pert-type breakdown + per-task-type heatmap written. 2365/2365 perturbations matched a base score (missing_base=0). Heatmap PNG generated at 300 DPI, transparent. Three-rankings figure wired to live JSON.
Evidence: `experiments/results_v2/robustness_v2.json`; `report_materials/figures/robustness_heatmap.png`; `scripts/robustness_analysis.py`; `scripts/three_rankings_figure.py`.

**[D-6] Calibration analysis (RQ5)**
Confidence: MEDIUM (see [P-3])
Finding: Per-model ECE computed via 4 fixed buckets keyed to claimed confidence (0.3 / 0.5 / 0.6 / 0.9). Reliability diagram + ECE bar produced. ChatGPT best (ECE=0.063), DeepSeek worst (0.179).
Evidence: `experiments/results_v2/calibration.json`; `scripts/calibration_analysis.py`; figures present.

**[D-7] Keyword vs judge agreement**
Confidence: MEDIUM (see [H-3])
Finding: 25.0% pass-flip on `assumption_compliance` (keyword PASS, judge FAIL on 274/1094 runs). Spearman ρ=0.59 on assumption dimension; near-zero on method_structure (saturation effect). Both PNG figures + JSONs exist.
Evidence: `experiments/results_v2/keyword_vs_judge_agreement.json`; `experiments/results_v2/top_disagreements_assumption.json`.

**[D-8] Tolerance sensitivity sweep**
Confidence: HIGH
Finding: Three tolerance levels (tight/default/loose) sweep across 1180 numeric-bearing runs. Ranking changes (`ranking_stable_across_levels=false`) — useful methodology disclosure.
Evidence: `experiments/results_v2/tolerance_sensitivity.json`.

**[D-9] task_type derivation utility**
Confidence: HIGH
Finding: `task_type_from_id` regex tested inline against 9 representative cases. Adopted by 2 downstream scripts.
Evidence: `baseline/utils_task_id.py:21`.

---

# 2. HALF-IMPLEMENTED — exists but fragile or incomplete

**[H-1] Poster integration of figures**
Severity: MAJOR
Finding: All 8 generated PNGs (three_rankings, robustness_heatmap, calibration_reliability, calibration_ece_ranking, error_taxonomy_hierarchical, judge_validation_scatter, judge_validation_by_model, tolerance_sensitivity) exist in `report_materials/figures/`, but `poster/main.tex` references them via `\figstub{...}` placeholder boxes (italic text inside an `\fbox{}`) — none are actually `\includegraphics`'d. Six `\figstub` calls live in lines 218, 240, 267, 281, 293, 307, 355.
Evidence: `poster/main.tex:46-50` defines stub macro; lines 218, 240, 267, 281, 293, 307, 355 use it.
Recommendation: Replace all 7 `\figstub` calls with `\includegraphics[width=0.95\linewidth]{...}` before May 8.

**[H-2] Reasoning-quality ranking still a TODO inside poster**
Severity: MAJOR
Finding: Poster line 229-230 reads "Reasoning quality (judge mean): Stub --- to fill from `llm_judge_scores_full.jsonl` aggregation." A full per-model judge mean is sitting in `llm_judge_scores_full.jsonl` — never aggregated and inserted.
Evidence: `poster/main.tex:229`.
Recommendation: 30-min script to compute per-model mean(reasoning_quality, assumption_compliance, method_structure, reasoning_completeness) and write the third column of the three-rankings panel.

**[H-3] keyword_vs_judge_agreement per_task_type breakdown polluted**
Severity: MINOR
Finding: `per_task_type` block in `keyword_vs_judge_agreement.json` has 104 keys instead of expected 38. v1 perturbation runs in `results_v1/runs.jsonl` carry a `task_type` field equal to the perturbed id (`BAYES_FACTOR_01_numerical` etc.), and `join_records` uses `r.get("task_type") or derive_task_type(...)` — so the stored value wins and the derive_task_type fallback never runs. Overall + per-model metrics are unaffected (they aggregate by model_family); only the per_task_type breakdown is bloated.
Evidence: `scripts/keyword_vs_judge_agreement.py:111`; `experiments/results_v2/keyword_vs_judge_agreement.json` per_task_type keys.
Recommendation: Force `derive_task_type(r["task_id"])` instead of `r.get("task_type")`. One-line fix; rerun the script.

**[H-4] HALLUCINATION + OVERCONFIDENCE buckets empty in error taxonomy**
Severity: MAJOR
Finding: `experiments/results_v2/error_taxonomy_v2.json` shows L1 totals = ASSUMPTION_VIOLATION 67, MATHEMATICAL_ERROR 48, FORMATTING_FAILURE 18, CONCEPTUAL_ERROR 10, **HALLUCINATION 0**. Out of 9 defined L2 codes, only 4 ever used (E1, E3, E6, E7). E5 (overconfidence), E8 (hallucination), E9 (unclassified) never selected. `repaired_pairs` count = 0 → Llama is not even proposing those codes. The judge prompt's L2 list pushes E5/E8/E9 toward the HALLUCINATION L1 with a "only if nothing else fits" caveat on E9 — Llama appears to take that as "avoid this bucket."
Evidence: `experiments/results_v2/error_taxonomy_v2.json` l1/l2 totals; `scripts/error_taxonomy.py:125` E9 caveat.
Recommendation: Either rerun with a less-deprecating prompt for HALLUCINATION codes (and a worked example for each), OR collapse the taxonomy to the 4 codes actually used and disclose this in the poster + paper.

**[H-5] Hand-authored perturbations not flagged in JSON**
Severity: MINOR
Finding: 3 numerical perturbations (DIRICHLET_01_numerical_v2, REGRESSION_05_numerical_v2, MLE_EFFICIENCY_02_numerical_v2) were hand-authored after LLM JSON-generation failures (Day-1 log §"Full run results"). None of these records carry a `hand_authored: true` flag in `perturbations_all.json` — only the same `perturbation_note` field every other record has. There is no way to filter them at analysis time.
Evidence: spot-check via `python -c "json.load(open('data/synthetic/perturbations_all.json'))"` confirms only `perturbation_note` differentiates them.
Recommendation: Add a `provenance: "hand_authored"` field on those 3 records (or document them separately in `data/synthetic/HAND_AUTHORED.md`).

**[H-6] Confidence "high" bucket has 0 records across all 5 models**
Severity: MAJOR (see also [P-3])
Finding: Every model's `per_bucket.high.n` is 0. ECE only weights populated buckets, so the `high` row contributes nothing to the reported ECE numbers. `extract_confidence` is keyword-based (hedge-words ↓, definitive-words ↑) and capped at 0.9 only when several definitive phrases stack — none of the 1230 base runs trigger that. The ECE numbers therefore measure only how well models' "medium" + "low" + "unstated" buckets agree with claimed values, not whether they are over/under-confident at the high end.
Evidence: `experiments/results_v2/calibration.json`; Day-1 log §"Calibration analysis (RQ5)" already flags this caveat at the bottom.
Recommendation: Either disclose explicitly in the poster's Limitations block ("no model produced enough definitive linguistic markers to land in the high-confidence bucket"), or replace keyword-based extraction with a judge-rated certainty pass. The poster currently mentions "keyword-based" but does not warn that the high-bin is empty — readers will assume balanced bins.

**[H-7] 1 missing perturbation judge score (parse_error)**
Severity: MINOR
Finding: `STATIONARY_01_numerical` (run_id `ea451f6b-c8de-462f-b097-05170bc4c2de`) sits as `parse_error` in `perturbation_judge_scores.jsonl`. Day-1 fix worked for the 1 previously stuck base-run record — but that fix was a one-off script (`scripts/_oneoff_rejudge_vb04_mistral.py`), not generalised. The new errored record is undocumented and could quietly bias perturbation-judge means.
Evidence: 1 errored record found via line-by-line scan.
Recommendation: Re-run the same one-off rejudge script with max_tokens=2048 against this new record.

**[H-8] No automated check that base-task vs perturbation prompts share the same system prompt**
Severity: MINOR
Finding: Both base and perturbation runs route through `llm_runner/model_clients.get_client(family).query(prompt, tid)`, which is hard-coded to `_SYSTEM_PROMPT` (line 24, 154, 211, 275, 331, 387). Verified by grep — identical. No regression test asserts this stays true if anyone adds a new client.
Evidence: `llm_runner/model_clients.py:24`.
Recommendation: Trivial test: `assert all(c._system_prompt == _SYSTEM_PROMPT for c in _CLIENTS.values())` — paper-scope.

**[H-9] Resume-safety in score_perturbations key choice**
Severity: MINOR
Finding: `score_perturbations.py:78` keys completion by `(model_family, task_id)` and skips if `raw_response` non-empty AND no error. This means a partial run with empty response (`raw=""`) would NOT be skipped — but a run that errored with a fully-populated response WOULD be re-attempted. Edge case is fine in practice; mention as a minor robustness gap.
Evidence: `scripts/score_perturbations.py:78`.

**[H-10] Tolerance sensitivity scope mismatch**
Severity: INFO
Finding: Tolerance sweep tested on 1180/1230 = 246-50 runs per model. The 50 missing per model = 10 CONCEPTUAL × 5 models. CONCEPTUAL has no numeric_targets, so excluding is correct. Document this denominator in the poster.
Evidence: `experiments/results_v2/tolerance_sensitivity.json`.

---

# 3. POTENTIAL ERRORS — validity threats to research claims

**[P-1] Base vs perturbation rubric parity — VERIFIED IDENTICAL**
Severity: INFO (no defect found, audited as control)
Finding: Both `experiments/run_benchmark` (base) and `scripts/score_perturbations.py` (perturbations) call `llm_runner.response_parser.full_score()`. Same WEIGHTS dict (N=M=A=C=R=0.20), same tolerance application (`numeric_targets[i].full_credit_tol` and `zero_credit_scale` per-target), same pass threshold (0.5), same `extract_confidence` heuristic. System prompt identical (single `_SYSTEM_PROMPT` constant). Perturbation numerical targets are recomputed by the dispatched solver before scoring.
Evidence: `scripts/score_perturbations.py:34,170`; `llm_runner/model_clients.py:24`.
Recommendation: Cite this control in the poster Methodology block — strengthens validity claim.

**[P-2] Robustness delta sign — verified, but interpret with care**
Severity: MINOR
Finding: `delta = base_mean - pert_mean` ⇒ positive = base better than pert ⇒ less robust. ChatGPT Δ=−0.0007 means pert mean is 0.0007 *higher* than base mean — well within stochastic noise (per-pert per-model SD on `final_score` is on the order of 0.2–0.3; with n=473 the ~0.001 effect has SE ≈ 0.012). DeepSeek Δ=+0.0006 is also within noise. The robustness ranking is reliable for top-rung vs bottom-rung separation (claude Δ=0.019 vs chatgpt Δ=−0.001) but the order between the top three is not statistically distinguishable.
Evidence: `experiments/results_v2/robustness_v2.json` per_perturbation_type values; `scripts/robustness_analysis.py:74`.
Recommendation: Bootstrap CI on each Δ before claiming a robustness ranking. Without CI, the poster should state "ChatGPT and DeepSeek effectively unaffected by perturbations" rather than "ranked best."

**[P-3] Calibration ECE skew — see also [H-6]**
Severity: MAJOR
Finding: ECE is computed as Σ (n_b/N) · |acc_b - claim_b| over 4 buckets, but `high` is empty for all 5 models, so the metric is effectively a 3-bucket weighted MAE. The bins are not even close to evenly populated: most weight sits on `medium` and `unstated` (the latter is the keyword-extractor's default 0.5 fall-through, NOT a bucket the model claimed). The poster headline "ChatGPT best calibrated (ECE=0.063)" is true under this 4-bucket scheme but does not test high-confidence calibration at all. Confidence labels are extracted from `raw_response` AFTER scoring → no leakage. But the labels themselves are noisy: any response with no recognized hedge or definitive phrase falls into `unstated`, which captures 47–63% of every model's runs.
Evidence: `experiments/results_v2/calibration.json` per_bucket; `scripts/calibration_analysis.py:65-79` bucket function.
Recommendation: Disclose in the poster Limitations: (a) zero `high` bucket records, (b) `unstated` is keyword-extractor fall-through, (c) ECE is therefore a coarse 3-bin metric. Stretch fix: compute a second ECE with token-logprob confidence where supported (Anthropic + OpenAI APIs).

**[P-4] Judge prompt parity across base vs perturbation**
Severity: MINOR
Finding: Same prompt template (`JUDGE_PROMPT_TEMPLATE` in `evaluation/llm_judge_rubric.py:44-95`), same `_format_checks()` for `required_*_checks`, same model + temperature=0. Perturbation task specs preserve `required_structure_checks` and `required_assumption_checks` from the base task verbatim (rephrase + semantic) or recomputed identically (numerical). No structural bias in the judge prompt that would inflate perturbation scores.
Evidence: `evaluation/llm_judge_rubric.py:44`; `data/synthetic/perturbations_all.json` spot-checked records.
Recommendation: None — passes audit.

**[P-5] Judge score inflation on perturbations — empirically not observed**
Severity: INFO
Finding: Comparing means: base set (n=1229) → method=0.946, assumption=0.446, reasoning=0.903, completeness=0.962. Pert set (n=2364) → method=0.934, assumption=0.439, reasoning=0.889, completeness=0.958. Pert means are ~0.01 LOWER than base means across all 4 dimensions. No inflation. The hypothesis "easier rephrasings get higher judge scores" is not supported.
Evidence: `experiments/results_v2/llm_judge_scores_full.jsonl`; `experiments/results_v2/perturbation_judge_scores.jsonl` aggregates printed via grep + python.

**[P-6] Excluded-task pattern in keyword-vs-judge agreement**
Severity: MINOR
Finding: 21 base task_ids (out of 171) have empty `required_assumption_checks`: MINIMAX (5), BAYES_RISK (5), MARKOV (1), CONCEPTUAL (10). The agreement script excludes these to avoid trivial 1.0/1.0 agreement noise. Across 5 models that's 5×21=105 + 5×6 v1 perturbations of those types = at most ~135 excluded — matches the reported 135 exclusions. Pattern is *not* random — it disproportionately excludes CONCEPTUAL (10/10 base tasks) and MINIMAX (5/5). The retained 1094 runs are still 89% of the population, but the headline "25% pass-flip" applies to the *non-CONCEPTUAL* subset.
Evidence: `scripts/keyword_vs_judge_agreement.py:273` exclusion line; manual count of empty-assumption tasks via tasks_all.json scan.
Recommendation: Disclose in the poster: "25.0% pass-flip on the 89% of tasks with non-empty assumption requirements; CONCEPTUAL/MINIMAX/BAYES_RISK excluded by design."

**[P-7] Inter-rater reliability — single judge**
Severity: MAJOR
Finding: Llama 3.3 70B is the sole external rater. No second judge model, no human spot-check beyond the top-5 disagreements paragraph in Day-1 log §"Strictness verification." A research claim that "keyword rubrics overstate Bayesian reasoning quality by 25%" rests entirely on one judge's pattern-matching. Per the Day-1 cross-provider check, scores are stable across Groq vs Together AI (same model) — but not across model families.
Evidence: `evaluation/llm_judge_rubric.py:38` JUDGE_MODEL constant; Day-1 log §"Strictness verification."
Recommendation: At minimum, run a 200-record stratified second-judge sample with GPT-4.1 or Mixtral-8x22B (~$1 cost) and report inter-judge κ on `assumption_compliance` — that single number defends the headline claim. Paper-scope: full ensemble.

**[P-8] v1 perturbations scored twice (different runs)**
Severity: MINOR
Finding: 75 v1 perturbations live in `data/synthetic/perturbations.json` and were originally run as part of the 1230-run base benchmark (`results_v1/runs.jsonl`). They were re-run by `score_perturbations.py` because it concatenates v1+v2 → `results_v2/perturbation_runs.jsonl`. Robustness analysis correctly excludes v1 perturbation rows when building base-score lookup, so there is no double-counting. But the v1 perturbation prompts now have *two* independent (model, score) pairs (one in each file) — the means may differ due to API stochasticity. Calibration + keyword-vs-judge use the v1-perturbation copy from `results_v1`; robustness uses the v2 copy. Cross-analysis comparisons could quietly diverge.
Evidence: `scripts/score_perturbations.py:44-55` combine_perturbations(); `experiments/results_v1/runs.jsonl` 1230 = 171 base + 75 v1-pert per-model.
Recommendation: Document in poster methodology that v1 perturbations were re-scored to align with the v2 batch run.

**[P-9] Confidence extraction is post-score, but bucket fall-through is large**
Severity: INFO
Finding: `extract_confidence` reads `raw_response` only; no leakage from scoring. But for 47-63% of every model's runs the response contains neither a hedge nor a definitive cue and falls into `unstated` (claimed=0.5). DeepSeek's `unstated` bucket has 0.713 actual accuracy — the largest under-confidence gap of any model. ECE flagging deepseek as worst is partly an artifact of a wide `unstated` bucket: 118 records, accuracy 0.713 vs claim 0.5 → contributes 0.103 of its 0.179 ECE.
Evidence: `experiments/results_v2/calibration.json` deepseek bucket.
Recommendation: Disclose `unstated` is the biggest contributor to deepseek's ECE — it's not "overconfident on stated claims," it's "doesn't make stated claims and is correct more often than the 0.5 fall-through assumes."

---

# 4. FURTHER DEVELOPMENT — opportunities ranked by impact

## POSTER-SCOPE (<4 hours, ship before May 8)

**[F-1] Insert all 8 figures into the poster**
Severity: CRITICAL (blocks the poster)
Finding: 8 figures exist as 300 DPI transparent PNGs; poster has 7 `\figstub` boxes and no `\includegraphics` calls.
Recommendation: 30-min mechanical replacement of stubs. This is the single highest-value item.

**[F-2] Compute and insert the per-model judge-mean ranking**
Severity: MAJOR
Finding: Reasoning-quality column of three-rankings panel is "Stub --- to fill" (poster line 229). All numbers exist in `llm_judge_scores_full.jsonl`.
Recommendation: 1-hour script (per-model mean of `reasoning_quality.score`); update `poster/main.tex:229` with the actual list.

**[F-3] Bootstrap CI on accuracy + robustness deltas (top-3 are not separable)**
Severity: MAJOR
Finding: ChatGPT Δ=-0.0007 vs DeepSeek Δ=+0.0006 vs Mistral Δ=+0.0135 — first two are statistical noise.
Recommendation: 2-hour script (`scipy.stats.bootstrap` on per-task delta distributions, 10k resamples, 95% CI). Add CI bars to robustness panel.

**[F-4] Per-task-type robustness annotation in poster RQ4 panel**
Severity: MAJOR
Finding: Heatmap exists; poster panel doesn't quote which Bayesian concepts are most fragile.
Recommendation: 1-hour read of `robustness_v2.json` per_task_type_heatmap → top-3 most-fragile concepts (likely those with highest Δ across all 5 models). Add to RQ4 panel.

**[F-5] Fix [H-3] keyword_vs_judge per_task_type bloat + rerun**
Severity: MINOR
Finding: 1-line fix; reruns in seconds.
Recommendation: Fix to make per_task_type breakdown defensible if a reviewer asks.

**[F-6] Rejudge `STATIONARY_01_numerical` parse_error [H-7]**
Severity: MINOR
Finding: 1 record, ~$0.001, 30 seconds.
Recommendation: Adapt `_oneoff_rejudge_vb04_mistral.py` for the new run_id with max_tokens=2048.

**[F-7] Disclose the empty `high` bucket [H-6, P-3] in Limitations**
Severity: MAJOR
Finding: Currently the poster says "Confidence extraction is keyword-based" — does NOT warn that no model ever lands in the high bin.
Recommendation: One bullet under Limitations: "No model produced enough definitive linguistic markers (e.g., 'the answer is exactly') to populate the high-confidence bucket; ECE measures medium/low/unstated calibration only."

**[F-8] 200-record stratified second-judge sample with GPT-4.1 [P-7]**
Severity: MAJOR
Finding: Single-judge claim is the biggest validity hole. 200 calls × ~$0.005 = ~$1.
Recommendation: Stratify by (model, task_type), reuse `evaluation/llm_judge_rubric.py` with `JUDGE_MODEL = "gpt-4.1"` (and OpenAI endpoint). Compute κ on assumption_compliance pass/fail. If κ ≥ 0.6, the headline claim holds. ~3 hours total.

**[F-9] Hand-authored perturbation provenance flag [H-5]**
Severity: MINOR
Finding: 3 records, ~5 min.
Recommendation: Add `"provenance": "hand_authored"` to those 3 records in perturbations_all.json (or write a HAND_AUTHORED.md note).

**[F-10] Document v1 perturbations were re-scored vs original [P-8]**
Severity: MINOR
Recommendation: One-sentence disclosure in the Methodology block.

## PAPER-SCOPE (significant new compute or data)

**[F-11] Multi-judge ensemble (Llama + GPT-4.1 + Mixtral or Qwen)** — proper inter-judge κ across all 1230 base runs + perturbations. ~$15-30. Strengthens RQ3 and RQ4 claims for paper.

**[F-12] Token-logprob calibration** — Anthropic + OpenAI APIs return `logprobs`; convert to a true probabilistic calibration measure (Brier score, ECE-10bin) and replace the keyword proxy. Gemini + DeepSeek + Mistral need a workaround (e.g., judge-rated certainty). Killer feature for the paper.

**[F-13] Sentence-transformer perturbation quality validation** — embed base prompt + each perturbation prompt with `all-MiniLM-L6-v2`; assert cosine similarity > 0.85 for rephrase, < 0.85 for semantic. Validates that the LLM rephrasings actually preserve semantics and the semantic ones differ. ~30-min script + 5min eval.

**[F-14] Human eval spot-check (30 tasks × 2 raters)** — gold standard for inter-rater reliability. Stratify across models, task types, and pass/fail outcomes. Compute κ vs Llama judge. Defends the headline claim irrefutably.

**[F-15] Error-taxonomy second human coding (20% sample)** — addresses the empty HALLUCINATION bucket [H-4] by checking whether the buckets are genuinely unused or Llama is collapsing them.

**[F-16] Prompt-sensitivity ablation: "show all steps" vs default** — does the system prompt's "Show your step-by-step reasoning" directive bias the assumption_compliance score? Run 100 base tasks × 2 prompt variants × 5 models. Tests whether the 25% pass-flip is robust to prompt wording.

**[F-17] Agreement analysis on perturbation set (mirror Day-1 §4)** — replicate the keyword-vs-judge analysis on the 2365 perturbation runs. Confirms the 25% pass-flip generalizes beyond base tasks.

**[F-18] Statistical significance testing on ranking differences** — bootstrap or paired permutation tests for every ranking pair (accuracy, calibration, robustness, reasoning). Required for any peer-reviewed venue.

## STRETCH

**[F-19] Token-level error attribution via attention/logprob analysis** — for the 274 pass-flip cases, identify which tokens triggered the keyword rubric. Costly (per-token analysis per model), but produces a clean "the rubric fired on this exact word" figure.

**[F-20] Adversarial perturbations** — generate prompts specifically designed to flip a model's pass/fail status while preserving correct mathematics. Tests robustness more aggressively than the rephrase/numerical/semantic taxonomy.

---

# Summary

## Findings by severity

| Severity | Count | IDs |
|---|---:|---|
| CRITICAL | 1 | F-1 |
| MAJOR | 9 | H-1, H-2, H-4, H-6, P-3, P-7, F-2, F-3, F-4, F-7, F-8 |
| MINOR | 9 | H-3, H-5, H-7, H-8, H-9, P-2, P-6, P-8, F-5, F-6, F-9, F-10 |
| INFO | 5 | H-10, P-1, P-4, P-5, P-9 |

(The MAJOR row has 11 entries because F-2 through F-8 includes both poster-scope fixes and validity disclosures; some IDs appear under both an H/P finding and an F recommendation.)

## Top 3 to fix before Day 3 poster work

1. **F-1 — Insert the 8 figures into the poster.** Without this the poster is unreadable. 30 minutes.
2. **F-2 — Replace the reasoning-quality stub.** The three-rankings panel is the conceptual centerpiece; one column is empty. 1 hour.
3. **F-7 — Disclose [H-6] empty `high` bucket + [H-4] empty HALLUCINATION bucket in Limitations.** Both are visible to any careful reviewer; preempt the question. 30 minutes total.

## Top 3 paper-scope opportunities

1. **F-11 — Multi-judge ensemble (Llama + GPT-4.1 + Mixtral).** Defends the load-bearing 25%-pass-flip claim with inter-judge κ across all dimensions and models.
2. **F-12 — Token-logprob calibration replacing the keyword proxy.** Fundamentally strengthens RQ5; makes ECE numbers comparable to mainstream calibration literature.
3. **F-14 — Human eval spot-check (30 tasks × 2 raters).** Gold-standard validity check for the LLM-as-judge methodology.

---

*End of report.*
