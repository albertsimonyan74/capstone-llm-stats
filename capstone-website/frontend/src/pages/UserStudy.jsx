import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import ReactMarkdown from 'react-markdown'
import remarkMath from 'remark-math'
import remarkGfm from 'remark-gfm'
import rehypeKatex from 'rehype-katex'

const API_BASE = import.meta.env.VITE_API_URL || ''

const MODEL_META = {
  claude:   { name: 'Claude Sonnet 4.6', color: '#00CED1', initials: 'CL' },
  chatgpt:  { name: 'GPT-4.1',           color: '#7FFFD4', initials: 'GP' },
  gemini:   { name: 'Gemini 2.5 Flash',  color: '#FF6B6B', initials: 'GM' },
  deepseek: { name: 'DeepSeek V4 Flash', color: '#4A90D9', initials: 'DS' },
  mistral:  { name: 'Mistral Large',     color: '#A78BFA', initials: 'MS' },
}

const MODEL_ORDER = ['claude', 'chatgpt', 'gemini', 'deepseek', 'mistral']

const VOTE_REASONS = [
  { key: 'mathematical_accuracy', label: 'Mathematical Accuracy',       desc: 'Correct formulas, calculations, and numerical results' },
  { key: 'clarity',               label: 'Clarity of Explanation',       desc: 'Most accessible and easy-to-follow step-by-step reasoning' },
  { key: 'thoroughness',          label: 'Thoroughness',                  desc: 'Identified all relevant assumptions, caveats, and edge cases' },
  { key: 'presentation',          label: 'Presentation Quality',          desc: 'Well-structured, clearly formatted and organized response' },
  { key: 'trustworthiness',       label: 'Statistical Trustworthiness',   desc: 'Demonstrated genuine understanding, not surface pattern matching' },
]

// ── Normalize LaTeX delimiters ────────────────────────────────────────────────
function normalizeMath(text) {
  if (!text) return text
  text = text.replace(/\\\((.+?)\\\)/gs, (_, m) => `$${m}$`)
  text = text.replace(/\\\[(.+?)\\\]/gs, (_, m) => `$$${m}$$`)
  return text
}

