import { useState, useEffect, useRef, useMemo, createContext, useContext } from 'react'
import { motion, AnimatePresence, useInView, useScroll, useTransform } from 'motion/react'
import { PieChart, Pie, Cell, Tooltip as RTooltip, Legend, ResponsiveContainer } from 'recharts'
import './App.css'
import tasksData from './data/tasks.json'
import statsData from './data/stats.json'
import resultsData from './data/results_summary.json'
import GlobeBackground from './components/GlobeBackground'
import Navbar          from './components/Navbar'
import SideNav         from './components/SideNav'
import NeuralNetwork   from './components/NeuralNetwork'
import HeroNetworkBg   from './components/HeroNetworkBg'
import KeyFindings, { useKeyFindings, KeyFindingCard } from './components/KeyFindings'
import { PerModelPassFlipPanel } from './components/MethodologyPanels'
import ThreeRankingsComparison from './components/ThreeRankingsComparison'
import VizGallery      from './pages/VizGallery'
import UserStudy       from './pages/UserStudy'
import Methodology     from './pages/Methodology'
import Limitations     from './pages/Limitations'
import References      from './pages/References'
import { TOOLTIP_MAP } from './data/TooltipMap'
import { ParamTooltip } from './components/ParamTooltip'

// ─── Palette ──────────────────────────────────────────────────
const C = {
  aqua:      '#00FFE0',
  aquaLight: '#7FFFD4',
  blue:      '#00B4D8',
  blueDeep:  '#0047AB',
  cyan:      '#00FFE0',
  teal:      '#00897B',
  purple:    '#A78BFA',
  text:      '#E8F4F8',
  textMuted: '#8BAFC0',
}

const TIER_COLORS  = { 1:'#7FFFD4', 2:'#00FFE0', 3:'#00B4D8', 4:'#A78BFA' }
const TIER_LABELS  = { 1:'BASIC', 2:'INTERMEDIATE', 3:'ADVANCED', 4:'EXPERT' }

const TIER_INFO = {
  1: { label:'BASIC',        color:'#7FFFD4', tasks:9,  icon:'◆',
       desc:'Closed-form posterior · Single conjugate update',
       detail:'Direct application of Bayes theorem. No multi-step reasoning required. Tests foundational probability mechanics.' },
  2: { label:'INTERMEDIATE', color:'#00FFE0', tasks:58, icon:'◆◆',
       desc:'Multi-step inference · Distribution properties · MCMC basics',
       detail:'Requires tracking intermediate quantities and chaining multiple theorems. Includes Phase 2 Gibbs, MH, and VB tasks.' },
  3: { label:'ADVANCED',     color:'#00B4D8', tasks:84, icon:'◆◆◆',
       desc:'Decision theory · Model comparison · Computational Bayes',
       detail:'Integrates multiple statistical frameworks. Includes HMC, RJMCMC, ABC, and Hierarchical Bayes tasks.' },
  4: { label:'EXPERT',       color:'#A78BFA', tasks:20, icon:'◆◆◆◆',
       desc:'Competing estimators · Asymptotic theory · Advanced MCMC',
       detail:'Graduate-level statistical theory. Tests the frontier of LLM mathematical reasoning under pressure.' },
}

// ─── Models (5 models, correct API versions) ─────────────────
const MODELS = [
  { id:'claude',   initials:'CL', name:'Claude Sonnet 4.5', full:'Claude Sonnet 4.5',
    version:'claude-sonnet-4-5',    provider:'Anthropic',       lab:'Frontier AI Lab',
    color:'#00CED1', api:'api.anthropic.com/v1/messages', maxTokens: 1024, avgOutputTokens: 811,
    strengths:'Strong mathematical reasoning, excellent at step-by-step Bayesian derivations and conjugate updates', status:'READY' },
  { id:'gemini',   initials:'GM', name:'Gemini 2.5 Flash',  full:'Gemini 2.5 Flash',
    version:'gemini-2.5-flash',     provider:'Google DeepMind', lab:'Alphabet',
    color:'#FF6B6B', api:'generativelanguage.googleapis.com', maxTokens: 4096, avgOutputTokens: 1729,
    strengths:'Fast inference, good at probability calculations and statistical formula application. Note: Gemini used a 4096-token output cap (not 1024) — see runs for details', status:'READY' },
  { id:'chatgpt',  initials:'GP', name:'GPT-4.1',           full:'GPT-4.1',
    version:'gpt-4.1',              provider:'OpenAI',           lab:'Microsoft Partnership',
    color:'#7FFFD4', api:'api.openai.com/v1/chat/completions', maxTokens: 1024, avgOutputTokens: 700,
    strengths:'Broad statistical knowledge, reliable at standard Bayesian textbook problems', status:'READY' },
  { id:'deepseek', initials:'DS', name:'DeepSeek V4 Flash', full:'DeepSeek V4 Flash',
    version:'deepseek-chat',        provider:'DeepSeek AI',      lab:'China',
    color:'#4A90D9', api:'api.deepseek.com/v1/chat/completions', maxTokens: 1024, avgOutputTokens: 706,
    strengths:'Strong mathematical background, emerging capability in statistical inference tasks', status:'READY' },
  { id:'mistral',  initials:'MS', name:'Mistral Large',     full:'Mistral Large Latest',
    version:'mistral-large-latest', provider:'Mistral AI',       lab:'France',
    color:'#A78BFA', api:'api.mistral.ai/v1/chat/completions', maxTokens: 1024, avgOutputTokens: 744,
    strengths:'Strong reasoning with European research pedigree, competitive on formal mathematical tasks', status:'READY' },
]
const MODEL_META = Object.fromEntries(MODELS.map(m => [m.id, m]))

// ─── Pipeline ─────────────────────────────────────────────────
const PIPELINE = [
  { label:'Task Generation',          title:'171 Statistical Tasks',
    stat:'38 task types · 4 tiers',
    bullets:[
      '171 base tasks across Bayesian inference, hypothesis testing, regression, MCMC, decision theory',
      '38 distinct task types organized into 4 difficulty tiers — T1 basic (9) · T2 intermediate (58) · T3 advanced (84) · T4 expert (20)',
      <>Each task is a JSON record: <code className="pl-mono">task_id</code> · <code className="pl-mono">prompt</code> · <code className="pl-mono">task_type</code> · <code className="pl-mono">tier</code> · <code className="pl-mono">numeric_targets</code> · <code className="pl-mono">required_assumption_checks</code></>,
      'required_structure_checks + required_assumption_checks define regex patterns the keyword scorer matches',
      <>Ground truth seeded <code className="pl-mono">numpy.random.seed(42)</code> for reproducibility</>,
      'Designed to require explicit assumption articulation, not just numerical answers',
    ],
    visual: 'tier-mini',
  },
  { label:'Standardized Prompting',   title:'Zero-Shot CoT Protocol',
    stat:'Zero-shot Chain-of-Thought',
    bullets:[
      'Zero-shot Chain-of-Thought framing (Wei et al., 2022) applied uniformly across all 5 models',
      'Identical prompts dispatched to Anthropic · OpenAI · Google · DeepSeek · Mistral via httpx (no vendor SDKs)',
      <>~6,010 raw responses collected: 855 base (171 × 5) + 2,365 perturbation (473 × 5) + self-consistency reruns</>,
      <>Per-response metadata captured: <code className="pl-mono">raw_response</code> · <code className="pl-mono">input_tokens</code> · <code className="pl-mono">output_tokens</code> · <code className="pl-mono">latency_ms</code> · <code className="pl-mono">model</code> · <code className="pl-mono">task_id</code></>,
      'Self-consistency: 3× reruns at T=0.7 for 161 numeric tasks × 5 models, used for Phase 1C ECE calibration',
      'Program-of-Thoughts explored as exploratory; zero-shot CoT only is the canonical scored baseline',
    ],
  },
  { label:'Multi-Model Evaluation',   title:'5 Leading LLMs + 1 External Judge',
    stat:'855 base runs · Llama 3.3 70B judge',
    bullets:[
      'Five frontier models: Claude · GPT-4.1 · Gemini · DeepSeek · Mistral',
      'Dual scoring path runs in parallel for every response — keyword (regex, deterministic) and Llama judge (rubric)',
      'Llama 3.3 70B Instruct via Together AI is deliberately external to the 5 evaluated — no self-preference bias',
      <>Per-response output: <code className="pl-mono">keyword_scores</code> + <code className="pl-mono">judge_scores</code> stored per dimension (N · M · A · C · R)</>,
      'Cross-provider validation following Yamauchi et al. (2025); Krippendorff α reported with bootstrap CI per dimension',
    ],
  },
  { label:'Five-Dimensional Scoring', title:'N·M·A·C·R Rubric',
    stat:'A=0.30 · R=0.25 · M=0.20 · C=0.15 · N=0.10',
    visual: 'nmacr-weights',
    bullets:[
      'NMACR composite = weighted sum across 5 rubric dimensions (single canonical scoring path, Approach A locked May 2026)',
      'Weights literature-derived: A from Du 2025 / Yamauchi 2025 / Au 2025 · M from Chen 2022 · R from Wei 2022 · C from Nagarkar 2026 · N from Liu 2025',
      <>Single source of truth: <code className="pl-mono">response_parser.py NMACR_WEIGHTS</code> constant; <code className="pl-mono">assert sum(NMACR_WEIGHTS.values()) == 1.0</code> guards rebalancing</>,
      'PASS threshold: NMACR ≥ 0.50 (used downstream for pass/flip analysis under perturbation)',
      'Single source of truth for all downstream RQ analyses (literature-NMACR aggregate per run)',
    ],
  },
  { label:'Robustness Testing',       title:'RQ4: Perturbation Analysis',
    stat:'2,365 perturbation runs · 0 errors',
    bullets:[
      <>473 perturbations across 171 base tasks: rephrase 171 · numerical 131 · semantic 171 (canonical: <code className="pl-mono">perturbations_all.json</code>)</>,
      'Three perturbation types preserve math while varying surface form — rephrase (same problem, reworded) · numerical (same structure, different numbers) · semantic (same math, different domain)',
      '2,365 total perturbation runs (473 × 5 models) with 0 API failures',
      <>Robustness Δ = base − perturbation per model · bootstrap CI (B=10,000, seed=42) for separability</>,
      'ChatGPT, Mistral, Gemini CIs all cross zero — three-of-five models are noise-equivalent under perturbation',
      'Per-perturbation-type disagreement: rephrase 21.6% · numerical 22.7% · semantic 18.1%',
    ],
    visual: 'pert-types',
  },
  { label:'Error Taxonomy',           title:'Hierarchical L1 / L2 Taxonomy',
    stat:'143 failures · 4 L1 buckets',
    bullets:[
      '143 failures hand-classified across all 5 models',
      'Four L1 buckets: ASSUMPTION_VIOLATION 67 (46.9%) · MATHEMATICAL_ERROR 48 (33.6%) · FORMATTING 18 · CONCEPTUAL 10',
      'HALLUCINATION bucket = 0 cases — every task has closed-form ground truth, real signal',
      'Primary failure mode varies sharply per model: ChatGPT assumption-dominated (25/38) · Claude math-dominated (10/19) · Gemini balanced (10A + 9M of 24) · DeepSeek mixed (15A + 13M of 36) · Mistral math+assumption (12M + 8A of 26)',
      'Llama 3.3 70B judge classifies; only 4 of 9 L2 codes activate (E1, E3, E6, E7)',
    ],
    visual: 'failure-mix',
  },
]

// ─── Pipeline SVG icons (monoline, no emoji) ─────────────────
const PIPELINE_ICONS = [
  // 1. Task Generation — grid
  <svg key="p0" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/>
    <rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>
  </svg>,
  // 2. Standardized Prompting — message bubble with text lines
  <svg key="p1" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
    <line x1="8" y1="10" x2="16" y2="10"/><line x1="8" y1="13.5" x2="13" y2="13.5"/>
  </svg>,
  // 3. Multi-Model Evaluation — three connected nodes
  <svg key="p2" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="4" r="2"/><circle cx="4" cy="20" r="2"/><circle cx="20" cy="20" r="2"/>
    <line x1="12" y1="6" x2="4.8" y2="18.3"/><line x1="12" y1="6" x2="19.2" y2="18.3"/>
    <line x1="6" y1="20" x2="18" y2="20"/>
  </svg>,
  // 4. Five-Dimensional Scoring — five ascending bars
  <svg key="p3" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <line x1="3" y1="21" x2="21" y2="21"/>
    <line x1="5" y1="21" x2="5" y2="15"/><line x1="9" y1="21" x2="9" y2="11"/>
    <line x1="13" y1="21" x2="13" y2="7"/><line x1="17" y1="21" x2="17" y2="13"/>
    <line x1="21" y1="21" x2="21" y2="17"/>
  </svg>,
  // 5. Robustness Testing — refresh/cycle arrows
  <svg key="p4" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
    <path d="M3 3v5h5"/>
  </svg>,
  // 6. Error Taxonomy — search with crosshair
  <svg key="p5" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="11" cy="11" r="7"/><line x1="16.5" y1="16.5" x2="22" y2="22"/>
    <line x1="8" y1="11" x2="14" y2="11"/><line x1="11" y1="8" x2="11" y2="14"/>
  </svg>,
]

// ─── Radar ────────────────────────────────────────────────────
// Dimensions: Math Accuracy (pass_rate), Speed (inv latency), Consistency (RQ4 robustness),
// Assumption Compliance (avg_assumption_score), Conceptual Reasoning (avg_structure_score)
// Values derived from 2026-04-26 benchmark: 171 tasks × 5 models, all complete
const RADAR_DIMS = ['Math\nAccuracy','Speed','Consistency','Assumption\nCompliance','Conceptual\nReasoning']
// Last-deploy snapshot of last-deploy radar — used as fallback if /api/v2/rankings fails.
// Indices: 0 Math Accuracy · 1 Speed · 2 Consistency · 3 Assumption Compliance · 4 Conceptual Reasoning
const RADAR_VALS_FALLBACK = {
  claude:   [0.89, 0.61, 0.91, 0.73, 0.95],
  gemini:   [0.86, 0.85, 0.90, 0.70, 0.93],
  chatgpt:  [0.78, 0.90, 0.93, 0.60, 0.87],
  deepseek: [0.79, 0.10, 0.90, 0.66, 0.88],
  mistral:  [0.85, 0.55, 0.92, 0.61, 0.90],
}
const RadarValuesContext = createContext(RADAR_VALS_FALLBACK)
const RadarSourceContext = createContext('fallback') // 'live' or 'fallback'

function normalizeAxis(scores, lo = 0.4, hi = 1.0) {
  const vals = Object.values(scores)
  const min = Math.min(...vals), max = Math.max(...vals)
  if (!isFinite(min) || !isFinite(max) || max === min) {
    return Object.fromEntries(Object.entries(scores).map(([k]) => [k, hi]))
  }
  return Object.fromEntries(
    Object.entries(scores).map(([k, v]) => [k, lo + ((v - min) / (max - min)) * (hi - lo)])
  )
}

function useRadarFromAPI() {
  const [vals, setVals] = useState(RADAR_VALS_FALLBACK)
  const [source, setSource] = useState('fallback')
  useEffect(() => {
    const API = import.meta.env.VITE_API_URL || ''
    fetch(`${API}/api/v2/rankings`)
      .then(r => r.ok ? r.json() : Promise.reject(new Error('http ' + r.status)))
      .then(d => {
        const acc = d?.accuracy?.per_model || {}
        const rob = d?.robustness?.per_model || {}
        const accMean = Object.fromEntries(
          Object.entries(acc).map(([m, v]) => [m, v?.mean ?? 0])
        )
        // Robustness: lower delta = more consistent → invert sign before normalizing
        const consInput = Object.fromEntries(
          Object.entries(rob).map(([m, v]) => [m, -(v?.mean_delta ?? 0)])
        )
        const accNorm = normalizeAxis(accMean)
        const consNorm = normalizeAxis(consInput)
        const next = {}
        for (const m of Object.keys(RADAR_VALS_FALLBACK)) {
          const fallback = RADAR_VALS_FALLBACK[m]
          next[m] = [
            accNorm[m] ?? fallback[0],
            fallback[1],            // Speed — not in API
            consNorm[m] ?? fallback[2],
            fallback[3],            // Assumption Compliance — keep snapshot
            fallback[4],            // Conceptual Reasoning — keep snapshot
          ]
        }
        if (Object.keys(next).length === 5) {
          setVals(next)
          setSource('live')
        }
      })
      .catch(() => { /* keep fallback */ })
  }, [])
  return [vals, source]
}

