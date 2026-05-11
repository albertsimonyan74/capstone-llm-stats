#!/usr/bin/env bash
set -euo pipefail

# One-command reproduction per capstone-guideline §8.1.
# Run from repo root.

echo "=== [1/6] Checking prerequisites ==="
command -v python3 >/dev/null || { echo "Python 3 required"; exit 1; }
command -v Rscript >/dev/null || { echo "R required for figure regen"; exit 1; }
command -v pdflatex >/dev/null || { echo "TeX Live / TinyTeX required"; exit 1; }
[ -f .env ] || { echo ".env missing; copy from .env.example and fill keys"; exit 1; }

echo "=== [2/6] Setting up Python environment ==="
python3 -m venv .venv
source .venv/bin/activate
pip install -q -r requirements.txt
export PYTHONPATH="$(pwd)/code:${PYTHONPATH:-}"

echo "=== [3/6] Restoring R environment ==="
cd code/visualization
Rscript -e 'if (!require("renv")) install.packages("renv", repos="https://cloud.r-project.org"); renv::restore()'
cd ../..

echo "=== [4/6] Running benchmark pipeline ==="
bash code/scripts/refresh_pipeline.sh

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
