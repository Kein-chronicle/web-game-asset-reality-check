#!/usr/bin/env bash
cd "$(dirname "$0")/.."
run() { printf '$ %s\n' "$*"; "$@"; printf '[exit %s]\n\n' "$?"; }
echo "# A page whose font is bundled and declared"
run python3 scripts/font_check.py tests/fixtures/good
echo "# A page that imports its font from a CDN at runtime"
run python3 scripts/font_check.py tests/fixtures/bad_cdn
echo "# A font named first in CSS but never declared with @font-face"
run python3 scripts/font_check.py tests/fixtures/bad_undeclared
echo "# Runtime crash check needs Playwright:  npm install playwright && npx playwright install chromium"
if [ -d node_modules/playwright ] || [ -n "${PW_DIR:-}" ]; then
  run node scripts/pageerror_smoke.mjs tests/fixtures/ok.html
  run node scripts/pageerror_smoke.mjs tests/fixtures/crash_async.html
fi
