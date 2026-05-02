// Manifest of all v2 visualizations.
// PNG files served from /visualizations/png/v2/
// Source files referenced relative to repo root (experiments/results_v2/*).

export const VIZ_CATEGORIES = [
  { id: 'rankings',      label: 'The Three Rankings', subtitle: 'Hero — accuracy, robustness, calibration', color: '#00FFE0' },
  { id: 'judge',         label: 'Judge Validation',   subtitle: 'RQ1 PRIMARY · 22.2% combined pass-flip · α negative on R, M', color: '#00B4D8' },
  { id: 'robustness',    label: 'Robustness',         subtitle: 'RQ4 · Perturbation analysis',              color: '#4A90D9' },
  { id: 'errors',        label: 'Error Taxonomy',     subtitle: 'RQ3 · 46.9% assumption violations',        color: '#A78BFA' },
  { id: 'calibration',   label: 'Calibration',        subtitle: 'RQ5 · Method-dependent · Phase 1C full coverage', color: '#7FFFD4' },
  { id: 'tasks',         label: 'Task Breakdown',     subtitle: 'RQ2 · REGRESSION cluster ~0.30',           color: '#FFB347' },
]

export const VISUALIZATIONS = [
  // ── 1. THREE RANKINGS (hero) ──────────────────────────────────
  {
    id: 'three_rankings', category: 'rankings', featured: true,
    title: 'The Three Rankings',
    subtitle: 'Accuracy ≠ Robustness ≠ Calibration',
    caption: 'Side-by-side rankings of all 5 models on three orthogonal lenses — single-metric leaderboards mislead. Gemini #1 accuracy, Mistral #1 robustness, ChatGPT #1 calibration.',
    source: 'experiments/results_v2/bootstrap_ci.json + robustness_v2.json + calibration.json',
    png: '/visualizations/png/v2/three_rankings.png',
  },
  {
    id: 'a6_aggregate_ranking', category: 'rankings',
    title: 'Aggregate Score Ranking',
    subtitle: 'Composite under literature-derived NMACR weights',
    caption: 'Composite ranking with bootstrap-derived bars + per-model formatting_failure_rate column. Gemini separable from Claude on accuracy under literature weights.',
    source: 'experiments/results_v2/bootstrap_ci.json',
    png: '/visualizations/png/v2/a6_aggregate_ranking.png',
  },
  {
    id: 'bootstrap_ci', category: 'rankings',
    title: 'Bootstrap CI on Accuracy',
    subtitle: 'Gemini 0.776 [0.753, 0.799] · Claude 0.712 [0.689, 0.736]',
    caption: '10,000 bootstrap resamples per model, seed=42, percentile method. Under literature weights, Gemini #1 separable from #2 Claude.',
    source: 'experiments/results_v2/bootstrap_ci.json',
    png: '/visualizations/png/v2/bootstrap_ci.png',
  },

  // ── 2. JUDGE VALIDATION (RQ1 PRIMARY) ─────────────────────────
  {
    id: 'agreement_metrics', category: 'judge', featured: true,
    title: 'Agreement Metrics — Keyword vs External Judge',
    subtitle: 'Krippendorff α = 0.55 (assumption) · −0.13 (RQ) · −0.04 (M)',
    caption: 'Three of four shared dimensions show keyword/judge divergence. Reasoning_quality and method_structure α are NEGATIVE — raters actively disagree.',
    source: 'experiments/results_v2/krippendorff_agreement.json + keyword_vs_judge_agreement.json',
    png: '/visualizations/png/v2/agreement_metrics_comparison.png',
  },
  {
    id: 'combined_pass_flip', category: 'judge', featured: true,
    title: 'Combined Pass-Flip — Phase 1.5',
    subtitle: '708 / 3,195 = 22.2% across base + perturbation',
    caption: 'Base 25.0% (274/1,095), perturbation 20.7% (434/2,100), combined 22.2%. Disagreement attenuates 4.4pp under perturbation — a stable rubric property, not an artefact of base wording.',
    source: 'experiments/results_v2/combined_pass_flip_analysis.json',
    png: '/visualizations/png/v2/combined_pass_flip_comparison.png',
  },
  {
    id: 'judge_scatter', category: 'judge',
    title: 'Judge vs Keyword — Per-Run Scatter',
    subtitle: '274 / 1,095 base runs flip pass/fail',
    caption: 'Each point is a single run scored by both raters. Off-diagonal mass = the 25% base pass-flip; combined denominator pushes to 22.2% across 3,195 runs.',
    source: 'experiments/results_v2/keyword_vs_judge_agreement.json',
    png: '/visualizations/png/v2/judge_validation_scatter.png',
  },
  {
    id: 'judge_by_model', category: 'judge',
    title: 'Judge vs Keyword — Per Model',
    subtitle: 'Pass-flip rate decomposed by model family',
    caption: 'Combined per-model pass-flip: claude 27.7% (177/639), gemini 23.5%, mistral 21.4%, chatgpt 19.1%, deepseek 19.1%. 9-point spread under the population mean.',
    source: 'experiments/results_v2/keyword_vs_judge_agreement.json',
    png: '/visualizations/png/v2/judge_validation_by_model.png',
  },

  // ── 3. ROBUSTNESS (RQ4) ───────────────────────────────────────
  {
    id: 'robustness_heatmap', category: 'robustness', featured: true,
    title: 'Robustness Heatmap',
    subtitle: 'Δ (perturbed − base) per model × task type',
    caption: 'Per-model × per-task-type degradation grid. Three uniformly-robust families: HIERARCHICAL, RJMCMC, VB. Under literature weights, Mistral ranks #1 robustness.',
    source: 'experiments/results_v2/robustness_v2.json',
    png: '/visualizations/png/v2/robustness_heatmap.png',
  },
  {
    id: 'a4b_per_dim_robustness', category: 'robustness',
    title: 'Per-Dimension Robustness Δ (Phase 1B Layer 2)',
    subtitle: '5 models × 5 NMACR dims = 25 deltas',
    caption: 'Layer 2 of RQ4. Claude / DeepSeek / Gemini lose most on the A dimension under perturbation — directly confirms the RQ3 assumption-violation finding. Cells annotated where |Δ| > 0.03.',
    source: 'experiments/results_v2/robustness_v2.json (per_dim_delta)',
    png: '/visualizations/png/v2/a4b_per_dim_robustness.png',
  },
  {
    id: 'robustness_perttype', category: 'robustness',
    title: 'Robustness by Perturbation Type',
    subtitle: 'rephrase / numerical / semantic',
    caption: 'BrittleBench 2026 taxonomy. Pass-flip per type: rephrase 21.6%, numerical 22.7%, semantic 18.1%.',
    source: 'experiments/results_v2/robustness_v2.json',
    png: '/visualizations/png/v2/a4_robustness_by_perttype.png',
  },

  // ── 4. ERROR TAXONOMY (RQ3) ──────────────────────────────────
  {
    id: 'taxonomy_sunburst', category: 'errors', featured: true,
    title: 'Error Taxonomy — Hierarchical',
    subtitle: 'L1 buckets × L2 codes · 143 base failures',
    caption: 'ASSUMPTION_VIOLATION 67 · MATHEMATICAL_ERROR 48 · FORMATTING 18 · CONCEPTUAL 10 · HALLUCINATION 0.',
    source: 'experiments/results_v2/error_taxonomy_v2.json',
    png: '/visualizations/png/v2/error_taxonomy_hierarchical.png',
  },
  {
    id: 'failure_by_tasktype', category: 'errors',
    title: 'Failure Rate by Task Type',
    subtitle: 'Where each task type ranks for failure share',
    caption: 'REGRESSION dominates. Markov chain types follow.',
    source: 'experiments/results_v2/error_taxonomy_v2.json',
    png: '/visualizations/png/v2/a1_failure_by_tasktype.png',
  },
  {
    id: 'failure_heatmap', category: 'errors',
    title: 'Failure Heatmap (Model × Task Type)',
    subtitle: 'Per-model failure-mode heterogeneity',
    caption: 'ChatGPT assumption-dominated (25/38). Claude math-dominated (10/19). Mistral math-dominated. DeepSeek mixed. Gemini balanced. Headline 46.9% hides this split.',
    source: 'experiments/results_v2/error_taxonomy_v2.json',
    png: '/visualizations/png/v2/a3_failure_heatmap.png',
  },

  // ── 5. CALIBRATION (RQ5) ─────────────────────────────────────
  {
    id: 'calibration_reliability', category: 'calibration', featured: true,
    title: 'Calibration Reliability — Verbalized',
    subtitle: '3-bucket ECE (0.3 / 0.5 / 0.6) · empty 0.9 bucket',
    caption: 'Hedge-heavy default-to-medium behaviour. No high-confidence records across any model. Gemini specifically 0 verbalized signals.',
    source: 'experiments/results_v2/calibration.json',
    png: '/visualizations/png/v2/calibration_reliability.png',
  },
  {
    id: 'a5b_per_dim_calibration', category: 'calibration',
    title: 'Per-Dimension Calibration ECE (Phase 1B Layer 5)',
    subtitle: '5 models × 5 NMACR dims',
    caption: 'Multi-dim extension of FermiEval (2025). Bucketed scores into {<0.4, <0.7, ≥0.7}; ECE = Σ_b w_b · |center_b − mean_b|. Gemini has no C row (all 246 base unstated).',
    source: 'experiments/results_v2/per_dim_calibration.json',
    png: '/visualizations/png/v2/a5b_per_dim_calibration.png',
  },
  {
    id: 'calibration_a5', category: 'calibration',
    title: 'Calibration — Per-Model Reliability',
    subtitle: 'Per-model ECE breakdown',
    caption: 'All five models cluster around medium-confidence — none escape into well-calibrated high-bucket.',
    source: 'experiments/results_v2/calibration.json',
    png: '/visualizations/png/v2/a5_calibration_reliability.png',
  },
  {
    id: 'self_consistency', category: 'calibration',
    title: 'Self-Consistency Calibration (Phase 1C full coverage, n=161 tasks)',
    subtitle: 'Verbalized vs consistency · Gemini outlier in both directions',
    caption: 'Phase 1C expanded from 30 stratified-hard tasks to all 161 numeric-target tasks. All 5 models severely overconfident under consistency: ECE 0.62–0.73. Gemini (0 verbalized signals) has the BEST consistency ECE (0.618).',
    source: 'experiments/results_v2/self_consistency_calibration.json',
    png: '/visualizations/png/v2/self_consistency_calibration.png',
  },

  // ── 6. TASK BREAKDOWN (RQ2) ──────────────────────────────────
  {
    id: 'accuracy_by_category', category: 'tasks', featured: true,
    title: 'Accuracy by Bayesian Category',
    subtitle: 'REGRESSION cluster ~0.30 across all 5 models',
    caption: 'Hardest categories: REGRESSION, MCMC, ADVANCED. Easiest: closed-form conjugate models.',
    source: 'experiments/results_v2/bootstrap_ci.json + tasks_all.json',
    png: '/visualizations/png/v2/a2_accuracy_by_category.png',
  },
]

export const FEATURED_IDS = VISUALIZATIONS.filter(v => v.featured).map(v => v.id)
