import { useRef } from 'react'
import { motion, useInView } from 'motion/react'
import {
  PerModelPassFlipPanel, KeywordDegradationPanel, PerDimRobustnessPanel,
  PerDimCalibrationPanel, AccCalibScatterPanel,
} from '../components/MethodologyPanels'

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

const PER_MODEL_FAILURE = [
  { model: 'ChatGPT',  dominant: 'Assumption violation', n_dom: 25, n_total: 38, breakdown: 'A 25 · M-error 4 · Format 6 · Conceptual 3', color: '#7FFFD4' },
  { model: 'Claude',   dominant: 'Math error',           n_dom: 10, n_total: 19, breakdown: 'M-error 10 · A 9',                              color: '#00CED1' },
  { model: 'Gemini',   dominant: 'Balanced split',       n_dom: 10, n_total: 24, breakdown: 'A 10 · M-error 9 · Conceptual 4 · Format 1',    color: '#FF6B6B' },
  { model: 'DeepSeek', dominant: 'Mixed (A + math)',     n_dom: 15, n_total: 36, breakdown: 'A 15 · M-error 13 · Format 6 · Conceptual 2',   color: '#4A90D9' },
  { model: 'Mistral',  dominant: 'Math error',           n_dom: 12, n_total: 26, breakdown: 'M-error 12 · A 8 · Format 5 · Conceptual 1',    color: '#A78BFA' },
]

const PERT_TYPE = [
  { kind: 'rephrase',   pct: 21.6, n: 162, total: 750 },
  { kind: 'numerical',  pct: 22.7, n: 136, total: 600 },
  { kind: 'semantic',   pct: 18.1, n: 136, total: 750 },
]

