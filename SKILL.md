---
name: web-asset-reality-check
description: Catch "declared but not real" in built web apps and games - fonts declared but never bundled, @font-face files that do not exist, runtime CDN stylesheets and fonts in an offline-by-design app, and runtime page errors (uncaught exceptions, console errors, failed requests) that the type checker cannot see. Use before shipping a web build, when text renders in a fallback font, or after any code-writing step to smoke-test the page in headless Chromium.
---

# web-asset-reality-check

Recurring failure of AI-built web projects: **declaration != reality.** Gates that read source or CSS strings pass while the
rendered result is something else. Measure the artifact.

## Fonts
Observed in audits of AI-built web games (the author's own; treat the proportions as anecdotal):
- Most builds had **zero font files** in `dist/`; the only font source was a runtime `@import` from a public CDN, contradicting a "client-only, no server" premise (offline, blocked CDN and `file://` silently fall back).
- CSS listed a pixel font first with **no `@font-face`**. Measured headlessly, three different font stacks rendered text with the identical width: all declarations dead, all falling back to the same font.
- Canvas text in game engines used `fontFamily: 'monospace'`, so in-game text was never the pixel font even when the CDN loaded. (This script does not check canvas text; compare rendered widths yourself.)
- `document.fonts.check()` returns true for system fallbacks: not evidence. Compare **rendered widths** of the same string under the declared stack and a generic stack; equal means the declaration is dead.

`scripts/font_check.py dist/` checks: (1) font files exist, (2) every `url()` inside an `@font-face` resolves to a file in the build, (3) every first-choice family has an `@font-face`,
(4) no external stylesheet or font at runtime (`@import` and `<link rel=stylesheet>`). Exit `3` if there is no CSS or HTML to measure.

## Runtime crashes tsc cannot see
- With Phaser, `import { Scene } from 'phaser'` compiles (ambient global types) but `Phaser.Math.Between(...)` crashes at runtime with
  `Phaser is not defined`. Add `import * as Phaser from 'phaser'` (or import the specific namespaces).
- If the crash happens inside an async callback (`document.fonts.ready.then(...)`), it surfaces as an unhandled rejection; the only
  symptom is "some HUD text never appears".
- `scripts/pageerror_smoke.mjs <url|file>` opens the page in headless Chromium and fails on `pageerror`, `console.error`, or failed
  requests. Run it after *every* code-writing step, not only at the end. Exit 3 = could not measure (Playwright missing, page could not be loaded). Install Playwright next to the script or in the project you run it from.

## Not covered here
Whether sprites are actually drawn is a rendering question: pair this with [`canvas-render-pixel-gate`](https://github.com/Kein-chronicle/canvas-render-pixel-gate) (rendered pixel richness). A `load.image` count proves the code references sprites, not that they are visible.

```bash
python3 scripts/font_check.py dist/
node scripts/pageerror_smoke.mjs http://localhost:8080/        # needs `npm i -D playwright`
PW_DIR=/path/to/project-with-playwright bash tests/run.sh
```
