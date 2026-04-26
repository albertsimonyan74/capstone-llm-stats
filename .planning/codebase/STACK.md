# Technology Stack

**Analysis Date:** 2026-04-26

## Overview

DS 299 Capstone — LLM statistical reasoning benchmark. The project is split into three runtime environments: a Python research/ML backend (benchmark runner, baselines, evaluation), a FastAPI web API, and a React/Vite frontend. A fourth environment — R — handles offline statistical visualization.

---

## Languages

**Primary:**
- Python 3.11 — all benchmark logic, LLM clients, scoring, MCP server, FastAPI backend
- JavaScript (ESM/JSX) — React frontend (`capstone-website/frontend/src/`)

**Secondary:**
- R 4.3.2 — offline statistical analysis and visualization scripts (`report_materials/r_analysis/`)

---

## Runtime

**Python Environment:**
- Python 3.11.5 (enforced by `.venv/lib/python3.11/`)
- Virtual environment: `.venv/` at project root — activate with `source .venv/bin/activate`
- All scripts must be run from project root so absolute imports resolve

**Node Environment:**
- Node.js v25.9.0
- npm 11.12.1

---

## Package Managers

**Python:** pip (lockfile: `requirements.txt` at project root, pinned versions)
- Backend-only subset: `capstone-website/backend/requirements.txt` (3 packages: fastapi, uvicorn, python-multipart)

**JavaScript:** npm
- Lockfile: `capstone-website/frontend/package-lock.json` (present and committed)

---

## Frameworks

**Python Web API:**
- FastAPI 0.111.0 — REST API serving benchmark data (`capstone-website/backend/main.py`)
- Uvicorn 0.30.0 — ASGI server, runs on port 8000

**Python MCP Server:**
- `mcp` (FastMCP) — Model Context Protocol server (`capstone_mcp/server.py`), exposes 8 tools over stdio transport

**React Frontend:**
- React 19.2.4 + React DOM 19.2.4 (`capstone-website/frontend/src/`)
- Motion 12.38.0 — animation library (replaces framer-motion)
- Vite 8.0.4 — build tool and dev server (port 3000, proxies `/api` to `localhost:8000`)
- `@vitejs/plugin-react` 6.0.1 — JSX transform

**Testing:**
- pytest — Python tests (`baseline/frequentist/test_frequentist.py`, `capstone_mcp/test_server.py`)

---

## Key Python Dependencies

**HTTP Client (LLM API calls):**
- `httpx` 0.28.1 — all 5 LLM clients use direct HTTP (no vendor SDKs)

**Scientific / Numerical:**
- `numpy` 2.3.5 — array operations in all baseline modules
- `scipy` 1.17.0 — statistical distributions and integration throughout `baseline/`
- `pandas` 2.3.3 — data manipulation in evaluation and scripts
- `statsmodels` 0.14.6 — regression and frequentist statistics
- `scikit-learn` 1.8.0 — ML utilities
- `numba` 0.63.1 — JIT compilation (dependency of pymc/pytensor)
- `matplotlib` 3.10.8 — plotting (seaborn 0.13.2 also present)

**Probabilistic Programming:**
- `pymc` 5.27.1 — Bayesian modeling (available but not used in main benchmark path; present for Jupyter exploration)
- `pytensor` 2.37.0 — computational graph backend for pymc
- `arviz` 0.23.4 — Bayesian diagnostic plots

**Data & Serialization:**
- `pydantic` — not present; data validation done with plain dicts/dataclasses
- Standard library `json` + `dataclasses` used throughout

**Linting:**
- `ruff` — Python linter (run: `ruff check .`)

**Jupyter:**
- `jupyterlab` 4.5.4, `notebook` 7.3.3 — exploratory analysis environment

---

## Key JavaScript Dependencies

**Production:**
- `react` ^19.2.4
- `react-dom` ^19.2.4
- `motion` ^12.38.0 — animation (Framer Motion successor)

**Development:**
- `vite` ^8.0.4
- `@vitejs/plugin-react` ^6.0.1
- `eslint` ^9.39.4 with `eslint-plugin-react-hooks` ^7.0.1 and `eslint-plugin-react-refresh` ^0.5.2
- `@types/react` ^19.2.14, `@types/react-dom` ^19.2.3

---

## R Packages (Visualization Pipeline)

All scripts in `report_materials/r_analysis/*.R`. Run from that directory: `cd report_materials/r_analysis && Rscript run_all.R`.

- `ggplot2` — static plots
- `plotly` + `htmlwidgets` — interactive HTML charts (14 outputs to `interactive/`)
- `dplyr`, `tidyr`, `tibble`, `readr`, `stringr` — tidyverse data wrangling
- `forcats`, `scales`, `viridis` — ggplot2 helpers
- `ggridges`, `ggrepel`, `patchwork` — ggplot2 extensions
- `gt` — formatted tables
- `jsonlite` — reading `runs.jsonl` and JSON data files

---

## Build & Containerization

**Frontend build:**
```bash
cd capstone-website/frontend && npm run build   # outputs to dist/
```
Docker: `capstone-website/frontend/Dockerfile` — Node 20 Alpine builder → nginx:alpine serving `dist/` on port 80.

**Backend:**
Docker: `capstone-website/backend/Dockerfile` — python:3.11-slim, uvicorn on port 8000.

**Nginx:** `capstone-website/frontend/nginx.conf` — serves static files, proxies `/api/` to `http://backend:8000/api/`.

---

## Configuration

**Environment variables:** Copy `.env.example` → `.env`. All 5 API keys required for full benchmark run.

**Frontend config:**
- `capstone-website/frontend/vite.config.js` — port 3000, `/api` proxy to 8000
- `capstone-website/frontend/eslint.config.js` — flat config, JSX, react-hooks rules

**Python linting:** `ruff check .` — no `ruff.toml` detected; uses defaults.

---

## Platform Requirements

**Development:**
- macOS or Linux (`.venv` path uses unix conventions)
- Python 3.11 (`.venv/lib/python3.11/`)
- Node.js 25.x, npm 11.x
- R 4.3.2 (for visualization pipeline only)

**Production:**
- Docker Compose (two containers: frontend/nginx + backend/uvicorn)
- No cloud-specific infra detected; backend reads local JSONL files from project root

---

*Stack analysis: 2026-04-26*
