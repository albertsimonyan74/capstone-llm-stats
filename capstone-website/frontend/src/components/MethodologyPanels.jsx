import { useEffect, useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ReferenceLine, ResponsiveContainer, ScatterChart, Scatter, ZAxis,
  LabelList, Cell, ErrorBar, LineChart, Line,
} from 'recharts'

const API = import.meta.env.VITE_API_URL || ''

const MODEL_COLORS = {
  claude:   '#00CED1',
  gemini:   '#FF6B6B',
  chatgpt:  '#7FFFD4',
  deepseek: '#4A90D9',
  mistral:  '#A78BFA',
}

const DIM_COLORS = {
  N: '#00FFE0',
  M: '#00B4D8',
  A: '#7FFFD4',
  C: '#4A90D9',
  R: '#A78BFA',
}

const MODELS = ['claude', 'chatgpt', 'gemini', 'deepseek', 'mistral']
const DIMS = ['N', 'M', 'A', 'C', 'R']

const PANEL_BG = 'rgba(255,255,255,0.025)'
const PANEL_BORDER = '1px solid rgba(0,255,224,0.18)'

function PanelShell({ title, subtitle, accent = '#00FFE0', children, caption, subCaption }) {
  return (
    <div style={{
      background: PANEL_BG, border: PANEL_BORDER, borderRadius: 14,
      padding: '20px 22px', marginBottom: 20,
    }}>
      <div style={{ marginBottom: 12 }}>
        <div style={{
          color: accent, fontSize: 11, fontWeight: 800, letterSpacing: '0.16em',
          textTransform: 'uppercase', marginBottom: 4,
        }}>{title}</div>
        {subtitle && (
          <div style={{ color: 'rgba(232,244,248,0.55)', fontSize: 12 }}>{subtitle}</div>
        )}
      </div>
      {children}
      {caption && (
        <p style={{
          color: 'rgba(232,244,248,0.75)', fontSize: 12, lineHeight: 1.7,
          margin: '14px 0 0',
        }}>{caption}</p>
      )}
      {subCaption && (
        <p style={{
          color: 'rgba(232,244,248,0.5)', fontSize: 11, lineHeight: 1.65,
          margin: '6px 0 0',
        }}>{subCaption}</p>
      )}
    </div>
  )
}

function TooltipBox({ children }) {
  return (
    <div style={{
      background: 'rgba(8,12,18,0.95)', border: '1px solid rgba(0,255,224,0.4)',
      borderRadius: 6, padding: '8px 12px', fontSize: 12, color: '#fff',
      fontFamily: 'monospace',
    }}>{children}</div>
  )
}

// ─── Panel 1: per-model keyword-judge disagreement ───────────────
const STATIC_PASSFLIP = {
  combined: {
    pct_pass_flip: 0.2074,
    n_eligible: 2850,
    n_pass_flip: 591,
    per_model: {
      claude:   { n_total: 644, n_eligible: 570, n_pass_flip: 149, pct: 0.2614035087719298 },
      chatgpt:  { n_total: 644, n_eligible: 570, n_pass_flip: 103, pct: 0.18070175438596492 },
      gemini:   { n_total: 644, n_eligible: 570, n_pass_flip: 130, pct: 0.22807017543859648 },
      deepseek: { n_total: 644, n_eligible: 570, n_pass_flip: 100, pct: 0.17543859649122806 },
      mistral:  { n_total: 644, n_eligible: 570, n_pass_flip: 109, pct: 0.1912280701754386 },
    },
  },
}

