#!/usr/bin/env bash
set -euo pipefail

# One-command reproduction per capstone-guideline §8.1.
# Default path regenerates figures and the paper PDF from committed
# results in data/processed_data/ — no API keys required.
# Set REGENERATE_BENCHMARK=1 to re-run the full LLM benchmark first
# (paid API calls, ~30 min, requires .env with all six provider keys).
# Run from repo root.

echo "=== [1/6] Checking prerequisites ==="
command -v python3 >/dev/null || { echo "Python 3 required"; exit 1; }
command -v Rscript >/dev/null || { echo "R required for figure regen"; exit 1; }
command -v pdflatex >/dev/null || { echo "TeX Live / TinyTeX required"; exit 1; }
[ -f .env ] || echo "Note: .env not present. Skipping benchmark step."

echo "=== [2/6] Setting up Python environment ==="
python3 -m venv .venv
source .venv/bin/activate
pip install -q -r requirements.txt
export PYTHONPATH="$(pwd)/code:${PYTHONPATH:-}"

echo "=== [3/6] Restoring R environment ==="
cd code/visualization
Rscript -e 'if (!require("renv")) install.packages("renv", repos="https://cloud.r-project.org"); renv::restore()'
cd ../..

if [ "${REGENERATE_BENCHMARK:-0}" = "1" ]; then
  echo "=== [4/6] Re-running full benchmark (paid API calls) ==="
  [ -f .env ] || { echo ".env required for benchmark step"; exit 1; }
  bash code/scripts/refresh_pipeline.sh
else
  echo "=== [4/6] Skipping benchmark (using committed results in data/processed_data/) ==="
fi

echo "=== [5/6] Regenerating figures ==="
cd code/visualization && Rscript run_all.R && cd ../..
cp code/visualization/figures/rank_flow.* paper/figures/ 2>/dev/null || true
cp code/visualization/figures/dimension_leaderboard.* paper/figures/ 2>/dev/null || true

echo "=== [6/6] Compiling paper ==="
cd paper
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
cd ..

echo ""
echo "Done. Paper at paper/main.pdf"
