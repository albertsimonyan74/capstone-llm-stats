# WEBSITE_SCRAPE — capstone-website/frontend

Self-contained scrape of the live website. All values inlined — no cross-file
refs. Read top-to-bottom without the repo.

Source files extracted:
`src/App.css`, `src/index.css`, `src/App.jsx`, `src/main.jsx`,
`src/data/sitePalette.js`, `src/components/{MethodologyPanels,
JudgeValidationPanels, KeyFindings, ThreeRankingsComparison, Navbar,
MobiusStrip, NeuralNetwork, GlobeBackground, HeroNetworkBg, ExpandablePanel,
GlobalCursor, SideNav}.jsx`, `src/pages/{Methodology, Limitations,
References, UserStudy, VizGallery}.jsx`, plus
`backend/static_data/llm-stats-vault/40-literature/` for citation metadata.

---

## SECTION A — DESIGN TOKENS

### A.1 — CSS custom properties (root scope, `App.css:7-34`)

Loaded from `:root` and used across all components. `index.css:3-8` defines a
parallel `body` font/color block (`'Inter', system-ui` / `#0A0E1A` / `#E0F7FF`)
that is superseded as soon as `App.css` mounts.

#### Backgrounds

| Variable | Value | Used for |
|---|---|---|
| `--bg-primary` | `#0A0F1E` | `body`, every section background |
| `--bg-secondary` | `#0D1426` | `awaiting-inner` panel; tooltip-body candidate |
| `--bg-card` | `rgba(0, 255, 224, 0.04)` | every `.card` panel |
| `--bg-card-hover` | `rgba(0, 255, 224, 0.09)` | `.rq-item:hover` |
| (hardcoded body fallback) | `#0A0E1A` (`index.css:4`) | first paint before App.css loads |

Body also wears a fixed dot grid:
`radial-gradient(circle, rgba(0,206,209,0.10) 1px, transparent 1px)` at 32px
spacing, opacity 0.7 (`App.css:124-132`).

#### Surfaces / borders

| Variable | Value | Used for |
|---|---|---|
| `--border-default` | `rgba(0, 255, 224, 0.14)` | card border, RQ-item hover frame |
| `--border-hover` | `rgba(0, 255, 224, 0.40)` | card-glow border, btn-secondary edge |
| `--border-active` | `rgba(0, 255, 224, 0.80)` | reserved (no current selectors) |

Inline panel border canon: `1px solid rgba(0, 255, 224, 0.18)` — the de-facto
PanelShell stroke (used by `MethodologyPanels`, `validation-panel`).

#### Text

| Variable | Value | Used for |
|---|---|---|
| `--text-primary` | `#E8F4F8` | body text |
| `--text-secondary` | `#8BAFC0` | secondary labels |
| `--text-muted` | `#4A6A7A` | very-dim labels |
| (alt body color) | `#E0F7FF` (`index.css:5`) | first paint fallback |

Inline alpha-tinted whites used throughout as a de-facto secondary scale:
`rgba(232,244,248,0.40)`, `0.50`, `0.55`, `0.65`, `0.70`, `0.78`, `0.85`,
`0.92`. No tokenization for these — repeated 30+ times inline.

#### Primary accent

| Variable | Value | Used for |
|---|---|---|
| `--aqua` | `#00FFE0` | nav-logo title, link color, accent eyebrow, scroll progress, `:focus-visible` outline, alpha markers |
| `--aqua-light` | `#7FFFD4` | gradient end-stops, eligibility-eligible bar mid |
| `--aqua-dim` | `rgba(0, 255, 224, 0.6)` | (declared, no current selector) |
| `--cyan` | `#00FFE0` | alias of `--aqua` |
| `--blue` | `#00B4D8` | gradient mid, navbar underline, agreement-metrics-label |
| `--blue-deep` | `#0047AB` | btn-primary gradient end |

#### Glow shadows

| Variable | Value | Where |
|---|---|---|
| `--glow-sm` | `0 0 14px rgba(0, 255, 224, 0.22)` | scroll-progress, btn-primary, timeline-dot, orbit-dot, filter-dot, travel-dot, back-to-top, awaiting-inner spinner |
| `--glow-md` | `0 0 28px rgba(0, 255, 224, 0.35)` | timeline-dot.highlight, btn hover |
| `--glow-lg` | `0 0 56px rgba(0, 255, 224, 0.45)` | (declared, reserved) |

Tooltip shadow (Recharts): `0 8px 24px rgba(0, 0, 0, 0.4)` (sitePalette.js
`RECHARTS_THEME.tooltipContentStyle`).

#### Radii

| Variable | Value | Where |
|---|---|---|
| `--radius-sm` | `8px` | `.rq-item`, mono-tag chips |
| `--radius-md` | `12px` | `.btn-primary` / `.btn-secondary` |
| `--radius-lg` | `16px` | `.card` |
| `--radius-xl` | `24px` | `.awaiting-inner` |

Inline overrides common: `14px` (panel-shell), `8–10px` (sub-cards),
`3–4px` (chips), `50%` (dots).

#### Fonts

| Variable | Value |
|---|---|
| `--font-body` | `'Space Grotesk', sans-serif` |
| `--font-mono` | `'Space Mono', monospace` |

Loaded from Google Fonts CDN (`App.css:5`):
`https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap`

`index.css:6` declares `'Inter', system-ui, sans-serif` on `body` — visible
only during initial paint before App.css mounts. Single Times New Roman
exception: `.alpha-formula { font-family: 'Times New Roman', serif }` for
the Krippendorff α math display (`App.css:877`).

#### Motion (keyframes declared in `App.css:36-98`)

`orbit` (spinning model orbits, 360° translateX 220px), `ringRotate` /
`ringCCW` (lat/lon rings), `hubPulse` (center hub pulse), `pingLarge`
(button-style ping), `shimmerSweep`, `pulseDot`, `pulse`, `spinGradient`
(awaiting-inner conic spin, 3s linear), `travelDot` (3s ease-in-out
infinite), `float`, `gridShift`. All motion suppressed under
`@media (prefers-reduced-motion: reduce)`.

### A.2 — Section radial backgrounds (`App.css:319-336`)

Each section gets an off-axis radial overlay:

```css
.sec-overview   { background: radial-gradient(ellipse 80% 50% at 50% 0%,   rgba(0,206,209,0.08) 0%, transparent 70%) var(--bg-primary); }
.sec-pipeline   { background: radial-gradient(ellipse 60% 60% at 0%  50%,  rgba(0,191,255,0.05) 0%, transparent 70%) var(--bg-primary); }
.sec-difficulty { background: radial-gradient(ellipse 60% 60% at 100% 30%, rgba(0,206,209,0.05) 0%, transparent 70%) var(--bg-primary); }
.sec-models     { background: radial-gradient(ellipse 60% 60% at 100% 50%, rgba(0,206,209,0.05) 0%, transparent 70%) var(--bg-primary); }
.sec-tasks      { background: radial-gradient(ellipse 60% 60% at 20% 80%,  rgba(0,191,255,0.05) 0%, transparent 70%) var(--bg-primary); }
.sec-research   { background: radial-gradient(ellipse 60% 60% at 50% 100%, rgba(0,191,255,0.05) 0%, transparent 70%) var(--bg-primary); }
```

Plus `.sec-overview::after` overlays a 1px grid at 80×80 px in
`rgba(0,206,209,0.025)`.

### A.3 — Recurring gradients

| Where | Definition |
|---|---|
| Scroll progress bar | `linear-gradient(90deg, #00FFE0, #00B4D8, #7FFFD4)` |
| Nav underline / timeline rail | `linear-gradient(90deg, #00FFE0, #00B4D8)` |
| `.btn-primary` | `linear-gradient(135deg, #00FFE0, #0047AB)` |
| Eligibility eligible bar | `linear-gradient(90deg, #00FFE0, #7FFFD4)` |
| Eligibility excluded bar | `linear-gradient(90deg, #FFB347, #FF8A4D)` |
| Krippendorff α track | `linear-gradient(to right, rgba(248,113,113,0.45) 0%, rgba(248,113,113,0.22) 35%, rgba(255,255,255,0.15) 50%, rgba(127,255,212,0.22) 65%, rgba(127,255,212,0.45) 100%)` |
| Awaiting-results border | `conic-gradient(from 0deg at 50% 50%, var(--aqua) 0deg, var(--blue) 90deg, transparent 150deg, transparent 360deg)` (3s linear spin) |
| Body dot grid | `radial-gradient(circle, rgba(0,206,209,0.10) 1px, transparent 1px)` 32px |

### A.4 — `src/data/sitePalette.js` — full export verbatim

```javascript
// Canonical site palette for Recharts components.
// Mirrors scripts/site_palette.py — keep in sync.

export const SITE_PALETTE = {
  bg: '#0f1118',
  fg: '#e2e8f0',
  fgMuted: '#94a3b8',
  fgSubtle: '#475569',
};

export const MODEL_COLORS = {
  claude:   '#5eead4',
  chatgpt:  '#86efac',
  gemini:   '#fda4af',
  deepseek: '#93c5fd',
  mistral:  '#c4b5fd',
};

export const MODEL_COLORS_ARRAY = [
  MODEL_COLORS.claude,
  MODEL_COLORS.chatgpt,
  MODEL_COLORS.gemini,
  MODEL_COLORS.deepseek,
  MODEL_COLORS.mistral,
];

// Lookup helper — accepts any common casing.
export function modelColor(name) {
  if (!name) return SITE_PALETTE.fgMuted;
  const key = String(name).toLowerCase();
  return MODEL_COLORS[key] || SITE_PALETTE.fgMuted;
}

export const BUCKET_COLORS = {
  'Assumption Violation': '#fbbf24',
  'Mathematical Error':    '#f87171',
  'Formatting Failure':    '#94a3b8',
  'Conceptual Error':      '#a78bfa',
};

export const ACCENTS = {
  teal:   '#5eead4',
  purple: '#a78bfa',
  coral:  '#f87171',
  gold:   '#fbbf24',
};

export const SEMANTIC = {
  good:    '#10b981',
  bad:     '#ef4444',
  neutral: '#94a3b8',
};

// === Recharts shared style constants ===
export const RECHARTS_THEME = {
  tooltipContentStyle: {
    background: 'rgba(15, 19, 28, 0.96)',
    border: '1px solid rgba(255, 255, 255, 0.08)',
    borderRadius: 8,
    padding: '8px 12px',
    boxShadow: '0 8px 24px rgba(0, 0, 0, 0.4)',
  },
  tooltipLabelStyle: {
    color: SITE_PALETTE.fg,
    fontWeight: 600,
    fontSize: 12,
  },
  tooltipItemStyle: {
    color: SITE_PALETTE.fg,
    fontSize: 11,
  },
  gridStroke: 'rgba(255, 255, 255, 0.06)',
  gridStrokeDasharray: '3 3',
  axisStroke: 'rgba(148, 163, 184, 0.3)',
  axisTickColor: SITE_PALETTE.fgMuted,
  axisTickFontSize: 11,
  axisLabelColor: SITE_PALETTE.fgMuted,
  axisLabelFontSize: 12,
  referenceLineStroke: SITE_PALETTE.fgMuted,
  referenceLineStrokeDasharray: '4 4',
};
```

### A.5 — Color → semantic role mapping

#### Models (Recharts pastel set, dark-bg-tuned)

| Model | Hex | Tailwind |
|---|---|---|
| `claude` | `#5eead4` | teal-300 |
| `chatgpt` | `#86efac` | green-300 |
| `gemini` | `#fda4af` | rose-300 |
| `deepseek` | `#93c5fd` | blue-300 |
| `mistral` | `#c4b5fd` | violet-300 |

`NeuralNetwork.jsx` defines a *parallel* model-color set (interactive hub):
`claude #00CED1`, `gemini #FF6B6B`, `chatgpt #7FFFD4`, `deepseek #4A90D9`,
`mistral #A78BFA`. Used only in the canvas hub; everywhere else the
sitePalette set is canon.

