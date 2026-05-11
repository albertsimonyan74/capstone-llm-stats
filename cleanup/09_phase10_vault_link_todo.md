# Phase 10 — Vault link cleanup TODO

**Status:** DEFERRED past 2026-05-15 (paper submission).
**Created:** 2026-05-11 during Phase 10 refactor.

---

## What

Live `llm-stats-vault/` (excluding `90-archive/`) contains **161 references**
to pre-Phase-10 paths that no longer exist at the working-repo root:

| Source path | Vault live refs |
|---|---:|
| `baseline/` | 60 |
| `evaluation/` | 55 |
| `llm_runner/` | 44 |
| `capstone_mcp/` | 8 |
| `scripts/` | 70 |
| `experiments/` | 61 |
| (plus residual `data/synthetic`, `data/benchmark_v1`) | various |

These are markdown link targets in Obsidian notes — broken if clicked,
but do not affect any code, test, or paper submission. The vault is
not part of the §5 submission tree.

## Why not done now

Plan 10.E threshold: defer vault cleanup if >30 live refs. Actual: 161.
Paper deadline 2026-05-15 takes priority.

## How to fix (post-submission)

```bash
# From repo root, run the same sed map used in 10.D over llm-stats-vault/
find llm-stats-vault/ -type f \( -name "*.md" -o -name "*.json" \) \
  -not -path "llm-stats-vault/90-archive/*" \
  -exec sed -i '' \
    -e 's|baseline/|code/data_preprocessing/|g' \
    -e 's|evaluation/|code/analysis/|g' \
    -e 's|llm_runner/|code/models/|g' \
    -e 's|capstone_mcp/|code/capstone_mcp/|g' \
    -e 's|report_materials/r_analysis|code/visualization|g' \
    {} \;

# Bounded scripts/:
find llm-stats-vault/ -type f \( -name "*.md" -o -name "*.json" \) \
  -not -path "llm-stats-vault/90-archive/*" \
  -exec sed -i '' -E \
    -e 's#(^|[^/A-Za-z0-9_])scripts/#\1code/scripts/#g' \
    {} \;

# Data path fixes:
find llm-stats-vault/ -type f \( -name "*.md" -o -name "*.json" \) \
  -not -path "llm-stats-vault/90-archive/*" \
  -exec sed -i '' \
    -e 's|experiments/results_v1|data/processed_data/results_v1|g' \
    -e 's|experiments/results_v2|data/processed_data/results_v2|g' \
    -e 's|data/benchmark_v1|data/raw_data/benchmark_v1|g' \
    -e 's|data/synthetic|data/raw_data/synthetic|g' \
    {} \;

# Recovery for any double-subs introduced:
find llm-stats-vault/ -type f \( -name "*.md" -o -name "*.json" \) \
  -not -path "llm-stats-vault/90-archive/*" \
  -exec sed -i '' \
    -e 's|data/raw_data/raw_data/|data/raw_data/|g' \
    {} \;
```

Verify with:
```bash
grep -rnE '(baseline|evaluation|llm_runner|capstone_mcp|scripts|experiments)/' \
  llm-stats-vault/ --exclude-dir=90-archive | wc -l   # should be ~0
```

## Notes

- 90-archive/ is intentionally untouched — historical record.
- `capstone-website/backend/static_data/llm-stats-vault/` is a copied
  snapshot of the vault that ships with the website (for serving
  literature notes via API). If website is redeployed post-cleanup,
  re-run snapshot copy.
