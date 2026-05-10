# Investigation 3 — error taxonomy diff

**Verdict: v2 supersedes v1.** Archive `data/error_taxonomy_results.json`.

## File comparison

| Property | A: `data/error_taxonomy_results.json` (v1) | B: `experiments/results_v2/error_taxonomy_v2.json` (v2) |
|---|---|---|
| mtime | 2026-04-26 22:49 | 2026-05-06 13:45 |
| size | 94,113 bytes | 91,607 bytes |
| top-level type | dict, 11 keys | dict, 11 keys |
| failures classified | 143 | 143 |
| classifier | Rule-based + 1 LLM call (`llm_calls_used: 1`) | Together AI Llama 3.3 70B Turbo |
| taxonomy depth | flat E1–E9 (9 categories) | hierarchical L1 → L2 (4 L1 buckets, 16 L2 codes) |
| top categories | E3 ASSUMPTION_VIOLATION=119, E7 TRUNCATION=93, E5 OVERCONFIDENCE=85 | ASSUMPTION_VIOLATION=67, MATHEMATICAL_ERROR=48, FORMATTING_FAILURE=18, CONCEPTUAL_ERROR=10 |
| has `judge_model` field | ❌ | ✅ `meta-llama/Llama-3.3-70B-Instruct-Turbo` |
| has `repaired_pairs`, `by_model_l2` | ❌ | ✅ |

A's per-error counts are inflated because tags overlap (one failure can be tagged as both E3 and E7); B uses a single L1 assignment per failure (143 = 67+48+18+10). They are different schemas describing the same underlying 143 failures.

## Generators

- A: [scripts/analyze_errors.py:22](scripts/analyze_errors.py#L22) writes to `data/error_taxonomy_results.json`. Documented in CLAUDE.md as `python scripts/analyze_errors.py`. Multi-tag rule-based + heuristic.
- B: `scripts/error_taxonomy.py` writes to `experiments/results_v2/error_taxonomy_v2.json` via Together AI judge.

## Downstream usage

**B (v2) is canonical.** Every consumer references v2:
- [audit/comprehensive_audit_2026-05-01.md](audit/comprehensive_audit_2026-05-01.md) lines 105, 174, 326, 381, 540, 563, 746, 749, 1099 — all v2.
- [audit/rq_ieee_formulations.md:286, 353](audit/rq_ieee_formulations.md) — v2.
- [llm-stats-vault/sessions/2026-05-07-poster-defense-prep.md](llm-stats-vault/sessions/2026-05-07-poster-defense-prep.md) lines 15, 164, 389, 402, 418 — v2 cited as canonical, defends `n_failures_classified=143` and `judge_model`.
- [llm-stats-vault/40-literature/citation-map.md:106](llm-stats-vault/40-literature/citation-map.md) — v2 mapped to Papers 09, 13.
- Poster figures (`error_taxonomy_hierarchical.png`, `failure_taxonomy_stacked.png`) — derived from v2 (4-bucket L1 visible in PNGs).

**A (v1) has no downstream consumers** other than its own generator. Zero references in code/figures/reports outside `scripts/analyze_errors.py` itself.

## Recommendation

- **Archive v1 file**: move `data/error_taxonomy_results.json` → `archive/data_legacy/error_taxonomy_results_v1.json` in Phase 3. No deletion.
- **Keep `scripts/analyze_errors.py` for now**: it is the script CLAUDE.md documents, and is callable. Mark as superseded in a doc comment in a follow-up; do not delete.
- **No code refactor needed**: `scripts/error_taxonomy.py` (the v2 generator) is what the paper depends on; A/B never share a code path.
