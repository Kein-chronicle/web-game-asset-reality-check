#!/usr/bin/env bash
set -u; here="$(cd "$(dirname "$0")" && pwd)"; s="$here/../scripts"; f="$here/fixtures"; bad=0
t() { name="$1"; want="$2"; shift 2; out="$("$@" 2>&1)"; got=$?; [ "$got" = "$want" ] && echo "ok   $name" || { echo "FAIL $name (want $want got $got)"; echo "$out"|sed 's/^/     /'; bad=1; }; }
t "bundled font with @font-face passes" 0 python3 "$s/font_check.py" "$f/good"
t "runtime CDN import is caught"        1 python3 "$s/font_check.py" "$f/bad_cdn"
t "dead font declaration is caught"     1 python3 "$s/font_check.py" "$f/bad_undeclared"
t "@font-face pointing at a missing file is caught even if another font exists" 1 python3 "$s/font_check.py" "$f/bad_missing_src"
out="$(python3 "$s/font_check.py" "$f/bad_missing_src" 2>&1)"; echo "$out" | grep -q "does not exist in the build" && echo "ok   ...for the right reason" || { echo "FAIL missing-src reason"; bad=1; }
t "external <link> stylesheet is caught" 1 python3 "$s/font_check.py" "$f/bad_link"
t "no css/html => unmeasured, not clean" 3 python3 "$s/font_check.py" "$(mktemp -d)"
if [ -n "${PW_DIR:-}" ]; then ln -sfn "$PW_DIR/node_modules" "$s/node_modules"; trap 'rm -f "$s/node_modules"' EXIT; fi
if (cd "$s" && node -e "import('playwright').then(()=>process.exit(0),()=>process.exit(1))" 2>/dev/null); then
  t "clean page passes"                  0 node "$s/pageerror_smoke.mjs" "$f/ok.html"
  t "async crash (Phaser not defined) is caught" 1 node "$s/pageerror_smoke.mjs" "$f/crash_async.html"
  out="$(node "$s/pageerror_smoke.mjs" "$f/crash_async.html" 2>&1)"; echo "$out" | grep -q "Phaser is not defined" && echo "ok   ...for the right reason" || { echo "FAIL crash reason"; bad=1; }
  t "unreachable server is 'unmeasured' (3), not a crash" 3 node "$s/pageerror_smoke.mjs" "http://127.0.0.1:9/"
  t "--wait before the URL is parsed correctly" 0 node "$s/pageerror_smoke.mjs" --wait 100 "$f/ok.html"
else [ "${REQUIRE_BROWSER:-0}" = 1 ] && { echo "UNMEASURED: required browser checks unavailable"; exit 3; }; echo "skip pageerror tests (Playwright not found: npm install playwright && npx playwright install chromium, or set PW_DIR)"; fi
exit $bad
