# web-game-asset-reality-check

**Catch web-game bugs the type checker can't: fonts that are declared but not shipped, runtime CDN dependencies, and page errors from headless Chromium.**

[![test](https://github.com/Kein-chronicle/web-game-asset-reality-check/actions/workflows/test.yml/badge.svg)](https://github.com/Kein-chronicle/web-game-asset-reality-check/actions/workflows/test.yml) ![license](https://img.shields.io/badge/license-MIT-blue.svg)

## Why

A build can type-check and still reference a font file that is not in the bundle, load its font from a CDN that is blocked offline, or throw `Phaser is not defined` inside an async callback. These checks find those, and treat "nothing to measure" as unmeasured, not clean.

## Install

**As a Claude Code skill** (Claude uses it when the task matches the skill description):

```sh
git clone https://github.com/Kein-chronicle/web-game-asset-reality-check.git ~/.claude/skills/web-asset-reality-check
```

For a single project, clone into `<project>/.claude/skills/web-asset-reality-check` instead, then start a new Claude Code session.

**As plain scripts:**

```sh
git clone https://github.com/Kein-chronicle/web-game-asset-reality-check.git
cd web-game-asset-reality-check
```

**Requires:** Node.js 22+ and Python 3.10+, Playwright (optional, for pageerror_smoke.mjs).

Install the browser test runtime:

```sh
npm install --no-save playwright@1.64.1
npx playwright install chromium
```

## Quick start

Check three font setups:

```console
$ bash examples/demo.sh
# A page whose font is bundled and declared
$ python3 scripts/font_check.py tests/fixtures/good
font files: pixel.woff2; @font-face families: ['pixel']
ok: declared fonts exist and nothing loads from a runtime CDN
[exit 0]

# A page that imports its font from a CDN at runtime
$ python3 scripts/font_check.py tests/fixtures/bad_cdn
font files: none; @font-face families: none
style.css: first-choice font 'vt323' has no @font-face in the build (dead declaration)
style.css: runtime external dependency https://fonts.googleapis.com/css2?family=VT323 (breaks offline / blocked CDN / file://)
[exit 1]

# A font named first in CSS but never declared with @font-face
$ python3 scripts/font_check.py tests/fixtures/bad_undeclared
font files: none; @font-face families: none
style.css: first-choice font 'press start 2p' has no @font-face in the build (dead declaration)
[exit 1]

# Runtime crash check needs Playwright:  npm install playwright && npx playwright install chromium
$ node scripts/pageerror_smoke.mjs tests/fixtures/ok.html
UNMEASURED: playwright not installed (npm install playwright && npx playwright install chromium)
[exit 3]

$ node scripts/pageerror_smoke.mjs tests/fixtures/crash_async.html
UNMEASURED: playwright not installed (npm install playwright && npx playwright install chromium)
[exit 3]
```

The output above is real: it is produced by the files in `examples/`.

## Use it on your own files

```sh
python3 scripts/font_check.py ./dist
node scripts/pageerror_smoke.mjs http://localhost:5173/   # needs: npm install playwright
```

Sample inputs for every file format are in `examples/` and `tests/`; the details are in [SKILL.md](SKILL.md).

## What it checks

- `font_check.py DIR`: every `url()` in an `@font-face` resolves to a file in the build, first-choice fonts have an `@font-face`, no external stylesheet or font loaded at runtime (`@import`, `<link>`). Exit `3` if there is no CSS or HTML.
- `pageerror_smoke.mjs [--wait MS] URL|FILE` opens the page in headless Chromium and fails on `pageerror`, `console.error` or failed requests. Exit `3` if Playwright is missing or the page cannot be loaded (needs `npm install playwright`).

## Limits

- The smoke test needs `npm install playwright` and a Chromium download.
- Fonts and runtime errors only: not images, audio or canvas text.

## Related projects

These solve neighbouring problems; use them when they fit better.

- **Lighthouse**: audits a deployed page; this checks a local build

## More from the same collection

Small, tested tools that grew out of running AI agents and game/app pipelines for months:

- [**canvas-render-pixel-gate**](https://github.com/Kein-chronicle/canvas-render-pixel-gate): Detect grey-box screenshots: measure unique colors and flat-fill share of a rendered game canvas, and refuse to pass what it could not measure.
- [**ffmpeg-video-qa-gates**](https://github.com/Kein-chronicle/ffmpeg-video-qa-gates): Machine QA for short videos with ffmpeg: frozen frames, dead air, loudness, true peak, size, a busy opening, and readable subtitle timing.
- [**cold-read-comprehension-review**](https://github.com/Kein-chronicle/cold-read-comprehension-review): Grade whether a video or page communicates, using independent cold readers checked against the author's truth file, and flag stale judgements.

## Development

```sh
env REQUIRE_BROWSER=1 bash tests/run.sh
```

The tests include inputs that are supposed to be rejected, so a green run also shows the checks can fail. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).

If this saved you a debugging session, a star helps other people find it. Bug reports and failing test cases are even better.

<sub>Keywords: web-development, game-development, testing, playwright, fonts, smoke-test, phaser, claude-skills</sub>
