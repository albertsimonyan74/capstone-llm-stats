import { useRef } from 'react'
import { motion, useInView } from 'motion/react'

const CAVEATS = [
  {
    title: 'Empty HALLUCINATION bucket',
    body: `The error taxonomy returned zero HALLUCINATION classifications across all 143 audited
    failures. This is a real signal, not a missing case: every benchmark task has a closed-form
    or seeded ground truth, so models fail by skipping required assumptions or miscomputing —
    not by fabricating priors, distributions, or data. Llama 3.3 70B may still under-surface
    hallucination on well-constrained tasks (E5/E8/E9 are flagged "use only if nothing else
    fits"), so the 0% rate is partly methodology artifact and partly a property of bounded
    numerical Bayesian problems.`,
  },
  {
    title: 'Empty high-confidence bucket (verbalized) — Gemini specifically zero-signal',
    body: `All five models produced 0 responses classified as high-confidence (claimed p ≥ 0.85)
    by the keyword-based extractor, leaving the 0.9 ECE bucket empty. Reported verbalized ECE
    values (0.06–0.18) are weighted MAEs over three populated buckets (0.3 / 0.5 / 0.6) — they
    capture calibration across the low-to-moderate confidence range only. Gemini specifically
    returned 0 verbalized confidence signals across 246 base runs and is excluded from the
    accuracy-calibration correlation. Phase 1C consistency extraction recovers a calibration
    estimate for Gemini (best of cohort, ECE 0.618). True probabilistic calibration requires
    token-level logprobs, not uniformly available across the 5 vendor APIs.`,
  },
  {
    title: 'Robustness top-2 not separable (ChatGPT/Mistral only)',
    body: `Robustness CIs cross zero for ChatGPT (Δ = 0.011 [−0.001, 0.024]) and Mistral
    (Δ = 0.007 [−0.006, 0.019]) — these two models are statistically indistinguishable from
    "no robustness deficit at all." The other three (Claude, Gemini, DeepSeek) have CIs
    separable from zero. Under literature-derived NMACR weights, accuracy is now separable
    on the top-2 (Gemini 0.776 vs Claude 0.712), so this caveat applies to robustness only.
    Cite Statistical Fragility (Hochlehnert et al., 2025): single-question swaps shift Pass@1
    ≥ 3 pp.`,
  },
  {
    title: 'Single-judge limitation (model AND prompt template)',
    body: `The combined 22.2% keyword-judge disagreement headline rests on a single external
    judge — Llama 3.3 70B Instruct via Together AI — with a single prompt template. Yamauchi et
    al. (2025) report that judge-prompt template choices have larger effects than judge-model
    choices; this design addresses model choice (5 distinct providers + 1 external judge family)
    but not template variance. Cross-provider agreement (Groq vs Together) was verified and
    strictness spot-checks were run on borderline cases; true cross-judge validation against an
    independent family (e.g., GPT-4 class or Claude Opus as judge) and multi-template ensembling
    are paper-scope future work. Cite Feuer et al. (2025) "Judgment Becomes Noise" for the
    systematic-noise framing; the 5-provider design is the architectural counter-design to
    family-preference bias.`,
  },
  {
    title: 'B3 stratification — RESOLVED via Phase 1C',
    body: `The original B3 self-consistency analysis used 30 stratified-hard tasks and found ECE
    values in the 0.33–0.64 range. Phase 1C expanded coverage to all 161 numeric-target tasks
    and found ECE values in the 0.62–0.73 range — HIGHER under full coverage. The stratified B3
    was UNDERSTATING overconfidence, not overstating it. The full-coverage finding is the
    canonical RQ5 result; B3 stratified data is preserved in
    llm-stats-vault/90-archive/phase_1c_superseded/. Claude's stratified estimate was the most
    misleading: 0.33 → 0.73 (+0.40 ECE delta).`,
  },
  {
    title: '135-task keyword-judge disagreement exclusion (CONCEPTUAL / MINIMAX / BAYES_RISK)',
    body: `Keyword-judge disagreement is computed on 1,095 of 1,230 base runs. The 135 excluded runs come from
    CONCEPTUAL/MINIMAX/BAYES_RISK task families with empty required_assumption_checks —
    keyword and judge scoring of assumption articulation cannot be compared on tasks that don't
    require assumption articulation. The same eligibility filter applies to the 2,100 of 2,365
    perturbation runs in the combined denominator (3,195 / 3,595).`,
  },
  {
    title: '10-task CONCEPTUAL exclusion from self-consistency',
    body: `Self-consistency calibration is computed on 161 of 171 tasks. The 10 CONCEPTUAL tasks
    (CONCEPTUAL_01–10) ask the model to explain or justify rather than compute — they have no
    numerical answer against which to measure 3-rerun agreement. This is a methodological
    property of consistency-based confidence extraction, not a project shortcut. Token-level
    logprobs (Multi-Answer Confidence 2026) would be required to extend calibration analysis
    to free-form explanatory tasks.`,
  },
  {
    title: 'Length-correlation in RQ scoring (Gemini verification)',
    body: `Gemini's reasoning_quality lead under literature-derived NMACR weighting (R=25%) is
    supported by 5/5 substantive hand-spot-checks and a uniformly distributed advantage across
    34/38 task types. However, the rubric design rewards step-by-step derivation, which
    correlates with response length: Gemini averages 2.4× the cohort response length. Pooled
    length–RQ Pearson r = 0.184 (weak); within-Gemini length–RQ r = 0.012 (effectively zero),
    indicating length does not drive Gemini's own variance. Length-controlled per-task analysis
    and a multi-judge ensemble are recommended methodology refinements deferred to future work.`,
  },
  {
    title: 'NMACR literature-derived weighting (post-hoc risk acknowledged)',
    body: `The N·M·A·C·R weights (A=0.30, R=0.25, M=0.20, C=0.15, N=0.10) were chosen based on
    prior literature predating this benchmark's data, not derived from the data itself.
    Citations: Du 2025, Boye & Moell 2025, and Yamauchi 2025 for A; Yamauchi 2025 and Au 2025
    for R; Wei 2022, Chen 2022, and Bishop 2006 for M; Nagarkar 2026, FermiEval 2025, and
    Multi-Answer Confidence 2026 for C; Liu 2025 and Boye & Moell 2025 for N. The runtime
    aggregation paths remain at equal 0.20 weights for v1 reproducibility; literature weights
    apply only via the Phase 1B recompute wrapper. Both schemes are honestly disclosed; the
    literature scheme is the canonical aggregate.`,
  },
  {
    title: 'PoT prompting explored but not in scored runs',
    body: `Program-of-Thoughts (Chen et al., 2022) prompting was implemented in scripts/ as
    exploratory code but is not part of the scored benchmark runs. The single shipped prompting
    strategy is zero-shot Chain-of-Thought (Wei et al., 2022). PoT is a paper-scope future
    work axis along with multi-judge ensembling and length-controlled per-task analysis; the
    canonical baseline shipping in this work is zero-shot CoT only.`,
  },
]

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

