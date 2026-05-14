# Phase B — `audit/` → `llm-stats-vault/90-archive/audit/` ref rewrite plan

Generated 2026-05-10. Repo root: `/Users/albertsimonyan/Desktop/capstone-llm-stats`.

Built from `grep -rn audit/ … | grep -v 90-archive/audit/`. Filters applied: drop `.venv`, `node_modules`, `.git`, `audit/` itself; suppress unrelated tokens like `audit_history`, `audit_repo`.

---

## Summary by category

| Category | File count | Ref count | Notes |
|---|---|---|---|
| A. Source code (live) | **3** | 5 | Docstrings/comments in Python — repo-root-relative paths |
| B. Project docs | **7** | 22 | Repo-root-relative; sed-safe global replace per file |
| C. Vault internal links (relative — need per-file depth math) | **9** | 21 | Both `[link](path)` and inline-code path tokens |
| D. Vault sibling `90-archive/*` refs to audit/ | **5** | 9 | After move, audit/ becomes their sibling |
| E. Bundled vault under `capstone-website/backend/static_data/` | **4** | 5 | Hand-copy from source vault after edits — no automated sync script |
| F. Do-not-touch (already correct, or non-text state) | **3** | n/a | `.obsidian/workspace.json`, `llm-stats-vault/cleanup/03a_audit_staging_investigation.md`, `2026-05-07-poster-defense-prep.md:253` already says `90-archive/audit/` |

**Total live references to rewrite:** **62 occurrences across 28 files.**

---

## Replacement convention

### Repo-root-relative (source code, top-level docs, llm-stats-vault/cleanup/, bundled-vault sources)

`audit/<file>` → `llm-stats-vault/90-archive/audit/<file>`

### Vault-internal relative links (depth-dependent)

Vault root: `llm-stats-vault/`. Source target was `<repo_root>/audit/`. Destination: `llm-stats-vault/90-archive/audit/`.

| Linker file path depth (relative to vault root) | Old `[…](X)` | New `[…](X)` |
|---|---|---|
| 1 (e.g., `00-home/`, `atlas/`, `40-literature/`, `sessions/`) | `../../audit/<file>` | `../90-archive/audit/<file>` |
| 2 (e.g., `knowledge/decisions/`, `knowledge/patterns/`, `40-literature/papers/`) | `../../../audit/<file>` | `../../90-archive/audit/<file>` |
| Sibling of `90-archive/audit/` (i.e., another `90-archive/*/` subdir) | `../../../audit/<file>` (going out of vault) | `../audit/<file>` (now sibling) — depth 2 below vault root via `90-archive/X/<file>` |

For inline-code references like `` `audit/X` `` (not bracket-linked), the convention is **same string substitution** (`audit/X` → `llm-stats-vault/90-archive/audit/X` in repo-root-relative docs, or the depth-appropriate relative path inside a vault file). Inline-code refs in vault paper notes are descriptive, not Obsidian-resolved, so repo-root-relative reads fine when the bundle is rendered statically by the website (which it is — see Section E).

---

## A. Source code (live, 3 files)

