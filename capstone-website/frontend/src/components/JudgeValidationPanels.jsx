import {
  CartesianGrid, XAxis, YAxis, ZAxis, Tooltip,
  ReferenceLine, ResponsiveContainer,
  ScatterChart, Scatter, Cell, ErrorBar, LabelList,
} from 'recharts'

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
  positive: '#7FFFD4',
  negative: '#FF6B6B',
  neutral:  '#8BAFC0',
}

const fmtSigned = (v) => (v >= 0 ? '+' : '−') + Math.abs(v).toFixed(3)

function TooltipBox({ children }) {
  return (
    <div style={{
      background: 'rgba(8,12,24,0.96)',
      border: '1px solid rgba(0,255,224,0.4)',
      borderRadius: 6,
      padding: '8px 12px',
      fontFamily: 'monospace',
      fontSize: 11,
      color: '#fff',
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
            <CartesianGrid strokeDasharray="2 4" stroke="rgba(255,255,255,0.06)" horizontal={false} />
            <XAxis
              type="number"
              dataKey="alpha"
              domain={[-0.30, 0.70]}
              ticks={[-0.25, 0, 0.25, 0.5]}
              tick={{ fill: 'rgba(232,244,248,0.6)', fontSize: 10, fontFamily: 'monospace' }}
              tickFormatter={v => v.toFixed(2)}
            />
            <YAxis
              type="category"
              dataKey="label"
              tick={{ fill: 'rgba(232,244,248,0.9)', fontSize: 11, fontFamily: 'monospace' }}
              width={140}
              interval={0}
              padding={{ top: 14, bottom: 8 }}
            />
            <ZAxis range={[120, 120]} />
            <Tooltip
              cursor={{ stroke: 'rgba(0,255,224,0.3)', strokeDasharray: '3 3' }}
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
              stroke="#FFB347"
              strokeWidth={1.6}
              strokeDasharray="3 3"
              label={{ value: 'α = 0 (chance)', fill: '#FFB347', fontSize: 11, fontWeight: 700, position: 'top', offset: 8 }}
            />
            <Scatter data={data} shape="circle">
              {data.map(d => (
                <Cell key={d.label} fill={TONE_COLOR[d.tone]} stroke="#fff" strokeWidth={1.4} />
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
                position="top"
                offset={10}
                formatter={fmtSigned}
                style={{ fill: 'rgba(232,244,248,0.95)', fontSize: 11, fontFamily: 'monospace', fontWeight: 600 }}
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
