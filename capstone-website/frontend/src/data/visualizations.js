// Manifest of all v2 visualizations.
// PNG files served from /visualizations/png/v2/
// Source files referenced relative to repo root (experiments/results_v2/*).
// Items with a `Component` field render as live React panels (no PNG).
import { AgreementMetricsForestPanel, JudgeKeywordConfusionMatrix, DisagreementByPertTypePanel } from '../components/JudgeValidationPanels'

export const VIZ_CATEGORIES = [
  { id: 'rankings',      label: 'Performance Leaderboards', subtitle: 'Hero — accuracy, robustness, calibration', color: '#00FFE0' },
  { id: 'judge',         label: 'Judge Validation',         subtitle: 'RQ1 PRIMARY · 20.74% combined keyword-judge disagreement · α negative on R, chance-level on M', color: '#00B4D8' },
  { id: 'methodology',   label: 'Methodology Detail',       subtitle: 'External-judge vs keyword agreement — per-model & metric-comparison views', color: '#94a3b8' },
  { id: 'robustness',    label: 'Robustness',               subtitle: 'RQ4 · Perturbation analysis',              color: '#4A90D9' },
  { id: 'errors',        label: 'Error Taxonomy',           subtitle: 'RQ3 · 46.9% assumption violations',        color: '#A78BFA' },
  { id: 'calibration',   label: 'Calibration',              subtitle: 'RQ5 · Method-dependent · Phase 1C full coverage', color: '#7FFFD4' },
  { id: 'tasks',         label: 'Task Breakdown',           subtitle: 'RQ2 · REGRESSION cluster ~0.30',           color: '#FFB347' },
  { id: 'rigor',         label: 'Statistical Rigor',        subtitle: 'Bootstrap intervals + numerical tolerance sweep', color: '#fbbf24' },
]

