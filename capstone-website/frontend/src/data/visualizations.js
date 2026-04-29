// Manifest of all R-generated visualizations.
// PNG/GIF files served from /visualizations/png/
// Interactive Plotly HTMLs served from /visualizations/interactive/

export const VISUALIZATIONS = [
  // ── FEATURED 4 ──────────────────────────────────────────────
  {
    id: 'heatmap',
    featured: true,
    title: 'Performance Heatmap',
    subtitle: 'Every model × every task type at a glance',
    description: 'Which model aced or failed each statistical topic? Each cell shows how a model (column) scored on a task type (row), averaged across all runs. Bright cyan = near-perfect. Dark = struggling. Rows sorted hardest to easiest.',
    png: '/visualizations/png/01_model_heatmap.png',
    interactive: '/visualizations/interactive/01_model_heatmap.html',
    type: 'Heatmap',
    category: 'Heatmaps',
    insight: 'REGRESSION and BAYES_FACTOR are consistently dark across every model — all 5 LLMs struggle with these. MINIMAX and RC_BOUND are bright cyan — nearly all models solve them correctly.',
  },
  {
    id: 'distributions',
    featured: true,
    title: 'Score Distributions',
    subtitle: 'How consistent is each model?',
    description: 'A wide, flat curve means the model is unpredictable — sometimes great, sometimes terrible. A tall, narrow peak means it\'s consistent. Each ridge shows the full spread of per-task scores for one model, not just the average.',
    png: '/visualizations/png/03_distributions.png',
    interactive: '/visualizations/interactive/03_distributions.html',
    type: 'Density',
    category: 'Distributions',
    insight: 'Claude has a bimodal shape — it either nails a task or completely fails it. Mistral and ChatGPT show smoother distributions, meaning more predictable (if slightly lower average) performance.',
  },
  {
    id: 'pass_rate',
    featured: true,
    title: 'Tier Breakdown',
    subtitle: 'Pass rates: Basic → Expert difficulty',
    description: 'The benchmark has 4 difficulty tiers — from Tier 1 (basic conjugate Bayes) to Tier 4 (graduate-level theory). This shows what percent of tasks each model passes at each tier. Where does each model hit its ceiling?',
    png: '/visualizations/png/13_pass_rate.png',
    interactive: '/visualizations/interactive/13_pass_rate.html',
    type: 'Heatmap',
    category: 'Heatmaps',
    insight: 'All 5 models pass Tier 1 near-perfectly (the basics are easy). Tier 4 is where models diverge sharply — Claude passes 69% while DeepSeek passes only 38% of expert tasks.',
  },
  {
    id: 'failure_analysis',
    featured: true,
    title: 'Best & Worst Task Types',
    subtitle: 'Where every model succeeds and fails',
    description: 'Ranked by failure rate — how often each task type scores below the 0.5 pass threshold. Each bar is stacked by model so you can see whether a task is universally hard or just hard for specific models.',
    png: '/visualizations/png/05_failure_analysis.png',
    interactive: '/visualizations/interactive/05_failure_analysis.html',
    type: 'Bar Chart',
    category: 'Comparisons',
    insight: 'REGRESSION alone accounts for ~40% of all benchmark failures. This one task type — requiring multi-line output — overwhelms every model\'s token budget (1024-token cap). MINIMAX and RC_BOUND have zero failures.',
  },

  // ── GALLERY ──────────────────────────────────────────────────
  {
    id: 'radar',
    title: 'Radar: Tier vs Model',
    subtitle: 'Multi-dimensional capability profile',
    description: 'Spider chart showing how each model\'s performance changes across the 4 difficulty tiers. A model that holds its shape from center to edge is consistent across difficulty. Models that shrink sharply toward the edge struggle on harder tasks.',
    png: '/visualizations/png/02_tier_radar_bar.png',
    interactive: '/visualizations/interactive/02_tier_radar.html',
    type: 'Radar',
    category: 'Distributions',
    insight: 'All models are near-perfect on Tier 1. Claude maintains the largest area on Tiers 3–4, confirming its edge on expert-level statistical reasoning.',
  },
  {
    id: 'latency_accuracy',
    title: 'Speed vs Accuracy',
    subtitle: 'Is slower always better?',
    description: 'Each dot is a model. X-axis = how long it takes to respond (milliseconds). Y-axis = average benchmark score. The ideal model is fast AND accurate — top-left corner. Bubble size = number of completed tasks.',
    png: '/visualizations/png/07_latency_accuracy.png',
    interactive: '/visualizations/interactive/07_latency_accuracy.html',
    type: 'Scatter',
    category: 'Comparisons',
    insight: 'Gemini is the fastest model. Claude achieves the highest accuracy with moderate latency. DeepSeek has the worst speed-accuracy ratio — slow and less accurate than Claude.',
  },
  {
    id: 'difficulty_line',
    title: 'Difficulty Progression',
    subtitle: 'Where does each model hit its wall?',
    description: 'Tasks are sorted from easiest to hardest (left to right). Smoothed curves show how each model\'s score degrades as difficulty increases. Vertical bands mark tier boundaries. The moment a curve drops sharply reveals each model\'s practical capability ceiling.',
    png: '/visualizations/png/14_difficulty.png',
    interactive: '/visualizations/interactive/14_difficulty.html',
    type: 'Line Chart',
    category: 'Distributions',
    insight: 'Models maintain scores above 0.7 through roughly the first 60% of tasks, then drop sharply — not gradually — once hitting a complexity threshold. This non-linear cliff effect is consistent across all 5 models.',
  },
  {
    id: 'bar_race',
    title: 'Ranking Animation',
    subtitle: 'Watch the leaderboard evolve task by task',
    description: 'An animated race showing how cumulative scores change as each benchmark task is revealed in order of difficulty. The final frame is the definitive ranking. Watch to see if the order was ever different mid-benchmark.',
    png: '/visualizations/png/15_bar_race.png',
    interactive: '/visualizations/png/15_bar_race.gif',
    type: 'Animation',
    category: 'Animation',
    isGif: true,
    insight: 'Rankings lock in after ~80 tasks and barely shift — the benchmark has enough statistical power to definitively rank models. Claude leads throughout; the middle pack (Mistral, Gemini, DeepSeek, ChatGPT) shuffles slightly but stays close.',
  },
  {
    id: 'error-distribution',
    title: 'Error Taxonomy: Overview',
    subtitle: '143 failures classified into 8 categories',
    description: 'Every failed run (score < 0.5) was classified into one of 8 error types using a hybrid rule-based + LLM-as-Judge pipeline. This chart shows how often each error type occurs across all 5 models and all 171 tasks.',
    png: '/visualizations/png/16a_error_distribution.png',
    interactive: null,
    type: 'Bar',
    category: 'Error Analysis',
    insight: 'The #1 failure reason (E3 Assumption Violation, 119 cases) is a reasoning gap — models skip stating priors, iid assumptions, or distributional assumptions. #2 (E7 Truncation, 93 cases) is a system limit — 1024 tokens cut off multi-target answers.',
  },
]

export const FEATURED_IDS = ['heatmap', 'distributions', 'pass_rate', 'failure_analysis']

export const VIZ_FILTER_MAP = {
  'All':           () => true,
  'Heatmaps':      v => v.category === 'Heatmaps',
  'Distributions': v => v.category === 'Distributions',
  'Comparisons':   v => v.category === 'Comparisons',
  'Animation':     v => v.category === 'Animation',
  'Error Analysis':v => v.category === 'Error Analysis',
}

export const VIZ_FILTERS = ['All', 'Heatmaps', 'Distributions', 'Comparisons', 'Animation', 'Error Analysis']
