import { useState, useRef } from 'react'
import { motion, AnimatePresence } from 'motion/react'

const API_BASE = 'http://localhost:8000'

const MODEL_META = {
  claude:   { name: 'Claude Sonnet 4.6', color: '#00CED1', initials: 'CL', vision: true },
  chatgpt:  { name: 'GPT-4.1',           color: '#7FFFD4', initials: 'GP', vision: true },
  gemini:   { name: 'Gemini 2.5 Flash',  color: '#FF6B6B', initials: 'GM', vision: true },
  deepseek: { name: 'DeepSeek-V3',       color: '#4A90D9', initials: 'DS', vision: false },
  mistral:  { name: 'Mistral Large',     color: '#A78BFA', initials: 'MS', vision: false },
}

const MODEL_ORDER = ['claude', 'chatgpt', 'gemini', 'deepseek', 'mistral']

function SkeletonCard({ index }) {
  const meta = MODEL_META[MODEL_ORDER[index]]
  return (
    <div style={{
      background: 'rgba(0,255,224,0.03)',
      border: `1px solid ${meta.color}33`,
      borderRadius: 12,
      padding: '20px 24px',
      display: 'flex',
      flexDirection: 'column',
      gap: 12,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <div style={{
          width: 36, height: 36, borderRadius: 8,
          background: meta.color + '22',
          border: `1px solid ${meta.color}55`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 11, fontFamily: 'var(--font-mono)', color: meta.color,
          fontWeight: 700,
        }}>{meta.initials}</div>
        <div>
          <div style={{ fontSize: 13, fontWeight: 600, color: '#e8f4f8' }}>{meta.name}</div>
          <div style={{
            height: 8, width: 60, borderRadius: 4,
            background: 'rgba(255,255,255,0.08)',
            marginTop: 4,
            animation: 'pulse 1.4s ease-in-out infinite',
          }}/>
        </div>
      </div>
      {[100, 85, 95, 70].map((w, i) => (
        <div key={i} style={{
          height: 8, width: `${w}%`, borderRadius: 4,
          background: 'rgba(255,255,255,0.06)',
          animation: `pulse 1.4s ease-in-out ${i * 0.15}s infinite`,
        }}/>
      ))}
    </div>
  )
}

function ResponseCard({ resp, voted, onVote, hasImage }) {
  const meta = MODEL_META[resp.model_id] || { name: resp.model_name, color: '#8BAFC0', initials: '?', vision: true }
  const isVoted = voted === resp.model_id
  const noVision = hasImage && !meta.vision
  const isError = !!resp.error

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      style={{
        background: isVoted ? `${meta.color}12` : 'rgba(0,255,224,0.03)',
        border: `1.5px solid ${isVoted ? meta.color : meta.color + '33'}`,
        borderRadius: 12,
        padding: '20px 24px',
        display: 'flex',
        flexDirection: 'column',
        gap: 14,
        transition: 'border-color 0.2s, background 0.2s',
        cursor: 'default',
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 36, height: 36, borderRadius: 8,
            background: meta.color + '22',
            border: `1px solid ${meta.color}55`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 11, fontFamily: 'var(--font-mono)', color: meta.color, fontWeight: 700,
          }}>{meta.initials}</div>
          <div>
            <div style={{ fontSize: 13, fontWeight: 600, color: '#e8f4f8' }}>{meta.name}</div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              {resp.latency_ms > 0 ? `${resp.latency_ms.toLocaleString()} ms` : '—'}
              {!meta.vision && <span style={{ marginLeft: 8, color: '#A78BFA' }}>text-only</span>}
            </div>
          </div>
        </div>
        {!isError && !noVision && (
          <button
            onClick={() => onVote(resp.model_id)}
            style={{
              padding: '6px 16px',
              borderRadius: 7,
              border: `1.5px solid ${isVoted ? meta.color : meta.color + '66'}`,
              background: isVoted ? meta.color + '22' : 'transparent',
              color: isVoted ? meta.color : 'var(--text-muted)',
              fontSize: 12,
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.18s',
              fontFamily: 'var(--font-mono)',
              letterSpacing: '0.04em',
            }}
          >
            {isVoted ? 'VOTED' : 'BEST'}
          </button>
        )}
      </div>

      {/* Body */}
      {noVision ? (
        <div style={{ color: '#A78BFA', fontSize: 13, fontStyle: 'italic' }}>
          Image input not supported — text-only model. Submit without image to get a response.
        </div>
      ) : isError ? (
        <div style={{ color: '#FF6B6B', fontSize: 13, fontFamily: 'var(--font-mono)' }}>
          Error: {resp.error}
        </div>
      ) : (
        <div style={{
          fontSize: 13.5,
          lineHeight: 1.75,
          color: '#c8dce8',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
          maxHeight: 420,
          overflowY: 'auto',
          paddingRight: 4,
        }}>
          {resp.response}
        </div>
      )}
    </motion.div>
  )
}

function VotePanel({ responses, question, sessionId, hasImage, onVoteDone }) {
  const [voted, setVoted] = useState(null)
  const [reason, setReason] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  async function handleVote(modelId) {
    setVoted(modelId)
  }

  async function submitVote() {
    if (!voted) return
    setSubmitting(true)
    try {
      await fetch(`${API_BASE}/api/user-study/vote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          question,
          voted_model: voted,
          reason: reason.trim() || null,
          had_image: hasImage,
        }),
      })
      setSubmitted(true)
      onVoteDone(voted)
    } catch (e) {
      console.error('Vote submit failed:', e)
    } finally {
      setSubmitting(false)
    }
  }

  if (submitted) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.97 }}
        animate={{ opacity: 1, scale: 1 }}
        style={{
          background: 'rgba(0,255,224,0.06)',
          border: '1px solid rgba(0,255,224,0.3)',
          borderRadius: 10,
          padding: '16px 24px',
          color: '#00FFE0',
          fontFamily: 'var(--font-mono)',
          fontSize: 13,
          textAlign: 'center',
        }}
      >
        Vote recorded for <strong style={{ color: MODEL_META[voted]?.color || '#00FFE0' }}>
          {MODEL_META[voted]?.name || voted}
        </strong>. Thank you for contributing.
      </motion.div>
    )
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      <div style={{ color: 'var(--text-muted)', fontSize: 12, fontFamily: 'var(--font-mono)', letterSpacing: '0.06em' }}>
        STEP 2 — SELECT BEST RESPONSE
      </div>
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        {MODEL_ORDER.map(id => {
          const resp = responses.find(r => r.model_id === id)
          if (!resp || resp.error || (hasImage && !MODEL_META[id].vision)) return null
          const meta = MODEL_META[id]
          const isVoted = voted === id
          return (
            <button
              key={id}
              onClick={() => handleVote(id)}
              style={{
                padding: '8px 18px',
                borderRadius: 8,
                border: `1.5px solid ${isVoted ? meta.color : meta.color + '55'}`,
                background: isVoted ? meta.color + '1a' : 'transparent',
                color: isVoted ? meta.color : 'var(--text-muted)',
                fontSize: 12,
                fontWeight: 700,
                cursor: 'pointer',
                transition: 'all 0.18s',
                fontFamily: 'var(--font-mono)',
              }}
            >
              {meta.name}
            </button>
          )
        })}
      </div>
      <textarea
        value={reason}
        onChange={e => setReason(e.target.value)}
        placeholder="Optional: why was this response better? (1-2 sentences)"
        rows={2}
        style={{
          background: 'rgba(0,255,224,0.04)',
          border: '1px solid rgba(0,255,224,0.15)',
          borderRadius: 8,
          padding: '10px 14px',
          color: '#e8f4f8',
          fontSize: 13,
          resize: 'vertical',
          fontFamily: 'inherit',
          outline: 'none',
          width: '100%',
          boxSizing: 'border-box',
        }}
      />
      <button
        onClick={submitVote}
        disabled={!voted || submitting}
        style={{
          alignSelf: 'flex-start',
          padding: '10px 28px',
          borderRadius: 8,
          border: '1.5px solid #00FFE0',
          background: voted ? 'rgba(0,255,224,0.12)' : 'transparent',
          color: voted ? '#00FFE0' : 'var(--text-muted)',
          fontSize: 13,
          fontWeight: 700,
          cursor: voted ? 'pointer' : 'not-allowed',
          fontFamily: 'var(--font-mono)',
          letterSpacing: '0.06em',
          transition: 'all 0.18s',
        }}
      >
        {submitting ? 'SUBMITTING...' : 'SUBMIT VOTE'}
      </button>
    </div>
  )
}

function AggregateStats() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [fetched, setFetched] = useState(false)

  async function load() {
    if (fetched) return
    setLoading(true)
    try {
      const r = await fetch(`${API_BASE}/api/user-study/results`)
      const d = await r.json()
      setData(d)
    } catch {}
    setLoading(false)
    setFetched(true)
  }

  if (!fetched) {
    return (
      <button
        onClick={load}
        style={{
          padding: '8px 20px',
          borderRadius: 8,
          border: '1px solid rgba(0,255,224,0.25)',
          background: 'transparent',
          color: 'var(--text-muted)',
          fontSize: 12,
          cursor: 'pointer',
          fontFamily: 'var(--font-mono)',
        }}
      >
        View aggregate vote results
      </button>
    )
  }

  if (loading) return <div style={{ color: 'var(--text-muted)', fontSize: 12 }}>Loading...</div>
  if (!data || data.total_votes === 0) return (
    <div style={{ color: 'var(--text-muted)', fontSize: 12, fontFamily: 'var(--font-mono)' }}>
      No votes yet.
    </div>
  )

  const dist = data.vote_distribution
  const max = Math.max(...Object.values(dist), 1)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      <div style={{ color: 'var(--text-muted)', fontSize: 11, fontFamily: 'var(--font-mono)', letterSpacing: '0.06em' }}>
        AGGREGATE VOTES — {data.total_votes} total
      </div>
      {Object.entries(dist).map(([id, count]) => {
        const meta = MODEL_META[id] || { name: id, color: '#8BAFC0' }
        const pct = Math.round((count / data.total_votes) * 100)
        return (
          <div key={id} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 100, fontSize: 11, color: meta.color, fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
              {meta.name}
            </div>
            <div style={{
              flex: 1, height: 12, borderRadius: 6,
              background: 'rgba(255,255,255,0.06)',
              overflow: 'hidden',
            }}>
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${(count / max) * 100}%` }}
                transition={{ duration: 0.6, ease: 'easeOut' }}
                style={{ height: '100%', background: meta.color + 'cc', borderRadius: 6 }}
              />
            </div>
            <div style={{ width: 52, textAlign: 'right', fontSize: 11, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              {count} ({pct}%)
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default function UserStudy() {
  const [question, setQuestion] = useState('')
  const [imageFile, setImageFile] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [responses, setResponses] = useState(null)
  const [sessionId, setSessionId] = useState(null)
  const [voteWinner, setVoteWinner] = useState(null)
  const [error, setError] = useState(null)
  const fileRef = useRef()

  function handleImage(file) {
    if (!file) return
    setImageFile(file)
    const reader = new FileReader()
    reader.onload = e => setImagePreview(e.target.result)
    reader.readAsDataURL(file)
  }

  function clearImage() {
    setImageFile(null)
    setImagePreview(null)
    if (fileRef.current) fileRef.current.value = ''
  }

  async function submit() {
    const q = question.trim()
    if (q.length < 5) { setError('Question too short (min 5 characters).'); return }
    if (q.length > 2000) { setError('Question too long (max 2000 characters).'); return }
    setError(null)
    setLoading(true)
    setResponses(null)
    setSessionId(null)
    setVoteWinner(null)

    const fd = new FormData()
    fd.append('question', q)
    if (imageFile) fd.append('image', imageFile)

    try {
      const r = await fetch(`${API_BASE}/api/user-study`, { method: 'POST', body: fd })
      if (r.status === 429) { setError('Rate limit reached (10 requests/hour per IP). Try again later.'); return }
      if (!r.ok) {
        const d = await r.json().catch(() => ({}))
        setError(d.detail || `Server error: ${r.status}`)
        return
      }
      const data = await r.json()
      setResponses(data.responses)
      setSessionId(data.session_id)
    } catch (e) {
      setError('Failed to reach backend. Is the server running on port 8000?')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section id="user-study" style={{ padding: '80px 0', position: 'relative', zIndex: 1 }}>
      <div style={{ maxWidth: 1100, margin: '0 auto', padding: '0 32px' }}>

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          style={{ marginBottom: 48 }}
        >
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: 8,
            padding: '5px 14px', borderRadius: 20,
            border: '1px solid rgba(0,255,224,0.25)',
            background: 'rgba(0,255,224,0.07)',
            fontSize: 11, letterSpacing: '0.1em',
            color: '#00FFE0', fontFamily: 'var(--font-mono)',
            marginBottom: 20,
          }}>
            LIVE COMPARISON
          </div>
          <h2 style={{
            fontSize: 36, fontWeight: 700, margin: '0 0 14px',
            background: 'linear-gradient(135deg, #00FFE0 0%, #00B4D8 60%, #A78BFA 100%)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
          }}>
            User Study
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: 15, lineHeight: 1.7, maxWidth: 640, margin: 0 }}>
            Submit a Bayesian or inferential statistics question. All 5 models respond in parallel.
            Vote for the explanation you find most useful — results feed the research.
          </p>
        </motion.div>

        {/* Input panel */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.1 }}
          style={{
            background: 'rgba(0,255,224,0.03)',
            border: '1px solid rgba(0,255,224,0.15)',
            borderRadius: 14,
            padding: '28px 32px',
            marginBottom: 36,
            display: 'flex',
            flexDirection: 'column',
            gap: 16,
          }}
        >
          <div style={{ color: 'var(--text-muted)', fontSize: 11, fontFamily: 'var(--font-mono)', letterSpacing: '0.06em' }}>
            STEP 1 — YOUR QUESTION
          </div>

          <textarea
            value={question}
            onChange={e => setQuestion(e.target.value)}
            placeholder="e.g. A coin is flipped 10 times and lands heads 7 times. Using a Beta(2,2) prior, what is the posterior distribution and its mean?"
            rows={5}
            style={{
              background: 'rgba(0,255,224,0.04)',
              border: '1px solid rgba(0,255,224,0.18)',
              borderRadius: 9,
              padding: '14px 16px',
              color: '#e8f4f8',
              fontSize: 14,
              lineHeight: 1.7,
              resize: 'vertical',
              fontFamily: 'inherit',
              outline: 'none',
              width: '100%',
              boxSizing: 'border-box',
              transition: 'border-color 0.18s',
            }}
            onFocus={e => e.target.style.borderColor = 'rgba(0,255,224,0.45)'}
            onBlur={e => e.target.style.borderColor = 'rgba(0,255,224,0.18)'}
          />

          {/* Image upload */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
            <button
              onClick={() => fileRef.current?.click()}
              style={{
                padding: '8px 18px',
                borderRadius: 8,
                border: '1px solid rgba(0,255,224,0.25)',
                background: 'transparent',
                color: 'var(--text-muted)',
                fontSize: 12,
                cursor: 'pointer',
                fontFamily: 'var(--font-mono)',
                display: 'flex', alignItems: 'center', gap: 7,
              }}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/>
                <polyline points="21 15 16 10 5 21"/>
              </svg>
              Attach image
            </button>
            <input
              ref={fileRef}
              type="file"
              accept="image/jpeg,image/png,image/gif,image/webp"
              style={{ display: 'none' }}
              onChange={e => handleImage(e.target.files?.[0])}
            />
            {imagePreview && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <img
                  src={imagePreview}
                  alt="preview"
                  style={{ height: 48, width: 72, objectFit: 'cover', borderRadius: 6, border: '1px solid rgba(0,255,224,0.25)' }}
                />
                <button
                  onClick={clearImage}
                  style={{
                    width: 24, height: 24, borderRadius: 5,
                    border: '1px solid rgba(255,100,100,0.3)',
                    background: 'rgba(255,100,100,0.08)',
                    color: '#FF6B6B',
                    fontSize: 12,
                    cursor: 'pointer',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                  }}
                >✕</button>
                <span style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                  {imageFile?.name}
                </span>
              </div>
            )}
            <span style={{ fontSize: 11, color: 'var(--text-muted)', marginLeft: 'auto' }}>
              {imageFile ? 'Vision: Claude, GPT-4.1, Gemini only' : 'Optional — attach a chart, equation, or problem statement'}
            </span>
          </div>

          {error && (
            <div style={{ color: '#FF6B6B', fontSize: 13, fontFamily: 'var(--font-mono)', padding: '8px 12px', background: 'rgba(255,107,107,0.08)', borderRadius: 7, border: '1px solid rgba(255,107,107,0.2)' }}>
              {error}
            </div>
          )}

          <button
            onClick={submit}
            disabled={loading || question.trim().length < 5}
            style={{
              alignSelf: 'flex-start',
              padding: '12px 36px',
              borderRadius: 9,
              border: '1.5px solid #00FFE0',
              background: (loading || question.trim().length < 5) ? 'transparent' : 'rgba(0,255,224,0.10)',
              color: (loading || question.trim().length < 5) ? 'var(--text-muted)' : '#00FFE0',
              fontSize: 13,
              fontWeight: 700,
              cursor: (loading || question.trim().length < 5) ? 'not-allowed' : 'pointer',
              fontFamily: 'var(--font-mono)',
              letterSpacing: '0.08em',
              transition: 'all 0.18s',
            }}
          >
            {loading ? 'QUERYING 5 MODELS...' : 'RUN COMPARISON'}
          </button>
        </motion.div>

        {/* Response grid */}
        <AnimatePresence mode="wait">
          {(loading || responses) && (
            <motion.div
              key={loading ? 'skeletons' : 'responses'}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
            >
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
                gap: 18,
                marginBottom: 32,
              }}>
                {loading
                  ? MODEL_ORDER.map((_, i) => <SkeletonCard key={i} index={i} />)
                  : MODEL_ORDER.map(id => {
                      const resp = responses.find(r => r.model_id === id)
                      if (!resp) return null
                      return (
                        <ResponseCard
                          key={id}
                          resp={resp}
                          voted={voteWinner}
                          onVote={id => !voteWinner && setVoteWinner(id)}
                          hasImage={!!imageFile}
                        />
                      )
                    })
                }
              </div>

              {/* Vote panel */}
              {responses && !loading && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  style={{
                    background: 'rgba(0,255,224,0.03)',
                    border: '1px solid rgba(0,255,224,0.15)',
                    borderRadius: 14,
                    padding: '24px 32px',
                    marginBottom: 24,
                  }}
                >
                  <VotePanel
                    responses={responses}
                    question={question.trim()}
                    sessionId={sessionId}
                    hasImage={!!imageFile}
                    onVoteDone={id => setVoteWinner(id)}
                  />
                </motion.div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Aggregate stats */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          style={{
            background: 'rgba(0,255,224,0.02)',
            border: '1px solid rgba(0,255,224,0.1)',
            borderRadius: 12,
            padding: '20px 28px',
          }}
        >
          <AggregateStats />
        </motion.div>

      </div>
    </section>
  )
}