| File | Line | Current | Replacement | sed command |
|---|---|---|---|---|
| `code/analysis/metrics.py` | 17 | `See audit/aggregation_locus.md for the single-path rationale and` | `See llm-stats-vault/90-archive/audit/aggregation_locus.md for the single-path rationale and` | `sed -i '' 's|audit/aggregation_locus.md|llm-stats-vault/90-archive/audit/aggregation_locus.md|g' code/analysis/metrics.py` |
| `code/analysis/metrics.py` | 18 | `audit/methodology_continuity.md §"NMACR weighting" for the literature defense` | `llm-stats-vault/90-archive/audit/methodology_continuity.md §"NMACR weighting" for the literature defense` | `sed -i '' 's|audit/methodology_continuity.md|llm-stats-vault/90-archive/audit/methodology_continuity.md|g' code/analysis/metrics.py` |
| `code/models/response_parser.py` | 19 | `See audit/aggregation_locus.md (single-path rationale) and` | `See llm-stats-vault/90-archive/audit/aggregation_locus.md (single-path rationale) and` | `sed -i '' 's|audit/aggregation_locus.md|llm-stats-vault/90-archive/audit/aggregation_locus.md|g' code/models/response_parser.py` |
| `code/models/response_parser.py` | 20 | `audit/methodology_continuity.md §"NMACR weighting" (literature defense).` | `llm-stats-vault/90-archive/audit/methodology_continuity.md §"NMACR weighting" (literature defense).` | `sed -i '' 's|audit/methodology_continuity.md|llm-stats-vault/90-archive/audit/methodology_continuity.md|g' code/models/response_parser.py` |
| `code/scripts/recompute_downstream.py` | 22 | `in nmacr_scores_v2.jsonl header AND in audit/recompute_log.md.` | `in nmacr_scores_v2.jsonl header AND in llm-stats-vault/90-archive/audit/recompute_log.md.` | `sed -i '' 's|audit/recompute_log.md|llm-stats-vault/90-archive/audit/recompute_log.md|g' code/scripts/recompute_downstream.py` |

**Combined per-file sed:**
```bash
sed -i '' -E 's#(^| |[\(`])audit/([a-zA-Z0-9_-]+\.md)#\1llm-stats-vault/90-archive/audit/\2#g' \
  code/analysis/metrics.py code/models/response_parser.py code/scripts/recompute_downstream.py
```

(The character-class anchor avoids matching the substring `audit/` if it ever appears mid-identifier; vetted against the current grep.)

---

## B. Project docs (7 files, 22 refs)

All repo-root-relative. Same `audit/X` → `llm-stats-vault/90-archive/audit/X` replacement.

| File | Lines | Refs |
|---|---|---|
| `CLAUDE.md` | 168 | 1 (`audit/recompute_log.md`) |
| `poster/SCRAPE_PLAN.md` | 8, 112 | 2 (both `audit/recompute_log.md`) |
| `capstone-website/mobile-fixes-changelog.md` | 3 | 1 (`audit/website_discovery.md`) |
| `llm-stats-vault/cleanup/01_inventory.md` | 99, 141, 180 | 3 (`### audit/` heading; `audit/tier1_baseline_…/runs.jsonl`; `audit/, vault, .planning/, llm-stats-vault/cleanup/`) |
| `llm-stats-vault/cleanup/01c_error_taxonomy_diff.md` | 31, 32 | 2 (linked refs to `audit/comprehensive_audit_2026-05-01.md`, `audit/rq_ieee_formulations.md`) |
| `llm-stats-vault/cleanup/01e_script_callers.md` | 46, 86, 87, 88 | 5 (refs to `audit/personal_todo_status.md`, `audit/tier2a6_dual_write_fix.md`, `audit/cleanup_audit_2026-05-02.md` ×2, `audit/discovery_audit_2026-05-02.md`, `audit/recompute_log.md`) |
| `llm-stats-vault/cleanup/02_reorg_plan.md` | 52, 54, 113, 133, 146, 147, 298, 354, 380, 407 | 8 inline path refs (note: line 52 says `audit/ ← UNCHANGED in this phase` describing repo-tree position — see special-cases below) |

### Special cases inside Group B

