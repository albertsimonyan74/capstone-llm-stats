import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence, useInView } from 'motion/react'
import { VISUALIZATIONS, FEATURED_IDS, VIZ_FILTERS, VIZ_FILTER_MAP } from '../data/visualizations'
import summaryData from '../data/results_summary.json'

// ─── Model metadata ───────────────────────────────────────────
const MODEL_META = {
  claude:   { name: 'Claude Sonnet 4.5', provider: 'Anthropic',  color: '#CC785C', abbr: 'CL' },
  chatgpt:  { name: 'GPT-4.1',           provider: 'OpenAI',     color: '#10A37F', abbr: 'GP' },
  mistral:  { name: 'Mistral Large',     provider: 'Mistral AI', color: '#FF7043', abbr: 'MS' },
  deepseek: { name: 'DeepSeek Chat',     provider: 'DeepSeek',   color: '#4D9FFF', abbr: 'DS' },
  gemini:   { name: 'Gemini 2.5 Flash',  provider: 'Google',     color: '#8AB4F8', abbr: 'GM' },
}

const RANK_GLOW = {
  1: { color: '#FFD700', shadow: '0 0 20px rgba(255,215,0,0.5)' },
  2: { color: '#C0C0C0', shadow: '0 0 14px rgba(192,192,192,0.4)' },
  3: { color: '#CD7F32', shadow: '0 0 14px rgba(205,127,50,0.4)' },
}

const SCORE_COLOR = (v) => {
  if (v >= 0.70) return '#00FFE0'
  if (v >= 0.60) return '#7FFFD4'
  if (v >= 0.50) return '#FFB347'
  return '#FF6B6B'
}

// ─── FadeIn helper ────────────────────────────────────────────
function FadeIn({ children, delay = 0, style = {} }) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, amount: 0.1 })
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 24 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.65, delay: delay / 1000, ease: [0.22, 1, 0.36, 1] }}
      style={style}
    >
      {children}
    </motion.div>
  )
}