#### NMACR dimension colors — three coexisting sets

(1) `MethodologyPanels.jsx:13-19` — `DIM_COLORS` (used in tooltips):

| Dim | Hex |
|---|---|
| N (numeric) | `#5eead4` |
| M (method) | `#7FFFD4` |
| A (assumption) | `#fbbf24` |
| C (calibration) | `#93c5fd` |
| R (reasoning) | `#a78bfa` |

(2) `App.jsx:1082-1088` — `NMACR_BARS` (pipeline weight visual):

| Dim | Hex |
|---|---|
| A (Assumption) | `#00FFE0` |
| R (Reasoning) | `#A78BFA` |
| M (Method) | `#00B4D8` |
| C (Calibration) | `#7FFFD4` |
| N (Numerical) | `#FFB347` |

(3) `pages/Methodology.jsx:107-113` — `SCORE_DIMS`:

| Dim | Hex |
|---|---|
| A | `#7FFFD4` |
| R | `#A78BFA` |
| M | `#00B4D8` |
| C | `#4A90D9` |
| N | `#00FFE0` |

The three sets do not agree. Tooltip context disambiguates.

#### Failure-bucket colors

(1) `sitePalette.js:34-39` `BUCKET_COLORS` (canonical):

| Bucket | Hex |
|---|---|
| Assumption Violation | `#fbbf24` |
| Mathematical Error | `#f87171` |
| Formatting Failure | `#94a3b8` |
| Conceptual Error | `#a78bfa` |

(2) `App.jsx:1163-1168` failure-mix segs (pipeline visual):
A `#00FFE0` / M `#FFB347` / F `#A78BFA` / C `#FF6B6B`.

#### Calibration-confidence buckets — set in print theme only (no website set).

#### Tier colors (`App.jsx:1090-1095`)

| Tier | n | % | Hex |
|---|---|---|---|
| T1 BASIC | 9 | 5% | `#5EEAD4` |
| T2 INTERMEDIATE | 58 | 34% | `#22D3EE` |
| T3 ADVANCED | 84 | 49% | `#3B82F6` |
| T4 EXPERT | 20 | 12% | `#A855F7` |

#### Perturbation-type colors (`App.css:1293-1295`)

| Type | Hex |
|---|---|
| rephrase | `#5eead4` |
| numerical | `#a78bfa` |
| semantic | `#f87171` |

#### Tone colors (`App.css:1512-1514`, `1680-1682`)

| Tone | Hex |
|---|---|
| `tone-negative` | `#FF6B6B` |
| `tone-positive` | `#7FFFD4` |
| `tone-neutral` | `rgba(232, 244, 248, 0.55)` |
| `rank-shift.rise` | `#34d399` |
| `rank-shift.fall` | `#f87171` |
| `rank-shift.stable` | `rgba(232, 244, 248, 0.35)` |

---

## SECTION B — TYPOGRAPHY SYSTEM

Two families: Space Grotesk (body), Space Mono (mono). Weights loaded:
300/400/500/600/700 (Grotesk), 400/700 (Mono, plus italic). Weight 800 used
inline though only 700 is loaded — browser synthesizes. No formal type
scale: sizes set per-element in px / clamp().

### B.1 — Roles

| Role | Family | Size (px) | Weight | line-height | letter-spacing | transform | Color | Source |
|---|---|---|---|---|---|---|---|---|
| Hero h1 | Space Grotesk | `clamp(32px, 5.5vw, 66px)` | 700 | 1.15 | — | none | `--text-primary` (`#E8F4F8`) | `App.jsx:1001` |
| Section h2 | Space Grotesk | `clamp(28px, 3.5vw, 42px)` | 700 | 1.2 | — | none | `#fff` | `pages/*.jsx` |
| Hero watermark | Space Grotesk | `20vw` | 800 | — | -0.02em | none | `rgba(0, 206, 209, 0.025)` | `App.css:343` |
| Nav-logo title | Space Grotesk | 14 | 700 | — | 0.05em | none | `--aqua` | `App.css:182-186` |
| Nav-logo "BB" mark | Space Mono | 14 | 900 | — | -0.04em | none | `#00FFE0` (text-shadow `0 0 12px rgba(0,255,224,0.8)`) | `Navbar.jsx:78` |
| Nav-button | Space Grotesk | 13 | 500 | — | — | none | `--text-secondary` | `App.css:201` |
| Nav-button active | Space Grotesk | 13 | 500 | — | — | none | `--aqua` | `App.css:207` |
| Section eyebrow ("// MARKER") | Space Grotesk | 10 | 700 | — | 0.20em | none | `rgba(0,255,224,0.55)` (or `rgba(255,184,71,0.65)` on Limitations) | `Methodology.jsx:227`, `Limitations.jsx:111`, `References.jsx:143` |
| Subhead "1 · Continuity Statement" | Space Grotesk | 11 | 700 | — | 0.18em | uppercase | `#00FFE0` | `Methodology.jsx:154` |
| Panel eyebrow (canonical) | Space Mono | 11 | 700–800 | — | 0.16em | uppercase | `var(--aqua)` (`#00FFE0`), or panel-specific accent | `MethodologyPanels.jsx:34-37`, `validation-label`, `tolerance-column-header`, `calibration-column-header`, `band-label` |
| Panel eyebrow alternate | Space Mono | 11–12 | 700 | — | 0.14em | uppercase | `#7FFFD4` (alpha-explainer-title), `#5eead4` (perturbation-explainer-title) | `App.css:854,1267` |
| Panel subtitle / italic-muted | Space Grotesk italic | 12–13 | 400 | 1.45–1.65 | — | — | `rgba(232,244,248,0.55)` or `0.65` | `MethodologyPanels.jsx:39`, `App.css:864,1276` |
| Validation meta | Space Mono italic | 10 | 400 | — | — | — | `rgba(232,244,248,0.5)` | `App.css:1429-1434` |
| Body | Space Grotesk | 13–14 | 400 | 1.7–1.85 | — | — | `--text-primary` | `pages/*.jsx` body paragraphs |
| Body-emphasis | Space Grotesk | 13–14 | 700 | 1.7–1.85 | — | — | `#fff` | inline `<strong>` |
| Card body | Space Grotesk | 12–13 | 400 | 1.55–1.65 | — | — | `rgba(232,244,248,0.7)` | `failure-mode-summary`, `pert-description`, etc. |
| Card label | Space Grotesk | 13 | 700 | 1.35 | — | — | `rgba(232,244,248,0.9)` | `KeyFindings.jsx:134` |
| Card hero number (KeyFinding "big") | Space Mono | 26 (38 hero) | 800 | 1.05 | — | — | model/dim color | `KeyFindings.jsx:128` |
| Failure-mode-count | Space Mono | 22 | 700 | — | — | — | `#fff` | `App.css:1175-1178` |
| Judge-hero-stat-number | Space Mono | 36 | 800 | 1 | — | — | `#7FFFD4` | `App.css:822-828` |
| Alpha-formula | Times New Roman serif | 22 | 400 | — | — | — | `#fff` | `App.css:876-881` |
| Alpha-formula-symbol α | Times New Roman serif italic | 26 | 700 | — | — | — | `#7FFFD4` | `App.css:882-887` |
| Mono-tag chip | Space Mono | 10.5 | 400 | — | — | none | `rgba(232,244,248,0.85)` on `rgba(0,0,0,0.3)` | `App.css:1465-1473` |
| Pert-label | Space Mono | 11 | 700 | — | 0.10em | none | `--text-primary` | `App.css:1304-1310` |
| Pert-tag (BEFORE/AFTER) | Space Mono | 9 | 700 | — | 0.05em | none | `rgba(232,244,248,0.5)` (BEFORE) / `#5eead4` (AFTER) | `App.css:1334-1347` |
| Pert-rate | Space Mono | 18 | 700 | — | — | — | model-specific | `App.css:1366-1373` |
| Recharts axis tick | Space Mono | 9–11 | 400 | — | — | — | `--fgMuted` (`#94a3b8`) | inline `tickFontSize`, `fontFamily: 'monospace'` |
| Recharts label list | Space Mono | 11 | 600–700 | — | — | — | `SITE_PALETTE.fg` (`#e2e8f0`) | `LabelList style` |
| Tooltip body | Space Mono | 11–12 | 400 | 1.55 | — | — | `SITE_PALETTE.fg` | `RECHARTS_THEME.tooltipItemStyle` |
| Tooltip label | Space Grotesk | 12 | 600 | — | — | — | `SITE_PALETTE.fg` | `RECHARTS_THEME.tooltipLabelStyle` |
| KeyFinding "Why it matters" eyebrow | Space Mono | 9 | 700 | — | 0.08em | uppercase | per-card color | `KeyFindings.jsx:151` |
| KeyFinding "why" body | Space Grotesk italic | 11 | 400 | 1.55 | — | — | `rgba(232,244,248,0.55)` | `KeyFindings.jsx:148` |
| Footer link | Space Grotesk | 11 | 600 | — | 0.08em | uppercase | `rgba(0,255,224,0.5)` → hover `#00FFE0` | `App.jsx:2495` |
| Footer body | Space Grotesk | 13 | 400 | 1.9 | — | — | `rgba(255,255,255,0.45)` | `App.jsx:2503` |
| BTN primary | Space Grotesk | 14 | 700 | — | 0.05em | none | `--bg-primary` on aqua→blue-deep gradient | `App.css:294-305` |
| BTN secondary | Space Grotesk | 14 | 700 | — | 0.05em | none | `--aqua` on transparent | `App.css:307-317` |

### B.2 — Letter-spacing buckets (the "small-caps eyebrow" axis)

| Tracking | Where |
|---|---|
| 0.02–0.05em | inline mono-tag, breakdown labels |
| 0.06–0.08em | failure-mode-tag, eligibility-combined |
| 0.10–0.12em | most "small-caps" eyebrows (live-results, RQ labels), pert-label |
| **0.14–0.16em** | dominant section-eyebrow tracking (`PanelShell` accent label, `validation-label`, `alpha-explainer-title`, `calibration-column-header`, `tolerance-column-header`) |
| 0.18em | `.calibration-headline` (max stretch) |
| 0.20em | `.sidenav-drawer__title`, section eyebrows ("// MARKER") |

The 0.14–0.16em + Space Mono + 700/800 weight + 11px + uppercase + accent
color combination is the **strongest typographic motif on the site**.

---

## SECTION C — PANELSHELL CONVENTION

Defined in `MethodologyPanels.jsx:24-57`. Wraps every Recharts panel.

### C.1 — JSX (verbatim)

```jsx
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
```

### C.2 — Specs

- Outer border: `1px solid rgba(0, 255, 224, 0.18)` (aqua at 18% α). No
  hover treatment on the shell itself; `ExpandablePanel` adds
  `transform: translateY(-2px)` + `box-shadow: 0 8px 24px rgba(0,0,0,0.3)`
  when the shell is expandable.
- Background fill: `rgba(255, 255, 255, 0.025)` (white at 2.5% α).
  Translucent over the dark page bg — looks like glass.
- Border-radius: `14px` (panel-shell) or `8px` (`kj-chart-panel`,
  sub-panels).
- Inner padding: `20px 22px` (canonical) / `22px 24px`
  (`.validation-panel`) / `12px 12px 6px` (`kj-chart-panel`).
- Margin-bottom: `20px` between stacked PanelShells.

#### Eyebrow (mandatory)

- Font: Space Mono (`var(--font-mono)`)
- Size: 11 px
- Weight: 800
- Tracking: 0.16em
- Transform: uppercase
- Color: `accent` prop (defaults `#00FFE0`)
- Margin-bottom: 4 px

Accent values seen:
- `#00FFE0` — default
- `#00B4D8` — `PerModelPassFlipPanel`, `KeywordDegradationPanel`
- `#7FFFD4` — `PerDimRobustnessPanel`, alpha-explainer-title
- `#A78BFA` — `PerDimCalibrationPanel`, `AccCalibScatterPanel`

