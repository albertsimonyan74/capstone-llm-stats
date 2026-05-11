# Poster rebuild — SCRAPE_PLAN

Phase 1 deliverable. **Awaiting review before any `.tex` edits.** Source-of-truth files
read in order: `main.tex`, `DESIGN_AUDIT.md`, `assets/latex_palette.tex`,
`code/scripts/print_theme.py`, `figures/`, `README.md`,
`capstone-website/frontend/src/{App.css,index.css,data/sitePalette.js}`,
`components/{MethodologyPanels,ThreeRankingsComparison,KeyFindings,MobiusStrip}.jsx`,
`CLAUDE.md`, `data/processed_data/results_v2/*`, `llm-stats-vault/90-archive/audit/recompute_log.md`.

Three findings need a decision before Phase 2 — flagged with **DECIDE** below.

---

## A. Palette deltas (web → print)

`assets/latex_palette.tex` already mirrors `print_theme.py`. Coverage check
against website tokens used in components we mimic:

| Token group | latex_palette.tex coverage | Notes |
|---|---|---|
| Page bg / body text / muted / border / gridline | ✅ `white` / `slate900` / `slate500` / `slate300` / `slate200` | Complete |
| Model brand (5) | ✅ `modelClaude/ChatGPT/Gemini/DeepSeek/Mistral` (-600 shades) | Complete |
| NMACR dim colors | ✅ `nmacrA/R/M/C/N` | Complete |
| L1 failure buckets | ✅ `bucketAssumption/Math/Format/Concept` | Complete |
| Calibration conf buckets (0.3/0.5/0.6) | ✅ `calibConf03/05/06` | Complete |
| Accent gold / teal / purple | ✅ `gold600` / `teal600` / `purple600` | Complete |
| Semantic good/bad/neutral | ✅ `emerald600` / `red600` / `slateNeutral` | Complete |

**Deltas needed: none.** All deliberate web tokens already have a print analog.
The only web tokens deliberately *not* mirrored are atmosphere effects —
glows, conic / radial gradients, dot grid — which DESIGN_AUDIT §5.3 explicitly
excludes from print.

**Conclusion:** `\input{latex_palette.tex}` is complete. Inline `\definecolor`
in current `main.tex` (`PosterPrimary`, `PosterAccent`, `ClaudeC`, etc.) gets
deleted in v2 and replaced with palette references (`slate900`, `teal600`,
`modelClaude`, …).

---

## B. Website patterns to inherit (ranked)

1. **PanelShell typography eyebrow** — `MethodologyPanels.jsx:34-37`. Mono
   uppercase, 11pt @ web, weight 800, tracking 0.16em, accent color. Strongest
   single signature in the design system. → Print macro `\eyebrow{ACCENT}{TEXT}`
   using Space Mono uppercase, tracking via `\addfontfeatures{LetterSpace=8.0}`,
   color `teal600` default.
2. **Mono tabular numerics for every numeric** — every Recharts axis tick,
   `LabelList`, and stat number sets `fontFamily: 'monospace'`. Body labels
   stay Space Grotesk. → Print macro `\num{N}` wraps `{\fontspec{Space
   Mono}[Numbers=Tabular]#1}`. Apply uniformly: ECE values, n=, percents,
   counts, table cells.
3. **Möbius monogram as decorative title-corner mark (~5% opacity)** —
   `MobiusStrip.jsx`. Caveat: web component is a `<canvas>` animation, not
   SVG. Rendering to static vector requires either (a) headless Chromium
   snapshot of the canvas at one frame + `convert -density 600 png pdf`, or
   (b) reimplement the parametric `mobiusPoint(u,v) = ((R+hw·v·cos(u/2))·cos(u),
   …)` in TikZ pgfplots (3D surf, hidden line removal). Recommend (a) for
   fidelity; bundle the resulting `mobius_monogram.pdf` flat. **DECIDE** below.
4. **Teal-600 single primary accent** — every panel eyebrow on the website
   uses one of three accents from `ACCENTS`: teal / gold / purple. Print
   reduces to teal-600 default with violet-600 reserved for the
   keyword↔judge divergence path only. No red, no gold for eyebrows. Gold
   reserved for chart-internal threshold reference lines (already canonical
   in print_theme: `ACCENT_GOLD_PRINT = #d97706`).
