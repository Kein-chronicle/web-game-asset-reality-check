#!/usr/bin/env node
// Open the page in headless Chromium and fail on ANY uncaught error / unhandled rejection / console.error.
// Why: tsc passing proves nothing at runtime (e.g. `import { Scene } from 'phaser'` compiles but `Phaser.Math` crashes at
// runtime), and a crash inside an async callback is swallowed as an unhandled rejection - the only symptom is "later UI never appears".
// usage: node pageerror_smoke.mjs <url|file.html> [--wait 1500]   exit 0 clean | 1 errors | 3 unmeasured (no playwright)
import { resolve } from 'node:path'; import { existsSync } from 'node:fs'; import { pathToFileURL } from 'node:url';
const a = process.argv.slice(2); const wi = a.indexOf('--wait');
const target = a.find((x, i) => !x.startsWith('--') && !(wi >= 0 && i === wi + 1));
const wait = wi >= 0 ? Number(a[wi + 1]) : 1500;
if (!Number.isFinite(wait) || wait < 0) { console.error('--wait needs a number of milliseconds'); process.exit(2); }
if (!target) { console.error('usage: pageerror_smoke.mjs <url|file>'); process.exit(2); }
let chromium;
try { ({ chromium } = await import('playwright')); }
catch {   // not next to this script: try the project you run it from
  try { const { createRequire } = await import('node:module'); ({ chromium } = await import(pathToFileURL(createRequire(pathToFileURL(process.cwd() + '/')).resolve('playwright')).href)); }
  catch { console.log('UNMEASURED: playwright not installed (npm install playwright && npx playwright install chromium)'); process.exit(3); }
}
const url = /^https?:|^file:/.test(target) ? target : (existsSync(target) ? pathToFileURL(resolve(target)).href : null);
if (!url) { console.log('UNMEASURED: target not found'); process.exit(3); }
const b = await chromium.launch().catch((e) => { console.log('UNMEASURED: ' + e.message.split('\n')[0]); process.exit(3); });
const p = await b.newPage(); const errs = [];
p.on('pageerror', (e) => errs.push('pageerror: ' + e.message));
p.on('console', (m) => { if (m.type() === 'error') errs.push('console.error: ' + m.text()); });
p.on('requestfailed', (r) => errs.push('requestfailed: ' + r.url()));
try { await p.goto(url, { waitUntil: 'load' }); } catch (e) { await b.close(); console.log('UNMEASURED: could not load the page: ' + e.message.split('\n')[0]); process.exit(3); }
await p.waitForTimeout(wait); await b.close();
if (errs.length) { console.log('FAIL:\n  ' + errs.join('\n  ')); process.exit(1); }
console.log('PASS: no uncaught errors, console errors or failed requests'); process.exit(0);
