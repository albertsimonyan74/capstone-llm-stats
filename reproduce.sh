#!/usr/bin/env bash
set -euo pipefail

# One-command reproduction per capstone-guideline §8.1.
# Regenerates figures and the paper PDF from committed results in
# data/processed_data/. Run from repo root.

echo "=== [1/5] Checking prerequisites ==="
command -v python3 >/dev/null || { echo "Python 3 required"; exit 1; }
command -v Rscript >/dev/null || { echo "R required for figure regen"; exit 1; }
command -v pdflatex >/dev/null || { echo "TeX Live / TinyTeX required"; exit 1; }

echo "=== [2/5] Setting up Python environment ==="
python3 -m venv .venv
source .venv/bin/activate
pip install -q -r requirements.txt
export PYTHONPATH="$(pwd)/code:${PYTHONPATH:-}"

echo "=== [3/5] Restoring R environment ==="
cd code/visualization
Rscript -e 'if (!require("renv")) install.packages("renv", repos="https://cloud.r-project.org"); renv::restore()'
cd ../..

echo "=== [4/5] Regenerating figures ==="
echo "  [a] Paper figures (Python — canonical, used in PDF)"
for f in code/visualization/paper_figures/*_paper.py; do
    echo "      Running $(basename "$f")..."
    python "$f" || { echo "FAILED: $f"; exit 1; }
done
echo "  [b] Supplementary R figures (used by website/poster)"
cd code/visualization && Rscript run_all.R || \
    echo "WARNING: R figure regen had failures (supplementary, non-blocking)"
cd ../..

echo "=== [5/5] Compiling paper ==="
cd paper
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
cp main.pdf paper.pdf
cd ..

echo ""
echo "Done. Paper at paper/paper.pdf (also paper/main.pdf)"
