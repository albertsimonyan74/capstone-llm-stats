---
tags: [session, literature, day3, vault]
date: 2026-05-01
---

# Day 3 — Literature Foundation Session (2026-05-01)

## Goal

Build a structured literature library at `llm-stats-vault/40-literature/` so
poster, paper, and future analysis can cite consistently. 22 sources total.

## Context

Day 3 of the May 8 poster sprint. Builds on:
- Day 1 ([[2026-04-30-day1-poster-sprint]]) — judge rubric + perturbation
  generator + calibration analysis groundwork.
- Day 2 audit — see `audit/day2_audit_report.md` for P-2/P-7 findings.
- Group B research — newly-discovered papers from Day 3 web searches feed RQ
  reweighting + literature comparison work.

## What was added

26 files total under `llm-stats-vault/40-literature/`:
- `README.md` — master index organized by theme.
- `citation-map.md` — reverse index (artifact → sources).
- `bibtex.bib` — 22 bibtex entries (papers + textbooks).
- `poster-citations.md` — drop-in short forms + citation cluster recipes.
- `papers/` (15 notes — 5 originally-cited + 10 newly-discovered).
- `textbooks/` (7 notes — graduate Bayesian texts).

## Sources catalogued

### Originally-cited papers (5)
1. Lu et al. (2025) — StatEval — arXiv 2510.09517
2. Nagarkar et al. (2026) — Can LLM Reasoning Be Trusted — arXiv 2601.14479
3. Liu et al. (2025) — MathEval — DOI 10.1007/s44366-025-0053-z
4. Chen et al. (2022) — Program of Thoughts — arXiv 2211.12588
5. Wei et al. (2022) — Chain of Thought — arXiv 2201.11903

### Newly-discovered papers (10)
6. Longjohn et al. (2025) — Bayesian Eval — arXiv 2511.10661
7. ReasonBench (2025) — Instability — arXiv 2512.07795
8. BrittleBench (2026) — Robustness — arXiv 2603.13285
9. Wang et al. (2025) — Ice Cream causal — arXiv 2505.13770
10. Park et al. (2025) — LLM-as-Judge empirical — arXiv 2506.13639
11. FermiEval (2025) — Overconfidence — arXiv 2510.26995
12. Multi-Answer (2026) — Consistency confidence — arXiv 2602.07842
13. Math-Failures (2026) — Reasoning failures — arXiv 2502.11574
14. Judgment-Noise (2025) — Single-judge bias — arXiv 2509.20293
15. Statistical Fragility (2025) — Tübingen/Cambridge — arXiv link TODO

### Graduate textbooks (7)
- Bolstad (2007) — Introduction to Bayesian Statistics, 2nd ed.
- Bishop (2006) — Pattern Recognition and Machine Learning
- Ghosh, Delampady & Samanta (2006) — Introduction to Bayesian Analysis
- Hoff (2009) — A First Course in Bayesian Statistical Methods
- Carlin & Louis (2008) — Bayesian Methods for Data Analysis, 3rd ed.
- Goldstein & Wooff (2007) — Bayes Linear Statistics
- Lee (2012) — Bayesian Statistics: An Introduction, 4th ed.

## TODOs flagged

13 of 15 paper notes have placeholder author lists (TODO markers in metadata
+ bibtex). Per task brief, max 2 web searches per source — TODO flagged where
metadata couldn't be fully verified within budget. Resolve before final
submission.

Paper 15 (Statistical Fragility) also needs the original arXiv link located
(currently cited via marktechpost.com summary).

## How to use this in future sessions

1. **Citing in poster:** open `40-literature/poster-citations.md`, copy the
   short form (e.g. "(Lu, 2025)") for the relevant theme.
2. **Citing in paper prose:** open the per-source note, copy the
   "Citation in paper" string. Use the bibtex key for `\cite{}`.
3. **Looking up "which source supports X":** open `citation-map.md`. Reverse
   index by RQ, script, task type, audit finding, poster panel, output file,
   figure.
4. **Adding a new source:** copy the per-paper or per-textbook template from
   this session log; save under `papers/` or `textbooks/`; update
   `README.md` theme sections + `bibtex.bib` + `citation-map.md`.

## Synchronization with website

The website's References section (capstone-website/frontend/src/) displays
the 5 originally-cited papers + 7 textbooks. The vault is now the source of
truth — when website References changes, mirror to vault first, then propagate
to poster/paper. Out of scope for this session: editing the website References
component.

## Verification

- `ls llm-stats-vault/40-literature/` → 4 top-level files + 2 dirs.
- `ls llm-stats-vault/40-literature/papers/` → 15 paper notes.
- `ls llm-stats-vault/40-literature/textbooks/` → 7 textbook notes.
- Total file count: **26**.

## Files added