#### Subtitle (optional)

- Font: Space Grotesk
- Size: 12 px
- Color: `rgba(232,244,248,0.55)`
- Sits directly below eyebrow.

#### Children

The chart sits between the header block and the caption. No internal
divider rule between header and chart. Heights set per-panel:
- Recharts BarChart: 240–280 px
- ScatterChart: 240–300 px
- Stacked-tolerance horizontal: 150 px each, 3 stacked.

#### Caption

- Font: Space Grotesk
- Size: 12 px
- Color: `rgba(232, 244, 248, 0.75)`
- Line-height: 1.7
- Margin: `14px 0 0`
- Used for: methodological context, finding interpretation. Single
  paragraph.

#### SubCaption

- Font: Space Grotesk (italics not enforced — but most use case is
  italic text)
- Size: 11 px
- Color: `rgba(232, 244, 248, 0.5)`
- Line-height: 1.65
- Margin: `6px 0 0`
- Used for: cohort-size disclosure, scope note.

### C.3 — `validation-panel` variant (`App.css:1401-1434`)

```css
.validation-panel {
  margin: 0 0 20px;
  padding: 22px 24px;
  background: rgba(255, 255, 255, 0.025);
  border: 1px solid rgba(0, 255, 224, 0.18);
  border-radius: 14px;
}
.validation-panel-header {
  display: flex; justify-content: space-between; align-items: baseline;
  margin-bottom: 14px; padding-bottom: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  flex-wrap: wrap; gap: 8px;
}
.validation-label {
  font-family: var(--font-mono);
  font-size: 11px; letter-spacing: 0.16em;
  color: var(--aqua); font-weight: 700;
  text-transform: uppercase;
}
.validation-meta {
  font-family: var(--font-mono);
  font-size: 10px; color: rgba(232, 244, 248, 0.5);
  font-style: italic;
}
```

A `border-bottom: 1px solid rgba(255,255,255,0.06)` separates header from
content (the only horizontal rule inside the panel chrome). Footer also
has matching `border-top: 1px solid rgba(255,255,255,0.06)` and is right-
aligned italic mono `rgba(232,244,248,0.5)` 10.5 px.

### C.4 — Per-model card variant (`App.css:1140-1148`)

```css
.failure-mode-card {
  background: rgba(255, 255, 255, 0.025);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-top: 3px solid;        /* color set inline per-model */
  border-radius: 8px;
  padding: 14px 16px;
  display: flex; flex-direction: column; gap: 10px;
}
```

Pattern reused by `pert-card` and KeyFinding cards: 3 px colored top stripe
+ neutral side/bottom borders. Color identifies model or category.

---

## SECTION D — INFOGRAPHIC INVENTORY

### D.1 — `ThreeRankingsComparison.jsx`

What: 3 side-by-side horizontal Recharts BarCharts (accuracy, robustness Δ,
calibration ECE), one row per model, value at right. `lowerIsBetter` flag
flips the caption. Every panel uses model brand color for bars.

Static fallback (post Phase 1.8, 2026-05-04):

```javascript
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
```

Encoding rules:
- Y axis = model (categorical, Space Mono 11px)
- X axis = numeric value, `tickFormatter={v => v.toFixed(3)}`, domain
  `[0, 'dataMax']`
- Bar fill = `MODEL_COLORS[entry.model]` (sitePalette pastel)
- LabelList at `position="right"`, Space Mono 11 px, `SITE_PALETTE.fg`
- Headline above the row: `"Three rankings · the same data tells three
  stories"` in `var(--aqua)` 12 px 700 tracking 0.14em uppercase
- Three accent colors per panel: Accuracy `ACCENTS.teal` (`#5eead4`),
  Robustness `ACCENTS.gold` (`#fbbf24`), Calibration `ACCENTS.purple`
  (`#a78bfa`).

Live data fetched from `${API}/api/v2/rankings` with the static fallback
above as initial state. Lower-is-better sorts ascending; higher-is-better
sorts descending.

Representative excerpt (`ThreeRankingsComparison.jsx:38-90`):

```javascript
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
      <div style={{ color: SITE_PALETTE.fgMuted, fontSize: 11, marginBottom: 10 }}>
        {lowerIsBetter ? 'Lower is better' : 'Higher is better'} · ranked 1→5
      </div>
      <BarChart data={items} layout="vertical" ...>
        <Bar dataKey="value" radius={[0, 4, 4, 0]}>
          {items.map((entry) => (
            <Cell key={entry.model} fill={MODEL_COLORS[entry.model]} />
          ))}
          <LabelList dataKey="value" position="right" formatter={valueFmt}
            style={{ fill: SITE_PALETTE.fg, fontSize: 11, fontFamily: 'monospace' }} />
        </Bar>
      </BarChart>
    </div>
  )
}
```

### D.2 — `KeyFindings.jsx`

What: 3+3 grid (`.kf-card-row-3`) of finding cards. Each card: big mono
number + label + description + italic "Why it matters" eyebrow. Card 0 is
hero (38 px number).

Card-color cycle (`COLORS = ['#00FFE0','#7FFFD4','#A78BFA','#FFB347','#00B4D8','#4A90D9']`)
— position-based, not data-based.

3 px colored top border, neutral side/bottom border, fill `${color}08`.

See Section F for full verbatim text.

### D.3 — `MethodologyPanels.jsx` — every panel

#### D.3.1 `PerModelPassFlipPanel`

What: 5 vertical bars, one per model, height = % keyword-judge disagreement
(combined cohort). Gold dashed reference line at cohort average.

Static fallback:

```javascript
const STATIC_PASSFLIP = {
  combined: {
    pct_pass_flip: 0.2074,
    n_eligible: 2850,
    n_pass_flip: 591,
    per_model: {
      claude:   { n_total: 644, n_eligible: 570, n_pass_flip: 149, pct: 0.2614 },
      chatgpt:  { n_total: 644, n_eligible: 570, n_pass_flip: 103, pct: 0.1807 },
      gemini:   { n_total: 644, n_eligible: 570, n_pass_flip: 130, pct: 0.2281 },
      deepseek: { n_total: 644, n_eligible: 570, n_pass_flip: 100, pct: 0.1754 },
      mistral:  { n_total: 644, n_eligible: 570, n_pass_flip: 109, pct: 0.1912 },
    },
  },
}
```

Visual encoding: Y `[0, 35]%`, gold dashed `ReferenceLine y={avgPct}`,
`label position: 'right'` reads `avg 20.74%`. Bars `MODEL_COLORS[model]`,
radius `[4,4,0,0]`. Accent eyebrow `#00B4D8`.

#### D.3.2 `KeywordDegradationPanel` + `KJBar`

What: 3 side-by-side panels (Base / Perturbation / Combined) each showing
the same per-model passflip % with a per-cohort reference line. 3-col grid
(`.kj-charts-grid`).

Static fallback:

```javascript
const STATIC_KJ_CHARTS = {
  base: {
    n_eligible: 750, pct_pass_flip: 0.2093,
    per_model: {
      claude:   { n_pass_flip: 39, n_eligible: 150, pct: 0.26 },
      chatgpt:  { n_pass_flip: 27, n_eligible: 150, pct: 0.18 },
      gemini:   { n_pass_flip: 34, n_eligible: 150, pct: 0.2266 },
      deepseek: { n_pass_flip: 27, n_eligible: 150, pct: 0.18 },
      mistral:  { n_pass_flip: 30, n_eligible: 150, pct: 0.20 },
    },
  },
  perturbation: {
    n_eligible: 2100, pct_pass_flip: 0.2066,
    per_model: {
      claude:   { n_pass_flip: 110, n_eligible: 420, pct: 0.2619 },
      chatgpt:  { n_pass_flip: 76,  n_eligible: 420, pct: 0.1809 },
      gemini:   { n_pass_flip: 96,  n_eligible: 420, pct: 0.2285 },
      deepseek: { n_pass_flip: 73,  n_eligible: 420, pct: 0.1738 },
      mistral:  { n_pass_flip: 79,  n_eligible: 420, pct: 0.1880 },
    },
  },
  combined: { /* matches PerModelPassFlipPanel above */ },
}
```

Each `KJBar` has Y `[0, 35]%`, per-cohort gold dashed reference at
`overallPct`. Panel title block: `Base / Perturbation / Combined` in
`#fff` 13 px 700, with `n_eligible` chip in mono 11 px
`rgba(232,244,248,0.5)`.

#### D.3.3 `PerModelFailuresPanel`

What: 5 cards (3+2 grid), one per model. Each card has 3 px colored top
border (`MODEL_COLORS[model]`), model name in matching color, dominant-
mode tag mono right, big count `dominant / total`, and a 4-row breakdown
with bars opacity-tinted from card color.

Static fallback:

```javascript
const STATIC_FAILURES = {
  by_model_l1: {
    chatgpt:  { ASSUMPTION_VIOLATION: 25, MATHEMATICAL_ERROR: 4,  FORMATTING_FAILURE: 6, CONCEPTUAL_ERROR: 3 },
    claude:   { MATHEMATICAL_ERROR: 10, ASSUMPTION_VIOLATION: 9 },
    gemini:   { ASSUMPTION_VIOLATION: 10, MATHEMATICAL_ERROR: 9, CONCEPTUAL_ERROR: 4, FORMATTING_FAILURE: 1 },
    deepseek: { ASSUMPTION_VIOLATION: 15, MATHEMATICAL_ERROR: 13, FORMATTING_FAILURE: 6, CONCEPTUAL_ERROR: 2 },
    mistral:  { MATHEMATICAL_ERROR: 12, ASSUMPTION_VIOLATION: 8, FORMATTING_FAILURE: 5, CONCEPTUAL_ERROR: 1 },
  },
}

const FAILURE_SUMMARY = {
  chatgpt:  { mode: 'Assumption-dominated', summary: 'Tends to skip required assumption checks.' },
  claude:   { mode: 'Math-dominated',       summary: 'Computational errors dominate.' },
  gemini:   { mode: 'Balanced split',       summary: 'No single dominant failure mode.' },
  deepseek: { mode: 'Mixed (A + math)',     summary: 'Both A and math contribute substantially.' },
  mistral:  { mode: 'Math-dominated',       summary: 'Math errors are primary failure mode.' },
}
```

Hallucination L1 bucket present in code, NOT populated (0/143). Site
explicitly comments: `// 4 populated L1 buckets (HALLUCINATION = 0/143;
see Limitations L1).`

#### D.3.4 `PerDimRobustnessPanel`

What: grouped vertical BarChart, dim on X (N/M/A/C/R), 5 bars per dim
(one per model). Plain `fgMuted` zero ref line.

Static fallback:

```javascript
const STATIC_PER_DIM_DELTA = {
  claude:   { N: 0.0101,  M: 0.0163,  A: 0.0754,  C: 0.0057,  R: 0.0110 },
  chatgpt:  { N: -0.0168, M: 0.0088,  A: -0.0013, C: -0.0050, R: 0.0053 },
  gemini:   { N: -0.0101, M: 0.0126,  A: 0.0402,  C: -0.0126, R: 0.0047 },
  deepseek: { N: -0.0341, M: 0.0075,  A: 0.1281,  C: -0.0227, R: 0.0226 },
  mistral:  { N: 0.0312,  M: -0.0176, A: 0.0025,  C: 0.0186,  R: -0.0075 },
}
```

#### D.3.5 `PerDimCalibrationPanel`

What: grouped BarChart of ECE per dim per model. Y `[0, 0.22]`, gold
dashed reference at `y=0.10` ("well-calibrated 0.10").

Static fallback:

