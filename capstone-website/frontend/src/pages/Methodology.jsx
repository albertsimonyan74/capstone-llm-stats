import { useRef } from 'react'
import { motion, useInView } from 'motion/react'
import {
  PerModelPassFlipPanel, KeywordDegradationPanel, PerDimRobustnessPanel,
  PerDimCalibrationPanel, AccCalibScatterPanel, PerModelFailuresPanel,
  BootstrapValidationPanel, AlphaValidationPanel, ToleranceValidationPanel,
  CalibrationMethodComparisonPanel, EligibilityFunnelPanel,
} from '../components/MethodologyPanels'
import ExpandablePanel from '../components/ExpandablePanel'

const ICON = {
  MessageSquare: (p) => (
    <svg width={p.size||20} height={p.size||20} viewBox="0 0 24 24" fill="none" stroke={p.color||'currentColor'} strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
    </svg>
  ),
  Scale: (p) => (
    <svg width={p.size||20} height={p.size||20} viewBox="0 0 24 24" fill="none" stroke={p.color||'currentColor'} strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
      <path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/>
      <path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/>
      <path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>
    </svg>
  ),
  BarChart3: (p) => (
    <svg width={p.size||20} height={p.size||20} viewBox="0 0 24 24" fill="none" stroke={p.color||'currentColor'} strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 3v18h18"/><path d="M7 16V8"/><path d="M12 16v-5"/><path d="M17 16V6"/>
    </svg>
  ),
  Shuffle: (p) => (
    <svg width={p.size||20} height={p.size||20} viewBox="0 0 24 24" fill="none" stroke={p.color||'currentColor'} strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
      <path d="M2 18h1.4c1.3 0 2.5-.6 3.3-1.7l6.1-8.6c.7-1.1 2-1.7 3.3-1.7H22"/>
      <path d="m18 2 4 4-4 4"/><path d="M2 6h1.9c1.5 0 2.9.9 3.6 2.2"/>
      <path d="M22 18h-5.9c-1.3 0-2.6-.7-3.3-1.8l-.5-.8"/><path d="m18 14 4 4-4 4"/>
    </svg>
  ),
  LineChart: (p) => (
    <svg width={p.size||20} height={p.size||20} viewBox="0 0 24 24" fill="none" stroke={p.color||'currentColor'} strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/>
    </svg>
  ),
  Target: (p) => (
    <svg width={p.size||20} height={p.size||20} viewBox="0 0 24 24" fill="none" stroke={p.color||'currentColor'} strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>
    </svg>
  ),
  Cpu: (p) => (
    <svg width={p.size||20} height={p.size||20} viewBox="0 0 24 24" fill="none" stroke={p.color||'currentColor'} strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
      <rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/>
      <path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3"/>
    </svg>
  ),
  Layers: (p) => (
    <svg width={p.size||20} height={p.size||20} viewBox="0 0 24 24" fill="none" stroke={p.color||'currentColor'} strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
      <path d="m12.83 2.18 8 4a2 2 0 0 1 0 3.64l-8 4a2 2 0 0 1-1.66 0l-8-4a2 2 0 0 1 0-3.64l8-4a2 2 0 0 1 1.66 0Z"/>
      <path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/>
      <path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/>
    </svg>
  ),
  CheckCheck: (p) => (
    <svg width={p.size||20} height={p.size||20} viewBox="0 0 24 24" fill="none" stroke={p.color||'currentColor'} strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
      <path d="M18 6 7 17l-5-5"/><path d="m22 10-7.5 7.5L13 16"/>
    </svg>
  ),
  AlertTriangle: (p) => (
    <svg width={p.size||20} height={p.size||20} viewBox="0 0 24 24" fill="none" stroke={p.color||'currentColor'} strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
      <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
      <path d="M12 9v4"/><path d="M12 17h.01"/>
    </svg>
  ),
  Calculator: (p) => (
    <svg width={p.size||20} height={p.size||20} viewBox="0 0 24 24" fill="none" stroke={p.color||'currentColor'} strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
      <rect width="16" height="20" x="4" y="2" rx="2"/>
      <line x1="8" x2="16" y1="6" y2="6"/>
      <line x1="16" x2="16" y1="14" y2="18"/>
      <path d="M16 10h.01"/><path d="M12 10h.01"/><path d="M8 10h.01"/>
      <path d="M12 14h.01"/><path d="M8 14h.01"/>
      <path d="M12 18h.01"/><path d="M8 18h.01"/>
    </svg>
  ),
  Languages: (p) => (
    <svg width={p.size||20} height={p.size||20} viewBox="0 0 24 24" fill="none" stroke={p.color||'currentColor'} strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
      <path d="m5 8 6 6"/>
      <path d="m4 14 6-6 2-3"/>
      <path d="M2 5h12"/>
      <path d="M7 2h1"/>
      <path d="m22 22-5-10-5 10"/>
      <path d="M14 18h6"/>
    </svg>
  ),
}

