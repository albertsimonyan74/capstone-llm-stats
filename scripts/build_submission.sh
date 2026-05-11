#!/usr/bin/env bash
set -euo pipefail

# Build submission archive per capstone-guideline §5.
# Internal tree matches the recommended example structure.
# Run from repo root.

STAGE="capstone_simonyan_submission"
rm -rf "$STAGE" "$STAGE.zip"
mkdir -p "$STAGE"/{paper,code,data}

# paper/
cp paper/main.tex "$STAGE/paper/"
cp paper/sections/*.tex "$STAGE/paper/"
cp paper/bib/refs.bib "$STAGE/paper/references.bib"
cp -r paper/figures "$STAGE/paper/figures"
cp paper/main.pdf "$STAGE/paper/paper.pdf" 2>/dev/null || \
  echo "WARNING: paper/main.pdf missing; compile before building submission"
cp paper/IEEEtran.cls paper/IEEEtran.bst "$STAGE/paper/"

# code/  (map working-repo code dirs into the example tree)
cp -r baseline       "$STAGE/code/data_preprocessing"  # task generation = data prep
cp -r evaluation     "$STAGE/code/analysis"             # scoring = analysis
cp -r llm_runner     "$STAGE/code/models"               # model clients
cp -r scripts        "$STAGE/code/scripts"
cp -r capstone_mcp   "$STAGE/code/capstone_mcp"
cp -r report_materials/r_analysis "$STAGE/code/visualization"

# Strip __pycache__ and renv/library cruft from the staged code copies
find "$STAGE/code" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find "$STAGE/code" -type d -name renv -exec rm -rf {} + 2>/dev/null || true
find "$STAGE/code" -name '.Rhistory' -delete 2>/dev/null || true

# data/  (split into raw vs processed per the example)
cp -r data/benchmark_v1 "$STAGE/data/raw_data"
mkdir -p "$STAGE/data/raw_data/synthetic"
cp -r data/synthetic/* "$STAGE/data/raw_data/synthetic/"
cp -r experiments/results_v2 "$STAGE/data/processed_data"

# Drop oversized JSONL files from processed_data if they exceed 10 MB
find "$STAGE/data/processed_data" -name '*.jsonl' -size +10M -delete 2>/dev/null || true
find "$STAGE/data/processed_data" -name '*.jsonl.bak*' -delete 2>/dev/null || true

# Root-level files
cp README.md "$STAGE/README.md"
cp requirements.txt "$STAGE/requirements.txt"
cp environment.yml "$STAGE/environment.yml" 2>/dev/null || true
cp report_materials/r_analysis/renv.lock "$STAGE/renv.lock" 2>/dev/null || true
cp reproduce.sh "$STAGE/reproduce.sh"
cp bayesian_scope.md "$STAGE/PROJECT_OVERVIEW.md"
cp .env.example "$STAGE/.env.example"
cp CLAUDE.md "$STAGE/CLAUDE.md" 2>/dev/null || true

# Note inside the ZIP that the working repo has a different layout
cat > "$STAGE/STRUCTURE_NOTE.md" <<'EOF'
# Submission Structure Note

This archive's internal structure matches the capstone-guideline §5
recommended example tree. The original working repository has a
different layout optimized for development; mappings:

    Submission                  → Working repo
    code/data_preprocessing/    → baseline/
    code/analysis/              → evaluation/
    code/models/                → llm_runner/
    code/visualization/         → report_materials/r_analysis/
    data/raw_data/              → data/
    data/processed_data/        → experiments/results_v2/

All scripts reference paths relative to the working-repo layout. To
actually run the code, use the working repo (linked in README.md) or
adjust paths after extraction.
EOF

# Zip
zip -rq "$STAGE.zip" "$STAGE"
echo "Built: $STAGE.zip ($(du -h "$STAGE.zip" | cut -f1))"
rm -rf "$STAGE"
