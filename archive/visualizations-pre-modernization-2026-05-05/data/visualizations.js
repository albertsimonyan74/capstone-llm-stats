// Manifest of all v2 visualizations.
// PNG files served from /visualizations/png/v2/
// Source files referenced relative to repo root (experiments/results_v2/*).
// Items with a `Component` field render as live React panels (no PNG).
import { AgreementMetricsForestPanel, JudgeKeywordConfusionMatrix } from '../components/JudgeValidationPanels'

export const VIZ_CATEGORIES = [
  { id: 'rankings',      label: 'The Three Rankings', subtitle: 'Hero — accuracy, robustness, calibration', color: '#00FFE0' },
  { id: 'judge',         label: 'Judge Validation',   subtitle: 'RQ1 PRIMARY · 20.74% combined keyword-judge disagreement · α negative on R, chance-level on M', color: '#00B4D8' },
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
    caption: 'Side-by-side rankings of all 5 models on three orthogonal lenses — single-metric leaderboards mislead. Gemini #1 accuracy; ChatGPT and Mistral statistically tied at top of robustness; Claude and ChatGPT essentially tied on calibration.',
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

  // ── 3. ROBUSTNESS (RQ4) ───────────────────────────────────────
  {
    id: 'robustness_heatmap', category: 'robustness', featured: true,
    title: 'Robustness Heatmap',
    subtitle: 'Δ (perturbed − base) per model × task type',
    caption: 'Per-model × per-task-type degradation grid. Three uniformly-robust families: HIERARCHICAL, RJMCMC, VB. Under literature weights, ChatGPT and Mistral are statistically tied at top of robustness — both noise-equivalent.',
    source: 'experiments/results_v2/robustness_v2.json',
    png: '/visualizations/png/v2/robustness_heatmap.png',
  },
  {
    id: 'robustness_perttype', category: 'robustness',
    title: 'Robustness by Perturbation Type',
    subtitle: 'rephrase / numerical / semantic',
    caption: 'BrittleBench 2026 taxonomy. Keyword-judge disagreement per type: rephrase 21.6%, numerical 22.7%, semantic 18.1%.',
    source: 'experiments/results_v2/robustness_v2.json',
    png: '/visualizations/png/v2/a4_robustness_by_perttype.png',
  },

  // ── 4. ERROR TAXONOMY (RQ3) ──────────────────────────────────
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

  // ── 5. CALIBRATION (RQ5) ─────────────────────────────────────
  {
    id: 'calibration_reliability', category: 'calibration', featured: true,
    title: 'Calibration Reliability — Verbalized',
    subtitle: '3 active buckets (0.3 / 0.5 / 0.6) · 0.9 bucket empty across all models',
    caption: 'Per-model accuracy at each verbalized confidence bucket. Diagonal = perfect calibration. Points below: overconfidence (claimed > actual). Points above: underconfidence (claimed < actual). Dot size ∝ bucket sample count. No high-confidence (0.9) records across any model — hedge-heavy default-to-medium behaviour.',
    source: 'experiments/results_v2/calibration.json',
    png: '/visualizations/png/v2/calibration_reliability.png',
  },
  {
    id: 'self_consistency', category: 'calibration',
    title: 'Self-Consistency Calibration (Phase 1C full coverage, n=161 tasks)',
    subtitle: 'Verbalized vs consistency · cohort-wide method-dependence',
    caption: 'Phase 1C expanded from 30 stratified-hard tasks to all 161 numeric-target tasks. All 5 models severely overconfident under consistency: ECE 0.62–0.73 (vs verbalized 0.03–0.20 post-Phase-1.8). The two methods yield qualitatively different conclusions for every model.',
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
