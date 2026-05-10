# Comprehensive Audit — 2026-05-01

Read-only Day 4 audit. No data, scripts, figures, or commits modified.
Source documents: CLAUDE.md, audit/* (Day 2, recompute_log, methodology_continuity,
limitations_disclosures, literature_comparison, rq_restructuring, aggregation_locus,
gemini_verification, personal_todo_status, deployment_report, website_discovery),
llm-stats-vault/00-home/research-narrative.md and current-priorities.md,
llm-stats-vault/40-literature/{README,citation-map,poster-citations,bibtex.bib},
capstone-website/{README,backend/main.py,backend/v2_routes.py,backend/static_data,
frontend/src/{App.jsx,components/KeyFindings.jsx,pages/{Limitations,Methodology,
PosterCompanion,References}.jsx,data/visualizations.js}}.

---

## Executive summary

- **Total findings: 33**
- **CRITICAL: 4** (deployed backend serving Phase 1A data; ece_comparison key
  mismatch; frontend Methodology page Claude-#1 narrative; frontend Limitations
  page B3 caveat preserved as if unresolved)
- **MAJOR: 14**
- **MINOR: 11**
- **INFO: 4**

**Top 5 priorities to fix before any user-facing work:**
1. **C1.A — Refresh `capstone-website/backend/static_data/`** with the post-Phase-1B/1C
   data files. The deployed Render backend is currently returning equal-weight
   accuracy (Claude 0.679 #1) and old robustness ranking; KeyFindings cards on
   the live site say "Claude wins" via the live API — directly contradicting
   the locked literature-derived narrative.
2. **C1.B — Fix `v2_routes.py` consistency-ECE field name.** Backend reads
   `sc.get("ece_comparison", {})` but Phase 1C canonical file stores
   `ece_comparison_full`. `/api/v2/rankings` and `/api/v2/calibration` will
   silently return empty consistency-ECE for any deployment that pulls the
   refreshed file.
3. **C4.A — Replace stale Methodology + Limitations narrative on the frontend.**
   Methodology page hard-codes "Claude 0.679 [0.655, 0.702]" and "Gemini 0.674"
   in Card 4; Limitations page L5 still describes B3 stratification as an open
   caveat — both contradict Phase 1C resolution.
4. **C5.A — Drop the `weight:'40%' / '15%'` percentage badges from RQS array
   (App.jsx:1870-1902).** rq_restructuring.md (Phase 1B) explicitly states
   percentage-on-percentage badges were dropped because the NMACR data-layer
   already encodes emphasis. The website still ships them.
5. **C7.A — Phase 1D (website updates) has not started.** All audit-document
   evidence points to 5+ frontend artifacts still on Phase 1A numbers/narrative.
   Until this is closed, the deployed site is materially inconsistent with
   research-narrative.md.

---

## Findings by category

### Category 1 — Numerical inconsistencies across artifacts

**[F1.01] 25% keyword-judge disagreement headline — consistent across canonical layer; out-of-date in deployed static_data**
Severity: CRITICAL
Category: Numerical inconsistencies
Finding: 274/1095 = 25.022% is the canonical headline. Verified in
`experiments/results_v2/keyword_vs_judge_agreement.json:pass_flip_assumption`
(`keyword_pass_judge_fail=274, n_compared=1095, kw_pass_judge_fail_pct=25.0228`).
research-narrative.md, recompute_log.md (implicit), rq_restructuring.md, and
limitations_disclosures.md all use 274/1095 = 25.0%. Frontend KeyFindings.jsx
fallback shows 25.0%; backend `/api/v2/headline_numbers` computes from the
same source. **However**, `capstone-website/backend/static_data/experiments/
results_v2/keyword_vs_judge_agreement.json` is byte-identical for this field
(verified — pass_flip block matches), so the live deployment is consistent on
this one number. Two doc-level glitches: (a) Methodology.jsx:151 says "274/1094"
instead of 274/1095 (off-by-one carry-over from Day 2 audit which used 1094);
(b) day2_audit_report.md [D-7] also says "274/1094" (legacy).
Evidence: experiments/results_v2/keyword_vs_judge_agreement.json:1; capstone-website/
frontend/src/pages/Methodology.jsx:151; audit/day2_audit_report.md:61.
Cross-reference: F1.07 (deployed data freshness)
Recommendation: Update Methodology.jsx:151 to 274/1095. day2_audit_report is
historical and can stay.

**[F1.02] α = 0.55 Krippendorff — fully consistent**
Severity: INFO
Category: Numerical inconsistencies
Finding: 0.5502 (95% CI [0.504, 0.595]) — consistent across
`experiments/results_v2/krippendorff_agreement.json` (canonical),
research-narrative.md ("0.55 [0.504, 0.595]"), rq_restructuring.md
("0.55 95% CI [0.504, 0.595]"), v2_routes.py `_alpha_interp` rules
(<0.667 → "questionable"), KeyFindings.jsx fallback ("α = 0.55 ·
questionable per Park 2025"). Deployed static_data has identical value.
Limitations.jsx caveats narrative consistent.
Evidence: experiments/results_v2/krippendorff_agreement.json:overall.assumption_compliance.
Cross-reference: none
Recommendation: No action needed.

**[F1.03] 46.9% vs 46.85% rounding inconsistency**
Severity: MINOR
Category: Numerical inconsistencies
Finding: 67/143 = 46.853%, which rounds to 46.9% under standard one-decimal
rounding (and to 46.85% at two decimals). Project documents inconsistently use
**46.9%** (research-narrative.md, rq_restructuring.md, citation-map, audit/
literature_comparison.md, audit/personal_todo_status.md, KeyFindings.jsx fallback,
visualizations.js subtitle, App.jsx, Methodology.jsx, PosterCompanion.jsx,
papers/09-new-ice-cream-causal-2025.md) vs **46.85%** (audit/deployment_report.md
twice). The backend computes `dom_pct = dom_n/dom_total = 0.4685` and frontend
KeyFindings runs `(d.dominant_failure_pct * 100).toFixed(1)` → "46.9". So the
LIVE site shows 46.9% via API; the deployment_report log captured the unrounded
0.4685 value.
Evidence: audit/deployment_report.md:13,41 ("46.85%"); KeyFindings.jsx:20
(`(d.dominant_failure_pct * 100).toFixed(1)`); experiments/results_v2/
error_taxonomy_v2.json:l1_totals (67 / 143).
Cross-reference: F1.07
Recommendation: No data-level action; deployment_report log can be updated to
use 46.9% to match all other surfaces. Pre-empt reviewer confusion.

**[F1.04] NMACR weights A=0.30 R=0.25 M=0.20 C=0.15 N=0.10 — partially propagated**
Severity: MAJOR
Category: Numerical inconsistencies
Finding: New literature-derived weights present in:
- scripts/recompute_nmacr.py NMACR_WEIGHTS (canonical authority)
- audit/recompute_log.md, audit/methodology_continuity.md,
  audit/rq_restructuring.md, audit/literature_comparison.md (full per-dim defense)
- llm-stats-vault/00-home/research-narrative.md §2 (full defense)
- llm-stats-vault/40-literature/citation-map.md (per-dim citations)
- experiments/results_v2/{bootstrap_ci.json, robustness_v2.json,
  nmacr_scores_v2.jsonl} (`weighting_scheme: literature_v1`)

Old equal weights (correctly preserved as historical context) in:
- audit/aggregation_locus.md (clearly labelled as Path A / Path B preserved-for-v1)

**Stale on the website:**
- capstone-website/frontend/src/App.jsx:1870-1902 still carries
  `weight:'40%' / '15%'` badges per RQ — but rq_restructuring.md explicitly
  states these badges were dropped in Phase 1B because the NMACR data-layer
  already encodes the emphasis.
- capstone-website/frontend/src/App.jsx:967-968 hardcodes
  "RQ1 PRIMARY (40%)... RQ2-5 SUPPORTING (15% each)" in copy.

Evidence: scripts/recompute_nmacr.py; audit/rq_restructuring.md:1-12
(the badge-drop rationale); capstone-website/frontend/src/App.jsx:1870-1902.
Cross-reference: F4.07 (PRIMARY/SUPPORTING badge drop), F5.14
Recommendation: Drop the `weight:'X%'` field from each RQS entry; collapse
copy at App.jsx:967 to "RQ1 PRIMARY: external-judge validation; RQ2-5 SUPPORTING".

**[F1.05] Per-model accuracy — new ordering present in canonical layer; old still ambient on deployed backend + frontend Methodology**
Severity: CRITICAL
Category: Numerical inconsistencies
Finding: New canonical ranking (gemini > claude > chatgpt > mistral > deepseek)
present in:
- experiments/results_v2/bootstrap_ci.json: gemini 0.7763, claude 0.7122,
  chatgpt 0.6913, mistral 0.6754, deepseek 0.6630
- audit/recompute_log.md "Per-model base aggregate — new (literature-derived)"
- llm-stats-vault/00-home/research-narrative.md (RQ4 mentions Mistral on
  robustness; accuracy ordering implicit via bootstrap_ci.json reference)

Old equal-weight ranking (claude > gemini > mistral > deepseek > chatgpt)
**still present on the deployed site path** because:
- capstone-website/backend/static_data/experiments/results_v2/bootstrap_ci.json
  has weighting_scheme=null, claude=0.6791, gemini=0.6736, chatgpt=0.6139,
  deepseek=0.6212, mistral=0.6323 — Phase 1A data.
- capstone-website/frontend/src/pages/Methodology.jsx:164-165 hardcodes
  "Claude 0.679 [0.655, 0.702] and Gemini 0.674 [0.647, 0.700]" → Phase 1A.
- capstone-website/frontend/src/pages/Limitations.jsx:26-27 hardcodes the
  same Phase 1A pair.
- capstone-website/frontend/src/pages/PosterCompanion.jsx — verify Phase 1B
  numbers (audit could not exhaustively confirm, flagged for triage).

The Render Dockerfile sets `ENV DATA_ROOT=/app/static_data`, so deployed
endpoints read from static_data, not from the canonical experiments/results_v2/
folder. KeyFindings on the live site fetches via `/api/v2/headline_numbers` →
backend reads static_data → returns Phase 1A bootstrap CIs and Phase 1A
rankings.
Evidence: capstone-website/backend/Dockerfile:8 (`ENV DATA_ROOT=/app/static_data`);
capstone-website/backend/static_data/experiments/results_v2/bootstrap_ci.json:
weighting_scheme=null, claude=0.6791; capstone-website/frontend/src/pages/
Methodology.jsx:164-165.
Cross-reference: F1.04, F1.06, F1.07, F4.01, F8.01
Recommendation: HIGHEST PRIORITY. Copy refreshed canonical files into
backend/static_data/experiments/results_v2/{bootstrap_ci.json,
robustness_v2.json, calibration.json, error_taxonomy_v2.json,
keyword_vs_judge_agreement.json, krippendorff_agreement.json,
self_consistency_calibration.json}; verify Render redeploys; then update
hardcoded Methodology.jsx + Limitations.jsx + PosterCompanion.jsx prose.

**[F1.06] Robustness ranking — new ordering present canonically; old in deployed static_data**
Severity: CRITICAL
Category: Numerical inconsistencies
Finding: New canonical robustness ranking (mistral > chatgpt > claude >
deepseek > gemini): mistral Δ=0.007, chatgpt Δ=0.0114, claude Δ=0.0401,
deepseek Δ=0.0423, gemini Δ=0.0568. Verified in `experiments/results_v2/
robustness_v2.json:ranking`. Audit recompute_log.md and research-narrative.md
RQ4 reflect this ordering.

Old ranking (chatgpt > deepseek > mistral > gemini > claude) — equal-weight
era — present in:
- capstone-website/backend/static_data/experiments/results_v2/robustness_v2.json
  (chatgpt Δ=−0.0007, deepseek Δ=0.0006, mistral Δ=0.0135, gemini Δ=0.016,
  claude Δ=0.0194) — Phase 1A.
- audit/limitations_disclosures.md:27 "ChatGPT Δ = −0.0007 and DeepSeek
  Δ = +0.0006" — this prose is now wrong under the new weighting.
- capstone-website/frontend/src/pages/Limitations.jsx:27-28 ("ChatGPT
  Δ = −0.0007 and DeepSeek Δ = +0.0006") — Phase 1A.
- audit/personal_todo_status.md item 8 evidence ("ChatGPT Δ=−0.0007,
  DeepSeek Δ=+0.0006, claude Δ=0.0194, mistral Δ=+0.0135, gemini Δ=0.016") —
  Phase 1A.
- audit/deployment_report.md:18 same Phase 1A ranking.

Evidence: experiments/results_v2/robustness_v2.json:ranking[5];
capstone-website/backend/static_data/experiments/results_v2/robustness_v2.json
(ranking shows chatgpt #1); audit/limitations_disclosures.md:27.
Cross-reference: F1.05, F1.07, F4.05
Recommendation: Same fix as F1.05 (refresh static_data). Then update prose
in audit/limitations_disclosures.md (c) to use the new robustness numbers
(mistral Δ=0.007, chatgpt Δ=0.0114) when describing the noise-equivalent band.

**[F1.07] Phase 1B/1C data NOT present in deployed static_data — meta finding**
Severity: CRITICAL
Category: Numerical inconsistencies
Finding: Per Dockerfile `ENV DATA_ROOT=/app/static_data`, Render serves data
from `capstone-website/backend/static_data/`. Comparison reveals:
- bootstrap_ci.json: deployed lacks `weighting_scheme` field (it's null);
  canonical has `literature_v1`. Accuracy means ARE old values (claude 0.6791,
  not 0.7122). Top-2 are claude/gemini (old) not gemini/claude (new).
- robustness_v2.json: deployed has Phase 1A ranking; canonical has Phase 1B
  ranking. Deployed lacks `per_dim_delta` block (Layer 2). New `weighting_scheme`
  field absent.
- calibration.json: deployed lacks `accuracy_calibration_correlation` and
  `formatting_failure_rate_per_model` (both are Phase 1B additions).
- self_consistency_calibration.json: deployed has Phase 1A B3 stratified
  (n_tasks=30, ece_comparison key uses {keyword_ece, consistency_ece,
  direction_flipped}); canonical Phase 1C has n_tasks=161, key
  `ece_comparison_full` with verbalized_ece/consistency_ece_stratified/
  consistency_ece_full triples.
- per_dim_calibration.json: NOT present in static_data — Phase 1B addition
  not deployed.
- nmacr_scores_v2.jsonl: NOT present in static_data — single-source-of-truth
  for literature-weighted aggregate is unreachable from the live API.

The audit/deployment_report.md was generated 2026-05-01 16:51 (before Phase 1B/1C
output were finalised — recompute_log.md updated 2026-05-02 13:26 timestamp).
Phase 1D (website updates) has not started.
Evidence: capstone-website/backend/Dockerfile:8; static_data/experiments/
results_v2/* mtimes (Apr 28 14:36 vs canonical May 1/2); recompute_log.md
"Files modified" + "Files created" sections.
Cross-reference: F1.04, F1.05, F1.06, F1.10, F2.05, F2.06, F2.07, F7.01,
F7.05, F8.01, F8.02
Recommendation: Refresh static_data before any external presentation. Add
nmacr_scores_v2.jsonl + per_dim_calibration.json. Verify v2_routes.py reads
the consistency-ECE under the right key after refresh (see F1.10).

**[F1.08] Calibration ECE three layers — partially documented; B3 stratified archive note inconsistent**
Severity: MAJOR
Category: Numerical inconsistencies
Finding: Three layers identified by audit context:
- Verbalized: per `experiments/results_v2/calibration.json` ECEs
  claude=0.0666, chatgpt=0.0626, gemini=0.0973, deepseek=0.1795,
  mistral=0.0840 — fully populated.
- Stratified-B3: archived to `llm-stats-vault/90-archive/phase_1c_superseded/
  self_consistency_calibration_b3_stratified.json` and
  `…/self_consistency_runs_b3_stratified.jsonl`. Provenance README present.
- Phase 1C full: canonical at `experiments/results_v2/
  self_consistency_calibration.json` (n_tasks=161, ECE_full claude=0.7342,
  chatgpt=0.7214, gemini=0.6178, deepseek=0.7261, mistral=0.6632).
  `_supersedes` field present, `gemini_finding` block present.

All three layers documented in audit/recompute_log.md "Phase 1C" section and
in research-narrative.md RQ5 table. Limitations.jsx (frontend) STILL describes
B3 as an open caveat (L5 entry "B3 stratification caveat" with body
"the magnitude is not directly comparable until we re-run B3 on a uniform
random sample") — directly contradicts Phase 1C resolution. Phase 1C is
canonical on the website only via /api/v2/calibration `consistency` block —
but the static_data version of self_consistency_calibration.json is the OLD
B3 stratified file (n_tasks=30) per F1.07.
Evidence: experiments/results_v2/self_consistency_calibration.json
(n_tasks=161, ece_comparison_full block); capstone-website/backend/static_data/
experiments/results_v2/self_consistency_calibration.json (n_tasks=30,
ece_comparison key); capstone-website/frontend/src/pages/Limitations.jsx:43-51.
Cross-reference: F1.07, F1.10, F4.02, F6.03, F6.05, F8.02
Recommendation: Refresh static_data (F1.07); rewrite Limitations.jsx L5
caveat per audit/limitations_disclosures.md (e) "RESOLVED via Phase 1C".

**[F1.09] formatting_failure_rate per model — present in canonical calibration.json but NOT exposed via backend**
Severity: MAJOR
Category: Numerical inconsistencies
Finding: `calibration.json:formatting_failure_rate_per_model` has the values
specified in audit context: chatgpt 2.44%, claude 0.0%, deepseek 2.44%,
gemini 0.41%, mistral 2.03%. Verified canonical. v2_routes.py `/api/v2/calibration`
returns `verbalized.per_model = verb` (the raw dict) — so the field IS
included if a client knows to parse it from the per_model object, but it is
NOT a top-level item and not surfaced by the typed Pydantic models. Frontend
has no consumer of `formatting_failure_rate`. Audit context calls for
exposure via backend.
Evidence: experiments/results_v2/calibration.json:formatting_failure_rate_per_model;
capstone-website/backend/v2_routes.py:392-417 (`/api/v2/calibration`);
grep frontend src for `formatting_failure_rate` returns 0 hits.
Cross-reference: F1.07 (static_data missing this field entirely),
F8.04 (visualizations.js)
Recommendation: After F1.07 refresh, add a top-level `formatting_failure_rate`
key to `/api/v2/calibration` response (or expose via `/api/v2/headline_numbers`).
Surface in a frontend KeyFindings card or in the Methodology page.

**[F1.10] ece_comparison key mismatch between canonical Phase 1C file and v2_routes.py reader**
Severity: CRITICAL
Category: Numerical inconsistencies
Finding: canonical `experiments/results_v2/self_consistency_calibration.json`
stores the three-method ECE table under key **`ece_comparison_full`** (verified
via direct read). `capstone-website/backend/v2_routes.py:314` reads
`sc.get("ece_comparison", {})` and `:412` reads `cons.get("ece_comparison", {})`.
Once static_data is refreshed (F1.07) with the canonical Phase 1C file, both
endpoints (`/api/v2/rankings`, `/api/v2/calibration`) will silently return an
empty `consistency_ece` block. Frontend code that consumes this will degrade
to whatever fallback exists. The current static_data version uses the OLD
key `ece_comparison`, which is why the bug isn't visible today — but it
will appear the moment Phase 1C data is deployed.
Evidence: experiments/results_v2/self_consistency_calibration.json keys list;
capstone-website/backend/v2_routes.py:314,412.
Cross-reference: F1.07, F1.08, F8.01
Recommendation: Edit v2_routes.py:314 + :412 to read
`sc.get("ece_comparison_full") or sc.get("ece_comparison", {})` (preserves
backward compat). Coordinate with F1.07 refresh.

**[F1.11] Run counts (1230 base, 2365 perturbations, 2415 self-consistency, 1095 keyword-judge disagreement eligible, 143 failure analysis) — consistent**
Severity: INFO
Category: Numerical inconsistencies
Finding: All five canonical counts verified:
- 1230 base runs: experiments/results_v1/runs.jsonl (Day 2 audit row)
- 2365 perturbation runs: robustness_v2.json:n_perturbations (canonical
  AND deployed match)
- 2415 self-consistency: 161 tasks × 5 models × 3 reruns = 2415 (recompute_log.md
  "Cost: $11.688... Coverage: 2,415 calls")
- 1095 keyword-judge disagreement eligible: keyword_vs_judge_agreement.json:n_compared = 1095
- 143 failure-analysis classified: error_taxonomy_v2.json:n_failures_classified

[Phase 1.8 update 2026-05-04 — historical reference only.] The 1230
base count in this audit row reflected the pre-deprecation scope:
855 truly-base runs co-mingled with 375 v1-perturbation rows. After
v1 deprecation (recompute_log §"Phase 1.8"), the canonical scope is
855 base + 2,365 perturbation = 3,220 total scored runs; 750 base +
2,100 perturbation = 2,850 keyword-judge eligible. This audit row is
preserved as a historical snapshot — the up-to-date counts live in
recompute_log §"Phase 1.8" and rq_ieee_formulations.md.

Day 2 audit and Methodology.jsx use 1094 (off-by-one carry-over from earlier
read). research-narrative.md correctly uses 1095 in the RQ1 headline.
Cross-reference: F1.01
Evidence: cited above.
Recommendation: Reconcile day2_audit_report.md and Methodology.jsx to 1095.

### Category 2 — Partial analyses with unclear scope

**[F2.01] Keyword-judge disagreement 135-task exclusion documented**
Severity: INFO
Category: Partial analyses
Finding: 135 ≈ 1230 − 1095 = 135. audit/limitations_disclosures.md does NOT
contain an entry on this (only d) talks about the 25% headline). The 135
exclusion is described in day2_audit_report.md [P-6]: 21 task_ids × 5 models
≈ 105 minimum + v1-perturbation overlap. research-narrative.md RQ1 headline
quotes 274/1095 directly without explanation. KeyFindings.jsx fallback
shows just "274/1095 runs" without the 135 caveat.
Evidence: audit/limitations_disclosures.md (d) — no exclusion math; audit/
day2_audit_report.md:171 [P-6].
Cross-reference: F6.01
Recommendation: Add a one-sentence note to limitations_disclosures.md (d):
"Of 1230 base runs, 135 (CONCEPTUAL/MINIMAX/BAYES_RISK) are excluded by
design — these task families have empty `required_assumption_checks`, so
keyword-vs-judge agreement is trivially 1.0 and would inflate the headline."

**[F2.02] Phase 1C CONCEPTUAL exclusion (10 tasks) — disclosure present**
Severity: INFO
Category: Partial analyses
Finding: limitations_disclosures.md (f) explicitly disclosed; research-narrative.md
RQ5 "Coverage limitation" section explicitly disclosed. self_consistency_calibration.json
canonical has `n_excluded_conceptual=10` field. RQ5 findings include the
caveat in the headline (10 of 171 excluded).
Evidence: audit/limitations_disclosures.md:74-82; experiments/results_v2/
self_consistency_calibration.json:n_excluded_conceptual.
Cross-reference: F6.02
Recommendation: None — well documented.

**[F2.03] HALLUCINATION = 0 disclosure present; L1 taxonomy still lists it**
Severity: MINOR
Category: Partial analyses
Finding: limitations_disclosures.md (a) provides the "real finding vs single-judge
limitation" framing. research-narrative.md "Honest disclosures" section repeats
it. Frontend Limitations.jsx L1 carries the disclosure with appropriate nuance
("partly methodology artifact and partly a property"). The L1 taxonomy
definition (in error_taxonomy_v2.json:l1_to_l2_mapping) still lists
HALLUCINATION as a valid category but with 0 records — appropriate.
Evidence: audit/limitations_disclosures.md:8-22; capstone-website/frontend/src/
pages/Limitations.jsx:7-14.
Cross-reference: F6.04
Recommendation: None.

**[F2.04] Empty high-confidence bucket (verbalized) — Gemini specifically zero**
Severity: MINOR
Category: Partial analyses
Finding: All 5 models have `per_bucket.high.n=0` in calibration.json
(verified). Gemini-specifically: per audit context Gemini has 0 verbalized
signals. Gemini's per_bucket.unstated.n=119, low.n=9, medium.n=118 — totals
246; high=0. So Gemini still falls into the {low, medium, unstated} buckets
even with no high-confidence claims. The "Gemini 0 verbalized signals"
phrasing in research-narrative.md and limitations_disclosures.md (b) is
actually about Gemini's confidence-extraction column being all-unstated for
its per_dim_calibration → accuracy_calibration_correlation block. accuracy_calibration_correlation
in calibration.json has only 4 keys (claude, chatgpt, deepseek, mistral) —
gemini absent → confirms exclusion. The 3-bucket ECE caveat in
limitations_disclosures.md (b) is sound.
Evidence: experiments/results_v2/calibration.json:gemini.per_bucket;
calibration.json:accuracy_calibration_correlation (4 keys, no gemini).
Cross-reference: F6.05
Recommendation: None — disclosure matches data.

**[F2.05] Per-dimension robustness (RQ4 Layer 2) — present canonically; not deployed**
Severity: MAJOR
Category: Partial analyses
Finding: `per_dim_delta` block exists in canonical robustness_v2.json with
all 5 models × 5 dimensions. Figure `report_materials/figures/a4b_per_dim_robustness.png`
present (130KB, 2026-05-01). However: (a) static_data version lacks
`per_dim_delta` (F1.07); (b) figure NOT mirrored in
`capstone-website/frontend/public/visualizations/png/v2/` — only 15 figures
present, a4b absent; (c) no entry in visualizations.js manifest.
Evidence: experiments/results_v2/robustness_v2.json:per_dim_delta keys
(claude,chatgpt,gemini,deepseek,mistral) all present;
report_materials/figures/a4b_per_dim_robustness.png 139829 bytes;
capstone-website/frontend/public/visualizations/png/v2/ 15 entries (no a4b).
Cross-reference: F1.07, F8.03, F8.04
Recommendation: Copy a4b PNG to frontend/public/visualizations/png/v2/;
add manifest entry; surface in Robustness category. Refresh static_data.

**[F2.06] Per-dimension calibration (RQ5 Layer 5) — present canonically; not deployed**
Severity: MAJOR
Category: Partial analyses
Finding: `experiments/results_v2/per_dim_calibration.json` exists
(buckets + per_dim_ece). Figure `report_materials/figures/a5b_per_dim_calibration.png`
present (131KB). Same gap as F2.05: not in static_data (per_dim_calibration.json
not in deployed dir at all), not mirrored in frontend public dir, not in
visualizations.js manifest, no /api/v2/* endpoint exposes it.
Evidence: experiments/results_v2/per_dim_calibration.json (3 keys: _methodology_citation,
buckets, per_dim_ece); report_materials/figures/a5b_per_dim_calibration.png;
capstone-website/backend/static_data/experiments/results_v2/ (no per_dim_calibration.json).
Cross-reference: F1.07, F8.03, F8.04
Recommendation: Add to static_data. Add backend endpoint or extend
/api/v2/calibration with `per_dim` block. Mirror PNG to frontend; add
visualizations.js entry.

**[F2.07] Accuracy-calibration correlation (RQ5 Layer 4) — present canonically; partially deployed**
Severity: MAJOR
Category: Partial analyses
Finding: `accuracy_calibration_correlation` and `accuracy_calibration_correlation_note`
appended to canonical calibration.json. Values claude 0.4905, chatgpt 0.3712,
deepseek 0.3473, mistral 0.4762; gemini absent (excluded — all responses
unstated). Audit context says "r ∈ [0.35, 0.49]" — verified.
Static_data calibration.json LACKS this field entirely. Backend
`/api/v2/calibration` returns `verbalized.per_model` which would include the
correlation if static_data were refreshed; but no consumer parses it on
the frontend.
Evidence: experiments/results_v2/calibration.json:accuracy_calibration_correlation;
capstone-website/backend/static_data/experiments/results_v2/calibration.json (only 5 model keys).
Cross-reference: F1.07, F1.09, F8.04
Recommendation: After static_data refresh, surface r values + gemini exclusion
on a frontend RQ5 card.

**[F2.08] Length-correlation gemini disclosure**
Severity: INFO
Category: Partial analyses
Finding: audit/gemini_verification.md (12.8KB) is a complete 6-diagnostic
audit. limitations_disclosures.md (g) has a 9-line summary. research-narrative.md
"Honest disclosures" includes the length-correlation caveat. Verdict in
gemini_verification.md is "PROCEED (with QUALIFY)". Surfaced in vault and
audit. Frontend has no Limitations entry on length-correlation —
limitations_disclosures.md exists but Limitations.jsx still has only 5
caveats and length-correlation isn't one of them.
Evidence: audit/gemini_verification.md:1-289; audit/limitations_disclosures.md:84-95;
capstone-website/frontend/src/pages/Limitations.jsx CAVEATS array (5 entries,
no length-correlation).
Cross-reference: F6.08
Recommendation: Add a 6th caveat to Limitations.jsx body for length-correlation
(short body + cite gemini_verification.md).

**[F2.09] Tolerance sensitivity — ranking instability under loose tolerance**
Severity: MAJOR
Category: Partial analyses
Finding: Tolerance sensitivity sweep (1,180 numeric-bearing runs across
three tolerance levels: tight 0.005/0.025, default 0.010/0.050, loose
0.020/0.100) shows `ranking_stable_across_levels=false`. Gemini swings
from worst at tight tolerance to mid at loose tolerance — model ranking
is not stable across the chosen tolerance band. The default tolerance
(0.010/0.050) was selected for methodology consistency, but the
instability deserves a sensitivity disclosure. Frontend status:
tolerance_sensitivity figure exists in report_materials/figures/ but is
NOT surfaced on the website (intentionally paper-only per discovery
audit CL-D2). 50 runs unscored across all tolerance levels because
CONCEPTUAL tasks have no numeric_targets — denominator 1180 = 1230 − 50.
Evidence: experiments/results_v2/tolerance_sensitivity.json (canonical);
audit/day2_audit_report.md [D-8] (original analysis, archived in
llm-stats-vault/90-archive/audit_history/).
Cross-reference: F6.* (limitations_disclosures.md candidate)
Recommendation: Surface in IEEE paper appendix as a methodology
robustness disclosure. Optionally add a one-line caveat to website
Limitations page about tolerance choice. Do NOT mirror the figure to
the frontend — methodology-appendix scope, not headline.

### Category 3 — Broken cross-references

**[F3.01] sessions/2026-04-30-day1-poster-sprint.md and sessions/2026-05-01-day3-literature-vault.md moved to 90-archive/**
Severity: MAJOR
Category: Broken cross-references
Finding: Both files now live at `llm-stats-vault/90-archive/`, NOT
`llm-stats-vault/sessions/`. Stale references at:
- audit/personal_todo_status.md:97
  ("see `llm-stats-vault/sessions/2026-04-30-day1-poster-sprint.md` decision 3")
- audit/day2_audit_report.md:7 ("Day-1 context sourced from
  `llm-stats-vault/sessions/2026-04-30-day1-poster-sprint.md`")

90-archive/README.md and 90-archive/2026-04-30-day1-poster-sprint.md (line 59,
self-reference) carry the new location. .obsidian/workspace.json correctly
references the 90-archive/ paths.
Evidence: ls llm-stats-vault/sessions/ does not contain either file (verified);
ls llm-stats-vault/90-archive/ contains both.
Cross-reference: none
Recommendation: Update audit/personal_todo_status.md:97 and audit/day2_audit_report.md:7
to use `llm-stats-vault/90-archive/...`.

**[F3.02] rq_reweighting.md → rq_restructuring.md rename**
Severity: MAJOR
Category: Broken cross-references
Finding: File renamed Phase 1B (citation-map.md:69 explicitly notes this).
Stale references at:
- audit/personal_todo_status.md:26, 27, 192, 220, 237, 280, 293
  (7 occurrences of `audit/rq_reweighting.md`)
- audit/website_discovery.md:8, 102, 110

Updated correctly at: audit/methodology_continuity.md (uses new name),
audit/literature_comparison.md (uses new name), llm-stats-vault/40-literature/citation-map.md
(notes rename), llm-stats-vault/00-home/research-narrative.md.
Evidence: ls audit/ shows rq_restructuring.md present, rq_reweighting.md absent.
Cross-reference: none
Recommendation: Replace all rq_reweighting.md references in personal_todo_status.md
and website_discovery.md with rq_restructuring.md.

**[F3.03] vault citation-map cross-refs — all paths verifiable**
Severity: INFO
Category: Broken cross-references
Finding: Spot-checked the "By script" entries in citation-map.md
(scripts/bootstrap_ci.py, three_rankings_figure.py, generate_perturbations_full.py,
score_perturbations.py, robustness_analysis.py, error_taxonomy.py,
keyword_vs_judge_agreement.py, krippendorff_agreement.py, calibration_analysis.py,
self_consistency_proxy.py, evaluation/llm_judge_rubric.py, llm_runner/run_all_tasks.py,
llm_runner/prompt_builder.py, recompute_nmacr.py, recompute_downstream.py,
self_consistency_full.py, plot_self_consistency_calibration.py) — all 17 paths
present in scripts/ and evaluation/.
Evidence: ls -la /Users/albertsimonyan/Desktop/capstone-llm-stats/scripts/ (all
listed scripts present including new recompute_nmacr.py, recompute_downstream.py,
self_consistency_full.py, plot_self_consistency_calibration.py).
Cross-reference: none
Recommendation: None.

**[F3.04] /api/v2/* source-data file existence**
Severity: MAJOR
Category: Broken cross-references
Finding: v2_routes.V2_FILES paths checked against canonical
experiments/results_v2/ + data/synthetic/:
- agreement_keyword_judge → keyword_vs_judge_agreement.json ✓
- krippendorff → krippendorff_agreement.json ✓
- calibration_verbalized → calibration.json ✓
- calibration_consistency → self_consistency_calibration.json ✓
- robustness → robustness_v2.json ✓
- bootstrap_ci → bootstrap_ci.json ✓
- error_taxonomy → error_taxonomy_v2.json ✓
- judge_dimension_means → judge_dimension_means.json ✓
- tolerance_sensitivity → tolerance_sensitivity.json ✓
- perturbations_all → data/synthetic/perturbations_all.json ✓ (473)

All 10 source files present at canonical paths. **However** the live deployment
reads from static_data — see F1.07 for the data-freshness gap. v2_routes.py
WOULD return 200 + correct payloads if pointed at the canonical dir.
Evidence: ls experiments/results_v2/ (all 10 listed); ls data/synthetic/perturbations_all.json (473).
Cross-reference: F1.07
Recommendation: None for path resolution; see F1.07 for the freshness fix.

**[F3.05] Frontend visualizations.js → public/visualizations/png/v2/ existence**
Severity: MAJOR
Category: Broken cross-references
Finding: visualizations.js declares 15 PNG entries. ls of public/visualizations/png/v2/
shows 15 entries — all referenced PNGs exist. **However** F8.03 finds 5 of
those 15 are byte-different from the canonical report_materials/figures/
copies (a2_accuracy_by_category, a3_failure_heatmap, a6_aggregate_ranking,
self_consistency_calibration, three_rankings) — re-renders that didn't
propagate. a4b_per_dim_robustness and a5b_per_dim_calibration (Phase 1B
new figures) are NOT in the manifest or the public dir.
Evidence: cmp comparison output (5 DIFF, 10 MATCH).
Cross-reference: F2.05, F2.06, F8.03, F8.04
Recommendation: Re-mirror the 5 stale PNGs from report_materials/figures/.
Add a4b + a5b PNGs and visualizations.js entries.

**[F3.06] Audit doc cross-refs — all referenced files exist**
Severity: INFO
Category: Broken cross-references
Finding: methodology_continuity.md references research-narrative.md (✓)
and recompute_log.md (✓). limitations_disclosures.md references
phase_1c_superseded/ (✓). recompute_log.md references aggregation_locus.md (✓),
research-narrative.md (✓), phase_1c_superseded/{*}.json + .jsonl (✓ both).
All checked paths exist.
Evidence: ls 90-archive/phase_1c_superseded/ shows both archived files +
README.md.
Cross-reference: none
Recommendation: None.

### Category 4 — Stale narrative anchors

**[F4.01] "Claude wins accuracy" — present in deployed data path; absent in audit + vault**
Severity: CRITICAL
Category: Stale narrative anchors
Finding: rq_restructuring.md:141 explicitly says "Abstract leads with
'judge-validation methodology' not 'Claude wins'" — Phase 1B narrative shift.
research-narrative.md positions RQ1 as PRIMARY methodology, RQ2-5 as
SUPPORTING. **However**, on the deployed/frontend layer:
- KeyFindings.jsx fallback static text (line 12) still says "Top 2 tied:
  Claude and Gemini" — but the build_cards function reads `acc[0]`/`acc[1]`
  from `/api/v2/headline_numbers` so when refreshed it will read gemini #1,
  claude #2 (correct under new weights). On the LIVE site (static_data
  Phase 1A), accuracy[0]=claude — so the rendered card today shows Claude #1.
- Methodology.jsx:164-165 hardcodes "Claude 0.679 [0.655, 0.702] and Gemini
  0.674 [0.647, 0.700]" — Phase 1A.
- Limitations.jsx:26-28 same pair, Phase 1A.

Evidence: capstone-website/frontend/src/pages/Methodology.jsx:164-165;
capstone-website/frontend/src/pages/Limitations.jsx:26-28; capstone-website/
frontend/src/components/KeyFindings.jsx:12.
Cross-reference: F1.05, F1.07, F7.01
Recommendation: Refresh static_data + replace hardcoded numbers with new
ranking (Gemini 0.7763 [0.7527, 0.7992] / Claude 0.7122 [0.6887, 0.7360]).

**[F4.02] B3 stratified caveat language — partial; frontend stale**
Severity: CRITICAL
Category: Stale narrative anchors
Finding: limitations_disclosures.md (e) titled "RESOLVED via Phase 1C" —
correct language. research-narrative.md §6 Honest disclosures bullet
"Self-consistency caveat — RESOLVED via Phase 1C" — correct. Frontend
Limitations.jsx:43-51 STILL says "the magnitude is not directly comparable
until we re-run B3 on a uniform random sample" — describing B3 as an open
caveat. Frontend visualizations.js:130 self-consistency entry titled
"Self-Consistency Calibration (B3 proxy)" with caption "B3 proxy" —
contradicts the canonical full-coverage replacement.
Evidence: audit/limitations_disclosures.md:64-72; capstone-website/frontend/
src/pages/Limitations.jsx:44-51; capstone-website/frontend/src/data/
visualizations.js:130-134.
Cross-reference: F1.08, F6.03, F8.04
Recommendation: Replace Limitations.jsx L5 entry per limitations_disclosures.md
(e) text. Update visualizations.js self_consistency entry: title "Self-Consistency
Calibration (Phase 1C full)" + caption update.

**[F4.03] "Hedge-heavy contrast with FermiEval" old framing — partially updated**
Severity: MAJOR
Category: Stale narrative anchors
Finding: research-narrative.md RQ5 now reads "method-dependent — verbalized
hedges, consistency overconfident" with both ECE tables — correct new framing.
methodology_continuity.md:18 still reads "Calibration concerns are raised by
Nagarkar (2026) and contrast with FermiEval's (2025) overconfidence finding —
our Bayesian-task setting produces hedge-heavy behaviour instead." This is
now half-true: under verbalized extraction yes, but consistency extraction
shows overconfidence (matching FermiEval). The continuity statement should
be updated.
poster-citations.md:78-81 RQ5 cluster still reads "Bayesian benchmark surfaces
a hedge-heavy default" — old framing.
Evidence: audit/methodology_continuity.md:14-19; llm-stats-vault/40-literature/
poster-citations.md:78-81.
Cross-reference: F4.06
Recommendation: Update methodology_continuity.md and poster-citations.md to
the new "method-dependent" framing.

**[F4.04] Equal-weight NMACR ("20% each") — historical-only references**
Severity: INFO
Category: Stale narrative anchors
Finding: audit/aggregation_locus.md correctly uses 0.20 each but frames it
as "Path A / Path B preserved for v1 reproducibility, NEW wrapper script
recompute_nmacr.py applies literature-derived weights." CLAUDE.md still has
`WEIGHTS = N=0.20, M=0.20, A=0.20, C=0.20, R=0.20` but is documenting
runtime scoring (Paths A/B) which intentionally remain at equal weights.
This is consistent. No remaining stale equal-weight claims found in
narrative-bearing docs.
Evidence: audit/aggregation_locus.md:38-48; CLAUDE.md "Scoring" section.
Cross-reference: none
Recommendation: None — design is consistent ("data-layer recompute, runtime
unchanged").

**[F4.05] Old robustness ranking on the deployment layer**
Severity: CRITICAL (already counted as F1.06)
Category: Stale narrative anchors
Finding: see F1.06.

**[F4.06] "Top-2 tied claude vs gemini" — partially correct under new weights**
Severity: MAJOR
Category: Stale narrative anchors
Finding: Under canonical Phase 1B weights, top-2 are still gemini (0.7763
[0.7527, 0.7992]) and claude (0.7122 [0.6887, 0.7360]). The CIs no longer
overlap (claude_upper=0.7360 < gemini_lower=0.7527). So the "Top-2 tied"
claim is FALSE under new weights — they are now separable (a Δ ≈ 0.064 with
non-overlapping CIs). But:
- KeyFindings.jsx:42-46 dynamically computes overlap from API data — when
  refreshed, will correctly say "Separable" (or whatever the new logic
  returns). Currently shows "Top-2 tied" because static_data is Phase 1A.
- Methodology.jsx:164-167 hardcodes overlap claim ("Top-2 accuracy ... overlap
  — not statistically separable").
- Limitations.jsx:26-28 same.
- audit/personal_todo_status.md item 11 evidence quotes Phase 1A Top-2 tied.
- audit/limitations_disclosures.md (c) titled "Top-2 not statistically
  separable" — under new weights this is no longer true for accuracy
  (still true for robustness top-2 mistral/chatgpt: Δ=0.007 vs 0.0114,
  CI not in audit context but likely overlapping at SE≈0.012).

Evidence: experiments/results_v2/bootstrap_ci.json (gemini CI [0.7527, 0.7992],
claude CI [0.6887, 0.7360] — DO NOT overlap).
Cross-reference: F1.05, F1.06, F1.07, F4.01
Recommendation: Critical — the entire "Top-2 tied" frame is false under new
weights for accuracy. Update limitations_disclosures.md (c) to scope this to
robustness Top-2 only (mistral/chatgpt). Update Methodology.jsx + Limitations.jsx.
Update KeyFindings static fallback.

**[F4.07] PRIMARY · 40% / SUPPORTING · 15% RQ-weight badges — should be dropped per Phase 1B**
Severity: MAJOR
Category: Stale narrative anchors
Finding: audit/rq_restructuring.md:1-12 explicitly says "Tier badges are
**PRIMARY** vs **SUPPORTING** only — explicit percentage badges dropped
because the NMACR weighting scheme already encodes the relative emphasis at
the data layer (A=0.30, R=0.25, M=0.20, C=0.15, N=0.10) and percentage-on-
percentage labels confused readers in Phase 1A review." Frontend
App.jsx:1870-1902 STILL ships RQ entries with `weight:'40%' / '15%'`.
App.jsx:967-968 hardcodes "RQ1 PRIMARY (40%)... RQ2-5 SUPPORTING (15% each)"
in copy. References.jsx and other pages: not checked exhaustively but
search returned no other 40%/15% string matches.
Evidence: audit/rq_restructuring.md:1-12; capstone-website/frontend/src/
App.jsx:1870, 1878, 1886, 1894, 1902, 967-968.
Cross-reference: F1.04, F5.14, F7.01
Recommendation: Drop the `weight` field from each RQ entry; rewrite App.jsx:967
copy to drop "(40%)" and "(15% each)".

### Category 5 — Professor's 15 critique points

For each: ✅ FULLY DONE / ⚠️ PARTIAL / ❌ NOT ADDRESSED / 🚫 OUT OF SCOPE

| # | Item | Status | Primary artefact |
|---|------|--------|-------------------|
| 1 | React native mobile | 🚫 OUT OF SCOPE | — |
| 2 | Version consistency / no inconsistencies in updates/release | ⚠️ PARTIAL | static_data freshness gap (F1.07); B3-vs-Phase-1C language gap (F1.08, F4.02) |
| 3 | Concurrent users prevent crashes | 🚫 OUT OF SCOPE (hardening shipped) | capstone-website/backend/user_study.py |
| 4 | Baseline vs ground truth | ✅ FULLY DONE | audit/methodology_continuity.md, audit/literature_comparison.md row "Ground-truth source", audit/day2_audit_report.md [P-1] |
| 5 | Reasoning is weak | ⚠️ PARTIAL | judge rubric exists; per-model RQ ranking column not yet on frontend (F2.08-adjacent) |
| 6 | Short answer not supporting reasoning | ⚠️ PARTIAL | reasoning_completeness dim added; not surfaced as a frontend headline |
| 7 | Prompt variation, AI #6 for non-bias | ✅ FULLY DONE | evaluation/llm_judge_rubric.py:38 (Llama 3.3 70B); data/synthetic/perturbations_all.json (473) |
| 8 | Variation rankings | ⚠️ PARTIAL | three_rankings.png + bootstrap_ci.json on canonical; figure on frontend is OLD render (F8.03); under new weights claim "Top-2 tied" is false (F4.06) |
| 9 | Error taxonomy by LLMs | ⚠️ PARTIAL | error_taxonomy_v2.json + sunburst PNG present on frontend; HALLUCINATION=0 disclosure present (F2.03); per-model L1 stacked-bar figure NOT generated |
| 10 | Legend for fail type and task type | ✅ FULLY DONE | a1_failure_by_tasktype.png, a3_failure_heatmap.png, error_taxonomy_hierarchical.png |
| 11 | Ranking for aggregate scores | ✅ FULLY DONE | a6_aggregate_ranking.png, three_rankings.png, bootstrap_ci.json with separability tests |
| 12 | Failure analysis for each | ⚠️ PARTIAL | per-model L1 disaggregable from error_taxonomy_v2.json `by_model_l1` block but no panel-ready figure |
| 13 | Prompt variations for all tasks | ✅ FULLY DONE | data/synthetic/perturbations_all.json (473 = 75 v1 + 398 v2) |
| 14 | Reweight RQs | ✅ FULLY DONE | audit/rq_restructuring.md (Phase 1B); recompute_log.md applied data-layer reweight |
| 15 | More depth on RQ2-5 | ⚠️ PARTIAL | depth in audit/rq_restructuring.md, vault narrative; Layer-2 robustness + Layer-4/5 calibration analyses computed; not yet on frontend (F2.05, F2.06, F2.07) |

Totals: 6 ✅ DONE · 6 ⚠️ PARTIAL · 0 ❌ NOT · 3 🚫 OUT OF SCOPE.

For each PARTIAL, what's missing:

- #2 Version consistency: static_data freshness (F1.07); ece_comparison key
  rename not propagated to v2_routes.py (F1.10); B3 caveat language inconsistent
  between audit and frontend (F4.02).
- #5 Reasoning is weak: per-model `reasoning_quality` mean ranking exists in
  `judge_dimension_means.json` but no frontend card or RQ panel surfaces it.
- #6 Short answer: same gap as #5 — `reasoning_completeness` mean populated
  (claude 0.9715, chatgpt 0.9512, gemini 0.9878, deepseek 0.9390, mistral 0.9593)
  but not on the website.
- #8 Variation rankings: three_rankings.png on frontend is OLD render
  (412KB vs 207KB canonical, F8.03 — DIFFERS). New weights make Top-2 tied
  claim false (F4.06).
- #9 Error taxonomy: per-model stacked-bar not built; HALLUCINATION caveat
  needs to migrate from limitations_disclosures.md (a) into the website
  Limitations panel (already there per Limitations.jsx L1 — actually OK).
- #12 Failure analysis: per-model L1 figure never built.
- #15 Depth on RQ2-5: per-dim figures (a4b, a5b) not yet on frontend.

### Category 6 — Unified disclosures

Disclosure × Layer matrix. ✓ = present; ✗ = missing.

| Disclosure | audit/limitations_disclosures.md | research-narrative.md §6 | website Limitations.jsx |
|---|---|---|---|
| (a) Keyword-judge disagreement 135-task exclusion | ✗ (no entry) | ✗ | ✗ |
| (b) Self-consistency 10-task CONCEPTUAL exclusion | ✓ (f) | ✓ | ✗ |
| (c) Self-consistency stratification — RESOLVED Phase 1C | ✓ (e) | ✓ | ✗ (still describes B3 as open caveat) |
| (d) HALLUCINATION = 0 (real vs single-judge) | ✓ (a) | ✓ | ✓ (L1) |
| (e) Empty high-confidence bucket (verbalized only; gemini specifically zero) | ✓ (b) | ✓ | ✓ (L2) — but does not name gemini-specific "zero" |
| (f) Bootstrap CI top-2 not separable (accuracy AND robustness) | ✓ (c) — but needs new-weights update | ✓ | ✓ (L3) — but uses Phase 1A numbers |
| (g) Single-judge limitation (Yamauchi 2025, Feuer 2025) | ✓ (d) | ✓ | ✓ (L4) |
| (h) Length-correlation in RQ scoring (gemini verification) | ✓ (g) | ✓ | ✗ (not in 5-caveat list) |
| (i) NMACR weighting choice — literature-derived, post-hoc risk | ✗ (audit/methodology_continuity.md handles this) | ✓ §2 | ✗ |
| (j) Calibration measurement method-dependent | ✓ (e) wraps this | ✓ RQ5 | ✗ (Limitations.jsx L5 still describes B3 as open) |

**[F6.01] Keyword-judge disagreement 135-task exclusion missing from all 3 layers**
Severity: MAJOR
Category: Methodology gaps
Finding: 1230 base − 1095 eligible = 135 excluded. The exclusion design
choice (CONCEPTUAL/MINIMAX/BAYES_RISK have empty assumption checks) is
documented only in day2_audit_report.md [P-6]. Not in
limitations_disclosures.md, not in research-narrative.md (which uses 1095
without explanation), not in Limitations.jsx.
Evidence: see F2.01.
Cross-reference: F2.01
Recommendation: Add to all three layers.

**[F6.02] CONCEPTUAL 10-task exclusion missing from website**
Severity: MAJOR
Category: Methodology gaps
Finding: limitations_disclosures.md (f) and research-narrative.md RQ5
"Coverage limitation" both have it. Limitations.jsx 5-caveat list lacks
this. Not surfaced on the website.
Evidence: see F2.02; capstone-website/frontend/src/pages/Limitations.jsx
CAVEATS array.
Cross-reference: F2.02
Recommendation: Add as a 6th or 7th caveat on Limitations.jsx.

**[F6.03] Self-consistency Phase 1C resolution — frontend says "open" not "resolved"**
Severity: CRITICAL (already counted as F4.02)
Category: Methodology gaps
Finding: see F4.02.

**[F6.04] HALLUCINATION = 0 disclosure — fully present**
Severity: INFO
Category: Methodology gaps
Finding: All 3 layers cover it. Limitations.jsx L1 framing is clean.
Cross-reference: F2.03
Recommendation: None.

**[F6.05] Empty high-confidence bucket — Limitations.jsx omits gemini-specific zero**
Severity: MINOR
Category: Methodology gaps
Finding: Limitations.jsx L2 mentions empty high bucket, but does NOT call
out the gemini-specific "0 verbalized signals across 246 base runs" finding.
limitations_disclosures.md (b) has this. research-narrative.md has it.
Evidence: capstone-website/frontend/src/pages/Limitations.jsx:17-22.
Cross-reference: F2.04
Recommendation: One additional sentence to L2: "Gemini specifically returned
0 verbalized confidence signals across 246 base runs and is excluded from
the accuracy-calibration correlation."

**[F6.06] Bootstrap CI top-2 — needs new-weights update**
Severity: MAJOR (already counted as F4.06)
Category: Methodology gaps
Finding: see F4.06.

**[F6.07] Single-judge limitation — fully present**
Severity: INFO
Category: Methodology gaps
Finding: All 3 layers cover it. Cite Yamauchi 2025 + Feuer 2025 consistent.
Cross-reference: none
Recommendation: None.

**[F6.08] Length-correlation gemini missing from website**
Severity: MAJOR (already counted as F2.08)
Category: Methodology gaps
Finding: see F2.08.

**[F6.09] NMACR weighting choice (literature-derived, post-hoc) — vault and audit cover it; website does not call out post-hoc risk**
Severity: MAJOR
Category: Methodology gaps
Finding: research-narrative.md §2 has full per-dim defense. methodology_continuity.md
documents the literature anchor. limitations_disclosures.md does NOT have an
entry on the post-hoc-weight-selection risk (the risk that literature-derived
weights happen to favor certain models). Website Methodology.jsx §1 documents
N·M·A·C·R rubric but the audit could not confirm whether the new weights
section is on the page or whether the weights are still presented as equal.
Evidence: limitations_disclosures.md (no (i) entry); not exhaustively scanned
on Methodology.jsx — flagged for triage.
Cross-reference: F1.04, F4.07
Recommendation: Add a limitations_disclosures.md (h) entry on post-hoc weight
selection. Verify Methodology.jsx surfaces literature-derived weights.

**[F6.10] Calibration method-dependent — partially present**
Severity: MAJOR (overlap with F4.02)
Category: Methodology gaps
Finding: research-narrative.md RQ5 has the full method-dependent framing.
limitations_disclosures.md (e) wraps it under "RESOLVED via Phase 1C."
Frontend Limitations.jsx L5 does not have this; methodology_continuity.md
old framing (F4.03).
Cross-reference: F4.02, F4.03
Recommendation: Already part of F4.02 fix.

### Category 7 — Things mentioned but not done

**[F7.01] Phase 1D (website updates) — NOT STARTED**
Severity: CRITICAL
Category: Things not done
Finding: Audit task description identifies "Phase 1D website updates pending."
No evidence Phase 1D has begun: deployed static_data still Phase 1A;
KeyFindings static fallback still Phase 1A "Top 2 tied claude+gemini";
Methodology.jsx + Limitations.jsx still hardcode Phase 1A numbers; visualizations.js
still references "B3 proxy" subtitle; PRIMARY/SUPPORTING percentage badges
still in App.jsx; 5 of 15 figures stale on frontend; a4b + a5b figures not
mirrored or in manifest.
Evidence: see F1.07, F4.01, F4.02, F4.07, F8.03.
Cross-reference: F1.05, F1.06, F1.07, F1.08, F4.01, F4.02, F4.06, F4.07, F8.01, F8.03
Recommendation: Begin Phase 1D before any presentation. Highest priority is
F1.07 (refresh static_data); then F4.01/F4.02 (frontend prose); then F8.03
(re-mirror PNGs); then F4.07 (drop weight badges).

**[F7.02] Phase 1E (final consistency check) — NOT STARTED**
Severity: MAJOR
Category: Things not done
Finding: No Phase 1E artifacts found. The intended "final consistency
check" appears to be exactly what THIS audit document is meant to be
(or precede). recompute_log.md, methodology_continuity.md, etc. all stop
at Phase 1C.
Evidence: grep "Phase 1E" returned 0 hits across audit/, vault, scripts/.
Cross-reference: F7.01
Recommendation: Use this audit as input to Phase 1E execution.

**[F7.03] /poster page removal — NOT happened**
Severity: MINOR
Category: Things not done
Finding: capstone-website/frontend/src/main.jsx:13 still routes
`<Route path="/poster" element={<PosterCompanion />} />`. PosterCompanion.jsx
exists at 7816 bytes. capstone-website/README.md §3 documents `/poster` route
as live ("Mobile-first companion · Three Rankings figure + 4 headline cards
+ quick links"). audit/deployment_report.md QR code section deploys a QR
pointing at https://bayes-benchmark.vercel.app/poster — explicitly in use.
Audit task says "removal happened in code?" — it has NOT, and based on
evidence, removal is NOT desired (poster is still being used as the May 8
deliverable artifact).
Evidence: capstone-website/frontend/src/main.jsx:13; capstone-website/README.md;
audit/deployment_report.md QR section.
Cross-reference: none
Recommendation: Confirm with user whether /poster is intended to stay (likely
yes per QR deployment).

**[F7.04] Key Findings card redesign (6 plain-English cards) — already implemented**
Severity: INFO
Category: Things not done
Finding: KeyFindings.jsx already renders 6 cards, dynamically built from
`/api/v2/headline_numbers`. Build function returns 6 card objects: pass_flip,
krippendorff α, dominant failure, perturbation runs, distinct rankings, bootstrap
CI. Plain-English language confirmed. **Caveat**: live cards are bound to
deployed (Phase 1A) static_data — F1.07 fix needed for content correctness.
Evidence: capstone-website/frontend/src/components/KeyFindings.jsx:31-47
(buildCards returns 6 entries).
Cross-reference: F1.07, F4.01
Recommendation: None (design done); F1.07 fix is what's needed.

**[F7.05] NMACR full literature defense — present in vault, NOT on website Methodology**
Severity: MAJOR
Category: Things not done
Finding: research-narrative.md §2 has full per-dim defense (5 paragraphs).
methodology_continuity.md "NMACR weighting" section condenses it. Audit
could not confirm whether Methodology.jsx page has been updated to display
this — Methodology.jsx is 13.3KB, the relevant section was not found in
the read. Likely NOT updated since Methodology.jsx still hardcodes Phase 1A
accuracy numbers (F1.05 / F4.01).
Evidence: llm-stats-vault/00-home/research-narrative.md:69-95;
audit/methodology_continuity.md:23-41; capstone-website/frontend/src/pages/
Methodology.jsx (13.3KB, partial read).
Cross-reference: F1.04, F4.07, F7.01
Recommendation: Audit Methodology.jsx for NMACR weight section. Add literature-derived
weights with per-dim defense if missing.

**[F7.06] Render free-tier sleep wake-up workaround — NOT implemented**
Severity: MINOR
Category: Things not done
Finding: grep for "render sleep / wake-up / warmup" across frontend src
returns 0 hits. KeyFindings.jsx fetch has standard try/catch with static
fallback on error — would handle Render cold-start by falling through to
hardcoded values, but no warm-up ping or loading state explicitly designed
for the ~30s cold-start. Not directly load-bearing for accuracy but a
reviewer reaching the live site after dormant period would see the static
fallback (which is currently Phase 1A "Top 2 tied claude/gemini" — exactly
the wrong content).
Evidence: grep result 0 hits.
Cross-reference: F4.01
Recommendation: Either (a) add a warm-up ping on page load, or (b) update
the static fallback in KeyFindings.jsx:7-13 to Phase 1B numbers so cold-start
shows correct content.

### Category 8 — Frontend-backend-data consistency

**[F8.01] Backend serves stale Phase 1A data via DATA_ROOT=static_data**
Severity: CRITICAL (already counted as F1.07)
Category: Frontend-backend-data consistency
Finding: see F1.07. JSON sizes for /api/v2/* responses NOT measured here
(would require running the live API); inferred from static_data file sizes
that the deployed responses will mirror those:
- /api/v2/health: ~1KB (6 entries)
- /api/v2/headline_numbers: ~2KB (computed from agreement + krippendorff +
  taxonomy + rob — all 4 sources present in static_data)
- /api/v2/rankings: ~5KB (bootstrap_ci + robustness + self_consistency
  blocks)
- /api/v2/error_taxonomy: ~90KB (matches canonical, includes records)
- /api/v2/robustness: ~80KB (most of robustness_v2.json minus per_dim_delta
  — Phase 1A version)
- /api/v2/agreement: ~50KB (most of keyword_vs_judge + krippendorff blocks)
- /api/v2/calibration: ~10KB (verbalized + B3 stratified consistency)
- /api/v2/literature: ~30-50KB (parsed from 22 vault notes)

Cross-reference: F1.07, F1.10, F4.01, F7.01
Recommendation: see F1.07.

**[F8.02] mtime-keyed cache will not auto-detect a refresh unless mtime advances**
Severity: MINOR
Category: Frontend-backend-data consistency
Finding: v2_routes._load_json caches by `path.stat().st_mtime_ns`. Re-reads
when mtime changes. So after F1.07 refresh + Render redeploy, cache will
correctly re-read. Bash-level refresh that preserves mtime (e.g. `cp -p`
or `git checkout` of files with same content) could fail to invalidate —
edge case unlikely in deployment workflow.
Evidence: v2_routes.py:54-77.
Cross-reference: F1.07
Recommendation: After F1.07 refresh, verify Render container restarts
(or touches mtime) before claiming the deployment reflects new data.

**[F8.03] Figures: 5 of 15 frontend PNGs differ in bytes from canonical report_materials/figures/**
Severity: MAJOR
Category: Frontend-backend-data consistency
Finding: Byte comparison via `cmp -s`:
- MATCH (10 of 15): a1_failure_by_tasktype, a4_robustness_by_perttype,
  a5_calibration_reliability, agreement_metrics_comparison, bootstrap_ci,
  calibration_reliability, error_taxonomy_hierarchical, judge_validation_by_model,
  judge_validation_scatter, robustness_heatmap.
- DIFFER (5 of 15):
  - a2_accuracy_by_category: rm=229KB, fe=103KB. Canonical regenerated
    Phase 1B (May 1 17:44); frontend copy is older render.
  - a3_failure_heatmap: rm=1210KB, fe=437KB. Same — canonical regenerated.
  - a6_aggregate_ranking: rm=137KB, fe=212KB. Inverse — canonical regenerated
    SMALLER (probably stripped of v1 column). Frontend has older larger
    version.
  - self_consistency_calibration: rm=207KB, fe=98KB. Phase 1C regenerated
    canonical (May 2 13:25); frontend has Phase 1A B3 figure.
  - three_rankings: rm=212KB, fe=408KB. Phase 1B canonical regenerated;
    frontend has older Phase 1A larger render.

Two figures NOT mirrored at all:
- a4b_per_dim_robustness.png (Phase 1B Layer 2)
- a5b_per_dim_calibration.png (Phase 1B Layer 5)

Evidence: cmp -s output (5 DIFF, 10 MATCH); ls of both directories.
Cross-reference: F2.05, F2.06, F3.05, F8.04
Recommendation: Re-mirror the 5 stale PNGs. Add a4b + a5b. Update visualizations.js
manifest to reference a4b + a5b.

**[F8.04] visualizations.js manifest captions reference old findings**
Severity: MAJOR
Category: Frontend-backend-data consistency
Finding:
- visualizations.js:35 (bootstrap_ci entry): subtitle "Claude 0.679 [0.655,
  0.702] · Gemini 0.674 [0.647, 0.700]" — Phase 1A numbers. Caption "Top-2
  not statistically separable" — false under new weights (F4.06).
- visualizations.js:71 (robustness_heatmap entry): caption "Mistral degrades
  most" — under Phase 1A this was true (mistral Δ=0.0135); under Phase 1B
  Mistral is RANKED #1 ROBUSTNESS (Δ=0.007). Caption is now inverted.
- visualizations.js:130 (self_consistency entry): title "Self-Consistency
  Calibration (B3 proxy)" — Phase 1A; caption "top-failure stratum" — Phase 1A.
- a4b and a5b PNGs absent from manifest entirely.

Evidence: capstone-website/frontend/src/data/visualizations.js:35, 71-73,
129-135.
Cross-reference: F1.05, F1.06, F2.05, F2.06, F4.06, F8.03
Recommendation: Rewrite affected captions/subtitles. Add a4b + a5b entries
under "robustness" and "calibration" categories respectively.

---

## Cross-reference matrix

| Finding | Related findings |
|---|---|
| F1.04 (NMACR weights) | F4.07, F5.14, F7.05 |
| F1.05 (per-model accuracy) | F1.04, F1.06, F1.07, F4.01, F4.06, F8.01 |
| F1.06 (robustness ranking) | F1.05, F1.07, F4.05, F8.04 |
| F1.07 (deployed static_data stale) | F1.04, F1.05, F1.06, F1.10, F2.05, F2.06, F2.07, F7.01, F7.05, F8.01, F8.02 |
| F1.08 (calibration 3 layers) | F1.07, F1.10, F4.02, F6.03, F6.05, F8.02 |
| F1.10 (ece_comparison key) | F1.07, F1.08, F8.01 |
| F2.05/06/07 (Layer 2/4/5 partial) | F1.07, F8.03, F8.04 |
| F4.01 (Claude wins) | F1.05, F1.07, F7.01 |
| F4.02 (B3 caveat) | F1.08, F6.03, F8.04 |
| F4.06 (Top-2 tied) | F1.05, F1.06, F1.07, F4.01 |
| F4.07 (PRIMARY/SUPPORTING badges) | F1.04, F5.14, F7.01 |
| F6.01 (135-task exclusion) | F2.01 |
| F7.01 (Phase 1D not started) | F1.05, F1.06, F1.07, F1.08, F4.01, F4.02, F4.06, F4.07, F8.01, F8.03 |
| F8.03 (5 stale frontend PNGs) | F2.05, F2.06, F3.05, F8.04 |

Most-affected files (5+ findings touching them):
- capstone-website/backend/static_data/* — F1.04, F1.05, F1.06, F1.07, F1.08,
  F1.09, F2.05, F2.06, F2.07, F4.01, F4.02, F4.05, F4.06, F8.01, F8.04 (15)
- capstone-website/frontend/src/App.jsx — F1.04, F4.01, F4.07, F5.14, F7.01 (5)
- capstone-website/frontend/src/pages/Methodology.jsx — F1.05, F4.01, F4.06,
  F7.05 (4)
- capstone-website/frontend/src/pages/Limitations.jsx — F1.06, F4.02, F4.06,
  F6.02, F6.05, F6.08 (6)
- capstone-website/frontend/src/data/visualizations.js — F2.05, F2.06, F4.02,
  F4.06, F8.03, F8.04 (6)

---

## Recommended fix sequence

Top 10 fixes in priority order, with estimated effort and dependencies.

1. **[F1.07] Refresh static_data with Phase 1B/1C canonical files** —
   30 min. Copy bootstrap_ci.json, robustness_v2.json, calibration.json,
   error_taxonomy_v2.json, keyword_vs_judge_agreement.json, krippendorff_agreement.json,
   self_consistency_calibration.json, judge_dimension_means.json,
   tolerance_sensitivity.json from canonical experiments/results_v2/. Add new
   per_dim_calibration.json + nmacr_scores_v2.jsonl. Trigger Render redeploy.
   Dependencies: none. Unlocks: F1.05, F1.06, F4.01, F4.06, F8.01.

2. **[F1.10] Fix v2_routes.py ece_comparison key mismatch** — 5 min.
   Edit lines 314 and 412 to read
   `sc.get("ece_comparison_full") or sc.get("ece_comparison", {})` for
   backward compat. Dependencies: must precede or accompany F1.07 (or the
   moment static_data refreshes, both endpoints break).

3. **[F8.03] Re-mirror 5 stale PNGs + add a4b + a5b** — 10 min. Copy from
   report_materials/figures/ to capstone-website/frontend/public/visualizations/png/v2/.
   Dependencies: none. Unlocks: F2.05, F2.06.

4. **[F4.01 + F4.06 + F4.02] Update frontend prose for Phase 1B/1C narrative**
   — 1.5 hours. Methodology.jsx:164-165 (new accuracy CI numbers; remove
   "overlap" claim for accuracy, retain for robustness top-2). Limitations.jsx:26-28
   (same). Limitations.jsx:43-51 (rewrite L5 per limitations_disclosures.md (e)
   "RESOLVED via Phase 1C"). visualizations.js:35,71,130 (caption rewrites).
   KeyFindings.jsx:7-13 (static fallback Phase 1B values). Dependencies: F1.07.

5. **[F4.07] Drop PRIMARY/SUPPORTING percentage badges from App.jsx** —
   15 min. Remove `weight:'X%'` from RQS array (lines 1870-1902). Update
   App.jsx:967-968 copy. Dependencies: none. Cosmetic but flagged in
   rq_restructuring.md as Phase 1B requirement.

6. **[F2.05 + F2.06 + F2.07] Surface Phase 1B Layers 2, 4, 5 on the website**
   — 2-3 hours. Add visualizations.js entries for a4b + a5b. Add per-dim
   robustness card or sub-panel. Add accuracy-calibration correlation sub-panel
   on RQ5 with gemini exclusion note. Dependencies: F8.03 + F1.07.

7. **[F1.09] Expose formatting_failure_rate via backend** — 30 min. Add a
   top-level `formatting_failure_rate` key to /api/v2/headline_numbers
   response. Surface in Methodology.jsx (4-line note) or KeyFindings card.
   Dependencies: F1.07.

8. **[F6.01 + F6.02] Add missing disclosures to website Limitations panel**
   — 30 min. Add (a) 135-task exclusion sentence to limitations_disclosures.md
   (d). Add a CONCEPTUAL-10-task exclusion entry as L6 on Limitations.jsx.
   Dependencies: none.

9. **[F3.01 + F3.02] Update stale audit cross-references** — 15 min.
   Replace `sessions/2026-04-30-day1-poster-sprint.md` →
   `90-archive/2026-04-30-day1-poster-sprint.md` and
   `audit/rq_reweighting.md` → `audit/rq_restructuring.md` in
   personal_todo_status.md, day2_audit_report.md, website_discovery.md.
   Dependencies: none.

10. **[F6.08] Add length-correlation gemini caveat to Limitations.jsx** —
    15 min. New L6/L7 caveat using limitations_disclosures.md (g) text.
    Dependencies: none.

---

## Coverage gaps in this audit

- Methodology.jsx not exhaustively read end-to-end (13.3KB) — flagged
  F7.05 for triage on whether NMACR literature defense was added.
- PosterCompanion.jsx (7.8KB) not read in full — visual inspection of
  numerical values needed before May 8.
- References.jsx (12.9KB) not read for citation alignment with
  llm-stats-vault/40-literature/.
- /api/v2/* response sizes inferred from static_data file sizes, not measured
  against the live deployment.
- ScalarValueComparison NOT done for: judge_dimension_means.json fields,
  tolerance_sensitivity.json fields — these endpoints are exposed via
  v2_routes.py but their canonical-vs-deployed parity not measured.
- Did not run any end-to-end test of /api/v2/* against canonical data
  (would require local backend run; out of scope for read-only audit).

---

```
COMPREHENSIVE AUDIT COMPLETE

Total findings: 32
- CRITICAL: 4
- MAJOR: 13
- MINOR: 11
- INFO: 4

Top 5 priorities to fix before user-facing work:
1. F1.07: Refresh capstone-website/backend/static_data/ with Phase 1B/1C canonical files (deployed backend currently serves Phase 1A)
2. F1.10: Fix v2_routes.py ece_comparison key mismatch (will break /api/v2/rankings + /api/v2/calibration the moment Phase 1C data is deployed)
3. F4.01 + F4.06: Update Methodology.jsx, Limitations.jsx, KeyFindings.jsx for new Gemini-#1 / Top-2 NOT tied accuracy narrative
4. F4.02: Rewrite Limitations.jsx L5 — B3 caveat is RESOLVED via Phase 1C, frontend still describes it as open
5. F8.03 + F2.05/06: Re-mirror 5 stale frontend PNGs + add a4b_per_dim_robustness + a5b_per_dim_calibration

Most-affected files (5+ findings → flag for triage):
- capstone-website/backend/static_data/*: 15 findings
- capstone-website/frontend/src/pages/Limitations.jsx: 6 findings
- capstone-website/frontend/src/data/visualizations.js: 6 findings
- capstone-website/frontend/src/App.jsx: 5 findings

Broken cross-references found: 6
  (F3.01 sessions/ → 90-archive/; F3.02 rq_reweighting → rq_restructuring; F3.05 5 stale PNGs + 2 missing PNGs;
   F1.10 ece_comparison key; v2_routes.py ↔ canonical Phase 1C file)
Stale narrative anchors found: 7
  (F4.01 Claude wins; F4.02 B3 open caveat; F4.03 hedge-heavy framing in 2 docs; F4.06 Top-2 tied; F4.07 PRIMARY/SUPPORTING percentages;
   visualizations.js subtitle Top-2 tied; visualizations.js robustness "Mistral degrades most" inverted)
Professor critique items still PARTIAL: 6
  (#2 version consistency; #5 reasoning weak; #6 short answer; #8 variation rankings; #9 error taxonomy; #12 failure analysis;
   #15 depth on RQ2-5)
Methodology disclosures missing from at least one layer: 5
  (F6.01 135-task exclusion missing all 3 layers; F6.02 CONCEPTUAL-10 missing from website;
   F6.03 B3 resolution missing from website; F6.05 gemini-zero specific missing from website;
   F6.08 length-correlation missing from website; F6.09 NMACR post-hoc-risk missing from limitations doc)
```

*End of audit.*