```javascript
const STATIC_PER_DIM_ECE = {
  N: { claude: 0.1612, chatgpt: 0.1669, gemini: 0.1541, deepseek: 0.1673, mistral: 0.1599 },
  M: { claude: 0.1443, chatgpt: 0.1419, gemini: 0.1484, deepseek: 0.1396, mistral: 0.1435 },
  A: { claude: 0.1657, chatgpt: 0.1654, gemini: 0.1677, deepseek: 0.1685, mistral: 0.1724 },
  C: { claude: 0.0534, chatgpt: 0.0593, gemini: 0.0448, deepseek: 0.0393, mistral: 0.0474 },
  R: { claude: 0.1125, chatgpt: 0.0926, gemini: 0.1292, deepseek: 0.091,  mistral: 0.0999 },
}
```

#### D.3.6 `AccCalibScatterPanel`

What: scatter, X = accuracy `[0.6, 0.8]`, Y = acc-calib Pearson r
`[-0.1, 0.6]`. Gold dashed `r=0` reference line. 5 colored circles +
LabelList model name on top of each marker.

Static fallback:

```javascript
const STATIC_ACC_CALIB = {
  acc_calib_corr: { claude: 0.4164, chatgpt: 0.3632, gemini: 0.3876, deepseek: 0.4204, mistral: 0.4245 },
  accuracy: {
    claude: 0.697605, chatgpt: 0.67326, gemini: 0.73142,
    deepseek: 0.668568, mistral: 0.667635,
  },
}
```

#### D.3.7 `BootstrapValidationPanel` + `ForestChart`

What: 2 side-by-side scatters (accuracy + robustness Δ) each with
`ErrorBar direction="x"` from `[r.mean - r.ci_low, r.ci_high - r.mean]`,
domains `[0.60, 0.78]` (acc) and `[-0.03, 0.07]` (Δ). Robustness panel has
gold ref line at Δ=0 with label `Δ = 0`.

Static fallback:

```javascript
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
```

Footer: `Hochlehnert et al. 2025 · Statistical Fragility framing`.
Captions explicitly call `not_separable` chips for CI-overlap pairs.

#### D.3.8 `AlphaValidationPanel` + `AlphaForestChart`

What: 3-row forest, tone-colored dots — `good` for A, `bad` for R,
`neutral` for M. Gold dashed reference at α=0 with label `α = 0 (chance)`.
Below the chart, a 3-row readout grid:
`label · alpha [ci_low, ci_high] · interpretation`.

Data:

```javascript
const KRIPP_DIMS = [
  { key: 'A', name: 'assumption_compliance', label: 'A · assumption',
    alpha:  0.5730, ci_low:  0.5155, ci_high:  0.6219,
    interp: 'moderate', tone: 'positive' },
  { key: 'R', name: 'reasoning_quality', label: 'R · reasoning',
    alpha: -0.1246, ci_low: -0.1967, ci_high: -0.0589,
    interp: 'CI excludes 0', tone: 'negative' },
  { key: 'M', name: 'method_structure', label: 'M · method',
    alpha: -0.0090, ci_low: -0.0723, ci_high:  0.0617,
    interp: 'CI contains 0', tone: 'neutral' },
]

const ALPHA_TONE_COLOR = {
  positive: SEMANTIC.good,    // #10b981
  negative: SEMANTIC.bad,     // #ef4444
  neutral:  SITE_PALETTE.fgMuted,  // #94a3b8
}
```

Header: `KRIPPENDORFF α · INTER-RATER RELIABILITY` mono 11 px aqua.
Meta right: `Base scope n=750 · B=1,000 · seed=42`.
Footer: `Adopted over Spearman ρ per Yamauchi 2025 · threshold-free framing
(CI-vs-zero does the work)`.

#### D.3.9 `ToleranceValidationPanel`

What: 3 vertically stacked horizontal BarCharts (TIGHT / DEFAULT / LOOSE),
each with the same X domain `[0.40, 0.65]`. Bars sorted by accuracy desc,
LabelList at right showing 3-decimal accuracy.

Tolerance ranks (1 = top accuracy):

```javascript
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
```

Headers: `TIGHT (0.005, 0.025)`, `DEFAULT (0.010, 0.050)`,
`LOOSE (0.020, 0.100)`. Footer: `Gemini swings worst→mid (#5→#3) as
tolerance loosens; DeepSeek slips #3→#5; Claude/ChatGPT stable at top.
Bayesian closed-form numerics are tolerance-sensitive at the boundary, not
numerically fragile within typical bounds.`

#### D.3.10 `CalibrationMethodComparisonPanel`

What: hand-rolled dual-leaderboard (no Recharts). Left = verbalized ECE
ranking, right = self-consistency ECE ranking. Each row: `#rank · model ·
[track-with-dot] · value · rank-shift-arrow`. Arrow `↑` `#34d399`,
`↓` `#f87171`, `→` muted.

```javascript
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

// Track domains for dot positioning
const VERB_MIN = 0,    VERB_MAX = 0.22
const CONS_MIN = 0.55, CONS_MAX = 0.78
```

Headline above row: `SAME MODELS · DIFFERENT METHODS · DIFFERENT
LEADERBOARDS` mono 11 px aqua tracking 0.18em. Each dot:
`box-shadow: 0 0 8px {MODEL_COLOR}88` (halo).

Verbalized column header: `VERBALIZED ECE` aqua. Self-consistency column
header: `SELF-CONSISTENCY ECE` `#FFB347` (amber/orange).

Summary line: `Every model reverses direction between methods. Claude #1 →
#5; Gemini #3 → #1; DeepSeek #5 → #4. Per-task accuracy-calibration
correlations stay tight (Mistral 0.42, DeepSeek 0.42, Claude 0.42, Gemini
0.39, ChatGPT 0.36) — the leaderboard flip is method-driven, not signal-
strength driven.`

#### D.3.11 `EligibilityFunnelPanel`

What: 2 stacked horizontal bars (base + perturbation), each split into
`eligible` (aqua → aqua-light gradient) and `excluded` (FFB347 →
FF8A4D gradient) with inline numerics. Combined readout below.

Hardcoded:

```javascript
const baseTotal = 855, baseElig = 750, baseExcl = 105
const pertTotal = 2365, pertElig = 2100, pertExcl = 265
const combTotal = 3220, combElig = 2850, combPct = 88.5
```

Header: `ELIGIBILITY FILTERS · WHO COUNTS IN α`.
Combined chip: `COMBINED · 2,850 of 3,220 = 88.5% eligible`.
Rationale: `21 distinct task families × 5 models — CONCEPTUAL · MINIMAX ·
BAYES_RISK plus the MARKOV_04 outlier — share empty
required_assumption_checks. Keyword and judge scoring of assumption
articulation cannot be compared on tasks that don't require assumption
articulation.`
Footer: `Self-consistency: 161/171 tasks (10 CONCEPTUAL excluded — no
numeric answer for 3-rerun agreement). Error taxonomy: 143 base failures
classified; FORMATTING_FAILURE (18/143) reported separately.`

### D.4 — `JudgeValidationPanels.jsx`

#### D.4.1 `AgreementMetricsForestPanel`

Duplicate of `AlphaValidationPanel` with class names prefixed
`agreement-metrics-*` (used in VizGallery). Same data, same encoding.
Header: `AGREEMENT METRICS — KEYWORD vs EXTERNAL JUDGE` mono 11 px
`#00B4D8` tracking 0.12em. Meta: `Base scope · n=750 · 3 shared dimensions
· B=1,000 · seed=42`.

#### D.4.2 `JudgeKeywordConfusionMatrix`

What: 2×2 grid. Cells:
- agreement (both pass) — fill `rgba(127,255,212,0.08)`, border
  `rgba(127,255,212,0.25)`
- agreement (both fail) — same as above
- flip (keyword over-credits) — fill `rgba(255,107,107,0.08)`, border
  `rgba(255,107,107,0.28)`
- flip (keyword under-credits) — same red as above

Each cell: count (26 px 800 white), pct (12 px 600 muted), label (9.5 px
italic muted).

```javascript
const CONFUSION = {
  total: 750,
  both_pass: 376,
  keyword_only_pass: 157,
  judge_only_pass: 42,
  both_fail: 175,
}
const COMBINED_FLIP_PCT = 20.74
```

Computed pct: `n/total × 100` to 1 decimal.

Summary: `199 of 750 base runs flip pass/fail (26.5% total disagreement;
20.9% directional pass-flip)` — wait, this is computed live from the data:
`flips = 157 + 42 = 199`, `pct = 199/750 = 26.5%`, directional pct =
`157/750 = 20.9%`.

Footer: `Off-diagonal mass = the disagreement reported in the headline
metrics. Combined denominator (base + perturbation, n=2,850) holds at
20.74% directional pass-flip (591 cases).`

#### D.4.3 `DisagreementByPertTypePanel`

What: hand-rolled horizontal bars (no Recharts). Per-perturbation-type:

```javascript
const PERT_BREAKDOWN = [
  { label: 'REPHRASE',  pct: 21.6, n: 162, total: 750, color: '#5eead4' },
  { label: 'NUMERICAL', pct: 22.7, n: 136, total: 600, color: '#a78bfa' },
  { label: 'SEMANTIC',  pct: 18.1, n: 136, total: 750, color: '#fbbf24' },
]
```

Vertical dashed `combined 20.74%` reference line at
`118px + (100% - 222px) * (20.74/27)`. X scale `[0, 27%]`. Bar height 30
px. Per-type label color matches bar fill (mono 12 px 800 tracking
0.08em). Right column shows `pct` in 14 px 800 white + `n/total` in 10.5
px 0.55-α below.

Summary: `434 of 2,100 perturbation runs flip pass/fail across REPHRASE
/ NUMERICAL / SEMANTIC (combined directional pass-flip rate 20.74% on
n=2,850).`

### D.5 — Pipeline visuals (`App.jsx:1111-1192`)

#### D.5.1 NMACR-weights mini visual

```javascript
const NMACR_BARS = [
  { dim:'A', label:'Assumption',  weight:0.30, color:'#00FFE0' },
  { dim:'R', label:'Reasoning',   weight:0.25, color:'#A78BFA' },
  { dim:'M', label:'Method',      weight:0.20, color:'#00B4D8' },
  { dim:'C', label:'Calibration', weight:0.15, color:'#7FFFD4' },
  { dim:'N', label:'Numerical',   weight:0.10, color:'#FFB347' },
]
```

Title: `Literature-derived dimension weights · sum = 1.0`. Each row =
3-col grid `130px 1fr 50px`: tag + track-with-fill + weight.

#### D.5.2 Tier-mini stack

```javascript
const TIER_BARS = [
  { tier:'T1 BASIC',        n: 9, pct: 5,  color:'#5EEAD4' },
  { tier:'T2 INTERMEDIATE', n:58, pct:34, color:'#22D3EE' },
  { tier:'T3 ADVANCED',     n:84, pct:49, color:'#3B82F6' },
  { tier:'T4 EXPERT',       n:20, pct:12, color:'#A855F7' },
]
```

Title: `171 tasks across 4 difficulty tiers`. Single 32-px-tall stacked
bar; segment width = pct, label inside (mono 9 px) + count (10 px).

#### D.5.3 Perturbation chips

```javascript
const PERT_TYPES = [
  { name:'rephrase',  count:171, color:'#00FFE0', note:'Same problem, reworded' },
  { name:'numerical', count:131, color:'#FFB347', note:'Same structure, new numbers' },
  { name:'semantic',  count:171, color:'#A78BFA', note:'Same math, new domain' },
]
```

Title: `3 perturbation types · 473 total`. 3-col chip grid.

#### D.5.4 Failure-mix per-model

```javascript
const FAILURE_MIX = [
  { model:'ChatGPT',  total:38, A:25, M:4,  F:6, C:3, color:'#7FFFD4' },
  { model:'Claude',   total:19, A:9,  M:10, F:0, C:0, color:'#00CED1' },
  { model:'DeepSeek', total:36, A:15, M:13, F:6, C:2, color:'#4A90D9' },
  { model:'Mistral',  total:26, A:8,  M:12, F:5, C:1, color:'#A78BFA' },
  { model:'Gemini',   total:24, A:10, M:9,  F:1, C:4, color:'#FF6B6B' },
]
```

