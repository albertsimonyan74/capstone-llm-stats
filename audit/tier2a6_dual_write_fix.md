# Tier 2A.6 — Dual-write Bug + Fix (2026-05-05)

## Bug

Tier 2A spec required every visualization generator to dual-write to:
- `report_materials/figures/<name>.png` (poster export, full-resolution)
- `capstone-website/frontend/public/visualizations/png/v2/<name>.png` (site)

Two generators in `scripts/generate_group_a_figures.py` only wrote the
report_materials path — the public copy went stale and the site continued
serving an older version.

| function | output | second write fixed? |
|---|---|---|
| `figure_a1` | `a1_failure_by_tasktype.png` | already dual-write ✓ |
| `figure_a2` | `a2_accuracy_by_category.png` | already dual-write ✓ |
| `figure_a3` | `a3_failure_heatmap.png` (and `_full`) | already dual-write ✓ |
| **`figure_a4`** | `a4_robustness_by_perttype.png` | **NO — fixed in this commit** |
| **`figure_a5`** | `a5_calibration_reliability.png` | **NO — fixed in this commit** |
| `figure_a6` | `a6_aggregate_ranking.png` | already dual-write ✓ |

## Evidence (pre-fix mtimes)

```
report_materials/figures/a4_robustness_by_perttype.png : 12:00
public/v2/a4_robustness_by_perttype.png                : 02:04   ← 10h stale
report_materials/figures/a5_calibration_reliability.png: 12:00
public/v2/a5_calibration_reliability.png               : 02:04   ← 10h stale
```

`a3_failure_heatmap.png` was also flagged stale (rm 14:08 / pub 12:00) but
the dual-write was already correct — the gap reflected an older invocation
that wrote to both, then a follow-up regen of just `figure_a2` chained into
the wrong call path. Re-running `generate_group_a_figures.py` resyncs.

## Fix

Both functions now follow the established pattern (cf. `figure_a1`):

```python
fig.savefig(out, dpi=300, facecolor=SITE_BG, bbox_inches="tight")
fig.savefig(WEB_DIR / "<name>.png",
            dpi=150, facecolor=SITE_BG, bbox_inches="tight")
plt.close(fig)
```

`WEB_DIR` is the canonical public/v2 path established at module top.

## Validation

After fix + `python scripts/generate_group_a_figures.py`:

```
public/v2/a3_failure_heatmap.png        : 15:56  (matches rm)
public/v2/a4_robustness_by_perttype.png : 15:56  (matches rm)
public/v2/a5_calibration_reliability.png: 15:56  (matches rm)
```

All six A-series outputs now sync rm ↔ pub on every regen. Future Tier 2A.x
chart edits should keep this invariant.
