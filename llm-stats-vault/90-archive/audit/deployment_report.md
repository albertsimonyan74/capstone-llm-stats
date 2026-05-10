# Day 3 Deployment Report — 2026-05-01

## URLs
- Frontend: https://bayes-benchmark.vercel.app
- Backend: https://bayes-benchmark.onrender.com
- QR target: https://bayes-benchmark.vercel.app/poster

## Backend smoke test (Render)

| Endpoint | Status | Notes |
|----------|--------|-------|
| `/api/v2/health` | 200 ✅ | `ok=true` · 6 / 6 required files exist + parse |
| `/api/v2/headline_numbers` | 200 ✅ | `pass_flip_rate=0.2502` (274/1095) · `α=0.5502` interpretation `questionable` · dominant `ASSUMPTION_VIOLATION 46.85%` · `n_runs=2365` `n_perturbations=473` |
| `/api/v2/rankings` | 200 ✅ | accuracy + robustness + calibration each populated · `models=[claude,chatgpt,gemini,deepseek,mistral]` |
| `/api/v2/error_taxonomy` | 200 ✅ | `n_failures_classified=143` · `judge_model=meta-llama/Llama-3.3-70B-Instruct-Turbo` · L1 totals `{ASSUMPTION_VIOLATION:67, MATHEMATICAL_ERROR:48, FORMATTING_FAILURE:18, CONCEPTUAL_ERROR:10}` (HALLUCINATION 0 — empty bucket disclosed in Limitations) |
| `/api/v2/robustness` | 200 ✅ | `n_perturbations=2365` · ranking ChatGPT Δ=−0.0007, DeepSeek Δ=+0.0006, Mistral +0.0135, Gemini +0.016, Claude +0.0194 |
| `/api/v2/agreement` | 200 ✅ | `n_joined=1095` · `flip_pct=25.02%` · `α=0.5502` 95% CI [0.504, 0.595] |
| `/api/v2/calibration` | 200 ✅ | verbalized: 5 models · consistency: 30 tasks (B3 stratum) |
| `/api/v2/literature` | 200 ✅ | `totals.all=22` · `papers=15` (originals=5 + new=10) · `textbooks=7` |

### v1 regression check
- `/api/status` → `total_tasks=171` `benchmark_ready=true` ✅
- `/api/leaderboard` → 200, returns `{"ranking": [], "total_runs": 0}`. v1 runs.jsonl on Render is empty bundle copy from previous deploys; not a regression.

## Frontend smoke test (Vercel)

| Route | Status | Notes |
|-------|--------|-------|
| `/` | 200 ✅ | SPA shell loads `/assets/index-CxkvZrqc.js` (matches local `npm run build`) |
| `/poster` | 200 ✅ | Direct URL hits SPA fallback (`vercel.json` rewrite); same JS bundle |
| `/api/v2/health` (proxy) | 200 ✅ | `vercel.json` rewrite proxies to Render — `ok=true 6/6` confirmed |
| `/visualizations/png/v2/three_rankings.png` | 200 ✅ | 407 591 bytes |
| `/visualizations/png/v2/agreement_metrics_comparison.png` | 200 ✅ | |
| `/visualizations/png/v2/error_taxonomy_hierarchical.png` | 200 ✅ | |
| `/visualizations/png/v2/a2_accuracy_by_category.png` | 200 ✅ | |
| `/visualizations/png/v2/bootstrap_ci.png` | 200 ✅ | 149 224 bytes |
| `/visualizations/png/v1/01_model_heatmap.png` (archive) | 200 ✅ | 343 603 bytes |

## KeyFindings live-fetch
- Verified populating from `/api/v2/headline_numbers` on production: **YES**
- Vercel proxy `/api/(.*) → bayes-benchmark.onrender.com/api/$1` confirmed working with payload `pass_flip_rate=0.2502, α=0.5502, dominant=ASSUMPTION_VIOLATION 46.85%`. KeyFindings component computes the 6 cards from this payload directly.

