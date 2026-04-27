import { useState, useEffect, useRef, useMemo } from 'react'
import { motion, AnimatePresence, useInView, useScroll, useTransform } from 'motion/react'
import './App.css'
import tasksData from './data/tasks.json'
import statsData from './data/stats.json'
import resultsData from './data/results_summary.json'
import GlobeBackground from './components/GlobeBackground'
import Navbar          from './components/Navbar'
import NeuralNetwork   from './components/NeuralNetwork'
import ResultsSection  from './pages/ResultsSection'
import VizGallery      from './pages/VizGallery'
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
    color:'#00CED1', api:'api.anthropic.com/v1/messages',
    strengths:'Strong mathematical reasoning, excellent at step-by-step Bayesian derivations and conjugate updates', status:'READY' },
  { id:'gemini',   initials:'GM', name:'Gemini 2.5 Flash',  full:'Gemini 2.5 Flash',
    version:'gemini-2.5-flash',     provider:'Google DeepMind', lab:'Alphabet',
    color:'#FF6B6B', api:'generativelanguage.googleapis.com',
    strengths:'Fast inference, good at probability calculations and statistical formula application', status:'READY' },
  { id:'chatgpt',  initials:'GP', name:'GPT-4.1',           full:'GPT-4.1',
    version:'gpt-4.1',              provider:'OpenAI',           lab:'Microsoft Partnership',
    color:'#7FFFD4', api:'api.openai.com/v1/chat/completions',
    strengths:'Broad statistical knowledge, reliable at standard Bayesian textbook problems', status:'READY' },
  { id:'deepseek', initials:'DS', name:'DeepSeek Chat',     full:'DeepSeek Chat',
    version:'deepseek-chat',        provider:'DeepSeek AI',      lab:'China',
    color:'#4A90D9', api:'api.deepseek.com/v1/chat/completions',
    strengths:'Strong mathematical background, emerging capability in statistical inference tasks', status:'READY' },
  { id:'mistral',  initials:'MS', name:'Mistral Large',     full:'Mistral Large Latest',
    version:'mistral-large-latest', provider:'Mistral AI',       lab:'France',
    color:'#A78BFA', api:'api.mistral.ai/v1/chat/completions',
    strengths:'Strong reasoning with European research pedigree, competitive on formal mathematical tasks', status:'READY' },
]
const MODEL_META = Object.fromEntries(MODELS.map(m => [m.id, m]))

// ─── Pipeline ─────────────────────────────────────────────────
const PIPELINE = [
  { icon:'📐', label:'Task Generation',          title:'171 Statistical Tasks',
    stat:'38 task types · 4 tiers',
    desc:'Tasks span 38 types across Phase 1 (136 tasks: conjugate Bayes, frequentist inference, Markov chains) and Phase 2 (35 tasks: MCMC, Variational Bayes, ABC). Each task has deterministic ground truth computed with numpy seed=42.' },
  { icon:'💬', label:'Standardized Prompting',   title:'Zero-Shot CoT Protocol',
    stat:'3 prompting strategies',
    desc:'All models receive identical prompts requiring step-by-step reasoning (Wei et al., 2022). Three prompting modes implemented: Zero-shot CoT (baseline), Few-shot CoT (2 exemplars), Program-of-Thoughts (Chen et al., 2022).' },
  { icon:'🤖', label:'Multi-Model Evaluation',   title:'5 Leading LLMs',
    stat:'1,230 total runs',
    desc:'Claude, ChatGPT, Mistral, DeepSeek, Gemini evaluated under identical conditions via standardized Model Context Protocol. 1,230 total runs across all tasks and models.' },
  { icon:'📊', label:'Five-Dimensional Scoring', title:'N·M·A·C·R Rubric',
    stat:'N=M=A=C=R=0.20',
    desc:'Each response scored on: Numerical Accuracy (N), Method Selection (M), Assumption Compliance (A), Confidence Calibration (C), Reasoning Quality (R). Equal weights (0.20 each). Pass threshold: 0.50.' },
  { icon:'🔄', label:'Robustness Testing',       title:'RQ4: Perturbation Analysis',
    stat:'375 synthetic runs',
    desc:'75 base tasks × 3 perturbation types (numerical, rephrase, semantic) = 225 robustness run combinations per model. Tests whether models rely on surface patterns vs. genuine statistical understanding.' },
  { icon:'🔍', label:'Error Taxonomy',           title:'Systematic Error Classification',
    stat:'143 failures · 8 categories',
    desc:'143 failures classified into 8 error types (E1-E8) using hybrid rule-based + LLM-as-Judge pipeline. Most common: E3 Assumption Violation (119 cases), E7 Truncation (93 cases from 1024-token cap).' },
]

// ─── Radar ────────────────────────────────────────────────────
// Dimensions: Math Accuracy (pass_rate), Speed (inv latency), Consistency (RQ4 robustness),
// Assumption Compliance (avg_assumption_score), Conceptual Reasoning (avg_structure_score)
// Values derived from 2026-04-26 benchmark: 171 tasks × 5 models, all complete
const RADAR_DIMS = ['Math\nAccuracy','Speed','Consistency','Assumption\nCompliance','Conceptual\nReasoning']
const RADAR_VALS = {
  claude:   [0.89, 0.61, 0.91, 0.73, 0.95],
  gemini:   [0.86, 0.85, 0.90, 0.70, 0.93],
  chatgpt:  [0.78, 0.90, 0.93, 0.60, 0.87],
  deepseek: [0.79, 0.10, 0.90, 0.66, 0.88],
  mistral:  [0.85, 0.55, 0.92, 0.61, 0.90],
}

