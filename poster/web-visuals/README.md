# poster/web-visuals — high-DPI captures of website infographics

Three production PNGs captured headlessly from the live deployed site for
inclusion in the A0 print poster.

## Source

- **URL**: https://bayes-benchmark.vercel.app
- **Capture date**: 2026-05-06
- **Capturer**: Playwright Chromium (chromium-headless-shell v1217)
- **Viewport**: 1600 × 1200
- **deviceScaleFactor**: 3 (retina output for print)

## Outputs

| File | Selector | Dimensions (px) | Size |
|---|---|---|---|
| `pipeline.png` | `section#pipeline` | 4200 × 3465 | 873 KB |
| `models.png` | `section#models` | 4200 × 2616 | 1.36 MB |
| `nmacr_weights.png` | smallest div in `section#methodology` containing both `.nmacr-segment` and `.nmacr-cards-grid` (no native id/class — tagged at runtime as `[data-capture="nmacr"]`) | 3600 × 1563 | 443 KB |

All three captures exceed the 2400 px long-edge target. PNGs are device-
scaled at 3× DPR.

## What each one shows

- **pipeline.png** — orbital benchmarking pipeline. h2 "Pipeline" + the
  six-stage hexagonal orbit (Task Generation, Standardized Prompting,
  Multi-Model Evaluation, Five-Dimensional Scoring, Robustness Testing,
  Error Taxonomy) around the central "Benchmarking" hub, with rotating
  dashed orbital rings.
- **models.png** — Models Under Evaluation hub. h2 + the
  `NeuralNetwork.jsx` canvas with 5 model badges (CL · GM · GP · DS · MS)
  on the proximity-edge particle network.
- **nmacr_weights.png** — NMACR rubric panel. The 5-segment horizontal
  weight bar (A · 30%, R · 25%, M · 20%, C · 15%, N · 10%), the 5
  dimension cards below it, and the "Aggregation locus" body footer
  describing where literature-derived weights are applied.

## Reproducing

From the repo root:

```bash
node poster/web-visuals/capture.mjs
```

The script:
1. Opens the live URL with `waitUntil: 'domcontentloaded'` (`networkidle`
   times out — the site keeps long-poll fetches alive).
2. Waits 4 s for the rAF canvases (NeuralNetwork, MobiusStrip,
   GlobeBackground, HeroNetworkBg) to render at least one frame.
3. Tags the NMACR Card wrapper with `data-capture="nmacr"` via in-page
   evaluate (the wrapper has no native id/class — pure inline styles).
4. Injects a stylesheet that zeroes all CSS animation/transition
   durations. Canvas rAF loops cannot be paused this way; whatever frame
   they happen to be on at capture time is what gets captured.
5. For each target: scrolls into view, waits 600 ms, calls
   `element.screenshot({ scale: 'device' })`.

If the canvas decorations look sparse (NeuralNetwork particles or
pipeline rotating-ring dots), re-run 2–3 times and pick the best frame.

## Notes on canvas decorations

- `pipeline.png` orbital rings: CSS-driven `@keyframes ringRotate` /
  `ringCCW` — frozen by the animation-zero stylesheet. Dot positions are
  deterministic per ring at the frozen instant.
- `models.png` neural network: HTML5 canvas with `requestAnimationFrame`
  loop. Cannot be paused via CSS. Edge connectivity and node positions
  are the same across runs (determined by `Math.random()` seed in
  `NeuralNetwork.jsx`'s `useEffect`), but pulse positions differ.
- `models.png` background `HeroNetworkBg`: same — different pulse
  positions per run.
- `pipeline.png` dot grid (`body::before`): static, deterministic.