export const VISUALIZATIONS = [
  // ── 1. PERFORMANCE LEADERBOARDS (hero) ────────────────────────
  {
    id: 'dimension_leaderboard', category: 'rankings', featured: true,
    title: 'Performance Leaderboard · 3 Dimensions',
    subtitle: 'Each panel sorted by its own metric — no model wins all three',
    caption: 'Three horizontal-bar panels share model identity colors. Best in panel highlighted: Gemini leads Accuracy (0.731), ChatGPT leads Robustness (Δ=+0.0003), Claude leads Calibration (ECE=0.033). Replaces the prior boxes-and-lines three_rankings + bump-chart pair.',
    source: 'experiments/results_v2/bootstrap_ci.json + robustness_v2.json + calibration.json',
    png: '/visualizations/png/v2/dimension_leaderboard.png',
    width: 2082, height: 719,
  },
  {
    id: 'a6_aggregate_ranking', category: 'rankings',
    title: 'Aggregate Score Ranking',
    subtitle: 'Composite under literature-derived NMACR weights',
    caption: 'Composite ranking with bootstrap-derived bars + per-model formatting_failure_rate column. Gemini separable from Claude on accuracy under literature weights.',
    source: 'experiments/results_v2/bootstrap_ci.json',
    png: '/visualizations/png/v2/a6_aggregate_ranking.png',
  },

  // ── 2. JUDGE VALIDATION (RQ1 PRIMARY) ─────────────────────────
  {
    id: 'agreement_metrics', category: 'judge', featured: true,
    title: 'Agreement Metrics — Keyword vs External Judge',
    subtitle: 'Krippendorff α = 0.57 (assumption) · −0.125 (RQ) · −0.009 (M)',
    caption: 'Forest plot of Krippendorff α with 95% bootstrap CIs across the 3 shared dimensions (n=750, base scope). Reasoning_quality CI [−0.197, −0.059] excludes zero — structural disagreement. Method_structure CI [−0.072, +0.062] contains zero — essentially chance-level. Only assumption_compliance reaches positive agreement (α=+0.573).',
    source: 'experiments/results_v2/krippendorff_agreement.json',
    Component: AgreementMetricsForestPanel,
  },
  {
    id: 'judge_scatter', category: 'judge',
    title: 'Judge vs Keyword — Disagreement Matrix',
    subtitle: '199 / 750 base runs disagree (157 directional pass-flips)',
    caption: '2×2 confusion matrix on assumption_compliance (n=750 base eligible). Diagonal = agreement (376 both-pass + 175 both-fail = 73.5%). Off-diagonal = disagreement (157 keyword-only-pass + 42 judge-only-pass = 26.5%). Combined denominator (base + perturbation, n=2,850) holds at 20.74% directional pass-flip.',
    source: 'experiments/results_v2/keyword_vs_judge_agreement.json + combined_pass_flip_analysis.json',
    Component: JudgeKeywordConfusionMatrix,
  },
  {
    id: 'disagreement_by_perttype', category: 'judge', noExpand: true,
    title: 'Disagreement by perturbation type',
    subtitle: 'REPHRASE / NUMERICAL / SEMANTIC pass-flip rates',
    caption: 'Per-perturbation-flavor breakdown of keyword/judge disagreement. Stable across types — disagreement is structural.',
    source: 'experiments/results_v2/combined_pass_flip_analysis.json',
    Component: DisagreementByPertTypePanel,
  },

  // ── 3. METHODOLOGY DETAIL (PNG companions) ────────────────────
  {
    id: 'judge_validation_by_model', category: 'methodology',
    title: 'Judge agreement by model',
    subtitle: 'External Llama-judge vs keyword rubric',
    caption: 'Per-model breakdown of agreement on assumption_compliance, reasoning_quality, and method_structure dimensions.',
    source: 'experiments/results_v2/keyword_vs_judge_agreement.json',
    png: '/visualizations/png/v2/judge_validation_by_model.png',
    width: 4172, height: 2068,
  },
  {
    id: 'judge_validation_scatter', category: 'methodology',
    title: 'Judge vs rubric scatter',
    subtitle: 'Per-task agreement scatter',
    caption: 'Scatter of per-task keyword score vs external-judge score on the shared dimensions.',
    source: 'experiments/results_v2/keyword_vs_judge_agreement.json',
    png: '/visualizations/png/v2/judge_validation_scatter.png',
    width: 6566, height: 1849,
  },
  {
    id: 'agreement_metrics_comparison', category: 'methodology',
    title: 'Cross-metric agreement',
    subtitle: 'Krippendorff α / Cohen κ / Spearman ρ',
    caption: 'Three inter-rater-reliability statistics side-by-side, dimension by dimension. Krippendorff α is the cohort headline; κ and ρ provided for triangulation.',
    source: 'experiments/results_v2/krippendorff_agreement.json',
    png: '/visualizations/png/v2/agreement_metrics_comparison.png',
    width: 2371, height: 1550,
  },

  // ── 4. ROBUSTNESS (RQ4) ───────────────────────────────────────
  {
    id: 'robustness_heatmap', category: 'robustness', featured: true,
    title: 'Robustness Heatmap',
    subtitle: 'Δ (perturbed − base) per model × task type · vertical · all cells annotated',
    caption: 'Per-model × per-task-type degradation grid (37 task types × 5 models). Three uniformly-robust families: HIERARCHICAL, RJMCMC, VB. Under literature weights, ChatGPT and Mistral are statistically tied at top of robustness — both noise-equivalent.',
    source: 'experiments/results_v2/robustness_v2.json',
    png: '/visualizations/png/v2/robustness_heatmap.png',
    width: 1072, height: 1716,
  },
  {
    id: 'robustness_perttype', category: 'robustness',
    title: 'Robustness by Perturbation Type',
    subtitle: 'rephrase / numerical / semantic',
    caption: 'BrittleBench 2026 taxonomy. Keyword-judge disagreement per type: rephrase 21.6%, numerical 22.7%, semantic 18.1%.',
    source: 'experiments/results_v2/robustness_v2.json',
    png: '/visualizations/png/v2/a4_robustness_by_perttype.png',
  },
  {
    id: 'a4b_per_dim_robustness', category: 'robustness',
    title: 'Robustness by perturbation type',
    subtitle: 'Rephrase / numerical / semantic breakdown',
    caption: 'Per-dimension Δ by perturbation type — surfaces which dimensions degrade most under each transformation.',
    source: 'experiments/results_v2/per_dim_calibration.json',
    png: '/visualizations/png/v2/a4b_per_dim_robustness.png',
    width: 2070, height: 1323,
  },
  {
    id: 'tolerance_sensitivity', category: 'robustness',
    title: 'Numerical tolerance sensitivity',
    subtitle: 'Score sensitivity to full_credit_tol sweep',
    caption: 'Sweep of `full_credit_tol` to show how the cohort accuracy curve responds to scoring-tolerance choices. Validates that headline rankings do not depend on a knife-edge tolerance.',
    source: 'experiments/results_v2/tolerance_sensitivity.json',
    png: '/visualizations/png/v2/tolerance_sensitivity.png',
    width: 2519, height: 1349,
  },

  // ── 5. ERROR TAXONOMY (RQ3) ──────────────────────────────────
  {
    id: 'taxonomy_sunburst', category: 'errors', featured: true,
    title: 'Error Taxonomy — Hierarchical',
    subtitle: 'L1 buckets × L2 codes · 143 base failures',
    caption: 'ASSUMPTION_VIOLATION 67 · MATHEMATICAL_ERROR 48 · FORMATTING 18 · CONCEPTUAL 10 (4 populated L1 buckets; HALLUCINATION empty — see Limitations).',
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

  // ── 6. CALIBRATION (RQ5) ─────────────────────────────────────
  {
    id: 'calibration_ece_ranking', category: 'calibration', featured: true,
    title: 'Calibration · ECE leaderboard',
    subtitle: 'Verbalized confidence vs empirical accuracy',
    caption: 'Smaller ECE = better calibrated. Green / yellow / red zones flag well-calibrated (<0.05), mildly miscalibrated (0.05–0.10), severely miscalibrated (>0.10). Claude #1 (0.033), ChatGPT #2 (0.034), DeepSeek tail (0.198).',
    source: 'experiments/results_v2/calibration.json',
    png: '/visualizations/png/v2/calibration_ece_ranking.png',
    width: 1635, height: 585,
  },
  {
    id: 'calibration_reliability', category: 'calibration',
    title: 'Calibration gap by confidence bucket',
    subtitle: 'Per-bucket signed gap, model × confidence-level',
    caption: "Distance from zero shows miscalibration magnitude. DeepSeek's 0.6 bucket is severely overconfident (−0.21); Claude near-zero across buckets.",
    source: 'experiments/results_v2/calibration.json',
    png: '/visualizations/png/v2/calibration_reliability_smallmultiples.png',
  },
  {
    id: 'self_consistency', category: 'calibration',
    title: 'Self-Consistency Calibration (Phase 1C full coverage, n=161 tasks)',
    subtitle: 'Verbalized vs consistency · cohort-wide method-dependence',
    caption: 'Phase 1C expanded from 30 stratified-hard tasks to all 161 numeric-target tasks. All 5 models severely overconfident under consistency: ECE 0.62–0.73 (vs verbalized 0.03–0.20 post-Phase-1.8). The two methods yield qualitatively different conclusions for every model.',
    source: 'experiments/results_v2/self_consistency_calibration.json',
    png: '/visualizations/png/v2/self_consistency_calibration.png',
  },
  {
    id: 'a5b_per_dim_calibration', category: 'calibration',
    title: 'Per-dimension calibration',
    subtitle: 'ECE per assumption / reasoning / method dim',
    caption: 'Dimension-level ECE breakdown — surfaces which judge dimensions drive cohort calibration error.',
    source: 'experiments/results_v2/per_dim_calibration.json',
    png: '/visualizations/png/v2/a5b_per_dim_calibration.png',
    width: 2069, height: 1322,
  },

  // ── 7. TASK BREAKDOWN (RQ2) ──────────────────────────────────
  {
    id: 'accuracy_by_category', category: 'tasks', featured: true,
    title: 'Accuracy by Bayesian Category',
    subtitle: 'REGRESSION cluster ~0.30 across all 5 models',
    caption: 'Heatmap: 5 model rows × 6 category cols, color centered on cohort mean. Hardest categories: REGRESSION, MCMC, ADVANCED. Easiest: closed-form conjugate models.',
    source: 'experiments/results_v2/bootstrap_ci.json + tasks_all.json',
    png: '/visualizations/png/v2/a2_accuracy_by_category.png',
    width: 1629, height: 628,
  },

  // ── 8. STATISTICAL RIGOR ─────────────────────────────────────
  {
    id: 'bootstrap_ci', category: 'rigor',
    title: 'Bootstrap confidence intervals',
    subtitle: 'B=10,000 model accuracy CIs',
    caption: 'Bootstrap-derived 95% CIs on per-model literature-weighted accuracy. Anchors all separability claims in the rankings panel and aggregate composite.',
    source: 'experiments/results_v2/bootstrap_ci.json',
    png: '/visualizations/png/v2/bootstrap_ci.png',
    width: 3558, height: 1321,
  },
]

export const FEATURED_IDS = VISUALIZATIONS.filter(v => v.featured).map(v => v.id)