- **`llm-stats-vault/cleanup/02_reorg_plan.md`**: this file describes the *post-state* tree. Several refs are intentional descriptions of the new location, not stale paths. Inspect each line; the rewrite list is:
  - L52 `├── audit/ ← UNCHANGED in this phase. (Separate prompt to archive/keep.)` — **REWRITE** to `├── llm-stats-vault/90-archive/audit/        ← (was top-level audit/, moved 2026-05-10)`
  - L54 `│   ├── audit/                    (existing)` — **DO NOT REWRITE**: this line is showing the *new* `90-archive/audit/` subtree contents. It's correct after the move (the line above it is the `90-archive/` parent). Verify in execution.
  - L113 `| audit/ | KEEP-IN-PLACE | — | (Separate prompt handles fate.) |` — **REWRITE** to `| llm-stats-vault/90-archive/audit/ | KEEP-IN-PLACE | — | Moved 2026-05-10 from repo root. |`
  - L133 `… per audit/cleanup_audit_2026-05-02.md:202 …` — **REWRITE** to `… per llm-stats-vault/90-archive/audit/cleanup_audit_2026-05-02.md:202 …`
  - L146 `audit/tier1_baseline_20260503_195141/` — **REWRITE**.
  - L147 `audit/v1_deprecation_baseline_20260504_001522/` — **REWRITE**.
  - L298 `per audit/cleanup_audit_2026-05-02.md [CL-B6]` — **REWRITE**.
  - L354 `…audit/recompute_log.md cross-refs.` — **REWRITE**.
  - L380 `audit/recompute_log.md, audit/cleanup_audit_2026-05-02.md, etc., reference moved file paths.` — **REWRITE** (both).
  - L407 — **DO NOT REWRITE**: text already says `Does not touch audit/ (separate prompt). Top-level archive/ was removed …` — the `audit/` here is the past-tense name. After the move, "audit/" no longer exists as a name; this prose stays factual as a historical note. Recommend a small edit: append `(audit/ moved to llm-stats-vault/90-archive/audit/ 2026-05-10.)` to L407 for clarity.

**Per-file sed (selective; do NOT pipe across all of `llm-stats-vault/cleanup/02_reorg_plan.md` because of the L54 + L407 special cases):**

```bash
# repo-rooted docs that are safe for global replace
for f in CLAUDE.md poster/SCRAPE_PLAN.md capstone-website/mobile-fixes-changelog.md \
         llm-stats-vault/cleanup/01_inventory.md llm-stats-vault/cleanup/01c_error_taxonomy_diff.md llm-stats-vault/cleanup/01e_script_callers.md ; do
  sed -i '' -E 's#(^| |\(|`|\[)audit/([a-zA-Z0-9_./-]+(\.md|\.json|\.jsonl|/[a-zA-Z0-9_./-]+|/))#\1llm-stats-vault/90-archive/audit/\2#g' "$f"
done