// ─── Leaderboard Card ─────────────────────────────────────────
function LeaderCard({ modelId, data, rank }) {
  const meta      = MODEL_META[modelId]
  const isPending = !data
  const isPartial = data && data.tasks < 171
  const rankInfo  = RANK_GLOW[rank]

  return (
    <motion.div
      whileHover={{ y: -4, boxShadow: `0 12px 40px ${meta.color}33` }}
      transition={{ type: 'spring', stiffness: 380, damping: 26 }}
      style={{
        background: 'rgba(255,255,255,0.03)',
        border: `1px solid ${isPending ? 'rgba(255,255,255,0.06)' : `${meta.color}33`}`,
        borderRadius: 14,
        padding: '20px 18px',
        position: 'relative',
        opacity: isPending ? 0.55 : 1,
      }}
    >
      {rank && !isPending && (
        <div style={{
          position: 'absolute', top: 10, right: 12,
          fontSize: 11, fontWeight: 800,
          color: rankInfo?.color || 'rgba(139,175,192,0.5)',
          textShadow: rankInfo?.shadow || 'none',
          fontFamily: 'monospace',
        }}>
          #{rank}
        </div>
      )}

      <div style={{
        width: 40, height: 40, borderRadius: 10, marginBottom: 10,
        background: `${meta.color}18`,
        border: `2px solid ${isPending ? 'rgba(255,255,255,0.1)' : meta.color}`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        color: isPending ? 'rgba(255,255,255,0.3)' : meta.color,
        fontWeight: 800, fontSize: 13,
      }}>
        {meta.abbr}
      </div>

      <div style={{ fontSize: 13, fontWeight: 700, color: isPending ? 'rgba(255,255,255,0.35)' : '#fff', marginBottom: 2 }}>
        {meta.name}
      </div>
      <div style={{ fontSize: 10, color: 'rgba(255,255,255,0.35)', marginBottom: 14 }}>
        {meta.provider}
      </div>

      {isPending ? (
        <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.25)', fontStyle: 'italic' }}>
          Results pending
        </div>
      ) : isPartial ? (
        <>
          <div style={{ fontSize: 26, fontWeight: 800, color: meta.color, lineHeight: 1, marginBottom: 6 }}>
            {(data.avg_score * 100).toFixed(1)}%
          </div>
          <div style={{ fontSize: 10, fontWeight: 700, color: '#FF9A3C',
                        background: 'rgba(255,154,60,0.1)', borderRadius: 8,
                        padding: '2px 8px', display: 'inline-block' }}>
            PARTIAL · {data.tasks}/171
          </div>
        </>
      ) : (
        <>
          <div style={{ fontSize: 30, fontWeight: 800, color: SCORE_COLOR(data.avg_score), lineHeight: 1, marginBottom: 8 }}>
            {(data.avg_score * 100).toFixed(1)}%
          </div>

          <div style={{ marginBottom: 10 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
              <span style={{ color: 'rgba(255,255,255,0.4)', fontSize: 9, fontWeight: 700, letterSpacing: '0.08em' }}>PASS RATE</span>
              <span style={{ color: meta.color, fontSize: 10, fontWeight: 700 }}>{(data.pass_rate * 100).toFixed(0)}%</span>
            </div>
            <div style={{ height: 3, background: 'rgba(255,255,255,0.06)', borderRadius: 2 }}>
              <motion.div
                style={{ height: '100%', background: meta.color, borderRadius: 2 }}
                initial={{ width: 0 }}
                whileInView={{ width: `${data.pass_rate * 100}%` }}
                viewport={{ once: true }}
                transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
              />
            </div>
          </div>

          <div style={{ fontSize: 10, color: 'rgba(255,255,255,0.35)' }}>
            Latency: {(data.avg_latency / 1000).toFixed(1)}s avg
          </div>
        </>
      )}
    </motion.div>
  )
}

// ─── VizCard (standard gallery card) ─────────────────────────
function VizCard({ viz, index, setFullImg, onOpenGif, featured = false }) {
  const [imgLoaded, setImgLoaded] = useState(false)
  const [iframeOpen, setIframeOpen] = useState(false)
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, amount: 0.1 })
  const hasInteractive = viz.interactive !== null

  return (
      <motion.div
        ref={ref}
        initial={{ opacity: 0, y: 32 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.6, delay: (index % 4) * 0.08, ease: [0.22, 1, 0.36, 1] }}
        whileHover={{ y: -4, boxShadow: featured ? '0 16px 48px rgba(0,255,224,0.2)' : '0 12px 40px rgba(0,255,224,0.15)' }}
        style={{
          background: featured ? 'rgba(0,255,224,0.025)' : 'rgba(255,255,255,0.025)',
          border: featured ? '1px solid rgba(0,255,224,0.18)' : '1px solid rgba(0,255,224,0.1)',
          borderRadius: 16,
          overflow: 'hidden',
          transition: 'border-color 0.2s',
          cursor: 'none',
        }}
        data-hover="true"
      >
        {/* Image preview */}
        <div style={{ position: 'relative', aspectRatio: featured ? '16/9' : '16/10', overflow: 'hidden', background: '#050a16' }}>
          <img
            src={viz.png}
            alt={viz.title}
            loading="lazy"
            onLoad={() => setImgLoaded(true)}
            style={{
              width: '100%', height: '100%', objectFit: 'cover',
              opacity: imgLoaded ? 1 : 0,
              transition: 'opacity 0.4s ease',
            }}
          />
          {!imgLoaded && (
            <div style={{
              position: 'absolute', inset: 0, display: 'flex',
              alignItems: 'center', justifyContent: 'center',
              flexDirection: 'column', gap: 8,
            }}>
              <div style={{ width: 32, height: 32, border: '2px solid rgba(0,255,224,0.2)',
                            borderTop: '2px solid rgba(0,255,224,0.7)', borderRadius: '50%',
                            animation: 'spin 1s linear infinite' }}/>
              <div style={{ color: 'rgba(0,255,224,0.4)', fontSize: 11 }}>Loading…</div>
            </div>
          )}

          {/* Type badge */}
          <div style={{
            position: 'absolute', top: 10, right: 10,
            background: 'rgba(0,10,20,0.8)',
            border: '1px solid rgba(0,255,224,0.3)',
            backdropFilter: 'blur(6px)',
            borderRadius: 5, padding: '2px 8px',
            fontSize: 10, fontWeight: 700, color: '#00FFE0', letterSpacing: '0.07em',
          }}>
            {viz.type}
          </div>

          {/* Featured badge */}
          {featured && (
            <div style={{
              position: 'absolute', top: 10, left: 10,
              background: 'rgba(0,255,224,0.15)',
              border: '1px solid rgba(0,255,224,0.4)',
              backdropFilter: 'blur(6px)',
              borderRadius: 5, padding: '2px 8px',
              fontSize: 9, fontWeight: 700, color: '#00FFE0', letterSpacing: '0.1em',
            }}>
              KEY INSIGHT
            </div>
          )}

          {/* Zoom overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            whileHover={{ opacity: 1 }}
            onClick={() => setFullImg(viz.png)}
            style={{
              position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.4)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 28, cursor: 'none',
            }}
          >
            <span style={{ color: 'rgba(0,255,224,0.9)', textShadow: '0 0 20px rgba(0,255,224,0.6)' }}>⊕</span>
          </motion.div>
        </div>

        {/* Card body */}
        <div style={{ padding: featured ? '18px 20px 20px' : '16px 18px 18px' }}>
          <div style={{ fontSize: featured ? 16 : 15, fontWeight: 700, color: '#fff', marginBottom: 3 }}>
            {viz.title}
          </div>
          <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', marginBottom: 12, letterSpacing: '0.02em' }}>
            {viz.subtitle}
          </div>

          {/* Description */}
          <div style={{
            fontSize: 12, color: 'rgba(255,255,255,0.6)', lineHeight: 1.65, marginBottom: 12,
          }}>
            {viz.description}
          </div>

          {/* Insight callout */}
          <div style={{
            background: 'rgba(0,255,224,0.05)',
            borderLeft: '2px solid rgba(0,255,224,0.45)',
            borderRadius: '0 6px 6px 0',
            padding: '8px 12px',
            fontSize: 11.5,
            color: 'rgba(255,255,255,0.75)',
            lineHeight: 1.6,
            marginBottom: 14,
          }}>
            <span style={{ color: 'rgba(0,255,224,0.7)', fontWeight: 700, fontSize: 10, letterSpacing: '0.07em', display: 'block', marginBottom: 3 }}>KEY FINDING</span>
            {viz.insight}
          </div>

          {/* Action buttons */}
          <div style={{ display: 'flex', gap: 8 }}>
            <button
              data-hover="true"
              onClick={() => setFullImg(viz.png)}
              style={{
                flex: 1, padding: '9px 0',
                background: 'transparent',
                border: '1px solid rgba(0,255,224,0.2)',
                borderRadius: 7, color: 'rgba(0,255,224,0.75)',
                fontSize: 12, fontWeight: 600, cursor: 'none',
                transition: 'border-color 0.18s, color 0.18s, background 0.18s',
              }}
              onMouseEnter={e => {
                e.currentTarget.style.borderColor = 'rgba(0,255,224,0.55)'
                e.currentTarget.style.color = '#00FFE0'
                e.currentTarget.style.background = 'rgba(0,255,224,0.06)'
              }}
              onMouseLeave={e => {
                e.currentTarget.style.borderColor = 'rgba(0,255,224,0.2)'
                e.currentTarget.style.color = 'rgba(0,255,224,0.75)'
                e.currentTarget.style.background = 'transparent'
              }}
            >
              View Static
            </button>

            {hasInteractive ? (
              <button
                data-hover="true"
                onClick={() => viz.isGif ? onOpenGif(viz.interactive) : setIframeOpen(v => !v)}
                style={{
                  flex: 1, padding: '9px 0',
                  background: iframeOpen && !viz.isGif ? 'rgba(0,255,224,0.18)' : 'rgba(0,255,224,0.1)',
                  border: `1px solid ${iframeOpen && !viz.isGif ? 'rgba(0,255,224,0.55)' : 'rgba(0,255,224,0.3)'}`,
                  borderRadius: 7, color: '#00FFE0',
                  fontSize: 12, fontWeight: 600, cursor: 'none',
                  transition: 'background 0.18s, border-color 0.18s',
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.background = 'rgba(0,255,224,0.18)'
                  e.currentTarget.style.borderColor = 'rgba(0,255,224,0.5)'
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.background = iframeOpen && !viz.isGif ? 'rgba(0,255,224,0.18)' : 'rgba(0,255,224,0.1)'
                  e.currentTarget.style.borderColor = iframeOpen && !viz.isGif ? 'rgba(0,255,224,0.55)' : 'rgba(0,255,224,0.3)'
                }}
              >
                {viz.isGif ? 'View Animation ▶' : iframeOpen ? 'Close Interactive ▲' : 'Open Interactive ▼'}
              </button>
            ) : (
              <div
                title="No interactive version — static only"
                style={{
                  flex: 1, padding: '9px 0',
                  background: 'rgba(255,255,255,0.02)',
                  border: '1px solid rgba(255,255,255,0.07)',
                  borderRadius: 7, color: 'rgba(255,255,255,0.22)',
                  fontSize: 12, fontWeight: 600, textAlign: 'center',
                  userSelect: 'none',
                }}
              >
                Static only
              </div>
            )}
          </div>

          {/* Inline interactive iframe panel */}
          <AnimatePresence>
            {iframeOpen && !viz.isGif && viz.interactive && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 520 }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
                style={{ overflow: 'hidden', borderTop: '1px solid rgba(0,255,224,0.15)', marginTop: 12 }}
              >
                <iframe
                  src={viz.interactive}
                  title={`${viz.title} interactive`}
                  style={{ width: '100%', height: 520, border: 'none', background: '#050a16', borderRadius: '0 0 12px 12px' }}
                  loading="lazy"
                />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
  )
}

