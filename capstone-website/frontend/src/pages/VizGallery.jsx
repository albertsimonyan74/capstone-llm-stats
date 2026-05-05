import { useState, useRef } from 'react'
import { motion, AnimatePresence, useInView } from 'motion/react'
import { VISUALIZATIONS, VIZ_CATEGORIES } from '../data/visualizations'
import ExpandablePanel from '../components/ExpandablePanel'

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

function VizCard({ viz, color, setFullImg }) {
  const [imgLoaded, setImgLoaded] = useState(false)
  const Comp = viz.Component

  return (
    <motion.div
      whileHover={{ y: -4, boxShadow: `0 12px 40px ${color}33` }}
      transition={{ type: 'spring', stiffness: 380, damping: 26 }}
      style={{
        background: 'rgba(255,255,255,0.025)',
        border: `1px solid ${color}33`,
        borderTop: `3px solid ${color}`,
        borderRadius: 14,
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {Comp ? (
        <div
          style={{
            background: 'rgba(8,12,24,0.4)',
            padding: '18px 18px 8px',
            borderBottom: `1px solid ${color}1A`,
          }}
        >
          <ExpandablePanel title={viz.title}><Comp /></ExpandablePanel>
        </div>
      ) : (
        <button
          onClick={() => setFullImg(viz.png)}
          aria-label={`Open ${viz.title} full size`}
          style={{
            position: 'relative', aspectRatio: '16/10', background: '#fff',
            border: 'none', padding: 0, cursor: 'zoom-in', overflow: 'hidden',
            display: 'block',
          }}
        >
          <img
            src={viz.png}
            alt={viz.title}
            loading="lazy"
            onLoad={() => setImgLoaded(true)}
            style={{
              width: '100%', height: '100%', objectFit: 'cover', display: 'block',
              opacity: imgLoaded ? 1 : 0, transition: 'opacity 0.35s ease',
            }}
          />
          {!imgLoaded && (
            <div style={{
              position: 'absolute', inset: 0, display: 'flex',
              alignItems: 'center', justifyContent: 'center',
            }}>
              <div style={{
                width: 28, height: 28, border: '2px solid rgba(0,255,224,0.18)',
                borderTop: `2px solid ${color}`, borderRadius: '50%',
                animation: 'spin 1s linear infinite',
              }} />
            </div>
          )}
        </button>
      )}

      <div style={{ padding: '16px 18px 18px', display: 'flex', flexDirection: 'column', flex: 1 }}>
        <div style={{ color: '#fff', fontSize: 14.5, fontWeight: 700, marginBottom: 4, lineHeight: 1.3 }}>
          {viz.title}
        </div>
        <div style={{ color: color, fontSize: 11, fontWeight: 600, marginBottom: 10, opacity: 0.85 }}>
          {viz.subtitle}
        </div>
        <div style={{ color: 'rgba(232,244,248,0.7)', fontSize: 12, lineHeight: 1.6, marginTop: 'auto' }}>
          {viz.caption}
        </div>
      </div>
    </motion.div>
  )
}

export default function VizGallery({ setFullImg }) {
  const [open, setOpen] = useState(true)

  return (
    <>
      <FadeIn>
        <div style={{ display:'flex', alignItems:'center', justifyContent:'center', gap:16, marginBottom: open ? 40 : 0, flexWrap:'wrap' }}>
          <div style={{ textAlign:'center' }}>
            <h2 style={{ fontSize:'clamp(32px,4vw,48px)', fontWeight:700, color:'var(--text-primary)', margin:0, lineHeight:1.2 }}>
              Benchmark Visualizations
            </h2>
            <motion.div
              initial={{ scaleX:0 }}
              whileInView={{ scaleX:1 }}
              viewport={{ once:true }}
              transition={{ duration:0.7, delay:0.25 }}
              style={{ width:64, height:3, background:'linear-gradient(90deg,var(--aqua),var(--blue))', margin:'12px auto 0', borderRadius:2, transformOrigin:'left' }}
            />
          </div>
          <motion.button
            onClick={() => setOpen(v => !v)}
            whileHover={{ scale:1.05 }}
            whileTap={{ scale:0.95 }}
            style={{
              marginTop:4,
              padding:'8px 20px', borderRadius:8,
              border:`1.5px solid rgba(0,255,224,${open?'0.6':'0.35'})`,
              background: open ? 'rgba(0,255,224,0.10)' : 'rgba(0,255,224,0.05)',
              color: open ? '#00FFE0' : 'rgba(0,255,224,0.7)',
              fontSize:12, fontWeight:700, cursor:'pointer',
              fontFamily:'var(--font-mono)', letterSpacing:'0.05em',
              transition:'all 0.18s',
            }}
          >
            {open ? '▼ COLLAPSE' : `▶ EXPAND (${VISUALIZATIONS.length} FIGURES)`}
          </motion.button>
        </div>
      </FadeIn>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 8 }}
            transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
          >
            {VIZ_CATEGORIES.map((cat, ci) => {
              const items = VISUALIZATIONS.filter(v => v.category === cat.id)
              if (!items.length) return null
              return (
                <FadeIn key={cat.id} delay={60 + 30 * ci}>
                  <div style={{
                    display: 'flex', alignItems: 'baseline', gap: 14, marginBottom: 14, marginTop: ci === 0 ? 0 : 28,
                    paddingBottom: 10, borderBottom: `1px solid ${cat.color}33`,
                  }}>
                    <span style={{
                      fontFamily: 'monospace', color: cat.color, fontSize: 14, fontWeight: 800,
                    }}>{ci + 1}.</span>
                    <span style={{ color: '#fff', fontSize: 18, fontWeight: 700 }}>{cat.label}</span>
                    <span style={{ color: cat.color, fontSize: 11, fontWeight: 600, opacity: 0.8 }}>{cat.subtitle}</span>
                  </div>
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
                    gap: 18, marginBottom: 32,
                  }}>
                    {items.map(v => (
                      <VizCard key={v.id} viz={v} color={cat.color} setFullImg={setFullImg} />
                    ))}
                  </div>
                </FadeIn>
              )
            })}
          </motion.div>
        )}
      </AnimatePresence>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </>
  )
}
