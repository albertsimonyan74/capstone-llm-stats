# 2026-05-06 — Poster rebuild (Phase 1: SCRAPE_PLAN)

Goal: rebuild the Overleaf-bound LaTeX poster (`poster/main.tex`) so it inherits
the website's visual identity, compiles via XeLaTeX, and respects Sarvazyan's
print rules.

## Phase 1 — DONE

- Read inventory: `main.tex`, `DESIGN_AUDIT.md`, `assets/latex_palette.tex`,
  `scripts/print_theme.py`, `figures/`, `README.md`,
  `frontend/src/{App.css, index.css, data/sitePalette.js,
  components/MethodologyPanels, ThreeRankingsComparison, KeyFindings, MobiusStrip}.jsx`,
  `CLAUDE.md`, `experiments/results_v2/*`, `audit/recompute_log.md`.
- Verified live numerics from `experiments/results_v2/*` and
  `data/synthetic/perturbations_all.json`.
- Wrote `poster/SCRAPE_PLAN.md` with sections A–J.

## Numeric corrections found vs current `main.tex`

| Field | Current main.tex | Canonical (verified) |
|---|---|---|
| Perturbations | 398 | **473** (75 v1 + 398 v2 covering 171 base task_ids) |
| Pass-flip n | 1,094 | **2,850** (combined base+pert eligible) |
| Pass-flip rate | 25.0% | **20.74%** (591 / 2,850) |
| α (assumption) | 0.59 | **0.573** |
| α (reasoning_quality) | 0.16 | **−0.125** (CI excludes zero) |
| α (method_structure) | −0.01 | **−0.009** (CI [−0.072, +0.062]) |
| Accuracy leader | implicit Claude | **Gemini** (0.7314 [0.7060, 0.7565]) |
| Calibration leader | ChatGPT (0.063) | **Claude** (verbalized ECE 0.033) — Claude/ChatGPT tied |
| Robustness leader | not stated | **ChatGPT** (Δ=+0.0003) — ChatGPT/Mistral tied |

**Important:** the user-spec wording "Claude leads accuracy; ChatGPT leads
calibration" contradicts current canonical data. The website (`KeyFindings`
card 5) already says "three different rankings — Gemini/ChatGPT/Claude on
accuracy/robustness/calibration". Recommend rewording the Key Findings
bullet to match the website.

## Open DECIDE points (need answers before Phase 2)

1. Möbius monogram production path — (a) headless Chromium snapshot of
   `MobiusStrip.jsx`, (b) TikZ reimplementation, (c) skip. Recommend (a).
2. NMACR weights display — equal-only vs both equal + literature.
   Recommend show both (matches website narrative).
3. PDF figures — extend `dual_save()` to emit PDF, convert SVG→PDF at
   build, or use PNG@600dpi. Recommend extending `dual_save()`. Note: the
   `D` git status on `poster/figures/*.pdf` means PDFs were deleted in a
   prior commit (deliberate per `print_theme.py` policy + README).
4. Assumption-skip framing — 51.5% (judge zero-rate, n=1,229) vs 46.9%
   (audited L1 ASSUMPTION_VIOLATION 67/143). Recommend 46.9% to match
   `KeyFindings` card 3.

## Phase 2 + 3 — pending Phase 1 review

After answers to DECIDE-1..3 + Three-Leaders rewording confirmed, produce:
- `poster/main_v2.tex` (XeLaTeX target, hand-rolled TikZ overlay, no
  tikzposter, all coords as `\newlength`).
- `poster/overleaf_bundle/` (flat: main.tex, latex_palette.tex, aua_logo.png,
  mobius_monogram.pdf, fig1..7 PDFs, README_OVERLEAF.md).
- Local `xelatex main.tex` × 2 verification.

## Files touched

- `poster/SCRAPE_PLAN.md` — NEW.
- `llm-stats-vault/sessions/2026-05-06-poster-rebuild.md` — NEW (this file).

No `.tex` edits in Phase 1 per spec.
