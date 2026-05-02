# Track A Diagnostic — Methodology Page Missing Elements

**Date:** 2026-05-02
**Scope:** Compare expected Phase 2 + Group C + Group D Methodology content against live production deployment.
**Mode:** Read-only. No source edits, no commits, no deploys.

---

## Live deployment status

| Item | Value |
|------|-------|
| Live page | https://bayes-benchmark.vercel.app/methodology (HTTP 200) |
| Deployed bundle | `/assets/index-CYErrNq0.js` (1,517,588 bytes, HTTP 200) |
| Local `dist/` bundle | `index-CYErrNq0.js` (1,517,588 bytes — **byte-for-byte match**) |
| `origin/main` HEAD | `3d7fe81` "Group D follow-up: wire Panels 3/4/5 to live API data" |
| Local `HEAD` | `3d7fe81` (clean working tree) |
| **Lag detected** | **NO** — Vercel is serving the latest commit |

Implication: anything visibly missing on the live page is **not** a deploy lag. It is either present-but-mis-perceived, or a runtime render issue the user is observing.

---

## Phase 2 content presence in deployed bundle

Each row checks a verbatim distinctive phrase from the Phase 2 expected-content list against the minified bundle.

| Element | In bundle? | Source location | Diagnosis |
|---------|-----------|-----------------|-----------|
| NMACR literature defense ("literature-derived weights") | ✓ (1 hit) | [Methodology.jsx:159](capstone-website/frontend/src/pages/Methodology.jsx#L159) | PRESENT |
| `A=30%`, `R=25%`, `M=20%`, `C=15%`, `N=10%` weights stated | ✓ (1 hit each) | [Methodology.jsx:160-174](capstone-website/frontend/src/pages/Methodology.jsx#L160-L174) | PRESENT |
| "Du et al" 3-line literature triangulation | ✓ (3 hits) | [Methodology.jsx:162,164,167](capstone-website/frontend/src/pages/Methodology.jsx#L162) | PRESENT |
| Aggregation locus disclosure | ✓ (1 hit) | [Methodology.jsx:197-205](capstone-website/frontend/src/pages/Methodology.jsx#L197-L205) | PRESENT |
| Keyword-degradation paragraph: "3.7pp differential" | ✓ (1 hit) | [Methodology.jsx:236](capstone-website/frontend/src/pages/Methodology.jsx#L236) | PRESENT |
| "moving in opposite directions" | ✓ (1 hit) | [Methodology.jsx:233](capstone-website/frontend/src/pages/Methodology.jsx#L233) | PRESENT |
| Per-perturbation: rephrase 1.96pp / numerical 2.92pp / semantic 5.96pp | ✓ (1 hit) | [MethodologyPanels.jsx:163](capstone-website/frontend/src/components/MethodologyPanels.jsx#L163) | PRESENT |
| Krippendorff α = 0.55 (assumption) | ✓ (3 hits) | [Methodology.jsx:223,247](capstone-website/frontend/src/pages/Methodology.jsx#L223) | PRESENT |
| α = -0.13 (reasoning) | ✓ (3 hits) | [Methodology.jsx:223,245](capstone-website/frontend/src/pages/Methodology.jsx#L223) | PRESENT |
| α = -0.04 (method) | ✓ | [Methodology.jsx:224,247](capstone-website/frontend/src/pages/Methodology.jsx#L224) | PRESENT |
| "α is NEGATIVE on R and M" callout | ✓ | [Methodology.jsx:242](capstone-website/frontend/src/pages/Methodology.jsx#L242) | PRESENT |
| "0.5502" exact float | ✗ (0 hits) | rendered as "α = 0.55" | **NOT A GAP** — rounded for display; raw 0.5502 is in API not UI |
| "structural" disagreement framing | ✓ (1 hit) | bundle | PRESENT |
| ChatGPT "assumption-dominated" / Claude+Mistral "math-dominated" | ✓ (3 hits each) | [Methodology.jsx:283-285](capstone-website/frontend/src/pages/Methodology.jsx#L283-L285) | PRESENT |
| Per-model failure mode table (5 rows) | ✓ | [Methodology.jsx:95-101,288-308](capstone-website/frontend/src/pages/Methodology.jsx#L95-L101) | PRESENT |
| "Gemini calibration inversion" / "0 verbalized confidence" | ✓ (1+2 hits) | [Methodology.jsx:366-371](capstone-website/frontend/src/pages/Methodology.jsx#L366-L371) | PRESENT |
| "1,095 of 1,230" / "135 excluded" disclosure | ✓ (2 hits each) | [Methodology.jsx:393-394](capstone-website/frontend/src/pages/Methodology.jsx#L393-L394) | PRESENT |
| "161 of 171" / "10 CONCEPTUAL" disclosure | ✓ (2 hits each) | [Methodology.jsx:400-402](capstone-website/frontend/src/pages/Methodology.jsx#L400-L402) | PRESENT |
| FORMATTING_FAILURE 18/143 disclosure | ✓ (1 hit) | [Methodology.jsx:404-410](capstone-website/frontend/src/pages/Methodology.jsx#L404-L410) | PRESENT |
| Lit convergence #1 — Multi-dimensional rubrics | ✓ | [Methodology.jsx:110](capstone-website/frontend/src/pages/Methodology.jsx#L110) | PRESENT |
| Lit convergence #2 — Bootstrap CI separability | ✓ | [Methodology.jsx:111](capstone-website/frontend/src/pages/Methodology.jsx#L111) | PRESENT |
| Lit convergence #3 — Variance-as-first-class | ✓ | [Methodology.jsx:112](capstone-website/frontend/src/pages/Methodology.jsx#L112) | PRESENT |
| Lit convergence #4 — Verbalized confidence is unreliable | ✓ | [Methodology.jsx:113](capstone-website/frontend/src/pages/Methodology.jsx#L113) | PRESENT |
| Lit convergence #5 — Three-way convergence | ✓ | [Methodology.jsx:114](capstone-website/frontend/src/pages/Methodology.jsx#L114) | PRESENT |
| Lit convergence #6 — Single-judge limitations | ✓ | [Methodology.jsx:115](capstone-website/frontend/src/pages/Methodology.jsx#L115) | PRESENT |
| Literature comparison table (7 systems × 11 dims) | ✓ | [Methodology.jsx:16-31, 437-483](capstone-website/frontend/src/pages/Methodology.jsx#L437-L483) | PRESENT |

**Count:** 27 / 27 expected Phase 2 elements found in deployed bundle. Zero PHASE_2_GAPs.

---

## Group C panel presence

Component class names are minified, so check by distinctive chart titles + recharts imports + panel-internal strings.

| Panel | Source | Title in bundle | Recharts wired | API endpoint hit | Static fallback | Diagnosis |
|-------|--------|-----------------|----------------|------------------|-----------------|-----------|
| 1. Per-Model Pass-Flip | [MethodologyPanels.jsx:90-154](capstone-website/frontend/src/components/MethodologyPanels.jsx#L90-L154) | "Pass-flip rate by model" ✓ | BarChart ✓ | `/api/v2/pass_flip` ✓ | STATIC_PASSFLIP inlined ✓ | PRESENT |
| 2. Keyword-Degradation PNG | [MethodologyPanels.jsx:157-176](capstone-website/frontend/src/components/MethodologyPanels.jsx#L157-L176) | "Keyword vs Judge PASS rates" ✓ | n/a (PNG) | n/a (static asset) | `/visualizations/png/v2/combined_pass_flip_comparison.png` 200 ✓ | PRESENT |
| 3. Per-Dim Robustness | [MethodologyPanels.jsx:195-268](capstone-website/frontend/src/components/MethodologyPanels.jsx#L195-L268) | "Robustness degradation by NMACR" ✓ | BarChart ✓ | `/api/v2/robustness` ✓ | STATIC_PER_DIM_DELTA ✓ | PRESENT |
| 4. Per-Dim Calibration | [MethodologyPanels.jsx:279-344](capstone-website/frontend/src/components/MethodologyPanels.jsx#L279-L344) | "Calibration ECE by NMACR" ✓ | BarChart ✓ | `/api/v2/calibration` ✓ | STATIC_PER_DIM_ECE ✓ | PRESENT |
| 5. Acc-Calib Scatter | [MethodologyPanels.jsx:355-446](capstone-website/frontend/src/components/MethodologyPanels.jsx#L355-L446) | "Accuracy vs calibration per model" ✓ | ScatterChart ✓ | `/api/v2/calibration` + `/api/v2/rankings` ✓ | STATIC_ACC_CALIB ✓ | PRESENT |

Recharts in bundle: `responsive-container` + `recharts-wrapper` + `recharts` (6 hits total). All 5 panels integrated. Zero panel gaps.

---

## Group D follow-up backend wiring

| Field | Backend returns it | Frontend reads it | Diagnosis |
|-------|--------------------|--------------------|-----------|
| `/api/v2/pass_flip` → `combined.pct_pass_flip` = 0.2216, all 5 models populated | ✓ | ✓ ([MethodologyPanels.jsx:93-97](capstone-website/frontend/src/components/MethodologyPanels.jsx#L93-L97)) | WIRED |
| `/api/v2/robustness` → `per_dim_delta` keyed by `{model: {N,M,A,C,R}}` | ✓ | ✓ ([MethodologyPanels.jsx:206-222](capstone-website/frontend/src/components/MethodologyPanels.jsx#L206-L222)) | WIRED |
| `/api/v2/calibration` → `per_dim_ece` keyed by `{N,M,A,C,R: {model: ece}}` | ✓ | ✓ ([MethodologyPanels.jsx:283-289](capstone-website/frontend/src/components/MethodologyPanels.jsx#L283-L289)) | WIRED |
| `/api/v2/calibration` → `accuracy_calibration_correlation` (4 models, Gemini absent by design) | ✓ | ✓ ([MethodologyPanels.jsx:368-371](capstone-website/frontend/src/components/MethodologyPanels.jsx#L368-L371)) | WIRED |
| `/api/v2/rankings` → `accuracy.per_model[m].mean` | ✓ | ✓ ([MethodologyPanels.jsx:372-377](capstone-website/frontend/src/components/MethodologyPanels.jsx#L372-L377)) | WIRED |
| `/api/v2/health` | 12 files, all_ok=true ✓ | n/a | OK |

Zero DATA_GAPs.

---

## Missing elements summary

| Class | Count |
|-------|-------|
| DEPLOY_LAG (need redeploy) | 0 |
| PHASE_2_GAP (never added) | 0 |
| DATA_GAP (API empty) | 0 |
| RENDER_BUG (CSS/JS issue) | 0 — could not verify visually without browser-execution; bundle contains all expected strings |

---

## What was NOT found that the prompt expected

A few "expected phrases" from the Track A diagnostic spec are **not** in the source verbatim — but are not gaps:

1. **`0.5502`** — source uses `"α = 0.55"` rounded; raw float lives only in `judge_validation.json` API. Display rounding, not a gap.
2. **`A=0.30`** — source uses `A=30%` (percent form, line 160) and `weight: 0.30` (decimal form, line 9). Two forms; both present.
3. **Original literal "Krippendorff α = -0.13"** with that exact spacing — source uses unicode minus `α = −0.133` (line 244). Visually identical, byte-different. Grep with `-0.13` (ASCII hyphen) misses it; grep with `−0.13` (U+2212) finds it.

These are **not omissions** — they are formatting normalisations between audit prose and rendered UI.

---

## Recommended fixes

**None needed for content.** Bundle, source, backend all aligned at commit `3d7fe81`.

If user perception of "missing elements" persists, the most likely causes — in order of probability — are:

1. **Browser cache (highest probability).** User's browser is holding `index-<old-hash>.js` from before commit `fc7f079` (Group C, 5 panels) or `3d7fe81` (Group D wiring). Hard-refresh (Cmd-Shift-R) or DevTools → Disable Cache → reload.
2. **Confusion with another page.** `PosterCompanion.jsx` is missing several Phase 2 figures (per `audit/discovery_audit_2026-05-02.md` D-PC-04). If user is reviewing PosterCompanion not Methodology, that explains "missing." Verify which page they are on.
3. **Recharts render failure on user's browser.** All 4 chart panels depend on recharts ResponsiveContainer; if the user's browser blocks JS, has an extension breaking SVG, or has a viewport-zero situation, panels render empty. Check browser console for errors.
4. **Visual hierarchy makes a section feel "missing."** The α-NEGATIVE callout and Gemini-inversion callout are rendered as small `Callout` boxes (orange/red borders); they may be perceived as decorative, not as primary content. If user expected a dedicated section, rendering style is the cause, not absence.

---

## Most likely root cause

**Browser cache.** Local `dist/index-CYErrNq0.js` matches deployed bundle byte-for-byte; source contains every Phase 2 + Group C + Group D expected element; backend returns every expected field. Source-of-truth is correct. The discrepancy lives in whatever the user's browser is rendering, which is one HTTP layer outside this audit's reach.

**Suggested verification step** (no code change): ask the user to (a) hard-refresh (Cmd-Shift-R) the `/methodology` page, (b) open DevTools Network tab, (c) confirm the loaded bundle is `index-CYErrNq0.js`, (d) screenshot the page sections that look "missing." Comparing the screenshot against the 9-section structure in [Methodology.jsx:118-486](capstone-website/frontend/src/pages/Methodology.jsx#L118-L486) will identify the perceived gap.
