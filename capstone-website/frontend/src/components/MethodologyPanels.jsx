import { useEffect, useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ReferenceLine, ResponsiveContainer, ScatterChart, Scatter, ZAxis,
  LabelList, Cell,
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

// ─── Panel 1: per-model pass-flip ────────────────────────────────
const STATIC_PASSFLIP = {
  combined: {
    pct_pass_flip: 0.2216,
    n_eligible: 3195,
    n_pass_flip: 708,
    per_model: {
      claude:   { n_total: 719, n_eligible: 639, n_pass_flip: 177, pct: 0.27699530516431925 },
      chatgpt:  { n_total: 719, n_eligible: 639, n_pass_flip: 122, pct: 0.19092331768388107 },
      gemini:   { n_total: 719, n_eligible: 639, n_pass_flip: 150, pct: 0.2347417840375587 },
      deepseek: { n_total: 719, n_eligible: 639, n_pass_flip: 122, pct: 0.19092331768388107 },
      mistral:  { n_total: 719, n_eligible: 639, n_pass_flip: 137, pct: 0.21439749608763695 },
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
  const avgPct = (combined.pct_pass_flip ?? 0.2216) * 100
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
      title="Pass-flip rate by model"
      subtitle="Combined base + perturbation analysis (n=3,195 eligible runs)"
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
                    <div>pass-flip: {r.pct.toFixed(2)}%</div>
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

// ─── Panel 2: keyword-degradation PNG ────────────────────────────
export function KeywordDegradationPanel() {
  return (
    <PanelShell
      title="Keyword vs Judge PASS rates: base vs perturbation"
      accent="#00B4D8"
      caption="Side-by-side comparison of PASS rates per model under base prompts and perturbed prompts, for both scoring methods. Note the divergence: keyword PASS rate (left bars per model) drops from base to perturbation while judge PASS rate (right bars) rises. The gap is largest on semantic perturbations, where vocabulary changes most aggressively break keyword regex matches."
      subCaption="Base: 1,095 runs · Perturbation: 2,100 runs · Combined: 3,195 runs. Per-perturbation-type differential: rephrase 1.96pp, numerical 2.92pp, semantic 5.96pp."
    >
      <img
        src="/visualizations/png/v2/combined_pass_flip_comparison.png"
        alt="Keyword vs judge PASS rates: base vs perturbation, per model"
        style={{
          width: '100%', height: 'auto', display: 'block',
          borderRadius: 8, background: 'rgba(255,255,255,0.02)',
        }}
        loading="lazy"
      />
    </PanelShell>
  )
}

// ─── Panel 3: per-dim robustness deltas ──────────────────────────
const STATIC_PER_DIM_DELTA = {
  claude:   { N: 0.0026,  M: 0.019,   A: 0.0698,  C: 0.015,   R: 0.0111 },
  chatgpt:  { N: -0.0099, M: 0.0106,  A: 0.0,     C: 0.0017,  R: 0.0032 },
  gemini:   { N: 0.0058,  M: 0.0137,  A: 0.0243,  C: null,    R: 0.0034 },
  deepseek: { N: -0.0435, M: 0.0053,  A: 0.1258,  C: -0.0393, R: 0.0225 },
  mistral:  { N: 0.0278,  M: -0.0127, A: -0.0116, C: 0.019,   R: -0.0119 },
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
      caption="Bars above zero = score decreased under perturbation (worse). DeepSeek shows the largest assumption-compliance degradation (+12.6pp on A); Mistral is uniquely robust on A and R (negative deltas = scores rose under perturbation). The N dimension (numerical correctness) is roughly stable for all models — math is robust; reasoning and assumption articulation are the brittle dimensions. Source: experiments/results_v2/robustness_v2.json (per_dim_delta block)."
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
  C: { claude: 0.0546, chatgpt: 0.0608, gemini: null,   deepseek: 0.039,  mistral: 0.0504 },
  R: { claude: 0.1125, chatgpt: 0.0926, gemini: 0.1292, deepseek: 0.091,  mistral: 0.0999 },
}

export function PerDimCalibrationPanel() {
  // Static-only: per_dim_calibration.json is not exposed by /api/v2/calibration.
  // Source data is committed in experiments/results_v2/per_dim_calibration.json.
  const rows = DIMS.map(dim => {
    const row = { dim }
    for (const m of MODELS) row[m] = STATIC_PER_DIM_ECE[dim]?.[m] ?? null
    return row
  })

  return (
    <PanelShell
      title="Calibration ECE by NMACR dimension"
      subtitle="Expected Calibration Error per dimension, by model (lower is better)"
      accent="#A78BFA"
      caption="Models calibrate moderately well on M (method) and best on C (verbalized confidence, 0.04–0.06 ECE). A (assumption) is the weakest dimension across all models (≈0.16–0.17 ECE) — confidence in assumption articulation poorly tracks accuracy. R varies most (DeepSeek 0.09 vs Gemini 0.13). Gemini has no C value (zero verbalized signals). Dashed line = 0.10 reference threshold for well-calibrated. Source: experiments/results_v2/per_dim_calibration.json."
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
  acc_calib_corr: { claude: 0.4905, chatgpt: 0.3712, deepseek: 0.3473, mistral: 0.4762 },
  accuracy: {
    claude: 0.712221, chatgpt: 0.691285, gemini: 0.776253,
    deepseek: 0.662972, mistral: 0.675376,
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
      const liveCorr = cal?.verbalized?.per_model?.accuracy_calibration_correlation
      if (liveCorr) setCorr(liveCorr)
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
      caption="For each model (excluding Gemini, which produces 0 verbalized confidence signals), correlation between accuracy and calibration. Higher r = confidence tracks accuracy more closely. Claude (r=0.49) and Mistral (r=0.48) show the strongest tracking; ChatGPT (r=0.37) and DeepSeek (r=0.35) are weaker. All r values are positive — no model is inversely calibrated. Reference line at r=0 (no correlation)."
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
