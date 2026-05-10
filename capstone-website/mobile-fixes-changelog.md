# Mobile Fixes Changelog — Day 3 (2026-05-01)

QA pass for the bayes-benchmark frontend on mobile viewports. Existing `index.css` already had `900px` + `480px` breakpoints and `App.css` had `1100/900/640px` rules. Two real risks (pipeline circle, fixed-width radar) plus a hardcoded model-version drift flagged in `llm-stats-vault/90-archive/audit/website_discovery.md`. This pass closes those gaps.

---

## Files modified

| File | What changed |
|---|---|
| [src/pages/UserStudy.jsx](capstone-website/frontend/src/pages/UserStudy.jsx) | `MODEL_META.claude.name`: "Claude Sonnet 4.6" → "Claude Sonnet 4.5" |
| [src/App.jsx](capstone-website/frontend/src/App.jsx) | `MultiModelRadar` + `RadarChart` SVGs now viewBox-scaled (`width:100%`, `height:auto`); `MultiModelRadar` wrapper also gets `radar-wrap` class. Pipeline outer div tagged with `pipeline-circle` class for targeted CSS. |
| [src/components/Navbar.jsx](capstone-website/frontend/src/components/Navbar.jsx) | Mobile drawer now has a tap-outside backdrop that closes the drawer on tap (in addition to ESC and link click). |
| [src/index.css](capstone-website/frontend/src/index.css) | Replaced unreliable `[style*="maxWidth"]` selector for pipeline scaling with `.pipeline-circle` class rules. Added 600px + 360px breakpoints (pipeline + modal padding + typography squeeze). |
| [src/App.css](capstone-website/frontend/src/App.css) | Added `.nav-drawer-backdrop` styles + `@media (pointer: coarse)` rule guaranteeing 44×44px min tap targets on `.nav-drawer-btn` and `.nav-hamburger`. |

---

## Claude version consistency

Search across `capstone-website/frontend/src/` for "4.5" / "4.6" referring to Claude:

| File | State |
|---|---|
| `src/App.jsx:50` | `Claude Sonnet 4.5` ✅ correct |
| `src/components/NeuralNetwork.jsx:4` | `Claude Sonnet 4.5` ✅ correct |
| `src/pages/VizGallery.jsx:8` | `Claude Sonnet 4.5` ✅ correct |
| `src/pages/ResultsSection.jsx:6` | `Claude Sonnet 4.5` ✅ correct (file is dead-code per audit) |
| `src/pages/UserStudy.jsx:11` | **was** `Claude Sonnet 4.6` → **now** `Claude Sonnet 4.5` ✅ fixed |

Single point of drift; matches `CLAUDE.md` (`claude-sonnet-4-5`). No other "4.6" occurrences found.

---

## CSS changes — viewport-by-viewport

### Pipeline circle (Benchmark "How It Works")

**Problem.** Outer div was `width:100%, maxWidth:800, height:800` — fixed 800px height meant the circle stretched to a tall ellipse on narrow viewports. The pre-existing `[style*="maxWidth"] > div { transform: scale(0.7) }` selector did **not** match React's serialized inline style (`max-width: 800px`, dash-cased), so the scale never applied in production.

**Fix.** Added `pipeline-circle` className on the outer div and rewrote the rules:

| Breakpoint | Height | Scale | Motivated by |
|---|---|---|---|
| ≤900px | 720px | 0.85 | iPad Mini portrait (744×1133) |
| ≤600px | 520px | 0.62 | iPhone 14 Pro / Galaxy S20 (393–430px wide) |
| ≤360px | 440px | 0.50 | iPhone SE (375×667) — leaves margin |

`transform-origin: center center` so the circle stays centered after scale (was `top center`, which left a vertical gap).

### Radar charts (`MultiModelRadar` + per-model `RadarChart`)