// ── Markdown + LaTeX + GFM tables renderer ────────────────────────────────────
function MarkdownRenderer({ text, color }) {
  if (!text) return null
  const normalized = normalizeMath(text)
  return (
    <div
      className="md-response"
      style={{
        fontSize: 13.5, lineHeight: 1.75, color: '#c8dce8',
        wordBreak: 'break-word', maxHeight: 520, overflowY: 'auto',
        paddingRight: 4, '--md-accent': color,
      }}
    >
      <ReactMarkdown
        remarkPlugins={[remarkMath, remarkGfm]}
        rehypePlugins={[[rehypeKatex, { throwOnError: false, strict: false }]]}
        components={{
          p:          ({ children }) => <p style={{ margin: '0 0 10px' }}>{children}</p>,
          strong:     ({ children }) => <strong style={{ color: '#e8f4f8', fontWeight: 700 }}>{children}</strong>,
          em:         ({ children }) => <em style={{ color: '#b8d0e0' }}>{children}</em>,
          code:       ({ node, className, children, ...props }) => {
            const isBlock = node?.position?.start?.line !== node?.position?.end?.line || String(children).includes('\n')
            return isBlock
              ? <pre style={{ background: 'rgba(0,0,0,0.35)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 8, padding: '12px 14px', overflow: 'auto', margin: '8px 0' }}><code style={{ fontSize: 12, fontFamily: 'var(--font-mono)', color: '#c8dce8' }}>{children}</code></pre>
              : <code style={{ background: 'rgba(0,255,224,0.1)', border: '1px solid rgba(0,255,224,0.2)', borderRadius: 4, padding: '1px 5px', fontSize: 12.5, fontFamily: 'var(--font-mono)', color: '#00FFE0' }}>{children}</code>
          },
          ul:         ({ children }) => <ul style={{ margin: '4px 0 10px', paddingLeft: 20 }}>{children}</ul>,
          ol:         ({ children }) => <ol style={{ margin: '4px 0 10px', paddingLeft: 20 }}>{children}</ol>,
          li:         ({ children }) => <li style={{ marginBottom: 4, color: '#b8d0e0' }}>{children}</li>,
          h1:         ({ children }) => <h1 style={{ fontSize: 16, fontWeight: 700, color: '#e8f4f8', margin: '12px 0 6px' }}>{children}</h1>,
          h2:         ({ children }) => <h2 style={{ fontSize: 14, fontWeight: 700, color: '#e8f4f8', margin: '10px 0 5px' }}>{children}</h2>,
          h3:         ({ children }) => <h3 style={{ fontSize: 13, fontWeight: 700, color: '#d0e8f0', margin: '8px 0 4px' }}>{children}</h3>,
          h4:         ({ children }) => <h4 style={{ fontSize: 12, fontWeight: 700, color: '#b8d0e0', margin: '6px 0 3px' }}>{children}</h4>,
          blockquote: ({ children }) => <blockquote style={{ borderLeft: '3px solid rgba(0,255,224,0.4)', paddingLeft: 12, margin: '8px 0', color: '#9ab8c8' }}>{children}</blockquote>,
          hr:         () => <hr style={{ border: 'none', borderTop: '1px solid rgba(255,255,255,0.1)', margin: '12px 0' }} />,
          table:      ({ children }) => (
            <div style={{ overflowX: 'auto', margin: '10px 0' }}>
              <table style={{ borderCollapse: 'collapse', width: '100%', fontSize: 12 }}>{children}</table>
            </div>
          ),
          thead:      ({ children }) => <thead>{children}</thead>,
          tbody:      ({ children }) => <tbody>{children}</tbody>,
          tr:         ({ children }) => <tr>{children}</tr>,
          th:         ({ children }) => <th style={{ border: '1px solid rgba(0,255,224,0.25)', padding: '7px 12px', background: 'rgba(0,255,224,0.07)', color: '#00FFE0', textAlign: 'left', fontWeight: 700 }}>{children}</th>,
          td:         ({ children }) => <td style={{ border: '1px solid rgba(255,255,255,0.1)', padding: '6px 12px', color: '#c8dce8' }}>{children}</td>,
        }}
      >
        {normalized}
      </ReactMarkdown>
    </div>
  )
}

// ── Divergence analysis ───────────────────────────────────────────────────────
function extractFinalAnswer(text) {
  if (!text) return ''
  const lines = text.split('\n')
  // Scan bottom-up for ANSWER: tag (plain or **ANSWER:** markdown bold)
  for (let i = lines.length - 1; i >= 0; i--) {
    const line = lines[i].trim()
    if (/^\*{0,2}ANSWER:\*{0,2}/i.test(line)) {
      const val = line.replace(/^\*{0,2}ANSWER:\*{0,2}\s*/i, '').replace(/\*{0,2}$/, '').trim()
      if (val) return val
      // Value may be on the next non-empty line (model put answer on separate line)
      for (let j = i + 1; j < lines.length; j++) {
        const next = lines[j].trim()
        if (next) return next
      }
      return ''
    }
  }
  for (let i = lines.length - 1; i >= 0; i--) {
    if (lines[i].trim()) return lines[i].trim().slice(0, 200)
  }
  return ''
}

const NUMERIC_TOLERANCE = 0.02

// Normalize fractions like "1/6", "3/7" → decimal string before numeric extraction
function normalizeFractions(s) {
  return s.replace(/(-?\d+(?:\.\d+)?)\s*\/\s*(\d+(?:\.\d+)?)/g, (_, n, d) => {
    const val = parseFloat(n) / parseFloat(d)
    return isFinite(val) && parseFloat(d) !== 0 ? val.toFixed(8) : _
  })
}

function normalizeAnswerStr(s) {
  let norm = normalizeFractions(s)
  norm = norm.replace(/(\d+(?:\.\d+)?)\s*%/g, (_, n) => (parseFloat(n) / 100).toFixed(4))
  norm = norm.toLowerCase()
    .replace(/\b\d+\.\d+\b/g, n => parseFloat(n).toFixed(3))
    .replace(/[,;]/g, ' ')
    .replace(/\s+/g, ' ').trim().slice(0, 120)
  return norm
}

// Extract first numeric value from answer string.
// Normalizes fractions (1/6 → 0.1667) and percentages (43% → 0.43).
function extractFirstNum(s) {
  if (!s) return null
  const norm = normalizeFractions(s)
  const pct = norm.match(/(-?\d+(?:\.\d+)?(?:e[+-]?\d+)?)\s*%/i)
  if (pct) {
    const n = parseFloat(pct[1]) / 100
    return isFinite(n) ? n : null
  }
  const m = norm.match(/-?\d+(?:\.\d+)?(?:e[+-]?\d+)?/i)
  if (!m) return null
  const n = parseFloat(m[0])
  return isFinite(n) ? n : null
}

// Extract all numeric values from an answer string
function extractAllNums(s) {
  if (!s) return []
  const norm = normalizeFractions(s)
    .replace(/(\d+(?:\.\d+)?)\s*%/g, (_, n) => String(parseFloat(n) / 100))
  const matches = norm.match(/-?\d+(?:\.\d+)?(?:e[+-]?\d+)?/gi) || []
  return matches.map(m => parseFloat(m)).filter(n => isFinite(n))
}

// Compare two sorted numeric arrays element-wise within tolerance
function numsClose(a, b, tol) {
  if (a.length === 0 && b.length === 0) return true
  if (a.length !== b.length) return false
  const sa = [...a].sort((x, y) => x - y)
  const sb = [...b].sort((x, y) => x - y)
  return sa.every((v, i) => Math.abs(v - sb[i]) <= tol)
}

function computeDivergence(responses) {
  const valid = responses.filter(r => !r.error && r.response)
  if (valid.length < 2) return null

  const extracted = valid.map(r => ({
    model_id: r.model_id,
    rawAnswer: extractFinalAnswer(r.response),
    normAnswer: normalizeAnswerStr(extractFinalAnswer(r.response)),
    allNums: extractAllNums(extractFinalAnswer(r.response)),
  }))

  // Override: if all normalized strings are identical → instant consensus
  const normSet = new Set(extracted.map(e => e.normAnswer))
  if (normSet.size === 1) {
    const allIds = extracted.map(e => e.model_id)
    return {
      modelStatus: Object.fromEntries(allIds.map(id => [id, 'consensus'])),
      verdict: 'consensus', severity: 'none',
      message: 'All models converge on the same answer.',
      groups: [['0', allIds]], extracted,
    }
  }

  let groups // Array of [normKey, [model_ids]]
  const allHaveNums = extracted.every(e => e.allNums.length > 0)

  if (allHaveNums) {
    // Group by sorted number arrays (handles multi-value answers and different orderings)
    const groupNums = []
    const groupMembers = []
    for (const e of extracted) {
      let found = -1
      for (let gi = 0; gi < groupNums.length; gi++) {
        if (numsClose(e.allNums, groupNums[gi], NUMERIC_TOLERANCE)) {
          found = gi; break
        }
      }
      if (found === -1) {
        groupNums.push(e.allNums)
        groupMembers.push([e.model_id])
      } else {
        groupMembers[found].push(e.model_id)
      }
    }
    groups = groupMembers.map((members, i) => [String(i), members])
  } else {
    // Fallback: first-number comparison or string match
    const groupMembers = []
    for (const e of extracted) {
      let matched = -1
      for (let gi = 0; gi < groupMembers.length; gi++) {
        const repId = groupMembers[gi][0]
        const rep = extracted.find(x => x.model_id === repId)
        if (!rep) continue
        const n1 = extractFirstNum(e.rawAnswer)
        const n2 = extractFirstNum(rep.rawAnswer)
        if (n1 !== null && n2 !== null && Math.abs(n1 - n2) <= NUMERIC_TOLERANCE) {
          matched = gi; break
        }
        if (n1 === null && n2 === null && e.normAnswer === rep.normAnswer) {
          matched = gi; break
        }
      }
      if (matched === -1) {
        groupMembers.push([e.model_id])
      } else {
        groupMembers[matched].push(e.model_id)
      }
    }
    groups = groupMembers.map((members, i) => [String(i), members])
  }

  const groupList = [...groups].sort((a, b) => b[1].length - a[1].length)
  const total = extracted.length
  const largest = groupList[0][1].length

  const modelStatus = {}
  for (const [norm, models] of groupList) {
    const size = models.length
    let status
    if (groupList.length === 1) status = 'consensus'
    else if (size === largest && size >= Math.ceil(total * 0.6)) status = 'majority'
    else if (size === 1) status = 'outlier'
    else if (size < largest) status = 'minority'
    else status = 'split'
    for (const m of models) modelStatus[m] = status
  }

  let verdict, message, severity
  if (groupList.length === 1) {
    verdict = 'consensus'; severity = 'none'
    message = 'All models converge on the same answer.'
  } else if (largest >= total - 1 && total >= 4) {
    const outliers = groupList.slice(1).flatMap(g => g[1])
    const names = outliers.map(id => MODEL_META[id]?.name || id).join(', ')
    verdict = 'near-consensus'; severity = 'caution'
    message = `Caution: ${names} provides an answer that diverges from the other ${largest} models. Verify this model's result independently.`
  } else if (largest >= Math.ceil(total * 0.6)) {
    const minority = groupList.slice(1).flatMap(g => g[1])
    const names = minority.map(id => MODEL_META[id]?.name || id).join(', ')
    verdict = 'majority'; severity = 'note'
    message = `Note: ${names} give different answers from the majority (${largest} models). The majority answer may be more reliable.`
  } else if (groupList.length === total && total >= 3) {
    verdict = 'no-consensus'; severity = 'warning'
    message = 'All models provide different answers. No consensus has been reached — verify using a reference source before relying on any single model.'
  } else {
    verdict = 'split'; severity = 'caution'
    message = `Models are split across ${groupList.length} distinct answers. Exercise judgment when selecting the correct result.`
  }

  return { modelStatus, verdict, severity, message, groups: groupList, extracted }
}

const DIVERGENCE_COLORS = { consensus: '#7FFFD4', majority: '#00FFE0', minority: '#F59E0B', outlier: '#FF6B6B', split: '#A78BFA', none: 'transparent' }
const DIVERGENCE_LABELS = { consensus: 'CONSENSUS', majority: 'MAJORITY', minority: 'MINORITY ANSWER', outlier: '⚠ DIVERGENT', split: 'SPLIT', none: '' }
const SEVERITY_COLORS   = { none: 'rgba(127,255,212,0.7)', note: 'rgba(0,255,224,0.7)', caution: 'rgba(245,158,11,0.9)', warning: 'rgba(255,107,107,0.9)' }

// ── Skeleton card ─────────────────────────────────────────────────────────────
function SkeletonCard({ index }) {
  const meta = MODEL_META[MODEL_ORDER[index]]
  return (
    <div style={{ background: 'rgba(0,255,224,0.03)', border: `1px solid ${meta.color}33`, borderRadius: 12, padding: '20px 24px', display: 'flex', flexDirection: 'column', gap: 12 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <div style={{ width: 36, height: 36, borderRadius: 8, background: meta.color + '22', border: `1px solid ${meta.color}55`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 11, fontFamily: 'var(--font-mono)', color: meta.color, fontWeight: 700 }}>{meta.initials}</div>
        <div>
          <div style={{ fontSize: 13, fontWeight: 600, color: '#e8f4f8' }}>{meta.name}</div>
          <div style={{ height: 8, width: 60, borderRadius: 4, background: 'rgba(255,255,255,0.08)', marginTop: 4, animation: 'pulse 1.4s ease-in-out infinite' }}/>
        </div>
      </div>
      {[100, 85, 95, 70].map((w, i) => (
        <div key={i} style={{ height: 8, width: `${w}%`, borderRadius: 4, background: 'rgba(255,255,255,0.06)', animation: `pulse 1.4s ease-in-out ${i * 0.15}s infinite` }}/>
      ))}
    </div>
  )
}

// ── Response card with inline voting ─────────────────────────────────────────
function ResponseCard({ resp, divergenceStatus, voted, onVote, voteSubmitted, aggregateData, hasImage }) {
  const meta = MODEL_META[resp.model_id] || { name: resp.model_name, color: '#8BAFC0', initials: '?' }
  const isVotedThis  = voted === resp.model_id
  const isError      = !!resp.error
  const dvStatus     = divergenceStatus || 'none'
  const dvColor      = DIVERGENCE_COLORS[dvStatus] || 'transparent'
  const dvLabel      = DIVERGENCE_LABELS[dvStatus] || ''
  const [selectingReason, setSelectingReason] = useState(false)

  // Aggregate bar for this model
  const aggTotal = aggregateData?.total_votes || 0
  const aggCount = aggregateData?.vote_distribution?.[resp.model_id] || 0
  const aggPct   = aggTotal > 0 ? Math.round((aggCount / aggTotal) * 100) : 0

  function handleVoteClick() {
    if (voteSubmitted || voted) return
    setSelectingReason(true)
  }

  function handleReasonSelect(reasonKey, reasonLabel) {
    setSelectingReason(false)
    onVote(resp.model_id, reasonKey, reasonLabel)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      style={{
        background: isVotedThis ? `${meta.color}12` : 'rgba(0,255,224,0.03)',
        border: `1.5px solid ${isVotedThis ? meta.color : meta.color + '33'}`,
        borderRadius: 12,
        padding: '20px 24px',
        display: 'flex', flexDirection: 'column', gap: 14,
        transition: 'border-color 0.2s, background 0.2s',
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ width: 36, height: 36, borderRadius: 8, background: meta.color + '22', border: `1px solid ${meta.color}55`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 11, fontFamily: 'var(--font-mono)', color: meta.color, fontWeight: 700 }}>{meta.initials}</div>
          <div>
            <div style={{ fontSize: 13, fontWeight: 600, color: '#e8f4f8' }}>{meta.name}</div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              {resp.latency_ms > 0 ? `${resp.latency_ms.toLocaleString()} ms` : '—'}
            </div>
          </div>
        </div>
        {/* Divergence badge */}
        {dvStatus !== 'none' && dvStatus !== 'consensus' && dvLabel && (
          <div style={{ fontSize: 9, fontWeight: 700, fontFamily: 'var(--font-mono)', letterSpacing: '0.06em', color: dvColor, border: `1px solid ${dvColor}66`, borderRadius: 4, padding: '2px 7px' }}>
            {dvLabel}
          </div>
        )}
      </div>

      {/* Body */}
      {isError ? (
        <div style={{ color: '#FF6B6B', fontSize: 13, fontFamily: 'var(--font-mono)' }}>Error: {resp.error}</div>
      ) : (
        <MarkdownRenderer text={resp.response} color={meta.color} />
      )}

      {/* Bottom: aggregate bar + vote section */}
      {!isError && (
        <div style={{ borderTop: '1px solid rgba(255,255,255,0.07)', paddingTop: 12, display: 'flex', flexDirection: 'column', gap: 10 }}>
          {/* Aggregate bar */}
          {aggTotal > 0 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', width: 80, flexShrink: 0 }}>
                {aggCount} vote{aggCount !== 1 ? 's' : ''} ({aggPct}%)
              </div>
              <div style={{ flex: 1, height: 5, background: 'rgba(255,255,255,0.06)', borderRadius: 3, overflow: 'hidden' }}>
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${aggPct}%` }}
                  transition={{ duration: 0.6, ease: 'easeOut' }}
                  style={{ height: '100%', background: meta.color + 'cc', borderRadius: 3 }}
                />
              </div>
            </div>
          )}

          {/* Vote section */}
          {!voteSubmitted && !voted && !selectingReason && (
            <button
              onClick={handleVoteClick}
              style={{
                alignSelf: 'flex-start', padding: '7px 18px', borderRadius: 7,
                border: `1.5px solid ${meta.color}66`, background: 'transparent',
                color: 'var(--text-muted)', fontSize: 12, fontWeight: 600,
                cursor: 'pointer', transition: 'all 0.18s', fontFamily: 'var(--font-mono)',
              }}
              onMouseEnter={e => { e.target.style.borderColor = meta.color; e.target.style.color = meta.color }}
              onMouseLeave={e => { e.target.style.borderColor = meta.color + '66'; e.target.style.color = 'var(--text-muted)' }}
            >
              Mark as Best ▼
            </button>
          )}

          {/* Reason selector */}
          {selectingReason && !voteSubmitted && (
            <motion.div
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              style={{ display: 'flex', flexDirection: 'column', gap: 6 }}
            >
              <div style={{ fontSize: 10, color: meta.color, fontFamily: 'var(--font-mono)', fontWeight: 700, letterSpacing: '0.06em', marginBottom: 2 }}>
                WHY IS THIS THE BEST RESPONSE?
              </div>
              {VOTE_REASONS.map(r => (
                <button
                  key={r.key}
                  onClick={() => handleReasonSelect(r.key, r.label)}
                  style={{
                    textAlign: 'left', padding: '8px 12px', borderRadius: 7,
                    border: `1px solid ${meta.color}44`, background: 'rgba(0,0,0,0.2)',
                    color: '#c8dce8', fontSize: 12, cursor: 'pointer',
                    transition: 'all 0.15s', fontFamily: 'inherit',
                  }}
                  onMouseEnter={e => { e.currentTarget.style.borderColor = meta.color; e.currentTarget.style.background = meta.color + '18' }}
                  onMouseLeave={e => { e.currentTarget.style.borderColor = meta.color + '44'; e.currentTarget.style.background = 'rgba(0,0,0,0.2)' }}
                >
                  <span style={{ color: meta.color, fontWeight: 700 }}>{r.label}</span>
                  <span style={{ color: 'rgba(255,255,255,0.45)', fontSize: 11, marginLeft: 6 }}>— {r.desc}</span>
                </button>
              ))}
              <button
                onClick={() => setSelectingReason(false)}
                style={{ alignSelf: 'flex-start', background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: 11, cursor: 'pointer', padding: '2px 0', fontFamily: 'inherit' }}
              >
                ✕ Cancel
              </button>
            </motion.div>
          )}

          {/* Submitted: your choice badge */}
          {voteSubmitted && isVotedThis && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: meta.color, fontFamily: 'var(--font-mono)', fontWeight: 700 }}>
              <span style={{ fontSize: 14 }}>✓</span> Your Choice
            </div>
          )}
        </div>
      )}
    </motion.div>
  )
}

// ── Divergence banner ─────────────────────────────────────────────────────────
function DivergenceBanner({ divergence }) {
  if (!divergence || divergence.severity === 'none') return null
  const color = SEVERITY_COLORS[divergence.severity] || 'rgba(0,255,224,0.7)'
  const bgMap = { none: 'transparent', note: 'rgba(0,255,224,0.05)', caution: 'rgba(245,158,11,0.06)', warning: 'rgba(255,107,107,0.06)' }
  const borderMap = { none: 'transparent', note: 'rgba(0,255,224,0.2)', caution: 'rgba(245,158,11,0.3)', warning: 'rgba(255,107,107,0.3)' }
  return (
    <motion.div
      initial={{ opacity: 0, y: -6 }}
      animate={{ opacity: 1, y: 0 }}
      style={{
        background: bgMap[divergence.severity],
        border: `1px solid ${borderMap[divergence.severity]}`,
        borderRadius: 10, padding: '12px 18px',
        marginBottom: 16, display: 'flex', alignItems: 'flex-start', gap: 10,
      }}
    >
      <div style={{ fontSize: 16, flexShrink: 0, marginTop: 1 }}>
        {divergence.severity === 'warning' ? '⚠' : divergence.severity === 'caution' ? '◈' : 'ℹ'}
      </div>
      <div>
        <div style={{ fontSize: 10, fontWeight: 700, color, fontFamily: 'var(--font-mono)', letterSpacing: '0.08em', marginBottom: 3 }}>
          ANSWER DIVERGENCE ANALYSIS
        </div>
        <div style={{ fontSize: 12.5, color: 'rgba(220,235,245,0.9)', lineHeight: 1.6 }}>
          {divergence.message}
        </div>
      </div>
    </motion.div>
  )
}

// ── Aggregate stats (top panel, always accessible) ────────────────────────────
function AggregateStats({ refreshTrigger }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [isOpen, setIsOpen] = useState(false)

  async function load() {
    setIsOpen(true); setLoading(true)
    try { const r = await fetch(`${API_BASE}/api/user-study/results`); setData(await r.json()) } catch {}
    setLoading(false)
  }

  useEffect(() => {
    if (refreshTrigger > 0 && isOpen) {
      setLoading(true)
      fetch(`${API_BASE}/api/user-study/results`).then(r => r.json()).then(d => { setData(d); setLoading(false) }).catch(() => setLoading(false))
    }
  }, [refreshTrigger])

  if (!isOpen) {
    return (
      <button onClick={load} style={{ padding: '9px 22px', borderRadius: 8, border: '1px solid rgba(0,255,224,0.4)', background: 'rgba(0,255,224,0.07)', color: 'rgba(0,255,224,0.9)', fontSize: 12, fontWeight: 700, cursor: 'pointer', fontFamily: 'var(--font-mono)', letterSpacing: '0.04em' }}>
        View Aggregate Vote Results ▼
      </button>
    )
  }

  return (
    <motion.div initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ color: 'rgba(0,255,224,0.8)', fontSize: 11, fontFamily: 'var(--font-mono)', letterSpacing: '0.06em', fontWeight: 700 }}>
          AGGREGATE VOTES
          {data ? ` — ${data.total_votes} vote${data.total_votes !== 1 ? 's' : ''}` : ''}
          {data?.unique_users ? <span style={{ color: 'rgba(167,139,250,0.8)', marginLeft: 10 }}>· {data.unique_users} unique user{data.unique_users !== 1 ? 's' : ''}</span> : null}
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={() => { setLoading(true); fetch(`${API_BASE}/api/user-study/results`).then(r => r.json()).then(d => { setData(d); setLoading(false) }).catch(() => setLoading(false)) }} disabled={loading} style={{ padding: '4px 12px', borderRadius: 6, border: '1px solid rgba(0,255,224,0.3)', background: 'rgba(0,255,224,0.06)', color: 'rgba(0,255,224,0.8)', fontSize: 10, fontWeight: 700, cursor: loading ? 'wait' : 'pointer', fontFamily: 'var(--font-mono)' }}>↻ REFRESH</button>
          <button onClick={() => setIsOpen(false)} style={{ padding: '4px 10px', borderRadius: 6, border: '1px solid rgba(255,255,255,0.15)', background: 'transparent', color: 'rgba(255,255,255,0.5)', fontSize: 10, fontWeight: 700, cursor: 'pointer', fontFamily: 'var(--font-mono)' }}>▲ CLOSE</button>
        </div>
      </div>
      {loading ? (
        <div style={{ color: 'var(--text-muted)', fontSize: 12 }}>Loading...</div>
      ) : !data || data.total_votes === 0 ? (
        <div style={{ color: 'var(--text-muted)', fontSize: 12, fontFamily: 'var(--font-mono)' }}>No votes yet. Be the first to submit a question and vote!</div>
      ) : (() => {
        const dist = data.vote_distribution
        const max = Math.max(...Object.values(dist), 1)
        return Object.entries(dist).map(([id, count]) => {
          const meta = MODEL_META[id] || { name: id, color: '#8BAFC0' }
          const pct = Math.round((count / data.total_votes) * 100)
          return (
            <div key={id} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{ width: 110, fontSize: 11, color: meta.color, fontFamily: 'var(--font-mono)', fontWeight: 600, flexShrink: 0 }}>{meta.name}</div>
              <div style={{ flex: 1, height: 12, borderRadius: 6, background: 'rgba(255,255,255,0.06)', overflow: 'hidden' }}>
                <motion.div initial={{ width: 0 }} animate={{ width: `${(count / max) * 100}%` }} transition={{ duration: 0.6, ease: 'easeOut' }} style={{ height: '100%', background: meta.color + 'cc', borderRadius: 6 }}/>
              </div>
              <div style={{ width: 60, textAlign: 'right', fontSize: 11, color: 'rgba(255,255,255,0.7)', fontFamily: 'var(--font-mono)', flexShrink: 0 }}>{count} ({pct}%)</div>
            </div>
          )
        })
      })()}
    </motion.div>
  )
}

// ── Main UserStudy component ───────────────────────────────────────────────────
export default function UserStudy() {
  const [question,      setQuestion]      = useState('')
  const [imageFile,     setImageFile]     = useState(null)
  const [imagePreview,  setImagePreview]  = useState(null)
  const [loading,       setLoading]       = useState(false)
  const [responses,     setResponses]     = useState(null)
  const [sessionId,     setSessionId]     = useState(null)
  const [error,         setError]         = useState(null)
  const [voted,         setVoted]         = useState(null)
  const [voteSubmitted, setVoteSubmitted] = useState(false)
  const [voteRefresh,   setVoteRefresh]   = useState(0)
  const [aggregateData, setAggregateData] = useState(null)
  const [divergence,    setDivergence]    = useState(null)
  const fileRef = useRef()

  function handleImage(file) {
    if (!file) return
    setImageFile(file)
    const reader = new FileReader()
    reader.onload = e => setImagePreview(e.target.result)
    reader.readAsDataURL(file)
  }

  function clearImage() {
    setImageFile(null); setImagePreview(null)
    if (fileRef.current) fileRef.current.value = ''
  }

  async function loadAggregate() {
    try {
      const r = await fetch(`${API_BASE}/api/user-study/results`)
      setAggregateData(await r.json())
    } catch {}
  }

  async function submit() {
    const q = question.trim()
    if (q.length < 5)    { setError('Question too short (min 5 characters).'); return }
    if (q.length > 2000) { setError('Question too long (max 2000 characters).'); return }
    setError(null); setLoading(true)
    setResponses(null); setSessionId(null); setVoted(null); setVoteSubmitted(false)
    setAggregateData(null); setDivergence(null)

    const fd = new FormData()
    fd.append('question', q)
    if (imageFile) fd.append('image', imageFile)

    try {
      const r = await fetch(`${API_BASE}/api/user-study`, { method: 'POST', body: fd })
      if (r.status === 429) { setError('Rate limit reached (10 requests/hour per IP). Try again later.'); return }
      if (!r.ok) { const d = await r.json().catch(() => ({})); setError(d.detail || `Server error: ${r.status}`); return }
      const data = await r.json()
      setResponses(data.responses)
      setSessionId(data.session_id)
      setDivergence(computeDivergence(data.responses))
      await loadAggregate()
    } catch {
      setError('Failed to reach backend. Is the server running on port 8000?')
    } finally {
      setLoading(false)
    }
  }

  async function handleVote(modelId, reasonKey, reasonLabel) {
    setVoted(modelId)
    try {
      await fetch(`${API_BASE}/api/user-study/vote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          question: question.trim(),
          voted_model: modelId,
          reason: reasonKey || null,
          reason_label: reasonLabel || null,
          had_image: !!imageFile,
          divergence_verdict: divergence?.verdict || null,
          divergence_data: divergence ? { verdict: divergence.verdict, severity: divergence.severity, model_statuses: divergence.modelStatus } : null,
        }),
      })
      setVoteSubmitted(true)
      setVoteRefresh(n => n + 1)
      await loadAggregate()
    } catch (e) {
      console.error('Vote submit failed:', e)
      setVoteSubmitted(true)
    }
  }

  return (
    <section id="user-study" style={{ padding: '80px 0', position: 'relative', zIndex: 1 }}>
      <div style={{ maxWidth: 1100, margin: '0 auto', padding: '0 32px' }}>

        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 24 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }} style={{ marginBottom: 32 }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '5px 14px', borderRadius: 20, border: '1px solid rgba(0,255,224,0.25)', background: 'rgba(0,255,224,0.07)', fontSize: 11, letterSpacing: '0.1em', color: '#00FFE0', fontFamily: 'var(--font-mono)', marginBottom: 20 }}>
            LIVE COMPARISON
          </div>
          <h2 style={{ fontSize: 36, fontWeight: 700, margin: '0 0 14px', background: 'linear-gradient(135deg, #00FFE0 0%, #00B4D8 60%, #A78BFA 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            User Study
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: 15, lineHeight: 1.7, maxWidth: 640, margin: 0 }}>
            Submit a Bayesian or inferential statistics question. All 5 models respond in parallel.
            Select the best response — results feed the research.
          </p>
        </motion.div>

        {/* Aggregate stats */}
        <motion.div initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} transition={{ duration: 0.5 }} style={{ background: 'rgba(0,255,224,0.02)', border: '1px solid rgba(0,255,224,0.1)', borderRadius: 12, padding: '16px 24px', marginBottom: 8 }}>
          <AggregateStats refreshTrigger={voteRefresh} />
        </motion.div>
        {/* Input panel */}
        <motion.div initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.5, delay: 0.1 }} style={{ background: 'rgba(0,255,224,0.03)', border: '1px solid rgba(0,255,224,0.15)', borderRadius: 14, padding: '28px 32px', marginBottom: 36, display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{ color: 'rgba(0,255,224,0.75)', fontSize: 11, fontFamily: 'var(--font-mono)', letterSpacing: '0.06em', fontWeight: 700 }}>
            YOUR QUESTION
          </div>

          <textarea
            value={question}
            onChange={e => setQuestion(e.target.value)}
            placeholder="e.g. A coin is flipped 10 times and lands heads 7 times. Using a Beta(2,2) prior, what is the posterior distribution and its mean?"
            rows={5}
            style={{ background: 'rgba(0,255,224,0.04)', border: '1px solid rgba(0,255,224,0.18)', borderRadius: 9, padding: '14px 16px', color: '#e8f4f8', fontSize: 14, lineHeight: 1.7, resize: 'vertical', fontFamily: 'inherit', outline: 'none', width: '100%', boxSizing: 'border-box', transition: 'border-color 0.18s' }}
            onFocus={e => e.target.style.borderColor = 'rgba(0,255,224,0.45)'}
            onBlur={e => e.target.style.borderColor = 'rgba(0,255,224,0.18)'}
          />

          {/* Image upload */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
            <button onClick={() => fileRef.current?.click()} style={{ padding: '8px 18px', borderRadius: 8, border: '1.5px solid rgba(0,255,224,0.65)', background: 'rgba(0,255,224,0.10)', color: 'rgba(0,255,224,0.95)', fontSize: 12, cursor: 'pointer', fontFamily: 'var(--font-mono)', display: 'flex', alignItems: 'center', gap: 7, fontWeight: 600 }}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
              Attach image
            </button>
            <input ref={fileRef} type="file" accept="image/jpeg,image/png,image/gif,image/webp" style={{ display: 'none' }} onChange={e => handleImage(e.target.files?.[0])}/>
            {imagePreview && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <img src={imagePreview} alt="preview" style={{ height: 48, width: 72, objectFit: 'cover', borderRadius: 6, border: '1px solid rgba(0,255,224,0.25)' }}/>
                <button onClick={clearImage} style={{ width: 24, height: 24, borderRadius: 5, border: '1px solid rgba(255,100,100,0.3)', background: 'rgba(255,100,100,0.08)', color: '#FF6B6B', fontSize: 12, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>✕</button>
                <span style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>{imageFile?.name}</span>
              </div>
            )}
            <span style={{ fontSize: 11, color: 'var(--text-muted)', marginLeft: 'auto' }}>
              {imageFile ? 'All 5 models respond — DeepSeek & Mistral use AI image description' : 'Optional — attach a chart, equation, or problem statement'}
            </span>
          </div>

          {error && (
            <div style={{ color: '#FF6B6B', fontSize: 13, fontFamily: 'var(--font-mono)', padding: '8px 12px', background: 'rgba(255,107,107,0.08)', borderRadius: 7, border: '1px solid rgba(255,107,107,0.2)' }}>{error}</div>
          )}

          <button
            onClick={submit}
            disabled={loading || question.trim().length < 5}
            style={{ alignSelf: 'flex-start', padding: '12px 36px', borderRadius: 9, border: '1.5px solid #00FFE0', background: (loading || question.trim().length < 5) ? 'transparent' : 'rgba(0,255,224,0.10)', color: (loading || question.trim().length < 5) ? 'var(--text-muted)' : '#00FFE0', fontSize: 13, fontWeight: 700, cursor: (loading || question.trim().length < 5) ? 'not-allowed' : 'pointer', fontFamily: 'var(--font-mono)', letterSpacing: '0.08em', transition: 'all 0.18s' }}
          >
            {loading ? 'QUERYING 5 MODELS...' : 'RUN COMPARISON'}
          </button>
        </motion.div>

        {/* Response grid */}
        <AnimatePresence mode="wait">
          {(loading || responses) && (
            <motion.div key={loading ? 'skeletons' : 'responses'} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.3 }}>
              {/* Divergence banner */}
              {!loading && divergence && <DivergenceBanner divergence={divergence} />}

              <div style={{ display: 'flex', flexDirection: 'column', gap: 18, marginBottom: 32 }}>
                {loading
                  ? MODEL_ORDER.map((_, i) => <SkeletonCard key={i} index={i} />)
                  : MODEL_ORDER.map(id => {
                      const resp = responses.find(r => r.model_id === id)
                      if (!resp) return null
                      return (
                        <ResponseCard
                          key={id}
                          resp={resp}
                          divergenceStatus={divergence?.modelStatus?.[id] || 'none'}
                          voted={voted}
                          onVote={handleVote}
                          voteSubmitted={voteSubmitted}
                          aggregateData={aggregateData}
                          hasImage={!!imageFile}
                        />
                      )
                    })
                }
              </div>

              {/* Vote submitted message */}
              {voteSubmitted && (
                <motion.div initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }} style={{ background: 'rgba(0,255,224,0.06)', border: '1px solid rgba(0,255,224,0.3)', borderRadius: 10, padding: '14px 24px', color: '#00FFE0', fontFamily: 'var(--font-mono)', fontSize: 13, textAlign: 'center', marginBottom: 24 }}>
                  Vote recorded for{' '}
                  <strong style={{ color: MODEL_META[voted]?.color || '#00FFE0' }}>
                    {MODEL_META[voted]?.name || voted}
                  </strong>. Thank you for contributing to the research.
                </motion.div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

      </div>
    </section>
  )
}
