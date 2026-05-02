---
tags: [session, website, ui, deployment]
date: 2026-04-28
---

# Session: UI Overhaul Part 2

## Status at Session End

Continuing from [[2026-04-27-website-ui-viz-overhaul]]. New 10-item task list received.

Previous session completed items 1–5 from the new list (confirmed via todo state):
1. ✅ Remove Timeline section
2. ✅ Move Research Questions to top + enhance visually
3. ✅ Clean References: remove lectures, add links, merge papers+textbooks into separate sections
4. ✅ Redesign How It Works as animated circle + deployment/RQ/user-study info
5. ✅ Make Difficulty Ladder + Scoring boxes fully horizontal

## Remaining Items (not yet applied)

6. ✅ **Viz Gallery expandable** — wrapped leaderboard/filter/gallery/footer in `{sectionOpen && <motion.div>}` with AnimatePresence fade-in. Collapsed by default.

7. ✅ **Phase 2 filter label** — `'Comp. Bayes'` → `'MCMC · VB · ABC'`

8. ✅ **Phase 2 task descriptions** — TaskCard now uses TASK_TYPE_TOOLTIPS description when `category === 'computational_bayes'` and task.description < 20 chars.

9. ✅ **Capability Radar** — dynamic textAnchor (end/start/middle based on lx vs cx); pad 32→48 / 36→52; label offset R+26→R+38 / R+28→R+42. No more clipping.

10. ✅ **Git commit + push** → commit 84fa12a → Vercel deploying.

**Also done:** TASK_TYPE_TOOLTIPS textbook fields — removed all `Lecture NN ·` prefixes.

## Key Code Locations

| Item | File | Lines |
|------|------|-------|
| VizGallery sectionOpen content | `VizGallery.jsx` | 432–605 |
| Phase 2 filter label | `App.jsx` | 1293 |
| TaskCard description logic | `App.jsx` | 1524–1527 |
| TASK_TYPE_TOOLTIPS textbook fields | `App.jsx` | 146–184 |
| RadarChart | `App.jsx` | 685–734 |
| NeuralNetwork | `components/NeuralNetwork.jsx` | full file |

## Notes

- Lecture references in TASK_TYPE_TOOLTIPS textbook fields should be removed (e.g. `'Lecture 21 · Carlin & Louis Ch.2'` → `'Carlin & Louis Ch.2'`)
- Radar SVG has `overflow="visible"` but container may clip; increase pad and use dynamic textAnchor
- NeuralNetwork canvas: dpr/HiDPI already handled correctly; "low quality" likely means too few background nodes or weak glow effects
- `tasks.json` frontend has `description: 'Gibbs'` for Phase 2 — don't need to touch the JSON file, just fix the TaskCard render logic
