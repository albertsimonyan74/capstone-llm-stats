#!/usr/bin/env bash
set -euo pipefail

# Build submission archive per capstone-guideline §5.
# Working repo now matches §5 layout (Phase 10 refactor), so this is
# mostly an identity copy with cruft stripping and size limits.
# Run from repo root.

STAGE="capstone_simonyan_submission"
rm -rf "$STAGE" "$STAGE.zip"
mkdir -p "$STAGE"/{paper,code,data}

# paper/
cp paper/main.tex "$STAGE/paper/"
cp paper/sections/*.tex "$STAGE/paper/"
cp paper/references.bib "$STAGE/paper/references.bib"
cp -r paper/figures "$STAGE/paper/figures"
cp paper/main.pdf "$STAGE/paper/paper.pdf" 2>/dev/null || \
  echo "WARNING: paper/main.pdf missing; compile before building submission"
cp paper/IEEEtran.cls paper/IEEEtran.bst "$STAGE/paper/"

# code/  (identity copy — working repo already §5-shaped)
cp -r code/data_preprocessing  "$STAGE/code/data_preprocessing"
cp -r code/analysis            "$STAGE/code/analysis"
cp -r code/models              "$STAGE/code/models"
cp -r code/scripts             "$STAGE/code/scripts"
cp -r code/capstone_mcp        "$STAGE/code/capstone_mcp"
cp -r code/visualization       "$STAGE/code/visualization"

# Strip __pycache__ and renv/library cruft from the staged code copies
find "$STAGE/code" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find "$STAGE/code" -type d -name renv -exec rm -rf {} + 2>/dev/null || true
find "$STAGE/code" -name '.Rhistory' -delete 2>/dev/null || true

# data/  (identity copy — working repo already §5-shaped)
cp -r data/raw_data       "$STAGE/data/raw_data"
cp -r data/processed_data "$STAGE/data/processed_data"

# Drop oversized JSONL files from processed_data if they exceed 10 MB
find "$STAGE/data/processed_data" -name '*.jsonl' -size +10M -delete 2>/dev/null || true
find "$STAGE/data/processed_data" -name '*.jsonl.bak*' -delete 2>/dev/null || true

# Root-level files
cp README.md "$STAGE/README.md"
cp requirements.txt "$STAGE/requirements.txt"
cp environment.yml "$STAGE/environment.yml" 2>/dev/null || true
cp code/visualization/renv.lock "$STAGE/renv.lock" 2>/dev/null || true
cp reproduce.sh "$STAGE/reproduce.sh"
cp .env.example "$STAGE/.env.example"
cp CLAUDE.md "$STAGE/CLAUDE.md" 2>/dev/null || true
cp conftest.py "$STAGE/conftest.py" 2>/dev/null || true

# Zip
zip -rq "$STAGE.zip" "$STAGE"
echo "Built: $STAGE.zip ($(du -h "$STAGE.zip" | cut -f1))"
rm -rf "$STAGE"