# 02_reorg_plan.md: hand-edit per the L52/L54/L407 notes above; do not pipe sed.
```

---

## C. Vault internal links (9 files, 21 refs — depth-dependent)

### Depth-1 vault files (linker is one level below vault root)

Old: `../../audit/<file>` → New: `../90-archive/audit/<file>`
Old inline: `audit/<file>` → New inline: `audit/<file>` left as-is **only if** the file lives inside `90-archive/` and the in-vault relative resolves; otherwise, write **`../90-archive/audit/<file>`** for clarity.

| File | Line | Form | Replacement |
|---|---|---|---|
| `llm-stats-vault/00-home/research-narrative.md` | 200 | inline `(audit/gemini_forensic_2026-05-03.md)` | `(../90-archive/audit/gemini_forensic_2026-05-03.md)` |
| `llm-stats-vault/00-home/research-narrative.md` | 343 | `[audit/aggregation_locus.md](../../audit/aggregation_locus.md)` | `[audit/aggregation_locus.md](../90-archive/audit/aggregation_locus.md)` (display text optional refresh; link target is what matters) |
| `llm-stats-vault/00-home/research-narrative.md` | 344-348 | same pattern × 5 | per-line analogues for `recompute_log.md`, `rq_restructuring.md`, `methodology_continuity.md`, `limitations_disclosures.md`, `literature_comparison.md` |
| `llm-stats-vault/00-home/current-priorities.md` | 26 | `../audit/comprehensive_audit_2026-05-01.md` | `../90-archive/audit/comprehensive_audit_2026-05-01.md` |
| `llm-stats-vault/00-home/current-priorities.md` | 27 | `../audit/discovery_audit_2026-05-02.md` | `../90-archive/audit/discovery_audit_2026-05-02.md` |
| `llm-stats-vault/atlas/scoring-pipeline.md` | 26 | `[audit/aggregation_locus.md](../../audit/aggregation_locus.md)` | `[audit/aggregation_locus.md](../90-archive/audit/aggregation_locus.md)` |
| `llm-stats-vault/40-literature/citation-map.md` | 70, 72, 73, 74, 149 | inline `` `audit/<file>` `` × 5 (`rq_restructuring.md`, `methodology_continuity.md`, `literature_comparison.md`, `recompute_log.md`, `limitations_disclosures.md`) | inline `` `../90-archive/audit/<file>` `` × 5 |
| `llm-stats-vault/sessions/2026-05-06-poster-rebuild.md` | 13 | inline `audit/recompute_log.md` | `../90-archive/audit/recompute_log.md` |

### Depth-2 vault files (linker is two levels below vault root)

Old: `../../../audit/<file>` → New: `../../90-archive/audit/<file>`

| File | Line | Form | Replacement |
|---|---|---|---|
| `llm-stats-vault/knowledge/decisions/all-scoring-weights-are-equal-at-0.20.md` | 62 | `[…](../../../audit/aggregation_locus.md)` | `[…](../../90-archive/audit/aggregation_locus.md)` |
| `llm-stats-vault/knowledge/decisions/all-scoring-weights-are-equal-at-0.20.md` | 63 | `[…](../../../audit/recompute_log.md)` | `[…](../../90-archive/audit/recompute_log.md)` |
| `llm-stats-vault/knowledge/decisions/all-scoring-weights-are-equal-at-0.20.md` | 64 | `[…](../../../audit/methodology_continuity.md)` | `[…](../../90-archive/audit/methodology_continuity.md)` |
| `llm-stats-vault/knowledge/patterns/scoring-weights-must-be-updated-in-two-files.md` | 46 | `[…](../../../audit/recompute_log.md)` | `[…](../../90-archive/audit/recompute_log.md)` |
| `llm-stats-vault/knowledge/patterns/perturbation-types-test-three-robustness-axes.md` | 32 | inline `audit/recompute_log.md` | inline `../../90-archive/audit/recompute_log.md` |
| `llm-stats-vault/40-literature/papers/01-original-stateval-2025.md` | 37 | inline `audit/literature_comparison.md` | inline `../../90-archive/audit/literature_comparison.md` |
| `llm-stats-vault/40-literature/papers/11-new-fermieval-2025.md` | 22, 36 | inline `audit/limitations_disclosures.md` × 2 | × 2 |
| `llm-stats-vault/40-literature/papers/12-new-multi-answer-confidence-2026.md` | 22, 35 | inline `audit/limitations_disclosures.md` × 2 | × 2 |
| `llm-stats-vault/40-literature/papers/14-new-judgment-becomes-noise-2025.md` | 35 | inline `audit/limitations_disclosures.md` | × 1 |

### Per-file sed for vault group C

Run from repo root. **Order matters** — replace the longer relative form first to avoid double-rewrite.

```bash
# Depth-1 files (linkers in 00-home/, atlas/, 40-literature/, sessions/)
for f in llm-stats-vault/00-home/research-narrative.md \
         llm-stats-vault/00-home/current-priorities.md \
         llm-stats-vault/atlas/scoring-pipeline.md \
         llm-stats-vault/40-literature/citation-map.md \
         llm-stats-vault/sessions/2026-05-06-poster-rebuild.md ; do
  sed -i '' -E \
    -e 's#\.\./\.\./audit/#../90-archive/audit/#g' \
    -e 's#\.\./audit/#../90-archive/audit/#g' \
    "$f"
  # Bare inline 'audit/<file>' references (no leading '../'):
  sed -i '' -E "s#\`audit/([a-zA-Z0-9_./-]+\.md)\`#\`../90-archive/audit/\1\`#g" "$f"
done

