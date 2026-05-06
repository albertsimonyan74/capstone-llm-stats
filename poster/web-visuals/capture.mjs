// Capture three high-DPI PNGs of website infographics.
// Source: https://bayes-benchmark.vercel.app
// Run: node poster/web-visuals/capture.mjs   (from repo root)
import { chromium } from 'playwright'

const URL = 'https://bayes-benchmark.vercel.app'
const OUT = './poster/web-visuals'

// Tag the NMACR Card wrapper (no native id/class — inline-styled).
// pipeline + models have stable section ids.
const TARGETS = [
  { name: 'pipeline.png',      selector: 'section#pipeline' },
  { name: 'models.png',        selector: 'section#models' },
  { name: 'nmacr_weights.png', selector: '[data-capture="nmacr"]' },
]

const browser = await chromium.launch()
const ctx = await browser.newContext({
  viewport: { width: 1600, height: 1200 },
  deviceScaleFactor: 3,                  // retina output for print
})
const page = await ctx.newPage()
await page.goto(URL, { waitUntil: 'domcontentloaded', timeout: 60000 })

// Let canvases (NeuralNetwork, MobiusStrip, GlobeBackground, HeroNetworkBg)
// render at least one frame and let lazy data settle.
await page.waitForTimeout(4000)

// Tag NMACR card wrapper. Smallest div inside section#methodology that
// contains both the .nmacr-segment bar and the .nmacr-cards-grid below.
await page.evaluate(() => {
  const ds = document.querySelectorAll('section#methodology div')
  for (const d of ds) {
    if (
      d.querySelector('.nmacr-segment') &&
      d.querySelector('.nmacr-cards-grid') &&
      !Array.from(d.children).some(c =>
        c.querySelector?.('.nmacr-segment') &&
        c.querySelector?.('.nmacr-cards-grid'))
    ) {
      d.setAttribute('data-capture', 'nmacr')
      return
    }
  }
})

// Freeze CSS animations + transitions. Canvas-based rAF loops can't be
// paused this way — accept whatever frame they're on.
await page.addStyleTag({ content: `
  *, *::before, *::after {
    animation-duration: 0s !important;
    animation-delay: 0s !important;
    transition-duration: 0s !important;
    transition-delay: 0s !important;
  }
` })

// Suppress decorative globe (covers full viewport at low alpha but
// shouldn't bleed into a section-element screenshot — element.screenshot
// only paints the element's box). Still freeze for safety.
await page.waitForTimeout(800)

for (const t of TARGETS) {
  const el = page.locator(t.selector).first()
  await el.scrollIntoViewIfNeeded()
  // Allow any IntersectionObserver-triggered animations one tick.
  await page.waitForTimeout(600)
  await el.screenshot({ path: `${OUT}/${t.name}`, scale: 'device' })
  const box = await el.boundingBox()
  console.log(`Captured ${t.name}  box=${Math.round(box.width)}x${Math.round(box.height)}`)
}

await browser.close()