// ─── Task type tooltips ───────────────────────────────────────
const TASK_TYPE_TOOLTIPS = {
  DISC_MEDIAN:   { title:'Discrete Posterior Median',   subdivision:'Bayesian Point Estimation',        description:'Find the median of a discrete posterior distribution by computing cumulative probability and finding first value where CDF ≥ 0.5.',               textbook:'Carlin & Louis Ch.2' },
  BAYES_RISK:    { title:'Bayesian Risk',               subdivision:'Decision Theory',                   description:'Compute Bayes risk B(δ) = Σ R(δ,θᵢ)·π(θᵢ) — prior-weighted expected loss of an estimator.',                                                   textbook:'Carlin & Louis Ch.2' },
  BIAS_VAR:      { title:'Bias-Variance Decomposition', subdivision:'Frequentist Estimation Theory',     description:'Decompose MSE into bias² + variance. Verifies MSE = Bias² + Variance exactly for a given estimator.',                                             textbook:'Hoff Ch.5' },
  BINOM_FLAT:    { title:'Binomial with Flat Prior',    subdivision:'Conjugate Bayesian Models',         description:'Apply uniform Beta(1,1) prior to Binomial data. Posterior is Beta(x+1, n-x+1) — the Laplace smoothed estimate.',                                textbook:'Bolstad Ch.3' },
  DIRICHLET:     { title:'Dirichlet-Multinomial',       subdivision:'Multivariate Conjugate Models',     description:'Conjugate Bayesian model for categorical data. Dirichlet prior updated with multinomial counts to give Dirichlet posterior.',                     textbook:'Hoff Ch.3 · Bishop Ch.2' },
  FISHER_INFO:   { title:'Fisher Information',          subdivision:'Frequentist Estimation Theory',     description:'Compute I(θ) = E[(∂/∂θ log f)²] — expected curvature of log-likelihood. Measures how much data informs about θ.',                               textbook:'Ghosh et al Ch.1' },
  MINIMAX:       { title:'Minimax Criterion',           subdivision:'Statistical Decision Theory',       description:'Select estimator that minimizes worst-case (maximum) risk over all possible parameter values.',                                                   textbook:'Carlin & Louis Ch.2' },
  MSE_COMPARE:   { title:'MSE Comparison',              subdivision:'Frequentist Estimation Theory',     description:'Compare mean squared errors of competing estimators to determine which is superior.',                                                              textbook:'Hoff Ch.5' },
  NORMAL_GAMMA:  { title:'Normal-Gamma Model',          subdivision:'Conjugate Bayesian Models',         description:'Joint conjugate prior for Normal data with unknown mean and variance.',                                                                            textbook:'Hoff Ch.5' },
  OPT_SCALED:    { title:'Optimal Scaled Estimator',    subdivision:'Frequentist Estimation Theory',     description:'Find constant c minimizing MSE of c·max(Xᵢ). Optimal c = (n+2)/(n+1).',                                                                         textbook:'Ghosh et al Ch.1' },
  RC_BOUND:      { title:'Rao-Cramér Bound',            subdivision:'Frequentist Estimation Theory',     description:'Lower bound for estimator variance: Var(θ̂) ≥ (1+b\'(θ))²/I(θ). Determines whether estimator is efficient.',                                    textbook:'Ghosh et al Ch.1' },
  UNIFORM_MLE:   { title:'Uniform MLE',                 subdivision:'Maximum Likelihood Estimation',     description:'MLE for Uniform(0,θ) is max(X₁,...,Xₙ) — the largest order statistic.',                                                                         textbook:'Ghosh et al Ch.1' },
  MARKOV:        { title:'Markov Chain Analysis',       subdivision:'Stochastic Processes',              description:'Compute n-step transition probabilities, stationary distributions, and verify Chapman-Kolmogorov equations.',                                    textbook:'Norris · Ross Ch.4' },
  ORDER_STAT:    { title:'Order Statistics',            subdivision:'Frequentist Distribution Theory',   description:'Compute density and CDF of k-th order statistic X(k). For Uniform[0,1], X(k) ~ Beta(k, n-k+1).',                                              textbook:'Casella & Berger Ch.5' },
  REGRESSION:    { title:'OLS Linear Regression',       subdivision:'Frequentist Regression',            description:'Ordinary least squares estimators B̂ and Â that minimize sum of squared residuals.',                                                             textbook:'Casella & Berger Ch.11' },
  BOX_MULLER:    { title:'Box-Muller Transform',        subdivision:'Simulation Methods',                description:'Generate Normal(0,1) samples from Uniform(0,1) using η₁=√(-2logU)cos(2πV).',                                                                    textbook:'Robert & Casella Ch.2' },
  HPD:           { title:'HPD Credible Interval',       subdivision:'Bayesian Interval Estimation',      description:'Highest Posterior Density interval — shortest interval containing specified probability mass.',                                                    textbook:'Bolstad Ch.5 · Lee Ch.2' },
  BAYES_FACTOR:  { title:'Bayes Factor',                subdivision:'Bayesian Model Comparison',         description:'BF₁₂ = p(data|M₁)/p(data|M₂) — ratio of marginal likelihoods.',                                                                               textbook:'Carlin & Louis Ch.2 · Lee Ch.4' },
  JEFFREYS:      { title:'Jeffreys Prior',              subdivision:'Objective Bayesian Analysis',       description:'Invariant prior p(θ) ∝ √I(θ). For Binomial: Beta(0.5,0.5).',                                                                                   textbook:'Ghosh et al Ch.5 · Lee Ch.3' },
  PPC:           { title:'Posterior Predictive Check',  subdivision:'Bayesian Model Assessment',         description:'Check model fit by comparing observed T(y) to replicated T(y_rep).',                                                                             textbook:'Hoff Ch.4 · Carlin & Louis Ch.2' },
  BAYES_REG:     { title:'Bayesian Linear Regression',  subdivision:'Bayesian Regression',               description:'Normal-Inverse-Gamma conjugate prior for regression.',                                                                                           textbook:'Carlin & Louis Ch.4 · Hoff Ch.9' },
  MLE_MAP:       { title:'MLE vs MAP Comparison',       subdivision:'Bayesian vs Frequentist Estimation',description:'Compare MLE, MAP (posterior mode), and posterior mean. MAP shrinks MLE toward prior mean.',                                                     textbook:'Ghosh et al Ch.2 · Hoff Ch.3' },
  CI_CREDIBLE:   { title:'CI vs Credible Interval',     subdivision:'Frequentist vs Bayesian Inference', description:'Compare frequentist 95% CI with Bayesian 95% credible interval.',                                                                               textbook:'All 7 textbooks' },
  LOG_ML:        { title:'Log Marginal Likelihood',     subdivision:'Bayesian Model Selection',          description:'log p(data|prior) — log normalizing constant of the posterior.',                                                                                  textbook:'Carlin & Louis Ch.2 · Ghosh et al Ch.2' },
  GAMBLER:       { title:"Gambler's Ruin",              subdivision:'Stochastic Processes',              description:'Probability of ruin starting from fortune i with absorbing barriers at 0 and M.',                                                               textbook:'Ross Ch.4' },
  STATIONARY:    { title:'Stationary Distribution',     subdivision:'Markov Chain Theory',               description:'Limiting distribution π satisfying π@P = π, sum(π)=1.',                                                                                         textbook:'Norris Ch.1' },
  RANGE_DIST:    { title:'Range Distribution',          subdivision:'Order Statistics',                  description:'Distribution of R = max(Xᵢ) - min(Xᵢ) for Uniform[0,1] samples.',                                                                              textbook:'Casella & Berger Ch.5' },
  MLE_EFFICIENCY:{ title:'MLE Efficiency',              subdivision:'Frequentist Estimation Theory',     description:'Verify MLE variance equals Rao-Cramér lower bound.',                                                                                             textbook:'Ghosh et al Ch.1' },
  BETA_BINOM:    { title:'Beta-Binomial Model',         subdivision:'Conjugate Bayesian Models',         description:'Canonical conjugate model: Beta(α,β) prior + Binomial likelihood = Beta(α+x, β+n-x) posterior.',                                              textbook:'Hoff Ch.3 · Bolstad Ch.3' },
  GAMMA_POISSON: { title:'Gamma-Poisson Model',         subdivision:'Conjugate Bayesian Models',         description:'Conjugate model for count data: Gamma(α,β) prior + Poisson likelihood = Gamma(α+Σx, β+n) posterior.',                                         textbook:'Hoff Ch.3 · Bolstad Ch.10' },
  CONCEPTUAL:    { title:'Conceptual Reasoning',        subdivision:'Bayesian Theory & Interpretation',  description:'Tests deep understanding of Bayesian concepts: prior influence, credible vs confidence intervals, exchangeability.',                              textbook:'All 7 textbooks' },
  // Phase 2 — Computational Bayesian Methods
  GIBBS:         { title:'Gibbs Sampling',              subdivision:'Computational Bayes (Phase 2)',     description:'An MCMC technique that samples from a joint posterior one variable at a time using each variable\'s conditional distribution. Alternates between p(θ₁|θ₂,data) and p(θ₂|θ₁,data) — converges to the joint posterior after burn-in.',        textbook:'Hoff Ch.10 · Carlin & Louis Ch.4' },
  MH:            { title:'Metropolis–Hastings (MH)',    subdivision:'Computational Bayes (Phase 2)',     description:'A general MCMC algorithm: propose a new θ* from a proposal distribution q, then accept it with probability α = min(1, p(θ*|data)·q(θ|θ*) / p(θ|data)·q(θ*|θ)). Works on any target distribution, even unnormalized posteriors.',      textbook:'Hoff Ch.10 · Carlin & Louis Ch.4' },
  HMC:           { title:'Hamiltonian Monte Carlo (HMC)',subdivision:'Computational Bayes (Phase 2)',    description:'An advanced MCMC method that uses "momentum" variables and physics-inspired leapfrog integration to make large, informed jumps across the posterior. Avoids the random-walk inefficiency of MH. Used in Stan and PyMC.',                  textbook:'Neal (2011) · Carlin & Louis Ch.4' },
  RJMCMC:        { title:'Reversible Jump MCMC',        subdivision:'Computational Bayes (Phase 2)',     description:'Extends standard MCMC to jump between models of different dimensionality (model selection). Here: jumps between M₁ (one group mean) and M₂ (two group means), computing posterior model probabilities via prior-weighted odds.',          textbook:'Green (1995) · Carlin & Louis Ch.7' },
  VB:            { title:'Variational Bayes (CAVI)',    subdivision:'Computational Bayes (Phase 2)',     description:'Approximates the posterior by finding a simpler distribution q(θ) that minimizes KL-divergence from the true posterior. CAVI (Coordinate Ascent VI) optimizes each factor of the mean-field approximation in turn, maximizing the ELBO.', textbook:'Blei et al (2017) · Bishop Ch.10' },
  ABC:           { title:'Approximate Bayesian Computation (ABC)',subdivision:'Computational Bayes (Phase 2)', description:'Bypasses likelihood evaluation entirely: draw θ from prior, simulate fake data, accept θ if a summary statistic of simulated data matches the observed data within tolerance ε. Used when the likelihood is intractable.',              textbook:'Sisson et al (2018) · Carlin & Louis Ch.4' },
  HIERARCHICAL:  { title:'Hierarchical Bayesian Model', subdivision:'Computational Bayes (Phase 2)',     description:'Pools information across groups by adding hyperpriors on the group-level parameters. Each group\'s posterior is a compromise between its own data and the population-level estimate — known as "shrinkage" toward the grand mean.',          textbook:'Hoff Ch.8 · Gelman et al Ch.5' },
}

// ─── Animation variants ───────────────────────────────────────
const fadeUp = {
  hidden: { opacity: 0, y: 28, filter: 'blur(6px)' },
  visible: {
    opacity: 1, y: 0, filter: 'blur(0px)',
    transition: { duration: 0.7, ease: [0.22, 1, 0.36, 1] }
  }
}

const staggerContainer = (delay = 0) => ({
  hidden: {},
  visible: { transition: { staggerChildren: 0.1, delayChildren: delay } }
})

const staggerItem = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.22, 1, 0.36, 1] } }
}

const scaleIn = {
  hidden: { opacity: 0, scale: 0.92 },
  visible: { opacity: 1, scale: 1, transition: { type: 'spring', stiffness: 300, damping: 24 } }
}

// ═══════════════════════════════════════════════════════════════
//  UTILITY COMPONENTS
// ═══════════════════════════════════════════════════════════════

// ─── Scroll Progress ──────────────────────────────────────────
function ScrollProgress() {
  const { scrollYProgress } = useScroll()
  const scaleX = useTransform(scrollYProgress, [0, 1], [0, 1])
  return (
    <motion.div
      className="scroll-progress"
      style={{ scaleX, transformOrigin: 'left' }}
    />
  )
}

// ─── Back to Top ──────────────────────────────────────────────
function BackToTop() {
  const [vis, setVis] = useState(false)
  useEffect(() => {
    const fn = () => setVis(window.scrollY > window.innerHeight * 0.8)
    window.addEventListener('scroll', fn, { passive: true })
    return () => window.removeEventListener('scroll', fn)
  }, [])
  return (
    <AnimatePresence>
      {vis && (
        <motion.button
          key="back-to-top"
          className="back-to-top"
          initial={{ opacity: 0, y: 16, scale: 0.8 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 16, scale: 0.8 }}
          whileHover={{ y: -4, boxShadow: 'var(--glow-md)' }}
          whileTap={{ scale: 0.92 }}
          transition={{ type: 'spring', stiffness: 400, damping: 28 }}
          onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
        >↑</motion.button>
      )}
    </AnimatePresence>
  )
}

// ─── FadeIn ───────────────────────────────────────────────────
function FadeIn({ children, delay = 0, style = {}, className = '' }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, amount: 0.15 })
  return (
    <motion.div
      ref={ref}
      initial="hidden"
      animate={isInView ? 'visible' : 'hidden'}
      variants={fadeUp}
      transition={{ delay: delay / 1000 }}
      style={style}
      className={className}
    >
      {children}
    </motion.div>
  )
}

// ─── Section Divider ──────────────────────────────────────────
function SectionDivider() { return <div className="section-divider" /> }

// ─── Hero Orbs ────────────────────────────────────────────────
function HeroOrbs() {
  return (
    <div className="hero-orbs" aria-hidden="true">
      <motion.div className="orb orb-1"
        animate={{ x:[0,70,-40,0], y:[0,-50,35,0], scale:[1,1.12,0.94,1] }}
        transition={{ duration:22, repeat:Infinity, ease:'easeInOut' }}
      />
      <motion.div className="orb orb-2"
        animate={{ x:[0,-55,45,0], y:[0,55,-35,0], scale:[1,0.88,1.1,1] }}
        transition={{ duration:28, repeat:Infinity, ease:'easeInOut', delay:3 }}
      />
      <motion.div className="orb orb-3"
        animate={{ x:[0,40,-60,0], y:[0,-30,55,0], scale:[1,1.18,0.91,1] }}
        transition={{ duration:35, repeat:Infinity, ease:'easeInOut', delay:7 }}
      />
    </div>
  )
}

// ─── CountUp ──────────────────────────────────────────────────
function CountUp({ target, duration=2000, suffix='' }) {
  const [val, setVal] = useState(0)
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true })
  useEffect(() => {
    if (!isInView) return
    let start = null
    const step = ts => {
      if (!start) start = ts
      const p = Math.min((ts-start)/duration, 1)
      const ease = 1 - Math.pow(1 - p, 3)
      setVal(Math.floor(ease * target))
      if (p < 1) requestAnimationFrame(step)
    }
    requestAnimationFrame(step)
  }, [target, duration, isInView])
  return <span ref={ref}>{val}{suffix}</span>
}

// ─── Tooltip ──────────────────────────────────────────────────
function Tooltip({ text, children }) {
  const [show, setShow] = useState(false)
  const [pos,  setPos]  = useState({ x:0, y:0 })
  const timer           = useRef(null)

  const onEnter = e => {
    const r = e.currentTarget.getBoundingClientRect()
    setPos({ x: r.left, y: r.bottom + 8 })
    timer.current = setTimeout(() => setShow(true), 250)
  }
  const onLeave = () => { clearTimeout(timer.current); setShow(false) }

  return (
    <span style={{ position:'relative', display:'inline-block' }} onMouseEnter={onEnter} onMouseLeave={onLeave}>
      {children}
      <AnimatePresence>
        {show && (
          <motion.div
            key="tooltip"
            initial={{ opacity: 0, y: 6, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 6, scale: 0.96 }}
            transition={{ duration: 0.18, ease: 'easeOut' }}
            style={{
              position:'fixed', left: Math.min(pos.x, window.innerWidth-300), top: pos.y,
              width:280, background:'#0D1B2A', border:'1px solid var(--border-hover)',
              borderRadius:10, padding:'12px 14px', zIndex:9999,
              boxShadow:'var(--glow-md)', pointerEvents:'none',
              fontSize:12, color:'var(--text-primary)', lineHeight:1.6,
            }}
          >
            {text}
          </motion.div>
        )}
      </AnimatePresence>
    </span>
  )
}

// ─── Card ─────────────────────────────────────────────────────
function Card({ children, className='', glow=false, onClick, style={} }) {
  return (
    <motion.div
      className={`card ${glow?'card-glow':''} ${className}`}
      style={style}
      onClick={onClick}
      whileHover={onClick ? { y: -3, boxShadow: 'var(--glow-md)', borderColor: 'var(--border-hover)' } : undefined}
      transition={{ type: 'spring', stiffness: 400, damping: 30 }}
    >
      {children}
    </motion.div>
  )
}

// ─── Pill ─────────────────────────────────────────────────────
function Pill({ children, color=C.aqua, bg }) {
  return (
    <span style={{
      fontSize:11, padding:'3px 10px', borderRadius:10, fontWeight:700,
      color, border:`1px solid ${color}60`, background: bg||`${color}15`,
    }}>
      {children}
    </span>
  )
}

// ─── Section title ────────────────────────────────────────────
function SectionTitle({ children, sub }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, amount: 0.5 })
  return (
    <div ref={ref} style={{ textAlign:'center', marginBottom:56 }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      >
        <h2 style={{ fontSize:'clamp(32px,4vw,48px)', fontWeight:700, color:'var(--text-primary)', margin:0, lineHeight:1.2 }}>
          {children}
        </h2>
        {sub && (
          <p style={{ color:'var(--text-secondary)', fontSize:15, margin:'12px 0 0', lineHeight:1.7 }}>{sub}</p>
        )}
        <motion.div
          initial={{ scaleX: 0 }}
          animate={isInView ? { scaleX: 1 } : { scaleX: 0 }}
          transition={{ duration: 0.7, delay: 0.25, ease: [0.22, 1, 0.36, 1] }}
          style={{
            width:64, height:3,
            background:'linear-gradient(90deg, var(--aqua), var(--blue))',
            margin:'16px auto 0', borderRadius:2,
            transformOrigin: 'left',
          }}
        />
      </motion.div>
    </div>
  )
}