5. **Thin teal hairline below section heading** — web uses
   `border-bottom: 1px solid rgba(0,255,224,0.18)` under panel headers.
   Print equivalent: `\textcolor{teal600}\rule{\linewidth}{0.6pt}` below
   each section title.
6. **Italic-muted captions** — DESIGN_AUDIT §6.2. Print: `\textit{}` +
   color `slate500`, max 2 lines, italic Space Grotesk.
7. **3px colored top border on per-model cards** — DESIGN_AUDIT §6.4. Print
   equivalent: TikZ panel with `top color=modelX, top color band=2pt` (one
   thin colored bar at top, neutral border below). Used for failure-mode
   cards, NOT for the keyword/judge takeaway boxes (those get the new
   teal-left-border treatment per spec).
8. **Italic muted "Why it matters" eyebrow at card foot** — `KeyFindings.jsx:151`.
   Print: italic micro-eyebrow `slate500`, body italic. Apply to Conclusions
   bullets if room.

---

## C. Overleaf bundle file list (flat)

```
poster/overleaf_bundle/
├── main.tex                           (renamed from main_v2.tex)
├── latex_palette.tex                  (copy of poster/assets/latex_palette.tex)
├── aua_logo.png                       (recompressed from poster/AUA_ML_RGB_ENG.webp → png@600dpi)
├── mobius_monogram.pdf                (NEW — see DECIDE-1)
├── fig1_disagreement.pdf              (regenerated — see DECIDE-3)
├── fig2_krippendorff.pdf              (regenerated)
├── fig3_dimension_leaderboard.pdf     (regenerated)
├── fig4_calibration_paired.pdf        (regenerated)
├── fig5_failure_taxonomy.pdf          (regenerated)
├── fig6_robustness_heatmap.pdf        (regenerated — used in RQ4 panel)
├── fig7_nmacr_weights.pdf             (regenerated — see DECIDE-2)
└── README_OVERLEAF.md                 (XeLaTeX, main.tex, font notes)
```

Flat — no nested includes beyond `\input{latex_palette.tex}`.

