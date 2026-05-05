# Website Design Audit

Read-only inventory of design tokens, components, and patterns the website uses. Source of truth for whether the poster references or deliberately diverges. Stack: Vite + React 19 + Recharts (no Tailwind). Two parallel token systems coexist — `App.css` CSS custom properties (UI shell) and `src/data/sitePalette.js` (chart palette).

Cross-references throughout point at:
- [capstone-website/frontend/src/App.css](../capstone-website/frontend/src/App.css)
- [capstone-website/frontend/src/index.css](../capstone-website/frontend/src/index.css)
- [capstone-website/frontend/src/data/sitePalette.js](../capstone-website/frontend/src/data/sitePalette.js)

---

## 1. Color tokens

### 1.1 Background layers

| Role | Hex | Defined | Used for |
|---|---|---|---|
| Page bg (canonical) | `#0A0F1E` | `--bg-primary` ([App.css:9](../capstone-website/frontend/src/App.css#L9)) | `body`, all section backgrounds |
| Page bg (alternate) | `#0A0E1A` | hardcoded ([index.css:4](../capstone-website/frontend/src/index.css#L4)) | `body` fallback before App.css loads |
| Elevated bg | `#0D1426` | `--bg-secondary` ([App.css:10](../capstone-website/frontend/src/App.css#L10)) | Awaiting-results inner panel, tooltip body candidate |
| Card bg | `rgba(0,255,224,0.04)` | `--bg-card` | All `.card` panels |
| Card hover bg | `rgba(0,255,224,0.09)` | `--bg-card-hover` | `.rq-item:hover` |
| Validation panel bg | `rgba(255,255,255,0.025)` | inline `PANEL_BG` ([MethodologyPanels.jsx:24](../capstone-website/frontend/src/components/MethodologyPanels.jsx#L24)) | All `<PanelShell>` and `.validation-panel` |
| Sub-panel bg | `rgba(0,0,0,0.18)`–`(0,0,0,0.25)` | inline | KJ chart panels, alpha-formula block, calibration columns |
| Recharts tooltip bg | `rgba(15,19,28,0.96)` | `RECHARTS_THEME.tooltipContentStyle` ([sitePalette.js:58](../capstone-website/frontend/src/data/sitePalette.js#L58)) | Every chart tooltip |
| Chart base bg | `#0f1118` | `SITE_PALETTE.bg` ([sitePalette.js:5](../capstone-website/frontend/src/data/sitePalette.js#L5)) | Recharts cell strokes (separator from cell fill) |

Note the two-system seam: `App.css` shell uses `#0A0F1E`, the Recharts palette uses `#0f1118`. Close but not identical.

### 1.2 Foreground / text

| Role | Hex | Token |
|---|---|---|
| Primary text | `#E8F4F8` | `--text-primary` (App.css) |
| Primary text (alt) | `#E0F7FF` | hardcoded body (index.css:5) |
| Chart fg | `#e2e8f0` | `SITE_PALETTE.fg` |
| Secondary text | `#8BAFC0` | `--text-secondary` |
| Chart muted fg | `#94a3b8` | `SITE_PALETTE.fgMuted` (axes, ref lines) |
| Muted text | `#4A6A7A` | `--text-muted` (very dim labels) |
| Subtle / border | `#475569` | `SITE_PALETTE.fgSubtle` |
| Accent / link | `#00FFE0` | `--aqua` |

Body uses inline alpha-tinted whites (`rgba(232,244,248,0.5/0.55/0.65/0.7/0.78/0.85/0.92)`) as the de-facto secondary scale, not a defined token.

### 1.3 Semantic colors

| Role | Canonical hex | Other hexes seen | Source |
|---|---|---|---|
| Good / agreement | `#10b981` | `#5eead4`, `#7FFFD4`, `#34d399` | `SEMANTIC.good` + inline |
| Warning / threshold | `#fbbf24` | `#FFB347` (warning-orange) | `ACCENTS.gold` + inline |
| Bad / disagreement | `#ef4444` | `#f87171`, `#FF6B6B` | `SEMANTIC.bad`, `BUCKET_COLORS["Mathematical Error"]`, `.tone-negative` |
| Info / neutral | `#94a3b8` | — | `SEMANTIC.neutral` |
| Info accent | `#00B4D8` | — | `--blue` (PassFlip, Confusion-matrix panels) |

Inconsistency: same semantic in three+ different hexes per role (coral lives at `#f87171` / `#FF6B6B` / `#dc2626-print`; teal-greens span four shades). Print theme canonicalizes; web is fragmented.

### 1.4 Model brand colors

Source of truth: [sitePalette.js:11-17](../capstone-website/frontend/src/data/sitePalette.js#L11-L17). Mirrored to Python at `scripts/site_palette.py` (per file comment). Used in every Recharts figure and every per-model card border.

| Model | Hex | Tailwind name |
|---|---|---|
| `claude` | `#5eead4` | teal-300 |
| `chatgpt` | `#86efac` | green-300 |
| `gemini` | `#fda4af` | rose-300 |
| `deepseek` | `#93c5fd` | blue-300 |
| `mistral` | `#c4b5fd` | violet-300 |

Pastels tuned for dark bg only; print theme substitutes -600 shades (see §5).

### 1.5 NMACR dimension colors

Source: [MethodologyPanels.jsx:13-19](../capstone-website/frontend/src/components/MethodologyPanels.jsx#L13-L19). Used to color dim labels in chart tooltips and legends.

| Dim | Hex |
|---|---|
| N (numeric) | `#5eead4` (`ACCENTS.teal`) |
| M (method) | `#7FFFD4` |
| A (assumption) | `#fbbf24` (`ACCENTS.gold`) |
| C (calibration) | `#93c5fd` |
| R (reasoning) | `#a78bfa` (`ACCENTS.purple`) |

Note: this collides with model colors — `claude` (`#5eead4`) shares hex with dim N, `deepseek` (`#93c5fd`) shares hex with dim C. Tooltip context disambiguates.

The animated scoring bars in [App.jsx:533-537](../capstone-website/frontend/src/App.jsx#L533-L537) use a *different* per-dim color set (`#00897B`, `#EC4899`, `#A78BFA`, `#F59E0B`, `#00FFE0`) plus *different* weights (A=30, R=25, M=20, C=15, N=10) than the canonical equal-weight scoring (`evaluation/metrics.py`). This is the website's "literature-derived" display, not an authoritative token surface.

### 1.6 Bucket / failure-mode colors

Source: [sitePalette.js:34-39](../capstone-website/frontend/src/data/sitePalette.js#L34-L39).

| Bucket | Hex |
|---|---|
| Assumption Violation | `#fbbf24` |
| Mathematical Error | `#f87171` |
| Formatting Failure | `#94a3b8` |
| Conceptual Error | `#a78bfa` |

### 1.7 Gradients

| Gradient | Definition | Usage |
|---|---|---|
| Aqua → blue → aqua-light | `linear-gradient(90deg, #00FFE0, #00B4D8, #7FFFD4)` | Scroll progress bar ([App.css:147](../capstone-website/frontend/src/App.css#L147)) |
| Aqua → blue | `linear-gradient(90deg, #00FFE0, #00B4D8)` | Nav underline, timeline rail |
| Aqua → blue-deep | `linear-gradient(135deg, #00FFE0, #0047AB)` | `.btn-primary` |
| Eligibility eligible | `linear-gradient(90deg, #00FFE0, #7FFFD4)` | `.eligibility-bar-eligible` |
| Eligibility excluded | `linear-gradient(90deg, #FFB347, #FF8A4D)` | `.eligibility-bar-excluded` |
| Krippendorff α strip (red→neutral→teal) | `linear-gradient(to right, rgba(248,113,113,0.45) 0%, …(0.22) 35%, rgba(255,255,255,0.15) 50%, rgba(127,255,212,0.22) 65%, …(0.45) 100%)` | `.alpha-scale-track` ([App.css:914-922](../capstone-website/frontend/src/App.css#L914-L922)) — **the canonical site analog** of the poster's saturated `#dc2626 → #cbd5e1 → #0d9488` strip |
| Conic — awaiting-border | `conic-gradient(from 0deg at 50% 50%, var(--aqua) 0deg, var(--blue) 90deg, transparent 150deg)` | Spinning border for awaiting-results panel |
| Radial dot grid | `radial-gradient(circle, rgba(0,206,209,0.10) 1px, transparent 1px)` 32px | `body::before` |

### 1.8 Glows / shadows (not technically colors but tied to palette)

| Token | Value |
|---|---|
| `--glow-sm` | `0 0 14px rgba(0,255,224,0.22)` |
| `--glow-md` | `0 0 28px rgba(0,255,224,0.35)` |
| `--glow-lg` | `0 0 56px rgba(0,255,224,0.45)` |
| Tooltip shadow | `0 8px 24px rgba(0,0,0,0.4)` |

All glows are aqua-tinted; no print analog (light-bg posters can't carry CRT glow without becoming muddy).

---

## 2. Typography

### 2.1 Font families

Loaded from Google Fonts ([App.css:5](../capstone-website/frontend/src/App.css#L5)):

```css
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap');
```

| Token | Stack | Role |
|---|---|---|
| `--font-body` | `'Space Grotesk', sans-serif` | Body, headings, UI chrome |
| `--font-mono` | `'Space Mono', monospace` | All-caps section labels, numeric values, axis ticks, tooltips |

`index.css:6` declares `'Inter', system-ui, sans-serif` on `body` as a separate fallback — superseded by `App.css` once mounted, but visible during initial paint. No serif outside one one-off: `.alpha-formula { font-family: 'Times New Roman', serif }` for the Krippendorff α math display ([App.css:877](../capstone-website/frontend/src/App.css#L877)).

### 2.2 Weights actually used

`100`/`200` not loaded. In use across CSS+JSX: `300` (loaded only), `400`, `500`, `600`, `700`, `800`. `800` reserved for: hero watermark, panel-shell uppercase labels, dominant numbers (`.failure-mode-count`, calibration-headline, judge-hero-stat-number), CTA buttons. `700` is the default "emphasized" weight (most labels, navbar logo, `.alpha-formula-symbol`).

### 2.3 Type scale

No abstract scale — sizes set per-element in `px`. Census from CSS + inline JSX:

| Size | Where |
|---|---|
| `9px` | Eligibility-bar excluded label, ci-note, alpha-region-note, micro-stats |
| `10px` / `10.5px` | Mono section eyebrows, `.dim-name`, kj-chart-n, footer text |
| `11px` | Validation labels, axis ticks, readout rows, mono badges |
| `12px` | Panel subtitles, body small, tooltip body |
| `12.5px`–`13px` | Card body copy, summary text, RQ labels |
| `14px` | Default body, navbar logo, button labels |
| `15px`–`17px` | Eyebrow paragraphs, RQ details, modal body |
| `18px` | Pert-rate large numerics |
| `22px`–`26px` | Failure-mode-count, alpha-formula, alpha-formula-symbol |
| `28px`–`36px` | Stat numbers, judge-hero-stat-number |
| `clamp(20px, 7vw, 46px)` | h1 hero (responsive) |
| `clamp(20px, 5vw, 36px)` | h2 |
| `clamp(32px, 4vw, 48px)` | section title (App.jsx:505) |
| `20vw` | `.hero-watermark` (huge faded background text) |

### 2.4 Letter-spacing patterns

The website uses uppercase-mono section eyebrows everywhere, distinguished by tracking:

| Tracking | Where |
|---|---|
| `0.02em`–`0.05em` | Inline tags, mono-tag, breakdown labels |
| `0.06em`–`0.08em` | Failure-mode-tag, eligibility-combined |
| `0.10em`–`0.12em` | Most "small-caps" eyebrows (live-results, key-challenges, RQ labels) |
| `0.14em`–`0.16em` | The dominant section-eyebrow tracking (`PanelShell` accent label, `.validation-label`, `.alpha-explainer-title`, `.calibration-column-header`) |
| `0.18em` | `.calibration-headline` (the most stretched) |

Pattern: small (10–11px) + 700/800 weight + uppercase + letter-spacing 0.14–0.16em + accent color = the canonical "panel eyebrow." This is the strongest typographic motif in the design system.

### 2.5 Line-heights

`1.2` (h1/h2), `1.3`–`1.4` (compact card labels), `1.55`–`1.65` (body small), `1.7`–`1.85` (long-form body / RQ details). No tokens; values inline.

---

## 3. Spacing and layout

### 3.1 Border-radius scale

Token from `App.css:28-31`:

```css
--radius-sm: 8px;
--radius-md: 12px;
--radius-lg: 16px;
--radius-xl: 24px;
```

Used by `.card` (lg), `.btn-primary` / `.btn-secondary` (md), `.rq-item` (sm), `.awaiting-inner` (xl). Inline overrides are common: panels use `14px`, sub-cards `8–10px`, narrow chips `3–4px`, dots `50%`. No abstract spacing scale — values inline.

### 3.2 Common paddings

- Section vertical: `100px 32px 60px` (desktop), `56px 20px` (mobile)
- Card / panel: `20px 22px` (`PanelShell`), `22px 24px` (`.validation-panel`), `24px` (`.card`), `18px 20px` (sub-panels)
- Sub-panel inset: `12–14px`
- Pill: `4px 10px` / `1px 6px` for mono-tags

### 3.3 Borders

`1px solid rgba(0,255,224,0.18)` is the canonical aqua-tinted panel border (`PANEL_BORDER`). `.validation-panel` uses the same. Sub-panels use `1px solid rgba(255,255,255,0.06–0.08)` (neutral). Card/panel hover bumps to `rgba(0,255,224,0.40)` (`--border-hover`).

`failure-mode-card` and `pert-card` use `border-top: 3px solid <color>` as a colored accent strip — this is a recurring per-model / per-category identifier pattern.

### 3.4 Grid system

No formal grid. Pages are width-capped at `maxWidth: 1100–1200px` and centered. Heavy use of CSS Grid (`grid-template-columns`) at the panel level (`repeat(3, 1fr)`, `repeat(4, 1fr)`, etc.) with media-query collapses to `1fr` at 900/700/600/500px breakpoints. Common gaps: `12–22px`.

### 3.5 Section radial backgrounds

Each section gets a subtle off-axis radial gradient overlay ([App.css:320-325](../capstone-website/frontend/src/App.css#L320-L325)) — `rgba(0,206,209,0.05–0.08)` or `rgba(0,191,255,0.05)` ellipses at varying anchor points. This is the website's "atmosphere" effect; no print equivalent attempted (and shouldn't be).

---

## 4. Component inventory

`PanelShell` ([MethodologyPanels.jsx:27-57](../capstone-website/frontend/src/components/MethodologyPanels.jsx#L27-L57)) is the canonical wrapper for every Recharts panel: accent eyebrow + subtitle + chart + caption + sub-caption stacked, `PANEL_BG` / `PANEL_BORDER` / `borderRadius: 14`. The poster's panel chrome mirrors this shape.

| # | Component / file | Data | Visual decisions |
|---|---|---|---|
| 4.1 | `PerModelPassFlipPanel` — [MethodologyPanels.jsx:86-150](../capstone-website/frontend/src/components/MethodologyPanels.jsx#L86-L150) | `${API}/api/v2/pass_flip` + static fallback | Recharts BarChart; 5 bars in `MODEL_COLORS`; gold dashed cohort-average ref line; Y `[0, 35]`% |
| 4.2 | `KeywordDegradationPanel` + `KJBar` — [MethodologyPanels.jsx:189-264](../capstone-website/frontend/src/components/MethodologyPanels.jsx#L189-L264) | same | 3 side-by-side panels (base/pert/combined) in `.kj-charts-grid`; each has its own gold ref line |
| 4.3 | `PerModelFailuresPanel` — [MethodologyPanels.jsx:316-358](../capstone-website/frontend/src/components/MethodologyPanels.jsx#L316-L358) | `${API}/api/v2/error_taxonomy` | 5 cards in `.failure-modes-grid` (3+2 → 2 → 1); `border-top: 3px solid <model_color>`; breakdown bars opacity-tinted from card color |
| 4.4 | `PerDimRobustnessPanel` — [MethodologyPanels.jsx:377-450](../capstone-website/frontend/src/components/MethodologyPanels.jsx#L377-L450) | `${API}/api/v2/robustness` | grouped BarChart; dim on X, 5 model bars per dim; plain `fgMuted` zero ref line |
| 4.5 | `PerDimCalibrationPanel` — [MethodologyPanels.jsx:461-526](../capstone-website/frontend/src/components/MethodologyPanels.jsx#L461-L526) | `${API}/api/v2/calibration` | same shape as 4.4; Y `[0, 0.22]`; gold dashed ref at `y=0.10` ("well-calibrated") |
| 4.6 | `AccCalibScatterPanel` — [MethodologyPanels.jsx:537-620](../capstone-website/frontend/src/components/MethodologyPanels.jsx#L537-L620) | live | ScatterChart; 5 dots in `MODEL_COLORS` stroked `SITE_PALETTE.bg` |
| 4.7 | `BootstrapValidationPanel` + `ForestChart` — [MethodologyPanels.jsx:636-768](../capstone-website/frontend/src/components/MethodologyPanels.jsx#L636-L768) | static | 2 side-by-side scatters w/ `ErrorBar direction="x"`; fixed domains `[0.60, 0.78]` acc, `[-0.03, 0.07]` Δ; `mono-tag` chips for `not_separable` |
| 4.8 | `AlphaValidationPanel` + `AlphaForestChart` — [MethodologyPanels.jsx:771-899](../capstone-website/frontend/src/components/MethodologyPanels.jsx#L771-L899) | static | 3-row forest, tone-colored dots (good/bad/neutral); gold ref at α=0. **No gradient strip on the web** — only the muted-pastel `.alpha-explainer` ([App.css:914-922](../capstone-website/frontend/src/App.css#L914-L922)). Saturated print strip is a deliberate divergence (§5) |
| 4.9 | `AgreementMetricsForestPanel` — [JudgeValidationPanels.jsx:45-143](../capstone-website/frontend/src/components/JudgeValidationPanels.jsx#L45-L143) | static | duplicate of 4.8 with `.agreement-metrics-*` class names |
| 4.10 | `JudgeKeywordConfusionMatrix` — [JudgeValidationPanels.jsx:156-212](../capstone-website/frontend/src/components/JudgeValidationPanels.jsx#L156-L212) | static | 2×2 grid; `.grid-cell.agreement` vs `.grid-cell.flip` carry the divergence color. Web analog of poster `disagreement_matrix.svg` |
| 4.11 | `DisagreementByPertTypePanel` — [JudgeValidationPanels.jsx:214-299](../capstone-website/frontend/src/components/JudgeValidationPanels.jsx#L214-L299) | static | hand-rolled bars (no Recharts); per-type colors `#5eead4`/`#a78bfa`/`#fbbf24`; vertical dashed combined-rate line |
| 4.12 | `ToleranceValidationPanel` + `ToleranceBandPanel` — [MethodologyPanels.jsx:927-1000](../capstone-website/frontend/src/components/MethodologyPanels.jsx#L927-L1000) | static | 3 vertically-stacked horizontal BarCharts; same X `[0.40, 0.65]`; mono `LabelList` at right |
| 4.13 | `CalibrationMethodComparisonPanel` — [MethodologyPanels.jsx:1023-1119](../capstone-website/frontend/src/components/MethodologyPanels.jsx#L1023-L1119) | static | hand-rolled dual-leaderboard; rise/fall arrow column (`#34d399`/`#f87171`); dot `box-shadow: 0 0 8px {color}88` glow halo |
| 4.14 | `EligibilityFunnelPanel` — [MethodologyPanels.jsx:1125-1180](../capstone-website/frontend/src/components/MethodologyPanels.jsx#L1125-L1180) | static | 2 stacked horizontal bars (aqua eligible / amber excluded gradients) |
| 4.15 | `ThreeRankingsComparison` — [components/ThreeRankingsComparison.jsx](../capstone-website/frontend/src/components/ThreeRankingsComparison.jsx) | `${API}/api/v2/rankings` | 3 side-by-side horizontal Recharts bars; `lowerIsBetter` flips caption |

Chrome (non-figure): `Navbar` (glassmorphism `backdrop-filter: blur(24px)`), `SideNav`, `KeyFindings` (3+2 grid `.kf-card-row-*`), `ExpandablePanel` (accordion), decorative hero backdrops (`MobiusStrip`, `NeuralNetwork`, `GlobeBackground`, `HeroNetworkBg`), `GlobalCursor` (hidden on `pointer: coarse`).

There is **no website robustness-heatmap component** — that figure lives only in `poster/scripts/robustness_heatmap_print.py` + the R pipeline. The website renders robustness via the per-dim bar panel (4.4), not a 38×5 heatmap.

---

## 5. Print-theme deltas

Cross-reference with [poster/scripts/print_theme.py](scripts/print_theme.py).

### 5.1 Direct equivalents

| Concept | Web | Print |
|---|---|---|
| Model — claude | `#5eead4` (teal-300) | `#0d9488` (teal-600) |
| Model — chatgpt | `#86efac` (green-300) | `#16a34a` (green-600) |
| Model — gemini | `#fda4af` (rose-300) | `#e11d48` (rose-600) |
| Model — deepseek | `#93c5fd` (blue-300) | `#2563eb` (blue-600) |
| Model — mistral | `#c4b5fd` (violet-300) | `#7c3aed` (violet-600) |
| Accent gold (ref lines) | `#fbbf24` | `#d97706` (amber-600) |
| Accent purple | `#a78bfa` | `#7c3aed` |
| Accent teal | `#5eead4` | `#0d9488` |
| Semantic good | `#10b981` | `#059669` (emerald-600) |
| Semantic bad | `#ef4444` | `#dc2626` (red-600) |
| Semantic neutral | `#94a3b8` | `#64748b` (slate-500) |
| Body text | `#E8F4F8` | `#0f172a` (slate-900) |
| Muted text | `#8BAFC0` | `#475569` (slate-500) |
| Page bg | `#0A0F1E` | `#ffffff` |
| Gridlines | `rgba(255,255,255,0.06)` | `#e2e8f0` (slate-200) |

Pattern: each pastel tailwind-300 model color maps to the matching tailwind-600 — preserves hue identity across light↔dark. Print substitution is **not** a literal inversion; the website pastels would muddy in CMYK.

### 5.2 Substituted with no direct web counterpart

| Concept | Web (closest) | Print |
|---|---|---|
| Krippendorff strip — left anchor | `rgba(248,113,113,0.45)` (web is muted-pastel) | `#dc2626` saturated red-600 |
| Krippendorff strip — mid | `rgba(255,255,255,0.15)` | `#cbd5e1` slate-300 |
| Krippendorff strip — right anchor | `rgba(127,255,212,0.45)` | `#0d9488` saturated teal-600 |
| α-strip dot fill | `#fff` web | `#0f172a` (slate-900) on print — anchors against saturated bg |
| NMACR segment colors (stacked-bar order A,R,M,C,N) | Inline JSX uses six different color sets across components (no canonical) | `#10b981 / #8b5cf6 / #06b6d4 / #3b82f6 / #14b8a6` (canonical print) |
| Calibration bucket — 0.3 / 0.5 / 0.6 | n/a | teal / purple / gold |
| Heatmap colormap | n/a (no web heatmap) | matplotlib `RdBu_r` with `vmin=−0.3 / vmax=+0.3` ([robustness_heatmap_print.py:45](scripts/robustness_heatmap_print.py#L45)) |
| Heatmap white-text threshold | n/a | `|Δ| > 0.18` flips text to `#ffffff` |

### 5.3 Web tokens with no print equivalent (gaps)

These are atmosphere/UI tokens with no print analog defined — and probably shouldn't be replicated, but worth flagging in case future poster figures want them:

- **`--aqua` / `--blue` / `--blue-deep`** UI accent palette. The poster currently uses tailwind-600 model colors as accent stand-ins. No dedicated "brand teal" for non-data UI. Any new chrome (callout boxes, headers, eyebrow color) needs a decision.
- **Glow tokens** (`--glow-sm/md/lg`). Inappropriate on print but the visual effect of "elevated emphasis" needs a print substitute (suggestion: subtle drop-shadow `0 1px 2px rgba(15,23,42,0.08)` matching slate-900 alpha).
- **Conic / radial gradients** (awaiting border, section atmospherics, body dot grid). No print analog. If the poster wants spatial differentiation it should use solid panel fills + subtle borders (`#e2e8f0`) rather than gradients.
- **Dimension colors (NMACR)**. The print theme defines `NMACR_SEGMENT_COLORS` but the web has *three* different per-dim color sets in `MethodologyPanels.jsx`, `App.jsx` AnimatedScoringBars, and `sitePalette.ACCENTS`. Print canonicalizes; web is fragmented. Decision needed: which web set should the print mirror reference if a future figure needs to cite a "matching" web source? (Default: `MethodologyPanels.DIM_COLORS` since that's the one rendered in tooltips.)
- **Bucket colors (4 failure modes)**. `BUCKET_COLORS` is exported from `sitePalette.js` but the print theme only defines a 3-key `BUCKET_COLORS_PRINT` (calibration small-multiples). If the poster ever renders the failure-mode breakdown it needs the four mappings: assumption / mathematical / formatting / conceptual.
- **Validation-panel border** (`rgba(0,255,224,0.18)`). No print equivalent. Suggested: `1px solid #cbd5e1` (slate-300) for visible-on-white panel chrome.

### 5.4 Heatmap-specific contracts (already locked)

From [robustness_heatmap_print.py:45-46](scripts/robustness_heatmap_print.py#L45-L46) and the krippendorff strip script:

- Heatmap diverging colormap: `RdBu_r` with `vmin=-0.3 / vmax=+0.3` — symmetric around zero. Cell-text color flip threshold `|v| > 0.18`.
- Krippendorff strip footer-zone tints (lighter than gradient anchors so dots pop): `#fca5a5` neg, `#cbd5e1` mid, `#5eead4` pos. Zone header colors use the matching -900 shades for high contrast.
- Label-box border on print: `#94a3b8` slate-400.

These have no website counterpart and are poster-canonical.

---

## 6. Recurring patterns worth preserving

Five patterns the website uses with high consistency. The poster keeps them.

### 6.1 Mono small-caps panel eyebrow

The strongest signature of the design system. Pattern: `font-family: var(--font-mono)`, `font-size: 11px`, `font-weight: 700-800`, `letter-spacing: 0.14-0.16em`, `text-transform: uppercase`, accent color (aqua/blue/purple per panel).

Used in `PanelShell` accent label, `.validation-label` ([App.css:1420-1427](../capstone-website/frontend/src/App.css#L1420-L1427)), `.alpha-explainer-title`, `.calibration-column-header`, `.tolerance-column-header`. Poster uses the same construction with print-substituted accent (`#0d9488` or `#0f172a`).

### 6.2 Italic-muted captions

Sub-text under panel headers / charts uniformly use italic + alpha-muted white (8+ `font-style: italic` declarations in App.css). Examples — `.alpha-explainer-subtitle { font-size: 13px; color: rgba(232,244,248,0.65); font-style: italic; }`, `.validation-meta { font-family: var(--font-mono); font-size: 10px; color: rgba(232,244,248,0.5); font-style: italic; }`. Print equivalent: italic + `#475569` slate-500.

### 6.3 Mono numeric values, body-font labels

Numbers (alpha values, ECE, %, n=) render in `Space Mono` for decimal alignment; labels in `Space Grotesk`. See `.dot-row` ([App.css:1630-1638](../capstone-website/frontend/src/App.css#L1630-L1638)). Recharts axis ticks and `LabelList` formatters consistently set `fontFamily: 'monospace'`. Carry into print.

### 6.4 Color-coded card border-top accent

Per-model and per-category cards encode identity as a 3px colored top border, neutral side+bottom borders, model-name in matching color, breakdown bars opacity-tinted from same color. See `.failure-mode-card` ([App.css:1140-1148](../capstone-website/frontend/src/App.css#L1140-L1148)) and `.perturbation-type-card` ([App.css:1283-1295](../capstone-website/frontend/src/App.css#L1283-L1295)). Cleaner than colored full borders; print preserves.

### 6.5 Reference-line dashed gold

Every chart with a meaningful threshold (cohort average, α=0, ECE=0.10, Δ=0) draws `strokeDasharray="3 3"` (or `"4 4"`) in `ACCENTS.gold` (`#fbbf24`) with a small `position: 'top'` label. Six panels use this (PassFlip, KJ-3panel, AlphaForest, KrippValidation, ToleranceBand, CalibrationECE). Print substitutes `ACCENT_GOLD_PRINT = "#d97706"` — semantic ("gold = chance / threshold / cohort-avg") preserved.

---

## Notes on what was checked but not located

- **No tailwind config** — site uses pure CSS custom properties + inline styles. The audit task referenced `tailwind.config.{js,ts}` but the codebase doesn't use Tailwind.
- **No "robustness heatmap" website component** — the figure exists only in `poster/scripts/robustness_heatmap_print.py` and the R pipeline. The website renders robustness as bar panels (§4.5) and the three-rankings horizontal bars.
- **No Next.js / app/ directory** — site is Vite + React Router (`src/pages/*.jsx`). The audit task assumed Next.js.
- **No canonical NMACR weight set on the website**. `App.jsx:533-537` displays "literature-derived" `A=30, R=25, M=20, C=15, N=10`. `evaluation/metrics.py` and `response_parser.py` use equal `0.20` each (per CLAUDE.md). The displayed weights in the bars are illustrative, not the live-scored values.
- **No system-wide opacity token scale** — alpha-tinted whites (`0.4–0.92`) are repeated inline 30+ times without abstraction. Treat the seven distinct values (`0.4, 0.5, 0.55, 0.65, 0.7, 0.78, 0.85, 0.92`) as the de-facto secondary text scale.