## QR code
| Field | Value |
|-------|-------|
| Target | `https://bayes-benchmark.vercel.app/poster` |
| File | `report_materials/poster_qr.png` |
| Labeled | `report_materials/poster_qr_labeled.png` (label: "Or visit: bayes-benchmark.vercel.app/poster") |
| Site copy | `capstone-website/frontend/public/qr/poster_qr.png` |
| Size | 900 × 900 px (labeled: 900 × 980 px) |
| QR version | 5 (37 × 37 modules) |
| Error correction | H (highest, 30% recovery) |
| Box size | 20 px / module |
| Border | 4 modules |
| Print recommendation | 2-inch square minimum for reliable scanning at 3-foot distance; 1-inch is the floor |

Test scan: encoding deterministic (PIL/qrcode reproducible). Round-trip decode via pyzbar not run — `libzbar` binary not in repo deps. Scan with phone camera before printing the poster.

## Bundle size
- Frontend JS: 1 118.12 kB (gzip 323.55 kB) — single chunk
- Frontend CSS: 17.51 kB (gzip 4.53 kB)
- Decision: acceptable for May 8; no code-splitting needed. Vite warning about >500 kB chunks noted, deferred.

## Issues encountered + resolutions

### Issue 1 — v2 data files not on Render after first push
**Symptom:** `/api/v2/health` returned `ok=false 2/6` even after backend `git push`.
**Diagnosis:** `render.yaml` declares `env: python` (not Docker), so the Dockerfile's `DATA_ROOT=/app/static_data` is inert. v2_routes.py falls back to `BASE_DIR = repo root`. Files I bundled under `capstone-website/backend/static_data/` were therefore invisible to the running app.
**Fix:** committed the same JSON + literature files at repo root paths (`experiments/results_v2/*.json`, `data/synthetic/perturbations_all.json`, `llm-stats-vault/40-literature/papers/*.md`, `llm-stats-vault/40-literature/textbooks/*.md`) in commit `016c40a`. static_data copies kept for any future Docker switch.

### Issue 2 — Render not auto-deploying the second push
**Symptom:** After commit `016c40a`, Render stayed on the prior build for 10+ minutes; health still `2/6`.
**Diagnosis:** Render Free tier appears to coalesce / drop rapid sequential auto-deploy events.
**Fix:** pushed an empty commit `2b07869` ("deploy: trigger Render redeploy"). Render picked it up within ~2 min. After ~3 min total, health flipped to `ok=true 6/6`.

### Issue 3 — Dockerfile didn't COPY v2_routes.py
**Symptom:** Would have caused ImportError on a Docker build.
**Fix:** updated Dockerfile in same backend commit (`a93f8f0`) — `COPY main.py user_study.py v2_routes.py ./`. Defensive only; current Render path is Python builder.

## Final state
| Artifact | Value |
|----------|-------|
| Frontend HEAD | `2b07869` (deployed, bundle hash `index-CxkvZrqc.js`) |
| Backend HEAD | `2b07869` |
| v2 figures live | 15 (under `/visualizations/png/v2/`) |
| v1 figures archived | 19 (under `/visualizations/png/v1/`, served, not rendered) |
| References live | 22 (15 papers + 7 textbooks via `/api/v2/literature`) |
| Render free-tier first-request latency | ~0.5 s (warm) |
| Render redeploy wall-clock (post empty commit) | ~3 min |

## Deferred items
- Cross-device physical scan validation — relies on a phone in front of the screen, deferred to in-person poster session.
- pyzbar round-trip QR decode test — `libzbar` not available in the repo venv; encoding determinism trusted.
- v1 `/api/leaderboard` returning 0 rows — v1 runs.jsonl not redeployed; not blocking, v1 is legacy.

---

## Final print

- Production /poster URL: **https://bayes-benchmark.vercel.app/poster**
- 8 backend endpoints: **all 200 ✅**
- KeyFindings live-fetch on production: **YES**
- QR code path: **report_materials/poster_qr.png** (+ labeled variant + site copy)
- Total deploy wall-clock: **~25 min** (3 git pushes + Render redeploy + Vercel deploy + smoke test + QR generation)
- Failures: **none after Issue 1/2 resolved**