# Depth-2 files (linkers in knowledge/decisions/, knowledge/patterns/, 40-literature/papers/)
for f in llm-stats-vault/knowledge/decisions/all-scoring-weights-are-equal-at-0.20.md \
         llm-stats-vault/knowledge/patterns/scoring-weights-must-be-updated-in-two-files.md \
         llm-stats-vault/knowledge/patterns/perturbation-types-test-three-robustness-axes.md \
         llm-stats-vault/40-literature/papers/01-original-stateval-2025.md \
         llm-stats-vault/40-literature/papers/11-new-fermieval-2025.md \
         llm-stats-vault/40-literature/papers/12-new-multi-answer-confidence-2026.md \
         llm-stats-vault/40-literature/papers/14-new-judgment-becomes-noise-2025.md ; do
  sed -i '' -E \
    -e 's#\.\./\.\./\.\./audit/#../../90-archive/audit/#g' \
    "$f"
  # Bare inline 'audit/<file>' (paper-notes use these):
  sed -i '' -E "s# audit/([a-zA-Z0-9_./-]+\.md)# ../../90-archive/audit/\1#g" "$f"
done
```

**Per-file diff verification will be required after sed (per Phase C step 4).**

---

## D. Vault sibling refs (5 files, 9 refs)

These live inside `llm-stats-vault/90-archive/*/`. After the move, `audit/` is a sibling at `llm-stats-vault/90-archive/audit/`. Old refs that reached *out* of the vault to `<repo_root>/audit/` now resolve *inside* the vault.

| File | Line | Old | New | Note |
|---|---|---|---|---|
| `llm-stats-vault/90-archive/README.md` | 33 | `Active audit deliverables → audit/` | `Active audit deliverables → ./audit/` (sibling) | Edit prose; was descriptive of repo-root `audit/`, now points to sibling subdir. Verify whole paragraph for tense. |
| `llm-stats-vault/90-archive/phase_1c_superseded/README.md` | 22 | `[audit/recompute_log.md](../../../audit/recompute_log.md)` | `[audit/recompute_log.md](../audit/recompute_log.md)` | depth: linker 1 below `90-archive/`; sibling = `../audit/` |
| `llm-stats-vault/90-archive/intermediate_analyses/gemini_verification.md` | 253 | inline `audit/limitations_disclosures.md` | inline `../audit/limitations_disclosures.md` | sibling — depth 1 below 90-archive |
| `llm-stats-vault/90-archive/intermediate_analyses/scripts/self_consistency_proxy.py` | 592 | print string `audit/limitations_disclosures.md` | print string `llm-stats-vault/90-archive/audit/limitations_disclosures.md` | python file: replace with repo-root-relative for clarity (the script is run from repo root per CLAUDE.md) |
| `llm-stats-vault/90-archive/sprint-history-aggregated.md` | 1704, 1706 | text refs `audit/literature_comparison.md`, `audit/rq_reweighting.md` | `../audit/literature_comparison.md`, `../audit/rq_reweighting.md` | depth 0 below 90-archive (file is at 90-archive/ root); sibling = `audit/` (no `../` prefix). **Correct: just `audit/<file>` resolves to sibling for this file**. So no rewrite needed — verify post-move. |
| `llm-stats-vault/90-archive/superseded_scripts/README.md` | 32, 33, 34 | text refs to 3 audit files | `../audit/<file>` × 3 | depth 1 below 90-archive |
| `llm-stats-vault/90-archive/superseded_scripts/recompute_nmacr.py` | 32 | comment `audit/recompute_log.md` | `llm-stats-vault/90-archive/audit/recompute_log.md` (repo-root-relative for python clarity) | |
| `llm-stats-vault/90-archive/_originals/2026-05-01-day3-literature-vault.md` | 141, 143 | text refs `audit/literature_comparison.md`, `audit/rq_reweighting.md` | `../audit/<file>` × 2 | depth 1 below 90-archive |

---

## E. Bundled vault under `capstone-website/backend/static_data/llm-stats-vault/` (4 files, 5 refs)

### Bundling mechanism

**No automated sync script exists.** Verified by:
- `find capstone-website/backend -maxdepth 2 -name '*.sh' -o -name 'sync*' -o -name 'build*' -o -name 'Makefile'` returns nothing actionable.
- `capstone-website/backend/Dockerfile`: `COPY static_data/ ./static_data/` — bundle is consumed as-is into the Docker image; no transform.
- `capstone-website/backend/main.py:33`: `BASE_DIR = Path(os.environ.get("DATA_ROOT", str(Path(__file__).parent.parent.parent)))` — the backend reads from `static_data/` only when `DATA_ROOT=/app/static_data` (Dockerfile sets this); locally it reads from repo root.
- `.gitignore:23`: `!capstone-website/backend/static_data/**` — static_data is force-included against a parent ignore. Confirms manual curation.
- Bundle scope: `find capstone-website/backend/static_data/llm-stats-vault -name '*.md' | wc -l` = 24 vs source 91 → only `40-literature/{papers,textbooks}/` + `40-literature/README.md` + `40-literature/poster-citations.md` are bundled.

### Bundled files needing edits

| Bundled file | Source counterpart | Refs |
|---|---|---|
| `capstone-website/backend/static_data/llm-stats-vault/40-literature/papers/01-original-stateval-2025.md` | `llm-stats-vault/40-literature/papers/01-original-stateval-2025.md` | 1 |
| `capstone-website/backend/static_data/llm-stats-vault/40-literature/papers/11-new-fermieval-2025.md` | source | 2 |
| `capstone-website/backend/static_data/llm-stats-vault/40-literature/papers/12-new-multi-answer-confidence-2026.md` | source | 2 |
| `capstone-website/backend/static_data/llm-stats-vault/40-literature/papers/14-new-judgment-becomes-noise-2025.md` | source | 1 |

### Phase C regen procedure (manual; no script)

After Group C edits land in source vault, copy each edited paper note to its bundled twin:

```bash
cp llm-stats-vault/40-literature/papers/01-original-stateval-2025.md \
   capstone-website/backend/static_data/llm-stats-vault/40-literature/papers/01-original-stateval-2025.md

cp llm-stats-vault/40-literature/papers/11-new-fermieval-2025.md \
   capstone-website/backend/static_data/llm-stats-vault/40-literature/papers/11-new-fermieval-2025.md

cp llm-stats-vault/40-literature/papers/12-new-multi-answer-confidence-2026.md \
   capstone-website/backend/static_data/llm-stats-vault/40-literature/papers/12-new-multi-answer-confidence-2026.md

cp llm-stats-vault/40-literature/papers/14-new-judgment-becomes-noise-2025.md \
   capstone-website/backend/static_data/llm-stats-vault/40-literature/papers/14-new-judgment-becomes-noise-2025.md
```

**Caveat**: bundled paper notes use `../../90-archive/audit/<file>` after edits, but `static_data/llm-stats-vault/90-archive/audit/` doesn't exist in the bundle (90-archive is not bundled). The relative link in the bundled rendered Markdown will be a dangling reference at runtime. **This is acceptable** — the bundled paper notes are served as static text/HTML and the audit links are not interactive in the deployed site (no UI element follows them). If a future feature renders these as live links, the audit dir would need bundling too. Note this in the Phase C commit message.

---

## F. Do-not-touch (3 entries)

| File | Line | Reason |
|---|---|---|
| `llm-stats-vault/.obsidian/workspace.json` | 179 | Already says `"90-archive/audit/recompute_log.md"`. Obsidian session state from prior exploration; correct after move. |
| `llm-stats-vault/sessions/2026-05-07-poster-defense-prep.md` | 253 | Already says `90-archive/audit/`. Already migrated. |
| `llm-stats-vault/cleanup/03a_audit_staging_investigation.md` | 17, 49, 89 | This investigation file describes the staging vs source state; its `audit/` references are correct historical descriptions of the pre-move repo. **DO NOT REWRITE** — the document is a forensic record. |

---

## Phase C — execution sequence (with prep)

### Prep: clear scaffold staging stubs (working tree only; no commit needed)

```bash
rm llm-stats-vault/90-archive/audit/recompute_log.md
rmdir llm-stats-vault/90-archive/audit/
rm llm-stats-vault/90-archive/data/processed_data/results_v2/nmacr_scores_v2.jsonl
rmdir llm-stats-vault/90-archive/data/processed_data/results_v2/
rmdir llm-stats-vault/90-archive/code/scripts/
```

(These stubs were never tracked in git, so deletions don't enter history.)

### Step 1: snapshot

```bash
tar -czf llm-stats-vault/cleanup/pre_audit_migration_snapshot_$(date +%Y%m%d).tar.gz audit/
tar -tzf llm-stats-vault/cleanup/pre_audit_migration_snapshot_$(date +%Y%m%d).tar.gz | wc -l
ls -la llm-stats-vault/cleanup/pre_audit_migration_snapshot_*.tar.gz
```

### Step 2: git mv (preserves history)

```bash
git mv audit/ llm-stats-vault/90-archive/audit/
```

### Step 3: apply Group A (source code) sed

Run the per-file sed commands from Section A. Diff each:
```bash
git diff --stat code/analysis/metrics.py code/models/response_parser.py code/scripts/recompute_downstream.py
```
Expect 5 line changes total. Show diff before staging.

### Step 4: apply Group B (project docs) sed

Run the safe-loop sed for 6 files. Then hand-edit `llm-stats-vault/cleanup/02_reorg_plan.md` per the L52/L54/L407 notes in Section B. Diff each.

### Step 5: apply Group C (vault internal) sed

Run the depth-1 and depth-2 loops. After each file, verify with:
```bash
grep -nE "audit/" <file>          # only intentional new references should remain
```

### Step 6: apply Group D (vault sibling) edits

Per-file hand-edits in order — most are short. Verify each.

### Step 7: regen Group E (bundled vault) via cp

Run the four `cp` commands from Section E.

### Step 8: link-resolution spot checks

For three representative vault files, confirm the new relative links resolve to a real file:
```bash
# depth-1 example
test -f llm-stats-vault/90-archive/audit/aggregation_locus.md && echo "OK: linked from atlas/scoring-pipeline.md (../90-archive/audit/aggregation_locus.md)"

# depth-2 example
test -f llm-stats-vault/90-archive/audit/recompute_log.md && echo "OK: linked from knowledge/patterns/perturbation-types-test-three-robustness-axes.md (../../90-archive/audit/recompute_log.md)"

# sibling example
test -f llm-stats-vault/90-archive/audit/recompute_log.md && echo "OK: linked from 90-archive/phase_1c_superseded/README.md (../audit/recompute_log.md)"
```

### Step 9: full-repo verification grep

```bash
grep -rn -E "(^|[^a-zA-Z0-9_/-])audit/" \
  --exclude-dir=.venv --exclude-dir=node_modules --exclude-dir=.git \
  --exclude-dir=llm-stats-vault/90-archive --exclude-dir=capstone-website/backend/static_data \
  . 2>/dev/null
```

Expected output: empty (or only `llm-stats-vault/cleanup/03a_audit_staging_investigation.md` and `llm-stats-vault/cleanup/03b_audit_ref_rewrite_plan.md` historical descriptions).

### Step 10: tests

```bash
source .venv/bin/activate
pytest code/data_preprocessing/frequentist/test_frequentist.py code/capstone_mcp/test_server.py -v
```
Expected: 53 passing (24 + 29). No new failures from this migration since the changes are docstring/comment text only, no import paths changed.

### Step 11: commits (two logical chunks)

```bash
# Chunk 1: the move itself (preserves git history)
git add llm-stats-vault/90-archive/audit/
# (git mv already staged the moves, but stage tarball + cleanup files)
git add llm-stats-vault/cleanup/pre_audit_migration_snapshot_*.tar.gz llm-stats-vault/cleanup/03a_audit_staging_investigation.md llm-stats-vault/cleanup/03b_audit_ref_rewrite_plan.md
git commit -m "Move audit/ → llm-stats-vault/90-archive/audit/ (git mv, history preserved)

Consolidates archival under llm-stats-vault/90-archive/ per the
single-canonical-archive convention established 2026-05-10. Pre-move
snapshot at llm-stats-vault/cleanup/pre_audit_migration_snapshot_<date>.tar.gz. No
content changes in this commit; ref rewrites land in the next."

# Chunk 2: rewrite all refs
git add code/analysis/metrics.py code/models/response_parser.py code/scripts/recompute_downstream.py \
        CLAUDE.md poster/SCRAPE_PLAN.md capstone-website/mobile-fixes-changelog.md \
        llm-stats-vault/cleanup/01_inventory.md llm-stats-vault/cleanup/01c_error_taxonomy_diff.md llm-stats-vault/cleanup/01e_script_callers.md llm-stats-vault/cleanup/02_reorg_plan.md \
        llm-stats-vault/00-home/research-narrative.md llm-stats-vault/00-home/current-priorities.md \
        llm-stats-vault/atlas/scoring-pipeline.md \
        llm-stats-vault/40-literature/citation-map.md \
        llm-stats-vault/40-literature/papers/01-original-stateval-2025.md \
        llm-stats-vault/40-literature/papers/11-new-fermieval-2025.md \
        llm-stats-vault/40-literature/papers/12-new-multi-answer-confidence-2026.md \
        llm-stats-vault/40-literature/papers/14-new-judgment-becomes-noise-2025.md \
        llm-stats-vault/knowledge/decisions/all-scoring-weights-are-equal-at-0.20.md \
        llm-stats-vault/knowledge/patterns/scoring-weights-must-be-updated-in-two-files.md \
        llm-stats-vault/knowledge/patterns/perturbation-types-test-three-robustness-axes.md \
        llm-stats-vault/sessions/2026-05-06-poster-rebuild.md \
        llm-stats-vault/90-archive/README.md llm-stats-vault/90-archive/phase_1c_superseded/README.md \
        llm-stats-vault/90-archive/intermediate_analyses/gemini_verification.md \
        llm-stats-vault/90-archive/intermediate_analyses/scripts/self_consistency_proxy.py \
        llm-stats-vault/90-archive/superseded_scripts/README.md llm-stats-vault/90-archive/superseded_scripts/recompute_nmacr.py \
        llm-stats-vault/90-archive/_originals/2026-05-01-day3-literature-vault.md \
        llm-stats-vault/90-archive/sprint-history-aggregated.md \
        capstone-website/backend/static_data/llm-stats-vault/40-literature/papers/01-original-stateval-2025.md \
        capstone-website/backend/static_data/llm-stats-vault/40-literature/papers/11-new-fermieval-2025.md \
        capstone-website/backend/static_data/llm-stats-vault/40-literature/papers/12-new-multi-answer-confidence-2026.md \
        capstone-website/backend/static_data/llm-stats-vault/40-literature/papers/14-new-judgment-becomes-noise-2025.md
git commit -m "Rewrite audit/ refs to new vault path across source, docs, and vault links

Updates 62 references across 28 files following the audit/ →
llm-stats-vault/90-archive/audit/ migration. Source code docstrings,
project docs, and vault internal links use depth-appropriate relative
paths. Bundled paper notes under capstone-website/backend/static_data/
manually re-synced (no automated bundler exists)."
```

### Step 12: final verify

```bash
ls audit 2>&1 | head    # No such file or directory
git status -s
git log --oneline -5
```

---

## Files NOT touched in this plan

- `code/scripts/` — out of scope per `llm-stats-vault/cleanup/02_reorg_plan.md` §F; the staging stub is removed in prep but the source `code/scripts/` is untouched.
- Any `.obsidian/` state — Obsidian re-resolves links on next open.
- Pre-existing dirty state (`poster/figures/*`, `report_materials/*`, `data/processed_data/results_v2/error_taxonomy_v2.json`, `poster/scripts/dimension_leaderboard_print.py`) — not from this migration; leave as found.

End of plan.