// ─── Animated Scoring Bars ────────────────────────────────────
function AnimatedScoringBars() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, amount: 0.3 })

  const bars = [
    { label:'Assumption Compliance',   weight:30, key:'A', color:'#00897B', desc:'Acknowledgment of prior, data, and model assumptions. Heaviest weight (Du 2025, Boye & Moell 2025, Yamauchi 2025).' },
    { label:'Reasoning Quality',       weight:25, key:'R', color:'#EC4899', desc:'Shows work, identifies model, states formula, interprets result. Most externally-judgeable dimension.' },
    { label:'Method Structure',        weight:20, key:'M', color:'#A78BFA', desc:'Correct method selection and derivation steps. Partially redundant with R.' },
    { label:'Confidence Calibration',  weight:15, key:'C', color:'#F59E0B', desc:'Expressed certainty matches actual accuracy. Separate evaluation track honestly disclosed.' },
    { label:'Numeric Accuracy',       weight:10, key:'N', color:'#00FFE0', desc:'Exact numerical match within tolerance bounds. Necessary but trivially checkable.' },
  ]

  return (
    <div ref={ref}>
      <div style={{ color:'var(--aqua)', fontSize:10, fontWeight:700, letterSpacing:'0.12em', marginBottom:6, textAlign:'center' }}>
        COMPOSITE SCORE = A·0.30 + R·0.25 + M·0.20 + C·0.15 + N·0.10
      </div>
      <div style={{ color:'var(--text-muted)', fontSize:10, textAlign:'center', marginBottom:20 }}>
        Literature-derived weights · Pass threshold: final_score ≥ 0.5
      </div>
      {/* Horizontal grid of 5 scoring components */}
      <div style={{ display:'grid', gridTemplateColumns:'repeat(5,1fr)', gap:10 }}>
        {bars.map(b => (
          <div key={b.key} style={{ background:'rgba(0,0,0,0.2)', border:`1px solid ${b.color}33`, borderRadius:10, padding:'14px 10px', textAlign:'center' }}>
            <div style={{ width:34, height:34, borderRadius:8, background:`${b.color}18`, border:`1.5px solid ${b.color}`, display:'flex', alignItems:'center', justifyContent:'center', color:b.color, fontWeight:800, fontSize:15, margin:'0 auto 8px' }}>{b.key}</div>
            <div style={{ color:'var(--text-primary)', fontSize:11, fontWeight:700, marginBottom:4, lineHeight:1.3 }}>{b.label}</div>
            <div style={{ color:b.color, fontWeight:800, fontSize:16, fontFamily:'var(--font-mono)', marginBottom:8 }}>{b.weight}%</div>
            <div style={{ height:5, background:'rgba(255,255,255,0.06)', borderRadius:3, overflow:'hidden' }}>
              <motion.div
                initial={{ width:0 }}
                animate={isInView ? { width:'100%' } : { width:0 }}
                transition={{ duration:1.0, delay:bars.indexOf(b)*0.15, ease:[0.22,1,0.36,1] }}
                style={{ height:'100%', borderRadius:3, background:`linear-gradient(90deg,${b.color}99,${b.color})`, boxShadow:`0 0 8px ${b.color}66` }}
              />
            </div>
            <div style={{ color:'rgba(255,255,255,0.4)', fontSize:9, marginTop:6, lineHeight:1.4 }}>{b.desc}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

// ─── Live Results Panel ───────────────────────────────────────
function LiveResults() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, amount: 0.2 })

  const complete = resultsData.models_complete
  const partial  = resultsData.models_partial
  const totalModels = 5

  // Best model by avg_score (complete models only)
  const bestModel = complete.reduce((best, m) => {
    const s = resultsData.by_model[m]?.avg_score ?? 0
    return s > (resultsData.by_model[best]?.avg_score ?? 0) ? m : best
  }, complete[0])

  // Overall avg across complete models
  const overallAvg = complete.reduce((sum, m) => sum + (resultsData.by_model[m]?.avg_score ?? 0), 0) / complete.length

  // Task type extremes (using complete models' data weighted equally)
  const ttStats = resultsData.task_type_stats
  const sorted = Object.entries(ttStats).sort((a, b) => a[1].avg - b[1].avg)
  const hardest = sorted[0]
  const easiest = sorted[sorted.length - 1]

  const updatedAt = new Date(resultsData.generated_at).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric'
  })

  const STAT = ({ label, value, sub, color = '#00FFE0' }) => (
    <div style={{
      background: 'rgba(0,0,0,0.28)',
      border: '1px solid rgba(0,255,224,0.12)',
      borderRadius: 10,
      padding: '12px 16px',
      flex: '1 1 140px',
      minWidth: 0,
    }}>
      <div style={{ color: 'rgba(0,255,224,0.55)', fontSize: 9, fontWeight: 700, letterSpacing: '0.1em', marginBottom: 5, textTransform: 'uppercase' }}>
        {label}
      </div>
      <div style={{ color, fontFamily: 'var(--font-mono)', fontWeight: 800, fontSize: String(value).length > 12 ? 11 : 15, marginBottom: sub ? 3 : 0, wordBreak: 'break-all', lineHeight: 1.3 }}>
        {value}
      </div>
      {sub && (
        <div style={{ color: 'rgba(255,255,255,0.4)', fontSize: 10 }}>{sub}</div>
      )}
    </div>
  )

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 16 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 16 }}
      transition={{ duration: 0.6, delay: 0.2 }}
      style={{
        marginTop: 24,
        border: '1px solid rgba(0,255,224,0.28)',
        borderRadius: 14,
        padding: '18px 20px',
        background: 'rgba(0,255,224,0.03)',
        boxShadow: '0 0 28px rgba(0,255,224,0.07)',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{ width: 7, height: 7, borderRadius: '50%', background: '#00FFE0', boxShadow: '0 0 8px #00FFE0', animation: 'pulse 1.4s ease-in-out infinite alternate' }} />
          <span style={{ color: '#00FFE0', fontSize: 10, fontWeight: 700, letterSpacing: '0.12em' }}>LIVE RESULTS</span>
        </div>
        <span style={{ color: 'rgba(255,255,255,0.3)', fontSize: 9 }}>Last updated {updatedAt}</span>
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
        <STAT
          label="Models Benchmarked"
          value={`${complete.length} / ${totalModels}`}
          sub={partial.length ? `+${partial.length} partial (${partial.join(', ')})` : 'all complete'}
        />
        <STAT
          label="Overall Avg Score"
          value={overallAvg.toFixed(3)}
          sub={`${resultsData.total_runs} total runs`}
        />
        <STAT
          label="Best Model"
          value={bestModel.toUpperCase()}
          sub={`avg ${(resultsData.by_model[bestModel]?.avg_score ?? 0).toFixed(3)}`}
          color="#A78BFA"
        />
        <STAT
          label="Hardest Task Type"
          value={hardest[0]}
          sub={`avg ${hardest[1].avg.toFixed(3)}`}
          color="#FF6B6B"
        />
        <STAT
          label="Easiest Task Type"
          value={easiest[0]}
          sub={`avg ${easiest[1].avg.toFixed(3)}`}
          color="#7FFFD4"
        />
      </div>
    </motion.div>
  )
}

// ─── Tier Ladder ─────────────────────────────────────────────
const TIER_TASK_EXAMPLES = {
  1: ['BETA_BINOM', 'GAMMA_POISSON', 'BINOM_FLAT', 'DIRICHLET'],
  2: ['NORMAL_GAMMA', 'JEFFREYS', 'MARKOV', 'GIBBS', 'MH', 'VB'],
  3: ['BAYES_RISK', 'HPD', 'HMC', 'RJMCMC', 'ABC', 'HIERARCHICAL'],
  4: ['BAYES_FACTOR', 'LOG_ML', 'BIAS_VAR', 'MSE_COMPARE', 'RC_BOUND'],
}
const TIER_CHALLENGES = {
  1: ['Single conjugate update', 'Direct Bayes theorem application', 'Closed-form posterior'],
  2: ['Chained multi-step inference', 'MCMC sampling (Gibbs/MH)', 'Distribution property derivation'],
  3: ['Decision theory optimization', 'Computational Bayes (HMC/RJMCMC/ABC)', 'Multi-framework integration'],
  4: ['Competing estimator comparison', 'Asymptotic efficiency theory', 'Advanced MCMC diagnostics'],
}

