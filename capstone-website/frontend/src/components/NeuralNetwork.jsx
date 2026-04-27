import { useEffect, useRef, useState } from 'react'

const MODELS = [
  { id:'claude',   initials:'CL', name:'Claude Sonnet 4.5', version:'claude-sonnet-4-5',  provider:'Anthropic',       color:'#00CED1', status:'COMPLETE' },
  { id:'gemini',   initials:'GM', name:'Gemini 2.5 Flash',  version:'gemini-2.5-flash',   provider:'Google DeepMind', color:'#FF6B6B', status:'COMPLETE' },
  { id:'chatgpt',  initials:'GP', name:'GPT-4.1',           version:'gpt-4.1',            provider:'OpenAI',          color:'#7FFFD4', status:'COMPLETE' },
  { id:'deepseek', initials:'DS', name:'DeepSeek Chat',     version:'deepseek-chat',       provider:'DeepSeek AI',     color:'#4A90D9', status:'COMPLETE' },
  { id:'mistral',  initials:'MS', name:'Mistral Large',     version:'mistral-large-latest',provider:'Mistral AI',      color:'#A78BFA', status:'COMPLETE' },
]

export default function NeuralNetwork({ onSelect, selected }) {
  const canvasRef  = useRef(null)
  const mouseRef   = useRef({ x: 0, y: 0 })
  const hoveredRef = useRef(null)
  const [hovered, setHovered] = useState(null)
  const [tooltip, setTooltip] = useState(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d', { willReadFrequently: false })

    let W, H
    const resize = () => {
      W = canvas.width  = canvas.parentElement?.clientWidth || window.innerWidth
      H = canvas.height = 500
    }
    resize()
    window.addEventListener('resize', resize)

    // ── Build nodes ────────────────────────────────────────────
    const BG_COUNT = 48

    // Background nodes — scattered randomly
    const bgNodes = Array.from({ length: BG_COUNT }, (_, i) => ({
      id: i,
      baseX: Math.random() * 0.92 + 0.04,  // fraction of W
      baseY: Math.random() * 0.85 + 0.075, // fraction of H
      vx: (Math.random() - 0.5) * 0.00015,
      vy: (Math.random() - 0.5) * 0.00015,
      phase: Math.random() * Math.PI * 2,
      isModel: false,
    }))

    // Model nodes — evenly spaced, mid-height with slight variation
    const modelNodes = MODELS.map((m, i) => {
      const xFrac = 0.1 + i * 0.2
      const yFrac = 0.35 + (i % 2 === 0 ? 0 : 0.20) + (i === 2 ? -0.05 : 0)
      return {
        id: BG_COUNT + i,
        modelIdx: i,
        baseX: xFrac,
        baseY: yFrac,
        driftAngle: (Math.PI * 2 * i) / MODELS.length,
        driftR: 0.025 + i * 0.005,
        driftSpeed: 0.0004 + i * 0.00008,
        phase: (i / MODELS.length) * Math.PI * 2,
        isModel: true,
      }
    })

    const allNodes = [...bgNodes, ...modelNodes]

    // Current positions (computed each frame)
    const pos = allNodes.map(() => ({ x: 0, y: 0 }))

    // ── Build edges (connect nearby nodes) ──────────────────────
    const DIST_THRESH_FRAC = 0.22  // as fraction of W
    const getPos = (n, t) => {
      if (n.isModel) {
        const drift = n.driftR
        return {
          x: n.baseX + Math.cos(t * n.driftSpeed + n.phase) * drift,
          y: n.baseY + Math.sin(t * n.driftSpeed * 0.7 + n.phase) * drift * 0.6,
        }
      }
      return {
        x: n.baseX + Math.sin(t * 0.0001 + n.phase) * 0.015,
        y: n.baseY + Math.cos(t * 0.00008 + n.phase) * 0.015,
      }
    }

    // Pre-compute edge list (based on initial positions)
    const initialPos = allNodes.map((n) => getPos(n, 0))
    const edges = []
    for (let i = 0; i < allNodes.length; i++) {
      for (let j = i + 1; j < allNodes.length; j++) {
        const dx = (initialPos[i].x - initialPos[j].x)
        const dy = (initialPos[i].y - initialPos[j].y) * (H / (W || 1))
        const dist = Math.sqrt(dx * dx + dy * dy)
        if (dist < DIST_THRESH_FRAC) edges.push({ a: i, b: j })
      }
    }

    // ── Pulses ─────────────────────────────────────────────────
    let pulses = []
    const spawnPulse = () => {
      if (edges.length === 0) return
      const e = edges[Math.floor(Math.random() * edges.length)]
      pulses.push({ edgeIdx: edges.indexOf(e), t: 0, speed: 0.008 + Math.random() * 0.012, reversed: Math.random() > 0.5 })
    }

    let t = 0
    let raf
    let spawnTimer = 0

    const draw = () => {
      ctx.clearRect(0, 0, W, H)

      // Update positions
      allNodes.forEach((n, i) => {
        const p = getPos(n, t)
        pos[i] = { x: p.x * W, y: p.y * H }
      })

      // Parallax offset from mouse
      const px = ((mouseRef.current.x / (W || 1)) - 0.5) * 18
      const py = ((mouseRef.current.y / (H || 1)) - 0.5) * 10

      const gx = (i) => pos[i].x + px
      const gy = (i) => pos[i].y + py

      // Draw edges
      edges.forEach(({ a, b }) => {
        const ax = gx(a), ay = gy(a)
        const bx = gx(b), by = gy(b)
        const dist = Math.sqrt((ax-bx)**2 + (ay-by)**2)
        const alpha = Math.max(0, (1 - dist / (DIST_THRESH_FRAC * W)) * 0.12)
        ctx.beginPath()
        ctx.moveTo(ax, ay)
        ctx.lineTo(bx, by)
        ctx.strokeStyle = `rgba(0,255,224,${alpha})`
        ctx.lineWidth = 0.8
        ctx.stroke()
      })

      // Update & draw pulses
      spawnTimer++
      if (spawnTimer >= 22) { spawnPulse(); spawnTimer = 0 }

      const alive = []
      pulses.forEach(p => {
        p.t += p.speed
        if (p.t > 1) return  // die
        alive.push(p)

        const e  = edges[p.edgeIdx]
        if (!e) return
        const t0 = p.reversed ? 1 - p.t : p.t
        const ax = gx(e.a), ay = gy(e.a)
        const bx = gx(e.b), by = gy(e.b)
        const px2 = ax + (bx - ax) * t0
        const py2 = ay + (by - ay) * t0

        const alpha = Math.sin(p.t * Math.PI) * 0.9
        ctx.beginPath()
        ctx.arc(px2, py2, 2.5, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(0,255,224,${alpha})`
        ctx.shadowColor = '#00FFE0'
        ctx.shadowBlur  = 6
        ctx.fill()
        ctx.shadowBlur = 0
      })
      pulses = alive

      // Draw background nodes
      bgNodes.forEach((n, i) => {
        const x = gx(i), y = gy(i)
        const pulse = 0.25 + Math.sin(t * 0.002 + n.phase) * 0.1
        ctx.beginPath()
        ctx.arc(x, y, 2.5, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(0,255,224,${pulse})`
        ctx.fill()
      })

      // Draw model nodes
      modelNodes.forEach((n, mi) => {
        const idx = BG_COUNT + mi
        const x = gx(idx), y = gy(idx)
        const model = MODELS[mi]
        const isHov = hoveredRef.current === mi
        const isSel = selected === mi
        const pulse = 0.6 + Math.sin(t * 0.0015 + n.phase) * 0.25
        const r = isHov || isSel ? 28 : 22

        // Outer glow ring
        ctx.beginPath()
        ctx.arc(x, y, r + 8, 0, Math.PI * 2)
        ctx.strokeStyle = `${model.color}${Math.round(pulse * 40).toString(16).padStart(2,'0')}`
        ctx.lineWidth = 1
        ctx.stroke()

        // Main circle
        ctx.beginPath()
        ctx.arc(x, y, r, 0, Math.PI * 2)
        ctx.fillStyle = `${model.color}22`
        ctx.fill()
        ctx.strokeStyle = model.color
        ctx.lineWidth = isHov || isSel ? 2.5 : 1.5
        if (isHov || isSel) {
          ctx.shadowColor = model.color
          ctx.shadowBlur  = 20
        }
        ctx.stroke()
        ctx.shadowBlur = 0

        // Initials
        ctx.fillStyle = model.color
        ctx.font = `700 13px "Space Grotesk", sans-serif`
        ctx.textAlign = 'center'
        ctx.textBaseline = 'middle'
        ctx.fillText(model.initials, x, y)

        // Label below
        ctx.fillStyle = isHov || isSel ? model.color : 'rgba(232,244,248,0.7)'
        ctx.font = `600 10px "Space Grotesk", sans-serif`
        ctx.fillText(model.name, x, y + r + 14)

        ctx.fillStyle = 'rgba(139,175,192,0.6)'
        ctx.font = `400 9px "Space Mono", monospace`
        ctx.fillText(model.version, x, y + r + 26)

        // Status badge
        const statusColor = model.status === 'COMPLETE' ? '#00FF88' : '#FF9A3C'
        ctx.font = `700 8px "Space Grotesk", sans-serif`
        ctx.fillStyle = statusColor
        ctx.fillText(model.status, x, y + r + 38)
      })

      t++
      raf = requestAnimationFrame(draw)
    }

    draw()

    // ── Mouse interaction ─────────────────────────────────────
    const onMove = (e) => {
      const rect = canvas.getBoundingClientRect()
      mouseRef.current = { x: e.clientX - rect.left, y: e.clientY - rect.top }

      // Check hover on model nodes
      let found = null
      modelNodes.forEach((n, mi) => {
        const idx = BG_COUNT + mi
        const x = pos[idx].x
        const y = pos[idx].y
        const dist = Math.sqrt((mouseRef.current.x - x)**2 + (mouseRef.current.y - y)**2)
        if (dist < 30) found = mi
      })

      if (found !== hoveredRef.current) {
        hoveredRef.current = found
        setHovered(found)
        canvas.style.cursor = found !== null ? 'pointer' : 'default'

        if (found !== null) {
          const m = MODELS[found]
          const idx = BG_COUNT + found
          setTooltip({
            x: pos[idx].x,
            y: pos[idx].y,
            model: m,
          })
        } else {
          setTooltip(null)
        }
      }
    }

    const onClick = () => {
      if (hoveredRef.current !== null) {
        onSelect?.(hoveredRef.current === selected ? null : hoveredRef.current)
      }
    }

    canvas.addEventListener('mousemove', onMove)
    canvas.addEventListener('click', onClick)

    return () => {
      window.removeEventListener('resize', resize)
      canvas.removeEventListener('mousemove', onMove)
      canvas.removeEventListener('click', onClick)
      cancelAnimationFrame(raf)
    }
  }, [selected, onSelect])

  return (
    <div style={{ position: 'relative', width: '100%' }}>
      <canvas ref={canvasRef} style={{ display: 'block', width: '100%', height: 500 }}/>

      {/* Tooltip overlay */}
      {tooltip && (
        <div
          style={{
            position: 'absolute',
            left: Math.min(tooltip.x + 36, (canvasRef.current?.clientWidth || 800) - 220),
            top: Math.max(tooltip.y - 60, 0),
            background: '#0D1426',
            border: `1px solid ${tooltip.model.color}`,
            borderRadius: 10,
            padding: '10px 14px',
            pointerEvents: 'none',
            zIndex: 10,
            minWidth: 180,
            boxShadow: `0 0 20px ${tooltip.model.color}44`,
          }}
        >
          <div style={{ color: tooltip.model.color, fontWeight: 700, fontSize: 13, marginBottom: 4 }}>
            {tooltip.model.name}
          </div>
          <div style={{ color: '#8BAFC0', fontSize: 11, fontFamily: 'monospace', marginBottom: 4 }}>
            {tooltip.model.version}
          </div>
          <div style={{ color: '#8BAFC0', fontSize: 11, marginBottom: 4 }}>{tooltip.model.provider}</div>
          <div style={{
            display: 'inline-block', fontSize: 9, fontWeight: 700, padding: '2px 6px',
            borderRadius: 6, marginTop: 2,
            color: tooltip.model.status === 'COMPLETE' ? '#00FF88' : '#FF9A3C',
            border: `1px solid ${tooltip.model.status === 'COMPLETE' ? '#00FF8844' : '#FF9A3C44'}`,
            background: tooltip.model.status === 'COMPLETE' ? 'rgba(0,255,136,0.1)' : 'rgba(255,154,60,0.1)',
          }}>
            {tooltip.model.status}
          </div>
          <div style={{ color: '#4A6A7A', fontSize: 10, marginTop: 6 }}>Click to view details</div>
        </div>
      )}

      <div style={{ textAlign: 'center', marginTop: 12, color: '#4A6A7A', fontSize: 11, fontFamily: 'monospace' }}>
        5 models · hover to inspect · click to select
      </div>
    </div>
  )
}
