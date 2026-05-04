import { useEffect, useState } from 'react'
import { motion } from 'motion/react'

const API = import.meta.env.VITE_API_URL || ''

// Canonical numbers post Phase 1.8 v1 deprecation (2026-05-04) — used as static fallback if API is unreachable.
const STATIC_FALLBACK = {
  pass_flip_rate: 0.2074,
  pass_flip_n: 591,
  pass_flip_total: 2850,
  krippendorff_alpha_assumption: 0.573,
  krippendorff_alpha_rq: -0.125,
  krippendorff_alpha_method: -0.009,
  krippendorff_alpha_n: 750,
  dominant_failure_pct: 0.469,
  dominant_failure_n: 67,
  dominant_failure_total: 143,
  rankings: {
    accuracy_top: 'gemini',
    accuracy_top_score: 0.7314,
    robustness_top: 'chatgpt',
    calibration_top: 'claude',
  },
  ece_consistency_min: 0.62,
  ece_consistency_max: 0.73,
  ece_consistency_gemini: 0.618,
}

const COLORS = ['#00FFE0', '#7FFFD4', '#A78BFA', '#FFB347', '#00B4D8', '#4A90D9']

function buildCards(d, pf) {
  const flipPct = pf?.combined?.pct_pass_flip != null
    ? (pf.combined.pct_pass_flip * 100).toFixed(1)
    : (d.pass_flip_rate * 100).toFixed(1)
  const flipN = pf?.combined?.n_pass_flip ?? d.pass_flip_n
  const flipTotal = pf?.combined?.n_eligible ?? d.pass_flip_total

  const alphaA = (d.krippendorff_alpha_assumption ?? d.krippendorff_alpha)?.toFixed?.(2) ?? '0.57'

  return [
    {
      big: '1 in 5',
      label: 'Simple scoring overlooks bad reasoning',
      desc: `Across ${flipTotal.toLocaleString()} evaluable runs (750 base + 2,100 perturbations), the keyword scorer and LLM judge disagreed on ${flipPct}% (${flipN.toLocaleString()}) of cases — keyword said the response passed, judge said it failed. The disagreement holds under prompt rewording — a robustness finding for the methodology.`,
      why: 'Most LLM benchmarks score by keyword-matching alone. Analysis across multiple prompt variants shows this approach systematically misses bad reasoning at a measurable rate.',
    },
    {
      big: 'α = -0.125 to 0.57',
      label: 'Two scoring methods give different answers',
      desc: `Krippendorff agreement on assumption articulation is ${alphaA} (n=750). On reasoning_quality, the agreement is NEGATIVE (α=−0.125, 95% CI [−0.197, −0.059] excludes zero) — the two methods disagree more than they would by chance. On method_structure, agreement is essentially chance-level (α=−0.009, CI [−0.072, +0.062] contains zero) — the methods cannot be claimed to align. The reasoning disagreement is structural, not noise.`,
      why: "Confirms the 1-in-5 finding above isn't a fluke. The two scoring methods genuinely measure different things on reasoning_quality. On method_structure they're essentially chance-level — neither aligned nor systematically opposed.",
    },
    {
      big: 'Almost half',
      label: 'Models skip the reasoning, not the math',
      desc: `Across ${d.dominant_failure_total ?? 143} audited failures, ${d.dominant_failure_n ?? 67} (${((d.dominant_failure_pct ?? 0.469) * 100).toFixed(1)}%) were classified as assumption violations — gaps in articulating priors, distributions, or independence structure. By contrast, 48 (33.6%) were classified as math errors. The primary failure mode is reasoning, not computation.`,
      why: "When LLMs fail at Bayesian reasoning, it's usually not because they can't compute — it's because they skip the reasoning steps. This is the silent failure mode.",
    },
    {
      big: 'Gemini #1',
      label: "The 'best' model on accuracy under literature-weighted NMACR",
      desc: 'Gemini ranks #1 on accuracy with mean 0.7314 [0.7060, 0.7565] under the literature-weighted NMACR scheme (A=30%, R=25%, M=20%, C=15%, N=10%). Claude #2 at 0.6976 [0.6694, 0.7249] — a 3.4pp lead. The dimensional weighting follows Du 2025, Boye-Moell 2025, and Yamauchi 2025.',
      why: 'Benchmark rankings depend on the choice of dimensional weighting. The literature-derived scheme reflects what published research identifies as evaluation priorities for LLMs on Bayesian reasoning.',
    },
    {
      big: '3 different rankings',
      label: 'Accuracy, robustness, calibration disagree',
      desc: 'Ranking models on accuracy, robustness, and calibration produces three completely different leaderboards. Gemini wins accuracy (0.7314). ChatGPT and Mistral are statistically tied at the top of robustness (Δ=+0.0003 and +0.0013 respectively — both noise-equivalent, CIs cross zero). Claude and ChatGPT essentially tie on calibration (verbalized ECE 0.033 / 0.034). No single model dominates across all three axes.',
      why: "Single-number leaderboards mislead. The same data tells three different stories about which model is 'best.'",
    },
    {
      big: 'All overconfident',
      label: 'Models think they\'re right when they\'re wrong',
      desc: "When a model gives the same answer 3 times in a row (confident agreement), it's still wrong about 60-70% of the time on hard tasks. Across 161 numerical-answer tasks, ECE scores range from 0.62 to 0.73 for all 5 models. All five models are severely overconfident under self-consistency extraction, despite appearing well-calibrated by verbalized measurement (ECE 0.06–0.18). Calibration is method-dependent.",
      why: "'Confidence' doesn't mean 'correctness' for current LLMs on Bayesian reasoning. Calibration is method-dependent.",
    },
  ]
}