- `llm-stats-vault/40-literature/README.md`
- `llm-stats-vault/40-literature/citation-map.md`
- `llm-stats-vault/40-literature/bibtex.bib`
- `llm-stats-vault/40-literature/poster-citations.md`
- `llm-stats-vault/40-literature/papers/01-original-stateval-2025.md`
- `llm-stats-vault/40-literature/papers/02-original-can-llm-reasoning-2026.md`
- `llm-stats-vault/40-literature/papers/03-original-matheval-2025.md`
- `llm-stats-vault/40-literature/papers/04-original-program-of-thoughts-2022.md`
- `llm-stats-vault/40-literature/papers/05-original-chain-of-thought-2022.md`
- `llm-stats-vault/40-literature/papers/06-new-longjohn-bayesian-eval-2025.md`
- `llm-stats-vault/40-literature/papers/07-new-reasonbench-2025.md`
- `llm-stats-vault/40-literature/papers/08-new-brittlebench-2026.md`
- `llm-stats-vault/40-literature/papers/09-new-ice-cream-causal-2025.md`
- `llm-stats-vault/40-literature/papers/10-new-llm-judge-empirical-2025.md`
- `llm-stats-vault/40-literature/papers/11-new-fermieval-2025.md`
- `llm-stats-vault/40-literature/papers/12-new-multi-answer-confidence-2026.md`
- `llm-stats-vault/40-literature/papers/13-new-math-reasoning-failures-2026.md`
- `llm-stats-vault/40-literature/papers/14-new-judgment-becomes-noise-2025.md`
- `llm-stats-vault/40-literature/papers/15-new-statistical-fragility-2025.md`
- `llm-stats-vault/40-literature/textbooks/bolstad-bayesian-statistics.md`
- `llm-stats-vault/40-literature/textbooks/bishop-prml.md`
- `llm-stats-vault/40-literature/textbooks/ghosh-delampady-samanta-bayesian.md`
- `llm-stats-vault/40-literature/textbooks/hoff-bayesian-methods.md`
- `llm-stats-vault/40-literature/textbooks/carlin-louis-bayesian-data-analysis.md`
- `llm-stats-vault/40-literature/textbooks/goldstein-wooff-bayes-linear.md`
- `llm-stats-vault/40-literature/textbooks/lee-bayesian-statistics.md`

## Files modified

- `llm-stats-vault/00-home/current-priorities.md` — added "Literature
  foundation (added 2026-05-01)" section with 22-source breakdown and
  pointers to vault index files.

## Next steps

- ~~Resolve the 13 TODO author-list placeholders before final paper submission~~
  → Done in Day 3 housekeeping pass below.
- ~~Locate original arXiv link for Paper 15 (Statistical Fragility).~~
  → Done in Day 3 housekeeping pass below (canonical: arXiv 2504.07086).
- When `audit/literature_comparison.md` is written by Group B, add inline
  links from each paper note to the comparison row.
- When `audit/rq_reweighting.md` is written, update RQ→source mappings in
  citation-map.md if the reweighting changes which RQ load-bears each finding.
- Follow-up review needed: Papers 09 (Ice Cream) and 10 (LLM-as-Judge) have
  bibtex keys `wang2025icecream` and `park2025judge` that don't match their
  actual first authors (Du and Yamauchi respectively). Keys retained per
  task constraint but Citation forms in the per-paper notes still read
  "(Wang et al., 2025)" / "(Park et al., 2025)" — those were not in the
  housekeeping pass scope. Update before final submission.
