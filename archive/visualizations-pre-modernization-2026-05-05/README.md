# Pre-Modernization Visualization Backup

Snapshot date: 2026-05-05

Pre-iteration baseline before applying:
- Tier 1: Universal palette + typography pass
- Tier 2: Chart-type upgrades (Three Rankings, PerDimRobustness, Failure Rate)
- Tier 3: Small-multiples redesigns
- Tier 4: Info-density annotations

## Contents

- `png/` — all PNGs from `capstone-website/frontend/public/visualizations/png/v2/` (17 files)
- `components/` — all live JSX/CSS files referencing Recharts (`App.jsx`, `App.css`, plus `components/JudgeValidationPanels.jsx`, `components/ThreeRankingsComparison.jsx`, `components/MethodologyPanels.jsx`)
- `scripts/` — all Python generator scripts from `scripts/` (22 files)
- `data/` — `visualizations.js` manifest

Per-folder MANIFEST/list files describe exact contents:
- `png/MANIFEST.txt`
- `components/CHART_FILES.txt`
- `scripts/SCRIPT_LIST.txt`

## How to restore a single chart

### Restore a PNG

```bash
cp archive/visualizations-pre-modernization-2026-05-05/png/<filename>.png \
   capstone-website/frontend/public/visualizations/png/v2/<filename>.png
```

### Restore a Recharts component

```bash
cp archive/visualizations-pre-modernization-2026-05-05/components/<path> \
   capstone-website/frontend/src/<path>
```

Example:

```bash
cp archive/visualizations-pre-modernization-2026-05-05/components/components/ThreeRankingsComparison.jsx \
   capstone-website/frontend/src/components/ThreeRankingsComparison.jsx
```

### Restore a generator script

```bash
cp archive/visualizations-pre-modernization-2026-05-05/scripts/<script>.py \
   scripts/<script>.py
```

### Restore the manifest

```bash
cp archive/visualizations-pre-modernization-2026-05-05/data/visualizations.js \
   capstone-website/frontend/src/data/visualizations.js
```

After restoring, rebuild the frontend and redeploy:

```bash
cd capstone-website/frontend && npm run build
```