Title: `Per-model failure-mode mix · 143 total`. Per row: model name
colored, then a single horizontal stacked bar (segments
`A #00FFE0 / M #FFB347 / F #A78BFA / C #FF6B6B`), then total count right.

### D.6 — Methodology page literature comparison table

Defined in `Methodology.jsx:115-130` (`LIT_TABLE`). 9-column table
comparing this work against StatEval, MathEval, ReasonBench, BrittleBench,
Ice-Cream, FermiEval, Nagarkar. Last column = "THIS WORK". Rows:
Domain, # tasks, Ground truth, Format, External judge, Perturbations,
Statistical rigor, NMACR weighting, Calibration, Error taxonomy, Open
data.

Notable values (THIS WORK column):
- `# tasks: 171 (136 P1 + 35 P2)`
- `Ground truth: Closed-form + seeded MC`
- `External judge: ✓ Llama 3.3 70B (Together AI)`
- `Perturbations: ✓ 398 v2 perturbations`
- `Statistical rigor: Bootstrap CI + Krippendorff α`
- `NMACR weighting: literature-derived (A=.30, R=.25, M=.20, C=.15, N=.10)`
- `Error taxonomy: ✓ 4-L1 / 9-L2 hierarchical`

### D.7 — `pages/UserStudy.jsx`, `pages/VizGallery.jsx`

`UserStudy.jsx` — fetches `/api/user-study` to fan out to all 5 models in
parallel with semaphore-limited concurrency on the backend. No new chart
components; renders model response cards with model-color tinted borders
and inline scoring bars.

`VizGallery.jsx` — flat grid (`viz-grid-responsive`,
`auto-fill, minmax(min(340px, 100%), 1fr)`) of static R-pipeline figures
(PNG/SVG). `confusion-matrix-panel` and `agreement-metrics-panel` are
re-used inside `ExpandablePanel` modals.

---

## SECTION E — DECORATIVE MOTIFS

### E.1 — `MobiusStrip.jsx`

What: HTML5 `<canvas>` 2D drawing of a parametrically-rendered Möbius
band, animated rotation. Pure canvas; no Three.js.

Geometry — `mobiusPoint(u, v)` with R=1.1, halfwidth=0.44:

```javascript
function mobiusPoint(u, v) {
  const R=1.1, hw=0.44
  const c2=Math.cos(u/2), s2=Math.sin(u/2), cu=Math.cos(u), su=Math.sin(u)
  return { x:(R+hw*v*c2)*cu, y:(R+hw*v*c2)*su, z:hw*v*s2 }
}
```

Quad mesh: U=90 longitudinal, V=16 lateral. Each quad rotated by axis
`ax = 0.38 + sin(angle*0.28) * 0.12` and `ay = angle * 0.75`. Projection:
perspective with f=5, scale `min(W,H) * 0.24`.

Per-frame: build quad list, sort back-to-front by avgZ, fill each in
`rgba(col,0.07)` and stroke in `rgba(col,0.2)` lineWidth 0.7.

Color palette (interpolated by parameter `u`):
```javascript
const PALETTE = [[0,255,224],[0,180,216],[167,139,250]]
// aqua, blue, purple
```

Animation: `angle += 0.005` per frame (60 fps → ~21 s full cycle). Default
opacity 0.45 on a `position:absolute, inset:0, pointer-events:none`
`<canvas>`.

Where used: hero overlay (currently — Overview section uses
`HeroNetworkBg`, but `MobiusStrip` is the brand-signature motif documented
in vault sessions).

### E.2 — `NeuralNetwork.jsx`

What: HTML5 canvas 2D, single rAF loop. 48 background nodes + 5 model
nodes, edges by proximity at t=0, traveling pulses on edges. Hub-and-
network layout with mouseover tooltip.

Geometry: model nodes at fractional positions
`xFrac = 0.1 + i*0.2`, `yFrac = 0.35 + (i%2===0 ? 0 : 0.20)`. Each model
node has `driftR = 0.025 + i*0.005` and `driftSpeed = 0.0004 + i*0.00008`.

Color palette (model-specific overrides, NOT sitePalette):

```javascript
const MODELS = [
  { id:'claude',   color:'#00CED1' },
  { id:'gemini',   color:'#FF6B6B' },
  { id:'chatgpt',  color:'#7FFFD4' },
  { id:'deepseek', color:'#4A90D9' },
  { id:'mistral',  color:'#A78BFA' },
]
```

Edges: `DIST_THRESH_FRAC = 0.22` of W (aspect-corrected).
Edge alpha: `(1 - dist/maxDist) * 0.12` aqua. Pulse radius 2.5 px,
shadow 6 px.

Animation: continuous, 60 fps. Pulse spawn every 22 frames.

Where used: section "Models" — interactive hub for selecting a model
to inspect.

### E.3 — `GlobeBackground.jsx`

What: HTML5 canvas 2D rotating wireframe sphere with network nodes/edges.
Felt-not-seen background motif. Opacity 0.07 net (canvas at 0.75, draws
at ~0.07 alpha).

Geometry: R=340 px sphere, lat lines every 20°, lon lines every 30°, 32
random network nodes in spherical coords. Edges by great-circle distance
< 0.85 rad. Position: anchored at `cx = W*0.72, cy = H*0.5` (right-shifted).

Animation: `angle += 0.0003` per frame → ~5.8 min full revolution.
Random node "pulse-bright" event every 120 frames.

Colors: all aqua (`#00FFE0`):
- Lat-line stroke: `rgba(0,255,224,0.07)` lw 0.5
- Lon-line stroke: `rgba(0,255,224,0.06)` lw 0.5
- Edges: `rgba(0,255,224,0.09)` lw 0.4
- Nodes: `rgba(0,255,224,fade*0.25*brightMul)`, brightMul up to 4×

Where used: persistent fixed-position background canvas (`position:fixed,
inset:0, zIndex:0, pointer-events:none, opacity:0.75`).

### E.4 — `HeroNetworkBg.jsx`

What: HTML5 canvas 2D, 72 nodes + proximity edges + pulses. Variant of
NeuralNetwork without model identification — pure decoration.

Color palette (3-stop interpolation by node index):

```javascript
const PALETTE = [
  [0, 255, 224],   // aqua
  [0, 180, 216],   // blue
  [167, 139, 250], // purple
]
```

Edges: `THRESH = 0.22`. Edge alpha
`(1 - dist/maxDist) * 0.09` aqua, lw 0.7. Pulses spawn every 18 frames,
speed `0.007 + Math.random() * 0.01`.

Default opacity: 0.55. Where used: Overview hero section overlay
(`<HeroNetworkBg opacity={0.55} />`).

### E.5 — `GlobalCursor.jsx`

What: precision circle reticle replacing system cursor (CSS-driven, see
`index.css:46-79`). 13×13 px aqua-bordered circle, 24×24 on hover.
Disabled under `@media (pointer: coarse)`.

### E.6 — Hero orbs (`App.css:350-378`)

3 absolute-positioned blurred orbs (60 px filter blur), radial gradients
in aqua / blue / aqua-light. Orbiting via `@keyframes orbit` (translateX
220 px on a 360° rotation).

---

## SECTION F — KEYFINDINGS CARDS (verbatim)

`KeyFindings.jsx`. 6 cards. Card 0 is hero (full-row, 38 px number). Cards
cycle through `COLORS = ['#00FFE0','#7FFFD4','#A78BFA','#FFB347','#00B4D8','#4A90D9']`
by index. Each card has 3 px colored top border, neutral side/bottom
borders, fill `${color}08`, `border-radius: 12 px`, padding
`20px 20px 18px`.

### Card structure (per card)

- `big` — Mono number/headline, 26 px (38 px hero), 800, accent color
- `label` — Body label, 13 px (15 px hero), 700, `rgba(232,244,248,0.9)`
- `desc` — Description, 12 px, 400, `rgba(232,244,248,0.78)`,
  line-height 1.6
- `why` — "Why it matters" italic block at card foot, separated by
  `1px solid ${color}22`, 11 px italic `rgba(232,244,248,0.55)`, with
  inline mono uppercase eyebrow `WHY IT MATTERS` 9 px in accent color.

### Card 0 — hero

- big: `1 in 5`
- label: `Simple scoring overlooks bad reasoning`
- desc: `Across 2,850 evaluable runs (750 base + 2,100 perturbations), the
  keyword scorer and LLM judge disagreed on 20.7% (591) of cases — keyword
  said the response passed, judge said it failed. The disagreement holds
  under prompt rewording — a robustness finding for the methodology.`
  (numbers `flipPct`, `flipN`, `flipTotal` filled live from `pf.combined`.)
- why: `Most LLM benchmarks score by keyword-matching alone. Analysis
  across multiple prompt variants shows this approach systematically
  misses bad reasoning at a measurable rate.`
- accent: `#00FFE0` (COLORS[0])

### Card 1

- big: `α = -0.125 to 0.57`
- label: `Two scoring methods give different answers`
- desc: `Krippendorff agreement on assumption articulation is 0.57
  (n=750). On reasoning_quality, the agreement is NEGATIVE (α=−0.125, 95%
  CI [−0.197, −0.059] excludes zero) — the two methods disagree more than
  they would by chance. On method_structure, agreement is essentially
  chance-level (α=−0.009, CI [−0.072, +0.062] contains zero) — the methods
  cannot be claimed to align. The reasoning disagreement is structural,
  not noise.`
- why: `Confirms the 1-in-5 finding above isn't a fluke. The two scoring
  methods genuinely measure different things on reasoning_quality. On
  method_structure they're essentially chance-level — neither aligned nor
  systematically opposed.`
- accent: `#7FFFD4` (COLORS[1])

### Card 2

- big: `Almost half`
- label: `Models skip the reasoning, not the math`
- desc: `Across 143 audited failures, 67 (46.9%) were classified as
  assumption violations — gaps in articulating priors, distributions, or
  independence structure. By contrast, 48 (33.6%) were classified as math
  errors. The primary failure mode is reasoning, not computation.`
- why: `When LLMs fail at Bayesian reasoning, it's usually not because
  they can't compute — it's because they skip the reasoning steps. This is
  the silent failure mode.`
- accent: `#A78BFA` (COLORS[2])

### Card 3

- big: `Gemini #1`
- label: `The 'best' model on accuracy under literature-weighted NMACR`
- desc: `Gemini ranks #1 on accuracy with mean 0.7314 [0.7060, 0.7565]
  under the literature-weighted NMACR scheme (A=30%, R=25%, M=20%, C=15%,
  N=10%). Claude #2 at 0.6976 [0.6694, 0.7249] — a 3.4pp lead. The
  dimensional weighting follows Du 2025, Boye-Moell 2025, and Yamauchi
  2025.`
- why: `Benchmark rankings depend on the choice of dimensional weighting.
  The literature-derived scheme reflects what published research
  identifies as evaluation priorities for LLMs on Bayesian reasoning.`
- accent: `#FFB347` (COLORS[3])

### Card 4

- big: `3 different rankings`
- label: `Accuracy, robustness, calibration disagree`
- desc: `Ranking models on accuracy, robustness, and calibration produces
  three completely different leaderboards. Gemini wins accuracy (0.7314).
  ChatGPT and Mistral are statistically tied at the top of robustness
  (Δ=+0.0003 and +0.0013 respectively — both noise-equivalent, CIs cross
  zero). Claude and ChatGPT essentially tie on calibration (verbalized ECE
  0.033 / 0.034). No single model dominates across all three axes.`
- why: `Single-number leaderboards mislead. The same data tells three
  different stories about which model is 'best.'`
- accent: `#00B4D8` (COLORS[4])

### Card 5