const JUDGE_FACTS = [
  { icon: ICON.Cpu,           label: 'JUDGE',                  color: '#FFB347', title: 'Llama 3.3 70B Instruct',                body: 'Sixth model deliberately external to the five evaluated (Claude · GPT-4.1 · Gemini · DeepSeek · Mistral) — no self-preference bias possible. The 70B parameter scale matches frontier-class judges in the literature (Yamauchi 2025) while remaining cost-feasible for 6,010+ scoring calls. Cross-provider spot-check against Groq’s Llama endpoint confirmed agreement, ruling out vendor-specific bias in judge outputs.', cite: 'via Together AI · spot-checked vs Groq' },
  { icon: ICON.Layers,        label: 'RUBRIC',                 color: '#A78BFA', title: '5 dimensions · 3 shared with keyword',  body: 'Each response scored 0–1 on five dimensions: Numerical (10%), Method (20%), Assumption (30%), Reasoning quality (25%), Confidence (15%). The literature-derived weights compose into a single 0–1 NMACR score. Three dimensions (Assumption, Reasoning, Method) are also extractable by the keyword scorer; α is computed on these three. Numerical and Confidence are judge-only — not extractable from response text via regex.',                                                                              cite: 'Yamauchi et al. (2025) rubric design' },
  { icon: ICON.AlertTriangle, label: 'DIVERGENCE & AGREEMENT', color: '#FF6B6B', title: 'α = +0.57 / −0.125 / −0.009',           body: 'Krippendorff α across the 3 shared dimensions (base, n=750). Assumption shows moderate agreement (α=+0.573, CI [0.516, 0.622]) — keyword and judge largely concur on assumption articulation. Reasoning quality is NEGATIVE (α=−0.125, CI excludes zero) — the two scorers structurally disagree. Method structure is essentially chance-level (α=−0.009, CI contains zero) — neither aligned nor systematically opposed.',                                                                                                                                                                                          cite: 'Reasoning CI [−0.197, −0.059] excludes 0 · Method CI [−0.072, +0.062] contains 0' },
]

const COMMITMENTS = [
  { icon: ICON.MessageSquare, label: 'PROMPTING',    color: '#00FFE0', title: 'Zero-shot Chain-of-Thought',     body: 'Single shipped prompting strategy; PoT explored but not in scored runs.',                                       cite: 'Wei et al. (2022)' },
  { icon: ICON.Scale,         label: 'SCORING',      color: '#A78BFA', title: 'External-judge validation',       body: 'Llama 3.3 70B Instruct via Together AI scores per-dimension, externally to the 5 evaluated models.',          cite: 'Yamauchi et al. (2025)' },
  { icon: ICON.BarChart3,     label: 'SEPARABILITY', color: '#00B4D8', title: 'Bootstrap-CI on rankings',        body: '10,000 resamples per model; statistical separability tested rather than asserted.',                          cite: 'Hochlehnert et al. (2025) · Longjohn et al. (2025)' },
  { icon: ICON.Shuffle,       label: 'ROBUSTNESS',   color: '#FFB347', title: 'Perturbation testing (3 types)',  body: 'Rephrase, numerical-substitution, semantic perturbations across 2,365 runs.',                                  cite: 'BrittleBench (2026)' },
  { icon: ICON.LineChart,     label: 'VARIANCE',     color: '#FF6B6B', title: 'Variance as first-class metric',  body: 'Per-task variance and rank stability reported alongside point estimates.',                                     cite: 'Au et al. (2025) · ReasonBench' },
  { icon: ICON.Target,        label: 'CALIBRATION',  color: '#7FFFD4', title: 'Dual-method calibration',         body: 'Verbalized confidence + self-consistency both measured; method-dependence disclosed.',                          cite: 'Nagarkar (2026) · Multi-Answer Confidence (2026)' },
]

const SCORE_DIMS = [
  { dim: 'A', name: 'Assumption Compliance',  weight: 0.30, color: '#7FFFD4', desc: 'Required assumption checks (prior_specified, iid_stated). Heaviest weight: Du 2025, Boye & Moell 2025, Yamauchi 2025 all identify assumption articulation as the primary failure mode in LLM statistical reasoning.' },
  { dim: 'R', name: 'Reasoning Quality',      weight: 0.25, color: '#A78BFA', desc: 'Four sub-criteria × 0.25: shows work, identifies model, states formula, interprets result. Yamauchi 2025: dimension where external-judge adds most over keyword scoring.' },
  { dim: 'M', name: 'Method Selection',       weight: 0.20, color: '#00B4D8', desc: 'Required structure checks (e.g. states_prior, applies_bayes_theorem). Wei 2022, Chen 2022: method articulation central but partially redundant with reasoning.' },
  { dim: 'C', name: 'Confidence Calibration', weight: 0.15, color: '#4A90D9', desc: 'Verbalized hedges + percentages. Nagarkar 2026, FermiEval 2025: separate evaluation track. Keyword-based extraction is the weakest baseline; honestly disclosed.' },
  { dim: 'N', name: 'Numerical Accuracy',     weight: 0.10, color: '#00FFE0', desc: 'Extracted from required ANSWER: line. Liu 2025, Boye & Moell 2025: necessary but trivially checkable. Lowest weight reflects this.' },
]

