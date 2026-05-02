import { useEffect, useState } from 'react'
import { motion } from 'motion/react'

const API = import.meta.env.VITE_API_URL || ''

// Phase 1B/1C/1.5 canonical numbers — used as static fallback if API is unreachable.
const STATIC_FALLBACK = {
  pass_flip_rate: 0.222,
  pass_flip_n: 708,
  pass_flip_total: 3195,
  krippendorff_alpha_assumption: 0.55,
  krippendorff_alpha_rq: -0.13,
  krippendorff_alpha_method: -0.04,
  dominant_failure_pct: 0.469,
  dominant_failure_n: 67,
  dominant_failure_total: 143,
  rankings: {
    accuracy_top: 'gemini',
    accuracy_top_score: 0.776,
    robustness_top: 'mistral',
    calibration_top: 'chatgpt',
  },
  ece_consistency_min: 0.62,
  ece_consistency_max: 0.73,
  ece_consistency_gemini: 0.618,
}

const COLORS = ['#00FFE0', '#7FFFD4', '#A78BFA', '#FFB347', '#00B4D8', '#4A90D9']

function buildCards(d, pf) {
  // Headline 1 — combined pass-flip across 3,195 runs
  const flipPct = pf?.combined?.pct_pass_flip != null
    ? (pf.combined.pct_pass_flip * 100).toFixed(1)
    : (d.pass_flip_rate * 100).toFixed(1)
  const flipN = pf?.combined?.n_pass_flip ?? d.pass_flip_n
  const flipTotal = pf?.combined?.n_eligible ?? d.pass_flip_total

  const alphaA = (d.krippendorff_alpha_assumption ?? d.krippendorff_alpha)?.toFixed?.(2) ?? '0.55'

  return [
    {
      big: '1 in 5',
      label: 'Simple scoring overlooks bad reasoning',
      desc: `Across ${flipTotal.toLocaleString()} evaluable runs (1,095 base + 2,100 perturbations), ${flipPct}% (${flipN.toLocaleString()}) passed simple keyword-matching but failed when read carefully by an external AI judge. The disagreement holds under prompt rewording — a robustness finding for the methodology.`,
      why: 'Most LLM benchmarks score by keyword-matching alone. Our analysis across multiple prompt variants shows this approach systematically misses bad reasoning at a measurable rate.',
    },
    {
      big: 'α = -0.13 to 0.55',
      label: 'Two scoring methods give different answers',
      desc: `Krippendorff agreement on assumption articulation is ${alphaA} (questionable per Park et al. 2025 thresholds). On reasoning_quality and method_structure, the agreement is NEGATIVE — the two methods disagree more than they agree by chance. The disagreement is not noise — it's structural.`,
      why: "Confirms the 1-in-5 finding above isn't a fluke. The two scoring methods genuinely measure different things on three of four dimensions.",
    },
    {
      big: 'Almost half',
      label: 'Models skip the reasoning, not the math',
      desc: `Out of ${d.dominant_failure_total ?? 143} cases where a model failed, ${d.dominant_failure_n ?? 67} (${((d.dominant_failure_pct ?? 0.469) * 100).toFixed(0)}%) failed because they didn't articulate their assumptions — even though their math was often correct. Compare: only 48 (34%) failed because of math errors.`,
      why: "When LLMs fail at Bayesian reasoning, it's usually not because they can't compute — it's because they skip the reasoning steps. This is the silent failure mode.",
    },
    {
      big: 'Gemini #1',
      label: "The 'best' model depends on what you measure",
      desc: 'Equal-weight scoring (treat all 5 evaluation dimensions the same) ranks Claude #1. Literature-weighted scoring (emphasize what published research says matters most: assumption articulation and reasoning quality) ranks Gemini #1.',
      why: 'Benchmark rankings depend on the weighting scheme. Researchers should justify their weights, not pick equal weighting by default.',
    },
    {
      big: '3 different rankings',
      label: 'Accuracy, robustness, calibration disagree',
      desc: 'When we ranked models on accuracy, robustness, and calibration, the three rankings looked completely different. Gemini wins accuracy but is least robust. Mistral wins robustness. ChatGPT wins calibration. Only ChatGPT and Mistral are in the noise-equivalent band on robustness — others are statistically separable.',
      why: "Single-number leaderboards mislead. The same data tells three different stories about which model is 'best.'",
    },
    {
      big: 'All overconfident',
      label: 'Models think they\'re right when they\'re wrong',
      desc: "When a model gives the same answer 3 times in a row (confident agreement), it's still wrong about 60-70% of the time on hard tasks. We tested this across 161 numerical-answer tasks and found ECE scores of 0.62-0.73 for all 5 models. Notably, Gemini — which produces zero verbalized confidence under keyword extraction — has the BEST consistency calibration (0.62), an outlier in both directions.",
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

export default function KeyFindings() {
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

  const list = cards || staticCards()

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
      gap: 14,
      maxWidth: 1300, margin: '0 auto 32px',
    }}>
      {list.map((c, i) => {
        const color = COLORS[i % COLORS.length]
        const isHero = i === 0
        return (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.04 * i, duration: 0.45 }}
            style={{
              border: `1px solid ${color}33`,
              borderTop: `3px solid ${color}`,
              borderRadius: 12,
              padding: '20px 20px 18px',
              background: `${color}08`,
              opacity: loading && !cards ? 0.55 : 1,
              transition: 'opacity 0.3s',
              gridColumn: isHero ? '1 / -1' : 'auto',
            }}
          >
            <div style={{
              fontFamily: 'monospace', color: color,
              fontSize: isHero ? 38 : 26, fontWeight: 800, lineHeight: 1.05, marginBottom: 8,
            }}>
              {c.big}
            </div>
            <div style={{
              color: 'rgba(232,244,248,0.9)', fontSize: isHero ? 15 : 13, fontWeight: 700,
              marginBottom: 10, lineHeight: 1.35,
            }}>
              {c.label}
            </div>
            <div style={{ color: 'rgba(232,244,248,0.78)', fontSize: 12, lineHeight: 1.6, marginBottom: 10 }}>
              {c.desc}
            </div>
            {c.why && (
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
                {c.why}
              </div>
            )}
          </motion.div>
        )
      })}
    </div>
  )
}
