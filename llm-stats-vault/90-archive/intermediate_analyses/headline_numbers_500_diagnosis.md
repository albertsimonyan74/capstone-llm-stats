# /api/v2/headline_numbers 500 — Diagnosis

## 1. Exception
```
AttributeError: 'str' object has no attribute 'get'
```

## 2. Location
[capstone-website/backend/v2_routes.py:220](../capstone-website/backend/v2_routes.py#L220) inside `_build_rankings()`, called from [v2_routes.py:291](../capstone-website/backend/v2_routes.py#L291) (`headline_numbers`).

```python
cal_items = [(m, d.get("ece")) for m, d in calib.items() if d.get("ece") is not None]
```

## 3. Proximate cause
`calibration.json` was extended in the Phase 1B/1C/1.5 refresh with three non-model top-level keys. `_build_rankings()` iterates every top-level key as if each were a model dict and calls `.get("ece")` unconditionally. One of the new keys is a `str`, so `.get` raises.

## 4. Schema mismatch — expected vs actual

`_build_rankings()` expects `calibration.json` to be `{model_family: {ece, ...}}` only.

Actual top-level keys in `experiments/results_v2/calibration.json`:

| Key | Type | Safe for `.get("ece")`? |
|---|---|---|
| `chatgpt` | dict | yes |
| `claude` | dict | yes |
| `deepseek` | dict | yes |
| `gemini` | dict | yes |
| `mistral` | dict | yes |
| `accuracy_calibration_correlation` | dict | yes (returns None) |
| **`accuracy_calibration_correlation_note`** | **str** | **NO → AttributeError** |
| `formatting_failure_rate_per_model` | dict | yes (returns None) |

Reproduced locally:
```
File "v2_routes.py", line 220, in <listcomp>
    cal_items = [(m, d.get("ece")) for m, d in calib.items() if d.get("ece") is not None]
AttributeError: 'str' object has no attribute 'get'
```

## 5. Recommended fix
Single-line guard at [v2_routes.py:220](../capstone-website/backend/v2_routes.py#L220) — filter to dict values only:

```python
cal_items = [(m, d.get("ece")) for m, d in calib.items()
             if isinstance(d, dict) and d.get("ece") is not None]
```

Safer than restructuring the JSON because (a) it tolerates any future metadata sibling keys (note text, correlations, footnotes), and (b) it leaves `calibration.json` schema unchanged for downstream consumers (the `/api/v2/calibration` endpoint at line 398 returns the file as-is).

## 6. Severity
**Can wait for Group D (housekeeping).**

Justification:
- `KeyFindings.jsx` reads `pf?.combined?.pct_pass_flip` from the working `/api/v2/pass_flip` endpoint and falls back to `STATIC_FALLBACK` if `headline_numbers` fails. All 6 hero cards still render with correct values on production.
- No other frontend caller of `/api/v2/headline_numbers` was identified in the React source tree.
- The bug is a one-line iteration guard, not a data corruption — the underlying calibration data is intact and served correctly via `/api/v2/calibration`.

If user-facing breakage emerges (e.g. a future component starts depending on `headline_numbers.rankings`), promote to BLOCKING and ship the one-line fix.