export default function Limitations() {
  return (
    <section id="limitations" style={{ padding: '96px 24px 80px', position: 'relative', zIndex: 1 }}>
      <div style={{ maxWidth: 1100, margin: '0 auto' }}>
        <FadeIn>
          <div style={{ color: 'rgba(255,184,71,0.65)', fontSize: 10, fontWeight: 700, letterSpacing: '0.2em', marginBottom: 8 }}>
            // HONEST DISCLOSURES · NOT FAILURES
          </div>
          <h2 style={{ fontSize: 'clamp(28px,3.5vw,42px)', fontWeight: 700, color: '#fff', margin: '0 0 8px', lineHeight: 1.2 }}>
            Limitations
          </h2>
          <div style={{ width: 64, height: 3, background: 'linear-gradient(90deg,#FFB347,#FF9A3C)', borderRadius: 2, marginBottom: 32 }} />
          <p style={{ color: 'rgba(232,244,248,0.7)', fontSize: 14, lineHeight: 1.75, maxWidth: 800, marginBottom: 28 }}>
            Ten caveats the methodology requires us to disclose. Each is a property of the design,
            not a bug. Read them as the boundary of what the headline numbers can and cannot
            claim.
          </p>
        </FadeIn>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 16 }}>
          {CAVEATS.map((c, i) => (
            <FadeIn key={i} delay={60 * i}>
              <div style={{
                background: 'rgba(255,184,71,0.04)',
                border: '1px solid rgba(255,184,71,0.25)',
                borderLeft: '4px solid #FFB347',
                borderRadius: 10,
                padding: '20px 26px',
              }}>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: 14, marginBottom: 10 }}>
                  <span style={{
                    color: '#FFB347', fontFamily: 'monospace', fontSize: 14, fontWeight: 800,
                  }}>L{i + 1}</span>
                  <span style={{ color: '#fff', fontSize: 16, fontWeight: 700 }}>{c.title}</span>
                </div>
                <p style={{ color: 'rgba(232,244,248,0.78)', fontSize: 13, lineHeight: 1.8, margin: 0 }}>
                  {c.body}
                </p>
              </div>
            </FadeIn>
          ))}
        </div>
      </div>
    </section>
  )
}