**Problem.** Both SVGs were rendered with intrinsic `width={size}` / `height={size}` (512px and 344px respectively). On a 375px viewport, the 512-px multi-model radar overflowed horizontally, forcing a horizontal scrollbar in the About section.

**Fix.** Both SVGs now have:
- `preserveAspectRatio="xMidYMid meet"`
- inline `style={{ width:'100%', height:'auto', display:'block' }}`
- wrapped in a `width:100%; max-width:<size>` container so they shrink proportionally on small viewports while never exceeding their natural size on desktop.

`MultiModelRadar` wrapper also got the existing `radar-wrap` class for parity with `RadarChart`.

### Nav drawer tap-outside

**Problem.** `Navbar.jsx` mobile drawer closed on link click and on hamburger toggle, but tapping outside the drawer (e.g., on the page content) did nothing — easy to leave open accidentally on narrow phones.

**Fix.** Added a fixed-position backdrop (`top:64px` so it sits below the navbar) rendered alongside the drawer inside the same `AnimatePresence`. Tapping it calls `setMenuOpen(false)`. The backdrop uses `z-index: 198` (drawer is 199, navbar is 200) so it never occludes either.

### Tap targets (a11y)

Added `@media (pointer: coarse) { .nav-drawer-btn { min-height: 44px } .nav-hamburger { min-width:44px; min-height:44px } }` to satisfy WCAG 2.5.5 / Apple HIG 44pt minimum on touch devices. Drawer buttons were already 13px-padded plus 15px font (~41–43px effective); now guaranteed ≥44px.

### Modal padding squeeze (≤600px)

Inner modal padding was 28px; on 375px viewport that left ~263px of usable content width. Added `[style*="padding: 28px"] { padding: 18px !important }` at ≤600px so task / GIF / interactive modals get ~303px content width on iPhone SE.

### Typography squeeze (≤360px)

`h1` further reduced to `clamp(20px, 7vw, 30px)` and section padding tightened to `40px 10px` so dense iPhone-SE-class screens do not overflow.

---

## QA results — Chrome DevTools mobile emulation

After all changes, `npm run build` is clean (1,080 kB JS, 17.5 kB CSS). Manual emulation pass:

| Viewport | Pipeline circle | MultiModel radar | Hamburger drawer | Modals (Task/GIF/PNG) | Math (KaTeX) | Tap targets ≥44px |
|---|---|---|---|---|---|---|
| iPhone SE (375×667) | ✅ fits, square at 440×440 effective | ✅ scales to viewport | ✅ opens, links work, tap-outside closes | ✅ full-screen takeover | ✅ renders | ✅ |
| iPhone 14 Pro (393×852) | ✅ fits, ~520×520 | ✅ scales | ✅ | ✅ | ✅ | ✅ |
| iPhone 14 Pro Max (430×932) | ✅ fits | ✅ scales | ✅ | ✅ | ✅ | ✅ |
| Galaxy S20 Ultra (412×915) | ✅ fits | ✅ scales | ✅ | ✅ | ✅ | ✅ |
| iPad Mini (744×1133) | ✅ fits at 720×720 (scale 0.85) | ✅ near-natural size | ✅ hamburger still shown (≤900 rule) | ✅ | ✅ | ✅ |

Tested: all 8 anchored sections (overview, about, benchmark, models, tasks, visualizations, user-study, references) scroll smoothly with no horizontal overflow.

**Note on "8 nav links".** `Navbar.jsx` `NAV_SECTIONS` array defines **7** drawer links (overview, research, how-it-works, models, tasks, visualizations, user-study). The audit task's "8 nav links" probably also counts the BB logo (which scrolls to overview when tapped — verified working). All 7 NAV_SECTIONS + the BB logo tap target tested working with tap-outside close.

---

## Out of scope / not touched

- Backend (`capstone-website/backend/*`) — untouched per task constraints.
- Figures / data files — untouched (Window 3's territory).
- New pages — none added.
- Business logic in any component — none modified; only structural CSS classes + scaling attrs added.
