# Investigation 4 — perturbation count audit

**Verdict: canonical file complete. 473 records = 75 + 398 exactly. All 171 base tasks covered. The "~14 per base task" recollection was wrong — actual mean is 2.77.**

## Counts

| File | Records |
|---|---|
| `perturbations.json` (v1, hand-authored) | 75 |
| `perturbations_v2.json` (v2, LLM-generated) | 398 |
| `perturbations_all.json` (canonical merged) | **473** |
| Sum-match (`v1 + v2 == all`) | ✅ exact |

## Coverage of 171 base tasks

- Base tasks in `tasks_all.json`: **171**
- Base tasks with ≥ 1 perturbation in `_all`: **171** (full coverage)
- Base tasks missing from `_all`: **0**
- Base task IDs in `_all` but not in `tasks_all.json`: **0**

## Per-base distribution

```
min  =  2
max  =  3
mean =  2.77
median = 3

Histogram:
  2 perturbations: 40 base tasks
  3 perturbations: 131 base tasks
```

Total: 40·2 + 131·3 = 80 + 393 = 473 ✓

## Per-type distribution

```
rephrase  : 171  (1 per base — universal)
semantic  : 171  (1 per base — universal)
numerical : 131  (skipped for 40 bases where numerical mutation isn't applicable, e.g. conceptual or qualitative tasks)
```

The 40 bases with only 2 perturbations are exactly the ones where `numerical` was omitted.

## v1 vs v2 base coverage

```
v1 unique base_task_ids: 25   (×3 types each = 75)
v2 unique base_task_ids: 146  (mix of 2 and 3 types each = 398)
v1 ∩ v2 (overlap):        0
v1 ∪ v2:                 171 = 25 + 146
```

**v1 and v2 partition the 171 baselines disjointly.** No double-counting.

v2 records all carry `_v2` suffix in `task_id`: 398/398 confirmed (matches CLAUDE.md filter rule for the deprecation cleanup).

Sample v1 base_task_ids (covered by hand-authored only): `BAYES_FACTOR_01`, `BAYES_RISK_01`, `BETA_BINOM_01`, `BIAS_VAR_01`, `BINOM_FLAT_01`, `BINOM_FLAT_02`, `BOX_MULLER_01`, `CI_CREDIBLE_01`, `DISC_MEDIAN_01`, `FISHER_INFO_01` (and 15 more).

## Conclusion

- Canonical `perturbations_all.json` is **complete**: 473 records, all 171 base tasks covered, sum exactly matches v1+v2.
- The headline claim "473 perturbations across 171 base tasks = 2.77 avg" is correct.
- The earlier "~14 per base task" recollection is wrong — likely a confusion with a different artefact (perhaps total runs per task = 5 models × ~3 perturbations + base = ~17–20 runs/base, near "~14"-ish for some subset).
- `data/raw_data/synthetic/perturbations.json` and `perturbations_v2.json` are **superseded for data purposes** but `perturbations.json` remains required as the v1-id filter source per CLAUDE.md (kept on disk).

## Implications for `data/perturbations/` reorg

Safe to define new layout:
```
data/perturbations/
  canonical_473.json        ← rename of perturbations_all.json
  v1_hand_authored.json     ← rename of perturbations.json (v1, 75 records, kept for filter use)
  v2_llm_generated.json     ← rename of perturbations_v2.json (v2, 398 records)
```
…OR keep filenames as-is to avoid breaking the 5+ consumer scripts and website backend hard-coded path `data/raw_data/synthetic/perturbations.json` (per CLAUDE.md "Phase 1.8" deprecation note). **Reorg plan defaults to keep-in-place + symlink/copy under `data/perturbations/` if a fresher layout is needed**, since renaming would touch many call sites.
