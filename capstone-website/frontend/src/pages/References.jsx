import { useEffect, useRef, useState } from 'react'
import { motion, useInView } from 'motion/react'

const API = import.meta.env.VITE_API_URL || ''

// Filename-keyed grouping: maps each paper file to its display group + grounding line.
// 3 visual groups per spec.
const GROUP = {
  // Closest Prior Work
  '01-original-stateval-2025.md':           { group: 'closest', grounding: 'Closest prior work — same statistical-reasoning lens, multiple-choice format. We extend to Bayesian inference + free-response.' },
  '03-original-matheval-2025.md':           { group: 'closest', grounding: 'Multi-dimensional rubric baseline. Our N·M·A·C·R extends MathEval\'s separation of numeric vs reasoning.' },

  // Methodology Foundations
  '04-original-program-of-thoughts-2022.md':{ group: 'methods',  grounding: 'Program-of-Thoughts considered and deferred — Bayesian closed-form derivations are symbolic, not arithmetic.' },
  '05-original-chain-of-thought-2022.md':   { group: 'methods',  grounding: 'Zero-shot CoT is the prompting baseline for all benchmark runs.' },
  '10-new-llm-judge-empirical-2025.md':     { group: 'methods',  grounding: 'Yamauchi et al. — α-over-ρ for inter-rater reliability; judge-design sensitivity > judge-model sensitivity. Underpins RQ1.' },
  '06-new-longjohn-bayesian-eval-2025.md':  { group: 'methods',  grounding: 'Bootstrap-CI motivation. Supports ranking separability claims.' },
  '15-new-statistical-fragility-2025.md':   { group: 'methods',  grounding: 'Hochlehnert et al. — single-question swaps shift Pass@1 ≥ 3pp; motivates bootstrap-CI separability tests.' },
  '07-new-reasonbench-2025.md':             { group: 'methods',  grounding: 'Variance-as-first-class evaluation framing — supports the three-rankings narrative.' },
  '08-new-brittlebench-2026.md':            { group: 'methods',  grounding: 'Perturbation taxonomy (rephrase / numerical / semantic) directly adopted.' },

  // Failure Modes & Calibration
  '09-new-ice-cream-causal-2025.md':        { group: 'failures', grounding: 'Du et al. — independently reports ~47% assumption-violation on causal-inference tasks. Validates RQ3.' },
  '13-new-math-reasoning-failures-2026.md': { group: 'failures', grounding: 'Boye & Moell — multi-domain math-reasoning failure catalogue; unwarranted assumptions aligns with our REGRESSION drops.' },
  '14-new-judgment-becomes-noise-2025.md':  { group: 'failures', grounding: 'Feuer et al. — single-judge benchmarks introduce systematic noise. Cited in Limitations.' },
  '11-new-fermieval-2025.md':               { group: 'failures', grounding: 'Domain shifts confidence behaviour — our Bayesian setting hedges where FermiEval overconfidently estimates.' },
  '12-new-multi-answer-confidence-2026.md': { group: 'failures', grounding: 'Verbalized vs consistency-based confidence dichotomy — names the upgrade path for RQ5.' },
  '02-original-can-llm-reasoning-2026.md':  { group: 'failures', grounding: 'Nagarkar et al. — reliability + hallucination motivation for any LLM-statistics calibration claim. Motivates RQ5.' },
}

const GROUP_META = {
  closest:  { label: 'Closest Prior Work',           color: '#00FFE0' },
  methods:  { label: 'Methodology Foundations',      color: '#00B4D8' },
  failures: { label: 'Failure Modes & Calibration',  color: '#A78BFA' },
}

