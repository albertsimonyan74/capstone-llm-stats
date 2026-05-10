# Phase A — Investigate `llm-stats-vault/90-archive/{audit,experiments}/` staging

Generated 2026-05-10. Repo root: `/Users/albertsimonyan/Desktop/capstone-llm-stats`. Git: `main`.

Untracked staging dirs were observed at session start. This file investigates whether they are (a) empty scaffold, (b) full identical copy, or (c) partial / diverged migration.

---

## 1. `llm-stats-vault/90-archive/audit/`

### Top-level listing
```
total 8
-rw-r--r--  1 user  staff  877 May 10 12:39 recompute_log.md
```

**Single file.** Source `audit/` contains 22 entries (16 markdown reports, 2 JSON snapshots, 2 nested baseline directories with `runs.jsonl` snapshots, 2 more reports). Staging has 1 of 22.

### `diff -rq audit/ llm-stats-vault/90-archive/audit/`
```
Only in audit: aggregation_locus.md
Only in audit: approach_a_baseline_snapshot.json
Only in audit: cleanup_audit_2026-05-02.md
Only in audit: comprehensive_audit_2026-05-01.md
Only in audit: deployment_report.md
Only in audit: discovery_audit_2026-05-02.md
Only in audit: gemini_forensic_2026-05-03.md
Only in audit: group_a_completion.md
Only in audit: limitations_disclosures.md
Only in audit: literature_comparison.md
Only in audit: methodology_continuity.md
Only in audit: personal_todo_status.md
Files audit/recompute_log.md and llm-stats-vault/90-archive/audit/recompute_log.md differ
Only in audit: rq_ieee_formulations.md
Only in audit: rq_restructuring.md
Only in audit: tier1_baseline_20260503_195141
Only in audit: tier1_diff_report.md
Only in audit: tier2a6_dual_write_fix.md
Only in audit: track_a_diagnostic_2026-05-02.md
Only in audit: v1_deprecation_baseline_20260504_001522
Only in audit: v1_deprecation_diff_report.md
Only in audit: website_discovery.md
```

21 files only in source, 1 file differs.

### `recompute_log.md` content comparison

| Property | Source `audit/recompute_log.md` | Staging `90-archive/audit/recompute_log.md` |
|---|---|---|
| Size | 26,744 bytes | 877 bytes |
| Lines | 589 | 26 |
| `n_base` | populated (real run) | `0` |
| `n_perturbation` | populated (real run) | `0` |
| Tables | filled with model/run rows | empty headers only |
| `generated_at` (header note) | 2026-05-03T15:59:00.436882+00:00 | 2026-05-03T15:59:00.436882+00:00 (same) |

**Verdict:** staging file is a dry-run / zero-input scaffold of the same generator (`scripts/recompute_downstream.py`). Same timestamp metadata, but emitted with no records — empty markdown skeleton with table headers and `Records: 0`. Not an extract of the real audit log.

---

## 2. `llm-stats-vault/90-archive/experiments/` (informational)

### Listing
```
llm-stats-vault/90-archive/experiments/results_v2/nmacr_scores_v2.jsonl  (542 bytes, 1 line)
```

Single file under `results_v2/`. Source `experiments/results_v2/` has 20 files (~24 MB).

### `nmacr_scores_v2.jsonl` content comparison

| Property | Source | Staging |
|---|---|---|
| Lines | 3,596 (1 header + 3,595 records) | 1 (header only) |
| Header `n_base` | 1230 | 0 |
| Header `n_perturbation` | 2365 | 0 |
| Header `generated_at` | 2026-05-03T15:59:12.116159+00:00 | 2026-05-03T15:59:00.436452+00:00 |
| Data records | 3,595 | 0 |

**Verdict:** same scaffold pattern. Header-only artifact from a zero-input run of `scripts/recompute_downstream.py` writing into the vault destination instead of the canonical `experiments/` destination.

---

## 3. Provenance hypothesis

`scripts/recompute_downstream.py` writes two outputs: a JSONL (`nmacr_scores_v2.jsonl`) and a markdown log (`recompute_log.md`). Both staging files match a zero-records run of that script. Likely cause: a previous session pointed the script's output paths at `llm-stats-vault/90-archive/...` while the input runs filter excluded everything (n=0), producing the scaffolds. They were never deleted.

Neither file is on disk anywhere else in the vault (verified by the file listing). They are not partial migrations of `audit/`, just orphaned dry-run output.

---

## 4. Recommendation

**Option (a): staging is empty/scaffold → delete it, do a fresh `git mv`.**

Concrete steps for Phase C:

1. `rm llm-stats-vault/90-archive/audit/recompute_log.md`
2. `rmdir llm-stats-vault/90-archive/audit/`
3. `git mv audit/ llm-stats-vault/90-archive/audit/` — preserves history.
4. (Out of scope for this prompt — `experiments/` is staying put per the spec.) Cleanup of the stub `llm-stats-vault/90-archive/experiments/results_v2/nmacr_scores_v2.jsonl` can be folded into a follow-up. Recommended: delete it + the empty parent dirs in the same Phase C commit, since it's a zero-data orphan with no provenance value.

No risk of overwriting real archived content — the staging holds zero data records.

### Confidence
- High. Direct inspection of file sizes, line counts, and header metadata; no dependency on git history or external state.
