#!/usr/bin/env bash
# scripts/refresh_pipeline.sh
# Full post-benchmark pipeline refresh.
# Run from project root after all model benchmark runs are complete.
#
# Usage:
#   bash scripts/refresh_pipeline.sh              # all steps
#   bash scripts/refresh_pipeline.sh --no-judge   # skip LLM-as-Judge (faster)

set -euo pipefail
cd "$(dirname "$0")/.."

NO_JUDGE=""
if [[ "${1:-}" == "--no-judge" ]]; then
    NO_JUDGE="--no-judge"
fi

source .venv/bin/activate

echo "=== Step 1: Formal scoring (run_benchmark.py) ==="
python -m experiments.run_benchmark $NO_JUDGE

echo ""
echo "=== Step 2: Summarize results (results_summary.json) ==="
python scripts/summarize_results.py

echo ""
echo "=== Step 3: RQ4 perturbation analysis (rq4_analysis.json) ==="
python scripts/analyze_perturbations.py

echo ""
echo "=== Pipeline complete ==="
echo "Outputs:"
echo "  experiments/results_v1/results.json"
echo "  experiments/results_v1/rq4_analysis.json"
echo "  capstone-website/frontend/src/data/results_summary.json"
