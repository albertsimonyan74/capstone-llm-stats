# PROJECT: DS 299 Capstone — LLM Bayesian Benchmark (Completion)

## What
Finish the capstone benchmark project. Four remaining work streams:
1. **New benchmark concepts** — add missing task types, generate tasks, run against all models
2. **Results pipeline** — integrate new runs into metrics/evaluation, refresh results.json
3. **Visualization fixes** — fix "Open Interactive" button, replace unclear R charts with informative ones
4. **Paper-ready state** — complete Gemini runs, run RQ4 synthetic benchmark, final report render

## Why
DS 299 deliverable. Benchmark currently at ~80% completion:
- Gemini missing 62/136 Phase 1 tasks + all 35 Phase 2 tasks
- RQ4 synthetic benchmark (375 runs): 0/375 done
- results.json empty (run_benchmark.py never ran successfully)
- "Open Interactive" viz button broken (Safari iframe blocked)
- Several visualizations unclear/duplicative

## What's Done
- Phase 1: 136 benchmark tasks (31 types, 4 tiers)
- Phase 2: 35 advanced computational Bayes tasks (Gibbs/MH/HMC/RJMCMC/VB/ABC/Hierarchical)
- 4 models complete (Claude/ChatGPT/Mistral/DeepSeek): 136+35=171 tasks each
- Research gap closures: LLM-as-Judge, few-shot CoT, PoT, task validator, bibliography
- Website: React + FastAPI, viz gallery, task browser, leaderboard
- R pipeline: 15 PNGs, 14 interactive HTMLs, master report (9.3MB)
- Codebase map: .planning/codebase/ (7 docs)

## Constraints
- Gemini free tier: 250 RPD limit, 15s inter-request delay required
- All scoring weight changes must update BOTH response_parser.py AND metrics.py
- tasks.json files are generated — never edit manually
- runs.jsonl is append-only
- 5 API keys required (ANTHROPIC/GEMINI/OPENAI/DEEPSEEK/MISTRAL)

## Success Criteria
- [ ] Gemini Phase 1 + Phase 2 complete (171 runs)
- [ ] RQ4 synthetic benchmark complete (375 runs)
- [ ] results.json populated with all 855 runs
- [ ] "Open Interactive" button works in all browsers
- [ ] Visualizations clearly communicate benchmark findings
- [ ] R master report re-rendered with final complete data
- [ ] Any new task types added and benchmarked