const TEXTBOOK_DESC = {
  'bolstad-bayesian-statistics.md':       'Foundational. Conjugate models, credible intervals, HPD regions. Maps to BETA_BINOM, BINOM_FLAT, HPD.',
  'bishop-prml.md':                       'Comprehensive. Variational Bayes (Ch.10), Dirichlet-Multinomial (Ch.2). Core for VB and DIRICHLET.',
  'ghosh-delampady-samanta-bayesian.md':  'Graduate-level. Jeffreys priors, Fisher information, Rao-Cramér bounds. Primary for JEFFREYS, FISHER_INFO, RC_BOUND.',
  'hoff-bayesian-methods.md':             'Open access. Normal-Gamma, posterior predictive checks, Gibbs sampling. Covers NORMAL_GAMMA, PPC, GIBBS.',
  'carlin-louis-bayesian-data-analysis.md':'Advanced computation. Gibbs/MH/HMC, Bayesian regression, hierarchical models. Core for Phase 2.',
  'goldstein-wooff-bayes-linear.md':      'Specialised reference for Bayes linear methodology. Theoretical grounding.',
  'lee-bayesian-statistics.md':           'Clear introduction. Inference fundamentals. Key for CI_CREDIBLE and BAYES_FACTOR.',
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

function PaperCard({ p, color }) {
  const url = p.url || (p.arxiv_id ? `https://arxiv.org/abs/${p.arxiv_id.replace(/^arxiv:/i, '').replace(/^arXiv:/, '')}` : '')
  const grounding = (GROUP[p.filename] || {}).grounding || p.summary || ''
  const cite = p.citation_poster || `${p.authors} (${p.year})`
  const idTag = p.arxiv_id ? `arXiv:${p.arxiv_id}` : (p.year ? `${p.year}` : '')

  return (
    <motion.div
      whileHover={{ y: -3, boxShadow: `0 12px 40px ${color}33` }}
      transition={{ type: 'spring', stiffness: 380, damping: 26 }}
      style={{ borderRadius: 14 }}
    >
      <a
        href={url || '#'}
        target={url ? '_blank' : '_self'}
        rel="noopener noreferrer"
        style={{
          textDecoration: 'none', display: 'block', height: '100%',
          background: 'rgba(255,255,255,0.025)',
          border: `1px solid ${color}33`,
          borderTop: `3px solid ${color}`,
          borderRadius: 14,
          padding: '16px 18px',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
          <span style={{ color: 'rgba(232,244,248,0.55)', fontSize: 11, fontWeight: 600 }}>{cite}</span>
          {p.year && (
            <span style={{
              background: `${color}1A`, color: color,
              fontSize: 10, fontWeight: 700, padding: '2px 7px', borderRadius: 4,
            }}>
              {p.year}
            </span>
          )}
        </div>
        <div style={{ color: '#fff', fontSize: 13, fontWeight: 700, lineHeight: 1.4, marginBottom: 8 }}>
          {p.title || p.filename}
        </div>
        <p style={{ color: 'rgba(232,244,248,0.65)', fontSize: 11.5, lineHeight: 1.6, margin: '0 0 8px' }}>
          {grounding}
        </p>
        {idTag && (
          <div style={{ fontFamily: 'monospace', fontSize: 10, color: color, opacity: 0.75 }}>{idTag} ↗</div>
        )}
      </a>
    </motion.div>
  )
}

export default function References() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch(`${API}/api/v2/literature`)
      .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json()
      })
      .then(setData)
      .catch(e => setError(e.message))
  }, [])

  const papers = data?.originals || data?.new
    ? [...(data.originals || []), ...(data.new || [])]
    : []
  const grouped = { closest: [], methods: [], failures: [] }
  for (const p of papers) {
    const g = (GROUP[p.filename] || {}).group
    if (g && grouped[g]) grouped[g].push(p)
    else grouped.methods.push(p)
  }

  const totalPapers = papers.length
  const totalBooks = data?.textbooks?.length || 0

  return (
    <section id="references" style={{ padding: '96px 24px 80px', position: 'relative', zIndex: 1 }}>
      <div style={{ maxWidth: 1300, margin: '0 auto' }}>
        <FadeIn>
          <div style={{ color: 'rgba(0,255,224,0.55)', fontSize: 10, fontWeight: 700, letterSpacing: '0.2em', marginBottom: 8 }}>
            // {totalPapers ? `${totalPapers} RESEARCH PAPERS · ${totalBooks} TEXTBOOKS` : 'LITERATURE'}
          </div>
          <h2 style={{ fontSize: 'clamp(28px,3.5vw,42px)', fontWeight: 700, color: '#fff', margin: '0 0 8px', lineHeight: 1.2 }}>
            References
          </h2>
          <div style={{ width: 64, height: 3, background: 'linear-gradient(90deg,#00FFE0,#00B4D8)', borderRadius: 2, marginBottom: 36 }} />
        </FadeIn>

        {error && (
          <div style={{ color: '#FF6B6B', fontSize: 13, padding: 16, border: '1px solid rgba(255,107,107,0.4)', borderRadius: 8, marginBottom: 24 }}>
            Could not load references from /api/v2/literature: {error}
          </div>
        )}

        {!data && !error && (
          <div style={{ color: 'rgba(255,255,255,0.4)', fontSize: 13, fontStyle: 'italic' }}>
            Loading references…
          </div>
        )}

        {data && (
          <>
            {['closest', 'methods', 'failures'].map(gid => {
              const meta = GROUP_META[gid]
              const list = grouped[gid]
              if (!list.length) return null
              return (
                <FadeIn key={gid} delay={60}>
                  <div style={{
                    color: meta.color, fontSize: 12, fontWeight: 700,
                    letterSpacing: '0.16em', marginBottom: 14, marginTop: 8, textTransform: 'uppercase',
                  }}>
                    {meta.label} · {list.length} {list.length === 1 ? 'paper' : 'papers'}
                  </div>
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                    gap: 12, marginBottom: 36,
                  }}>
                    {list.map(p => (
                      <PaperCard key={p.filename} p={p} color={meta.color} />
                    ))}
                  </div>
                </FadeIn>
              )
            })}

            {/* Textbooks */}
            {data.textbooks?.length > 0 && (
              <FadeIn delay={120}>
                <div style={{
                  color: '#7FFFD4', fontSize: 12, fontWeight: 700,
                  letterSpacing: '0.16em', marginBottom: 14, marginTop: 24, textTransform: 'uppercase',
                }}>
                  Graduate Textbooks · {data.textbooks.length}
                </div>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                  gap: 12, marginBottom: 36,
                }}>
                  {data.textbooks.map(b => {
                    const desc = TEXTBOOK_DESC[b.filename] || b.summary || ''
                    let host = ''
                    if (b.url) {
                      try { host = new URL(b.url).hostname.replace(/^www\./, '') } catch { host = '' }
                    }
                    return (
                      <motion.div
                        key={b.filename}
                        whileHover={{ y: -3, boxShadow: '0 8px 28px rgba(127,255,212,0.2)' }}
                        transition={{ type: 'spring', stiffness: 380, damping: 26 }}
                        style={{ borderRadius: 14 }}
                      >
                        <a
                          href={b.url || '#'}
                          target={b.url ? '_blank' : '_self'}
                          rel="noopener noreferrer"
                          style={{
                            textDecoration: 'none', display: 'block', height: '100%',
                            background: 'rgba(255,255,255,0.025)',
                            border: '1px solid rgba(127,255,212,0.25)',
                            borderRadius: 14, padding: '14px 18px',
                          }}
                        >
                          <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
                            <div style={{
                              width: 8, height: 8, borderRadius: '50%',
                              background: '#7FFFD4', flexShrink: 0, marginTop: 6,
                              boxShadow: '0 0 6px #7FFFD4',
                            }} />
                            <div style={{ flex: 1 }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4, gap: 8 }}>
                                <div style={{ color: '#fff', fontSize: 12.5, fontWeight: 700, lineHeight: 1.4 }}>
                                  {b.title || b.filename}
                                </div>
                                {b.year && (
                                  <span style={{
                                    background: 'rgba(127,255,212,0.10)', color: '#7FFFD4',
                                    fontSize: 10, fontWeight: 700, padding: '2px 7px', borderRadius: 4, flexShrink: 0,
                                  }}>
                                    {String(b.year).match(/\d{4}/)?.[0] || b.year}
                                  </span>
                                )}
                              </div>
                              <div style={{ color: 'rgba(232,244,248,0.55)', fontSize: 11, marginBottom: 6 }}>
                                {b.authors}
                              </div>
                              {desc && (
                                <p style={{ color: 'rgba(232,244,248,0.7)', fontSize: 11, lineHeight: 1.55, margin: '0 0 8px' }}>
                                  {desc}
                                </p>
                              )}
                              {host && (
                                <div style={{ fontFamily: 'monospace', fontSize: 10, color: '#7FFFD4', opacity: 0.75 }}>
                                  {host} ↗
                                </div>
                              )}
                            </div>
                          </div>
                        </a>
                      </motion.div>
                    )
                  })}
                </div>
              </FadeIn>
            )}
          </>
        )}
      </div>
    </section>
  )
}