- big: `All overconfident`
- label: `Models think they're right when they're wrong`
- desc: `When a model gives the same answer 3 times in a row (confident
  agreement), it's still wrong about 60-70% of the time on hard tasks.
  Across 161 numerical-answer tasks, ECE scores range from 0.62 to 0.73
  for all 5 models. All five models are severely overconfident under
  self-consistency extraction, despite appearing well-calibrated by
  verbalized measurement (ECE 0.06–0.18). Calibration is method-
  dependent.`
- why: `'Confidence' doesn't mean 'correctness' for current LLMs on
  Bayesian reasoning. Calibration is method-dependent.`
- accent: `#4A90D9` (COLORS[5])

### Static fallback constants (`KeyFindings.jsx:6-27`)

```javascript
const STATIC_FALLBACK = {
  pass_flip_rate: 0.2074,
  pass_flip_n: 591,
  pass_flip_total: 2850,
  krippendorff_alpha_assumption: 0.573,
  krippendorff_alpha_rq: -0.125,
  krippendorff_alpha_method: -0.009,
  krippendorff_alpha_n: 750,
  dominant_failure_pct: 0.469,
  dominant_failure_n: 67,
  dominant_failure_total: 143,
  rankings: {
    accuracy_top: 'gemini',
    accuracy_top_score: 0.7314,
    robustness_top: 'chatgpt',
    calibration_top: 'claude',
  },
  ece_consistency_min: 0.62,
  ece_consistency_max: 0.73,
  ece_consistency_gemini: 0.618,
}
```

---

## SECTION G — CANONICAL NUMERIC FACTS

### G.1 — Perturbations: three distinct numbers

| Number | Meaning | Source |
|---|---|---|
| **473** unique perturbation records | full count of perturbation specs (75 v1 + 398 v2 covering all 171 base task_ids) | `data/synthetic/perturbations_all.json` (live `len()`); pipeline visual title `App.jsx:1146`: `3 perturbation types · 473 total`; CLAUDE.md §"Perturbations" |
| **398** v2 perturbations | the LLM-generated v2 records subset (suffix `_v2`); also legacy figure in `Methodology.jsx:123` literature comparison row | `Methodology.jsx:123`: `'Perturbations:': '✓ 398 v2 perturbations'`; `App.jsx:1147-1153` `count: 171/131/171` (rephrase/numerical/semantic) — sums to 473 |
| **2,365** perturbation runs | 473 × 5 models = 2,365 total perturbation runs scored | `EligibilityFunnelPanel.jsx`: `pertTotal = 2365` |
| **2,100** perturbation eligible | 2,365 − 265 excluded (21 task families × 5 models with empty `required_assumption_checks`) | `EligibilityFunnelPanel.jsx`: `pertElig = 2100` |
| **855** base runs | (171 tasks × 5 models) | `EligibilityFunnelPanel.jsx`: `baseTotal = 855` |
| **750** base eligible | 855 − 105 excluded | `EligibilityFunnelPanel.jsx`: `baseElig = 750` |
| **3,220** combined total | 855 + 2,365 | `EligibilityFunnelPanel.jsx`: `combTotal = 3220` |
| **2,850** combined eligible | 750 + 2,100 = 88.5% of 3,220 | `EligibilityFunnelPanel.jsx`: `combElig = 2850, combPct = 88.5`; `MethodologyPanels.jsx:178`: `combined.n_eligible: 2850`; `KeyFindings.jsx:11`: `pass_flip_total: 2850` |

The pipeline visual `App.jsx:1146` says `3 perturbation types · 473
total` but the chip counts inside it (171 + 131 + 171 = 473) sum to 473
correctly — though the displayed split (`PERT_TYPES count: 171, 131, 171`)
differs from the per-type analysis denominator
(`PERT_BREAKDOWN.total: 750, 600, 750` in
`JudgeValidationPanels.jsx:215-219`). The two are different cuts: one is
unique perturbation specs, the other is per-type runs joined to keyword+
judge scoring eligibility.

### G.2 — NMACR weights

Site displays the **literature-derived** scheme everywhere a user-facing
weight is shown. Equal weights are NEVER displayed on the website.

Locations where literature weights `A=30, R=25, M=20, C=15, N=10` appear:

- `App.jsx:1082-1088` — `NMACR_BARS` pipeline visual (with
  `Literature-derived dimension weights · sum = 1.0` title)
- `Methodology.jsx:107-113` — `SCORE_DIMS` rubric cards
- `Methodology.jsx:123` — literature comparison row last column
- `Methodology.jsx:344-348` — body prose: `NMACR_WEIGHTS = (A=0.30,
  R=0.25, M=0.20, C=0.15, N=0.10)`
- `KeyFindings.jsx` Card 3 desc: `under the literature-weighted NMACR
  scheme (A=30%, R=25%, M=20%, C=15%, N=10%)`
- `MethodologyPanels.jsx:573` `AccCalibScatterPanel` subtitle: `Pearson r
  between per-task aggregate (literature-weighted NMACR) and per-task
  confidence proxy (dim_C)`
- `MethodologyPanels.jsx:738` `BootstrapValidationPanel`: section title
  `Accuracy (literature-weighted NMACR)`

The CLAUDE.md states `WEIGHTS = N=0.20, M=0.20, A=0.20, C=0.20, R=0.20`
(equal) — this is the live runtime scoring weight in
`evaluation/metrics.py` and `llm_runner/response_parser.py`. The
**website's `NMACR_BARS` display + Methodology body ALL render the
literature-derived scheme**, AND `Methodology.jsx:344-348` claims the
runtime parser uses the SAME literature weights as the metrics path.

CONFLICT: CLAUDE.md says equal 0.20×5; the website body and the
literature-comparison table claim runtime uses
A=0.30/R=0.25/M=0.20/C=0.15/N=0.10. Both cannot be true simultaneously —
this is a documented inconsistency.

The accuracy values displayed (Gemini 0.7314 etc.) on the site are
labeled `literature-weighted NMACR` in panel subtitles. Whether the
underlying numbers were computed with equal or literature weights is not
verified inside this scrape; what the website *displays* and *claims* is
the literature scheme.

### G.3 — Per-model headline metrics

#### Accuracy (post Phase 1.8, 2026-05-04)

| # | Model | Mean | 95% CI |
|---|---|---|---|
| 1 | Gemini | 0.7314 | [0.7060, 0.7565] |
| 2 | Claude | 0.6976 | [0.6694, 0.7249] |
| 3 | ChatGPT | 0.6733 | [0.6449, 0.7012] |
| 4 | DeepSeek | 0.6686 | [0.6384, 0.6988] |
| 5 | Mistral | 0.6676 | [0.6401, 0.6949] |

Source: `MethodologyPanels.jsx:634-640` `BOOTSTRAP_ACCURACY` static const
+ `ThreeRankingsComparison.jsx:14`. Backed by
`experiments/results_v2/bootstrap_ci.json` (B=10,000, seed=42).

#### Robustness Δ (base − perturbation; lower is better)

| # | Model | Δ | 95% CI | Notes |
|---|---|---|---|---|
| 1 | ChatGPT | 0.0003 | [-0.0133, 0.0144] | CI crosses 0 — not separable from no-deficit |
| 2 | Mistral | 0.0013 | [-0.0116, 0.0142] | CI crosses 0 |
| 3 | Gemini | 0.0129 | [-0.0026, 0.0288] | CI crosses 0 |
| 4 | Claude | 0.0305 | [0.0163, 0.0445] | separates from 0 |
| 5 | DeepSeek | 0.0388 | [0.0215, 0.0560] | separates from 0 |

Source: `MethodologyPanels.jsx:642-648` `BOOTSTRAP_ROBUSTNESS` +
`ThreeRankingsComparison.jsx:19-25`. Backed by
`experiments/results_v2/robustness_v2.json`.

#### Calibration ECE (verbalized; lower is better)

| # | Model | ECE |
|---|---|---|
| 1 | Claude | 0.0334 |
| 2 | ChatGPT | 0.0339 |
| 3 | Gemini | 0.0765 |
| 4 | Mistral | 0.0811 |
| 5 | DeepSeek | 0.1977 |

Source: `MethodologyPanels.jsx:1007-1013` `CALIB_VERBALIZED`. Backed by
`experiments/results_v2/calibration.json`.

`ThreeRankingsComparison.jsx:26-32` displays values rounded to 3 decimals:
`claude 0.033, chatgpt 0.034, gemini 0.077, mistral 0.081, deepseek 0.198`.

#### Calibration ECE (self-consistency, n=161 numeric tasks; lower is better)

| # | Model | ECE | Rank shift vs verbalized |
|---|---|---|---|
| 1 | Gemini | 0.6178 | ↑ 2 |
| 2 | Mistral | 0.6632 | ↑ 2 |
| 3 | ChatGPT | 0.7214 | ↓ 1 |
| 4 | DeepSeek | 0.7261 | ↑ 1 |
| 5 | Claude | 0.7342 | ↓ 4 |

Source: `MethodologyPanels.jsx:1015-1021` `CALIB_CONSISTENCY`. Backed by
`experiments/results_v2/self_consistency_calibration.json`.

#### Per-model accuracy-calibration Pearson r

| Model | r |
|---|---|
| Mistral | 0.4245 |
| DeepSeek | 0.4204 |
| Claude | 0.4164 |
| Gemini | 0.3876 |
| ChatGPT | 0.3632 |

Source: `MethodologyPanels.jsx:530`.

### G.4 — Keyword-vs-judge disagreement

| Number | Meaning | Source |
|---|---|---|
| **20.74%** combined directional pass-flip | keyword PASS, judge FAIL on assumption_compliance | `MethodologyPanels.jsx:178`, `JudgeValidationPanels.jsx:154`, `Methodology.jsx:375` (hero stat 20.74%), `KeyFindings.jsx:33` |
| **591** flip count (combined) | numerator | same |
| **2,850** eligible (combined) | denominator | same |
| **199** total disagreement (base) | both keyword-only-pass + judge-only-pass | `JudgeValidationPanels.jsx:158`: `keyword_only_pass + judge_only_pass = 157 + 42 = 199` |
| **26.5%** total disagreement rate (base) | 199 / 750 | computed live |
| **20.9%** directional pass-flip (base) | 157 / 750 | computed live |
| **376** both-pass (base) | upper-left of 2×2 | `JudgeValidationPanels.jsx:148` |
| **175** both-fail (base) | lower-right of 2×2 | same |
| **157** keyword-only-pass (base) | upper-right (flip — keyword over-credits) | same |
| **42** judge-only-pass (base) | lower-left (flip — keyword under-credits) | same |

Per-model directional pass-flip (combined):

| Model | n_pass_flip | n_eligible | pct |
|---|---|---|---|
| Claude | 149 | 570 | 26.14% |
| ChatGPT | 103 | 570 | 18.07% |
| Gemini | 130 | 570 | 22.81% |
| DeepSeek | 100 | 570 | 17.54% |
| Mistral | 109 | 570 | 19.12% |

Source: `MethodologyPanels.jsx:179-185`.

Per-perturbation-type rate:

| Type | pct | n | total |
|---|---|---|---|
| REPHRASE | 21.6% | 162 | 750 |
| NUMERICAL | 22.7% | 136 | 600 |
| SEMANTIC | 18.1% | 136 | 750 |

Source: `JudgeValidationPanels.jsx:215-219`.

### G.5 — Krippendorff α per dimension (base scope, n=750)

| Dim | α | 95% CI | Interpretation |
|---|---|---|---|
| A · assumption | +0.5730 | [+0.5155, +0.6219] | moderate (positive) |
| R · reasoning | -0.1246 | [-0.1967, -0.0589] | CI excludes 0 (negative) |
| M · method | -0.0090 | [-0.0723, +0.0617] | CI contains 0 (chance-level) |

Source: `MethodologyPanels.jsx:771-787` `KRIPP_DIMS` +
`JudgeValidationPanels.jsx:8-23`. Backed by
`experiments/results_v2/krippendorff_agreement.json` (B=1,000, seed=42).
KeyFindings card 1 displays α_A as `0.57` (truncated 1-decimal).