export function PerModelPassFlipPanel() {
  const [data, setData] = useState(STATIC_PASSFLIP)
  useEffect(() => {
    fetch(`${API}/api/v2/pass_flip`)
      .then(r => r.ok ? r.json() : null)
      .then(j => { if (j?.combined?.per_model) setData(j) })
      .catch(() => {})
  }, [])

  const combined = data?.combined ?? STATIC_PASSFLIP.combined
  const pm = combined.per_model
  const avgPct = (combined.pct_pass_flip ?? 0.2074) * 100
  const rows = MODELS
    .map(m => ({
      model: m,
      pct: (pm[m]?.pct ?? 0) * 100,
      n_pass_flip: pm[m]?.n_pass_flip ?? 0,
      n_eligible: pm[m]?.n_eligible ?? 0,
    }))
    .sort((a, b) => b.pct - a.pct)

  return (
    <PanelShell
      title="Keyword-judge disagreement by model"
      subtitle="Combined base + perturbation analysis (n=2,850 eligible runs)"
      accent="#00B4D8"
      caption={`Claude shows the highest keyword-judge disagreement (${rows[0].pct.toFixed(1)}%) while ChatGPT and DeepSeek tie for the lowest (${rows[rows.length - 1].pct.toFixed(1)}%). The 8.6pp spread suggests Claude's response style is more keyword-friendly without engaging with assumptions substantively. ChatGPT and DeepSeek's lower disagreement may indicate more literal keyword matching to actual reasoning content. Dashed line = combined cohort average (${avgPct.toFixed(2)}%).`}
    >
      <div style={{ width: '100%', height: 260 }}>
        <ResponsiveContainer>
          <BarChart data={rows} margin={{ top: 16, right: 12, bottom: 8, left: 0 }}>
            <CartesianGrid strokeDasharray="2 4" stroke="rgba(255,255,255,0.07)" />
            <XAxis dataKey="model" tick={{ fill: 'rgba(232,244,248,0.7)', fontSize: 11 }} />
            <YAxis
              tick={{ fill: 'rgba(232,244,248,0.7)', fontSize: 11 }}
              tickFormatter={v => `${v}%`}
              domain={[0, 35]}
            />
            <Tooltip
              cursor={{ fill: 'rgba(0,255,224,0.05)' }}
              content={({ active, payload }) => {
                if (!active || !payload?.[0]) return null
                const r = payload[0].payload
                return (
                  <TooltipBox>
                    <div style={{ color: MODEL_COLORS[r.model], fontWeight: 700, marginBottom: 4 }}>{r.model}</div>
                    <div>disagreement: {r.pct.toFixed(2)}%</div>
                    <div>{r.n_pass_flip} / {r.n_eligible} runs</div>
                  </TooltipBox>
                )
              }}
            />
            <ReferenceLine
              y={avgPct} stroke="#FFB347" strokeDasharray="4 4"
              label={{ value: `avg ${avgPct.toFixed(2)}%`, fill: '#FFB347', fontSize: 10, position: 'right' }}
            />
            <Bar dataKey="pct" radius={[4, 4, 0, 0]}>
              {rows.map(r => <Cell key={r.model} fill={MODEL_COLORS[r.model]} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </PanelShell>
  )
}

// ─── Panel 2: keyword-judge disagreement (3 interactive bar panels) ─
const STATIC_KJ_CHARTS = {
  base: {
    n_eligible: 750,
    pct_pass_flip: 0.20933333333333334,
    per_model: {
      claude:   { n_pass_flip: 39, n_eligible: 150, pct: 0.26 },
      chatgpt:  { n_pass_flip: 27, n_eligible: 150, pct: 0.18 },
      gemini:   { n_pass_flip: 34, n_eligible: 150, pct: 0.22666666666666666 },
      deepseek: { n_pass_flip: 27, n_eligible: 150, pct: 0.18 },
      mistral:  { n_pass_flip: 30, n_eligible: 150, pct: 0.2 },
    },
  },
  perturbation: {
    n_eligible: 2100,
    pct_pass_flip: 0.20666666666666667,
    per_model: {
      claude:   { n_pass_flip: 110, n_eligible: 420, pct: 0.2619047619047619 },
      chatgpt:  { n_pass_flip: 76,  n_eligible: 420, pct: 0.18095238095238095 },
      gemini:   { n_pass_flip: 96,  n_eligible: 420, pct: 0.22857142857142856 },
      deepseek: { n_pass_flip: 73,  n_eligible: 420, pct: 0.1738095238095238 },
      mistral:  { n_pass_flip: 79,  n_eligible: 420, pct: 0.1880952380952381 },
    },
  },
  combined: {
    n_eligible: 2850,
    pct_pass_flip: 0.2074,
    per_model: {
      claude:   { n_pass_flip: 149, n_eligible: 570, pct: 0.2614035087719298 },
      chatgpt:  { n_pass_flip: 103, n_eligible: 570, pct: 0.18070175438596492 },
      gemini:   { n_pass_flip: 130, n_eligible: 570, pct: 0.22807017543859648 },
      deepseek: { n_pass_flip: 100, n_eligible: 570, pct: 0.17543859649122806 },
      mistral:  { n_pass_flip: 109, n_eligible: 570, pct: 0.1912280701754386 },
    },
  },
}

function KJBar({ panelKey, data }) {
  const block = data?.[panelKey] ?? STATIC_KJ_CHARTS[panelKey]
  const pm = block.per_model
  const overallPct = (block.pct_pass_flip ?? 0) * 100
  const rows = MODELS.map(m => ({
    model: m,
    pct: (pm[m]?.pct ?? 0) * 100,
    n_pass_flip: pm[m]?.n_pass_flip ?? 0,
    n_eligible: pm[m]?.n_eligible ?? 0,
  }))
  const TITLES = { base: 'Base', perturbation: 'Perturbation', combined: 'Combined' }
  return (
    <div className="kj-chart-panel">
      <div className="kj-chart-title">
        {TITLES[panelKey]} <span className="kj-chart-n">n_eligible = {block.n_eligible.toLocaleString()}</span>
      </div>
      <div style={{ width: '100%', height: 240 }}>
        <ResponsiveContainer>
          <BarChart data={rows} margin={{ top: 14, right: 14, bottom: 4, left: 0 }}>
            <CartesianGrid strokeDasharray="2 4" stroke="rgba(255,255,255,0.07)" />
            <XAxis dataKey="model" tick={{ fill: 'rgba(232,244,248,0.7)', fontSize: 10 }} />
            <YAxis
              tick={{ fill: 'rgba(232,244,248,0.7)', fontSize: 10 }}
              tickFormatter={v => `${v}%`}
              domain={[0, 35]}
            />
            <Tooltip
              cursor={{ fill: 'rgba(0,255,224,0.05)' }}
              content={({ active, payload }) => {
                if (!active || !payload?.[0]) return null
                const r = payload[0].payload
                return (
                  <TooltipBox>
                    <div style={{ color: MODEL_COLORS[r.model], fontWeight: 700, marginBottom: 4 }}>{r.model}</div>
                    <div>{r.pct.toFixed(2)}% ({r.n_pass_flip}/{r.n_eligible})</div>
                  </TooltipBox>
                )
              }}
            />
            <ReferenceLine
              y={overallPct} stroke="#FFB347" strokeDasharray="4 4"
              label={{ value: `overall ${overallPct.toFixed(1)}%`, fill: '#FFB347', fontSize: 9, position: 'right' }}
            />
            <Bar dataKey="pct" radius={[4, 4, 0, 0]}>
              {rows.map(r => <Cell key={r.model} fill={MODEL_COLORS[r.model]} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export function KeywordDegradationPanel() {
  const [data, setData] = useState(null)
  useEffect(() => {
    fetch(`${API}/api/v2/pass_flip`)
      .then(r => r.ok ? r.json() : null)
      .then(j => { if (j?.combined?.per_model) setData(j) })
      .catch(() => {})
  }, [])
  return (
    <PanelShell
      title="Keyword vs Judge disagreement: per-model · per-cohort"
      accent="#00B4D8"
      caption="Three panels show keyword-judge disagreement rate (keyword PASS but judge FAIL on assumption_compliance) per model, broken out by cohort. The dashed line marks the cohort overall rate. Disagreement is essentially flat across cohorts (base 20.9%, perturbation 20.7%, combined 20.74%) — keyword's regex-based scoring is more sensitive to surface-form changes than the LLM judge."
      subCaption="Base: 750 runs · Perturbation: 2,100 runs · Combined: 2,850 runs."
    >
      <div className="kj-charts-grid">
        <KJBar panelKey="base" data={data}/>
        <KJBar panelKey="perturbation" data={data}/>
        <KJBar panelKey="combined" data={data}/>
      </div>
    </PanelShell>
  )
}

// ─── Panel 2.5: per-model failure modes (5 cards 3+2) ──────────────
const STATIC_FAILURES = {
  by_model_l1: {
    chatgpt:  { ASSUMPTION_VIOLATION: 25, MATHEMATICAL_ERROR: 4,  FORMATTING_FAILURE: 6, CONCEPTUAL_ERROR: 3 },
    claude:   { MATHEMATICAL_ERROR: 10, ASSUMPTION_VIOLATION: 9 },
    gemini:   { ASSUMPTION_VIOLATION: 10, MATHEMATICAL_ERROR: 9, CONCEPTUAL_ERROR: 4, FORMATTING_FAILURE: 1 },
    deepseek: { ASSUMPTION_VIOLATION: 15, MATHEMATICAL_ERROR: 13, FORMATTING_FAILURE: 6, CONCEPTUAL_ERROR: 2 },
    mistral:  { MATHEMATICAL_ERROR: 12, ASSUMPTION_VIOLATION: 8, FORMATTING_FAILURE: 5, CONCEPTUAL_ERROR: 1 },
  },
}

const L1_LABEL = {
  ASSUMPTION_VIOLATION: 'Assumption violation',
  MATHEMATICAL_ERROR:   'Math error',
  FORMATTING_FAILURE:   'Format',
  CONCEPTUAL_ERROR:     'Conceptual',
  HALLUCINATION:        'Hallucination',
}

const FAILURE_SUMMARY = {
  chatgpt:  { mode: 'Assumption-dominated', summary: 'Tends to skip required assumption checks.' },
  claude:   { mode: 'Math-dominated',       summary: 'Computational errors dominate.' },
  gemini:   { mode: 'Balanced split',       summary: 'No single dominant failure mode.' },
  deepseek: { mode: 'Mixed (A + math)',     summary: 'Both A and math contribute substantially.' },
  mistral:  { mode: 'Math-dominated',       summary: 'Math errors are primary failure mode.' },
}

function buildFailureCards(byModelL1) {
  return MODELS.map(m => {
    const counts = byModelL1[m] || {}
    const entries = Object.entries(counts).sort((a, b) => b[1] - a[1])
    const total = entries.reduce((s, [, n]) => s + n, 0)
    const breakdown = entries.map(([k, n]) => ({
      label: L1_LABEL[k] || k,
      count: n,
      percent: total ? Math.round((100 * n) / total) : 0,
    }))
    const dominant = breakdown[0] ?? { count: 0, label: '—' }
    return {
      model: m,
      color: MODEL_COLORS[m],
      mode: FAILURE_SUMMARY[m]?.mode ?? '—',
      summary: FAILURE_SUMMARY[m]?.summary ?? '',
      dominantCount: dominant.count,
      total,
      breakdown,
    }
  })
}

export function PerModelFailuresPanel() {
  const [data, setData] = useState(STATIC_FAILURES)
  useEffect(() => {
    fetch(`${API}/api/v2/error_taxonomy`)
      .then(r => r.ok ? r.json() : null)
      .then(j => { if (j?.by_model_l1) setData({ by_model_l1: j.by_model_l1 }) })
      .catch(() => {})
  }, [])
  const cards = buildFailureCards(data?.by_model_l1 ?? STATIC_FAILURES.by_model_l1)
  const MODEL_LABEL = { claude: 'Claude', chatgpt: 'ChatGPT', gemini: 'Gemini', deepseek: 'DeepSeek', mistral: 'Mistral' }
  return (
    <div className="failure-modes-grid">
      {cards.map(c => {
        const dominantPct = c.total ? Math.round((100 * c.dominantCount) / c.total) : 0
        return (
          <div key={c.model} className="failure-mode-card" style={{ borderTopColor: c.color }}>
            <div className="failure-mode-header">
              <h4 className="failure-mode-model" style={{ color: c.color }}>{MODEL_LABEL[c.model]}</h4>
              <div className="failure-mode-tag">{c.mode}</div>
            </div>
            <div className="failure-mode-stat">
              <span className="failure-mode-count">{c.dominantCount} / {c.total}</span>
              <span className="failure-mode-percent">({dominantPct}% of failures)</span>
            </div>
            <div className="failure-mode-breakdown">
              {c.breakdown.map(item => (
                <div key={item.label} className="breakdown-row">
                  <div className="breakdown-label">{item.label}</div>
                  <div className="breakdown-bar-wrapper">
                    <div className="breakdown-bar"
                      style={{ width: `${item.percent}%`, background: c.color, opacity: 0.7 }}/>
                  </div>
                  <div className="breakdown-count">{item.count} ({item.percent}%)</div>
                </div>
              ))}
            </div>
            <p className="failure-mode-summary">{c.summary}</p>
          </div>
        )
      })}
    </div>
  )
}

// ─── Panel 3: per-dim robustness deltas ──────────────────────────
const STATIC_PER_DIM_DELTA = {
  claude:   { N: 0.0101,  M: 0.0163,  A: 0.0754,  C: 0.0057,  R: 0.0110 },
  chatgpt:  { N: -0.0168, M: 0.0088,  A: -0.0013, C: -0.0050, R: 0.0053 },
  gemini:   { N: -0.0101, M: 0.0126,  A: 0.0402,  C: -0.0126, R: 0.0047 },
  deepseek: { N: -0.0341, M: 0.0075,  A: 0.1281,  C: -0.0227, R: 0.0226 },
  mistral:  { N: 0.0312,  M: -0.0176, A: 0.0025,  C: 0.0186,  R: -0.0075 },
}

function shapeDimByModel(perModelByDim) {
  return DIMS.map(dim => {
    const row = { dim }
    for (const m of MODELS) row[m] = perModelByDim[m]?.[dim] ?? null
    return row
  })
}

export function PerDimRobustnessPanel() {
  const [perModel, setPerModel] = useState(() => {
    const out = {}
    for (const m of MODELS) {
      out[m] = {}
      for (const d of DIMS) out[m][d] = STATIC_PER_DIM_DELTA[m]?.[d] ?? null
    }
    return out
  })

  useEffect(() => {
    fetch(`${API}/api/v2/robustness`)
      .then(r => r.ok ? r.json() : null)
      .then(j => {
        const pdd = j?.per_dim_delta
        if (!pdd) return
        const out = {}
        for (const m of MODELS) {
          out[m] = {}
          for (const d of DIMS) {
            const v = pdd[m]?.[d]
            out[m][d] = (v && typeof v === 'object') ? v.mean_delta : (v ?? null)
          }
        }
        setPerModel(out)
      })
      .catch(() => {})
  }, [])

  const rows = shapeDimByModel(perModel)

  return (
    <PanelShell
      title="Robustness degradation by NMACR dimension"
      subtitle="Per-dimension change in score from base to perturbation, by model"
      accent="#7FFFD4"
      caption="Bars above zero = score decreased under perturbation (worse). DeepSeek shows the largest assumption-compliance degradation (+12.8pp on A); Mistral is the only model with a negative R delta (reasoning_quality slightly improves under perturbation, ΔR=−0.008). Numerical correctness (N) is stable to slightly improving for most models — math is robust; assumption articulation (A) is the most brittle dimension. Source: experiments/results_v2/robustness_v2.json (per_dim_delta block)."
    >
      <div style={{ width: '100%', height: 280 }}>
        <ResponsiveContainer>
          <BarChart data={rows} margin={{ top: 16, right: 12, bottom: 8, left: 0 }}>
            <CartesianGrid strokeDasharray="2 4" stroke="rgba(255,255,255,0.07)" />
            <XAxis dataKey="dim" tick={{ fill: 'rgba(232,244,248,0.7)', fontSize: 11 }} />
            <YAxis
              tick={{ fill: 'rgba(232,244,248,0.7)', fontSize: 11 }}
              tickFormatter={v => v.toFixed(2)}
            />
            <Tooltip
              cursor={{ fill: 'rgba(0,255,224,0.05)' }}
              content={({ active, payload, label }) => {
                if (!active || !payload?.length) return null
                return (
                  <TooltipBox>
                    <div style={{ color: DIM_COLORS[label], fontWeight: 700, marginBottom: 4 }}>dim {label}</div>
                    {payload.map(p => (
                      <div key={p.dataKey}>
                        <span style={{ color: MODEL_COLORS[p.dataKey] }}>{p.dataKey}</span>: {Number(p.value).toFixed(4)}
                      </div>
                    ))}
                  </TooltipBox>
                )
              }}
            />
            <Legend wrapperStyle={{ fontSize: 11, color: 'rgba(232,244,248,0.7)' }} />
            <ReferenceLine y={0} stroke="rgba(255,255,255,0.35)" />
            {MODELS.map(m => (
              <Bar key={m} dataKey={m} fill={MODEL_COLORS[m]} radius={[3, 3, 0, 0]} />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>
    </PanelShell>
  )
}

// ─── Panel 4: per-dim calibration ECE ────────────────────────────
const STATIC_PER_DIM_ECE = {
  N: { claude: 0.1612, chatgpt: 0.1669, gemini: 0.1541, deepseek: 0.1673, mistral: 0.1599 },
  M: { claude: 0.1443, chatgpt: 0.1419, gemini: 0.1484, deepseek: 0.1396, mistral: 0.1435 },
  A: { claude: 0.1657, chatgpt: 0.1654, gemini: 0.1677, deepseek: 0.1685, mistral: 0.1724 },
  C: { claude: 0.0534, chatgpt: 0.0593, gemini: 0.0448, deepseek: 0.0393, mistral: 0.0474 },
  R: { claude: 0.1125, chatgpt: 0.0926, gemini: 0.1292, deepseek: 0.091,  mistral: 0.0999 },
}

export function PerDimCalibrationPanel() {
  const [perDim, setPerDim] = useState(STATIC_PER_DIM_ECE)

  useEffect(() => {
    fetch(`${API}/api/v2/calibration`)
      .then(r => r.ok ? r.json() : null)
      .then(j => {
        const live = j?.per_dim_ece
        if (live && Object.keys(live).length) setPerDim(live)
      })
      .catch(() => {})
  }, [])

  const rows = DIMS.map(dim => {
    const row = { dim }
    for (const m of MODELS) row[m] = perDim[dim]?.[m] ?? null
    return row
  })

  return (
    <PanelShell
      title="Calibration ECE by NMACR dimension"
      subtitle="Expected Calibration Error per dimension, by model (lower is better)"
      accent="#A78BFA"
      caption="Models calibrate moderately well on M (method) and best on C (verbalized confidence, 0.04–0.06 ECE across all five models). A (assumption) is the weakest dimension across all models (≈0.16–0.17 ECE) — confidence in assumption articulation poorly tracks accuracy. R varies most (DeepSeek 0.09 vs Gemini 0.13). Dashed line = 0.10 reference threshold for well-calibrated. Source: experiments/results_v2/per_dim_calibration.json."
    >
      <div style={{ width: '100%', height: 280 }}>
        <ResponsiveContainer>
          <BarChart data={rows} margin={{ top: 16, right: 12, bottom: 8, left: 0 }}>
            <CartesianGrid strokeDasharray="2 4" stroke="rgba(255,255,255,0.07)" />
            <XAxis dataKey="dim" tick={{ fill: 'rgba(232,244,248,0.7)', fontSize: 11 }} />
            <YAxis
              tick={{ fill: 'rgba(232,244,248,0.7)', fontSize: 11 }}
              domain={[0, 0.22]}
              tickFormatter={v => v.toFixed(2)}
            />
            <Tooltip
              cursor={{ fill: 'rgba(0,255,224,0.05)' }}
              content={({ active, payload, label }) => {
                if (!active || !payload?.length) return null
                return (
                  <TooltipBox>
                    <div style={{ color: DIM_COLORS[label], fontWeight: 700, marginBottom: 4 }}>dim {label}</div>
                    {payload.map(p => (
                      <div key={p.dataKey}>
                        <span style={{ color: MODEL_COLORS[p.dataKey] }}>{p.dataKey}</span>: ECE {Number(p.value).toFixed(4)}
                      </div>
                    ))}
                  </TooltipBox>
                )
              }}
            />
            <Legend wrapperStyle={{ fontSize: 11, color: 'rgba(232,244,248,0.7)' }} />
            <ReferenceLine
              y={0.10} stroke="#FFB347" strokeDasharray="4 4"
              label={{ value: 'well-calibrated 0.10', fill: '#FFB347', fontSize: 10, position: 'right' }}
            />
            {MODELS.map(m => (
              <Bar key={m} dataKey={m} fill={MODEL_COLORS[m]} radius={[3, 3, 0, 0]} />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>
    </PanelShell>
  )
}

// ─── Panel 5: accuracy vs calibration scatter ────────────────────
const STATIC_ACC_CALIB = {
  acc_calib_corr: { claude: 0.4164, chatgpt: 0.3632, gemini: 0.3876, deepseek: 0.4204, mistral: 0.4245 },
  accuracy: {
    claude: 0.697605, chatgpt: 0.67326, gemini: 0.73142,
    deepseek: 0.668568, mistral: 0.667635,
  },
}

export function AccCalibScatterPanel() {
  const [acc, setAcc] = useState(STATIC_ACC_CALIB.accuracy)
  const [corr, setCorr] = useState(STATIC_ACC_CALIB.acc_calib_corr)

  useEffect(() => {
    let cancelled = false
    Promise.allSettled([
      fetch(`${API}/api/v2/calibration`).then(r => r.ok ? r.json() : null),
      fetch(`${API}/api/v2/rankings`).then(r => r.ok ? r.json() : null),
    ]).then(([cRes, rRes]) => {
      if (cancelled) return
      const cal = cRes.status === 'fulfilled' ? cRes.value : null
      const rk = rRes.status === 'fulfilled' ? rRes.value : null
      const liveCorr =
        cal?.accuracy_calibration_correlation ??
        cal?.verbalized?.per_model?.accuracy_calibration_correlation
      if (liveCorr && Object.keys(liveCorr).length) setCorr(liveCorr)
      const accPm = rk?.accuracy?.per_model
      if (accPm) {
        const next = {}
        for (const m of MODELS) if (accPm[m]?.mean != null) next[m] = accPm[m].mean
        if (Object.keys(next).length) setAcc(prev => ({ ...prev, ...next }))
      }
    }).catch(() => {})
    return () => { cancelled = true }
  }, [])

  const points = Object.keys(corr).map(m => ({
    model: m,
    accuracy: acc[m] ?? null,
    r: corr[m],
  })).filter(p => p.accuracy != null)

  return (
    <PanelShell
      title="Accuracy vs calibration per model"
      subtitle="Pearson r between per-task aggregate (literature-weighted NMACR) and per-task confidence proxy (dim_C)"
      accent="#A78BFA"
      caption="For each model, Pearson correlation between accuracy and calibration. Higher r = confidence tracks accuracy more closely. Post Phase 1.8 (2026-05-04): Mistral r=0.42, DeepSeek r=0.42, Claude r=0.42, Gemini r=0.39, ChatGPT r=0.36 — all five models in a tight band (0.36–0.42), all positive. No model is inversely calibrated. Reference line at r=0 (no correlation)."
      subCaption="Source: experiments/results_v2/calibration.json (accuracy_calibration_correlation block) + bootstrap_ci.json (accuracy means)."
    >
      <div style={{ width: '100%', height: 300 }}>
        <ResponsiveContainer>
          <ScatterChart margin={{ top: 16, right: 24, bottom: 32, left: 8 }}>
            <CartesianGrid strokeDasharray="2 4" stroke="rgba(255,255,255,0.07)" />
            <XAxis
              type="number" dataKey="accuracy" name="accuracy"
              domain={[0.6, 0.8]}
              tick={{ fill: 'rgba(232,244,248,0.7)', fontSize: 11 }}
              tickFormatter={v => v.toFixed(2)}
              label={{ value: 'accuracy (literature-weighted NMACR)', position: 'insideBottom', offset: -16, fill: 'rgba(232,244,248,0.6)', fontSize: 11 }}
            />
            <YAxis
              type="number" dataKey="r" name="r"
              domain={[-0.1, 0.6]}
              tick={{ fill: 'rgba(232,244,248,0.7)', fontSize: 11 }}
              tickFormatter={v => v.toFixed(2)}
              label={{ value: 'acc–calib r', angle: -90, position: 'insideLeft', fill: 'rgba(232,244,248,0.6)', fontSize: 11 }}
            />
            <ZAxis range={[140, 140]} />
            <Tooltip
              cursor={{ stroke: 'rgba(0,255,224,0.3)', strokeDasharray: '3 3' }}
              content={({ active, payload }) => {
                if (!active || !payload?.[0]) return null
                const p = payload[0].payload
                return (
                  <TooltipBox>
                    <div style={{ color: MODEL_COLORS[p.model], fontWeight: 700, marginBottom: 4 }}>{p.model}</div>
                    <div>accuracy: {p.accuracy.toFixed(3)}</div>
                    <div>acc–calib r: {p.r.toFixed(3)}</div>
                  </TooltipBox>
                )
              }}
            />
            <ReferenceLine
              y={0} stroke="#FFB347" strokeDasharray="4 4"
              label={{ value: 'r = 0', fill: '#FFB347', fontSize: 10, position: 'right' }}
            />
            <Scatter data={points} shape="circle">
              {points.map(p => <Cell key={p.model} fill={MODEL_COLORS[p.model]} stroke="#fff" strokeWidth={1} />)}
              <LabelList
                dataKey="model"
                position="top"
                style={{ fill: 'rgba(232,244,248,0.85)', fontSize: 11, fontFamily: 'monospace' }}
              />
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </PanelShell>
  )
}

// ═══════════════════════════════════════════════════════════════
// §5 — STATISTICAL VALIDATION (visualization-first restructure)
// ═══════════════════════════════════════════════════════════════

// Canonical post-Phase-1.8 (2026-05-04) — bootstrap_ci.json B=10000 seed=42
const BOOTSTRAP_ACCURACY = [
  { model: 'gemini',   mean: 0.7314, ci_low: 0.7060, ci_high: 0.7565 },
  { model: 'claude',   mean: 0.6976, ci_low: 0.6694, ci_high: 0.7249 },
  { model: 'chatgpt',  mean: 0.6733, ci_low: 0.6449, ci_high: 0.7012 },
  { model: 'deepseek', mean: 0.6686, ci_low: 0.6384, ci_high: 0.6988 },
  { model: 'mistral',  mean: 0.6676, ci_low: 0.6401, ci_high: 0.6949 },
]

const BOOTSTRAP_ROBUSTNESS = [
  { model: 'chatgpt',  mean: 0.0003, ci_low: -0.0133, ci_high: 0.0144 },
  { model: 'mistral',  mean: 0.0013, ci_low: -0.0116, ci_high: 0.0142 },
  { model: 'gemini',   mean: 0.0129, ci_low: -0.0026, ci_high: 0.0288 },
  { model: 'claude',   mean: 0.0305, ci_low:  0.0163, ci_high: 0.0445 },
  { model: 'deepseek', mean: 0.0388, ci_low:  0.0215, ci_high: 0.0560 },
]

function shapeForestPoints(rows) {
  return rows.map(r => ({
    ...r,
    err: [r.mean - r.ci_low, r.ci_high - r.mean],
  }))
}

function ForestChart({ data, domain, refX = null, valueLabel = 'mean', height = 220 }) {
  const points = shapeForestPoints(data)
  return (
    <div style={{ width: '100%', height }}>
      <ResponsiveContainer>
        <ScatterChart margin={{ top: 14, right: 90, bottom: 24, left: 8 }}>
          <CartesianGrid strokeDasharray="2 4" stroke="rgba(255,255,255,0.06)" horizontal={false} />
          <XAxis
            type="number"
            dataKey="mean"
            domain={domain}
            tick={{ fill: 'rgba(232,244,248,0.6)', fontSize: 10, fontFamily: 'monospace' }}
            tickFormatter={v => v.toFixed(3)}
          />
          <YAxis
            type="category"
            dataKey="model"
            tick={{ fill: 'rgba(232,244,248,0.9)', fontSize: 11, fontFamily: 'monospace' }}
            width={70}
            interval={0}
          />
          <ZAxis range={[120, 120]} />
          <Tooltip
            cursor={{ stroke: 'rgba(0,255,224,0.3)', strokeDasharray: '3 3' }}
            content={({ active, payload }) => {
              if (!active || !payload?.[0]) return null
              const p = payload[0].payload
              return (
                <TooltipBox>
                  <div style={{ color: MODEL_COLORS[p.model], fontWeight: 700, marginBottom: 4 }}>{p.model}</div>
                  <div>{valueLabel}: {p.mean.toFixed(4)}</div>
                  <div>95% CI: [{p.ci_low.toFixed(4)}, {p.ci_high.toFixed(4)}]</div>
                </TooltipBox>
              )
            }}
          />
          {refX !== null && (
            <ReferenceLine
              x={refX}
              stroke="#FFB347"
              strokeWidth={1.5}
              strokeDasharray="3 3"
              label={{ value: `Δ = ${refX}`, fill: '#FFB347', fontSize: 11, fontWeight: 700, position: 'top', offset: 4 }}
            />
          )}
          <Scatter data={points} shape="circle">
            {points.map(p => (
              <Cell key={p.model} fill={MODEL_COLORS[p.model]} stroke="#fff" strokeWidth={1.4} />
            ))}
            <ErrorBar
              dataKey="err"
              direction="x"
              width={6}
              strokeWidth={2}
              stroke="rgba(232,244,248,0.55)"
            />
            <LabelList
              dataKey="mean"
              position="right"
              offset={14}
              formatter={(v) => (v >= 0 ? '' : '−') + Math.abs(v).toFixed(3)}
              style={{ fill: 'rgba(232,244,248,0.95)', fontSize: 11, fontFamily: 'monospace', fontWeight: 600 }}
            />
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  )
}

export function BootstrapValidationPanel() {
  return (
    <div className="validation-panel">
      <div className="validation-panel-header">
        <span className="validation-label">BOOTSTRAP CI SEPARABILITY</span>
        <span className="validation-meta">B=10,000 · seed=42 · percentile method</span>
      </div>

      <div className="forest-row">
        <div className="forest-section">
          <div className="forest-section-title">Accuracy (literature-weighted NMACR)</div>
          <ForestChart
            data={BOOTSTRAP_ACCURACY}
            domain={[0.60, 0.78]}
            valueLabel="accuracy"
          />
          <div className="forest-caption">
            Gemini #1 with 3.4pp lead over #2 Claude — pair <span className="mono-tag">not_separable</span> (CIs overlap).
          </div>
        </div>

        <div className="forest-section">
          <div className="forest-section-title">Robustness Δ (base − perturbation)</div>
          <ForestChart
            data={BOOTSTRAP_ROBUSTNESS}
            domain={[-0.03, 0.07]}
            refX={0}
            valueLabel="Δ"
          />
          <div className="forest-caption">
            ChatGPT, Mistral, Gemini CIs cross zero — three-of-five noise-equivalent. Only Claude & DeepSeek separate from Δ=0.
          </div>
        </div>
      </div>

      <div className="validation-panel-footer">
        Hochlehnert et al. 2025 · Statistical Fragility framing
      </div>
    </div>
  )
}

// ─── §5.2 — Krippendorff α point-and-error-bar ─────────────────
const KRIPP_DIMS = [
  {
    key: 'A', name: 'assumption_compliance', label: 'A · assumption',
    alpha:  0.5730, ci_low:  0.5155, ci_high:  0.6219,
    interp: 'moderate agreement', tone: 'positive',
  },
  {
    key: 'R', name: 'reasoning_quality', label: 'R · reasoning',
    alpha: -0.1246, ci_low: -0.1967, ci_high: -0.0589,
    interp: 'CI excludes 0 — systematic disagreement', tone: 'negative',
  },
  {
    key: 'M', name: 'method_structure', label: 'M · method',
    alpha: -0.0090, ci_low: -0.0723, ci_high:  0.0617,
    interp: 'CI contains 0 — chance-level', tone: 'neutral',
  },
]

const ALPHA_TONE_COLOR = {
  positive: '#7FFFD4',
  negative: '#FF6B6B',
  neutral:  '#8BAFC0',
}

function AlphaForestChart() {
  const data = KRIPP_DIMS.map(d => ({
    label: d.label,
    alpha: d.alpha,
    ci_low: d.ci_low,
    ci_high: d.ci_high,
    err: [d.alpha - d.ci_low, d.ci_high - d.alpha],
    tone: d.tone,
  }))
  return (
    <div style={{ width: '100%', height: 220 }}>
      <ResponsiveContainer>
        <ScatterChart margin={{ top: 22, right: 90, bottom: 24, left: 8 }}>
          <CartesianGrid strokeDasharray="2 4" stroke="rgba(255,255,255,0.06)" horizontal={false} />
          <XAxis
            type="number"
            dataKey="alpha"
            domain={[-0.30, 0.70]}
            tick={{ fill: 'rgba(232,244,248,0.6)', fontSize: 10, fontFamily: 'monospace' }}
            tickFormatter={v => v.toFixed(2)}
          />
          <YAxis
            type="category"
            dataKey="label"
            tick={{ fill: 'rgba(232,244,248,0.9)', fontSize: 11, fontFamily: 'monospace' }}
            width={140}
            interval={0}
          />
          <ZAxis range={[120, 120]} />
          <Tooltip
            cursor={{ stroke: 'rgba(0,255,224,0.3)', strokeDasharray: '3 3' }}
            content={({ active, payload }) => {
              if (!active || !payload?.[0]) return null
              const p = payload[0].payload
              return (
                <TooltipBox>
                  <div style={{ color: ALPHA_TONE_COLOR[p.tone], fontWeight: 700, marginBottom: 4 }}>{p.label}</div>
                  <div>α = {p.alpha.toFixed(4)}</div>
                  <div>95% CI: [{p.ci_low.toFixed(4)}, {p.ci_high.toFixed(4)}]</div>
                </TooltipBox>
              )
            }}
          />
          <ReferenceLine
            x={0}
            stroke="#FFB347"
            strokeWidth={1.6}
            strokeDasharray="3 3"
            label={{ value: 'α = 0 (chance)', fill: '#FFB347', fontSize: 11, fontWeight: 700, position: 'top', offset: 6 }}
          />
          <Scatter data={data} shape="circle">
            {data.map(d => (
              <Cell key={d.label} fill={ALPHA_TONE_COLOR[d.tone]} stroke="#fff" strokeWidth={1.4} />
            ))}
            <ErrorBar
              dataKey="err"
              direction="x"
              width={6}
              strokeWidth={2}
              stroke="rgba(232,244,248,0.55)"
            />
            <LabelList
              dataKey="alpha"
              position="right"
              offset={14}
              formatter={(v) => (v >= 0 ? '+' : '−') + Math.abs(v).toFixed(3)}
              style={{ fill: 'rgba(232,244,248,0.95)', fontSize: 11, fontFamily: 'monospace', fontWeight: 600 }}
            />
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  )
}

export function AlphaValidationPanel() {
  const fmt = (v) => (v >= 0 ? '+' : '−') + Math.abs(v).toFixed(3)
  return (
    <div className="validation-panel">
      <div className="validation-panel-header">
        <span className="validation-label">KRIPPENDORFF α · INTER-RATER RELIABILITY</span>
        <span className="validation-meta">Base scope n=750 · B=1,000 · seed=42</span>
      </div>

      <AlphaForestChart />

      <div className="validation-readout">
        {KRIPP_DIMS.map(d => (
          <div key={d.key} className="readout-row">
            <span className="readout-tag" style={{ color: ALPHA_TONE_COLOR[d.tone] }}>{d.label}</span>
            <span className="readout-value">
              {fmt(d.alpha)} [{fmt(d.ci_low)}, {fmt(d.ci_high)}]
            </span>
            <span className={`readout-interpretation tone-${d.tone}`}>{d.interp}</span>
          </div>
        ))}
      </div>

      <div className="validation-panel-footer">
        Adopted over Spearman ρ per Yamauchi 2025 · threshold-free framing (CI-vs-zero does the work)
      </div>
    </div>
  )
}

// ─── §5.3 — Tolerance sensitivity slope chart ──────────────────
// Canonical from experiments/results_v2/tolerance_sensitivity.json
// Rankings (1 = top accuracy at level):
//   tight   → chatgpt, claude, deepseek, mistral, gemini
//   default → claude, chatgpt, deepseek, mistral, gemini
//   loose   → claude, chatgpt, gemini, mistral, deepseek
const TOLERANCE_RANKS = [
  { level: 'tight',   claude: 2, chatgpt: 1, gemini: 5, deepseek: 3, mistral: 4 },
  { level: 'default', claude: 1, chatgpt: 2, gemini: 5, deepseek: 3, mistral: 4 },
  { level: 'loose',   claude: 1, chatgpt: 2, gemini: 3, deepseek: 5, mistral: 4 },
]

const TOLERANCE_ACCURACY = {
  tight:   { claude: 0.5636, chatgpt: 0.5720, gemini: 0.5127, deepseek: 0.5339, mistral: 0.5212 },
  default: { claude: 0.5847, chatgpt: 0.5720, gemini: 0.5297, deepseek: 0.5381, mistral: 0.5381 },
  loose:   { claude: 0.6102, chatgpt: 0.5805, gemini: 0.5593, deepseek: 0.5508, mistral: 0.5593 },
}

// Pre-compute rank-ordered model lists per tolerance level for column rendering.
function ranksForLevel(level) {
  const ranks = TOLERANCE_RANKS.find(r => r.level === level)
  return MODELS
    .map(m => ({ model: m, rank: ranks[m], acc: TOLERANCE_ACCURACY[level][m] }))
    .sort((a, b) => a.rank - b.rank)
}

export function ToleranceValidationPanel() {
  const tightRows   = ranksForLevel('tight')
  const defaultRows = ranksForLevel('default')
  const looseRows   = ranksForLevel('loose')

  // Track per-model rank by level for connector SVG
  const rankAt = (level, model) =>
    TOLERANCE_RANKS.find(r => r.level === level)[model]

  // Models that change rank across any level
  const movingModels = MODELS.filter(m => {
    const t = rankAt('tight', m), d = rankAt('default', m), l = rankAt('loose', m)
    return !(t === d && d === l)
  })

  // SVG connector geometry (matches CSS row height + grid columns)
  const ROW_H = 30, ROW_GAP = 12, ROW_OFFSET = 14 // dot vertical alignment within row
  const yFor = (rank) => 60 + (rank - 1) * (ROW_H + ROW_GAP) + ROW_OFFSET
  const TOTAL_H = 60 + 5 * (ROW_H + ROW_GAP) + 20

  return (
    <div className="validation-panel">
      <div className="validation-panel-header">
        <span className="validation-label">TOLERANCE SENSITIVITY</span>
        <span className="validation-meta">3 tolerance bands · n=236 numeric runs/level/model</span>
      </div>

      <div className="tolerance-leaderboards" style={{ minHeight: TOTAL_H }}>
        {[
          { key: 'tight',   header: 'TIGHT',   range: '(0.005, 0.025)', rows: tightRows },
          { key: 'default', header: 'DEFAULT', range: '(0.010, 0.050)', rows: defaultRows },
          { key: 'loose',   header: 'LOOSE',   range: '(0.020, 0.100)', rows: looseRows },
        ].map(col => (
          <div key={col.key} className="tolerance-column">
            <div className="tolerance-column-header">
              <div>{col.header}</div>
              <div style={{ fontSize: 9, opacity: 0.6, marginTop: 2 }}>{col.range}</div>
            </div>
            {col.rows.map(r => (
              <div key={r.model} className="tolerance-rank-row">
                <span className="tolerance-rank-num">#{r.rank}</span>
                <span className="tolerance-rank-model">
                  <span className="tolerance-rank-dot" style={{ background: MODEL_COLORS[r.model] }} />
                  <span className="tolerance-rank-name">{r.model}</span>
                </span>
              </div>
            ))}
          </div>
        ))}

        {/* Bezier connectors for rank-changing models */}
        <svg className="tolerance-connector-svg" viewBox={`0 0 1000 ${TOTAL_H}`} preserveAspectRatio="none">
          {movingModels.map(m => {
            const yT = yFor(rankAt('tight', m))
            const yD = yFor(rankAt('default', m))
            const yL = yFor(rankAt('loose', m))
            const x1 = 333, x2 = 500, x3 = 667, x4 = 833
            const cps = 60
            return (
              <g key={m}>
                <path
                  d={`M ${x1} ${yT} C ${x1 + cps} ${yT} ${x2 - cps} ${yD} ${x2} ${yD}`}
                  stroke={MODEL_COLORS[m]}
                  strokeWidth={2.2}
                  fill="none"
                  opacity={0.85}
                />
                <path
                  d={`M ${x3} ${yD} C ${x3 + cps} ${yD} ${x4 - cps} ${yL} ${x4} ${yL}`}
                  stroke={MODEL_COLORS[m]}
                  strokeWidth={2.2}
                  fill="none"
                  opacity={0.85}
                />
              </g>
            )
          })}
        </svg>
      </div>

      <div className="validation-panel-footer">
        Gemini swings worst→mid (#5→#3) as tolerance loosens; DeepSeek slips #3→#5; Claude/ChatGPT stable at top. Bayesian closed-form numerics are tolerance-sensitive at the boundary, not numerically fragile within typical bounds.
      </div>
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════
// §6 — CALIBRATION METHOD-DEPENDENCE (dual-leaderboard infographic)
// ═══════════════════════════════════════════════════════════════

// Canonical post-Phase-1.8 (2026-05-04) — calibration.json + self_consistency_calibration.json
const CALIB_VERBALIZED = [
  { model: 'claude',   ece: 0.0334 },
  { model: 'chatgpt',  ece: 0.0339 },
  { model: 'gemini',   ece: 0.0765 },
  { model: 'mistral',  ece: 0.0811 },
  { model: 'deepseek', ece: 0.1977 },
]

const CALIB_CONSISTENCY = [
  { model: 'gemini',   ece: 0.6178 },
  { model: 'mistral',  ece: 0.6632 },
  { model: 'chatgpt',  ece: 0.7214 },
  { model: 'deepseek', ece: 0.7261 },
  { model: 'claude',   ece: 0.7342 },
]

export function CalibrationMethodComparisonPanel() {
  // Rank lookup per side
  const verbalRank = Object.fromEntries(CALIB_VERBALIZED.map((r, i) => [r.model, i + 1]))
  const consistRank = Object.fromEntries(CALIB_CONSISTENCY.map((r, i) => [r.model, i + 1]))

  // SVG connector geometry (matches CSS row geometry)
  const ROW_H = 30, ROW_GAP = 10, ROW_OFFSET = 18
  const Y_HEADER = 60
  const yFor = (rank) => Y_HEADER + (rank - 1) * (ROW_H + ROW_GAP) + ROW_OFFSET
  const TOTAL_H = Y_HEADER + 5 * (ROW_H + ROW_GAP) + 20

  return (
    <div className="validation-panel">
      <div className="validation-panel-header">
        <span className="validation-label">CALIBRATION IS METHOD-DEPENDENT</span>
        <span className="validation-meta">verbalized ECE vs self-consistency ECE · per-model rankings flip</span>
      </div>

      <div className="calibration-headline">SAME MODELS · DIFFERENT METHODS · DIFFERENT LEADERBOARDS</div>

      <div className="calibration-method-comparison" style={{ minHeight: TOTAL_H }}>
        <div className="calibration-column">
          <div className="calibration-column-header verbalized">
            <div>VERBALIZED ECE</div>
            <div style={{ fontSize: 9, opacity: 0.7, marginTop: 2 }}>keyword extraction · n=171/model</div>
          </div>
          {CALIB_VERBALIZED.map((r, i) => (
            <div key={r.model} className="calibration-rank-row">
              <span className="tolerance-rank-num">#{i + 1}</span>
              <span className="tolerance-rank-model">
                <span className="tolerance-rank-dot" style={{ background: MODEL_COLORS[r.model] }} />
                <span className="tolerance-rank-name">{r.model}</span>
              </span>
              <span style={{ color: 'rgba(232,244,248,0.95)', textAlign: 'right' }}>{r.ece.toFixed(3)}</span>
            </div>
          ))}
          <div className="calibration-summary-line">
            range 0.03–0.20 — looks well-calibrated
          </div>
        </div>

        <div className="calibration-column">
          <div className="calibration-column-header consistency">
            <div>SELF-CONSISTENCY ECE</div>
            <div style={{ fontSize: 9, opacity: 0.7, marginTop: 2 }}>3 reruns @ T=0.7 · n=161 numeric</div>
          </div>
          {CALIB_CONSISTENCY.map((r, i) => (
            <div key={r.model} className="calibration-rank-row">
              <span className="tolerance-rank-num">#{i + 1}</span>
              <span className="tolerance-rank-model">
                <span className="tolerance-rank-dot" style={{ background: MODEL_COLORS[r.model] }} />
                <span className="tolerance-rank-name">{r.model}</span>
              </span>
              <span style={{ color: 'rgba(232,244,248,0.95)', textAlign: 'right' }}>{r.ece.toFixed(3)}</span>
            </div>
          ))}
          <div className="calibration-summary-line">
            range 0.62–0.73 — severely overconfident
          </div>
        </div>

        {/* Bezier connectors — every model crosses */}
        <svg className="tolerance-connector-svg" viewBox={`0 0 1000 ${TOTAL_H}`} preserveAspectRatio="none">
          {MODELS.map(m => {
            const yL = yFor(verbalRank[m])
            const yR = yFor(consistRank[m])
            const x1 = 380, x2 = 620
            const cps = 80
            return (
              <path
                key={m}
                d={`M ${x1} ${yL} C ${x1 + cps} ${yL} ${x2 - cps} ${yR} ${x2} ${yR}`}
                stroke={MODEL_COLORS[m]}
                strokeWidth={2.4}
                fill="none"
                opacity={0.85}
              />
            )
          })}
        </svg>
      </div>

      <div className="validation-panel-footer">
        Every model reverses direction between methods. Claude #1 → #5; Gemini #3 → #1; DeepSeek #5 → #4. Per-task accuracy-calibration correlations stay tight (Mistral 0.42, DeepSeek 0.42, Claude 0.42, Gemini 0.39, ChatGPT 0.36) — the leaderboard flip is method-driven, not signal-strength driven.
      </div>
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════
// §7 — ELIGIBILITY FILTERS (stacked-bar funnel)
// ═══════════════════════════════════════════════════════════════

export function EligibilityFunnelPanel() {
  const baseTotal = 855, baseElig = 750, baseExcl = 105
  const pertTotal = 2365, pertElig = 2100, pertExcl = 265
  const combTotal = 3220, combElig = 2850, combPct = 88.5

  const Bar = ({ label, total, eligible, excluded }) => {
    const eligPct = (eligible / total) * 100
    const exclPct = (excluded / total) * 100
    return (
      <div className="eligibility-bar-row">
        <span className="eligibility-label">{label}</span>
        <div className="eligibility-bar">
          <div className="eligibility-bar-eligible" style={{ width: `${eligPct}%` }}>
            {eligible.toLocaleString()} eligible
          </div>
          <div className="eligibility-bar-excluded" style={{ width: `${exclPct}%` }}>
            {excluded} excl
          </div>
        </div>
        <span className="eligibility-total">total {total.toLocaleString()}</span>
      </div>
    )
  }

  return (
    <div className="validation-panel">
      <div className="validation-panel-header">
        <span className="validation-label">ELIGIBILITY FILTERS · WHO COUNTS IN α</span>
        <span className="validation-meta">methodologically-justified exclusion · matches Limitations L6</span>
      </div>

      <div className="eligibility-funnel">
        <Bar label="base runs"          total={baseTotal} eligible={baseElig} excluded={baseExcl} />
        <Bar label="perturbation runs"  total={pertTotal} eligible={pertElig} excluded={pertExcl} />

        <div className="eligibility-combined">
          COMBINED · {combElig.toLocaleString()} of {combTotal.toLocaleString()} = {combPct}% eligible
        </div>

        <div className="eligibility-rationale">
          <strong style={{ color: 'rgba(232,244,248,0.85)' }}>Why excluded:</strong> 21 distinct task families ×
          5 models — CONCEPTUAL · MINIMAX · BAYES_RISK plus the MARKOV_04 outlier — share empty
          <code style={{ fontSize: 11, padding: '0 4px', color: '#FFB347' }}>required_assumption_checks</code>.
          Keyword and judge scoring of assumption articulation cannot be compared on tasks that don&apos;t
          require assumption articulation. The same filter applies symmetrically to perturbation runs
          (each excluded base task contributes 2–3 perturbations × 5 models).
        </div>
      </div>

      <div className="validation-panel-footer">
        Self-consistency: 161/171 tasks (10 CONCEPTUAL excluded — no numeric answer for 3-rerun agreement).
        Error taxonomy: 143 base failures classified; FORMATTING_FAILURE (18/143) reported separately.
      </div>
    </div>
  )
}