- Paper 15 canonical title differs from MarkTechPost framing — note has
  both the descriptive title ("LLM Reasoning Benchmarks are Statistically
  Fragile") and canonical title ("A Sober Look at Progress…"). Pick one
  for paper prose before final submission.

---

## Day 3 housekeeping pass (2026-05-01, later)

Resolved all 14 flagged metadata items (13 author-list TODOs + Paper 15
canonical-arXiv lookup) via arXiv abstract pages.

### Papers resolved (verified author lists now present)

| # | Bibtex key | First author | Source verified |
|---|---|---|---|
| 01 | lu2025stateval | Yuchen Lu (+19) | arXiv 2510.09517 |
| 02 | nagarkar2026canllm | Crish Nagarkar (+2) | arXiv 2601.14479 |
| 03 | liu2025matheval | Tianqiao Liu (+5) | journal.hep.com.cn (Frontiers of Digital Education) |
| 06 | longjohn2025bayesian | Rachel Longjohn (+4) | arXiv 2511.10661 |
| 07 | reasonbench2025 | Nearchos Potamitis (+2) | arXiv 2512.07795 |
| 08 | brittlebench2026 | Angelika Romanou (+10) | arXiv 2603.13285 |
| 09 | wang2025icecream | Jin Du (+8) — actual first author | arXiv 2505.13770 |
| 10 | park2025judge | Yusuke Yamauchi (+2) — actual first author | arXiv 2506.13639 |
| 11 | fermieval2025 | Elliot L. Epstein (+3) | arXiv 2510.26995 |
| 12 | multianswer2026 | Yuhan Wang (+5) | arXiv 2602.07842 |
| 13 | mathfail2026 | Johan Boye, Birger Moell | arXiv 2502.11574 |
| 14 | judgment2025noise | Benjamin Feuer (+4) | arXiv 2509.20293 |
| 15 | fragility2025 | Andreas Hochlehnert (+5) | arXiv 2504.07086 (canonical title: "A Sober Look at Progress in Language Model Reasoning") |

**Surprises during resolution:**
- Paper 09 (`wang2025icecream`) actual first author is **Du**, not Wang.
  Bibtex key retained per task constraint (key stability); inline note added
  to the per-paper note's Authors field flagging the discrepancy.
- Paper 10 (`park2025judge`) actual first author is **Yamauchi**, not Park.
  Same treatment as Paper 09.
- Paper 15 was previously cited only via marktechpost.com summary. Canonical
  arXiv version (2504.07086) has a different title — the MarkTechPost
  framing "Statistically Fragile" is the article's editorial framing; the
  authors' own title is "A Sober Look at Progress in Language Model
  Reasoning: Pitfalls and Paths to Reproducibility". Both recorded in the
  per-paper note metadata; bibtex `title` uses the canonical version.
- Paper 13 (`mathfail2026`) submission year is **2025** (arXiv 2502 = Feb
  2025), but file was named with 2026. File name and bibtex key retained
  for stability; metadata Year field unchanged in this pass since it was
  not flagged TODO. Recommend a follow-up rename pass before publication.
- Paper 03 (MathEval) is **published in Frontiers of Digital Education**
  (a Springer journal), not just a generic Springer article. `journal`
  field added to bibtex.

### Papers still TODO

**0 / 14 remain unresolved.** All 14 items resolved within budget.

### Searches consumed

- Paper 03: 2 (1 web search + 1 fetch through journal.hep.com.cn after
  Springer DOI returned 303 redirects). On budget.
- Paper 15: 2 web searches (1 to find canonical arXiv ID, 1 to disambiguate
  authors via Hochlehnert/Bhatnagar query). On budget.
- Papers 01, 02, 06, 07, 08, 09, 10, 11, 12, 13, 14: 1 arXiv fetch each.
  Well under budget.

### Files modified

- `llm-stats-vault/40-literature/bibtex.bib` — full rewrite: replaced 13
  placeholder author lists with verified authors, repointed Paper 15 from
  @misc/marktechpost to @article/arXiv, added `journal` field to Paper 03,
  removed all TODO comments, updated header to reflect housekeeping pass.
- `llm-stats-vault/40-literature/papers/01-original-stateval-2025.md` —
  Authors line updated.
- `llm-stats-vault/40-literature/papers/02-original-can-llm-reasoning-2026.md` —
  Authors line updated.
- `llm-stats-vault/40-literature/papers/03-original-matheval-2025.md` —
  Authors line updated.
- `llm-stats-vault/40-literature/papers/06-new-longjohn-bayesian-eval-2025.md` —
  Authors line updated.
- `llm-stats-vault/40-literature/papers/07-new-reasonbench-2025.md` —
  Authors line updated.
- `llm-stats-vault/40-literature/papers/08-new-brittlebench-2026.md` —
  Authors line updated.
- `llm-stats-vault/40-literature/papers/09-new-ice-cream-causal-2025.md` —
  Authors line updated (with bibtex-key-mismatch note).
- `llm-stats-vault/40-literature/papers/10-new-llm-judge-empirical-2025.md` —
  Authors line updated (with bibtex-key-mismatch note).
- `llm-stats-vault/40-literature/papers/11-new-fermieval-2025.md` —
  Authors line updated.
- `llm-stats-vault/40-literature/papers/12-new-multi-answer-confidence-2026.md` —
  Authors line updated.
- `llm-stats-vault/40-literature/papers/13-new-math-reasoning-failures-2026.md` —
  Authors line updated.
- `llm-stats-vault/40-literature/papers/14-new-judgment-becomes-noise-2025.md` —
  Authors line updated.
- `llm-stats-vault/40-literature/papers/15-new-statistical-fragility-2025.md` —
  Authors line updated, arXiv ID + canonical title + URL updated, removed
  marktechpost-summary placeholder.

### Files NOT modified (per task scope constraints)

- `README.md` — still contains the now-stale "TODO author-list confirmations"
  section (lines 92–110). Out of scope (task: "Do not modify literature
  vault README, citation-map, or poster-citations files"). README needs a
  follow-up pass to remove that section.
- `citation-map.md`, `poster-citations.md` — same reason.

### Validation

- `bibtex.bib` entry count: **22** (5 originally-cited + 10 newly-discovered
  + 7 textbooks). Unchanged.
- `bibtex.bib` braces balanced: 182 open, 182 close.
- All 15 per-paper notes retain full template structure (Metadata,
  One-line summary, Key findings, How it grounds this project, Citation in
  poster, Citation in paper, Bibtex key, Project artifacts that cite this,
  Tags).
- No TODO markers remain in `papers/` or `bibtex.bib`.