const LIT_TABLE = {
  cols: ['Dimension', 'StatEval (Lu 2025)', 'MathEval (Liu 2025)', 'ReasonBench (2025)', 'BrittleBench (2026)', 'Ice-Cream (Du 2025)', 'FermiEval (2025)', 'Nagarkar (2026)', 'THIS WORK'],
  rows: [
    ['Domain',           'Statistics (descriptive + freq.)', 'General math', 'General reasoning', 'General reasoning', 'Causal inference', 'Fermi estimation', 'Statistical reasoning', 'Bayesian inference'],
    ['# tasks',          '~500 (frequentist)', '17 datasets unified', 'multi-domain', 'multi-bench', '~30 pitfalls', 'Fermi-style', 'unspecified', '171 (136 P1 + 35 P2)'],
    ['Ground truth',     'Hand-crafted MC keys', 'Mixed', 'Mixed', 'Mixed', 'Hand-crafted', 'Closed-form bounds', 'Mixed', 'Closed-form + seeded MC'],
    ['Format',           'Multiple-choice', 'Mixed', 'Free-response', 'Free-response', 'Free-response', 'Numeric interval', 'Free-response', 'Free-response, 5-dim rubric'],
    ['External judge',   '✗', '✓ rubric', 'partial', '✗', '✗', '✗', '✗', '✓ Llama 3.3 70B (Together AI)'],
    ['Perturbations',    '✗', '✗', '✓ variance', '✓ 3 types', '✗', '✗', '✗', '✓ 398 v2 perturbations'],
    ['Statistical rigor','Single-point', 'Multi-dim aggregate', 'Variance-as-1st-class', 'Bootstrap recommended', 'Single-point', 'CI calibration', 'Single-point', 'Bootstrap CI + Krippendorff α'],
    ['NMACR weighting',  'equal/unspecified', 'equal/unspecified', 'unspecified', 'equal/unspecified', 'unspecified', 'unspecified', 'unspecified', 'literature-derived (A=.30, R=.25, M=.20, C=.15, N=.10)'],
    ['Calibration',      '✗', '✗', '✗', '✗', '✗', '✓ verbalised CI', 'partial', '✓ verbalized + consistency (MAC 2026)'],
    ['Error taxonomy',   '✗', 'partial', '✗', '✗', '✓ assumption', '✗', 'partial (hallucination)', '✓ 4-L1 / 9-L2 hierarchical'],
    ['Open data',        '✓', '✓', 'partial', '✓', '✓', '✓', 'partial', '✓ All artefacts open'],
  ],
}

function FadeIn({ children, delay = 0 }) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, amount: 0.1 })
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 20 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.6, delay: delay / 1000 }}
    >
      {children}
    </motion.div>
  )
}

function Subhead({ children }) {
  return (
    <div style={{
      color: '#00FFE0', fontSize: 11, fontWeight: 700,
      letterSpacing: '0.18em', marginBottom: 12, textTransform: 'uppercase',
    }}>
      {children}
    </div>
  )
}

function Card({ children, accent = 'rgba(0,255,224,0.18)' }) {
  return (
    <div style={{
      background: 'rgba(255,255,255,0.025)',
      border: `1px solid ${accent}`,
      borderRadius: 14,
      padding: '24px 28px',
      marginBottom: 20,
    }}>
      {children}
    </div>
  )
}

function Callout({ color = '#FFB347', title, children }) {
  return (
    <div style={{
      background: `${color}10`,
      border: `1px solid ${color}55`,
      borderLeft: `4px solid ${color}`,
      borderRadius: 10,
      padding: '14px 18px',
      margin: '14px 0',
    }}>
      {title && (
        <div style={{ color, fontSize: 11, fontWeight: 800, letterSpacing: '0.14em', textTransform: 'uppercase', marginBottom: 6 }}>
          {title}
        </div>
      )}
      <div style={{ color: 'rgba(232,244,248,0.85)', fontSize: 13, lineHeight: 1.7 }}>
        {children}
      </div>
    </div>
  )
}

const PERT_TYPE = [
  { kind: 'rephrase',   pct: 21.6, n: 162, total: 750 },
  { kind: 'numerical',  pct: 22.7, n: 136, total: 600 },
  { kind: 'semantic',   pct: 18.1, n: 136, total: 750 },
]

const LITERATURE_CONVERGENCE = [
  'Multi-dimensional rubrics (vs single accuracy) per Lu et al. (2025), Liu et al. (2025), and Boye & Moell (2025) — the N·M·A·C·R rubric extends this convention to Bayesian inference.',
  'Bootstrap CI separability of rankings is a methodological mandate per Longjohn et al. (2025), Hochlehnert et al. (2025), Au et al. (2025), and BrittleBench (2026) — the separability matrix follows this convention.',
  'Variance-as-first-class evaluation (not just accuracy) per Au et al. (2025), BrittleBench (2026), and Hochlehnert et al. (2025) — the three-rankings framework directly implements this framing.',
  'Verbalized confidence is unreliable for calibration per Nagarkar et al. (2026), FermiEval (2025), and Multi-Answer Confidence (2026) — the empty high-confidence bucket across all five models, plus the cohort-wide divergence between verbalized and consistency extraction, confirms this in the Bayesian setting.',
  'Three-way convergence on assumption violations as primary failure mode: Du et al. (2025), Boye & Moell (2025), and the 46.9% empirical finding here independently agree.',
  'Single-judge limitations require multi-judge ensembling per Yamauchi et al. (2025) and Feuer et al. (2025) — explicitly disclosed as project limitation; multi-judge is paper-scope future work.',
]