// ─── Task type tooltips ───────────────────────────────────────
const TASK_TYPE_TOOLTIPS = {
  DISC_MEDIAN:   { title:'Discrete Posterior Median',   subdivision:'Bayesian Point Estimation',        description:'Find the median of a discrete posterior distribution by computing cumulative probability and finding first value where CDF ≥ 0.5.',               textbook:'Lecture 21 · Carlin & Louis Ch.2' },
  BAYES_RISK:    { title:'Bayesian Risk',               subdivision:'Decision Theory',                   description:'Compute Bayes risk B(δ) = Σ R(δ,θᵢ)·π(θᵢ) — prior-weighted expected loss of an estimator.',                                                   textbook:'Lecture 22 · Carlin & Louis Ch.2' },
  BIAS_VAR:      { title:'Bias-Variance Decomposition', subdivision:'Frequentist Estimation Theory',     description:'Decompose MSE into bias² + variance. Verifies MSE = Bias² + Variance exactly for a given estimator.',                                             textbook:'Lecture 25 · Hoff Ch.5' },
  BINOM_FLAT:    { title:'Binomial with Flat Prior',    subdivision:'Conjugate Bayesian Models',         description:'Apply uniform Beta(1,1) prior to Binomial data. Posterior is Beta(x+1, n-x+1) — the Laplace smoothed estimate.',                                textbook:'Lecture 21 · Bolstad Ch.3' },
  DIRICHLET:     { title:'Dirichlet-Multinomial',       subdivision:'Multivariate Conjugate Models',     description:'Conjugate Bayesian model for categorical data. Dirichlet prior updated with multinomial counts to give Dirichlet posterior.',                     textbook:'Lecture 26-27 · Hoff Ch.3 · Bishop Ch.2' },
  FISHER_INFO:   { title:'Fisher Information',          subdivision:'Frequentist Estimation Theory',     description:'Compute I(θ) = E[(∂/∂θ log f)²] — expected curvature of log-likelihood. Measures how much data informs about θ.',                               textbook:'Lecture 23 · Ghosh et al Ch.1' },
  MINIMAX:       { title:'Minimax Criterion',           subdivision:'Statistical Decision Theory',       description:'Select estimator that minimizes worst-case (maximum) risk over all possible parameter values.',                                                   textbook:'Lecture 22 · Carlin & Louis Ch.2' },
  MSE_COMPARE:   { title:'MSE Comparison',              subdivision:'Frequentist Estimation Theory',     description:'Compare mean squared errors of competing estimators to determine which is superior.',                                                              textbook:'Lecture 25 · Hoff Ch.5' },
  NORMAL_GAMMA:  { title:'Normal-Gamma Model',          subdivision:'Conjugate Bayesian Models',         description:'Joint conjugate prior for Normal data with unknown mean and variance.',                                                                            textbook:'Lecture 16-20 · Hoff Ch.5' },
  OPT_SCALED:    { title:'Optimal Scaled Estimator',    subdivision:'Frequentist Estimation Theory',     description:'Find constant c minimizing MSE of c·max(Xᵢ). Optimal c = (n+2)/(n+1).',                                                                         textbook:'Lecture 25' },
  RC_BOUND:      { title:'Rao-Cramér Bound',            subdivision:'Frequentist Estimation Theory',     description:'Lower bound for estimator variance: Var(θ̂) ≥ (1+b\'(θ))²/I(θ). Determines whether estimator is efficient.',                                    textbook:'Lecture 23-24 · Ghosh et al Ch.1' },
  UNIFORM_MLE:   { title:'Uniform MLE',                 subdivision:'Maximum Likelihood Estimation',     description:'MLE for Uniform(0,θ) is max(X₁,...,Xₙ) — the largest order statistic.',                                                                         textbook:'Lecture 24-25 · Ghosh et al Ch.1' },
  MARKOV:        { title:'Markov Chain Analysis',       subdivision:'Stochastic Processes',              description:'Compute n-step transition probabilities, stationary distributions, and verify Chapman-Kolmogorov equations.',                                    textbook:'Lecture 30-33' },
  ORDER_STAT:    { title:'Order Statistics',            subdivision:'Frequentist Distribution Theory',   description:'Compute density and CDF of k-th order statistic X(k). For Uniform[0,1], X(k) ~ Beta(k, n-k+1).',                                              textbook:'Lecture 29' },
  REGRESSION:    { title:'OLS Linear Regression',       subdivision:'Frequentist Regression',            description:'Ordinary least squares estimators B̂ and Â that minimize sum of squared residuals.',                                                             textbook:'Lecture 37-38' },
  BOX_MULLER:    { title:'Box-Muller Transform',        subdivision:'Simulation Methods',                description:'Generate Normal(0,1) samples from Uniform(0,1) using η₁=√(-2logU)cos(2πV).',                                                                    textbook:'Lecture 36' },
  HPD:           { title:'HPD Credible Interval',       subdivision:'Bayesian Interval Estimation',      description:'Highest Posterior Density interval — shortest interval containing specified probability mass.',                                                    textbook:'Bolstad Ch.5 · Lee Ch.2' },
  BAYES_FACTOR:  { title:'Bayes Factor',                subdivision:'Bayesian Model Comparison',         description:'BF₁₂ = p(data|M₁)/p(data|M₂) — ratio of marginal likelihoods.',                                                                               textbook:'Carlin & Louis Ch.2 · Lee Ch.4' },
  JEFFREYS:      { title:'Jeffreys Prior',              subdivision:'Objective Bayesian Analysis',       description:'Invariant prior p(θ) ∝ √I(θ). For Binomial: Beta(0.5,0.5).',                                                                                   textbook:'Ghosh et al Ch.5 · Lee Ch.3' },
  PPC:           { title:'Posterior Predictive Check',  subdivision:'Bayesian Model Assessment',         description:'Check model fit by comparing observed T(y) to replicated T(y_rep).',                                                                             textbook:'Hoff Ch.4 · Carlin & Louis Ch.2' },
  BAYES_REG:     { title:'Bayesian Linear Regression',  subdivision:'Bayesian Regression',               description:'Normal-Inverse-Gamma conjugate prior for regression.',                                                                                           textbook:'Lecture 40 · Carlin & Louis Ch.4 · Hoff Ch.9' },
  MLE_MAP:       { title:'MLE vs MAP Comparison',       subdivision:'Bayesian vs Frequentist Estimation',description:'Compare MLE, MAP (posterior mode), and posterior mean. MAP shrinks MLE toward prior mean.',                                                     textbook:'Ghosh et al Ch.2 · Hoff Ch.3' },
  CI_CREDIBLE:   { title:'CI vs Credible Interval',     subdivision:'Frequentist vs Bayesian Inference', description:'Compare frequentist 95% CI with Bayesian 95% credible interval.',                                                                               textbook:'All 7 textbooks · Lecture 40' },
  LOG_ML:        { title:'Log Marginal Likelihood',     subdivision:'Bayesian Model Selection',          description:'log p(data|prior) — log normalizing constant of the posterior.',                                                                                  textbook:'Carlin & Louis Ch.2 · Ghosh et al Ch.2' },
  GAMBLER:       { title:"Gambler's Ruin",              subdivision:'Stochastic Processes',              description:'Probability of ruin starting from fortune i with absorbing barriers at 0 and M.',                                                               textbook:'Lecture 32' },
  STATIONARY:    { title:'Stationary Distribution',     subdivision:'Markov Chain Theory',               description:'Limiting distribution π satisfying π@P = π, sum(π)=1.',                                                                                         textbook:'Lecture 33' },
  RANGE_DIST:    { title:'Range Distribution',          subdivision:'Order Statistics',                  description:'Distribution of R = max(Xᵢ) - min(Xᵢ) for Uniform[0,1] samples.',                                                                              textbook:'Lecture 29' },
  MLE_EFFICIENCY:{ title:'MLE Efficiency',              subdivision:'Frequentist Estimation Theory',     description:'Verify MLE variance equals Rao-Cramér lower bound.',                                                                                             textbook:'Lecture 23-24' },
  BETA_BINOM:    { title:'Beta-Binomial Model',         subdivision:'Conjugate Bayesian Models',         description:'Canonical conjugate model: Beta(α,β) prior + Binomial likelihood = Beta(α+x, β+n-x) posterior.',                                              textbook:'Hoff Ch.3 · Bolstad Ch.3' },
  GAMMA_POISSON: { title:'Gamma-Poisson Model',         subdivision:'Conjugate Bayesian Models',         description:'Conjugate model for count data: Gamma(α,β) prior + Poisson likelihood = Gamma(α+Σx, β+n) posterior.',                                         textbook:'Hoff Ch.3 · Bolstad Ch.10' },
  CONCEPTUAL:    { title:'Conceptual Reasoning',        subdivision:'Bayesian Theory & Interpretation',  description:'Tests deep understanding of Bayesian concepts: prior influence, credible vs confidence intervals, exchangeability.',                              textbook:'All 7 textbooks' },
  // Phase 2 — Computational Bayesian Methods
  GIBBS:         { title:'Gibbs Sampling',              subdivision:'Computational Bayes (Phase 2)',     description:'Sample from bivariate normal via alternating conditional draws. Burn-in discarded; convergence verified against analytic marginals.',             textbook:'Hoff Ch.10 · Carlin & Louis Ch.4' },
  MH:            { title:'Metropolis–Hastings',         subdivision:'Computational Bayes (Phase 2)',     description:'MCMC on logit-transformed Binomial-Normal posterior. Proposal in logit space; accept/reject via log-acceptance ratio.',                          textbook:'Hoff Ch.10 · Carlin & Louis Ch.4' },
  HMC:           { title:'Hamiltonian Monte Carlo',     subdivision:'Computational Bayes (Phase 2)',     description:'Leapfrog integrator on Gaussian target. Analytical posterior used; energy error ≈ 0 for exact Gaussians.',                                       textbook:'Neal (2011) · Carlin & Louis Ch.4' },
  RJMCMC:        { title:'Reversible Jump MCMC',        subdivision:'Computational Bayes (Phase 2)',     description:'Analytical Bayes factor between M1 (one mean) and M2 (split means). Posterior model probabilities via prior-weighted odds.',                     textbook:'Green (1995) · Carlin & Louis Ch.7' },
  VB:            { title:'Variational Bayes (CAVI)',    subdivision:'Computational Bayes (Phase 2)',     description:'Exact CAVI for Normal-Normal conjugate model. Mean-field variational posterior; ELBO computed analytically.',                                    textbook:'Blei et al (2017) · Bishop Ch.10' },
  ABC:           { title:'Approximate Bayesian Computation', subdivision:'Computational Bayes (Phase 2)', description:'Rejection ABC: draw θ~Uniform prior, simulate data, accept if |mean(sim)-observed|≤ε. Tolerance 0.10.',                                     textbook:'Sisson et al (2018) · Carlin & Louis Ch.4' },
  HIERARCHICAL:  { title:'Hierarchical Bayesian Model', subdivision:'Computational Bayes (Phase 2)',     description:'Empirical Bayes normal hierarchy. Posterior hyperparameters for group mean; shrinkage factor toward grand mean.',                               textbook:'Hoff Ch.8 · Gelman et al Ch.5' },
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
    { label:'Numeric Accuracy',       weight:20, key:'N', color:'#00FFE0', desc:'Exact numerical match within tolerance bounds' },
    { label:'Method Structure',        weight:20, key:'M', color:'#A78BFA', desc:'Correct method selection and derivation steps' },
    { label:'Assumption Compliance',   weight:20, key:'A', color:'#00897B', desc:'Acknowledgment of prior, data, and model assumptions' },
    { label:'Confidence Calibration',  weight:20, key:'C', color:'#F59E0B', desc:'Expressed certainty matches actual accuracy' },
    { label:'Reasoning Quality',       weight:20, key:'R', color:'#EC4899', desc:'Shows work, identifies model, states formula, interprets result' },
  ]

  return (
    <div ref={ref}>
      <div style={{ color:'var(--aqua)', fontSize:10, fontWeight:700, letterSpacing:'0.12em', marginBottom:6, textAlign:'center' }}>
        COMPOSITE SCORE = N·0.20 + M·0.20 + A·0.20 + C·0.20 + R·0.20
      </div>
      <div style={{ color:'var(--text-muted)', fontSize:10, textAlign:'center', marginBottom:20 }}>
        Pass threshold: final_score ≥ 0.5
      </div>
      {bars.map(b => (
        <div key={b.key} style={{ marginBottom:18 }}>
          <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:6 }}>
            <div style={{ display:'flex', alignItems:'center', gap:8 }}>
              <span style={{ background:`${b.color}22`, color:b.color, fontWeight:800, fontSize:11, padding:'2px 7px', borderRadius:5, border:`1px solid ${b.color}44` }}>{b.key}</span>
              <span style={{ color:'var(--text-primary)', fontSize:13, fontWeight:600 }}>{b.label}</span>
            </div>
            <span style={{ color:b.color, fontWeight:800, fontSize:14, fontFamily:'var(--font-mono)' }}>{b.weight}%</span>
          </div>
          <div style={{ height:8, background:'rgba(255,255,255,0.06)', borderRadius:4, overflow:'hidden' }}>
            <motion.div
              initial={{ width:0 }}
              animate={isInView ? { width:`${b.weight}%` } : { width:0 }}
              transition={{ duration:1.1, delay:bars.indexOf(b)*0.2, ease:[0.22,1,0.36,1] }}
              style={{
                height:'100%', borderRadius:4,
                background:`linear-gradient(90deg, ${b.color}cc, ${b.color})`,
                boxShadow:`0 0 10px ${b.color}88`,
              }}
            />
          </div>
          <div style={{ color:'var(--text-muted)', fontSize:10, marginTop:4 }}>{b.desc}</div>
        </div>
      ))}
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
function TierLadder() {
  const [expanded, setExpanded] = useState(null)
  const total = statsData.total_tasks

  return (
    <div>
      <div style={{ color:'var(--aqua)', fontSize:10, fontWeight:700, letterSpacing:'0.12em', marginBottom:16, textAlign:'center' }}>
        DIFFICULTY LADDER · {total} TASKS
      </div>
      {[4,3,2,1].map(tier => {
        const info    = TIER_INFO[tier]
        const isOpen  = expanded === tier
        const pct     = Math.round((info.tasks / total) * 100)
        return (
          <motion.div
            key={tier}
            onClick={() => setExpanded(isOpen ? null : tier)}
            style={{
              background: isOpen ? `${info.color}0D` : 'rgba(0,0,0,0.18)',
              border:`1px solid ${isOpen ? info.color : info.color+'33'}`,
              borderRadius:10, marginBottom:8, cursor:'pointer', overflow:'hidden',
              transition:'border-color 0.2s, background 0.2s',
            }}
            whileHover={{ borderColor: info.color+'88' }}
            transition={{ type:'spring', stiffness:400, damping:30 }}
          >
            <div style={{ display:'flex', alignItems:'center', gap:12, padding:'12px 16px' }}>
              <div style={{
                width:32, height:32, borderRadius:8, flexShrink:0,
                background:`${info.color}18`, border:`1px solid ${info.color}66`,
                display:'flex', alignItems:'center', justifyContent:'center',
                color:info.color, fontWeight:800, fontSize:11,
              }}>T{tier}</div>
              <div style={{ flex:1 }}>
                <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
                  <span style={{ color:info.color, fontWeight:700, fontSize:12 }}>{info.label}</span>
                  <span style={{ color:'var(--text-muted)', fontSize:11, fontFamily:'var(--font-mono)' }}>{info.tasks} tasks</span>
                </div>
                <div style={{ fontSize:11, color:'var(--text-secondary)', marginTop:2 }}>{info.desc}</div>
              </div>
              <div style={{ width:48, flexShrink:0, textAlign:'right' }}>
                <div style={{ height:4, background:'rgba(255,255,255,0.06)', borderRadius:2, marginBottom:4, overflow:'hidden' }}>
                  <div style={{ height:'100%', width:`${pct}%`, background:info.color, borderRadius:2, boxShadow:`0 0 6px ${info.color}` }}/>
                </div>
                <span style={{ color:info.color+'88', fontSize:9, fontFamily:'var(--font-mono)' }}>{pct}%</span>
              </div>
              <motion.span
                style={{ color:info.color, fontSize:11, flexShrink:0, width:14, display:'inline-block' }}
                animate={{ rotate: isOpen ? 90 : 0 }}
                transition={{ duration:0.2 }}
              >▶</motion.span>
            </div>
            <AnimatePresence>
              {isOpen && (
                <motion.div
                  initial={{ height:0, opacity:0 }}
                  animate={{ height:'auto', opacity:1 }}
                  exit={{ height:0, opacity:0 }}
                  transition={{ duration:0.25, ease:[0.22,1,0.36,1] }}
                  style={{ overflow:'hidden' }}
                >
                  <div style={{ padding:'0 16px 14px 60px', color:'var(--text-secondary)', fontSize:12, lineHeight:1.7, borderTop:`1px solid ${info.color}22` }}>
                    <div style={{ paddingTop:10 }}>{info.detail}</div>
                    <div style={{ marginTop:8, display:'flex', gap:6, flexWrap:'wrap' }}>
                      {Object.entries(TASK_TYPE_TOOLTIPS)
                        .filter(() => true)
                        .slice(0,3)
                        .map(([k]) => (
                          <span key={k} style={{ fontSize:9, padding:'2px 7px', borderRadius:4, background:`${info.color}15`, color:info.color, border:`1px solid ${info.color}33` }}>{k}</span>
                        ))}
                      <span style={{ fontSize:9, padding:'2px 7px', color:'var(--text-muted)' }}>+ more</span>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )
      })}
    </div>
  )
}

// ─── Radar Chart ─────────────────────────────────────────────
function RadarChart({ model }) {
  const size=200, cx=100, cy=100, R=70, n=5
  const step = (Math.PI*2)/n
  const vals = RADAR_VALS[model.id] || Array(n).fill(0.7)

  const pts = vals.map((v,i) => {
    const a = i*step - Math.PI/2
    return { x: cx+v*R*Math.cos(a), y: cy+v*R*Math.sin(a) }
  })
  const axes = Array.from({length:n},(_,i)=>{
    const a = i*step - Math.PI/2
    return { ex: cx+R*Math.cos(a), ey: cy+R*Math.sin(a), lx: cx+(R+22)*Math.cos(a), ly: cy+(R+22)*Math.sin(a) }
  })
  const rings = [0.25,0.5,0.75,1].map(s =>
    Array.from({length:n},(_,i)=>{
      const a=i*step-Math.PI/2
      return `${cx+s*R*Math.cos(a)},${cy+s*R*Math.sin(a)}`
    }).join(' ')
  )
  const poly = pts.map(p=>`${p.x},${p.y}`).join(' ')

  return (
    <div className="radar-wrap">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {rings.map((r,i)=>(
          <polygon key={i} points={r} fill="none" stroke="rgba(0,255,224,0.1)" strokeWidth="1"/>
        ))}
        {axes.map((ax,i)=>{
          const lines = RADAR_DIMS[i].split('\n')
          return (
            <g key={i}>
              <line x1={cx} y1={cy} x2={ax.ex} y2={ax.ey} stroke="rgba(0,255,224,0.12)" strokeWidth="1"/>
              {lines.map((l,j)=>(
                <text key={j} x={ax.lx} y={ax.ly+(j*9)-(lines.length>1?4:0)}
                  textAnchor="middle" dominantBaseline="middle"
                  fontSize="7.5" fill="var(--text-secondary)">
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

// ─── Multi-model radar ────────────────────────────────────────
const MODEL_COLORS = { claude:'#00CED1', gemini:'#FF6B6B', chatgpt:'#7FFFD4', deepseek:'#4A90D9', mistral:'#A78BFA' }
function MultiModelRadar() {
  const size=260, cx=130, cy=130, R=90, n=5
  const step = (Math.PI*2)/n
  const rings = [0.25,0.5,0.75,1].map(s =>
    Array.from({length:n},(_,i)=>{ const a=i*step-Math.PI/2; return `${cx+s*R*Math.cos(a)},${cy+s*R*Math.sin(a)}` }).join(' ')
  )
  const axes = Array.from({length:n},(_,i)=>{
    const a=i*step-Math.PI/2
    return { ex:cx+R*Math.cos(a), ey:cy+R*Math.sin(a), lx:cx+(R+26)*Math.cos(a), ly:cy+(R+26)*Math.sin(a) }
  })
  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center' }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {rings.map((r,i)=><polygon key={i} points={r} fill="none" stroke="rgba(0,255,224,0.08)" strokeWidth="1"/>)}
        {axes.map((ax,i)=>{
          const lines=RADAR_DIMS[i].split('\n')
          return (
            <g key={i}>
              <line x1={cx} y1={cy} x2={ax.ex} y2={ax.ey} stroke="rgba(0,255,224,0.1)" strokeWidth="1"/>
              {lines.map((l,j)=>(
                <text key={j} x={ax.lx} y={ax.ly+(j*9)-(lines.length>1?4:0)} textAnchor="middle" dominantBaseline="middle" fontSize="8" fill="var(--text-secondary)">{l}</text>
              ))}
            </g>
          )
        })}
        {Object.entries(RADAR_VALS).map(([id, vals]) => {
          const pts=vals.map((v,i)=>{ const a=i*step-Math.PI/2; return `${cx+v*R*Math.cos(a)},${cy+v*R*Math.sin(a)}` }).join(' ')
          const col=MODEL_COLORS[id]||'#00FFE0'
          return <polygon key={id} points={pts} fill={col+'22'} stroke={col} strokeWidth="1.5" opacity="0.85"/>
        })}
      </svg>
      <div style={{ display:'flex', flexWrap:'wrap', justifyContent:'center', gap:10, marginTop:6 }}>
        {Object.keys(RADAR_VALS).map(id=>(
          <div key={id} style={{ display:'flex', alignItems:'center', gap:4, fontSize:9, color:'var(--text-secondary)' }}>
            <div style={{ width:12, height:3, borderRadius:2, background:MODEL_COLORS[id]||'#00FFE0' }}/>
            {id.toUpperCase()}
          </div>
        ))}
      </div>
    </div>
  )
}

// ─── Timeline ─────────────────────────────────────────────────
const MILESTONES = [
  { date:'Jan 2026',    sub:'Project\nStart' },
  { date:'Feb 2026',    sub:'Baseline\nImpl.' },
  { date:'Mar 2026',    sub:'Benchmark\nCreation' },
  { date:'Apr 2026',    sub:'LLM\nEvaluation' },
  { date:'May 8, 2026', sub:'Poster\nPresentation', highlight:true },
]

function Timeline() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, amount: 0.3 })
  return (
    <div ref={ref} style={{ marginTop:48 }}>
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 10 }}
        transition={{ duration: 0.5 }}
        style={{ color:'var(--aqua)', fontSize:10, fontWeight:700, letterSpacing:'0.14em', textAlign:'center', marginBottom:28 }}
      >
        DS 299 CAPSTONE TIMELINE
      </motion.div>
      <div className="timeline">
        <div className="timeline-rail"/>
        {MILESTONES.map((m,i)=>(
          <motion.div
            key={i}
            className="timeline-item"
            initial={{ opacity: 0, y: 16 }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 16 }}
            transition={{ duration: 0.5, delay: i * 0.1, ease: [0.22, 1, 0.36, 1] }}
          >
            <div className={`timeline-dot${m.highlight?' highlight':''}`}/>
            <div className="timeline-label">
              <div style={{ fontWeight:700, fontSize:11, color:m.highlight?'var(--aqua)':'var(--text-secondary)', lineHeight:1.4 }}>{m.date}</div>
              {m.sub.split('\n').map((l,j)=>(
                <div key={j} style={{ fontSize:10, color:'var(--text-muted)', lineHeight:1.4 }}>{l}</div>
              ))}
            </div>
          </motion.div>
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
        <div className="hero-watermark">BAYESIAN</div>
      </div>

      <div style={{ position:'relative', zIndex:1, display:'flex', flexDirection:'column', justifyContent:'center', alignItems:'center', minHeight:'calc(100vh - 200px)' }}>
        <motion.div
          style={{ textAlign:'center', maxWidth:980 }}
          initial="hidden"
          animate="visible"
          variants={staggerContainer(0.15)}
        >
          {/* Eyebrow */}
          <motion.div variants={fadeUp} style={{ color:'var(--aqua)', fontSize:11, letterSpacing:'0.28em', marginBottom:20, fontFamily:'var(--font-mono)' }}>
            // DS 299 · CAPSTONE · 2026
          </motion.div>

          {/* Hero title */}
          <motion.h1 variants={fadeUp} style={{ fontSize:'clamp(32px,5.5vw,66px)', fontWeight:700, lineHeight:1.15, color:'var(--text-primary)', marginBottom:24 }}>
            Benchmarking LLMs on{' '}
            <span style={{ background:'linear-gradient(135deg,var(--aqua),var(--blue))', WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent' }}>
              Bayesian Statistical Reasoning
            </span>
          </motion.h1>

          <motion.p variants={fadeUp} style={{ color:'var(--text-secondary)', fontSize:15, marginBottom:44, lineHeight:1.7 }}>
            Evaluating <b style={{ color:'var(--text-primary)' }}>Claude · Gemini · ChatGPT · DeepSeek · Mistral</b>
            <br/>on 171 benchmark tasks across 38 Bayesian topic areas
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
          <motion.div variants={fadeUp} style={{ width:'60%', height:1, background:'linear-gradient(90deg,transparent,var(--aqua),transparent)', margin:'44px auto', opacity:0.3 }}/>

          {/* CTAs */}
          <motion.div variants={fadeUp} style={{ display:'flex', gap:14, justifyContent:'center' }}>
            <motion.button
              className="btn-primary"
              whileHover={{ y: -3, boxShadow: 'var(--glow-md)' }}
              whileTap={{ scale: 0.96 }}
              transition={{ type: 'spring', stiffness: 400, damping: 28 }}
              onClick={() => document.getElementById('results')?.scrollIntoView({behavior:'smooth'})}
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
          </motion.div>
        </motion.div>
      </div>
    </Section>
  )
}

// ═══════════════════════════════════════════════════════════════
//  2. BENCHMARK
// ═══════════════════════════════════════════════════════════════
function BenchmarkSection() {
  const [expanded, setExpanded] = useState(null)
  const pipelineRef = useRef(null)
  const isPipelineInView = useInView(pipelineRef, { once: true, amount: 0.2 })

  return (
    <Section id="benchmark" minHeight="auto">
      <SectionTitle sub="From textbooks to benchmark tasks to model evaluation — click any step to expand">How It Works</SectionTitle>

      {/* Pipeline */}
      <motion.div
        ref={pipelineRef}
        initial="hidden"
        animate={isPipelineInView ? 'visible' : 'hidden'}
        variants={staggerContainer(0.1)}
        style={{ display:'flex', justifyContent:'center', alignItems:'flex-start', flexWrap:'wrap', gap:0, marginBottom:16 }}
      >
        {PIPELINE.map((s,i) => (
          <motion.div key={s.label} variants={staggerItem} style={{ display:'flex', alignItems:'center' }}>
            <div style={{ position:'relative' }}>
              <span className="step-badge">{String(i+1).padStart(2,'0')}</span>
              <motion.div
                className={`card${expanded===i?' card-glow':''}`}
                style={{ width:155, textAlign:'center', padding:'20px 12px', cursor:'pointer',
                  borderColor: expanded===i ? 'var(--border-hover)' : undefined,
                  background: expanded===i ? 'rgba(0,255,224,0.04)' : undefined }}
                onClick={() => setExpanded(expanded===i ? null : i)}
                whileHover={{ y:-4, boxShadow:'var(--glow-md)', borderColor:'var(--border-hover)' }}
                transition={{ type:'spring', stiffness:400, damping:28 }}
              >
                <div style={{ fontSize:26, marginBottom:8, lineHeight:1 }}>{s.icon}</div>
                <div style={{ color:'var(--aqua)', fontWeight:700, fontSize:10, marginBottom:4, letterSpacing:'0.06em' }}>{s.label}</div>
                <div style={{ color:'var(--text-primary)', fontSize:11, fontWeight:600, marginBottom:5, lineHeight:1.3 }}>{s.title}</div>
                <div style={{ color:'var(--aqua)', fontSize:8, opacity:0.65, letterSpacing:'0.04em' }}>{s.stat}</div>
                <div style={{ color:'var(--text-muted)', fontSize:9, marginTop:6 }}>{expanded===i ? '▲ collapse':'▼ expand'}</div>
              </motion.div>
            </div>
            {i < PIPELINE.length-1 && (
              <div className="arrow-wrap">
                <span style={{ fontSize:16 }}>→</span>
                <div className="travel-dot" style={{ animationDelay:`${i*0.5}s` }}/>
              </div>
            )}
          </motion.div>
        ))}
      </motion.div>

      {/* Accordion detail */}
      <AnimatePresence mode="wait">
        {expanded !== null && (
          <motion.div
            key={expanded}
            initial={{ opacity:0, y:-8, height:0 }}
            animate={{ opacity:1, y:0, height:'auto' }}
            exit={{ opacity:0, y:-8, height:0 }}
            transition={{ duration:0.28, ease:[0.22,1,0.36,1] }}
            style={{ overflow:'hidden', maxWidth:680, margin:'0 auto 32px' }}
          >
            <Card glow style={{ padding:'22px 28px', textAlign:'center' }}>
              <div style={{ fontSize:30, marginBottom:8 }}>{PIPELINE[expanded].icon}</div>
              <div style={{ color:'var(--aqua)', fontWeight:700, fontSize:11, letterSpacing:'0.1em', marginBottom:4 }}>
                STEP {expanded+1} — {PIPELINE[expanded].label.toUpperCase()}
              </div>
              <div style={{ color:'var(--text-primary)', fontWeight:700, fontSize:16, marginBottom:12 }}>
                {PIPELINE[expanded].title}
              </div>
              <p style={{ color:'var(--text-secondary)', fontSize:13, lineHeight:1.75, margin:0 }}>
                {PIPELINE[expanded].desc}
              </p>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Tier Ladder + Scoring */}
      <FadeIn delay={150}>
        <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:24, maxWidth:800, margin:'0 auto' }}>
          <Card><TierLadder/></Card>
          <Card>
            <div style={{ color:'var(--aqua)', fontSize:10, fontWeight:700, letterSpacing:'0.12em', marginBottom:20 }}>SCORING FORMULA</div>
            <AnimatedScoringBars/>
            <LiveResults/>
          </Card>
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
                  {[['VERSION', selModel.version],['API', selModel.api],['MAX TOKENS','1 024']].map(([k,v]) => (
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
                  <div style={{ fontSize:9, color:'var(--text-muted)', marginBottom:4, textAlign:'center' }}>Placeholder · updates after runs</div>
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
function Tasks({ onOpenModal }) {
  const [tiers,       setTiers]       = useState([])
  const [category,    setCategory]    = useState('all')
  const [idInput,     setIdInput]     = useState('')
  const [topicInput,  setTopicInput]  = useState('')
  const [searchId,    setSearchId]    = useState('')
  const [searchTopic, setSearchTopic] = useState('')
  const [copied,      setCopied]      = useState(null)
  const [perPage,     setPerPage]     = useState(18)
  const [currentPage, setCurrentPage] = useState(1)
  const [viewMode,    setViewMode]    = useState('grid')

  const PER_PAGE_OPTIONS = [9, 18, 36, 72, 171]

  const filtered = useMemo(() => tasksData.filter(t => {
    if (tiers.length && !tiers.includes(t.tier)) return false
    if (category==='conceptual'          && t.category!=='conceptual')          return false
    if (category==='numeric'             && t.category!=='numeric')             return false
    if (category==='computational_bayes' && t.category!=='computational_bayes') return false
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
  const clearAll   = () => { setTiers([]); setCategory('all'); setIdInput(''); setTopicInput(''); setSearchId(''); setSearchTopic('') }
  const copyId     = (id, e) => {
    e.stopPropagation()
    navigator.clipboard.writeText(id).catch(()=>{})
    setCopied(id)
    setTimeout(()=>setCopied(null), 1500)
  }

  return (
    <Section id="tasks">
      <SectionTitle>Benchmark Tasks</SectionTitle>
      <div style={{ display:'grid', gridTemplateColumns:'250px 1fr', gap:24, alignItems:'start' }}>

        {/* Filter sidebar */}
        <motion.div
          style={{ position:'sticky', top:96 }}
          initial={{ opacity: 0, x: -20 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        >
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
                  { key:'all',                  label:'All' },
                  { key:'numeric',              label:'Numeric' },
                  { key:'conceptual',           label:'Concept' },
                  { key:'computational_bayes',  label:'Phase 2' },
                ].map(({ key: cat, label }) => (
                  <motion.button
                    key={cat}
                    onClick={() => setCategory(cat)}
                    whileTap={{ scale: 0.95 }}
                    style={{ flex:1, padding:'6px 4px', borderRadius:6, fontSize:10, fontWeight:700, cursor:'pointer',
                      border:`1px solid ${category===cat ? (cat==='computational_bayes'?'#A78BFA':'var(--aqua)') : 'var(--border-default)'}`,
                      background:category===cat?'var(--bg-card-hover)':'transparent',
                      color:category===cat ? (cat==='computational_bayes'?'#A78BFA':'var(--aqua)') : 'var(--text-secondary)',
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
        </motion.div>

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
      style={{ '--tier-color': tc, cursor:'pointer', padding:'18px 18px 18px 16px' }}
      whileHover={{ y: -3, boxShadow: 'var(--glow-md)', borderColor: 'var(--border-hover)' }}
      transition={{ type: 'spring', stiffness: 400, damping: 28 }}
    >
      <div className="task-id-row" style={{ justifyContent:'space-between', marginBottom:8 }}>
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
        <div style={{ color:'var(--blue)', fontSize:10, fontWeight:600, marginBottom:8,
          letterSpacing:'0.05em', cursor:'help',
          borderBottom:'1px dashed rgba(0,180,216,0.3)', paddingBottom:4, display:'inline-block' }}>
          {task.task_type}
        </div>
      </Tooltip>
      <p style={{ color:'var(--text-secondary)', fontSize:12, lineHeight:1.55, margin:'8px 0 12px', textTransform:'capitalize' }}>
        {(task.description||'').slice(0,105)}{(task.description||'').length>105?'…':''}
      </p>
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
        <Pill color={task.category==='conceptual' ? C.aquaLight : task.category==='computational_bayes' ? '#A78BFA' : C.blue}>
          {task.category==='computational_bayes' ? 'PHASE 2' : task.category.toUpperCase()}
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
              { label:'CATEGORY',   value:task.category.toUpperCase() },
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
            <p style={{ color:'var(--text-primary)', fontSize:14, lineHeight:1.75, margin:0, textTransform:'capitalize' }}>{task.description}</p>
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
//  5. RESULTS
// ═══════════════════════════════════════════════════════════════
function Results() {
  return (
    <Section id="results" minHeight="auto">
      <ResultsSection />
    </Section>
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
const TEXTBOOKS = [
  { text:'Bolstad — Introduction to Bayesian Statistics (2nd ed.)',              color:'#00FFE0', modules:['BB','HPD'] },
  { text:'Bishop — Pattern Recognition and Machine Learning',                    color:'#00B4D8', modules:['DIR'] },
  { text:'Ghosh, Delampady & Samanta — Introduction to Bayesian Analysis',       color:'#7FFFD4', modules:['JEF','RC'] },
  { text:'Hoff — A First Course in Bayesian Statistical Methods',                color:'#4A90D9', modules:['NG','PPC'] },
  { text:'Carlin & Louis — Bayesian Methods for Data Analysis (3rd ed.)',        color:'#00FFE0', modules:['BR','BF'] },
  { text:'Goldstein & Wooff — Bayes Linear Statistics',                          color:'#7FFFD4', modules:['BL'] },
  { text:'Lee — Bayesian Statistics: An Introduction (4th ed.)',                 color:'#00B4D8', modules:['CI'] },
]

const RQS = [
  { id:'RQ1', label:'Numerical & Statistical Accuracy',   color:'#00FFE0', status:'5/5 models complete · Claude 88.9% pass' },
  { id:'RQ2', label:'Method Selection Accuracy',           color:'#00B4D8', status:'5/5 models complete · structure scoring active' },
  { id:'RQ3', label:'Assumption Compliance',               color:'#7FFFD4', status:'5/5 models complete · assumption scoring active' },
  { id:'RQ4', label:'Robustness to Prompt Variations',     color:'#4A90D9', status:'375 runs · avg robustness 0.91 · ChatGPT most robust' },
  { id:'RQ5', label:'Confidence & Trust Calibration',      color:'#A78BFA', status:'✅ Complete · C=0.20 · calibration extraction active across 1,230 runs' },
]

const ABOUT_FINDINGS = [
  { icon:'🏆', text:'Claude leads overall (0.683) across all 171 tasks', color:'#00FFE0' },
  { icon:'📉', text:'MARKOV & STATIONARY hardest (avg 0.32) — all models struggle with Markov chain computations', color:'#FF6B6B' },
  { icon:'⚡', text:'E3 Assumption Violation most common (119 cases) — models proceed without stating priors, iid, or distributional assumptions', color:'#A78BFA' },
  { icon:'🔄', text:'Semantic perturbations cause largest score drops — surface framing shifts reasoning more than numerical changes', color:'#4A90D9' },
]
const ABOUT_REFS = [
  { authors:'Lu et al.', year:2025, title:'StatEval: Benchmarking LLMs on Statistical Reasoning', id:'arXiv:2510.09517' },
  { authors:'Nagarkar et al.', year:2026, title:'Can LLM Reasoning Be Trusted in Statistical Domains', id:'arXiv:2601.14479' },
  { authors:'Liu et al.', year:2025, title:'MathEval: A Comprehensive Benchmark for Mathematical Reasoning', id:'DOI:10.1007/s44366-025-0053-z' },
  { authors:'Chen et al.', year:2022, title:'Program of Thoughts Prompting', id:'arXiv:2211.12588' },
  { authors:'Wei et al.', year:2022, title:'Chain-of-Thought Prompting Elicits Reasoning in LLMs', id:'arXiv:2201.11903' },
]
const LECTURE_MAP = [
  ['Lec 21–22', 'MINIMAX · BAYES_RISK · DISC_MEDIAN'],
  ['Lec 23–25', 'FISHER_INFO · RC_BOUND · MLE_EFFICIENCY · BIAS_VAR'],
  ['Lec 26–27', 'DIRICHLET · BINOM_FLAT · GAMMA_POISSON'],
  ['Lec 28–29', 'ORDER_STAT · RANGE_DIST · UNIFORM_MLE · OPT_SCALED'],
  ['Lec 30–33', 'MARKOV · GAMBLER · STATIONARY'],
  ['Lec 36–38', 'BOX_MULLER · REGRESSION · LOG_ML'],
  ['Lec 39–40', 'BAYES_REG · CI_CREDIBLE · CONCEPTUAL'],
]
const SCORE_DIMS = [
  { dim:'N', name:'Numerical Accuracy',     color:'#00FFE0' },
  { dim:'M', name:'Method Selection',       color:'#00B4D8' },
  { dim:'A', name:'Assumption Compliance',  color:'#7FFFD4' },
  { dim:'C', name:'Confidence Calibration', color:'#4A90D9' },
  { dim:'R', name:'Reasoning Quality',      color:'#A78BFA' },
]

function About() {
  return (
    <Section id="about" minHeight="auto">
      <SectionTitle sub="DS 299 Capstone — evaluating LLM statistical reasoning at graduate level">About This Research</SectionTitle>

      {/* § 1 — Research Overview + CountUp stats */}
      <FadeIn>
        <Card style={{ maxWidth:900, margin:'0 auto 48px', padding:'36px 40px', textAlign:'center' }}>
          <p style={{ color:'var(--text-secondary)', fontSize:15, lineHeight:1.85, margin:'0 0 36px' }}>
            The first benchmark dedicated to Bayesian and inferential statistical reasoning,
            covering both classical conjugate methods and advanced computational techniques
            (MCMC, Variational Bayes, ABC). Five leading LLMs evaluated across five scoring
            dimensions derived from graduate-level curriculum.
          </p>
          <div style={{ display:'flex', flexWrap:'wrap', justifyContent:'center', gap:'28px 40px' }}>
            {[
              { target:171,  label:'Tasks' },
              { target:5,    label:'Models' },
              { target:1230, label:'Total Runs' },
              { target:38,   label:'Task Types' },
              { target:8,    label:'Error Categories' },
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

      {/* § 2 — Key Findings */}
      <FadeIn delay={80}>
        <div style={{ color:'var(--aqua)', fontSize:10, fontWeight:700, letterSpacing:'0.14em', textAlign:'center', marginBottom:20 }}>KEY FINDINGS</div>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(210px,1fr))', gap:14, maxWidth:900, margin:'0 auto 52px' }}>
          {ABOUT_FINDINGS.map((f,i) => (
            <motion.div
              key={i}
              whileHover={{ y:-4, scale:1.02, boxShadow:'var(--glow-md)' }}
              transition={{ type:'spring', stiffness:400, damping:28 }}
            >
              <Card style={{ padding:'22px 18px', height:'100%', boxSizing:'border-box' }}>
                <div style={{ fontSize:26, marginBottom:12 }}>{f.icon}</div>
                <div style={{ color:f.color, fontSize:12, lineHeight:1.65 }}>{f.text}</div>
              </Card>
            </motion.div>
          ))}
        </div>
      </FadeIn>

      {/* § 3 — Scoring Framework + Multi-model radar */}
      <FadeIn delay={140}>
        <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:24, maxWidth:900, margin:'0 auto 52px' }}>
          <Card style={{ padding:'24px 20px' }}>
            <div style={{ color:'var(--aqua)', fontSize:10, fontWeight:700, letterSpacing:'0.12em', marginBottom:20 }}>SCORING FRAMEWORK — N·M·A·C·R</div>
            {SCORE_DIMS.map(({ dim, name, color }) => (
              <div key={dim} style={{ display:'flex', alignItems:'center', gap:10, marginBottom:12 }}>
                <div style={{ width:28, height:28, borderRadius:6, background:`${color}22`, border:`1.5px solid ${color}`, display:'flex', alignItems:'center', justifyContent:'center', color, fontWeight:800, fontSize:13, flexShrink:0 }}>{dim}</div>
                <div style={{ flex:1 }}>
                  <div style={{ display:'flex', justifyContent:'space-between', marginBottom:4 }}>
                    <span style={{ color:'var(--text-primary)', fontSize:12, fontWeight:600 }}>{name}</span>
                    <span style={{ color:'var(--text-muted)', fontSize:11, fontFamily:'var(--font-mono)' }}>0.20</span>
                  </div>
                  <div style={{ height:4, background:'rgba(255,255,255,0.07)', borderRadius:2, overflow:'hidden' }}>
                    <motion.div initial={{ width:0 }} whileInView={{ width:'100%' }} viewport={{ once:true }}
                      transition={{ duration:0.8, delay:0.05 }}
                      style={{ height:'100%', background:`linear-gradient(90deg,${color}99,${color})`, borderRadius:2 }}/>
                  </div>
                </div>
              </div>
            ))}
            <div style={{ color:'var(--text-muted)', fontSize:10, marginTop:8, borderTop:'1px solid rgba(0,255,224,0.08)', paddingTop:10 }}>
              Pass threshold: 0.50 · Tier-5 stress multiplier: 1.5×
            </div>
          </Card>
          <Card style={{ padding:'24px 16px', display:'flex', flexDirection:'column', alignItems:'center' }}>
            <div style={{ color:'var(--aqua)', fontSize:10, fontWeight:700, letterSpacing:'0.12em', marginBottom:16, textAlign:'center' }}>MODEL CAPABILITY OVERVIEW</div>
            <MultiModelRadar/>
          </Card>
        </div>
      </FadeIn>

      {/* § 4 — Research Questions */}
      <FadeIn delay={170}>
        <div style={{ color:'var(--aqua)', fontSize:10, fontWeight:700, letterSpacing:'0.14em', textAlign:'center', marginBottom:20 }}>RESEARCH QUESTIONS</div>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(260px,1fr))', gap:12, maxWidth:900, margin:'0 auto 52px' }}>
          {RQS.map((q,i) => (
            <motion.div key={i} whileHover={{ x:4 }} transition={{ type:'spring', stiffness:400, damping:30 }}>
              <Card style={{ padding:'14px 16px', display:'flex', gap:10, alignItems:'flex-start' }}>
                <span style={{ background:`${q.color}22`, color:q.color, fontSize:9, fontWeight:700, padding:'3px 7px', borderRadius:4, flexShrink:0, marginTop:1 }}>{q.id}</span>
                <div>
                  <div style={{ color:'var(--text-primary)', fontSize:12, fontWeight:600, marginBottom:3 }}>{q.label}</div>
                  <div style={{ color:'var(--text-muted)', fontSize:10, fontStyle:'italic', lineHeight:1.4 }}>{q.status}</div>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>
      </FadeIn>

      {/* § 5 — References */}
      <FadeIn delay={200}>
        <div style={{ color:'var(--aqua)', fontSize:10, fontWeight:700, letterSpacing:'0.14em', textAlign:'center', marginBottom:20 }}>REFERENCES</div>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(270px,1fr))', gap:12, maxWidth:900, margin:'0 auto 52px' }}>
          {ABOUT_REFS.map((r,i) => (
            <motion.div key={i} whileHover={{ y:-3, scale:1.02, boxShadow:'var(--glow-md)' }} transition={{ type:'spring', stiffness:400, damping:28 }}>
              <Card style={{ padding:'14px 16px' }}>
                <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:6 }}>
                  <span style={{ color:'var(--text-muted)', fontSize:10 }}>{r.authors}</span>
                  <span style={{ background:'rgba(0,255,224,0.12)', color:'var(--aqua)', fontSize:9, fontWeight:700, padding:'2px 6px', borderRadius:4 }}>{r.year}</span>
                </div>
                <div style={{ color:'var(--text-primary)', fontSize:12, fontWeight:600, marginBottom:6, lineHeight:1.4 }}>{r.title}</div>
                <div style={{ fontFamily:'var(--font-mono)', fontSize:9, color:'var(--text-muted)' }}>{r.id}</div>
              </Card>
            </motion.div>
          ))}
        </div>
      </FadeIn>

      {/* § 6 — Textbooks */}
      <FadeIn delay={230}>
        <div style={{ color:'var(--aqua)', fontSize:10, fontWeight:700, letterSpacing:'0.14em', textAlign:'center', marginBottom:20 }}>7 GRADUATE TEXTBOOKS</div>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(270px,1fr))', gap:10, maxWidth:900, margin:'0 auto 52px' }}>
          {TEXTBOOKS.map((b,i) => (
            <motion.div key={i} whileHover={{ y:-3, scale:1.02 }} transition={{ type:'spring', stiffness:400, damping:28 }}>
              <Card style={{ padding:'12px 16px', display:'flex', gap:10, alignItems:'flex-start' }}>
                <div style={{ width:7, height:7, borderRadius:'50%', background:b.color, flexShrink:0, marginTop:4, boxShadow:`0 0 5px ${b.color}` }}/>
                <span style={{ color:'var(--text-secondary)', fontSize:11, lineHeight:1.55 }}>{b.text}</span>
              </Card>
            </motion.div>
          ))}
        </div>
      </FadeIn>

      {/* § 7 — Course Foundation */}
      <FadeIn delay={260}>
        <Card style={{ maxWidth:900, margin:'0 auto 40px', padding:'24px 28px' }}>
          <div style={{ color:'var(--aqua)', fontSize:10, fontWeight:700, letterSpacing:'0.14em', marginBottom:14 }}>COURSE FOUNDATION — DS 299 CAPSTONE</div>
          <p style={{ color:'var(--text-secondary)', fontSize:13, lineHeight:1.7, margin:'0 0 20px' }}>
            Built on DS 299 Capstone curriculum — Lectures 21–40 directly mapped to benchmark task types.
            Supervisor: Dr. Vahe Movsisyan, AUA.
          </p>
          <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(240px,1fr))', gap:8 }}>
            {LECTURE_MAP.map(([lec, tasks]) => (
              <div key={lec} style={{ display:'flex', gap:10, alignItems:'flex-start', padding:'8px 10px', background:'rgba(0,0,0,0.2)', borderRadius:8, border:'1px solid rgba(0,255,224,0.06)' }}>
                <span style={{ color:'var(--aqua)', fontSize:9, fontWeight:700, fontFamily:'var(--font-mono)', flexShrink:0, marginTop:1 }}>{lec}</span>
                <span style={{ color:'var(--text-muted)', fontSize:9, lineHeight:1.5 }}>{tasks}</span>
              </div>
            ))}
          </div>
        </Card>
      </FadeIn>

      <Timeline/>
    </Section>
  )
}

// ═══════════════════════════════════════════════════════════════
//  ROOT APP
// ═══════════════════════════════════════════════════════════════
export default function App() {
  const [modal,   setModal]   = useState(null)
  const [fullImg, setFullImg] = useState(null)

  useEffect(() => {
    const handler = (e) => {
      if (e.key === 'Escape') { setModal(null); setFullImg(null) }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [])

  return (
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
      <Overview/>
      <SectionDivider/>
      <BenchmarkSection/>
      <SectionDivider/>
      <Models/>
      <SectionDivider/>
      <Tasks onOpenModal={setModal}/>
      <SectionDivider/>
      <Results/>
      <SectionDivider/>
      <Visualizations setFullImg={setFullImg}/>
      <SectionDivider/>
      <About/>
      <motion.footer
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        style={{ textAlign:'center', padding:'28px 48px', borderTop:'1px solid var(--border-default)', color:'var(--text-muted)', fontSize:12, zIndex:1, position:'relative' }}
      >
        DS 299 Capstone · LLM Bayesian Benchmark · 2026 ·{' '}
        <span style={{ color:'var(--aqua)', fontFamily:'var(--font-mono)' }}>171 tasks · 5 models · 38 task types</span>
      </motion.footer>
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
            onLoad={() => console.log('PNG loaded:', fullImg)}
            onError={() => console.error('PNG failed:', fullImg)}
            style={{
              maxWidth: '90vw',
              maxHeight: '85vh',
              objectFit: 'contain',
              borderRadius: 8,
              display: 'block',
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
  )
}