### G.6 — Failure taxonomy (L1 buckets, n=143 audited)

| Bucket | n | % | Color |
|---|---|---|---|
| ASSUMPTION_VIOLATION | 67 | 46.9 | `#fbbf24` |
| MATHEMATICAL_ERROR | 48 | 33.6 | `#f87171` |
| FORMATTING_FAILURE | 18 | 12.6 | `#94a3b8` |
| CONCEPTUAL_ERROR | 10 | 7.0 | `#a78bfa` |
| HALLUCINATION | 0 | 0.0 | (n/a; would be `#a78bfa` if present) |

Source: `KeyFindings.jsx:13-15` (`dominant_failure_pct: 0.469,
dominant_failure_n: 67, dominant_failure_total: 143`); `Limitations.jsx:7`
hallucination caveat. L1 totals also reachable via
`experiments/results_v2/error_taxonomy_v2.json`. Per-model L1 breakdown
in `MethodologyPanels.jsx:267-274`.

### G.7 — Assumption-skip rate — multiple framings

The website uses **46.9%** as the canonical "assumption-skip" or
"assumption violation" headline, computed from the audited 143 failures.
The site does NOT display the 51.5% judge-zero-rate framing.

| Number | Definition | Where displayed |
|---|---|---|
| **46.9%** | 67 / 143 audited failures classified as ASSUMPTION_VIOLATION | KeyFindings card 2; Limitations metaphors; Methodology §6 literature convergence: `the 46.9% empirical finding here independently agrees` |
| 51.5% (NOT shown on site) | base-judge zero-rate on assumption_compliance dim, n=1,229 | only in `experiments/results_v2/judge_dimension_means.json` |

### G.8 — Other site-displayed numerics

| Number | Meaning | Source |
|---|---|---|
| 161 / 171 | self-consistency scope | `EligibilityFunnelPanel` footer |
| 10 | CONCEPTUAL tasks excluded from self-consistency | same |
| 21 | task families excluded from α / passflip eligibility | `EligibilityFunnelPanel` rationale |
| 88.5% | combined eligibility | `combPct` |
| 105 | base runs excluded | `baseExcl` |
| 265 | perturbation runs excluded | `pertExcl` |
| 750 | base eligible | shared denominator for confusion matrix + α |
| 6,010 | judge scoring calls (approximate) | `Methodology.jsx:93` `JUDGE_FACTS[0].body` |
| 38 | task families | inferred from `Methodology.jsx:115` literature row + Methodology §1; also called "38 types" in tier breakdown |
| 136 P1 + 35 P2 = 171 tasks | task counts | literature comparison row |
| `B = 10,000` bootstrap resamples for accuracy/robustness | | `BootstrapValidationPanel` |
| `B = 1,000` bootstrap resamples for α | | `AlphaValidationPanel`, `AgreementMetricsForestPanel` |
| `seed = 42` | | both |
| 4-L1 / 9-L2 hierarchical taxonomy | | literature row |
| 0.10 | "well-calibrated" ECE threshold | `PerDimCalibrationPanel` ref line |

### G.9 — Limitations page numerics (`Limitations.jsx`)

L3 "Robustness top-3 not separable":
- ChatGPT Δ = +0.0003 [−0.013, +0.014]
- Mistral Δ = +0.0013 [−0.012, +0.014]
- Gemini Δ = +0.013 [−0.003, +0.029]
- Claude Δ = +0.030
- DeepSeek Δ = +0.039
- Top-2 pair (ChatGPT vs Mistral) is `not_separable`

L4 single-judge: `combined 20.74%` headline, `Llama 3.3 70B Instruct via
Together AI`, `Yamauchi et al. (2025)` cited.

L5 eligibility: `2,850 / 3,220 = 88.5%`, `21 distinct task families`,
`105 excluded base runs`, `2,100 of 2,365 perturbation runs`.

L6 length-correlation: `pooled length–RQ Pearson r = 0.184`,
`within-Gemini length–RQ r = 0.012`, `Gemini averages 2.4× the cohort
response length`, `5/5 substantive hand-spot-checks`,
`uniformly distributed advantage across 34/38 task types`.

### G.10 — Conflicts flagged

1. **NMACR weights**: site displays `A=30, R=25, M=20, C=15, N=10`
   ("literature-derived"); CLAUDE.md says runtime scoring uses equal
   `0.20 × 5`. Methodology page body asserts the runtime parser uses the
   literature scheme — direct contradiction with CLAUDE.md.
2. **Pipeline pert chip counts** show `171 / 131 / 171` (= 473 by
   rephrase/numerical/semantic split) but per-type analysis in
   `JudgeValidationPanels` uses `750 / 600 / 750` denominators which are
   per-type *run counts after eligibility filter* — not unique pert
   counts. Both correct in context but the user-visible "473 total" tile
   sits next to charts that use 750/600/750 — labels must declare scope.
3. **Three NMACR color sets** (Methodology / pipeline / panel-tooltips)
   with no two matching. Tooltip context disambiguates but the print
   theme has to pick one.
4. **Two model-color palettes**: sitePalette pastel `#5eead4` etc. and
   NeuralNetwork's interactive set `#00CED1` etc. Site uses sitePalette
   everywhere except the NeuralNetwork hub.

---

## SECTION H — LAYOUT PATTERNS

### H.1 — Title-block composition (Overview, `App.jsx:993-1014`)

Hero is a centered flex column inside a section with
`min-height: calc(100vh - 200px)`. Title block:

1. h1 `Benchmarking LLMs on Bayesian Statistical Reasoning` —
   `clamp(32px, 5.5vw, 66px)` 700, line-height 1.15. The phrase
   "Bayesian Statistical Reasoning" is rendered in a gradient-text
   treatment: `linear-gradient(135deg, #00FFE0, #00B4D8)` clipped to text
   via `WebkitBackgroundClip: text; WebkitTextFillColor: transparent`.
2. Sub-line block: `American University of Armenia` followed by two
   role/name rows:
   - `Student: Albert Simonyan` → linkedin link, color `--aqua`, weight 700
   - `Supervisor: Dr. Vahe Movsisyan` → linkedin link
   - Sub-line typography: 15 px line-height 2, color `--text-secondary`
3. **Quote box** (Bayes 1763 epigraph) — left-border 3 px aqua, 36×48 px
   padding, glass background (`--bg-card` with backdrop-blur 12 px).
   Quote text is Georgia serif italic 17 px line-height 1.85.
   Attribution: `— Thomas Bayes, 1763 · An Essay Towards Solving a
   Problem in the Doctrine of Chances`. Decorative quote marks are
   serif 88 px 0.18 α aqua, animated `float 4s ease-in-out infinite`.
4. **Hairline divider** — `width: 60%, height: 1px, background:
   linear-gradient(90deg, transparent, var(--aqua), transparent),
   margin: 44px auto 32px, opacity: 0.3`.
5. **CTAs** — 3 buttons: View Results (btn-primary), Explore Tasks
   (btn-secondary), User Study (btn-secondary with violet border tint).

The Overview section also has `<HeroOrbs />` (3 blurred orbs) AND
`<HeroNetworkBg opacity={0.55} />` overlaid as decoration. A
`hero-watermark` sits as the lowest layer (20vw, 0.025 α aqua).

The persistent navbar (`Navbar.jsx`) sits at `position: fixed` 64 px high
with the `BB` logo monogram on the left and 11 nav links on the right;
glassmorphism `backdrop-filter: blur(24px)`, border-bottom
`rgba(0,255,224,0.10)` → `0.18` on scroll.

### H.2 — Section-header treatment (Methodology / Limitations / References)

All non-hero sections use the same composition:

1. Eyebrow line: `// EYEBROW · WORDS` — Space Grotesk 10 px 700
   tracking 0.20em, color `rgba(0,255,224,0.55)` (Methodology, References)
   or `rgba(255,184,71,0.65)` (Limitations).
2. Section h2: `clamp(28px, 3.5vw, 42px)` 700, color `#fff`,
   line-height 1.2.
3. Hairline rule — `width: 64px, height: 3px, background:
   linear-gradient(90deg, #00FFE0, #00B4D8), border-radius: 2px,
   margin-bottom: 36px`. Hard-coded 64 px not full-width — like a section
   underline mark, not a divider.
4. (Optional intro paragraph)
5. (Section content)

Subheads inside sections (`Methodology.jsx:147-168`):
`Subhead` component renders text in `color: #00FFE0, fontSize: 11,
fontWeight: 700, letterSpacing: 0.18em, textTransform: uppercase` with
optional right-aligned mono meta text 10.5 px tracking 0.04em.

Section dividers between sections: `App.css:402-407` — full-width 1 px
`linear-gradient(90deg, transparent 0%, var(--aqua) 50%, transparent
100%)` at 0.18 opacity.

### H.3 — Card-grid spacing & gutters

| Grid | Columns | Gap | Breakpoints |
|---|---|---|---|
| `kf-card-row-3` (Key Findings 3-col) | `repeat(3, 1fr)` | 16 px | → 1 col @ 900 px |
| `kf-card-row-2` | `repeat(2, 1fr)` | 16 px | → 1 col @ 900 px |
| `three-rankings-grid` | `repeat(3, 1fr)` | 20 px | → 1 col @ 900 px |
| `commitments-grid` (Methodology §1) | `repeat(3, 1fr)` | 14 px | 2 @ 900 px, 1 @ 600 px |
| `nmacr-cards-grid` (Methodology §2) | `repeat(3, 1fr)` | 14 px | 2 @ 900 px, 1 @ 600 px |
| `kj-charts-grid` | `repeat(3, 1fr)` | 14 px | 1 col @ 1000 px |
| `failure-modes-grid` | `repeat(3, 1fr)` | 16 px | 2 @ 900 px, 1 @ 600 px |
| `difficulty-cards-grid` | `repeat(4, 1fr)` | 14 px | 2 @ 1100 px, 1 @ 600 px |
| `perturbation-types-grid` | `repeat(3, 1fr)` | 14 px | 1 col @ 900 px |
| `rq-grid` | `repeat(3, 1fr)` | 16 px | 2 @ 900 px, 1 @ 600 px |
| `viz-grid-responsive` | `auto-fill, minmax(min(340px, 100%), 1fr)` | 18 px | — |
| References paper grid | `auto-fit, minmax(280px, 1fr)` | 12 px | — |

Page widths are width-capped at `maxWidth: 1100–1300 px`, centered.
Section vertical padding: `100px 32px 60px` desktop / `56px 20px` mobile.

### H.4 — Figure-caption placement convention

All charts wrapped in `PanelShell` (or `validation-panel`) follow the
same vertical stack:

```
[Eyebrow (mono 11px aqua/accent)]
[Subtitle (Grotesk 12px muted)]      ← optional
[Chart]
[Caption (Grotesk 12px 0.75-α, line-height 1.7)]
[SubCaption (Grotesk 11px 0.5-α, line-height 1.65)]   ← optional
```

For `validation-panel` variant:

```
[Header row: validation-label (left) | validation-meta (right)]
[1px divider rgba(255,255,255,0.06)]
[Chart]
[Readout grid (3-col mono fixed widths)]
[1px divider rgba(255,255,255,0.06)]
[Footer (mono 10.5px italic 0.5-α, right-aligned)]
```

### H.5 — Takeaway / callout-box treatment

Two patterns:

(1) **`.alpha-interpretation`** style (`App.css:1022-1031`):
```css
margin: 20px 0 12px;
padding: 14px 18px;
background: rgba(248, 113, 113, 0.06);   /* color-tinted at 6% α */
border-left: 3px solid #f87171;          /* same color, full saturation */
border-radius: 0 4px 4px 0;              /* no left radius */
font-size: 13px; line-height: 1.65;
color: rgba(232, 244, 248, 0.78);
```