export default function Methodology() {
  return (
    <section id="methodology" style={{ padding: '96px 24px 80px', position: 'relative', zIndex: 1 }}>
      <div style={{ maxWidth: 1200, margin: '0 auto' }}>
        <FadeIn>
          <div style={{ color: 'rgba(0,255,224,0.55)', fontSize: 10, fontWeight: 700, letterSpacing: '0.2em', marginBottom: 8 }}>
            // METHODOLOGY · CONTINUITY · LITERATURE
          </div>
          <h2 style={{ fontSize: 'clamp(28px,3.5vw,42px)', fontWeight: 700, color: '#fff', margin: '0 0 8px', lineHeight: 1.2 }}>
            Methodology
          </h2>
          <div style={{ width: 64, height: 3, background: 'linear-gradient(90deg,#00FFE0,#00B4D8)', borderRadius: 2, marginBottom: 36 }} />
        </FadeIn>

        {/* 1 — Continuity statement */}
        <FadeIn delay={50}>
          <Subhead>1 · Continuity Statement</Subhead>
          <p style={{ color: 'rgba(232,244,248,0.82)', fontSize: 14, lineHeight: 1.8, margin: '0 0 20px' }}>
            This benchmark extends StatEval (Lu et al., 2025) from descriptive and hypothesis-testing
            statistics to Bayesian inference, adopting free-response with a 5-dimensional rubric
            (N·M·A·C·R) per the convention of MathEval (Liu et al., 2025).
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14, marginBottom: 20 }} className="commitments-grid">
            {COMMITMENTS.map((c) => {
              const Icon = c.icon
              return (
                <div key={c.label} style={{
                  background: `${c.color}06`,
                  border: `1px solid ${c.color}33`,
                  borderTop: `3px solid ${c.color}`,
                  borderRadius: 10,
                  padding: '14px 16px 12px',
                  display: 'flex', flexDirection: 'column', gap: 8,
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <Icon size={18} color={c.color}/>
                    <span style={{ color: c.color, fontFamily: 'monospace', fontSize: 10, letterSpacing: '0.14em', fontWeight: 800 }}>
                      {c.label}
                    </span>
                  </div>
                  <div style={{ color: '#fff', fontSize: 13.5, fontWeight: 700, lineHeight: 1.35 }}>
                    {c.title}
                  </div>
                  <div style={{ color: 'rgba(232,244,248,0.72)', fontSize: 12, lineHeight: 1.6 }}>
                    {c.body}
                  </div>
                  <div style={{
                    marginTop: 'auto',
                    paddingTop: 8,
                    borderTop: `1px solid ${c.color}22`,
                    color: `${c.color}`,
                    fontFamily: 'monospace',
                    fontSize: 10,
                    opacity: 0.85,
                  }}>
                    {c.cite}
                  </div>
                </div>
              )
            })}
          </div>
        </FadeIn>

        {/* 2 — N·M·A·C·R Rubric */}
        <FadeIn delay={100}>
          <Subhead>2 · N·M·A·C·R Rubric (literature-derived weights)</Subhead>
          <Card>
            <p style={{ color: 'rgba(232,244,248,0.85)', fontSize: 14, lineHeight: 1.7, margin: '0 0 18px' }}>
              Five dimensions, literature-derived weights, justified per dimension.
            </p>
            <div style={{
              display: 'flex', width: '100%', height: 56, borderRadius: 8, overflow: 'hidden',
              border: '1px solid rgba(255,255,255,0.10)', marginBottom: 8,
            }}>
              {SCORE_DIMS.map(d => (
                <div key={d.dim} title={`${d.dim}: ${(d.weight*100).toFixed(0)}%`} style={{
                  width: `${d.weight*100}%`,
                  background: `linear-gradient(180deg, ${d.color}, ${d.color}cc)`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  position: 'relative',
                  minWidth: 0,
                  overflow: 'hidden',
                  borderRight: '1px solid rgba(0,0,0,0.18)',
                }}>
                  <span style={{
                    fontFamily: 'monospace', fontSize: 13, fontWeight: 800,
                    color: 'rgba(0,0,0,0.82)', whiteSpace: 'nowrap', padding: '0 6px',
                    letterSpacing: '0.04em',
                  }}>
                    {d.dim} · {(d.weight*100).toFixed(0)}%
                  </span>
                </div>
              ))}
            </div>
            <p style={{ color: 'rgba(232,244,248,0.55)', fontSize: 11.5, fontStyle: 'italic', textAlign: 'center', margin: '0 0 18px' }}>
              Weights sum to 1.00. Dimensions weighted by literature convergence
              (Du 2025, Boye-Moell 2025, Yamauchi 2025).
            </p>
            <div className="nmacr-cards-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14 }}>
              {SCORE_DIMS.map(d => (
                <div key={d.dim} style={{
                  border: `1px solid ${d.color}33`,
                  borderTop: `3px solid ${d.color}`,
                  borderRadius: 10,
                  padding: '14px 16px',
                  background: `${d.color}08`,
                }}>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginBottom: 6 }}>
                    <span style={{ color: d.color, fontSize: 22, fontWeight: 800, fontFamily: 'monospace' }}>{d.dim}</span>
                    <span style={{ color: '#fff', fontSize: 12, fontWeight: 700 }}>{d.name}</span>
                    <span style={{ marginLeft: 'auto', color: d.color, fontSize: 14, fontWeight: 800, fontFamily: 'monospace' }}>{(d.weight * 100).toFixed(0)}%</span>
                  </div>
                  <div style={{ color: 'rgba(232,244,248,0.65)', fontSize: 11, lineHeight: 1.55 }}>
                    {d.desc}
                  </div>
                </div>
              ))}
            </div>
            <p style={{ color: 'rgba(232,244,248,0.55)', fontSize: 11, lineHeight: 1.7, margin: '14px 0 0' }}>
              <strong>Aggregation locus:</strong> the literature-derived weights are applied at the
              source. Both the runtime parser (<code style={{ fontSize: 10 }}>llm_runner/response_parser.py</code>)
              and the metrics path (<code style={{ fontSize: 10 }}>evaluation/metrics.py</code>)
              use the same NMACR_WEIGHTS = (A=0.30, R=0.25, M=0.20, C=0.15, N=0.10).
              Per-run aggregates are stored in
              <code style={{ fontSize: 10 }}> nmacr_scores_v2.jsonl</code>, the single source of truth
              for downstream analyses (bootstrap CI, robustness, calibration). CONCEPTUAL tasks
              (no N) renormalize remaining weights to 1.0; mirrors runtime
              <code style={{ fontSize: 10 }}>full_score()</code>.
            </p>
          </Card>
        </FadeIn>

        {/* 3 — Llama judge + keyword-degradation */}
        <FadeIn delay={150}>
          <Subhead>3 · External Llama Judge</Subhead>

          {/* Hero infographic: KEYWORD vs EXTERNAL JUDGE + 20.74% center stat */}
          <div className="judge-hero-infographic">
            <div className="judge-hero-row">
              <div className="judge-hero-block judge-hero-block-keyword">
                <div className="judge-hero-block-label">KEYWORD SCORER</div>
                <div className="judge-hero-block-detail">regex on required_assumption_checks</div>
              </div>
              <div className="judge-hero-vs">vs</div>
              <div className="judge-hero-block judge-hero-block-judge">
                <div className="judge-hero-block-label">EXTERNAL JUDGE</div>
                <div className="judge-hero-block-detail"><span className="llama-badge">LLAMA 3.3 70B INSTRUCT</span></div>
              </div>
            </div>
            <div className="judge-hero-arrow">↓ both score 2,850 evaluable runs ↓</div>
            <div className="judge-hero-stat">
              <div className="judge-hero-stat-number">20.74%</div>
              <div className="judge-hero-stat-label">disagreement (591 cases)<br/>on assumption_compliance</div>
            </div>
          </div>

          {/* 6 fact cards (3+3 grid) — same layout as §1 commitments */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14, margin: '8px 0 24px' }} className="commitments-grid">
            {JUDGE_FACTS.map((c) => {
              const Icon = c.icon
              return (
                <div key={c.label} style={{
                  background: `${c.color}06`,
                  border: `1px solid ${c.color}33`,
                  borderTop: `3px solid ${c.color}`,
                  borderRadius: 10,
                  padding: '14px 16px 12px',
                  display: 'flex', flexDirection: 'column', gap: 8,
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <Icon size={18} color={c.color}/>
                    <span style={{ color: c.color, fontFamily: 'monospace', fontSize: 10, letterSpacing: '0.14em', fontWeight: 800 }}>
                      {c.label}
                    </span>
                  </div>
                  <div style={{ color: '#fff', fontSize: 13.5, fontWeight: 700, lineHeight: 1.35 }}>
                    {c.title}
                  </div>
                  <div style={{ color: 'rgba(232,244,248,0.72)', fontSize: 12, lineHeight: 1.6 }}>
                    {c.body}
                  </div>
                  <div style={{
                    marginTop: 'auto', paddingTop: 8,
                    borderTop: `1px solid ${c.color}22`,
                    color: c.color, fontFamily: 'monospace', fontSize: 10, opacity: 0.85,
                  }}>
                    {c.cite}
                  </div>
                </div>
              )
            })}
          </div>

          {/* Krippendorff α explainer infographic */}
          <div className="alpha-explainer">
            <div className="alpha-explainer-header">
              <h4 className="alpha-explainer-title">ABOUT KRIPPENDORFF α</h4>
              <p className="alpha-explainer-subtitle">
                Chance-corrected agreement between keyword scorer and external judge
              </p>
            </div>

            {/* Formula */}
            <div className="alpha-formula-block">
              <div className="alpha-formula">
                <span className="alpha-formula-symbol">α</span>
                <span className="alpha-formula-equals">=</span>
                <span>1 − (D<sub>o</sub> / D<sub>e</sub>)</span>
              </div>
              <ul className="alpha-formula-annotations">
                <li><strong>D<sub>o</sub></strong> — Observed disagreement: how often the two raters actually disagree</li>
                <li><strong>D<sub>e</sub></strong> — Expected disagreement: how often two random raters would disagree by chance, given the same label frequencies</li>
              </ul>
            </div>

            {/* Coverage block — per-dimension n + judge-only note */}
            <div className="alpha-coverage-block">
              <div className="alpha-coverage-header">Computed on 3 shared dimensions:</div>
              <ul className="alpha-coverage-list">
                <li>
                  <span className="dim-name">Assumption compliance</span>
                  <span className="dim-n">n = 750</span>
                </li>
                <li>
                  <span className="dim-name">Reasoning quality</span>
                  <span className="dim-n">n = 750</span>
                </li>
                <li>
                  <span className="dim-name">Method structure</span>
                  <span className="dim-n">n = 750</span>
                </li>
              </ul>
              <p className="alpha-coverage-explanation">
                750 = 855 truly-base runs − 105 runs from 21 task families with empty
                <code> required_assumption_checks</code> (CONCEPTUAL · MINIMAX · BAYES_RISK · MARKOV_04).
                Tasks that don't require assumption articulation can't be compared across the two
                scoring methods.
              </p>
              <p className="alpha-coverage-note">
                Numerical and Confidence dimensions are judge-only — not included in α
              </p>
            </div>

            {/* Number line scale -1 to +1 */}
            <div className="alpha-scale">
              <div className="alpha-scale-track">
                {/* Tick marks */}
                {[
                  { pct: 0,   v: '−1.0' },
                  { pct: 25,  v: '−0.5' },
                  { pct: 50,  v: '0' },
                  { pct: 75,  v: '+0.5' },
                  { pct: 100, v: '+1.0' },
                ].map(t => (
                  <div key={t.pct} className="alpha-tick" style={{ left: `${t.pct}%` }}>{t.v}</div>
                ))}
                {/* Markers */}
                <div className="alpha-marker alpha-marker-r" style={{ left: '43.75%' }}>
                  <div className="alpha-marker-dot"/>
                  <div className="alpha-marker-label">R · α=−0.125<br/><span className="ci-note">CI excludes zero</span></div>
                </div>
                <div className="alpha-marker alpha-marker-m" style={{ left: '49.55%' }}>
                  <div className="alpha-marker-dot"/>
                  <div className="alpha-marker-label">M · α=−0.009<br/><span className="ci-note">CI contains zero</span></div>
                </div>
                <div className="alpha-marker alpha-marker-a" style={{ left: '78.65%' }}>
                  <div className="alpha-marker-dot"/>
                  <div className="alpha-marker-label">A · α=+0.57<br/><span className="ci-note">above chance</span></div>
                </div>
              </div>

              {/* Region labels */}
              <div className="alpha-scale-regions">
                <div className="alpha-region alpha-region-negative">
                  SYSTEMATIC DISAGREEMENT
                  <span className="alpha-region-note">Raters pull in opposite directions, beyond chance</span>
                </div>
                <div className="alpha-region alpha-region-zero">
                  CHANCE BASELINE
                  <span className="alpha-region-note">Agreement equal to random</span>
                </div>
                <div className="alpha-region alpha-region-positive">
                  AGREEMENT BEYOND CHANCE
                  <span className="alpha-region-note">Closer to 1 = stronger</span>
                </div>
              </div>
            </div>

            {/* Interpretive paragraph */}
            <div className="alpha-interpretation">
              When a chance-corrected metric goes <strong>below zero</strong>, the two methods
              aren't just disagreeing randomly — they're systematically pulling in opposite
              directions. Reasoning quality's CI [−0.197, −0.059] excludes zero with 95%
              confidence, meaning this is <strong>structural disagreement, not noise</strong>.
              The keyword scorer and external judge are measuring different constructs on this
              dimension. Method structure (α=−0.009, CI [−0.072, +0.062]) sits at the chance
              baseline — neither aligned nor systematically opposed.
            </div>
          </div>

          <Card>
            <Callout color="#00B4D8" title="Keyword vs judge under perturbation">
              Across the 2,850 eligible runs sharing the assumption-compliance rubric, keyword
              scoring degrades faster than LLM-judge under perturbation, with the two methods
              moving in opposite directions: surface-form changes — rephrasing, numerical
              reseeding, semantic reframing — disproportionately break keyword regex matches,
              whereas the LLM-judge tracks the underlying mathematical content more robustly. The
              effect is largest on semantic perturbations, where vocabulary changes disrupt
              keyword matching most aggressively. This provides direct empirical support for
              LLM-as-judge as the canonical assumption-compliance metric in robustness evaluation,
              where the goal is to measure reasoning competence independent of surface phrasing.
            </Callout>

            <div className="perturbation-explainer">
              <div className="perturbation-explainer-header">
                <h4 className="perturbation-explainer-title">HOW PERTURBATIONS ARE GENERATED</h4>
                <p className="perturbation-explainer-subtitle">
                  Three transformation types preserve the math while varying the surface
                </p>
              </div>

              <div className="perturbation-types-grid">
                <div className="perturbation-type-card pert-rephrase">
                  <div className="pert-card-header">
                    <ICON.MessageSquare size={18} />
                    <span className="pert-label">REPHRASE</span>
                  </div>
                  <p className="pert-description">Same problem, different wording. Math identical.</p>
                  <div className="pert-example">
                    <div className="pert-example-row pert-before">
                      <span className="pert-tag">BEFORE</span>
                      <span className="pert-text">A coin is flipped 10 times and lands heads 7 times. Beta(2,2) prior.</span>
                    </div>
                    <div className="pert-arrow">↓</div>
                    <div className="pert-example-row pert-after">
                      <span className="pert-tag">AFTER</span>
                      <span className="pert-text">Out of 10 coin flips, 7 came up heads. Beta(2,2) prior.</span>
                    </div>
                  </div>
                  <div className="pert-card-footer">
                    <span className="pert-rate">21.6%</span>
                    <span className="pert-rate-label">disagreement</span>
                  </div>
                </div>

                <div className="perturbation-type-card pert-numerical">
                  <div className="pert-card-header">
                    <ICON.Calculator size={18} />
                    <span className="pert-label">NUMERICAL</span>
                  </div>
                  <p className="pert-description">Same structure, different numbers. New correct answer.</p>
                  <div className="pert-example">
                    <div className="pert-example-row pert-before">
                      <span className="pert-tag">BEFORE</span>
                      <span className="pert-text">10 flips, 7 heads → posterior Beta(9, 5)</span>
                    </div>
                    <div className="pert-arrow">↓</div>
                    <div className="pert-example-row pert-after">
                      <span className="pert-tag">AFTER</span>
                      <span className="pert-text">15 flips, 11 heads → posterior Beta(14, 7)</span>
                    </div>
                  </div>
                  <div className="pert-card-footer">
                    <span className="pert-rate">22.7%</span>
                    <span className="pert-rate-label">disagreement</span>
                  </div>
                </div>

                <div className="perturbation-type-card pert-semantic">
                  <div className="pert-card-header">
                    <ICON.Languages size={18} />
                    <span className="pert-label">SEMANTIC</span>
                  </div>
                  <p className="pert-description">Same math, different domain. Vocabulary changed.</p>
                  <div className="pert-example">
                    <div className="pert-example-row pert-before">
                      <span className="pert-tag">BEFORE</span>
                      <span className="pert-text">10 coin flips, 7 heads, Beta(2,2) prior</span>
                    </div>
                    <div className="pert-arrow">↓</div>
                    <div className="pert-example-row pert-after">
                      <span className="pert-tag">AFTER</span>
                      <span className="pert-text">10 patients tested, 7 positive, Beta(2,2) prior</span>
                    </div>
                  </div>
                  <div className="pert-card-footer">
                    <span className="pert-rate">18.1%</span>
                    <span className="pert-rate-label">largest semantic gap effect</span>
                  </div>
                </div>
              </div>

              <p className="perturbation-explainer-caption">
                All variants pre-generated and stored canonically — every model sees identical prompts.
                Total: 2,365 perturbation runs across 171 base tasks.
              </p>
            </div>

            <ExpandablePanel title="Keyword vs Judge disagreement"><KeywordDegradationPanel /></ExpandablePanel>
            <div style={{ marginTop: 14, display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10 }}>
              {PERT_TYPE.map(p => (
                <div key={p.kind} style={{
                  border: '1px solid rgba(0,180,216,0.3)',
                  borderRadius: 8,
                  padding: '10px 12px',
                  background: 'rgba(0,180,216,0.06)',
                }}>
                  <div style={{ color: '#00B4D8', fontSize: 11, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 4 }}>{p.kind}</div>
                  <div style={{ color: '#fff', fontFamily: 'monospace', fontSize: 18, fontWeight: 800 }}>{p.pct}%</div>
                  <div style={{ color: 'rgba(232,244,248,0.55)', fontSize: 10 }}>{p.n} / {p.total} runs</div>
                </div>
              ))}
            </div>
          </Card>
        </FadeIn>

        {/* 3.5 — Per-model keyword-judge disagreement panel */}
        <FadeIn delay={165}>
          <ExpandablePanel title="Per-model keyword-judge disagreement"><PerModelPassFlipPanel /></ExpandablePanel>
        </FadeIn>

        {/* 4 — Per-model failure modes */}
        <FadeIn delay={180}>
          <Subhead>4 · Per-model failure modes</Subhead>
          <p style={{ color: 'rgba(232,244,248,0.82)', fontSize: 14, lineHeight: 1.75, margin: '0 0 16px' }}>
            The 46.9% assumption-violation headline (RQ3) hides that 2 of 5 models have math errors
            as their dominant failure mode. ChatGPT is assumption-dominated (25/38 of its failures
            are assumption violations); Claude and Mistral are math-dominated; DeepSeek is mixed;
            Gemini is balanced. This is the actionable cross-cutting pattern beneath the cohort
            average.
          </p>
          <PerModelFailuresPanel />
        </FadeIn>

        {/* 4.5 — Per-dim robustness panel */}
        <FadeIn delay={195}>
          <ExpandablePanel title="Per-dimension robustness"><PerDimRobustnessPanel /></ExpandablePanel>
        </FadeIn>

        {/* 5 — Statistical validation (visualization-first) */}
        <FadeIn delay={210}>
          <Subhead>5 · Statistical Validation</Subhead>
          <ExpandablePanel title="Bootstrap CI validation"><BootstrapValidationPanel /></ExpandablePanel>
          <ExpandablePanel title="Krippendorff α validation"><AlphaValidationPanel /></ExpandablePanel>
          <ExpandablePanel title="Tolerance sensitivity"><ToleranceValidationPanel /></ExpandablePanel>
        </FadeIn>

        {/* 6 — Calibration is method-dependent (visualization-first) */}
        <FadeIn delay={240}>
          <Subhead>6 · Calibration is method-dependent</Subhead>
          <ExpandablePanel title="Calibration method comparison"><CalibrationMethodComparisonPanel /></ExpandablePanel>
          <ExpandablePanel title="Per-dimension calibration ECE"><PerDimCalibrationPanel /></ExpandablePanel>
        </FadeIn>

        {/* 7 — Eligibility filters / disclosures (visualization-first) */}
        <FadeIn delay={270}>
          <Subhead>7 · Eligibility filters and disclosures</Subhead>
          <ExpandablePanel title="Eligibility filters funnel"><EligibilityFunnelPanel /></ExpandablePanel>
        </FadeIn>

        {/* 8 — Literature convergence */}
        <FadeIn delay={300}>
          <Subhead>8 · Literature convergence (six anchors)</Subhead>
          <Card>
            <ul style={{ margin: 0, padding: 0, listStyle: 'none' }}>
              {LITERATURE_CONVERGENCE.map((s, i) => (
                <li key={i} style={{
                  display: 'flex', gap: 14, alignItems: 'flex-start',
                  padding: '10px 0',
                  borderBottom: i < LITERATURE_CONVERGENCE.length - 1 ? '1px solid rgba(0,255,224,0.10)' : 'none',
                }}>
                  <span style={{
                    color: '#00FFE0', fontFamily: 'monospace', fontSize: 12, fontWeight: 800,
                    minWidth: 28, lineHeight: 1.6,
                  }}>{i + 1}.</span>
                  <span style={{ color: 'rgba(232,244,248,0.85)', fontSize: 13, lineHeight: 1.7 }}>{s}</span>
                </li>
              ))}
            </ul>
          </Card>
        </FadeIn>

        {/* 9 — Literature comparison table */}
        <FadeIn delay={330}>
          <Subhead>9 · Literature comparison</Subhead>
          <Card>
            <p style={{ color: 'rgba(232,244,248,0.7)', fontSize: 12, lineHeight: 1.7, margin: '0 0 16px' }}>
              7 prior systems × 11 dimensions. The <span style={{ color: '#00FFE0', fontWeight: 700 }}>THIS WORK</span> column is highlighted.
            </p>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 11 }}>
                <thead>
                  <tr>
                    {LIT_TABLE.cols.map((c, i) => (
                      <th key={i} style={{
                        textAlign: 'left',
                        padding: '8px 10px',
                        borderBottom: '1px solid rgba(0,255,224,0.25)',
                        color: i === LIT_TABLE.cols.length - 1 ? '#00FFE0' : 'rgba(232,244,248,0.55)',
                        fontWeight: 700,
                        whiteSpace: 'nowrap',
                        background: i === LIT_TABLE.cols.length - 1 ? 'rgba(0,255,224,0.07)' : 'transparent',
                      }}>{c}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {LIT_TABLE.rows.map((row, ri) => (
                    <tr key={ri}>
                      {row.map((cell, ci) => {
                        const isLast = ci === row.length - 1
                        const isFirst = ci === 0
                        return (
                          <td key={ci} style={{
                            padding: '7px 10px',
                            borderBottom: '1px solid rgba(255,255,255,0.05)',
                            color: isLast ? '#00FFE0' : isFirst ? 'rgba(232,244,248,0.85)' : 'rgba(232,244,248,0.6)',
                            fontWeight: isLast || isFirst ? 600 : 400,
                            background: isLast ? 'rgba(0,255,224,0.05)' : 'transparent',
                            whiteSpace: 'nowrap',
                          }}>{cell}</td>
                        )
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </FadeIn>
      </div>
    </section>
  )
}
