import {
  CartesianGrid, XAxis, YAxis, ZAxis, Tooltip,
  ReferenceLine, ResponsiveContainer,
  ScatterChart, Scatter, Cell, ErrorBar, LabelList,
} from 'recharts'
import { SITE_PALETTE, ACCENTS, RECHARTS_THEME, SEMANTIC } from '../data/sitePalette'

const KRIPP_DIMS = [
  {
    key: 'A', label: 'A · assumption',
    alpha:  0.5730, ci_low:  0.5155, ci_high:  0.6219,
    interp: 'moderate', tone: 'positive',
  },
  {
    key: 'R', label: 'R · reasoning',
    alpha: -0.1246, ci_low: -0.1967, ci_high: -0.0589,
    interp: 'CI excludes 0', tone: 'negative',
  },
  {
    key: 'M', label: 'M · method',
    alpha: -0.0090, ci_low: -0.0723, ci_high:  0.0617,
    interp: 'CI contains 0', tone: 'neutral',
  },
]

const TONE_COLOR = {
  positive: SEMANTIC.good,
  negative: SEMANTIC.bad,
  neutral:  SITE_PALETTE.fgMuted,
}

const fmtSigned = (v) => (v >= 0 ? '+' : '−') + Math.abs(v).toFixed(3)

function TooltipBox({ children }) {
  return (
    <div style={{
      ...RECHARTS_THEME.tooltipContentStyle,
      fontFamily: 'monospace',
      fontSize: 11,
      lineHeight: 1.55,
    }}>{children}</div>
  )
}

