import { useEffect, useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell, LabelList,
} from 'recharts'

const API = import.meta.env.VITE_API_URL || ''

const MODEL_COLORS = {
  claude:   '#00CED1',
  gemini:   '#FF6B6B',
  chatgpt:  '#7FFFD4',
  deepseek: '#4A90D9',
  mistral:  '#A78BFA',
}

// Canonical numbers post Phase 1.8 v1 deprecation (2026-05-04) from bootstrap_ci.json + robustness_v2.json + calibration.json
const STATIC_RANKINGS = {
  accuracy: [
    { model: 'gemini',   value: 0.7314 },
    { model: 'claude',   value: 0.6976 },
    { model: 'chatgpt',  value: 0.6733 },
    { model: 'deepseek', value: 0.6686 },
    { model: 'mistral',  value: 0.6676 },
  ],
  robustness: [
    { model: 'chatgpt',  value: 0.0003 },
    { model: 'mistral',  value: 0.0013 },
    { model: 'gemini',   value: 0.0129 },
    { model: 'claude',   value: 0.0305 },
    { model: 'deepseek', value: 0.0388 },
  ],
  calibration: [
    { model: 'claude',   value: 0.033 },
    { model: 'chatgpt',  value: 0.034 },
    { model: 'gemini',   value: 0.077 },
    { model: 'mistral',  value: 0.081 },
    { model: 'deepseek', value: 0.198 },
  ],
}

const PANEL_BG = 'rgba(255,255,255,0.025)'
const PANEL_BORDER = '1px solid rgba(0,255,224,0.18)'

function rankingPanel({ title, accent, items, lowerIsBetter, valueFmt }) {
  return (
    <div style={{
      background: PANEL_BG, border: PANEL_BORDER, borderRadius: 14,
      padding: '18px 18px 14px', display: 'flex', flexDirection: 'column',
    }}>
      <div style={{
        color: accent, fontSize: 11, fontWeight: 800, letterSpacing: '0.16em',
        textTransform: 'uppercase', marginBottom: 4,
      }}>{title}</div>
      <div style={{ color: 'rgba(232,244,248,0.55)', fontSize: 11, marginBottom: 10 }}>
        {lowerIsBetter ? 'Lower is better' : 'Higher is better'} · ranked 1→5
      </div>
      <div style={{ width: '100%', height: 240 }}>
        <ResponsiveContainer>
          <BarChart data={items} layout="vertical" margin={{ top: 4, right: 48, bottom: 0, left: 8 }}>
            <CartesianGrid strokeDasharray="2 4" stroke="rgba(255,255,255,0.07)" horizontal={false} />
            <XAxis
              type="number"
              tick={{ fill: 'rgba(232,244,248,0.55)', fontSize: 10 }}
              tickFormatter={valueFmt}
              domain={[0, 'dataMax']}
            />
            <YAxis
              dataKey="model" type="category"
              tick={{ fill: 'rgba(232,244,248,0.85)', fontSize: 11, fontFamily: 'monospace' }}
              width={70}
            />
            <Tooltip
              cursor={{ fill: 'rgba(0,255,224,0.05)' }}
              contentStyle={{
                background: 'rgba(8,12,18,0.95)', border: '1px solid rgba(0,255,224,0.4)',
                borderRadius: 6, fontSize: 12,
              }}
              labelStyle={{ color: '#ffffff' }}
              itemStyle={{ color: '#ffffff' }}
              formatter={(v) => [valueFmt(v), title]}
            />
            <Bar dataKey="value" radius={[0, 4, 4, 0]}>
              {items.map((entry) => (
                <Cell key={entry.model} fill={MODEL_COLORS[entry.model]} />
              ))}
              <LabelList
                dataKey="value" position="right"
                formatter={valueFmt}
                style={{ fill: 'rgba(232,244,248,0.85)', fontSize: 11, fontFamily: 'monospace' }}
              />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export default function ThreeRankingsComparison() {
  const [data, setData] = useState(STATIC_RANKINGS)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API}/api/v2/rankings`)
      .then(r => r.ok ? r.json() : Promise.reject())
      .then(d => {
        const accPM = d?.accuracy?.per_model || {}
        const robPM = d?.robustness?.per_model || {}
        const calVE = d?.calibration?.verbalized_ece || {}

        const accuracy = Object.entries(accPM)
          .map(([model, v]) => ({ model, value: v?.mean ?? 0 }))
          .sort((a, b) => b.value - a.value)
        const robustness = Object.entries(robPM)
          .map(([model, v]) => ({ model, value: v?.mean_delta ?? 0 }))
          .sort((a, b) => a.value - b.value)
        const calibration = Object.entries(calVE)
          .map(([model, ece]) => ({ model, value: ece ?? 0 }))
          .sort((a, b) => a.value - b.value)

        if (accuracy.length && robustness.length && calibration.length) {
          setData({ accuracy, robustness, calibration })
        }
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  const fmt3 = (v) => (typeof v === 'number' ? v.toFixed(3) : v)

  return (
    <div style={{
      maxWidth: 1300, margin: '0 auto', padding: '0 4px',
      opacity: loading ? 0.85 : 1, transition: 'opacity 0.3s',
    }}>
      <div style={{
        color: 'var(--aqua)', fontSize: 12, fontWeight: 700, letterSpacing: '0.14em',
        textAlign: 'center', marginBottom: 14, textTransform: 'uppercase',
      }}>Three rankings · the same data tells three stories</div>
      <div className="three-rankings-grid">
        {rankingPanel({
          title: 'Accuracy', accent: '#00FFE0',
          items: data.accuracy, lowerIsBetter: false, valueFmt: fmt3,
        })}
        {rankingPanel({
          title: 'Robustness (Δ)', accent: '#FFB347',
          items: data.robustness, lowerIsBetter: true, valueFmt: fmt3,
        })}
        {rankingPanel({
          title: 'Calibration (ECE)', accent: '#A78BFA',
          items: data.calibration, lowerIsBetter: true, valueFmt: fmt3,
        })}
      </div>
    </div>
  )
}
