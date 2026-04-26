---
tags: [home, index, dashboard]
date: 2026-04-26
---

# LLM Statistical Reasoning Benchmark — Knowledge Base

> DS 299 Capstone: Benchmarking 5 LLMs on inferential and Bayesian statistical reasoning across 171 tasks.

## Run Status Snapshot (2026-04-26 — COMPLETE)

| Model | Phase 1 (136) | Phase 2 (35) | Synthetic (75) |
|-------|--------------|-------------|----------------|
| claude | ✅ 136/136 | ✅ 35/35 | ✅ 75/75 |
| chatgpt | ✅ 136/136 | ✅ 35/35 | ✅ 75/75 |
| deepseek | ✅ 136/136 | ✅ 35/35 | ✅ 75/75 |
| mistral | ✅ 136/136 | ✅ 35/35 | ✅ 75/75 |
| gemini | ✅ 136/136 | ✅ 35/35 | ✅ 75/75 |

**Total:** 1230 records (855 benchmark + 375 synthetic). No error records.

**Leaderboard (formal scoring):** Claude 0.683 > Mistral 0.644 > Gemini 0.642 > DeepSeek 0.625 > ChatGPT 0.621

**RQ4 Robustness:** ChatGPT 0.931 > Mistral 0.925 > Claude 0.915 > DeepSeek 0.901 > Gemini 0.896

**results.json:** ✅ Populated (5 models × 171 tasks = 855 entries)  
**rq4_analysis.json:** ✅ Complete (375 triples, all 5 models)  
**R report:** ✅ Re-rendered 2026-04-26, 9.6 MB, all 5 models

## Navigation

### Atlas (System Architecture)
- [[architecture]] — component map, module roles, data flow
- [[stack]] — Python 3.11, React 19, FastAPI, R 4.3.2, MCP
- [[scoring-pipeline]] — dual paths, weight reconciliation, LLM-as-Judge
- [[data-flow]] — task spec → runs.jsonl → results.json → website

### Active Priorities
- [[current-priorities]] — what remains before paper submission

### Key Knowledge
- [[five-research-questions-define-benchmark-scope]] — RQ1–RQ5
- [[all-scoring-weights-are-equal-at-0.20]] — why N=M=A=C=R=0.20
- [[adding-a-new-task-type-requires-4-changes]] — contribution checklist
- [[scoring-weights-must-be-updated-in-two-files]] — critical sync rule
- [[obsidian-vault-is-persistent-session-memory]] — vault + CLAUDE.md division of responsibility
- [[proposal-gap-user-study-not-implemented]] — user study from proposal: open item
- [[proposal-gap-error-taxonomy-analysis-missing]] — error_taxonomy.py stub needs analysis pipeline

### Sessions
- [[2026-04-26-vault-creation-and-workflow-setup]] — vault built, session workflow established
- [[2026-04-26-research-gap-closures-and-roadmap]] — LLM-as-Judge, PoT, few-shot, bibliography
- [[2026-04-26-benchmark-completion-and-r-report]] — all 5 models complete, R re-render, doc updates
- [[2026-04-26-error-taxonomy-pipeline]] — error taxonomy pipeline (E1-E9), proposal gap closed, vault updated

## Quick Commands

```bash
source .venv/bin/activate

# Full pipeline refresh (post-benchmark)
bash scripts/refresh_pipeline.sh

# Start website
cd capstone-website && uvicorn backend.main:app --reload
cd capstone-website/frontend && npm run dev

# Re-render R report
cd report_materials/r_analysis && Rscript run_all.R

# Run tests
pytest baseline/frequentist/test_frequentist.py capstone_mcp/test_server.py -v

# Error taxonomy (future — needs analysis script)
python scripts/analyze_errors.py  # NOT YET WRITTEN
```
