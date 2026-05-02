---
tags: [literature, citation-map, index]
date: 2026-05-01
---

# Citation Map

Reverse index: project artifact → sources that cite it.

---

## By RQ

- **RQ1 (Methodology):** Papers 01, 03, 10, 14
- **RQ2 (Task-category accuracy):** Papers 03, 13; Textbooks 01, 04, 05
- **RQ3 (Failure taxonomy):** Papers 02, 09, 13
- **RQ4 (Robustness):** Papers 07, 08, 15
- **RQ5 (Calibration):** Papers 02, 11, 12

## By script

- `scripts/bootstrap_ci.py`: Papers 06, 15
- `scripts/three_rankings_figure.py`: Paper 07
- `scripts/generate_perturbations_full.py`: Paper 08
- `scripts/score_perturbations.py`: Paper 08
- `scripts/robustness_analysis.py`: Papers 07, 08
- `scripts/error_taxonomy.py`: Papers 09, 13
- `scripts/keyword_vs_judge_agreement.py`: Paper 10
- `scripts/combined_pass_flip_analysis.py` (Phase 1.5): Paper 10 (Yamauchi)
- `scripts/krippendorff_agreement.py` (Group B1): Papers 10, 14
- `scripts/calibration_analysis.py`: Papers 02, 11, 12
- `scripts/self_consistency_proxy.py` (Group B3): Papers 11, 12 — ARCHIVED 2026-05-02 → `llm-stats-vault/90-archive/intermediate_analyses/scripts/`
- `evaluation/llm_judge_rubric.py`: Papers 10, 13, 14
- `llm_runner/run_all_tasks.py`: Papers 04, 05 (CoT and PoT prompting)
- `llm_runner/prompt_builder.py`: Papers 04, 05

## By task type family

- BETA_BINOM, BINOM_FLAT, HPD, GAMMA_POISSON → Textbook: Bolstad
- VB_*, DIRICHLET_*, BAYES_REG, LOG_ML → Textbook: Bishop
- JEFFREYS_*, FISHER_INFO_*, RC_BOUND_*, MLE_EFFICIENCY → Textbook: Ghosh et al.
- NORMAL_GAMMA_*, PPC_*, GIBBS_* (introductory) → Textbook: Hoff
- GIBBS, MH, HMC, RJMCMC, REGRESSION, HIERARCHICAL → Textbook: Carlin & Louis
- BAYES_LINEAR_*, LINEAR_APPROX_* → Textbook: Goldstein & Wooff
- CI_CREDIBLE_*, BAYES_FACTOR_* → Textbook: Lee

## By audit finding

- **P-2 (separability):** Paper 15
- **P-3 (calibration ECE skew):** Papers 11, 12
- **P-7 (single judge) strengthened:** Papers 10, 14
- **F-7 (empty high-confidence bucket):** Papers 11, 12
- **F-11 (multi-judge ensemble future work):** Paper 14
- **F-12 (logprob calibration) addressed via consistency proxy:** Papers 11, 12

## By poster panel

- **Abstract:** Papers 01, 07, 08, 10
- **Methodology:** Papers 03, 04, 05, 10, 13
- **Three Rankings:** Papers 06, 07, 15
- **Failure Taxonomy:** Papers 09, 13
- **Calibration (RQ5):** Papers 02, 11, 12
- **Limitations:** Papers 12, 14
- **Future Work:** Papers 12, 14
- **Foundations / textbook citations:** Textbooks 01–07 (one footer line)
- **Literature Comparison:** All 15 papers (Group B4)

## By document

- `audit/rq_restructuring.md` (Phase 1B; renamed from rq_reweighting.md):
  Papers 01, 02, 03, 09, 10, 11, 12, 13, 14
- `audit/methodology_continuity.md`: Papers 01, 03, 04, 05, 07, 08, 10, 11, 12, 14, 15
- `audit/literature_comparison.md`: All 15 papers
- `audit/recompute_log.md` (Phase 1B): literature-derived weight citations —
  Papers 02, 03, 04, 05, 07, 09, 10, 11, 12, 13; Textbook 02 (Bishop)
- `llm-stats-vault/00-home/research-narrative.md` (Phase 1B): all 22 sources

## Phase 1B — NMACR weighting (literature-derived)

Per-dimension citations grounding the locked weights
(A=0.30, R=0.25, M=0.20, C=0.15, N=0.10):

- **A dimension (0.30):** Papers 09 (Du, Ice Cream), 13 (Boye & Moell,
  Math-Reasoning-Failures), 10 (Yamauchi, LLM-as-Judge empirical study)