function TierLadder() {
  const [expanded, setExpanded] = useState(null)
  const total = statsData.total_tasks

  return (
    <div>
      <div style={{ color:'var(--aqua)', fontSize:10, fontWeight:700, letterSpacing:'0.12em', marginBottom:14, textAlign:'center' }}>
        DIFFICULTY LADDER · {total} TASKS
      </div>

      {/* 4 horizontal tier cards */}
      <div style={{ display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:8, marginBottom:16 }}>
        {[1,2,3,4].map(tier => {
          const info = TIER_INFO[tier]
          const pct  = Math.round((info.tasks / total) * 100)
          const isOpen = expanded === tier
          return (
            <motion.div
              key={tier}
              onClick={() => setExpanded(isOpen ? null : tier)}
              style={{
                background: isOpen ? `${info.color}0D` : 'rgba(0,0,0,0.22)',
                border:`1px solid ${isOpen ? info.color : info.color+'33'}`,
                borderRadius:10, cursor:'pointer', overflow:'hidden', padding:'12px 10px',
                textAlign:'center',
              }}
              whileHover={{ borderColor:info.color+'88', background:`${info.color}07` }}
              transition={{ type:'spring', stiffness:400, damping:30 }}
            >
              {/* T badge */}
              <div style={{ width:32, height:32, borderRadius:8, background:`${info.color}18`,
                border:`1.5px solid ${info.color}`, margin:'0 auto 8px',
                display:'flex', alignItems:'center', justifyContent:'center',
                color:info.color, fontWeight:800, fontSize:11,
                boxShadow: isOpen ? `0 0 12px ${info.color}44` : 'none' }}>
                T{tier}
              </div>
              {/* Difficulty dots */}
              <div style={{ display:'flex', justifyContent:'center', gap:3, marginBottom:8 }}>
                {[1,2,3,4].map(d => (
                  <div key={d} style={{ width:5, height:5, borderRadius:'50%',
                    background: d<=tier ? info.color : `${info.color}20`,
                    boxShadow: d<=tier ? `0 0 4px ${info.color}` : 'none' }}/>
                ))}
              </div>
              <div style={{ color:info.color, fontWeight:700, fontSize:10, marginBottom:3, letterSpacing:'0.04em' }}>{info.label}</div>
              <div style={{ color:'var(--text-muted)', fontSize:9, fontFamily:'var(--font-mono)' }}>{info.tasks} tasks · {pct}%</div>
              {/* Mini progress bar */}
              <div style={{ height:2, background:'rgba(255,255,255,0.06)', borderRadius:1, marginTop:8, overflow:'hidden' }}>
                <motion.div style={{ height:'100%', background:info.color, borderRadius:1 }}
                  initial={{ width:0 }} animate={{ width:`${pct}%` }}
                  transition={{ duration:0.6, ease:'easeOut', delay:0.1 }}/>
              </div>
              <div style={{ color:info.color+'80', fontSize:8, marginTop:5 }}>{isOpen ? '▲ close' : '▼ detail'}</div>
            </motion.div>
          )
        })}
      </div>

      {/* Expanded detail panel */}
      <AnimatePresence>
        {expanded !== null && (
          <motion.div
            initial={{ height:0, opacity:0 }}
            animate={{ height:'auto', opacity:1 }}
            exit={{ height:0, opacity:0 }}
            transition={{ duration:0.25, ease:[0.22,1,0.36,1] }}
            style={{ overflow:'hidden' }}
          >
            {(() => {
              const info = TIER_INFO[expanded]
              return (
                <div style={{ padding:'12px 0 4px' }}>
                  <p style={{ color:'var(--text-secondary)', fontSize:17, lineHeight:1.85, margin:'0 0 16px' }}>
                    {info.detail}
                  </p>
                  <div style={{ marginBottom:12 }}>
                    <div style={{ fontSize:11, color:info.color+'80', fontWeight:700, letterSpacing:'0.1em', marginBottom:8 }}>KEY CHALLENGES</div>
                    <div style={{ display:'flex', flexWrap:'wrap', gap:6 }}>
                      {TIER_CHALLENGES[expanded].map(c => (
                        <div key={c} style={{ display:'flex', alignItems:'center', gap:5 }}>
                          <div style={{ width:4, height:4, borderRadius:'50%', background:info.color, flexShrink:0 }}/>
                          <span style={{ fontSize:14, color:'var(--text-secondary)' }}>{c}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div style={{ fontSize:11, color:info.color+'80', fontWeight:700, letterSpacing:'0.1em', marginBottom:8 }}>TASK TYPES</div>
                  <div style={{ display:'flex', gap:5, flexWrap:'wrap' }}>
                    {TIER_TASK_EXAMPLES[expanded].map(k => (
                      <span key={k} style={{ fontSize:11, padding:'4px 9px', borderRadius:4,
                        background:`${info.color}14`, color:info.color,
                        border:`1px solid ${info.color}33`, fontFamily:'var(--font-mono)' }}>{k}</span>
                    ))}
                  </div>
                </div>
              )
            })()}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// ─── Radar Chart ─────────────────────────────────────────────
function RadarChart({ model }) {
  const pad=72, inner=200, size=inner+pad*2
  const cx=size/2, cy=size/2, R=80, n=5
  const step = (Math.PI*2)/n
  const radarMap = useContext(RadarValuesContext)
  const vals = radarMap[model.id] || Array(n).fill(0.7)

  const pts = vals.map((v,i) => {
    const a = i*step - Math.PI/2
    return { x: cx+v*R*Math.cos(a), y: cy+v*R*Math.sin(a) }
  })
  const axes = Array.from({length:n},(_,i)=>{
    const a = i*step - Math.PI/2
    const lx = cx+(R+38)*Math.cos(a), ly = cy+(R+38)*Math.sin(a)
    const anchor = lx < cx-5 ? 'end' : lx > cx+5 ? 'start' : 'middle'
    return { ex: cx+R*Math.cos(a), ey: cy+R*Math.sin(a), lx, ly, anchor }
  })
  const rings = [0.25,0.5,0.75,1].map(s =>
    Array.from({length:n},(_,i)=>{
      const a=i*step-Math.PI/2
      return `${cx+s*R*Math.cos(a)},${cy+s*R*Math.sin(a)}`
    }).join(' ')
  )
  const poly = pts.map(p=>`${p.x},${p.y}`).join(' ')

  return (
    <div className="radar-wrap" style={{ width:'100%', maxWidth:size, margin:'16px auto' }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} preserveAspectRatio="xMidYMid meet" style={{ width:'100%', height:'auto', display:'block' }}>
        {rings.map((r,i)=>(
          <polygon key={i} points={r} fill="none" stroke="rgba(0,255,224,0.1)" strokeWidth="1"/>
        ))}
        {axes.map((ax,i)=>{
          const lines = RADAR_DIMS[i].split('\n')
          return (
            <g key={i}>
              <line x1={cx} y1={cy} x2={ax.ex} y2={ax.ey} stroke="rgba(0,255,224,0.12)" strokeWidth="1"/>
              {lines.map((l,j)=>(
                <text key={j} x={ax.lx} y={ax.ly+(j*11)-(lines.length>1?5.5:0)}
                  textAnchor={ax.anchor} dominantBaseline="middle"
                  fontSize="8.5" fill="var(--text-secondary)">
                  {l}
                </text>
              ))}
            </g>
          )
        })}
        <polygon points={poly} fill={model.color+'4D'} stroke={model.color} strokeWidth="1.5"/>
        {pts.map((p,i)=><circle key={i} cx={p.x} cy={p.y} r="3" fill={model.color}/>)}
      </svg>
    </div>
  )
}

// ─── Key Findings: 2 rows of 3 cards · viz between rows · viz after row 2 ───
function KeyFindingsSection() {
  const { cards, loading } = useKeyFindings()
  if (!cards || cards.length < 6) return <KeyFindings/>
  return (
    <div style={{ maxWidth: 1300, margin: '0 auto' }}>
      {/* Cards 1-3 */}
      <div className="kf-card-row kf-card-row-3">
        <KeyFindingCard card={cards[0]} index={0} loading={loading}/>
        <KeyFindingCard card={cards[1]} index={1} loading={loading}/>
        <KeyFindingCard card={cards[2]} index={2} loading={loading}/>
      </div>

      {/* Viz #1 — per-model keyword-judge disagreement */}
      <div className="kf-viz-spacer">
        <PerModelPassFlipPanel/>
      </div>

      {/* Cards 4-6 */}
      <div className="kf-card-row kf-card-row-3">
        <KeyFindingCard card={cards[3]} index={3} loading={loading}/>
        <KeyFindingCard card={cards[4]} index={4} loading={loading}/>
        <KeyFindingCard card={cards[5]} index={5} loading={loading}/>
      </div>

      {/* Viz #2 — three rankings comparison */}
      <div className="kf-viz-spacer">
        <ThreeRankingsComparison/>
      </div>
    </div>
  )
}

// ─── Multi-model radar ────────────────────────────────────────
const MODEL_COLORS = { claude:'#00CED1', gemini:'#FF6B6B', chatgpt:'#7FFFD4', deepseek:'#4A90D9', mistral:'#A78BFA' }
function MultiModelRadar() {
  const [hoveredModel, setHoveredModel] = useState(null)
  const radarMap = useContext(RadarValuesContext)
  const pad=96, inner=320, size=inner+pad*2
  const cx=size/2, cy=size/2, R=130, n=5
  const step = (Math.PI*2)/n
  const rings = [0.25,0.5,0.75,1].map(s =>
    Array.from({length:n},(_,i)=>{ const a=i*step-Math.PI/2; return `${cx+s*R*Math.cos(a)},${cy+s*R*Math.sin(a)}` }).join(' ')
  )
  const axes = Array.from({length:n},(_,i)=>{
    const a=i*step-Math.PI/2
    const lx=cx+(R+60)*Math.cos(a), ly=cy+(R+60)*Math.sin(a)
    const anchor = lx < cx-5 ? 'end' : lx > cx+5 ? 'start' : 'middle'
    return { ex:cx+R*Math.cos(a), ey:cy+R*Math.sin(a), lx, ly, anchor }
  })
  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16, width:'100%' }}>
      <div className="radar-wrap" style={{ position:'relative', width:'100%', maxWidth:size }}>
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} preserveAspectRatio="xMidYMid meet" style={{ width:'100%', height:'auto', display:'block' }}>
          {rings.map((r,i)=><polygon key={i} points={r} fill="none" stroke="rgba(0,255,224,0.08)" strokeWidth="1"/>)}
          {axes.map((ax,i)=>{
            const lines=RADAR_DIMS[i].split('\n')
            return (
              <g key={i}>
                <line x1={cx} y1={cy} x2={ax.ex} y2={ax.ey} stroke="rgba(0,255,224,0.1)" strokeWidth="1"/>
                {lines.map((l,j)=>(
                  <text key={j} x={ax.lx} y={ax.ly+(j*14)-(lines.length>1?7:0)} textAnchor={ax.anchor} dominantBaseline="middle" fontSize="12" fill="rgba(200,220,230,0.95)" fontWeight="600">{l}</text>
                ))}
              </g>
            )
          })}
          {Object.entries(radarMap).map(([id, vals]) => {
            const pts=vals.map((v,i)=>{ const a=i*step-Math.PI/2; return `${cx+v*R*Math.cos(a)},${cy+v*R*Math.sin(a)}` }).join(' ')
            const col=MODEL_COLORS[id]||'#00FFE0'
            const isHov = hoveredModel===id
            const dimmed = hoveredModel && !isHov
            return (
              <polygon
                key={id}
                points={pts}
                fill={isHov ? col+'44' : col+'1A'}
                stroke={col}
                strokeWidth={isHov ? 2.5 : 1.5}
                opacity={dimmed ? 0.18 : isHov ? 1 : 0.85}
                style={{ cursor:'pointer', transition:'opacity 0.2s, stroke-width 0.2s' }}
                onMouseEnter={()=>setHoveredModel(id)}
                onMouseLeave={()=>setHoveredModel(null)}
              />
            )
          })}
        </svg>
        {/* Hover label */}
        {hoveredModel && (
          <div style={{
            position:'absolute', left:'50%', top:'50%',
            transform:'translate(-50%,-50%)',
            pointerEvents:'none', textAlign:'center',
            background:'rgba(10,14,26,0.85)', borderRadius:8,
            padding:'6px 12px', border:`1px solid ${MODEL_COLORS[hoveredModel]}55`,
          }}>
            <div style={{ color:MODEL_COLORS[hoveredModel], fontSize:11, fontWeight:700, fontFamily:'var(--font-mono)' }}>
              {hoveredModel.toUpperCase()}
            </div>
            <div style={{ display:'flex', flexDirection:'column', gap:2, marginTop:4 }}>
              {RADAR_DIMS.map((d,i)=>(
                <div key={i} style={{ fontSize:9, color:'rgba(200,220,230,0.8)', display:'flex', justifyContent:'space-between', gap:8 }}>
                  <span>{d.replace('\n',' ')}</span>
                  <span style={{ color:MODEL_COLORS[hoveredModel], fontWeight:700 }}>{(radarMap[hoveredModel][i]*100).toFixed(0)}%</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
      {/* Legend — horizontal row below radar */}
      <div style={{ display:'flex', flexDirection:'row', flexWrap:'wrap', gap:'6px 18px', justifyContent:'center' }}>
        {Object.keys(radarMap).map(id=>(
          <div
            key={id}
            style={{ display:'flex', alignItems:'center', gap:8, fontSize:13, color: hoveredModel===id ? MODEL_COLORS[id] : 'var(--text-secondary)', cursor:'pointer', transition:'color 0.2s', padding:'4px 10px', borderRadius:6, background: hoveredModel===id ? MODEL_COLORS[id]+'14' : 'transparent' }}
            onMouseEnter={()=>setHoveredModel(id)}
            onMouseLeave={()=>setHoveredModel(null)}
          >
            <div style={{ width:18, height:4, borderRadius:2, background:MODEL_COLORS[id]||'#00FFE0', flexShrink:0 }}/>
            <span style={{ fontFamily:'var(--font-mono)', fontWeight: hoveredModel===id ? 700 : 600 }}>{id.toUpperCase()}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

// ─── Section wrapper ──────────────────────────────────────────
function Section({ id, children, minHeight='100vh' }) {
  return (
    <section id={id} className={`sec-${id}`}
      style={{ minHeight, padding:'96px 64px 80px', position:'relative', zIndex:1 }}>
      {children}
    </section>
  )
}

// ═══════════════════════════════════════════════════════════════
//  1. OVERVIEW
// ═══════════════════════════════════════════════════════════════
function Overview() {
  return (
    <Section id="overview">
      <HeroOrbs />
      <div style={{ position:'absolute', inset:0, overflow:'hidden', zIndex:0, pointerEvents:'none' }}>
        <HeroNetworkBg opacity={0.55} />
      </div>

      <div style={{ position:'relative', zIndex:1, display:'flex', flexDirection:'column', justifyContent:'center', alignItems:'center', minHeight:'calc(100vh - 200px)' }}>
        <motion.div
          style={{ textAlign:'center', maxWidth:980 }}
          initial="hidden"
          animate="visible"
          variants={staggerContainer(0.15)}
        >
          {/* Hero title */}
          <motion.h1 variants={fadeUp} style={{ fontSize:'clamp(32px,5.5vw,66px)', fontWeight:700, lineHeight:1.15, color:'var(--text-primary)', marginBottom:24 }}>
            Benchmarking LLMs on{' '}
            <span style={{ background:'linear-gradient(135deg,var(--aqua),var(--blue))', WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent' }}>
              Bayesian Statistical Reasoning
            </span>
          </motion.h1>

          <motion.p variants={fadeUp} style={{ color:'var(--text-secondary)', fontSize:15, marginBottom:44, lineHeight:2 }}>
            American University of Armenia
            <br/><b style={{ color:'var(--text-primary)' }}>Student: </b>
            <a href="https://www.linkedin.com/in/albert-simonyan-3b0560311/" target="_blank" rel="noopener noreferrer" style={{ color:'var(--aqua)', textDecoration:'none', fontWeight:700 }}>Albert Simonyan</a>
            <br/><b style={{ color:'var(--text-primary)' }}>Supervisor: </b>
            <a href="https://www.linkedin.com/in/vahemovsisyan/" target="_blank" rel="noopener noreferrer" style={{ color:'var(--aqua)', textDecoration:'none', fontWeight:700 }}>Dr. Vahe Movsisyan</a>
          </motion.p>

          {/* Quote */}
          <motion.div variants={scaleIn} style={{
            maxWidth:800, margin:'0 auto',
            background:'var(--bg-card)',
            border:'1px solid var(--border-default)',
            borderLeft:'3px solid var(--aqua)',
            borderRadius:'var(--radius-lg)',
            padding:'36px 48px',
            backdropFilter:'blur(12px)',
            textAlign:'left', position:'relative', overflow:'hidden',
          }}>
            <span className="quote-open">"</span>
            <p style={{ fontSize:17, fontStyle:'italic', color:'var(--text-primary)', lineHeight:1.85, margin:'0 0 16px', fontFamily:'Georgia, serif' }}>
              "The probability of any event is the ratio between the value at which an
              expectation depending on the happening of the event ought to be computed,
              and the value of the thing expected upon its happening."
            </p>
            <div style={{ fontSize:12, color:'var(--aqua)', letterSpacing:'0.1em' }}>
              — Thomas Bayes, 1763 · <em style={{ color:'var(--text-secondary)' }}>An Essay Towards Solving a Problem in the Doctrine of Chances</em>
            </div>
            <span className="quote-close">"</span>
          </motion.div>

          {/* Divider */}
          <motion.div variants={fadeUp} style={{ width:'60%', height:1, background:'linear-gradient(90deg,transparent,var(--aqua),transparent)', margin:'44px auto 32px', opacity:0.3 }}/>

          {/* CTAs */}
          <motion.div variants={fadeUp} style={{ display:'flex', gap:14, justifyContent:'center', flexWrap:'wrap' }}>
            <motion.button
              className="btn-primary"
              whileHover={{ y: -3, boxShadow: 'var(--glow-md)' }}
              whileTap={{ scale: 0.96 }}
              transition={{ type: 'spring', stiffness: 400, damping: 28 }}
              onClick={() => document.getElementById('visualizations')?.scrollIntoView({behavior:'smooth'})}
            >
              View Results
            </motion.button>
            <motion.button
              className="btn-secondary"
              whileHover={{ y: -3, background: 'var(--bg-card-hover)' }}
              whileTap={{ scale: 0.96 }}
              transition={{ type: 'spring', stiffness: 400, damping: 28 }}
              onClick={() => document.getElementById('tasks')?.scrollIntoView({behavior:'smooth'})}
            >
              Explore Tasks →
            </motion.button>
            <motion.button
              className="btn-secondary"
              whileHover={{ y: -3, background: 'var(--bg-card-hover)', borderColor:'rgba(167,139,250,0.7)' }}
              whileTap={{ scale: 0.96 }}
              transition={{ type: 'spring', stiffness: 400, damping: 28 }}
              style={{ borderColor:'rgba(167,139,250,0.4)', color:'#A78BFA' }}
              onClick={() => document.getElementById('user-study')?.scrollIntoView({behavior:'smooth'})}
            >
              User Study ↗
            </motion.button>
          </motion.div>
        </motion.div>
      </div>
    </Section>
  )
}

// ─── RQ Integration callout content (rendered inside Research) ──
const RQ_INTEGRATION_LINES = [
  'RQ1 PRIMARY: external-judge validation — 20.74% combined keyword-judge disagreement, α = 0.57 on assumption (negative on reasoning, chance-level on method)',
  'RQ2–5 SUPPORTING: hardest categories, failure mode, robustness, calibration',
  'RQ4: 2,365 perturbation runs across 3 types (rephrase / numerical / semantic)',
]

// ═══════════════════════════════════════════════════════════════
//  2. PIPELINE
// ═══════════════════════════════════════════════════════════════
const NMACR_BARS = [
  { dim:'A', label:'Assumption',  weight:0.30, color:'#00FFE0' },
  { dim:'R', label:'Reasoning',   weight:0.25, color:'#A78BFA' },
  { dim:'M', label:'Method',      weight:0.20, color:'#00B4D8' },
  { dim:'C', label:'Calibration', weight:0.15, color:'#7FFFD4' },
  { dim:'N', label:'Numerical',   weight:0.10, color:'#FFB347' },
]

const TIER_BARS = [
  { tier:'T1 BASIC',        n: 9, pct: 5,  color:'#5EEAD4' },
  { tier:'T2 INTERMEDIATE', n:58, pct:34, color:'#22D3EE' },
  { tier:'T3 ADVANCED',     n:84, pct:49, color:'#3B82F6' },
  { tier:'T4 EXPERT',       n:20, pct:12, color:'#A855F7' },
]

const PERT_TYPES = [
  { name:'rephrase',  count:171, color:'#00FFE0', note:'Same problem, reworded' },
  { name:'numerical', count:131, color:'#FFB347', note:'Same structure, new numbers' },
  { name:'semantic',  count:171, color:'#A78BFA', note:'Same math, new domain' },
]

const FAILURE_MIX = [
  { model:'ChatGPT',  total:38, A:25, M:4,  F:6, C:3, color:'#7FFFD4' },
  { model:'Claude',   total:19, A:9,  M:10, F:0, C:0, color:'#00CED1' },
  { model:'DeepSeek', total:36, A:15, M:13, F:6, C:2, color:'#4A90D9' },
  { model:'Mistral',  total:26, A:8,  M:12, F:5, C:1, color:'#A78BFA' },
  { model:'Gemini',   total:24, A:10, M:9,  F:1, C:4, color:'#FF6B6B' },
]

function PipelineVisual({ kind }) {
  if (kind === 'nmacr-weights') {
    return (
      <div className="pipeline-visual nmacr-visual">
        <div className="pipeline-visual-title">Literature-derived dimension weights · sum = 1.0</div>
        {NMACR_BARS.map(b => (
          <div key={b.dim} className="nmacr-row">
            <span className="nmacr-tag" style={{ color:b.color }}>{b.dim} · {b.label}</span>
            <div className="nmacr-track">
              <div className="nmacr-fill" style={{ width:`${b.weight*100}%`, background:b.color }} />
            </div>
            <span className="nmacr-weight">{b.weight.toFixed(2)}</span>
          </div>
        ))}
      </div>
    )
  }
  if (kind === 'tier-mini') {
    return (
      <div className="pipeline-visual tier-visual">
        <div className="pipeline-visual-title">171 tasks across 4 difficulty tiers</div>
        <div className="tier-stack">
          {TIER_BARS.map(t => (
            <div key={t.tier} className="tier-seg" style={{ flexGrow:t.pct, background:t.color }}>
              <span className="tier-seg-label">{t.tier}</span>
              <span className="tier-seg-n">{t.n}</span>
            </div>
          ))}
        </div>
      </div>
    )
  }
  if (kind === 'pert-types') {
    return (
      <div className="pipeline-visual pert-visual">
        <div className="pipeline-visual-title">3 perturbation types · 473 total</div>
        <div className="pert-grid">
          {PERT_TYPES.map(p => (
            <div key={p.name} className="pert-chip" style={{ borderTopColor:p.color }}>
              <div className="pert-chip-head" style={{ color:p.color }}>{p.name}</div>
              <div className="pert-chip-count">{p.count}</div>
              <div className="pert-chip-note">{p.note}</div>
            </div>
          ))}
        </div>
      </div>
    )
  }
  if (kind === 'failure-mix') {
    return (
      <div className="pipeline-visual failure-visual">
        <div className="pipeline-visual-title">Per-model failure-mode mix · 143 total</div>
        {FAILURE_MIX.map(f => {
          const segs = [
            { k:'A', v:f.A, c:'#00FFE0', label:'Assumption' },
            { k:'M', v:f.M, c:'#FFB347', label:'Math' },
            { k:'F', v:f.F, c:'#A78BFA', label:'Format' },
            { k:'C', v:f.C, c:'#FF6B6B', label:'Conceptual' },
          ].filter(s => s.v > 0)
          return (
            <div key={f.model} className="failure-row">
              <span className="failure-model" style={{ color:f.color }}>{f.model}</span>
              <div className="failure-track">
                {segs.map(s => (
                  <div
                    key={s.k}
                    className="failure-seg"
                    style={{ width:`${(s.v/f.total)*100}%`, background:s.c }}
                    title={`${s.label}: ${s.v}`}
                  >
                    <span>{s.k} {s.v}</span>
                  </div>
                ))}
              </div>
              <span className="failure-total">{f.total}</span>
            </div>
          )
        })}
      </div>
    )
  }
  return null
}

function Pipeline() {
  const [expanded, setExpanded] = useState(null)

  const R_FRAC = 0.40
  const getPos = (i) => {
    const angle = (i / 6) * 2 * Math.PI - Math.PI / 2
    return {
      left: `${(0.5 + R_FRAC * Math.cos(angle)) * 100}%`,
      top:  `${(0.5 + R_FRAC * Math.sin(angle)) * 100}%`,
    }
  }

  return (
    <Section id="pipeline" minHeight="auto">
      <SectionTitle sub="Six-step pipeline from task generation to scoring — click any node to expand">Pipeline</SectionTitle>

      {/* Circular pipeline diagram */}
      <FadeIn>
        <div className="pipeline-circle" style={{ position:'relative', width:'100%', maxWidth:800, height:800, margin:'0 auto 8px' }}>

          {/* Outer rotating ring */}
          <div style={{ position:'absolute', left:'50%', top:'50%', width:'78%', height:'78%',
            animation:'ringRotate 32s linear infinite', borderRadius:'50%',
            border:'1px dashed rgba(0,255,224,0.18)', transform:'translate(-50%,-50%)' }}>
            <div style={{ position:'absolute', top:'-4px', left:'50%', transform:'translateX(-50%)', width:7, height:7, borderRadius:'50%', background:'rgba(0,255,224,0.7)', boxShadow:'0 0 8px rgba(0,255,224,0.6)' }}/>
            <div style={{ position:'absolute', bottom:'-4px', left:'50%', transform:'translateX(-50%)', width:5, height:5, borderRadius:'50%', background:'rgba(0,255,224,0.4)', boxShadow:'0 0 6px rgba(0,255,224,0.4)' }}/>
            <div style={{ position:'absolute', top:'50%', right:'-4px', transform:'translateY(-50%)', width:5, height:5, borderRadius:'50%', background:'rgba(0,180,216,0.5)', boxShadow:'0 0 6px rgba(0,180,216,0.5)' }}/>
            <div style={{ position:'absolute', top:'50%', left:'-4px', transform:'translateY(-50%)', width:4, height:4, borderRadius:'50%', background:'rgba(167,139,250,0.5)', boxShadow:'0 0 5px rgba(167,139,250,0.5)' }}/>
          </div>

          {/* Inner counter-rotating ring */}
          <div style={{ position:'absolute', left:'50%', top:'50%', width:'58%', height:'58%',
            animation:'ringCCW 20s linear infinite', borderRadius:'50%',
            border:'1px dashed rgba(0,180,216,0.18)', transform:'translate(-50%,-50%)' }}>
            <div style={{ position:'absolute', top:'-4px', left:'50%', transform:'translateX(-50%)', width:6, height:6, borderRadius:'50%', background:'rgba(0,180,216,0.5)', boxShadow:'0 0 7px rgba(0,180,216,0.5)' }}/>
            <div style={{ position:'absolute', bottom:'-4px', left:'50%', transform:'translateX(-50%)', width:4, height:4, borderRadius:'50%', background:'rgba(0,180,216,0.3)', boxShadow:'0 0 5px rgba(0,180,216,0.4)' }}/>
            <div style={{ position:'absolute', top:'50%', right:'-4px', transform:'translateY(-50%)', width:4, height:4, borderRadius:'50%', background:'rgba(0,255,224,0.4)', boxShadow:'0 0 5px rgba(0,255,224,0.4)' }}/>
          </div>

          {/* Electron orbit paths */}
          <div style={{ position:'absolute', left:'50%', top:'50%', width:'38%', height:'38%',
            animation:'ringRotate 28s linear infinite', borderRadius:'50%',
            border:'1.5px dashed rgba(0,255,224,0.22)', transform:'translate(-50%,-50%)' }}>
            <div style={{ position:'absolute', top:'-5px', left:'50%', transform:'translateX(-50%)',
              width:9, height:9, borderRadius:'50%', background:'#00FFE0',
              boxShadow:'0 0 12px rgba(0,255,224,0.9)' }}/>
            <div style={{ position:'absolute', bottom:'-4px', left:'50%', transform:'translateX(-50%)',
              width:6, height:6, borderRadius:'50%', background:'rgba(0,255,224,0.6)',
              boxShadow:'0 0 8px rgba(0,255,224,0.6)' }}/>
            <div style={{ position:'absolute', top:'50%', right:'-4px', transform:'translateY(-50%)',
              width:5, height:5, borderRadius:'50%', background:'rgba(0,255,224,0.45)',
              boxShadow:'0 0 6px rgba(0,255,224,0.5)' }}/>
          </div>
          <div style={{ position:'absolute', left:'50%', top:'50%', width:'48%', height:'28%',
            animation:'ringCCW 18s linear infinite', borderRadius:'50%',
            border:'1px dashed rgba(167,139,250,0.25)', transform:'translate(-50%,-50%)' }}>
            <div style={{ position:'absolute', top:'-4px', left:'50%', transform:'translateX(-50%)',
              width:8, height:8, borderRadius:'50%', background:'#A78BFA',
              boxShadow:'0 0 10px rgba(167,139,250,0.9)' }}/>
            <div style={{ position:'absolute', bottom:'-4px', left:'50%', transform:'translateX(-50%)',
              width:5, height:5, borderRadius:'50%', background:'rgba(167,139,250,0.55)',
              boxShadow:'0 0 7px rgba(167,139,250,0.6)' }}/>
            <div style={{ position:'absolute', top:'50%', left:'-4px', transform:'translateY(-50%)',
              width:4, height:4, borderRadius:'50%', background:'rgba(167,139,250,0.4)',
              boxShadow:'0 0 5px rgba(167,139,250,0.5)' }}/>
          </div>
          <div style={{ position:'absolute', left:'50%', top:'50%', width:'28%', height:'48%',
            animation:'ringRotate 22s linear infinite', borderRadius:'50%',
            border:'1px dashed rgba(0,180,216,0.22)', transform:'translate(-50%,-50%)' }}>
            <div style={{ position:'absolute', top:'-4px', left:'50%', transform:'translateX(-50%)',
              width:8, height:8, borderRadius:'50%', background:'#00B4D8',
              boxShadow:'0 0 10px rgba(0,180,216,0.9)' }}/>
            <div style={{ position:'absolute', bottom:'-4px', left:'50%', transform:'translateX(-50%)',
              width:5, height:5, borderRadius:'50%', background:'rgba(0,180,216,0.55)',
              boxShadow:'0 0 7px rgba(0,180,216,0.6)' }}/>
            <div style={{ position:'absolute', top:'50%', right:'-4px', transform:'translateY(-50%)',
              width:4, height:4, borderRadius:'50%', background:'rgba(0,180,216,0.4)',
              boxShadow:'0 0 5px rgba(0,180,216,0.5)' }}/>
          </div>

          {/* SVG connector lines */}
          <svg style={{ position:'absolute', inset:0, width:'100%', height:'100%', pointerEvents:'none' }}>
            {PIPELINE.map((_,i) => {
              const angle = (i / 6) * 2 * Math.PI - Math.PI / 2
              return (
                <line key={i}
                  x1="50%" y1="50%"
                  x2={`${(0.5 + R_FRAC * Math.cos(angle)) * 100}%`}
                  y2={`${(0.5 + R_FRAC * Math.sin(angle)) * 100}%`}
                  stroke={expanded===i ? 'rgba(0,255,224,0.38)' : 'rgba(0,255,224,0.09)'}
                  strokeWidth={expanded===i ? 1.5 : 1}
                  strokeDasharray="5 5"
                />
              )
            })}
          </svg>

          {/* Center hub */}
          <motion.div
            style={{ position:'absolute', left:'50%', top:'50%', width:145, height:145,
              transform:'translate(-50%,-50%)', borderRadius:'50%',
              background:'rgba(0,255,224,0.05)', border:'2px solid rgba(0,255,224,0.45)',
              display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center',
              boxShadow:'0 0 40px rgba(0,255,224,0.14)', zIndex:2 }}
            animate={{ boxShadow:['0 0 28px rgba(0,255,224,0.10)','0 0 56px rgba(0,255,224,0.24)','0 0 28px rgba(0,255,224,0.10)'] }}
            transition={{ duration:3, repeat:Infinity, ease:'easeInOut' }}
          >
            <div style={{ color:'var(--aqua)', fontWeight:800, fontSize:16, fontFamily:'var(--font-mono)', letterSpacing:'0.04em', textAlign:'center' }}>Benchmarking</div>
          </motion.div>

          {/* Pipeline step nodes — outer div handles position, inner motion.div handles scale */}
          {PIPELINE.map((s,i) => {
            const pos = getPos(i)
            const isActive = expanded === i
            return (
              <div key={i} style={{ position:'absolute', ...pos, transform:'translate(-50%,-50%)', width:132 }}>
                <motion.div
                  style={{
                    background: isActive ? 'rgba(0,255,224,0.08)' : 'rgba(255,255,255,0.03)',
                    border:`1px solid ${isActive ? 'rgba(0,255,224,0.55)' : 'rgba(0,255,224,0.15)'}`,
                    borderRadius:12, padding:'12px 10px 10px', cursor:'pointer', textAlign:'center',
                    boxShadow: isActive ? '0 0 18px rgba(0,255,224,0.15)' : 'none',
                    transition:'background 0.2s, border-color 0.2s, box-shadow 0.2s',
                  }}
                  onClick={() => setExpanded(isActive ? null : i)}
                  whileHover={{ scale:1.07 }}
                  whileTap={{ scale:0.97 }}
                  transition={{ type:'spring', stiffness:420, damping:26 }}
                >
                  <div style={{ color:isActive ? 'var(--aqua)' : 'rgba(0,255,224,0.7)', marginBottom:5, display:'flex', justifyContent:'center' }}>{PIPELINE_ICONS[i]}</div>
                  <div style={{ color: isActive ? 'var(--aqua)' : 'rgba(255,255,255,0.85)', fontSize:9, fontWeight:700, marginBottom:3, letterSpacing:'0.05em', lineHeight:1.3 }}>{s.label}</div>
                  <div style={{ color:'rgba(255,255,255,0.5)', fontSize:8, fontWeight:600, lineHeight:1.3 }}>{s.stat}</div>
                  <div style={{ color:'rgba(0,255,224,0.4)', fontSize:7, marginTop:5 }}>{isActive ? '▲ close' : '▼ expand'}</div>
                </motion.div>
              </div>
            )
          })}

        </div>

        {/* Expanded detail */}
        <AnimatePresence mode="wait">
          {expanded !== null && (
            <motion.div
              key={expanded}
              initial={{ opacity:0, y:-8, height:0 }}
              animate={{ opacity:1, y:0, height:'auto' }}
              exit={{ opacity:0, y:-8, height:0 }}
              transition={{ duration:0.28, ease:[0.22,1,0.36,1] }}
              style={{ overflow:'hidden', maxWidth:720, margin:'0 auto 16px' }}
            >
              <Card glow style={{ padding:'22px 28px' }}>
                <div style={{ display:'flex', flexDirection:'column', alignItems:'center', textAlign:'center' }}>
                  <div style={{ marginBottom:8, color:'var(--aqua)', display:'flex', justifyContent:'center' }}>{PIPELINE_ICONS[expanded]}</div>
                  <div style={{ color:'var(--aqua)', fontWeight:700, fontSize:10, letterSpacing:'0.1em', marginBottom:4 }}>
                    STEP {expanded+1} — {PIPELINE[expanded].label.toUpperCase()}
                  </div>
                  <div style={{ color:'var(--text-primary)', fontWeight:700, fontSize:15, marginBottom:14 }}>
                    {PIPELINE[expanded].title}
                  </div>
                </div>
                {PIPELINE[expanded].visual && (
                  <PipelineVisual kind={PIPELINE[expanded].visual} />
                )}
                {PIPELINE[expanded].bullets ? (
                  <ul className="pipeline-bullets">
                    {PIPELINE[expanded].bullets.map((b, idx) => (
                      <li key={idx}>{b}</li>
                    ))}
                  </ul>
                ) : (
                  <p style={{ color:'var(--text-secondary)', fontSize:12.5, lineHeight:1.75, margin:0, textAlign:'center' }}>
                    {PIPELINE[expanded].desc}
                  </p>
                )}
              </Card>
            </motion.div>
          )}
        </AnimatePresence>
      </FadeIn>

    </Section>
  )
}

// ═══════════════════════════════════════════════════════════════
//  DIFFICULTY LADDER (relocated under Models · enhanced content)
// ═══════════════════════════════════════════════════════════════
const TIER_DETAIL = {
  1: {
    label: 'BASIC',
    color: '#5EEAD4',
    tasks: 9,
    pct: 5,
    description: 'Direct application of Bayes theorem. No multi-step reasoning required. Tests foundational probability mechanics.',
    skills: 'Conjugate updating · Direct posterior derivation · Closed-form algebra',
    example: 'Beta-Binomial posterior given Bernoulli successes (k=3, n=10).',
    challenges: ['Single conjugate update', 'Direct Bayes theorem application', 'Closed-form posterior'],
    types: ['BETA_BINOM', 'GAMMA_POISSON', 'BINOM_FLAT', 'NORMAL_GAMMA', 'DIRICHLET'],
  },
  2: {
    label: 'INTERMEDIATE',
    color: '#22D3EE',
    tasks: 58,
    pct: 34,
    description: 'Multi-step inference combining priors, likelihoods, and posterior summaries. Requires recognition of distribution families and parameterization choices.',
    skills: 'Distribution-family recognition · Hierarchical priors · Posterior summarization',
    example: 'Frequentist CI vs Bayesian credible interval under conjugate Normal prior (n=20).',
    challenges: ['Chained multi-step inference', 'MCMC sampling basics (Gibbs/MH/VB)', 'HPD region & credible-interval derivation'],
    types: ['DISC_MEDIAN', 'UNIFORM_MLE', 'BAYES_RISK', 'BOX_MULLER', 'HPD', 'JEFFREYS', 'MLE_MAP', 'CI_CREDIBLE', 'CONCEPTUAL', 'GIBBS', 'MH', 'VB'],
  },
  3: {
    label: 'ADVANCED',
    color: '#3B82F6',
    tasks: 84,
    pct: 49,
    description: 'Sampling-based inference, hierarchical models, and non-conjugate posteriors. Largest tier — represents the most realistic Bayesian workflow.',
    skills: 'MCMC reasoning · Non-conjugate inference · Convergence diagnostics',
    example: 'Bayes-factor model comparison Beta(1,1) vs Beta(0.5,0.5) given x=3, n=10.',
    challenges: ['Computational Bayes (HMC / RJMCMC / ABC)', 'Bayes factor & marginal-likelihood reasoning', 'Hierarchical-model posterior simulation'],
    types: ['MINIMAX', 'BIAS_VAR', 'FISHER_INFO', 'RC_BOUND', 'MARKOV', 'ORDER_STAT', 'REGRESSION', 'BAYES_FACTOR', 'PPC', 'BAYES_REG', 'LOG_ML', 'HMC', 'RJMCMC', 'ABC', 'HIERARCHICAL'],
  },
  4: {
    label: 'EXPERT',
    color: '#A855F7',
    tasks: 20,
    pct: 12,
    description: 'Decision-theoretic reasoning, model comparison, and expert-level Bayesian workflow. Tests integration of multiple skills under realistic uncertainty.',
    skills: 'Bayesian decision theory · Model comparison · Expected utility maximization',
    example: 'MSE comparison across competing estimators under Uniform(0, θ), n=5.',
    challenges: ['Competing-estimator MSE optimization', 'Asymptotic efficiency under MLE', 'Advanced MCMC at scale'],
    types: ['OPT_SCALED', 'MSE_COMPARE', 'MLE_EFFICIENCY', 'GIBBS', 'MH', 'HMC', 'RJMCMC', 'VB', 'ABC', 'HIERARCHICAL'],
  },
}

function DifficultyPie() {
  const data = [1,2,3,4].map(t => ({
    name: `T${t} ${TIER_DETAIL[t].label}`,
    value: TIER_DETAIL[t].tasks,
    pct: TIER_DETAIL[t].pct,
    color: TIER_DETAIL[t].color,
  }))
  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          innerRadius={62}
          outerRadius={108}
          paddingAngle={1.5}
          stroke="rgba(0,0,0,0.5)"
          label={({ name, pct }) => `${name} · ${pct}%`}
          labelLine={{ stroke: 'rgba(255,255,255,0.4)' }}
        >
          {data.map((d, i) => <Cell key={i} fill={d.color}/>)}
        </Pie>
        <RTooltip
          formatter={(v, name) => [`${v} tasks`, name]}
          contentStyle={{ background:'rgba(0,0,0,0.9)', border:'1px solid rgba(255,255,255,0.15)', borderRadius:8, fontSize:12 }}
        />
        <Legend verticalAlign="bottom" iconType="circle" wrapperStyle={{ fontSize:11, paddingTop:8 }}/>
      </PieChart>
    </ResponsiveContainer>
  )
}

function DifficultyLadder() {
  return (
    <Section id="difficulty" minHeight="auto">
      <SectionTitle sub="171 tasks across 4 difficulty tiers — from conjugate updates to decision theory">Difficulty Ladder</SectionTitle>
      <FadeIn>
        <div style={{ maxWidth:1200, margin:'0 auto' }}>
          <Card style={{ marginBottom:20 }}>
            <div style={{ color:'var(--aqua)', fontSize:10, fontWeight:700, letterSpacing:'0.12em', marginBottom:8, textAlign:'center' }}>
              TIER DISTRIBUTION
            </div>
            <DifficultyPie/>
          </Card>
          <div className="difficulty-cards-grid">
            {[1,2,3,4].map(tier => {
              const d = TIER_DETAIL[tier]
              return (
                <div key={tier} style={{
                  background: `linear-gradient(135deg, ${d.color}14, transparent)`,
                  border: `1px solid ${d.color}55`,
                  borderTop: `3px solid ${d.color}`,
                  borderRadius: 12,
                  padding: '16px 16px 14px',
                  display: 'flex', flexDirection: 'column', gap: 10,
                }}>
                  {/* header: T-badge + name + count */}
                  <div style={{ display:'flex', alignItems:'center', gap:10 }}>
                    <div style={{
                      width:36, height:36, borderRadius:8,
                      background:`${d.color}22`, border:`1.5px solid ${d.color}`,
                      display:'flex', alignItems:'center', justifyContent:'center',
                      color:d.color, fontWeight:800, fontSize:12, fontFamily:'var(--font-mono)',
                    }}>T{tier}</div>
                    <div style={{ flex:1, minWidth:0 }}>
                      <div style={{ color:d.color, fontWeight:700, fontSize:11, letterSpacing:'0.1em' }}>{d.label}</div>
                      <div style={{ color:'var(--text-muted)', fontSize:10, fontFamily:'var(--font-mono)' }}>
                        {d.tasks} tasks · {d.pct}%
                      </div>
                    </div>
                  </div>
                  {/* difficulty dots */}
                  <div style={{ display:'flex', gap:5 }}>
                    {[1,2,3,4].map(i => (
                      <div key={i} style={{
                        flex:1, height:4, borderRadius:2,
                        background: i<=tier ? d.color : `${d.color}22`,
                        boxShadow: i<=tier ? `0 0 6px ${d.color}66` : 'none',
                      }}/>
                    ))}
                  </div>
                  {/* description */}
                  <div style={{ color:'rgba(232,244,248,0.78)', fontSize:12, lineHeight:1.6 }}>
                    {d.description}
                  </div>
                  {/* reasoning skills */}
                  <div>
                    <div style={{ color:`${d.color}cc`, fontSize:9, fontWeight:700, letterSpacing:'0.14em', marginBottom:4 }}>REASONING SKILLS</div>
                    <div style={{ color:'rgba(232,244,248,0.7)', fontSize:11.5, lineHeight:1.55 }}>{d.skills}</div>
                  </div>
                  {/* example */}
                  <div>
                    <div style={{ color:`${d.color}cc`, fontSize:9, fontWeight:700, letterSpacing:'0.14em', marginBottom:4 }}>EXAMPLE</div>
                    <div style={{ color:'rgba(232,244,248,0.7)', fontSize:11.5, lineHeight:1.55, fontStyle:'italic' }}>{d.example}</div>
                  </div>
                  {/* key challenges */}
                  <div>
                    <div style={{ color:`${d.color}cc`, fontSize:9, fontWeight:700, letterSpacing:'0.14em', marginBottom:6 }}>KEY CHALLENGES</div>
                    <ul style={{ margin:0, padding:0, listStyle:'none', display:'flex', flexDirection:'column', gap:3 }}>
                      {d.challenges.map(c => (
                        <li key={c} style={{ display:'flex', alignItems:'flex-start', gap:6 }}>
                          <span style={{ color:d.color, fontSize:7, marginTop:6, flexShrink:0 }}>◆</span>
                          <span style={{ color:'rgba(232,244,248,0.7)', fontSize:11.5, lineHeight:1.5 }}>{c}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  {/* task types badges */}
                  <div style={{ marginTop:'auto' }}>
                    <div style={{ color:`${d.color}cc`, fontSize:9, fontWeight:700, letterSpacing:'0.14em', marginBottom:6 }}>TASK TYPES</div>
                    <div style={{ display:'flex', flexWrap:'wrap', gap:4 }}>
                      {d.types.map(k => (
                        <span key={k} style={{
                          fontSize:9.5, padding:'3px 7px', borderRadius:4,
                          background:`${d.color}18`, color:d.color,
                          border:`1px solid ${d.color}33`, fontFamily:'var(--font-mono)',
                          letterSpacing:'0.02em',
                        }}>{k}</span>
                      ))}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </FadeIn>
    </Section>
  )
}

// ═══════════════════════════════════════════════════════════════
//  3. MODELS
// ═══════════════════════════════════════════════════════════════
function Models() {
  const [sel, setSel] = useState(null)
  const radarSource = useContext(RadarSourceContext)

  const selModel = sel !== null ? MODELS[sel] : null

  return (
    <Section id="models" minHeight="auto">
      <SectionTitle sub="Five state-of-the-art language models evaluated on Bayesian reasoning">Models Under Evaluation</SectionTitle>

      <FadeIn>
        <NeuralNetwork
          onSelect={(idx) => setSel(idx)}
          selected={sel}
        />
      </FadeIn>

      {/* Expanded panel */}
      <AnimatePresence mode="wait">
        {selModel && (
          <motion.div
            key={selModel.id}
            initial={{ opacity: 0, y: -16, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -16, scale: 0.97 }}
            transition={{ type: 'spring', stiffness: 350, damping: 28 }}
            style={{ maxWidth:700, margin:'24px auto 0' }}
          >
            <Card glow style={{ padding:'24px 28px' }}>
              <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', marginBottom:16 }}>
                <div style={{ display:'flex', alignItems:'center', gap:14 }}>
                  <div style={{ width:52, height:52, borderRadius:12, background:`${selModel.color}18`, border:`2px solid ${selModel.color}`, display:'flex', alignItems:'center', justifyContent:'center', color:selModel.color, fontWeight:800, fontSize:17 }}>{selModel.initials}</div>
                  <div>
                    <div style={{ color:'var(--text-primary)', fontWeight:800, fontSize:18 }}>{selModel.name}</div>
                    <div style={{ color:'var(--text-secondary)', fontSize:12 }}>{selModel.provider} · {selModel.lab}</div>
                  </div>
                </div>
                <motion.button
                  onClick={() => setSel(null)}
                  whileHover={{ background: 'var(--bg-card-hover)' }}
                  whileTap={{ scale: 0.9 }}
                  style={{ background:'none', border:'1px solid var(--border-default)', borderRadius:6, color:'var(--text-secondary)', fontSize:13, cursor:'pointer', padding:'3px 10px' }}
                >✕</motion.button>
              </div>

              <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:12, marginBottom:16 }}>
                <div style={{ display:'grid', gridTemplateColumns:'1fr', gap:8 }}>
                  {[['VERSION', selModel.version],['API', selModel.api],['TOKEN LIMIT (BENCHMARK)', (selModel.maxTokens || 1024).toLocaleString()],['AVG OUTPUT TOKENS', selModel.avgOutputTokens ? selModel.avgOutputTokens.toLocaleString() : '—']].map(([k,v]) => (
                    <div key={k} style={{ background:'rgba(0,0,0,0.22)', borderRadius:8, padding:'10px 12px' }}>
                      <div style={{ color:'var(--aqua)', fontSize:9, fontWeight:700, letterSpacing:'0.1em', marginBottom:4 }}>{k}</div>
                      <div style={{ color:'var(--text-primary)', fontSize:11, fontFamily:'var(--font-mono)', wordBreak:'break-all' }}>{v}</div>
                    </div>
                  ))}
                  <div style={{ background:'rgba(0,0,0,0.22)', borderRadius:8, padding:'12px 14px' }}>
                    <div style={{ color:'var(--aqua)', fontSize:9, fontWeight:700, letterSpacing:'0.1em', marginBottom:6 }}>STRENGTHS</div>
                    <p style={{ color:'var(--text-primary)', fontSize:12, lineHeight:1.7, margin:0 }}>{selModel.strengths}</p>
                  </div>
                </div>
                <div style={{ background:'rgba(0,0,0,0.22)', borderRadius:8, padding:'12px', display:'flex', flexDirection:'column', alignItems:'center' }}>
                  <div style={{ color:'var(--aqua)', fontSize:9, fontWeight:700, letterSpacing:'0.1em', marginBottom:4, textAlign:'center' }}>CAPABILITY RADAR</div>
                  <div style={{ fontSize:9, color:'var(--text-muted)', marginBottom:4, textAlign:'center' }}>{radarSource === 'live' ? 'Live data — updated each deploy' : 'Last-deploy snapshot'}</div>
                  <RadarChart model={selModel}/>
                </div>
              </div>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </Section>
  )
}

// ═══════════════════════════════════════════════════════════════
//  4. TASKS
// ═══════════════════════════════════════════════════════════════
function Tasks({ onOpenModal, isOpen, onToggle }) {
  const [tiers,       setTiers]       = useState([])
  const [category,    setCategory]    = useState('all')
  const [idInput,     setIdInput]     = useState('')
  const [topicInput,  setTopicInput]  = useState('')
  const [searchId,    setSearchId]    = useState('')
  const [searchTopic, setSearchTopic] = useState('')
  const [copied,      setCopied]      = useState(null)
  const [perPage,     setPerPage]     = useState(16)
  const [currentPage, setCurrentPage] = useState(1)
  const [viewMode,    setViewMode]    = useState('grid')

  const PER_PAGE_OPTIONS = [16, 32, 64, 171]

  const filtered = useMemo(() => tasksData.filter(t => {
    if (tiers.length && !tiers.includes(t.tier)) return false
    if (category==='conceptual' && t.category!=='conceptual') return false
    if (category==='numeric'    && t.category==='conceptual') return false
    if (searchId    && !t.task_id.toUpperCase().includes(searchId.toUpperCase()))   return false
    if (searchTopic) {
      const hay = (t.task_id+' '+t.description+' '+(t.notes_topic||'')).toLowerCase()
      if (!hay.includes(searchTopic.toLowerCase())) return false
    }
    return true
  }), [tiers, category, searchId, searchTopic])

  const filterKey = `${tiers.join('-')}-${category}-${searchId}-${searchTopic}`

  useEffect(() => { setCurrentPage(1) }, [filterKey])

  const totalPages     = Math.max(1, Math.ceil(filtered.length / perPage))
  const paginatedTasks = viewMode === 'grouped'
    ? filtered
    : filtered.slice((currentPage - 1) * perPage, currentPage * perPage)
  const groupedTasks   = viewMode === 'grouped'
    ? filtered.reduce((acc, task) => {
        const key = task.task_type
        if (!acc[key]) acc[key] = []
        acc[key].push(task)
        return acc
      }, {})
    : null

  const toggleTier = t => setTiers(p => p.includes(t) ? p.filter(x=>x!==t) : [...p,t])
  const clearAll   = () => { setTiers([]); setCategory('all'); setIdInput(''); setTopicInput(''); setSearchId(''); setSearchTopic('')}
  const copyId     = (id, e) => {
    e.stopPropagation()
    navigator.clipboard.writeText(id).catch(()=>{})
    setCopied(id)
    setTimeout(()=>setCopied(null), 1500)
  }

  return (
    <Section id="tasks" minHeight={isOpen ? '100vh' : 'auto'}>
      {/* Collapsible header */}
      <div style={{ display:'flex', alignItems:'center', justifyContent:'center', gap:16, marginBottom: isOpen ? 40 : 0 }}>
        <div style={{ textAlign:'center' }}>
          <h2 style={{ fontSize:'clamp(32px,4vw,48px)', fontWeight:700, color:'var(--text-primary)', margin:0, lineHeight:1.2 }}>
            Benchmark Tasks
          </h2>
          <motion.div
            initial={{ scaleX:0 }}
            whileInView={{ scaleX:1 }}
            viewport={{ once:true }}
            transition={{ duration:0.7, delay:0.25 }}
            style={{ width:64, height:3, background:'linear-gradient(90deg,var(--aqua),var(--blue))', margin:'12px auto 0', borderRadius:2, transformOrigin:'left' }}
          />
        </div>
        <motion.button
          onClick={onToggle}
          whileHover={{ scale:1.05 }}
          whileTap={{ scale:0.95 }}
          style={{
            marginTop:4,
            padding:'8px 20px', borderRadius:8,
            border:`1.5px solid rgba(0,255,224,${isOpen?'0.6':'0.35'})`,
            background: isOpen ? 'rgba(0,255,224,0.10)' : 'rgba(0,255,224,0.05)',
            color: isOpen ? '#00FFE0' : 'rgba(0,255,224,0.7)',
            fontSize:12, fontWeight:700, cursor:'pointer',
            fontFamily:'var(--font-mono)', letterSpacing:'0.05em',
            transition:'all 0.18s',
          }}
        >
          {isOpen ? '▼ COLLAPSE' : '▶ EXPAND (171 TASKS)'}
        </motion.button>
      </div>

      <AnimatePresence>
      {isOpen && (
      <motion.div
        initial={{ height:0, opacity:0 }}
        animate={{ height:'auto', opacity:1 }}
        exit={{ height:0, opacity:0 }}
        transition={{ duration:0.35, ease:[0.22,1,0.36,1] }}
        style={{ overflow:'hidden' }}
      >
      <div style={{ display:'grid', gridTemplateColumns:'250px 1fr', gap:24, alignItems:'start' }}>

        {/* Filter sidebar */}
        <div style={{ alignSelf:'start', marginTop:0 }}>
          <Card>
            <div style={{ textAlign:'center', paddingBottom:16, borderBottom:'1px solid var(--border-default)', marginBottom:16 }}>
              <motion.span
                key={filtered.length}
                initial={{ opacity: 0, scale: 0.7 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ type: 'spring', stiffness: 400, damping: 24 }}
                style={{ fontSize:28, fontWeight:700, color:'var(--aqua)', fontFamily:'var(--font-mono)', display:'inline-block' }}
              >
                {filtered.length}
              </motion.span>
              <span style={{ fontSize:13, color:'var(--text-secondary)' }}> tasks</span><br/>
              <span style={{ fontSize:11, color:'var(--text-muted)' }}>
                {filtered.length !== tasksData.length ? `filtered from ${tasksData.length} total` : 'total tasks'}
              </span>
              {totalPages > 1 && viewMode === 'grid' && (
                <div style={{ fontSize:11, color:'rgba(0,255,224,0.5)', marginTop:4 }}>
                  Page {currentPage} of {totalPages}
                </div>
              )}
            </div>

            <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:20 }}>
              <div className="filter-dot"/>
              <div style={{ color:'var(--aqua)', fontSize:10, fontWeight:700, letterSpacing:'0.14em' }}>FILTERS</div>
            </div>

            <div style={{ marginBottom:20 }}>
              <div style={{ color:'var(--text-secondary)', fontSize:10, fontWeight:700, letterSpacing:'0.1em', marginBottom:10 }}>TIER</div>
              {[1,2,3,4].map(t => (
                <motion.label
                  key={t}
                  style={{ display:'flex', alignItems:'center', gap:10, marginBottom:8, cursor:'pointer' }}
                  onClick={() => toggleTier(t)}
                  whileTap={{ scale: 0.97 }}
                >
                  <div style={{ width:17, height:17, borderRadius:4, border:`2px solid ${TIER_COLORS[t]}`,
                    background:tiers.includes(t)?TIER_COLORS[t]:'transparent',
                    boxShadow:tiers.includes(t)?`0 0 7px ${TIER_COLORS[t]}`:'none',
                    transition:'all 0.18s', flexShrink:0 }}/>
                  <span style={{ color:'var(--text-secondary)', fontSize:12 }}>
                    Tier {t} — {TIER_LABELS[t]}
                    <span style={{ color:TIER_COLORS[t], marginLeft:6 }}>({statsData.tier_counts[String(t)]||0})</span>
                  </span>
                </motion.label>
              ))}
            </div>

            <div style={{ marginBottom:20 }}>
              <div style={{ color:'var(--text-secondary)', fontSize:10, fontWeight:700, letterSpacing:'0.1em', marginBottom:10 }}>CATEGORY</div>
              <div style={{ display:'flex', gap:6 }}>
                {[
                  { key:'all',         label:'All' },
                  { key:'numeric',     label:'Numeric' },
                  { key:'conceptual',  label:'Concept' },
                ].map(({ key: cat, label }) => (
                  <motion.button
                    key={cat}
                    onClick={() => setCategory(cat)}
                    whileTap={{ scale: 0.95 }}
                    style={{ flex:1, padding:'6px 4px', borderRadius:6, fontSize:10, fontWeight:700, cursor:'pointer',
                      border:`1px solid ${category===cat ? 'var(--aqua)' : 'var(--border-default)'}`,
                      background:category===cat?'var(--bg-card-hover)':'transparent',
                      color:category===cat ? 'var(--aqua)' : 'var(--text-secondary)',
                      transition:'all 0.18s' }}
                  >
                    {label}
                  </motion.button>
                ))}
              </div>
            </div>

            <div style={{ marginBottom:20 }}>
              <div style={{ fontSize:11, fontWeight:700, color:'rgba(255,255,255,0.5)', letterSpacing:'0.1em', marginBottom:10 }}>SHOW PER PAGE</div>
              <div style={{ display:'flex', gap:6, flexWrap:'wrap' }}>
                {PER_PAGE_OPTIONS.map(n => (
                  <button
                    key={n}
                    data-hover="true"
                    onClick={() => { setPerPage(n); setCurrentPage(1) }}
                    style={{ padding:'5px 12px', borderRadius:6, border: perPage === n ? '1px solid rgba(0,255,224,0.8)' : '1px solid rgba(255,255,255,0.12)', background: perPage === n ? 'rgba(0,255,224,0.12)' : 'transparent', color: perPage === n ? '#00FFE0' : 'rgba(255,255,255,0.45)', fontSize:12, fontWeight: perPage === n ? 700 : 400, cursor:'none', transition:'all 0.15s ease' }}
                  >
                    {n === 171 ? 'All' : n}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ marginBottom:20 }}>
              <div style={{ fontSize:11, fontWeight:700, color:'rgba(255,255,255,0.5)', letterSpacing:'0.1em', marginBottom:10 }}>VIEW MODE</div>
              <div style={{ display:'flex', gap:6 }}>
                {['Grid', 'Grouped'].map(mode => (
                  <button
                    key={mode}
                    data-hover="true"
                    onClick={() => setViewMode(mode.toLowerCase())}
                    style={{ flex:1, padding:'7px 0', borderRadius:6, border: viewMode === mode.toLowerCase() ? '1px solid rgba(0,255,224,0.8)' : '1px solid rgba(255,255,255,0.12)', background: viewMode === mode.toLowerCase() ? 'rgba(0,255,224,0.12)' : 'transparent', color: viewMode === mode.toLowerCase() ? '#00FFE0' : 'rgba(255,255,255,0.45)', fontSize:12, fontWeight:600, cursor:'none' }}
                  >
                    {mode === 'Grid' ? '⊞ Grid' : '≡ Grouped'}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ marginBottom:14 }}>
              <div style={{ color:'var(--text-secondary)', fontSize:10, fontWeight:700, letterSpacing:'0.1em', marginBottom:8 }}>SEARCH BY TASK ID</div>
              <div style={{ display:'flex' }}>
                <input value={idInput} onChange={e=>setIdInput(e.target.value)}
                  onKeyDown={e=>e.key==='Enter'&&setSearchId(idInput)}
                  placeholder="e.g. BETA_BINOM_01"
                  style={{ flex:1, minWidth:0, background:'rgba(0,0,0,0.3)', border:'1px solid var(--border-default)', borderRight:'none', borderRadius:'6px 0 0 6px', padding:'7px 10px', color:'var(--aqua)', fontSize:11, fontFamily:'var(--font-mono)', outline:'none' }}/>
                <motion.button
                  onClick={()=>setSearchId(idInput)}
                  whileHover={{ background: '#00E0C7' }}
                  whileTap={{ scale: 0.9 }}
                  style={{ width:44, flexShrink:0, background:'var(--aqua)', border:'none', borderRadius:'0 6px 6px 0', color:'#070B14', cursor:'pointer', fontWeight:700, fontSize:14 }}
                >→</motion.button>
              </div>
            </div>

            <div style={{ marginBottom:20 }}>
              <div style={{ color:'var(--text-secondary)', fontSize:10, fontWeight:700, letterSpacing:'0.1em', marginBottom:8 }}>SEARCH BY TOPIC</div>
              <div style={{ display:'flex' }}>
                <input value={topicInput} onChange={e=>setTopicInput(e.target.value)}
                  onKeyDown={e=>e.key==='Enter'&&setSearchTopic(topicInput)}
                  placeholder="e.g. posterior median"
                  style={{ flex:1, minWidth:0, background:'rgba(0,0,0,0.3)', border:'1px solid var(--border-default)', borderRight:'none', borderRadius:'6px 0 0 6px', padding:'7px 10px', color:'var(--text-primary)', fontSize:11, outline:'none' }}/>
                <motion.button
                  onClick={()=>setSearchTopic(topicInput)}
                  whileHover={{ background: '#00E0C7' }}
                  whileTap={{ scale: 0.9 }}
                  style={{ width:44, flexShrink:0, background:'var(--aqua)', border:'none', borderRadius:'0 6px 6px 0', color:'#070B14', cursor:'pointer', fontWeight:700, fontSize:14 }}
                >→</motion.button>
              </div>
            </div>

            <motion.button
              onClick={clearAll}
              whileHover={{ borderColor: 'var(--border-hover)', color: 'var(--text-primary)' }}
              whileTap={{ scale: 0.97 }}
              style={{ width:'100%', background:'none', border:'1px dashed var(--border-default)', color:'var(--text-secondary)', padding:'8px', borderRadius:6, cursor:'pointer', fontSize:11 }}
            >
              ↺ CLEAR ALL FILTERS
            </motion.button>
          </Card>
        </div>

        {/* Task grid + pagination */}
        <div style={{ display:'flex', flexDirection:'column' }}>
          <AnimatePresence mode="wait">
            <motion.div
              key={filterKey + '-' + viewMode}
              initial="hidden"
              animate="visible"
              variants={staggerContainer()}
              style={{ alignContent:'start' }}
            >
              {filtered.length === 0 ? (
                <motion.div variants={fadeUp}>
                  <div className="empty-state">
                    <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
                      <circle cx="28" cy="28" r="18" stroke="var(--border-hover)" strokeWidth="2"/>
                      <line x1="41" y1="41" x2="56" y2="56" stroke="var(--border-hover)" strokeWidth="2.5" strokeLinecap="round"/>
                      <line x1="22" y1="28" x2="34" y2="28" stroke="var(--aqua)" strokeWidth="1.5" strokeLinecap="round" opacity="0.5"/>
                      <line x1="28" y1="22" x2="28" y2="34" stroke="var(--aqua)" strokeWidth="1.5" strokeLinecap="round" opacity="0.5"/>
                    </svg>
                    <div style={{ fontSize:15, fontWeight:600, color:'var(--text-secondary)' }}>No tasks match your filters</div>
                    <div style={{ fontSize:13 }}>Try adjusting the tier, category, or search terms</div>
                  </div>
                </motion.div>
              ) : viewMode === 'grouped' ? (
                Object.entries(groupedTasks)
                  .sort(([a], [b]) => a.localeCompare(b))
                  .map(([type, tasks]) => (
                    <motion.div key={type} variants={staggerItem} style={{ marginBottom:32 }}>
                      <div style={{ display:'flex', alignItems:'center', gap:12, marginBottom:16, paddingBottom:10, borderBottom:'1px solid rgba(0,255,224,0.12)' }}>
                        <span style={{ fontSize:13, fontWeight:700, color:'#00FFE0', fontFamily:'monospace', letterSpacing:'0.05em' }}>{type}</span>
                        <span style={{ fontSize:11, color:'rgba(255,255,255,0.35)', background:'rgba(255,255,255,0.06)', borderRadius:4, padding:'2px 8px' }}>
                          {tasks.length} task{tasks.length !== 1 ? 's' : ''}
                        </span>
                        <div style={{ flex:1, height:1, background:'rgba(0,255,224,0.06)' }}/>
                        <span style={{ fontSize:10, fontWeight:700, color:TIER_COLORS[tasks[0]?.tier] || '#fff', letterSpacing:'0.08em' }}>
                          TIER {tasks[0]?.tier}
                        </span>
                      </div>
                      <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(280px,1fr))', gap:14 }}>
                        {tasks.map(task => (
                          <TaskCard key={task.task_id} task={task} onClick={() => onOpenModal(task)} onCopy={copyId} copied={copied}/>
                        ))}
                      </div>
                    </motion.div>
                  ))
              ) : (
                <motion.div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(290px,1fr))', gap:14 }}>
                  {paginatedTasks.map(task => (
                    <motion.div key={task.task_id} variants={staggerItem}>
                      <TaskCard task={task} onClick={() => onOpenModal(task)} onCopy={copyId} copied={copied}/>
                    </motion.div>
                  ))}
                </motion.div>
              )}
            </motion.div>
          </AnimatePresence>

          {viewMode === 'grid' && totalPages > 1 && (
            <div style={{ display:'flex', alignItems:'center', justifyContent:'center', gap:8, marginTop:32, paddingTop:24, borderTop:'1px solid rgba(0,255,224,0.08)' }}>
              <button
                data-hover="true"
                onClick={() => setCurrentPage(p => Math.max(1, p-1))}
                disabled={currentPage === 1}
                style={{ padding:'6px 14px', borderRadius:6, border:'1px solid rgba(0,255,224,0.2)', background:'transparent', color: currentPage === 1 ? 'rgba(255,255,255,0.2)' : '#00FFE0', fontSize:12, cursor:'none' }}
              >← Prev</button>
              {Array.from({ length: totalPages }, (_, i) => i + 1)
                .filter(p => p === 1 || p === totalPages || Math.abs(p - currentPage) <= 1)
                .reduce((acc, p, i, arr) => { if (i > 0 && p - arr[i-1] > 1) acc.push('…'); acc.push(p); return acc }, [])
                .map((p, i) => p === '…' ? (
                  <span key={`ell-${i}`} style={{ color:'rgba(255,255,255,0.3)', fontSize:12 }}>…</span>
                ) : (
                  <button
                    key={p}
                    data-hover="true"
                    onClick={() => setCurrentPage(p)}
                    style={{ width:32, height:32, borderRadius:6, border: p === currentPage ? '1px solid rgba(0,255,224,0.8)' : '1px solid rgba(255,255,255,0.1)', background: p === currentPage ? 'rgba(0,255,224,0.12)' : 'transparent', color: p === currentPage ? '#00FFE0' : 'rgba(255,255,255,0.4)', fontSize:12, fontWeight: p === currentPage ? 700 : 400, cursor:'none' }}
                  >{p}</button>
                ))
              }
              <button
                data-hover="true"
                onClick={() => setCurrentPage(p => Math.min(totalPages, p+1))}
                disabled={currentPage === totalPages}
                style={{ padding:'6px 14px', borderRadius:6, border:'1px solid rgba(0,255,224,0.2)', background:'transparent', color: currentPage === totalPages ? 'rgba(255,255,255,0.2)' : '#00FFE0', fontSize:12, cursor:'none' }}
              >Next →</button>
            </div>
          )}
        </div>
      </div>
      </motion.div>
      )}
      </AnimatePresence>

    </Section>
  )
}

function TaskCard({ task, onClick, onCopy, copied }) {
  const tc  = TIER_COLORS[task.tier] || C.aqua
  const typeInfo = TASK_TYPE_TOOLTIPS[task.task_type]
  const tipContent = typeInfo ? (
    <div>
      <div style={{ color:C.aqua, fontWeight:700, marginBottom:4 }}>{typeInfo.title}</div>
      <div style={{ color:C.blue, fontSize:11, marginBottom:6 }}>{typeInfo.subdivision}</div>
      <div style={{ marginBottom:6, fontSize:12 }}>{typeInfo.description}</div>
      <div style={{ color:C.textMuted, fontStyle:'italic', fontSize:11 }}>{typeInfo.textbook}</div>
    </div>
  ) : task.task_type

  return (
    <motion.div
      className="task-card card"
      onClick={onClick}
      style={{ '--tier-color': tc, cursor:'pointer', padding:'18px 18px 18px 16px', height:260, display:'flex', flexDirection:'column' }}
      whileHover={{ y: -3, boxShadow: 'var(--glow-md)', borderColor: 'var(--border-hover)' }}
      transition={{ type: 'spring', stiffness: 400, damping: 28 }}
    >
      <div className="task-id-row" style={{ justifyContent:'space-between', marginBottom:8, flexShrink:0 }}>
        <div className="task-id-row">
          <span style={{ fontFamily:'var(--font-mono)', fontSize:12, color:'var(--cyan)', fontWeight:700 }}>
            {task.task_id}
          </span>
          <span
            className="copy-icon"
            onClick={e => onCopy(task.task_id, e)}
            title="Copy ID">
            {copied===task.task_id ? '✓' : '⎘'}
          </span>
        </div>
        <span style={{ fontSize:9, padding:'2px 7px', borderRadius:4, fontWeight:700, color:tc, border:`1px solid ${tc}60` }}>
          T{task.tier}·{TIER_LABELS[task.tier]?.[0]}
        </span>
      </div>
      <Tooltip text={tipContent}>
        <div style={{ color:'var(--blue)', fontSize:10, fontWeight:600, marginBottom:8, flexShrink:0,
          letterSpacing:'0.05em', cursor:'help',
          borderBottom:'1px dashed rgba(0,180,216,0.3)', paddingBottom:4, display:'inline-block' }}>
          {task.task_type}
        </div>
      </Tooltip>
      <p style={{ color:'var(--text-secondary)', fontSize:13, lineHeight:1.6, margin:'8px 0 12px', flex:1, overflow:'hidden' }}>
        {(() => {
          const desc = task.description || TASK_TYPE_TOOLTIPS[task.task_type]?.description || ''
          return desc.slice(0,280) + (desc.length>280 ? '…' : '')
        })()}
      </p>
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', flexShrink:0 }}>
        <Pill color={task.category==='conceptual' ? C.aquaLight : C.blue}>
          {task.category==='computational_bayes' ? 'NUMERIC' : task.category.toUpperCase()}
        </Pill>
        <span style={{ color:'var(--aqua)', fontSize:10, fontWeight:700 }}>VIEW →</span>
      </div>
    </motion.div>
  )
}

function TaskModal({ task, onClose }) {
  const [promptOpen, setPromptOpen] = useState(false)

  useEffect(() => {
    const handler = e => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onClose])

  const inputs = task.inputs_str ? (() => {
    try { return JSON.stringify(JSON.parse(task.inputs_str), null, 2) } catch { return task.inputs_str }
  })() : null

  return (
    <>
        <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', padding:'0 0 18px', borderBottom:'1px solid var(--border-default)', marginBottom:20 }}>
          <span style={{ fontFamily:'var(--font-mono)', fontSize:15, color:'var(--cyan)', fontWeight:800 }}>{task.task_id}</span>
          <motion.button
            onClick={onClose}
            whileHover={{ background: 'var(--bg-card-hover)', borderColor: 'var(--border-hover)' }}
            whileTap={{ scale: 0.9 }}
            style={{ background:'none', border:'1px solid var(--border-default)', borderRadius:6, color:'var(--text-secondary)', fontSize:14, cursor:'pointer', padding:'3px 10px' }}
          >✕</motion.button>
        </div>

        <div>
          {/* Stable 2×2 metadata grid — fixed height, never shifts */}
          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:12, marginBottom:24 }}>
            {[
              { label:'TIER',       value:`${task.tier} — ${TIER_LABELS[task.tier]}` },
              { label:'DIFFICULTY', value:(task.difficulty||'').toUpperCase() },
              { label:'TYPE',       value:task.task_type },
              { label:'CATEGORY',   value:task.category==='computational_bayes' ? 'NUMERIC' : task.category.toUpperCase() },
            ].map(({ label, value }) => (
              <div key={label} style={{ background:'rgba(0,255,224,0.04)', border:'1px solid rgba(0,255,224,0.12)', borderRadius:8, padding:'12px 16px', minHeight:72 }}>
                <div style={{ fontSize:10, fontWeight:700, color:'#00FFE0', letterSpacing:'0.1em', marginBottom:8 }}>{label}</div>
                <div style={{ fontSize:15, fontWeight:500, color:'#ffffff' }}>{value}</div>
              </div>
            ))}
          </div>

          {/* Description */}
          <div style={{ marginBottom:20 }}>
            <div style={{ color:'var(--aqua)', fontSize:10, fontWeight:700, letterSpacing:'0.12em', marginBottom:10 }}>DESCRIPTION</div>
            <p style={{ color:'var(--text-primary)', fontSize:14, lineHeight:1.75, margin:0 }}>{task.description || TASK_TYPE_TOOLTIPS[task.task_type]?.description || ''}</p>
          </div>

          {/* Collapsible task inputs */}
          {inputs && (
            <div style={{ margin:'16px 0' }}>
              <button
                data-hover="true"
                onClick={() => setPromptOpen(p => !p)}
                style={{ display:'flex', alignItems:'center', gap:8, background:'none', border:'none', color:'#00FFE0', fontSize:11, fontWeight:700, letterSpacing:'0.1em', cursor:'none', padding:0 }}
              >
                <motion.span animate={{ rotate: promptOpen ? 90 : 0 }} transition={{ duration: 0.2 }}>▶</motion.span>
                TASK INPUTS
              </button>
              <AnimatePresence>
                {promptOpen && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.25, ease: 'easeInOut' }}
                    style={{ overflow: 'hidden' }}
                  >
                    <div style={{ marginTop:12, background:'rgba(0,0,0,0.4)', border:'1px solid rgba(255,255,255,0.08)', borderRadius:8, padding:'14px 16px', fontSize:13, color:'rgba(255,255,255,0.75)', lineHeight:1.7, fontFamily:'monospace', whiteSpace:'pre-wrap', maxHeight:300, overflowY:'auto' }}>
                      {inputs}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )}

          {/* Ground truth parameters */}
          {task.category!=='conceptual' && Object.keys(task.numeric_targets||{}).length>0 && (
            <div style={{ marginTop:20 }}>
              <div style={{ fontSize:11, fontWeight:700, color:'#00FFE0', letterSpacing:'0.1em', marginBottom:12, display:'flex', alignItems:'center', gap:8 }}>
                GROUND TRUTH
                <span style={{ fontSize:10, color:'rgba(0,255,224,0.5)', fontWeight:400, fontStyle:'italic' }}>
                  hover parameter names for definitions
                </span>
              </div>
              <div style={{ background:'rgba(0,0,0,0.3)', border:'1px solid rgba(0,255,224,0.1)', borderRadius:10, padding:'4px 16px' }}>
                {Object.entries(task.numeric_targets).map(([k,v]) => {
                  try {
                    return <ParamTooltip key={k} paramKey={k} value={v} />
                  } catch {
                    return (
                      <div key={k} style={{ display:'flex', justifyContent:'space-between', padding:'8px 0', borderBottom:'1px solid rgba(0,255,224,0.08)' }}>
                        <span style={{ color:'#00FFE0', fontFamily:'monospace', fontSize:13 }}>{k}</span>
                        <span style={{ color:'#fff', fontFamily:'monospace', fontSize:13 }}>{typeof v === 'number' ? v.toFixed(6) : String(v)}</span>
                      </div>
                    )
                  }
                })}
              </div>
            </div>
          )}

          {task.category==='conceptual' && (task.rubric_keys||[]).length>0 && (
            <div>
              <div style={{ color:'var(--aqua)', fontSize:10, fontWeight:700, letterSpacing:'0.12em', marginBottom:10 }}>
                RUBRIC KEYS <span style={{ color:'var(--text-secondary)', fontWeight:400, fontSize:10, marginLeft:8 }}>(hover for details)</span>
              </div>
              {task.rubric_keys.map((k,i) => {
                const tip = TOOLTIP_MAP[k]
                return (
                  <div key={i} style={{ color:'var(--text-primary)', fontSize:13, padding:'7px 0', borderBottom:'1px solid rgba(0,255,224,0.08)' }}>
                    <span style={{ color:'var(--aqua)', marginRight:8 }}>◆</span>
                    {tip ? (
                      <Tooltip text={<span style={{ fontSize:12, lineHeight:1.6 }}>{tip}</span>}>
                        <span style={{ cursor:'help', borderBottom:'1px dashed var(--border-hover)' }}>{k}</span>
                      </Tooltip>
                    ) : k}
                  </div>
                )
              })}
            </div>
          )}
        </div>
    </>
  )
}

// ═══════════════════════════════════════════════════════════════
//  6. VISUALIZATIONS
// ═══════════════════════════════════════════════════════════════
function Visualizations({ setFullImg }) {
  return (
    <Section id="visualizations" minHeight="auto">
      <VizGallery setFullImg={setFullImg} />
    </Section>
  )
}

// ═══════════════════════════════════════════════════════════════
//  7. ABOUT
// ═══════════════════════════════════════════════════════════════
const RQS = [
  { id:'RQ1', tier:'PRIMARY', color:'#00FFE0',
    label:'External-Judge Validation',
    question:'Does keyword-based scoring agree with external-judge evaluation on assumption articulation, both on base prompts and under prompt perturbation?',
    headline:[
      '20.74% combined keyword-judge disagreement across 2,850 evaluable runs',
      'Krippendorff α = 0.57 (assumption, n=750); negative α on reasoning quality (−0.125 [−0.197, −0.059]); method structure essentially chance-level (α=−0.009, CI contains zero)',
      'Keyword-judge gap widens under perturbation',
    ],
    viewLink:'judge',
    detail:'Methodology contribution: keyword rubrics systematically overstate assumption-checking quality on Bayesian tasks. Across 2,850 eligible runs (750 base + 2,100 perturbation) the Llama 3.3 70B external judge (Together AI) flags 591 keyword-judge disagreements on assumption_compliance. Krippendorff α (base, n=750) = 0.573 on assumption; α = −0.125 on reasoning_quality (CI [−0.197, −0.059] excludes zero — systematic disagreement); α = −0.009 on method_structure (CI [−0.072, +0.062] contains zero — essentially chance-level, neither aligned nor systematically opposed). Spearman ρ = 0.59 on assumption.',
    grounding:'Yamauchi et al. 2025 (arXiv:2506.13639) — α-over-ρ for inter-rater reliability. Liu et al. 2025 — multi-dim rubric baseline. Feuer et al. 2025 — single-judge limitation.',
  },
  { id:'RQ2', tier:'SUPPORTING', color:'#FFB347',
    label:'Bayesian Category Difficulty',
    question:'Which Bayesian inference categories yield the lowest accuracy under literature-weighted scoring, and is the difficulty pattern consistent across the five evaluated LLMs?',
    headline:[
      'REGRESSION cluster: ~0.30 mean accuracy across all 5 models',
      'MCMC and ADVANCED tasks follow as next-hardest',
      'Difficulty pattern is consistent across models (all 5 models find the same categories hardest)',
    ],
    viewLink:'tasks',
    detail:'Domain-specific failure surface that prior benchmarks cannot expose. REGRESSION cluster, MCMC, and ADVANCED tasks score below cohort mean across every model. Under literature-derived NMACR weights, Gemini ranks #1 on accuracy (0.7314 [0.7060, 0.7565]).',
    grounding:'Liu et al. 2025 (MathEval) — task-category convention. Boye & Moell 2025 (Math-Reasoning-Failures) — unwarranted-assumption category.',
  },
  { id:'RQ3', tier:'SUPPORTING', color:'#A78BFA',
    label:'Dominant Failure Mode',
    question:'When LLMs fail on Bayesian inference tasks, do failures stem mostly from assumption-articulation gaps or computational errors, and does the distribution differ by model?',
    headline:[
      '67 of 143 audited failures (46.9%) are assumption violations',
      '48 of 143 (33.6%) are math errors',
      'Per-model split varies sharply: ChatGPT assumption-dominated, Claude math-dominated',
    ],
    viewLink:'errors',
    detail:'ASSUMPTION_VIOLATION 67/143 base failures · MATHEMATICAL_ERROR 48 · FORMATTING 18 · CONCEPTUAL 10 · HALLUCINATION 0. Per-model split is heterogeneous: ChatGPT 25/38 assumption-dominated; Claude 10/19 math-dominated; Mistral 12/26 math-dominated; DeepSeek mixed; Gemini balanced.',
    grounding:'Du et al. 2025 (Ice Cream) — independent ~47% reproduction on causal-inference tasks. Boye & Moell 2025 — Math-Reasoning-Failures.',
  },
  { id:'RQ4', tier:'SUPPORTING', color:'#4A90D9',
    label:'Ranking Stability across Evaluation Lenses',
    question:'Do per-model rankings remain stable across accuracy, robustness to perturbation, and calibration measurements, or does the choice of evaluation lens produce divergent leaderboards?',
    headline:[
      'Three different leaderboards: Gemini wins accuracy; ChatGPT and Mistral statistically tied at top of robustness; Claude and ChatGPT essentially tied on calibration',
      'Three of five models are statistically noise-equivalent on robustness (ChatGPT, Mistral, Gemini)',
      'No single model dominates across all three axes',
    ],
    viewLink:'robustness',
    detail:'2,365 perturbation runs (5 models × 473 perturbations, 0 errors). Under literature-derived NMACR weights, ChatGPT and Mistral hold the top two robustness slots and are statistically tied: Δ=+0.0003 [−0.013, +0.014] and Δ=+0.0013 [−0.012, +0.014] — both CIs cross zero, the pair is not_separable. Gemini (Δ=+0.0129) is also CI-crosses-zero. Only Claude (Δ=+0.0305) and DeepSeek (Δ=+0.0388) clearly separate from zero. Three uniformly-robust task types: HIERARCHICAL, RJMCMC, VB.',
    grounding:'BrittleBench 2026 — perturbation taxonomy. Au et al. 2025 (ReasonBench) — variance-as-first-class. Hochlehnert et al. 2025 (Statistical Fragility) — separability tests.',
  },
  { id:'RQ5', tier:'SUPPORTING', color:'#7FFFD4',
    label:'Calibration Method-Dependence',
    question:'How does calibration error vary between verbalized confidence extraction and self-consistency-based extraction, and which models exhibit method-dependent calibration patterns?',
    headline:[
      'Verbalized ECE 0.03–0.20 (hedge-heavy across models)',
      'Self-consistency ECE 0.62–0.73 (all overconfident under repeat-agreement)',
      'All five models reverse direction between methods — calibration is method-dependent cohort-wide',
    ],
    viewLink:'calibration',
    detail:'Verbalized extraction (n=171 base/model): hedge-heavy, ECE 0.033–0.198. Consistency extraction (Phase 1C, n=161 numeric tasks × 3 reruns): all 5 models severely overconfident, ECE 0.62–0.73. The two methods yield qualitatively different conclusions across the cohort. Accuracy-calibration correlations (Pearson r): mistral 0.42, deepseek 0.42, claude 0.42, gemini 0.39, chatgpt 0.36 — moderate decoupling across all five models, tight band 0.36–0.42.',
    grounding:'FermiEval 2025 — overconfidence contrast. Multi-Answer Confidence 2026 — consistency-based path. Nagarkar et al. 2026.',
  },
]

const SCORE_DIMS = [
  { dim:'N', name:'Numerical Accuracy',     color:'#00FFE0' },
  { dim:'M', name:'Method Selection',       color:'#00B4D8' },
  { dim:'A', name:'Assumption Compliance',  color:'#7FFFD4' },
  { dim:'C', name:'Confidence Calibration', color:'#4A90D9' },
  { dim:'R', name:'Reasoning Quality',      color:'#A78BFA' },
]

function Research() {
  const [openRQ, setOpenRQ] = useState(null)
  return (
    <Section id="research" minHeight="auto">
      <SectionTitle>Research</SectionTitle>

      {/* § 0 — Research Question Integration callout (moved from Pipeline) */}
      <FadeIn>
        <div style={{ maxWidth:1100, margin:'0 auto 28px' }}>
          <Card style={{ padding:'18px 24px', borderColor:'rgba(0,255,224,0.28)' }}>
            <div style={{ display:'flex', alignItems:'center', gap:10, marginBottom:12 }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#00FFE0" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
              <div style={{ color:'#00FFE0', fontWeight:700, fontSize:13, letterSpacing:'0.08em' }}>RESEARCH QUESTION INTEGRATION</div>
            </div>
            <ul style={{ margin:0, padding:0, listStyle:'none' }}>
              {RQ_INTEGRATION_LINES.map((l, j) => (
                <li key={j} style={{ display:'flex', alignItems:'flex-start', gap:8, marginBottom: j < RQ_INTEGRATION_LINES.length - 1 ? 8 : 0 }}>
                  <span style={{ color:'#00FFE0', fontSize:8, marginTop:5, flexShrink:0 }}>◆</span>
                  <span style={{ color:'var(--text-secondary)', fontSize:13, lineHeight:1.6 }}>{l}</span>
                </li>
              ))}
            </ul>
          </Card>
        </div>
      </FadeIn>

      {/* § 1 — Research Questions (5 cards, equal size, 3+2 grid) */}
      <FadeIn>
        {(() => {
          const renderCard = (q, idx) => {
            const isOpen = openRQ === idx
            return (
              <motion.div
                key={q.id}
                onClick={() => setOpenRQ(isOpen ? null : idx)}
                whileHover={{ y: -4, boxShadow: `0 14px 44px ${q.color}33` }}
                animate={{ boxShadow: isOpen ? `0 0 0 2px ${q.color}60` : 'none' }}
                transition={{ type: 'spring', stiffness: 400, damping: 28 }}
                className="rq-card"
                style={{
                  cursor: 'pointer',
                  background: 'rgba(255,255,255,0.025)',
                  border: `1px solid ${q.color}33`,
                  borderTop: `3px solid ${q.color}`,
                  borderRadius: 14,
                  padding: '20px 22px',
                  position: 'relative',
                  overflow: 'hidden',
                  height: '100%',
                  boxSizing: 'border-box',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 10, flexWrap: 'wrap' }}>
                  <div style={{
                    width: 34, height: 34, borderRadius: 8,
                    background: `${q.color}18`, border: `1.5px solid ${q.color}`,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    color: q.color, fontWeight: 800, fontSize: 11, fontFamily: 'var(--font-mono)',
                  }}>{q.id}</div>
                  <span style={{
                    background: `${q.color}22`,
                    color: q.color,
                    fontSize: 9, fontWeight: 800, letterSpacing: '0.14em',
                    padding: '4px 8px', borderRadius: 4,
                  }}>{q.tier}</span>
                </div>
                <div style={{
                  color: '#fff', fontSize: 13.5, fontWeight: 700,
                  marginBottom: 6, lineHeight: 1.3,
                }}>{q.label}</div>
                <div style={{
                  color: 'rgba(232,244,248,0.65)', fontSize: 11.5,
                  lineHeight: 1.55, marginBottom: 10, fontStyle: 'italic',
                }}>{q.question}</div>
                <div style={{
                  background: `${q.color}10`, border: `1px solid ${q.color}33`, borderRadius: 8,
                  padding: '10px 12px', marginBottom: 10,
                }}>
                  <div style={{ color: q.color, fontSize: 9, fontWeight: 700, letterSpacing: '0.12em', marginBottom: 4 }}>HEADLINE</div>
                  {Array.isArray(q.headline) ? (
                    <ul style={{ color: '#fff', fontSize: 12, fontWeight: 600, lineHeight: 1.5, margin: 0, paddingLeft: 16 }}>
                      {q.headline.map((h, hi) => (
                        <li key={hi} style={{ marginBottom: hi < q.headline.length - 1 ? 4 : 0 }}>{h}</li>
                      ))}
                    </ul>
                  ) : (
                    <div style={{ color: '#fff', fontSize: 12, fontWeight: 700, lineHeight: 1.45 }}>{q.headline}</div>
                  )}
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
                  <span
                    onClick={(e) => {
                      e.stopPropagation()
                      const el = document.getElementById('visualizations')
                      if (el) {
                        const top = el.getBoundingClientRect().top + window.scrollY - 80
                        window.scrollTo({ top, behavior: 'smooth' })
                      }
                    }}
                    style={{ color: q.color, fontSize: 11, fontWeight: 700, cursor: 'pointer' }}
                  >View results →</span>
                  <span style={{ color: q.color, fontSize: 10, opacity: 0.7 }}>{isOpen ? 'Hide details ▲' : 'Show details ▼'}</span>
                </div>
                <AnimatePresence>
                  {isOpen && (
                    <motion.div
                      initial={{ opacity: 0, height: 0, marginTop: 0 }}
                      animate={{ opacity: 1, height: 'auto', marginTop: 14 }}
                      exit={{ opacity: 0, height: 0, marginTop: 0 }}
                      transition={{ duration: 0.25 }}
                      style={{ overflow: 'hidden' }}
                    >
                      <div style={{ borderTop: `1px solid ${q.color}33`, paddingTop: 12 }}>
                        <p style={{ color: 'rgba(232,244,248,0.78)', fontSize: 12, lineHeight: 1.7, margin: '0 0 10px' }}>{q.detail}</p>
                        <div style={{ color: q.color, fontSize: 10, fontWeight: 700, letterSpacing: '0.12em', marginBottom: 4 }}>GROUNDING</div>
                        <p style={{ color: 'rgba(232,244,248,0.6)', fontSize: 11, lineHeight: 1.6, margin: 0 }}>{q.grounding}</p>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            )
          }

          return (
            <div className="rq-grid" style={{ maxWidth: 1300, margin: '0 auto 24px' }}>
              {RQS.map((q, i) => renderCard(q, i))}
            </div>
          )
        })()}

        <div style={{ height:36 }}/>
      </FadeIn>

      {/* § 2 — Research Overview + CountUp stats */}
      <FadeIn delay={60}>
        <Card style={{ maxWidth:1100, margin:'0 auto 48px', padding:'36px 40px', textAlign:'center' }}>
          <p style={{ color:'var(--text-secondary)', fontSize:15, lineHeight:1.85, margin:'0 0 36px' }}>
            The first free-response Bayesian-inference benchmark with externally-validated rubric
            scoring. 171 tasks (136 Phase 1 + 35 Phase 2), 5 frontier LLMs, 5-dimensional
            N·M·A·C·R rubric, external Llama 3.3 70B judge, 473 perturbations, bootstrap-CI
            separability tests. Supervised by Dr. Vahe Movsisyan, AUA.
          </p>
          <div style={{ display:'flex', flexWrap:'wrap', justifyContent:'center', gap:'28px 40px' }}>
            {[
              { target:171,  label:'Tasks' },
              { target:5,    label:'Models' },
              { target:2365, label:'Perturbation Runs' },
              { target:38,   label:'Task Types' },
              { target:143,  label:'Failures Audited' },
            ].map(({ target, label }) => (
              <div key={label} style={{ textAlign:'center', minWidth:80 }}>
                <div style={{ fontFamily:'var(--font-mono)', fontSize:40, fontWeight:800, color:'var(--aqua)', lineHeight:1 }}>
                  <CountUp target={target}/>
                </div>
                <div style={{ color:'var(--text-muted)', fontSize:11, marginTop:6, letterSpacing:'0.1em', textTransform:'uppercase' }}>{label}</div>
              </div>
            ))}
          </div>
        </Card>
      </FadeIn>

      {/* § 2.5 — Live Results panel (moved from Pipeline) */}
      <FadeIn delay={70}>
        <div style={{ maxWidth:1100, margin:'0 auto 48px' }}>
          <LiveResults/>
        </div>
      </FadeIn>

      {/* § 3 — Key Findings */}
      <FadeIn delay={80}>
        <div className="kf-inside-about" style={{ maxWidth:1300, margin:'0 auto 48px' }}>
          <div style={{ color:'var(--aqua)', fontSize:13, fontWeight:700, letterSpacing:'0.16em', textAlign:'center', marginBottom:24 }}>
            KEY FINDINGS
          </div>
          <KeyFindingsSection/>
        </div>
      </FadeIn>

      {/* § 4 — Model capability overview (radar, full-width, end of section) */}
      <FadeIn delay={100}>
        <div style={{ maxWidth:1300, margin:'0 auto 52px' }}>
          <div style={{ color:'var(--aqua)', fontSize:13, fontWeight:700, letterSpacing:'0.12em', marginBottom:16, textAlign:'center' }}>MODEL CAPABILITY OVERVIEW</div>
          <Card style={{ padding:'24px 16px', display:'flex', flexDirection:'column', alignItems:'center' }}>
            <MultiModelRadar/>
          </Card>
        </div>
      </FadeIn>

    </Section>
  )
}

// References component is now imported from ./pages/References (fetches /api/v2/literature)

// ═══════════════════════════════════════════════════════════════
//  ROOT APP
// ═══════════════════════════════════════════════════════════════
export default function App() {
  const [modal,             setModal]             = useState(null)
  const [fullImg,           setFullImg]           = useState(null)
  const [gifModal,          setGifModal]          = useState(null)
  const [gifLoading,        setGifLoading]        = useState(false)
  const [gifError,          setGifError]          = useState(false)
  const [tasksOpen,         setTasksOpen]         = useState(false)
  const [interactiveModal,  setInteractiveModal]  = useState(null)
  const [radarVals, radarSource] = useRadarFromAPI()

  useEffect(() => {
    const handler = (e) => {
      if (e.key === 'Escape') { setModal(null); setFullImg(null); setGifModal(null); setInteractiveModal(null) }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [])

  return (
    <RadarValuesContext.Provider value={radarVals}>
    <RadarSourceContext.Provider value={radarSource}>
    <>
    <motion.div
      className="app-root"
      initial={{ opacity: 0, filter: 'blur(8px)' }}
      animate={{ opacity: 1, filter: 'blur(0px)' }}
      transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
      style={{ background:'var(--bg-primary)', minHeight:'100vh', color:'var(--text-primary)', overflowX:'hidden' }}
    >
      <GlobeBackground/>
      <ScrollProgress/>
      <Navbar/>
      <SideNav/>
      <Overview/>
      <SectionDivider/>
      <Pipeline/>
      <SectionDivider/>
      <Models/>
      <SectionDivider/>
      <DifficultyLadder/>
      <SectionDivider/>
      <Tasks onOpenModal={setModal} isOpen={tasksOpen} onToggle={()=>setTasksOpen(o=>!o)}/>
      <SectionDivider/>
      <Methodology/>
      <SectionDivider/>
      <Research/>
      <SectionDivider/>
      <Visualizations setFullImg={setFullImg}/>
      <SectionDivider/>
      <Limitations/>
      <SectionDivider/>
      <UserStudy/>
      <SectionDivider/>
      <References/>

      {/* Footer */}
      <footer style={{ borderTop:'1px solid rgba(0,255,224,0.1)', padding:'28px 64px 32px', textAlign:'center', background:'rgba(0,0,0,0.25)' }}>
        <nav style={{ display:'flex', justifyContent:'center', flexWrap:'wrap', gap:'6px 20px', marginBottom:14 }}>
          {['overview','pipeline','models','difficulty','tasks','methodology','research','visualizations','limitations','user-study','references'].map(id => (
            <a key={id} href={`#${id}`}
              style={{ color:'rgba(0,255,224,0.5)', fontSize:11, fontWeight:600, letterSpacing:'0.08em', textDecoration:'none', textTransform:'uppercase', transition:'color 0.18s' }}
              onMouseEnter={e=>e.currentTarget.style.color='#00FFE0'}
              onMouseLeave={e=>e.currentTarget.style.color='rgba(0,255,224,0.5)'}
            >
              {id.replace(/-/g,' ')}
            </a>
          ))}
        </nav>
        <div style={{ color:'rgba(255,255,255,0.45)', fontSize:13, lineHeight:1.9 }}>
          <a href="https://www.linkedin.com/in/albert-simonyan-3b0560311/" target="_blank" rel="noopener noreferrer"
            style={{ color:'var(--aqua)', textDecoration:'none', fontWeight:700 }}>Albert Simonyan
          </a>
          {' '}· DS 299 Capstone · American University of Armenia · 2026
        </div>
      </footer>

      <BackToTop/>
    </motion.div>

    {/* PNG lightbox — outside filter motion.div for same reason as task modal */}
    <AnimatePresence>
      {fullImg && (
        <motion.div
          key="fullimg-backdrop"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.18 }}
          onClick={() => setFullImg(null)}
          style={{
            position: 'fixed',
            top: 0, left: 0, right: 0, bottom: 0,
            zIndex: 999999,
            background: 'rgba(0,0,0,0.92)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '60px 40px 40px',
          }}
        >
          <button
            onClick={e => { e.stopPropagation(); setFullImg(null) }}
            style={{
              position: 'fixed',
              top: 20, right: 24,
              width: 40, height: 40,
              borderRadius: 8,
              border: '1px solid rgba(255,255,255,0.2)',
              background: 'rgba(6,12,26,0.95)',
              color: '#fff',
              fontSize: 18,
              cursor: 'none',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 999999,
            }}
          >✕</button>
          <img
            src={fullImg}
            alt="visualization"
            onClick={e => e.stopPropagation()}
            style={{
              maxWidth: '90vw',
              maxHeight: '85vh',
              objectFit: 'contain',
              borderRadius: 8,
              display: 'block',
              background: '#ffffff',
              padding: 16,
              boxShadow: '0 24px 80px rgba(0,0,0,0.6)',
            }}
          />
          <div style={{
            position: 'fixed',
            bottom: 16,
            left: '50%',
            transform: 'translateX(-50%)',
            color: 'rgba(255,255,255,0.2)',
            fontSize: 11,
            pointerEvents: 'none',
          }}>
            Click outside or press ESC to close
          </div>
        </motion.div>
      )}
    </AnimatePresence>

    {/* GIF modal — outside filter motion.div for same stacking context reason */}
    <AnimatePresence>
      {gifModal && (
        <motion.div
          key="gif-modal-backdrop"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.18 }}
          onClick={() => setGifModal(null)}
          style={{
            position: 'fixed', inset: 0, zIndex: 999990,
            background: 'rgba(0,0,0,0.9)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            padding: 24,
          }}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.93, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.93, y: 20 }}
            transition={{ duration: 0.22, ease: 'easeOut' }}
            onClick={e => e.stopPropagation()}
            style={{
              width: '88vw', maxWidth: 1100,
              background: 'rgba(6,12,26,0.98)',
              border: '1px solid rgba(0,255,224,0.2)',
              borderRadius: 16,
              display: 'flex', flexDirection: 'column',
              overflow: 'hidden',
              boxShadow: '0 24px 80px rgba(0,0,0,0.7)',
            }}
          >
            <div style={{
              flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              padding: '12px 20px', borderBottom: '1px solid rgba(0,255,224,0.1)',
            }}>
              <div style={{ color: '#00FFE0', fontSize: 14, fontWeight: 700 }}>Score Race Animation</div>
              <button
                onClick={() => setGifModal(null)}
                style={{
                  width: 34, height: 34, borderRadius: 8,
                  border: '1px solid rgba(255,255,255,0.15)',
                  background: 'rgba(255,255,255,0.05)',
                  color: 'rgba(255,255,255,0.7)',
                  fontSize: 16, cursor: 'none',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}
              >✕</button>
            </div>
            <div style={{ padding: 12, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 200 }}>
              {gifLoading && !gifError && (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12, position: 'absolute' }}>
                  <div style={{ width: 40, height: 40, border: '3px solid rgba(0,255,224,0.2)', borderTop: '3px solid #00FFE0', borderRadius: '50%', animation: 'spin 0.9s linear infinite' }}/>
                  <div style={{ color: 'rgba(0,255,224,0.6)', fontSize: 12, fontFamily: 'monospace' }}>Loading animation…</div>
                </div>
              )}
              {gifError && (
                <div style={{ color: 'rgba(255,107,107,0.8)', fontSize: 13, textAlign: 'center', padding: '24px 0' }}>
                  Failed to load animation. Check the file exists at <code style={{ fontFamily: 'monospace', fontSize: 11 }}>{gifModal}</code>
                </div>
              )}
              <img
                src={gifModal}
                alt="Score Race Animation"
                onLoad={() => setGifLoading(false)}
                onError={() => { setGifLoading(false); setGifError(true) }}
                style={{ maxWidth: '100%', maxHeight: '80vh', objectFit: 'contain', borderRadius: 8, display: gifError ? 'none' : 'block', opacity: gifLoading ? 0 : 1, transition: 'opacity 0.3s' }}
              />
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>

    {/* Interactive viz modal — full-screen iframe lightbox */}
    <AnimatePresence>
      {interactiveModal && (
        <motion.div
          key="interactive-modal-backdrop"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.18 }}
          onClick={() => setInteractiveModal(null)}
          style={{
            position: 'fixed', inset: 0, zIndex: 999990,
            background: 'rgba(0,0,0,0.92)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            padding: 24,
          }}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.93, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.93, y: 20 }}
            transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
            onClick={e => e.stopPropagation()}
            style={{
              width: '92vw', maxWidth: 1200, height: '88vh',
              background: 'rgba(6,12,26,0.98)',
              border: '1px solid rgba(0,255,224,0.2)',
              borderRadius: 16,
              display: 'flex', flexDirection: 'column',
              overflow: 'hidden',
              boxShadow: '0 24px 80px rgba(0,0,0,0.7)',
            }}
          >
            <div style={{
              flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              padding: '12px 20px', borderBottom: '1px solid rgba(0,255,224,0.1)',
            }}>
              <div style={{ color: '#00FFE0', fontSize: 14, fontWeight: 700 }}>{interactiveModal.title}</div>
              <button
                onClick={() => setInteractiveModal(null)}
                style={{
                  width: 34, height: 34, borderRadius: 8,
                  border: '1px solid rgba(255,255,255,0.15)',
                  background: 'rgba(255,255,255,0.05)',
                  color: 'rgba(255,255,255,0.7)',
                  fontSize: 16, cursor: 'none',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}
              >✕</button>
            </div>
            <iframe
              key={interactiveModal.url}
              src={interactiveModal.url}
              title={interactiveModal.title}
              style={{ flex: 1, border: 'none', background: '#050a16' }}
            />
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>

    {/* Task modal — outside filter-animated motion.div — filter creates stacking context, breaks position:fixed */}
    <AnimatePresence>
      {modal && (
        <motion.div
          key="task-modal-backdrop"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
          onClick={() => setModal(null)}
          style={{
            position: 'fixed',
            top: 0, left: 0, right: 0, bottom: 0,
            zIndex: 99999,
            background: 'rgba(0,0,0,0.85)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: 24,
          }}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.96, y: 16 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.96, y: 16 }}
            transition={{ duration: 0.2, ease: 'easeOut' }}
            onClick={e => e.stopPropagation()}
            style={{
              position: 'relative',
              width: '100%',
              maxWidth: 640,
              maxHeight: '85vh',
              overflowY: 'auto',
              background: 'rgba(8, 14, 28, 0.98)',
              border: '1px solid rgba(0,255,224,0.2)',
              borderRadius: 16,
              padding: 28,
              boxShadow: '0 24px 80px rgba(0,0,0,0.7)',
            }}
          >
            <TaskModal task={modal} onClose={() => setModal(null)} />
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
    </>
    </RadarSourceContext.Provider>
    </RadarValuesContext.Provider>
  )
}