const LITERATURE_CONVERGENCE = [
  'Multi-dimensional rubrics (vs single accuracy) per Lu et al. (2025), Liu et al. (2025), and Boye & Moell (2025) — our N·M·A·C·R rubric extends this convention to Bayesian inference.',
  'Bootstrap CI separability of rankings is a methodological mandate per Longjohn et al. (2025), Hochlehnert et al. (2025), Au et al. (2025), and BrittleBench (2026) — our separability matrix follows this convention.',
  'Variance-as-first-class evaluation (not just accuracy) per Au et al. (2025), BrittleBench (2026), and Hochlehnert et al. (2025) — our three-rankings framework directly implements this framing.',
  'Verbalized confidence is unreliable for calibration per Nagarkar et al. (2026), FermiEval (2025), and Multi-Answer Confidence (2026) — our Gemini-zero-verbalized-signals finding confirms this in the Bayesian setting.',
  'Three-way convergence on assumption violations as primary failure mode: Du et al. (2025), Boye & Moell (2025), and our 46.9% empirical finding independently agree.',
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
          <Card>
            <p style={{ color: 'rgba(232,244,248,0.85)', fontSize: 14, lineHeight: 1.85, margin: 0 }}>
              This benchmark extends StatEval (Lu et al., 2025) from descriptive and hypothesis-testing
              statistics to Bayesian inference. Where StatEval uses multiple-choice format, we adopt
              free-response with a 5-dimensional rubric (N·M·A·C·R) following the multi-dimensional
              convention of MathEval (Liu et al., 2025). Our prompting baseline is the single shipped
              strategy: zero-shot Chain-of-Thought (Wei et al., 2022). Methodology rigour combines
              external-judge validation via Llama 3.3 70B (Yamauchi et al., 2025), bootstrap-CI
              separability motivated by Statistical Fragility (Hochlehnert et al., 2025) and Longjohn
              et al. (2025), perturbation robustness adapted from BrittleBench (2026), and the
              variance-as-first-class framing of ReasonBench (Au et al., 2025). Calibration concerns
              are raised by Nagarkar et al. (2026); we measure both verbalized and consistency-based
              extraction (Multi-Answer Confidence, 2026) and find calibration is method-dependent.
              Limitations around single-judge bias are framed by Judgment-Becomes-Noise (Feuer et al.,
              2025); future work toward multi-judge ensembling is explicitly scoped.
            </p>
          </Card>
        </FadeIn>

        {/* 2 — N·M·A·C·R Rubric */}
        <FadeIn delay={100}>
          <Subhead>2 · N·M·A·C·R Rubric (literature-derived weights)</Subhead>
          <Card>
            <p style={{ color: 'rgba(232,244,248,0.78)', fontSize: 13, lineHeight: 1.85, margin: '0 0 14px' }}>
              The N·M·A·C·R rubric uses literature-derived weights rather than equal weighting.
              Assumption articulation (A=30%) is weighted highest because three independent literature
              lines converge on assumption violations as the dominant failure mode in statistical
              reasoning evaluation: Du et al. (2025) identifies assumption violations as the primary
              failure mode in LLM causal-statistical reasoning; Boye &amp; Moell (2025) lists
              "unwarranted assumptions" as failure mode #1; Yamauchi et al. (2025) finds
              assumption_compliance is the dimension where keyword and external-judge raters diverge
              most. Reasoning quality (R=25%) is weighted second because Yamauchi et al. (2025)
              identifies it as the dimension where external-judge evaluation adds most value over
              keyword scoring. Method selection (M=20%) is weighted moderately because Wei et al.
              (2022) and Chen et al. (2022) establish method articulation as central but partially
              redundant with reasoning quality. Confidence calibration (C=15%) and numerical
              correctness (N=10%) are weighted lower because calibration is treated as a separate
              evaluation track in the field (Nagarkar 2026, FermiEval 2025) and numerical correctness
              is the dimension that needs least sophisticated evaluation (Liu 2025) — anyone with a
              calculator can verify a number.
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 14 }}>
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
              <strong>Aggregation locus:</strong> the runtime parser
              (<code style={{ fontSize: 10 }}>llm_runner/response_parser.py</code>) and post-hoc metric
              path (<code style={{ fontSize: 10 }}>evaluation/metrics.py</code>) remain locked at equal
              0.20 weights for v1 reproducibility. Phase 1B literature weights apply via a wrapper
              recompute (<code style={{ fontSize: 10 }}>scripts/recompute_nmacr.py</code>) producing
              <code style={{ fontSize: 10 }}> nmacr_scores_v2.jsonl</code> — the single source of truth
              for the literature-weighted aggregate. CONCEPTUAL tasks (no N) renormalize remaining
              weights to 1.0; mirrors runtime <code style={{ fontSize: 10 }}>full_score()</code>.
            </p>
          </Card>
        </FadeIn>

        {/* 3 — Llama judge + keyword-degradation */}
        <FadeIn delay={150}>
          <Subhead>3 · External Llama Judge</Subhead>
          <Card>
            <p style={{ color: 'rgba(232,244,248,0.85)', fontSize: 14, lineHeight: 1.8, margin: '0 0 12px' }}>
              <strong style={{ color: '#fff' }}>Why Llama 3.3 70B Instruct (via Together AI).</strong>{' '}
              The judge is a sixth model, deliberately external to the five benchmarked
              (Claude / GPT-4.1 / Gemini / DeepSeek / Mistral). Using one of the benchmarked models
              as judge would introduce self-preference bias (cf. Yamauchi et al., 2025; Feuer et al.,
              2025). Cross-provider agreement was spot-checked against Groq's Llama endpoint.
            </p>
            <p style={{ color: 'rgba(232,244,248,0.75)', fontSize: 13, lineHeight: 1.75, margin: '0 0 14px' }}>
              The judge produces a 4-dimensional rubric per response (numerical, method,
              assumption, reasoning quality + completeness). Krippendorff α between keyword and
              judge: assumption_compliance α = 0.55 (95% CI [0.50, 0.60], questionable per Park et al.
              2025); reasoning_quality α = -0.13 (CI entirely below zero); method_structure α = -0.04.
              Combined pass-flip across 1,095 base + 2,100 perturbation runs: 708 / 3,195 = 22.2%.
            </p>
            <Callout color="#00B4D8" title="Keyword vs judge under perturbation">
              Across the 3,195 eligible runs sharing the assumption-compliance rubric, keyword
              scoring degrades faster than LLM-judge under perturbation, with the two methods
              moving in opposite directions: keyword PASS rate drops from 68.7% (base) to 66.8%
              (perturbation, −1.9pp), while LLM-judge PASS rate rises from 48.6% to 50.4% (+1.8pp).
              The 3.7pp differential indicates that surface-form changes — rephrasing, numerical
              reseeding, semantic reframing — disproportionately break keyword regex matches,
              whereas the LLM-judge tracks the underlying mathematical content more robustly. The
              effect is largest on semantic perturbations (5.96pp differential), where vocabulary
              changes disrupt keyword matching most aggressively. This provides direct empirical
              support for LLM-as-judge as the canonical assumption-compliance metric in robustness
              evaluation, where the goal is to measure reasoning competence independent of surface
              phrasing.
            </Callout>
            <KeywordDegradationPanel />
            <Callout color="#FF6B6B" title="α is NEGATIVE on R and M">
              Krippendorff α reports systematic disagreement (not just weak agreement) on
              reasoning_quality (α = −0.133, 95% CI [−0.228, −0.039] entirely below zero) and
              method_structure (α = −0.042). Negative α means raters pull in opposite directions
              — keyword and judge reasoning rubrics do worse than chance on these two dimensions.
              On assumption_compliance, α = 0.55 (questionable). Three of four shared dimensions
              show keyword/judge divergence, not one.
            </Callout>
            <p style={{ color: 'rgba(232,244,248,0.7)', fontSize: 12, lineHeight: 1.7, margin: '14px 0 0' }}>
              Per-perturbation-type pass-flip: rephrase 21.6% (162/750), numerical 22.7% (136/600),
              semantic 18.1% (136/750). Numerical perturbations expose assumption-checking gaps
              most aggressively; semantic reframing exposes them least.
            </p>
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

        {/* 3.5 — Per-model pass-flip panel */}
        <FadeIn delay={165}>
          <PerModelPassFlipPanel />
        </FadeIn>

        {/* 4 — Per-model failure modes */}
        <FadeIn delay={180}>
          <Subhead>4 · Per-model failure modes</Subhead>
          <Card>
            <p style={{ color: 'rgba(232,244,248,0.78)', fontSize: 13, lineHeight: 1.75, margin: '0 0 14px' }}>
              The 46.9% assumption-violation headline (RQ3) hides that 2 of 5 models have math errors
              as their dominant failure mode. ChatGPT is assumption-dominated (25/38 of its failures
              are assumption violations); Claude and Mistral are math-dominated; DeepSeek is mixed;
              Gemini is balanced. This is the actionable cross-cutting pattern beneath the cohort
              average.
            </p>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
                <thead>
                  <tr>
                    {['Model', 'Dominant mode', 'Dominant / total', 'Full breakdown'].map(c => (
                      <th key={c} style={{ textAlign: 'left', padding: '8px 10px', borderBottom: '1px solid rgba(0,255,224,0.25)', color: 'rgba(232,244,248,0.55)', fontWeight: 700 }}>{c}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {PER_MODEL_FAILURE.map(m => (
                    <tr key={m.model}>
                      <td style={{ padding: '8px 10px', color: m.color, fontWeight: 700 }}>{m.model}</td>
                      <td style={{ padding: '8px 10px', color: '#fff' }}>{m.dominant}</td>
                      <td style={{ padding: '8px 10px', color: 'rgba(232,244,248,0.7)', fontFamily: 'monospace' }}>{m.n_dom} / {m.n_total}</td>
                      <td style={{ padding: '8px 10px', color: 'rgba(232,244,248,0.6)', fontSize: 11 }}>{m.breakdown}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </FadeIn>

        {/* 4.5 — Per-dim robustness panel */}
        <FadeIn delay={195}>
          <PerDimRobustnessPanel />
        </FadeIn>

        {/* 5 — Statistical validation + tolerance */}
        <FadeIn delay={210}>
          <Subhead>5 · Statistical Validation</Subhead>
          <Card>
            <div style={{ marginBottom: 14 }}>
              <strong style={{ color: '#00FFE0', fontSize: 13 }}>Bootstrap CI separability.</strong>
              <p style={{ color: 'rgba(232,244,248,0.75)', fontSize: 13, lineHeight: 1.75, margin: '4px 0 0' }}>
                10,000 bootstrap resamples per model, seed=42, percentile method. Under
                literature-derived NMACR weights, accuracy means are Gemini 0.776 [0.753, 0.799],
                Claude 0.712 [0.689, 0.736], ChatGPT 0.691 [0.668, 0.715], Mistral 0.675
                [0.652, 0.699], DeepSeek 0.663 [0.639, 0.686]. Gemini is separable from #2 Claude
                under literature weights. Robustness CIs cross zero for ChatGPT and Mistral only —
                effectively noise-equivalent, statistically indistinguishable from "no robustness
                deficit." (Hochlehnert et al., 2025, Statistical Fragility.)
              </p>
            </div>
            <div style={{ marginBottom: 14 }}>
              <strong style={{ color: '#00FFE0', fontSize: 13 }}>Krippendorff α inter-rater reliability.</strong>
              <p style={{ color: 'rgba(232,244,248,0.75)', fontSize: 13, lineHeight: 1.75, margin: '4px 0 0' }}>
                Adopted over Spearman ρ on the recommendation of Park et al. (2025): α handles
                missing data, multiple raters, and ordinal-vs-nominal scales correctly. Bootstrap
                B=1000, seed=42. Thresholds: α &gt; 0.8 strong, ≥ 0.667 acceptable, &lt; 0.667
                questionable. All three shared dims (assumption, reasoning, method) score
                "questionable"; reasoning and method specifically negative.
              </p>
            </div>
            <div>
              <strong style={{ color: '#00FFE0', fontSize: 13 }}>Tolerance sensitivity.</strong>
              <p style={{ color: 'rgba(232,244,248,0.75)', fontSize: 13, lineHeight: 1.75, margin: '4px 0 0' }}>
                Accuracy at task-specified tolerances vs tight (0.005, 0.025) / default (0.010,
                0.050) / loose (0.020, 0.100) sweeps. Rankings shift across levels — Gemini swings
                from worst at tight to mid at loose. Bayesian closed-form numerics are
                tolerance-sensitive at the boundary, not numerically fragile within typical bounds.
              </p>
            </div>
          </Card>
        </FadeIn>

        {/* 6 — Calibration is method-dependent */}
        <FadeIn delay={240}>
          <Subhead>6 · Calibration is method-dependent</Subhead>
          <Card>
            <p style={{ color: 'rgba(232,244,248,0.78)', fontSize: 13, lineHeight: 1.75, margin: '0 0 12px' }}>
              We measure calibration two ways and find substantively different conclusions.
              Verbalized extraction (n=246 base/model) is hedge-heavy: ECE 0.06–0.18, no model
              produces high-confidence (p ≥ 0.85) records. Phase 1C consistency extraction (3 reruns
              at T=0.7, n=161 numeric tasks × 5 models) reveals all 5 models severely overconfident
              under consistency: ECE 0.62–0.73.
            </p>
            <Callout color="#FF6B6B" title="Gemini calibration inversion">
              Gemini produces 0 verbalized confidence signals across 246 base runs (excluded from
              accuracy-calibration correlation) but produces 58 high-consistency runs and has the
              BEST consistency ECE (0.618). Same model, opposite calibration extremes depending on
              extraction method. Calibration measurement is method-dependent.
            </Callout>
            <PerDimCalibrationPanel />
            <p style={{ color: 'rgba(232,244,248,0.7)', fontSize: 12, lineHeight: 1.7, margin: '14px 0 0' }}>
              <strong>Accuracy-calibration correlation (RQ5 Layer 4):</strong> Pearson r between
              per-task aggregate (literature-weighted NMACR) and per-task confidence (dim_C):
              Claude 0.49, Mistral 0.48, ChatGPT 0.37, DeepSeek 0.35; Gemini not measurable
              (all 246 verbalized responses unstated). Honest interpretation: well-calibrated does
              not mean accurate; it means hedging behaviour tracks task difficulty.
            </p>
          </Card>
        </FadeIn>

        {/* 6.5 — Accuracy-calibration scatter panel */}
        <FadeIn delay={255}>
          <AccCalibScatterPanel />
        </FadeIn>

        {/* 7 — Eligibility filters / disclosures */}
        <FadeIn delay={270}>
          <Subhead>7 · Eligibility filters and disclosures</Subhead>
          <Card>
            <p style={{ color: 'rgba(232,244,248,0.78)', fontSize: 13, lineHeight: 1.75, margin: 0 }}>
              Pass-flip is computed on 1,095 of 1,230 base runs. The 135 excluded runs come from
              CONCEPTUAL/MINIMAX/BAYES_RISK task families with empty
              <code style={{ fontSize: 11 }}> required_assumption_checks</code> — keyword and judge
              scoring of assumption articulation cannot be compared on tasks that don't require
              assumption articulation.
            </p>
            <p style={{ color: 'rgba(232,244,248,0.78)', fontSize: 13, lineHeight: 1.75, margin: '10px 0 0' }}>
              Self-consistency calibration is computed on 161 of 171 tasks. The 10 CONCEPTUAL
              tasks are excluded because consistency-rate measurement requires numerical answers,
              which conceptual tasks don't have.
            </p>
            <p style={{ color: 'rgba(232,244,248,0.78)', fontSize: 13, lineHeight: 1.75, margin: '10px 0 0' }}>
              Error taxonomy is computed on 143 base failures classified by the Llama 3.3 70B
              judge. FORMATTING_FAILURE (18 / 143 = 12.6%) is reported separately as
              <code style={{ fontSize: 11 }}> formatting_failure_rate_per_model</code> and excluded
              from N·M·A·C·R aggregation by design — formatting glitches are orthogonal to
              substantive Bayesian reasoning.
            </p>
          </Card>
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