- **R dimension (0.25):** Papers 10 (Yamauchi), 13 (Boye & Moell),
  07 (Au et al., ReasonBench)
- **M dimension (0.20):** Papers 04 (Wei et al., CoT), 05 (Chen et al., PoT);
  Textbook 02 (Bishop, PRML)
- **C dimension (0.15):** Papers 02 (Nagarkar), 11 (FermiEval),
  12 (Multi-Answer Confidence)
- **N dimension (0.10):** Papers 03 (Liu, MathEval),
  13 (Boye & Moell, Math-Reasoning-Failures)

## Phase 1B — new scripts

- `scripts/recompute_nmacr.py`: All 15 papers (full literature defense for the
  weight scheme). Primary anchors: Papers 09, 13, 10 (A); 10, 13, 07 (R);
  04, 05 + Textbook 02 (M); 02, 11, 12 (C); 03, 13 (N).
- `scripts/recompute_downstream.py`: Papers 06, 07, 08, 11, 13, 15
  (per-dim robustness + per-dim calibration + correlation).

## By experimental output

- `experiments/results_v2/bootstrap_ci.json`: Papers 06, 15
- `experiments/results_v2/robustness_v2.json`: Paper 08
- `experiments/results_v2/error_taxonomy_v2.json`: Papers 09, 13
- `experiments/results_v2/calibration.json`: Papers 02, 11, 12
- `experiments/results_v2/keyword_vs_judge_agreement.json`: Paper 10
- `experiments/results_v2/llm_judge_scores_full.jsonl`: Papers 10, 14
- `experiments/results_v2/nmacr_scores_v2.jsonl` (Phase 1B): All 15 papers
- `experiments/results_v2/per_dim_calibration.json` (Phase 1B): Papers 11, 12

## By figure

- `report_materials/figures/bootstrap_ci.png`: Papers 06, 15
- `report_materials/figures/three_rankings.png`: Paper 07
- `report_materials/figures/robustness_heatmap.png`: Paper 08
- `report_materials/figures/error_taxonomy_hierarchical.png`: Papers 09, 13
- `report_materials/figures/judge_validation_scatter.png`: Paper 10
- `report_materials/figures/judge_validation_by_model.png`: Paper 10
- `report_materials/figures/a4b_per_dim_robustness.png` (Phase 1B): Papers 07, 08, 13
- `report_materials/figures/a5b_per_dim_calibration.png` (Phase 1B): Papers 11, 12
- `report_materials/figures/a2_accuracy_by_category.png` (regenerated): Papers 03, 13
- `report_materials/figures/a3_failure_heatmap.png` (regenerated): Papers 09, 13
- `report_materials/figures/a6_aggregate_ranking.png` (regenerated): Papers 06, 15

## By limitations / future work item

- Verbalized → consistency-based confidence upgrade: Paper 12
- Multi-judge ensembling: Paper 14
- Bootstrap-CI separability tests: Papers 06, 15
- Domain-dependent confidence behavior: Paper 11 (contrast)

## Phase 1C — Self-consistency full expansion

### By script
- `scripts/self_consistency_full.py`: Papers 11 (FermiEval), 12 (Multi-Answer Confidence)
- `scripts/plot_self_consistency_calibration.py`: Papers 11, 12
- (B3 entry `scripts/self_consistency_proxy.py`: ARCHIVED 2026-05-02 — see
  `llm-stats-vault/90-archive/intermediate_analyses/scripts/`. Phase 1C
  superseded data outputs live in `llm-stats-vault/90-archive/phase_1c_superseded/`.)

### By audit finding
- F-12 fully addressed: Phase 1C full-coverage replaces B3 stratified
- Length-correlation disclosure (new, gemini verification): Paper 13 (Boye & Moell)
- CONCEPTUAL exclusion disclosure (new): inherent to consistency methodology

### By document
- `audit/limitations_disclosures.md`: Papers 11, 12, 13 (gemini verification)
- `llm-stats-vault/00-home/research-narrative.md` RQ5 section:
  Papers 02, 11, 12

### By experimental output
- `experiments/results_v2/self_consistency_calibration.json` (canonical,
  full coverage): Papers 11, 12
- `experiments/results_v2/self_consistency_runs.jsonl` (2,415 records):
  Papers 11, 12

### By figure
- `report_materials/figures/self_consistency_calibration.png`
  (regenerated, two-panel verbalized vs consistency): Papers 11, 12