function staticCards() {
  return buildCards(STATIC_FALLBACK, {
    combined: {
      pct_pass_flip: STATIC_FALLBACK.pass_flip_rate,
      n_pass_flip: STATIC_FALLBACK.pass_flip_n,
      n_eligible: STATIC_FALLBACK.pass_flip_total,
    },
  })
}

// Hook: returns { cards, loading }
export function useKeyFindings() {
  const [cards, setCards] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/v2/headline_numbers`).then(r => r.ok ? r.json() : Promise.reject()),
      fetch(`${API}/api/v2/pass_flip`).then(r => r.ok ? r.json() : null).catch(() => null),
    ])
      .then(([hn, pf]) => { setCards(buildCards(hn, pf)); setLoading(false) })
      .catch(() => { setCards(staticCards()); setLoading(false) })
  }, [])

  return { cards: cards || staticCards(), loading }
}

// Single card renderer — exported so App.jsx can interleave with viz
export function KeyFindingCard({ card, index, hero = false, loading = false }) {
  const color = COLORS[index % COLORS.length]
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.04 * index, duration: 0.45 }}
      style={{
        border: `1px solid ${color}33`,
        borderTop: `3px solid ${color}`,
        borderRadius: 12,
        padding: '20px 20px 18px',
        background: `${color}08`,
        opacity: loading ? 0.55 : 1,
        transition: 'opacity 0.3s',
        height: '100%',
        boxSizing: 'border-box',
      }}
    >
      <div style={{
        fontFamily: 'monospace', color,
        fontSize: hero ? 38 : 26, fontWeight: 800, lineHeight: 1.05, marginBottom: 8,
      }}>
        {card.big}
      </div>
      <div style={{
        color: 'rgba(232,244,248,0.9)', fontSize: hero ? 15 : 13, fontWeight: 700,
        marginBottom: 10, lineHeight: 1.35,
      }}>
        {card.label}
      </div>
      <div style={{ color: 'rgba(232,244,248,0.78)', fontSize: 12, lineHeight: 1.6, marginBottom: 10 }}>
        {card.desc}
      </div>
      {card.why && (
        <div style={{
          borderTop: `1px solid ${color}22`,
          paddingTop: 10,
          fontSize: 11,
          color: 'rgba(232,244,248,0.55)',
          lineHeight: 1.55,
          fontStyle: 'italic',
        }}>
          <span style={{ color, fontWeight: 700, fontStyle: 'normal', letterSpacing: '0.08em', textTransform: 'uppercase', fontSize: 9, marginRight: 6 }}>
            Why it matters
          </span>
          {card.why}
        </div>
      )}
    </motion.div>
  )
}

// Original block-rendered version — preserved as default export for backward compat
export default function KeyFindings() {
  const { cards, loading } = useKeyFindings()

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
      gap: 14,
      maxWidth: 1300, margin: '0 auto 32px',
    }}>
      {cards.map((c, i) => (
        <div key={i} style={{ gridColumn: i === 0 ? '1 / -1' : 'auto' }}>
          <KeyFindingCard card={c} index={i} hero={i === 0} loading={loading} />
        </div>
      ))}
    </div>
  )
}
