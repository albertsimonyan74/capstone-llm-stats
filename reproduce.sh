#!/usr/bin/env bash
set -euo pipefail

# One-command reproduction per capstone-guideline §8.1.
# Regenerates paper figures and the PDF from committed results
# in data/processed_data/. Run from repo root.
#
# Linux/macOS native; Windows via WSL or Git Bash.

echo "=== [1/5] Checking prerequisites ==="
command -v python3 >/dev/null || { echo "Python 3 required"; exit 1; }
command -v pdflatex >/dev/null || { echo "TeX Live / TinyTeX required"; exit 1; }
if command -v Rscript >/dev/null 2>&1; then
    R_AVAILABLE=1
    echo "  R found: supplementary R figures will be regenerated"
else
    R_AVAILABLE=0
    echo "  R not found: skipping supplementary R figures (paper does not depend on them)"
fi

echo "=== [2/5] Setting up Python environment ==="
python3 -m venv .venv
source .venv/bin/activate
pip install -q -r requirements.txt
export PYTHONPATH="$(pwd)/code:${PYTHONPATH:-}"

echo "=== [3/5] Regenerating paper figures (Python) ==="
for f in code/visualization/paper_figures/*_paper.py; do
    echo "  $(basename "$f")"
    python "$f" || { echo "FAILED: $f"; exit 1; }
done

echo "=== [4/5] Regenerating supplementary figures (R, optional) ==="
if [ "$R_AVAILABLE" = "1" ]; then
    (cd code/visualization && \
     Rscript -e 'if (!require("renv", quietly=TRUE)) install.packages("renv", repos="https://cloud.r-project.org"); tryCatch(renv::restore(), error=function(e) message("renv::restore() had errors: ", e$message))' && \
     Rscript run_all.R) || \
        echo "WARNING: R supplementary figure regen had errors (non-blocking; paper does not depend on R figures)"
else
    echo "  Skipped (R unavailable)"
fi

echo "=== [5/5] Compiling paper ==="
cd paper
pdflatex -interaction=nonstopmode main.tex >/dev/null
bibtex main >/dev/null
pdflatex -interaction=nonstopmode main.tex >/dev/null
pdflatex -interaction=nonstopmode main.tex >/dev/null
pdflatex -interaction=nonstopmode main.tex >/dev/null   # 4th pass eliminates label warning
cp main.pdf paper.pdf
cd ..

echo ""
echo "Done. Paper at paper/paper.pdf (also paper/main.pdf)"