(2) **`Methodology.jsx:185-205` `<Callout>`**:
```jsx
<div style={{
  background: `${color}10`,            // 10/255 = ~6% α
  border: `1px solid ${color}55`,
  borderLeft: `4px solid ${color}`,
  borderRadius: 10,
  padding: '14px 18px',
  margin: '14px 0',
}}>
  <div style={{ color, fontSize: 11, fontWeight: 800,
    letterSpacing: '0.14em', textTransform: 'uppercase',
    marginBottom: 6 }}>
    {title}
  </div>
  <div style={{ color: 'rgba(232,244,248,0.85)', fontSize: 13,
    lineHeight: 1.7 }}>
    {children}
  </div>
</div>
```

(3) **Limitations card** — same structure as (2) but always
`borderLeft: 4px solid #FFB347` (amber/orange) with `L{n}` mono prefix
(amber 14 px 800) before the title.

Convention: **left-border accent + matching color tint at 6–10% α + no
gradient fills**. Color = semantic (red for negative finding, amber for
threshold/warning, accent for neutral note).

### H.6 — Interactive overlays

`ExpandablePanel.jsx` wraps any chart panel to make it click-to-expand
into a modal (`expandable-overlay`, `expandable-modal-content`).
`expandable-modal-content` is `max-width: 1400 px`, `max-height: 90vh`,
`background: rgba(6,12,26,0.98)`, border 1 px aqua at 20% α.

Tooltip portal lives in `components/Tooltip/TooltipPortal.jsx` and is
referenced via `data-hover` attribute mapping defined in `data/TooltipMap.js`.

### H.7 — Responsive breakpoints

`1280` / `1100` / `1000` / `900` / `820` / `700` / `640` / `600` /
`500` / `480` / `380` / `360` px. Most multi-col grids collapse to 1 col
at 900 or 600 px. Navbar collapses to hamburger drawer at 820 px. Pipeline
circle scales down at 900, 600, 360 px.

---

## SECTION I — REFERENCES + ATTRIBUTIONS

### I.1 — References (15 papers; ordered by groups as displayed on site)

Source: `backend/static_data/llm-stats-vault/40-literature/papers/*.md`
frontmatter, plus group classification from `pages/References.jsx:8-29`.

#### Closest Prior Work (2)

- **Lu et al. (2025)** — *StatEval: Benchmarking LLMs on Statistical
  Reasoning*. arXiv 2510.09517.
  Authors: Yuchen Lu, Run Yang, Yichen Zhang, Shuguang Yu, Runpeng Dai,
  Ziwei Wang, Jiayi Xiang, Wenxin E, Siran Gao, Xinyao Ruan, Yirui Huang,
  Chenjing Xi, Haibo Hu, Yueming Fu, Qinglan Yu, Xiaobing Wei, Jiani Gu,
  Rui Sun, Jiaxuan Jia, Fan Zhou.
  Grounding: `Closest prior work — same statistical-reasoning lens,
  multiple-choice format. We extend to Bayesian inference + free-response.`

- **Liu et al. (2025)** — *MathEval: A Comprehensive Benchmark for
  Mathematical Reasoning*. Springer 10.1007/s44366-025-0053-z.
  Authors: Tianqiao Liu, Zui Chen, Zhensheng Fang, Weiqi Luo, Mi Tian,
  Zitao Liu.
  Grounding: `Multi-dimensional rubric baseline. Our N·M·A·C·R extends
  MathEval's separation of numeric vs reasoning.`

#### Methodology Foundations (7)

- **Chen et al. (2022)** — *Program of Thoughts Prompting*. arXiv
  2211.12588 / TMLR 2023.
  Grounding: `Program-of-Thoughts considered and deferred — Bayesian
  closed-form derivations are symbolic, not arithmetic.`

- **Wei et al. (2022)** — *Chain-of-Thought Prompting Elicits Reasoning
  in Large Language Models*. NeurIPS 2022 / arXiv 2201.11903.
  Authors: Jason Wei, Xuezhi Wang, Dale Schuurmans, Maarten Bosma, Brian
  Ichter, Fei Xia, Ed H. Chi, Quoc V. Le, Denny Zhou.
  Grounding: `Zero-shot CoT is the prompting baseline for all benchmark
  runs.`

- **Yamauchi et al. (2025)** — *An Empirical Study of LLM-as-a-Judge: How
  Design Choices Impact Evaluation Reliability*. arXiv 2506.13639.
  Authors: Yusuke Yamauchi, Taro Yano, Masafumi Oyamada (bibtex key
  `park2025judge` is legacy).
  Grounding: `α-over-ρ for inter-rater reliability; judge-design
  sensitivity > judge-model sensitivity. Underpins RQ1.`

- **Longjohn et al. (2025)** — *Bayesian Evaluation of Large Language
  Model Behavior*. arXiv 2511.10661.
  Authors: Rachel Longjohn, Shang Wu, Saatvik Kher, Catarina Belém,
  Padhraic Smyth (UC Irvine).
  Grounding: `Bootstrap-CI motivation. Supports ranking separability
  claims.`

- **Hochlehnert et al. (2025)** — *LLM Reasoning Benchmarks are
  Statistically Fragile*. arXiv 2504.07086.
  Authors: Andreas Hochlehnert, Hardik Bhatnagar, Vishaal Udandarao,
  Samuel Albanie, Ameya Prabhu, Matthias Bethge (Tübingen AI Center /
  Cambridge).
  Grounding: `single-question swaps shift Pass@1 ≥ 3pp; motivates
  bootstrap-CI separability tests.`

- **ReasonBench (Potamitis, Klein, Arora, 2025)** — *Benchmarking the
  (In)Stability of LLM Reasoning*. arXiv 2512.07795.
  Grounding: `Variance-as-first-class evaluation framing — supports the
  three-rankings narrative.`

- **BrittleBench (Romanou et al., 2026)** — *Quantifying LLM Robustness
  via Prompt Sensitivity*. arXiv 2603.13285.
  Authors: Angelika Romanou, Mark Ibrahim, Candace Ross, Chantal Shaib,
  Kerem Oktar, Samuel J. Bell, Anaelia Ovalle, Jesse Dodge, Antoine
  Bosselut, Koustuv Sinha, Adina Williams.
  Grounding: `Perturbation taxonomy (rephrase / numerical / semantic)
  directly adopted.`

#### Failure Modes & Calibration (6)

- **Du et al. (2025)** — *Ice Cream Doesn't Cause Drowning: Benchmarking
  LLMs Against Statistical Pitfalls in Causal Inference*. arXiv
  2505.13770.
  Authors: Jin Du, Li Chen, Xun Xian, An Luo, Fangqiao Tian, Ganghua
  Wang, Charles Doss, Xiaotong Shen, Jie Ding.
  Grounding: `independently reports ~47% assumption-violation on
  causal-inference tasks. Validates RQ3.`

- **Boye & Moell (2025)** — *Large Language Models and Mathematical
  Reasoning Failures*. arXiv 2502.11574.
  Authors: Johan Boye, Birger Moell.
  Grounding: `multi-domain math-reasoning failure catalogue; unwarranted
  assumptions aligns with our REGRESSION drops.`

- **Feuer et al. (2025)** — *When Judgment Becomes Noise: How Design
  Failures in LLM Judge Benchmarks Silently Undermine Validity*. arXiv
  2509.20293.
  Authors: Benjamin Feuer, Chiung-Yi Tseng, Astitwa Sarthak Lathe,
  Oussama Elachqar, John P. Dickerson.
  Grounding: `single-judge benchmarks introduce systematic noise. Cited
  in Limitations.`

- **FermiEval (Epstein et al., 2025)** — *LLMs are Overconfident:
  Evaluating Confidence Interval Calibration with FermiEval*. arXiv
  2510.26995.
  Authors: Elliot L. Epstein, John Winnicki, Thanawat Sornwanee, Rajat
  Dwaraknath.
  Grounding: `Domain shifts confidence behaviour — our Bayesian setting
  hedges where FermiEval overconfidently estimates.`

- **Multi-Answer Confidence (Wang et al., 2026)** — *Evaluating and
  Calibrating LLM Confidence on Questions with Multiple Correct
  Answers*. arXiv 2602.07842.
  Authors: Yuhan Wang, Shiyu Ni, Zhikai Ding, Zihang Zhan, Yuanzi Li,
  Keping Bi.
  Grounding: `Verbalized vs consistency-based confidence dichotomy —
  names the upgrade path for RQ5.`

- **Nagarkar et al. (2026)** — *Can LLM Reasoning Be Trusted in
  Statistical Domains*. arXiv 2601.14479.
  Authors: Crish Nagarkar, Leonid Bogachev, Serge Sharoff.
  Grounding: `reliability + hallucination motivation for any LLM-
  statistics calibration claim. Motivates RQ5.`

### I.2 — Graduate Textbooks (7) — displayed as separate group

| Filename / short cite | Description |
|---|---|
| Bolstad (2007) — *Bayesian Statistics* | `Foundational. Conjugate models, credible intervals, HPD regions. Maps to BETA_BINOM, BINOM_FLAT, HPD.` |
| Bishop (2006) — *Pattern Recognition and Machine Learning* | `Comprehensive. Variational Bayes (Ch.10), Dirichlet-Multinomial (Ch.2). Core for VB and DIRICHLET.` |
| Ghosh, Delampady, Samanta (2006) — *An Introduction to Bayesian Analysis* | `Graduate-level. Jeffreys priors, Fisher information, Rao-Cramér bounds. Primary for JEFFREYS, FISHER_INFO, RC_BOUND.` |
| Hoff (2009) — *A First Course in Bayesian Statistical Methods* | `Open access. Normal-Gamma, posterior predictive checks, Gibbs sampling. Covers NORMAL_GAMMA, PPC, GIBBS.` |
| Carlin & Louis (2008) — *Bayesian Methods for Data Analysis* | `Advanced computation. Gibbs/MH/HMC, Bayesian regression, hierarchical models. Core for Phase 2.` |
| Goldstein & Wooff (2007) — *Bayes Linear Statistics* | `Specialised reference for Bayes linear methodology. Theoretical grounding.` |
| Lee (2012) — *Bayesian Statistics: An Introduction* | `Clear introduction. Inference fundamentals. Key for CI_CREDIBLE and BAYES_FACTOR.` |

### I.3 — Suggested poster footer line (`poster-citations.md`)

> Methodology grounded in [Lu25, ReasonBench, Park25]; perturbations
> follow [BrittleBench]; statistical rigor in [Longjohn25, Fragility25];
> calibration in [FermiEval, Nagarkar26, Multi-Answer26]; limitations
> framed by [Judgment-Noise25]. Bayesian foundations: Bolstad, Bishop,
> Hoff, Carlin & Louis, Lee, Ghosh et al., Goldstein & Wooff.

### I.4 — Author / institution / acknowledgments

From hero (`App.jsx:1009-1014`):

- Institution: **American University of Armenia** (DS 299 Capstone)
- Student: **Albert Simonyan**
  (https://www.linkedin.com/in/albert-simonyan-3b0560311/)
- Supervisor: **Dr. Vahe Movsisyan**
  (https://www.linkedin.com/in/vahemovsisyan/)
- Year: **2026**

From footer (`App.jsx:2503-2508`):

> Albert Simonyan · DS 299 Capstone · American University of Armenia · 2026

No dedicated "Acknowledgments" section is rendered on the website — the
title block + footer carry the full attribution. The Methodology page
cites instructors and reviewers indirectly via the literature comparison
and `JUDGE_FACTS` blocks.

Bayes 1763 epigraph (Overview hero quote box, `App.jsx:1027-1036`):

> "The probability of any event is the ratio between the value at which
> an expectation depending on the happening of the event ought to be
> computed, and the value of the thing expected upon its happening."
>
> — Thomas Bayes, 1763 · *An Essay Towards Solving a Problem in the
> Doctrine of Chances*

---

End of scrape.