// ─── Main VizGallery Component ────────────────────────────────
export default function VizGallery({ setFullImg, onOpenGif }) {
  const [activeFilter, setActiveFilter] = useState('All')
  const [galleryExpanded, setGalleryExpanded] = useState(false)
  const [sectionOpen, setSectionOpen] = useState(false)
  const GALLERY_PREVIEW = 6
  const summary = summaryData

  const allModels = ['claude', 'chatgpt', 'mistral', 'deepseek', 'gemini']
  const complete  = summary.models_complete
  const rankings  = [...complete].sort((a, b) =>
    (summary.by_model[b]?.avg_score || 0) - (summary.by_model[a]?.avg_score || 0)
  )
  const ordered = [
    ...rankings,
    ...allModels.filter(m => !complete.includes(m)),
  ]

  const featuredViz = VISUALIZATIONS.filter(v => FEATURED_IDS.includes(v.id))
  const galleryViz  = VISUALIZATIONS.filter(v => !FEATURED_IDS.includes(v.id))
  const filtered    = activeFilter === 'All'
    ? galleryViz
    : galleryViz.filter(VIZ_FILTER_MAP[activeFilter])

  // Also allow filtering featured vizs when user picks a filter
  const filteredFeatured = activeFilter === 'All'
    ? featuredViz
    : featuredViz.filter(VIZ_FILTER_MAP[activeFilter])

  const showFeatured = filteredFeatured.length > 0

  return (
    <>
      {/* ── Section header — click to toggle gallery ────────── */}
      <FadeIn>
        <motion.div
          data-hover="true"
          onClick={() => setSectionOpen(v => !v)}
          style={{
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            marginBottom: 8, flexWrap: 'wrap', gap: 12,
            cursor: 'none', userSelect: 'none',
          }}
          whileHover={{ opacity: 0.9 }}
        >
          <div>
            <div style={{ color: 'rgba(0,255,224,0.55)', fontSize: 10, fontWeight: 700, letterSpacing: '0.2em', marginBottom: 6 }}>
              // R ANALYSIS · GGPLOT2 + PLOTLY
            </div>
            <h2 style={{ fontSize: 'clamp(28px,3.5vw,42px)', fontWeight: 700, color: '#fff', margin: 0, lineHeight: 1.2 }}>
              Benchmark{' '}
              <span style={{ background: 'linear-gradient(135deg,#00FFE0,#00B4D8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                Visualizations
              </span>
            </h2>
          </div>
          <motion.button
            data-hover="true"
            whileTap={{ scale: 0.95 }}
            style={{
              padding: '10px 24px', borderRadius: 10, cursor: 'none',
              background: sectionOpen ? 'rgba(0,255,224,0.1)' : 'rgba(0,255,224,0.05)',
              border: `1px solid ${sectionOpen ? 'rgba(0,255,224,0.5)' : 'rgba(0,255,224,0.2)'}`,
              color: '#00FFE0', fontSize: 13, fontWeight: 700,
              display: 'flex', alignItems: 'center', gap: 8,
              transition: 'all 0.2s',
            }}
          >
            <span style={{ fontSize: 10, color: 'rgba(255,255,255,0.5)', fontFamily: 'monospace' }}>{VISUALIZATIONS.length} charts</span>
            {sectionOpen ? 'Collapse ▲' : 'Explore Gallery ▼'}
          </motion.button>
        </motion.div>
        <motion.div
          initial={{ scaleX: 0 }}
          whileInView={{ scaleX: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          style={{
            width: 64, height: 3, background: 'linear-gradient(90deg,#00FFE0,#00B4D8)',
            borderRadius: 2, marginBottom: sectionOpen ? 40 : 12, transformOrigin: 'left',
            transition: 'margin-bottom 0.3s',
          }}
        />
      </FadeIn>

      <AnimatePresence>
        {!sectionOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{ textAlign: 'center', padding: '32px 0 16px', color: 'rgba(255,255,255,0.3)', fontSize: 13 }}
          >
            Click "Explore Gallery" to view {VISUALIZATIONS.length} R-generated charts and interactive dashboards
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
      {sectionOpen && (
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 8 }}
        transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
      >

      {/* ── Leaderboard ─────────────────────────────────────── */}
      <FadeIn delay={60}>
        <div style={{ color: 'rgba(0,255,224,0.55)', fontSize: 10, fontWeight: 700, letterSpacing: '0.2em', marginBottom: 16 }}>
          MODEL LEADERBOARD
        </div>
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={{ visible: { transition: { staggerChildren: 0.08, delayChildren: 0.1 } } }}
          style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 14, marginBottom: 52 }}
        >
          {ordered.map((m) => {
            const rank = rankings.indexOf(m) + 1
            return (
              <motion.div
                key={m}
                variants={{ hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }}
              >
                <LeaderCard
                  modelId={m}
                  data={summary.by_model[m]}
                  rank={complete.includes(m) ? rank : null}
                />
              </motion.div>
            )
          })}
        </motion.div>
      </FadeIn>

      {/* ── Filter tabs ──────────────────────────────────────── */}
      <FadeIn delay={100}>
        <div style={{ display: 'flex', gap: 8, marginBottom: 28, flexWrap: 'wrap' }}>
          {VIZ_FILTERS.map(f => (
            <motion.button
              key={f}
              data-hover="true"
              onClick={() => setActiveFilter(f)}
              whileTap={{ scale: 0.95 }}
              style={{
                padding: '7px 18px', borderRadius: 8,
                background: activeFilter === f ? 'rgba(0,255,224,0.12)' : 'transparent',
                border: `1px solid ${activeFilter === f ? 'rgba(0,255,224,0.5)' : 'rgba(0,255,224,0.12)'}`,
                color: activeFilter === f ? '#00FFE0' : 'rgba(255,255,255,0.45)',
                fontSize: 13, fontWeight: 600, cursor: 'none',
                transition: 'all 0.18s',
              }}
            >
              {f}
              {f === 'All' && (
                <span style={{ marginLeft: 6, fontSize: 10, color: 'rgba(0,255,224,0.5)' }}>
                  {VISUALIZATIONS.length}
                </span>
              )}
            </motion.button>
          ))}
        </div>
      </FadeIn>

      <AnimatePresence mode="wait">
        <motion.div
          key={activeFilter}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
        >
          {/* ── Featured 2×2 grid ───────────────────────────── */}
          {showFeatured && (
            <div style={{ marginBottom: 40 }}>
              <div style={{
                color: 'rgba(0,255,224,0.55)', fontSize: 10, fontWeight: 700,
                letterSpacing: '0.2em', marginBottom: 16,
              }}>
                KEY VISUALIZATIONS
              </div>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(420px, 1fr))',
                gap: 24,
              }}>
                {filteredFeatured.map((viz, i) => (
                  <VizCard key={viz.id} viz={viz} index={i} setFullImg={setFullImg} onOpenGif={onOpenGif} featured />
                ))}
              </div>
            </div>
          )}

          {/* ── Remaining gallery ────────────────────────────── */}
          {filtered.length > 0 && (
            <div>
              {showFeatured && activeFilter === 'All' && (
                <div style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  marginBottom: 16,
                }}>
                  <div style={{ color: 'rgba(0,255,224,0.55)', fontSize: 10, fontWeight: 700, letterSpacing: '0.2em' }}>
                    FULL GALLERY
                  </div>
                  <motion.button
                    data-hover="true"
                    onClick={() => setGalleryExpanded(v => !v)}
                    whileTap={{ scale: 0.95 }}
                    style={{
                      padding: '5px 14px', borderRadius: 7, cursor: 'none',
                      background: galleryExpanded ? 'rgba(0,255,224,0.1)' : 'transparent',
                      border: '1px solid rgba(0,255,224,0.25)',
                      color: '#00FFE0', fontSize: 11, fontWeight: 600,
                      transition: 'all 0.18s',
                    }}
                  >
                    {galleryExpanded ? '▲ Show Less' : `▼ Show All (${filtered.length})`}
                  </motion.button>
                </div>
              )}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))',
                gap: 24,
              }}>
                {(galleryExpanded || activeFilter !== 'All' ? filtered : filtered.slice(0, GALLERY_PREVIEW)).map((viz, i) => (
                  <VizCard key={viz.id} viz={viz} index={i} setFullImg={setFullImg} onOpenGif={onOpenGif} />
                ))}
              </div>
              {!galleryExpanded && activeFilter === 'All' && filtered.length > GALLERY_PREVIEW && (
                <div style={{ textAlign: 'center', marginTop: 20 }}>
                  <motion.button
                    data-hover="true"
                    onClick={() => setGalleryExpanded(true)}
                    whileTap={{ scale: 0.95 }}
                    style={{
                      padding: '9px 28px', borderRadius: 8, cursor: 'none',
                      background: 'rgba(0,255,224,0.06)',
                      border: '1px solid rgba(0,255,224,0.25)',
                      color: '#00FFE0', fontSize: 13, fontWeight: 600,
                      transition: 'all 0.18s',
                    }}
                  >
                    Show {filtered.length - GALLERY_PREVIEW} More Visualizations ▼
                  </motion.button>
                </div>
              )}
            </div>
          )}

          {showFeatured === false && filtered.length === 0 && (
            <div style={{ textAlign: 'center', padding: '60px 0', color: 'rgba(255,255,255,0.3)', fontSize: 13 }}>
              No visualizations in this category.
            </div>
          )}
        </motion.div>
      </AnimatePresence>

      {/* ── Footer note ──────────────────────────────────────── */}
      <FadeIn delay={200}>
        <div style={{
          marginTop: 48, padding: '16px 20px',
          background: 'rgba(0,255,224,0.03)',
          border: '1px solid rgba(0,255,224,0.08)',
          borderRadius: 10,
          fontSize: 12, color: 'rgba(255,255,255,0.35)', lineHeight: 1.6,
        }}>
          <span style={{ color: 'rgba(0,255,224,0.5)', fontWeight: 700 }}>Note:</span>{' '}
          Charts generated with R (ggplot2 + Plotly). To regenerate after new runs:{' '}
          <code style={{ fontFamily: 'monospace', color: 'rgba(0,255,224,0.6)', fontSize: 11 }}>
            python scripts/summarize_results.py
          </code>{' '}
          then{' '}
          <code style={{ fontFamily: 'monospace', color: 'rgba(0,255,224,0.6)', fontSize: 11 }}>
            Rscript report_materials/r_analysis/run_all.R
          </code>.{' '}
          Last generated: {new Date(summary.generated_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}.
        </div>
      </FadeIn>

      </motion.div>
      )}
      </AnimatePresence>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </>
  )
}