`AUA_ML_RGB_ENG.webp` → convert to `aua_logo.png` (Overleaf's PDFLaTeX/XeLaTeX
won't read .webp without extra packages).

---

## D. Numeric / label fixes

Cross-checked against `data/raw_data/synthetic/perturbations_all.json` (live count),
`data/processed_data/results_v2/*` (live JSON), `CLAUDE.md`, and
`llm-stats-vault/90-archive/audit/recompute_log.md` Phase 1.8.

| Field | current main.tex | canonical (verified) | source |
|---|---|---|---|
| Perturbation total | "398 = 146 base × 2–3 variants" | **473 records** (75 v1 + 398 v2) covering 171 base task_ids | `len(perturbations_all.json) = 473`; CLAUDE.md "473 perturbations" |
| Pass-flip eligible n | "1,094" | **n = 2,850** (combined: base + perturbation, eligible) | `combined_pass_flip_analysis.json:combined.n_eligible = 2850` |
| Pass-flip rate | "25.0% (274 / 1094)" | **20.74% (591 / 2,850)** combined | same JSON, `pct_pass_flip = 0.2074`; `n_pass_flip = 591` |
| α (assumption) | "0.59" | **0.573** | `krippendorff_agreement.json` + KeyFindings static fallback |
| α (reasoning_quality) | "0.16" | **−0.125** (95% CI [−0.197, −0.059] excludes zero) | KeyFindings card 2 |
| α (method_structure) | "−0.01" | **−0.009** (CI [−0.072, +0.062], chance-level) | KeyFindings card 2 |
| Assumption-skip rate | "51.5% zeros" (base-only n=1,229) | **two valid framings — DECIDE-2 below** | judge_dimension_means.json (51.5%); error_taxonomy_v2.json (46.9% = 67/143 audited) |
| Accuracy leader | implicit "Claude" in row 4 | **Gemini** (mean 0.7314 [0.7060, 0.7565]) | `ThreeRankingsComparison.jsx:14`; `bootstrap_ci.json` |
| Robustness leader | not stated | **ChatGPT** (Δ=+0.0003) — ChatGPT/Mistral effectively tied (CIs cross zero) | same |
| Calibration leader | "ChatGPT (0.063)" | **Claude (verbalized ECE 0.033)** — Claude/ChatGPT effectively tied (0.033 / 0.034) | same |
| ECE table | values ~0.06–0.18 (old scoring) | new canonical: **claude 0.033, chatgpt 0.034, gemini 0.077, mistral 0.081, deepseek 0.198** | same |
| Run total | "1,230 = 5 × 246 base" | base 1,230 still correct; **total runs incl. perturbations: 5 × (246 + ~473) ≈ 3,595**. The 2,850 eligible figure subsets to where keyword + judge both produced a valid pass/fail. | runs.jsonl + perturbation_runs.jsonl |

**Three DECIDE points before Phase 2:**

### DECIDE-1: Möbius monogram production path

(a) Headless Chromium snapshot of `MobiusStrip.jsx` rendered standalone in
a tiny dev page → screenshot single frame → `convert` to PDF. Highest
fidelity, ~30 min implementation. Requires running `npm run dev` + a one-off
puppeteer script.

(b) Reimplement parametric Möbius surface in TikZ/pgfplots with `surf`,
`samples=90,16`, three-color gradient mapped to `u`, opacity 0.05. Pure
LaTeX, no external dependency, but the canvas's per-quad opacity-fill +
back-to-front sort is hard to match exactly. Lower fidelity, faster compile.

(c) Skip the monogram. Replace title-corner decorative mark with a thin
teal-600 hairline only.

**Recommendation: (a)** — it's the only option that visually matches the
website. (b) will look hand-drawn next to the site. (c) loses the brand
tie. Will write a one-off `poster/scripts/render_mobius_monogram.py` that
spins up puppeteer, captures, converts.

### DECIDE-2: NMACR weights — which to display?

`README.md` figure 1 ships `nmacr_weights.svg` showing **literature-derived**
weights `A=30, R=25, M=20, C=15, N=10`. **All actually-computed scores in
the figures use equal `0.20` weights** per CLAUDE.md and `code/analysis/metrics.py`.
The website's `KeyFindings` card 4 explicitly labels its Gemini-#1 finding
"under the literature-weighted NMACR scheme" — i.e., the site is up-front
that weights matter. The site shows BOTH: live equal-weight rankings
(`ThreeRankingsComparison`) AND literature-weighted Gemini-#1 framing.

Two coherent options:

(i) **Show equal weights** in the methods cartoon NMACR box. Caption notes
literature-derived alternative but doesn't display it. Rankings panel shows
the equal-weight numbers. Loses the "literature comparison" thread but
internally consistent. Simpler.

(ii) **Show both** as a small two-bar comparison in the methods cartoon
("we benchmark with equal weights; literature suggests A/R-heavy"). All
ranking numbers stay equal-weight. More honest, more poster space.

**Recommendation: (ii)** — keeps the poster aligned with the website
narrative ("rankings depend on weighting"). The existing `nmacr_weights.svg`
already visualizes (ii) — regenerate the bars with both schemes side-by-side
or use a single-row stacked-bar showing equal vs literature.

### DECIDE-3: Where do the PDF figures come from?

`code/scripts/print_theme.py:dual_save()` is **policy-locked to SVG + PNG only**
(per docstring + README) — no PDF. But Overleaf XeLaTeX wants PDFs (or PNGs)
for `\includegraphics`. SVG is not readable by `\includegraphics`.

The `D` git status on `poster/figures/*.pdf` confirms PDFs were deleted
in a prior commit — this is the deliberate policy.

Three coherent paths:

(i) **Add PDF output to `dual_save()`** — one-line change, regenerate all 7
figures, add `*.pdf` to bundle. Cleanest. Mild pushback: violates the
"SVG primary, no PDF" policy that the README explicitly states.

(ii) **Convert existing SVGs to PDF at bundle-build time** — a small
`poster/scripts/build_overleaf_bundle.sh` that runs
`rsvg-convert -f pdf in.svg -o out.pdf` (or `inkscape --export-type=pdf`).
Doesn't touch `dual_save`. Slight risk of font-substitution at conversion.

(iii) **Use PNG@600dpi in Overleaf** instead of PDF. PNG is already
shipped. Vector quality is lost for charts but at A0-print size 600dpi
is plenty. Simplest, no new tooling.

**Recommendation: (i)** — the no-PDF policy was reasonable when the
website was the primary distribution. For a print-shop A0 print run via
Overleaf, vector PDF beats raster PNG. One-line change to `dual_save()`,
update README. The deleted `*.pdf` files in git status are evidence this
was already attempted once and reverted; understanding why the revert
happened before re-introducing is on the agenda.

---

## E. Layout (rebuild target — for review)

5-row spine matching Sarvazyan's rubric, all coords as `\newlength` named
constants at top of `main_v2.tex`. Hand-rolled TikZ overlay (no
`tikzposter`). A0 portrait 841×1189mm.

```
Row 1 (≈12% h)   Title block (sentence case, breakable after "match?")
                 Author / supervisor / institute / mono URL on separate lines
                 AUA logo (left corner)        Möbius monogram (right corner, ~5% α)
                 Thin teal-600 hairline         (full width)

Row 2 (≈10% h)   Abstract (5 bullets, ≤8 lines, full width)

Row 3 (≈22% h)   Introduction (~25% w)  |  Methods cartoon (~75% w, full visual weight)
                                        5 PanelShell stages 01..05, mono eyebrow + 1-line caption
                                        teal-600 connectors, violet-600 keyword↔judge divergence branch

Row 4 (≈40% h)   3-column results grid:
                 Col-1   Three Rankings (fig3 dimension_leaderboard) + RQ2 difficulty
                 Col-2   Failure taxonomy (fig5) + RQ3 error types
                 Col-3   Calibration paired (fig4) + Disagreement matrix 2×2 (fig1) +
                         Robustness heatmap (fig6) — small multiples
                 Embedded Key Findings callout spanning bottom of grid:
                   Headline: "Three rankings, three winners — no model dominates."
                   Three mono-eyebrow + body bullets (KEYWORD vs JUDGE / TOP-2 SWAP /
                   DOMINANT FAILURE). Single teal-600 left border, no colored fills.

Row 5 (≈16% h)   Conclusions (wide, ~70% w)  |  Acks + References (~30% w)
```

**Top-2 swap copy** (per audit): The user-spec wording "Claude leads
accuracy; ChatGPT leads calibration" is **not what the data shows**. Live
canonical: **Gemini #1 accuracy / ChatGPT (≈Mistral) #1 robustness /
Claude (≈ChatGPT) #1 calibration** — three different leaders. Recommend
rewording the Key Findings bullet to:

> THREE LEADERS  Gemini leads accuracy (0.731). ChatGPT leads robustness
> (Δ = +0.000). Claude leads calibration (ECE = 0.033). No model wins all
> three.

— this is what the website's `useKeyFindings()` card 5 already says
verbatim. Aligns site and poster.

---

## F. Typography contract

| Element | Family | Size (A0 native pt) | Weight | Color | Notes |
|---|---|---|---|---|---|
| Title | Space Grotesk | 96 | 700 | slate900 | Sentence case, ≤2 lines |
| Author/Supervisor/Institute | Space Grotesk | 32 | 500 | slate500 | One per line |
| URL | Space Mono | 28 | 400 | slate500 | Mono — fixed-width URL look |
| Section title | Space Grotesk | 44 | 700 | slate900 | Followed by teal-600 hairline |
| Eyebrow (mono small-caps) | Space Mono | 18 | 700 | teal600 (default) | tracking 0.16em, uppercase |
| Body | Space Grotesk | 26 | 400 | slate900 | Sarvazyan rule ≥24pt — clearance verified |
| Body emphasis | Space Grotesk | 26 | 600 | slate900 | No italic for emphasis |
| Caption | Space Grotesk italic | 22 | 400 | slate500 | Max 2 lines |
| Numeric (in-body) | Space Mono | 26 | 700 | slate900 | `\num{}` macro, tabular figures |
| Figure caption | Space Grotesk italic | 20 | 400 | slate500 | Format: "n=X · what's varied · what's fixed" |
| Mono URL / code / task_id | Space Mono | 22 | 400 | slate900 | |

Line-width cap: every prose block ≤ 65 chars. Methods bullet-list panels and
Conclusions get internal `\begin{multicols}{2}` if the panel itself is wider
than 65 chars. Web body uses 1.55–1.7 line-height; print uses 1.35
(matplotlib axis-label aesthetic).

---

## G. Color discipline contract

- Background: `white` everywhere. No tinted panel fills.
- Body text: `slate900`. Muted: `slate500`.
- Accent (eyebrow, hairline, primary section markers): `teal600`. Single accent.
- Divergence accent: `purple600` ONLY for (a) the keyword↔judge branch line in
  the methods cartoon, (b) the disagreement-direction column in the 2×2
  matrix figure. Nowhere else.
- Reference lines / threshold markers: `gold600` (chart-internal only).
- Model identity: `modelClaude/ChatGPT/Gemini/DeepSeek/Mistral` (-600
  shades). Apply only where model identity is meaningful (chart cells,
  per-model card top-borders). Do NOT colorize model names in body prose
  (current main.tex does this — drop in v2).
- Takeaway boxes: thin `teal600` left border (3pt) + bold "TAKEAWAY:"
  Space Mono eyebrow + body on white. No SoftRed/SoftViolet/SoftTeal
  cycling. One convention only.

---

## H. Methods cartoon — TikZ structure (to inline, not external PDF)

5 PanelShell-style nodes left-to-right. Each node:
- mono eyebrow `01 / 05` … `05 / 05` in slate500
- bold heading in teal600
- 1-line body in slate900

```
[01] Tasks      → [02] Perturb    → [03] Score    → [04] Judge    → [05] Compare
171 base          473 unique         NMACR              Llama 3.3 70B    Three rankings:
38 task families  × 5 models         5 dims × 0.20      external rubric  acc · robust · calib
                  = 2,365 runs
                                            ↓
                                       [03b] Keyword
                                       rubric (legacy)
                                            ↓
                                       diverges to [05]
                                       in violet-600
```

Connectors `\draw[teal600, line width=1.5pt, -{Stealth[length=4mm]}]`. Divergence
branch in `purple600` with same arrow style. All 5 nodes equal width via
`\methodNodeWidth` length constant.

---

## I. Removals from current `main.tex`

Things to drop in v2 (all flagged in user spec):

- `\definecolor{...}` block lines 23–34 — replaced by `\input{latex_palette.tex}`.
- `\modelname{ColorC}{name}` macro and every body-prose use of it (model
  names should not be colorized in prose; only in chart cells).
- ALL CAPS title.
- The Key Findings "single-winner badges" framing — replaced per the
  THREE LEADERS rewrite above.
- Random soft-color `\colorlet{Soft...}` takeaways (none currently exist
  in main.tex but the spec flags them — confirm none reintroduced in v2).
- 5-rectangle TikZ pipeline (the row 2 methodology block currently has
  no cartoon — the new methods cartoon replaces it).
- Hardcoded ECE table with old values — regenerate from
  `ThreeRankingsComparison.jsx` static fallback (post Phase 1.8).
- "1,094 runs (135 tasks excluded)" disagreement framing — replaced with
  combined 2,850 / 591 / 20.74% framing.
- `tikzposter` document class + `\usetheme/\usecolorstyle/\usebackgroundstyle/\useblockstyle`
  — replaced with hand-rolled TikZ overlay layout.

---

## J. Open questions for review

1. **DECIDE-1** — Möbius monogram path: (a) puppeteer / (b) TikZ / (c) skip?
   Recommend (a).
2. **DECIDE-2** — NMACR weights: equal-only / both equal+literature?
   Recommend showing both with equal weights as the "live-scored" annotation.
3. **DECIDE-3** — PDF figures: extend `dual_save()` / convert at build-time
   / use PNG@600dpi? Recommend extending `dual_save()`.
4. **Three Leaders rewording** — confirm Key Findings should match the
   website verbatim (Gemini/ChatGPT/Claude on accuracy/robustness/calibration).
5. **Assumption-skip framing** — 51.5% (judge =0 rate, base n=1,229) or
   46.9% (audited L1 ASSUMPTION_VIOLATION = 67/143)? Recommend 46.9% to
   match KeyFindings card 3.
6. **PDF deletion in git status** — `poster/figures/*.pdf` shows as `D`
   (staged-deleted). Was this intentional and tied to a prior policy
   decision, or accidental? Affects DECIDE-3.

After answers I'll produce `main_v2.tex` and `overleaf_bundle/` per Phase 2+3.