export function AgreementMetricsForestPanel() {
  const data = KRIPP_DIMS.map(d => ({
    label: d.label,
    alpha: d.alpha,
    ci_low: d.ci_low,
    ci_high: d.ci_high,
    err: [d.alpha - d.ci_low, d.ci_high - d.alpha],
    tone: d.tone,
  }))

  return (
    <div className="agreement-metrics-panel">
      <div className="agreement-metrics-header">
        <span className="agreement-metrics-label">AGREEMENT METRICS — KEYWORD vs EXTERNAL JUDGE</span>
        <span className="agreement-metrics-meta">Base scope · n=750 · 3 shared dimensions · B=1,000 · seed=42</span>
      </div>

      <div style={{ width: '100%', height: 240 }}>
        <ResponsiveContainer>
          <ScatterChart margin={{ top: 38, right: 28, bottom: 24, left: 8 }}>
            <CartesianGrid strokeDasharray={RECHARTS_THEME.gridStrokeDasharray} stroke={RECHARTS_THEME.gridStroke} horizontal={false} />
            <XAxis
              type="number"
              dataKey="alpha"
              domain={[-0.30, 0.70]}
              ticks={[-0.25, 0, 0.25, 0.5]}
              tick={{ fill: RECHARTS_THEME.axisTickColor, fontSize: 10, fontFamily: 'monospace' }}
              stroke={RECHARTS_THEME.axisStroke}
              tickFormatter={v => v.toFixed(2)}
            />
            <YAxis
              type="category"
              dataKey="label"
              tick={{ fill: SITE_PALETTE.fg, fontSize: 11, fontFamily: 'monospace' }}
              stroke={RECHARTS_THEME.axisStroke}
              width={140}
              interval={0}
              padding={{ top: 14, bottom: 8 }}
            />
            <ZAxis range={[120, 120]} />
            <Tooltip
              cursor={{ stroke: SITE_PALETTE.fgMuted, strokeDasharray: '3 3' }}
              content={({ active, payload }) => {
                if (!active || !payload?.[0]) return null
                const p = payload[0].payload
                return (
                  <TooltipBox>
                    <div style={{ color: TONE_COLOR[p.tone], fontWeight: 700, marginBottom: 4 }}>{p.label}</div>
                    <div>α = {p.alpha.toFixed(4)}</div>
                    <div>95% CI: [{p.ci_low.toFixed(4)}, {p.ci_high.toFixed(4)}]</div>
                  </TooltipBox>
                )
              }}
            />
            <ReferenceLine
              x={0}
              stroke={ACCENTS.gold}
              strokeWidth={1.6}
              strokeDasharray="3 3"
              label={{ value: 'α = 0 (chance)', fill: ACCENTS.gold, fontSize: 11, fontWeight: 700, position: 'top', offset: 8 }}
            />
            <Scatter data={data} shape="circle">
              {data.map(d => (
                <Cell key={d.label} fill={TONE_COLOR[d.tone]} stroke={SITE_PALETTE.fg} strokeWidth={1.4} />
              ))}
              <ErrorBar
                dataKey="err"
                direction="x"
                width={6}
                strokeWidth={2}
                stroke={SITE_PALETTE.fgMuted}
              />
              <LabelList
                dataKey="alpha"
                position="top"
                offset={10}
                formatter={fmtSigned}
                style={{ fill: SITE_PALETTE.fg, fontSize: 11, fontFamily: 'monospace', fontWeight: 600 }}
              />
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      <div className="alpha-readout">
        {KRIPP_DIMS.map(d => (
          <div key={d.key} className={`readout-row tone-${d.tone}`}>
            <span className="readout-tag" style={{ color: TONE_COLOR[d.tone] }}>{d.label}</span>
            <span className="readout-value">
              {fmtSigned(d.alpha)}
              <span className="readout-ci"> [{fmtSigned(d.ci_low)}, {fmtSigned(d.ci_high)}]</span>
            </span>
            <span className="readout-interp" style={{ color: TONE_COLOR[d.tone] }}>{d.interp}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

// ─── Confusion matrix (Panel 2) ─────────────────────────────────
const CONFUSION = {
  total: 750,
  both_pass: 376,
  keyword_only_pass: 157,
  judge_only_pass: 42,
  both_fail: 175,
}

const COMBINED_FLIP_PCT = 20.74

export function JudgeKeywordConfusionMatrix() {
  const { total, both_pass, keyword_only_pass, judge_only_pass, both_fail } = CONFUSION
  const flips = keyword_only_pass + judge_only_pass
  const pct = (n) => ((n / total) * 100).toFixed(1)

  return (
    <div className="confusion-matrix-panel">
      <div className="confusion-matrix-header">
        <span className="confusion-matrix-label">JUDGE vs KEYWORD — DISAGREEMENT MATRIX</span>
        <span className="confusion-matrix-meta">Base scope · n=750 eligible · assumption_compliance dimension</span>
      </div>

      <div className="confusion-grid">
        <div className="grid-corner" />
        <div className="grid-col-header">JUDGE: PASS</div>
        <div className="grid-col-header">JUDGE: FAIL</div>

        <div className="grid-row-header">KEYWORD: PASS</div>
        <div className="grid-cell agreement">
          <div className="cell-count">{both_pass}</div>
          <div className="cell-pct">{pct(both_pass)}%</div>
          <div className="cell-label">agreement — both pass</div>
        </div>
        <div className="grid-cell flip">
          <div className="cell-count">{keyword_only_pass}</div>
          <div className="cell-pct">{pct(keyword_only_pass)}%</div>
          <div className="cell-label">flip — keyword over-credits</div>
        </div>

        <div className="grid-row-header">KEYWORD: FAIL</div>
        <div className="grid-cell flip">
          <div className="cell-count">{judge_only_pass}</div>
          <div className="cell-pct">{pct(judge_only_pass)}%</div>
          <div className="cell-label">flip — keyword under-credits</div>
        </div>
        <div className="grid-cell agreement">
          <div className="cell-count">{both_fail}</div>
          <div className="cell-pct">{pct(both_fail)}%</div>
          <div className="cell-label">agreement — both fail</div>
        </div>
      </div>

      <div className="confusion-summary">
        <span className="summary-stat">
          <strong>{flips}</strong> of <strong>{total}</strong> base runs flip pass/fail
          (<strong>{((flips / total) * 100).toFixed(1)}%</strong> total disagreement;
          {' '}<strong>{pct(keyword_only_pass)}%</strong> directional pass-flip)
        </span>
      </div>

      <div className="confusion-footer">
        Off-diagonal mass = the disagreement reported in the headline metrics.
        Combined denominator (base + perturbation, n=2,850) holds at <strong>{COMBINED_FLIP_PCT}%</strong> directional pass-flip (591 cases).
      </div>
    </div>
  )
}

// ─── Per-perturbation-type breakdown (Panel 3) ──────────────────
const PERT_BREAKDOWN = [
  { label: 'REPHRASE',  pct: 21.6, n: 162, total: 750, color: '#5eead4' },
  { label: 'NUMERICAL', pct: 22.7, n: 136, total: 600, color: '#a78bfa' },
  { label: 'SEMANTIC',  pct: 18.1, n: 136, total: 750, color: '#fbbf24' },
]

export function DisagreementByPertTypePanel() {
  const SCALE_MAX = 27
  const combinedPct = COMBINED_FLIP_PCT
  const combinedLeft = (combinedPct / SCALE_MAX) * 100

  return (
    <div className="agreement-metrics-panel">
      <div className="agreement-metrics-header">
        <span className="agreement-metrics-label">DISAGREEMENT BY PERTURBATION TYPE</span>
        <span className="agreement-metrics-meta">Base + perturbation scope · n=2,850 · directional pass-flip</span>
      </div>

      <div style={{ position: 'relative', padding: '20px 8px 12px', minHeight: 240 }}>
        <div style={{
          position: 'absolute', top: 18, bottom: 32,
          left: `calc(118px + (100% - 222px) * ${combinedPct / SCALE_MAX})`, width: 0,
          borderLeft: '1px dashed rgba(148,163,184,0.7)', zIndex: 1,
        }} />
        <div style={{
          position: 'absolute', top: 0,
          left: `calc(118px + (100% - 222px) * ${combinedPct / SCALE_MAX})`,
          transform: 'translateX(-50%)',
          fontFamily: 'monospace', fontSize: 11, fontWeight: 700,
          color: 'rgba(148,163,184,0.95)', whiteSpace: 'nowrap', zIndex: 2,
        }}>
          combined {combinedPct}%
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 18, marginTop: 22 }}>
          {PERT_BREAKDOWN.map(r => (
            <div key={r.label} style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
              <span style={{
                width: 104, fontFamily: 'monospace', fontSize: 12,
                fontWeight: 800, letterSpacing: '0.08em', color: r.color,
                flexShrink: 0,
              }}>{r.label}</span>
              <div style={{ position: 'relative', flex: 1, height: 30, background: 'rgba(255,255,255,0.04)', borderRadius: 4 }}>
                <div style={{
                  height: '100%', width: `${(r.pct / SCALE_MAX) * 100}%`,
                  background: r.color, borderRadius: 4, opacity: 0.92,
                }} />
              </div>
              <span style={{
                width: 100, fontFamily: 'monospace', fontSize: 13,
                color: 'rgba(232,244,248,0.92)', fontWeight: 700,
                textAlign: 'left', flexShrink: 0,
              }}>
                <span style={{ color: '#fff', fontSize: 14, fontWeight: 800 }}>{r.pct.toFixed(1)}%</span>
                <span style={{ display: 'block', color: 'rgba(232,244,248,0.55)', fontSize: 10.5, marginTop: 2 }}>{r.n}/{r.total}</span>
              </span>
            </div>
          ))}
        </div>

        <div style={{
          fontFamily: 'monospace', fontSize: 10,
          color: 'rgba(232,244,248,0.45)', display: 'flex',
          justifyContent: 'space-between', marginTop: 14, padding: '0 100px 0 118px',
        }}>
          <span>0%</span><span>{SCALE_MAX}%</span>
        </div>
      </div>

      <div className="confusion-summary">
        <span className="summary-stat">
          <strong>434</strong> of <strong>2,100</strong> perturbation runs flip pass/fail across REPHRASE / NUMERICAL / SEMANTIC
          (combined directional pass-flip rate <strong>{combinedPct}%</strong> on n=2,850).
        </span>
      </div>

      <div className="confusion-footer">
        All three flavors land within ±5pp of the combined cohort rate.
        Disagreement is a structural property of model output, not an artifact
        of any one perturbation flavor. NUMERICAL trends slightly higher;
        SEMANTIC slightly lower; REPHRASE sits at the cohort mean.
      </div>
    </div>
  )
}
