#!/usr/bin/env python3
"""web-asset-reality-check / fonts: do the declared fonts actually exist in the build?
Checks a built web dir (dist/): (1) font files exist, (2) no runtime CDN for CSS/fonts, (3) every first-choice font-family
in CSS has an @font-face - otherwise the declaration is dead and the browser silently falls back, (4) every url() inside an @font-face
resolves to a file in the build, (5) no external <link rel=stylesheet> or @import "https://..." at runtime.
exit 0 ok | 1 problems | 2 bad input | 3 nothing to measure"""
import os, re, sys
GENERIC = {"serif", "sans-serif", "monospace", "cursive", "fantasy", "system-ui", "ui-monospace", "ui-sans-serif", "ui-serif",
           "-apple-system", "blinkmacsystemfont", "inherit", "initial", "unset", "arial", "helvetica", "times new roman", "courier new", "georgia", "verdana", "tahoma"}
FONT_EXT = (".woff2", ".woff", ".ttf", ".otf")
root = sys.argv[1] if len(sys.argv) > 1 else ""
if not os.path.isdir(root): print("usage: font_check.py <dist-dir>"); sys.exit(2)
files = [os.path.join(d, f) for d, _, fs in os.walk(root) for f in fs]
css = [f for f in files if f.endswith((".css", ".html"))]
if not css: print("UNMEASURED: no css/html in build"); sys.exit(3)
text = {f: open(f, encoding="utf-8", errors="ignore").read() for f in css}
problems = []
def rel(f): return os.path.relpath(f, root)
def resolves(css_file, ref):
    ref = ref.split("?")[0].split("#")[0]
    if not ref or ref.startswith("data:"): return True
    base = root if ref.startswith("/") else os.path.dirname(css_file)
    return os.path.isfile(os.path.normpath(os.path.join(base, ref.lstrip("/") if ref.startswith("/") else ref)))
fontfiles = [f for f in files if f.lower().endswith(FONT_EXT)]
declared = {m.group(1).strip().strip("'\"").lower() for t in text.values() for m in re.finditer(r"@font-face\s*\{[^}]*font-family\s*:\s*([^;}]+)", t, re.S)}
for f, t in text.items():
    for blk in re.finditer(r"@font-face\s*\{([^}]*)\}", t, re.S):
        urls = re.findall(r"url\(\s*['\"]?([^)'\"\s]+)", blk.group(1))
        if not urls: problems.append(f"{rel(f)}: an @font-face has no src url() (nothing to load)")
        for u in urls:
            if re.match(r"https?:", u): continue                      # reported below as a runtime external dependency
            if not resolves(f, u): problems.append(f"{rel(f)}: @font-face src '{u}' does not exist in the build")
    for m in re.finditer(r"""<link[^>]+href=["'](https?://[^"']+)["'][^>]*>|@import\s+["'](https?://[^"']+)["']""", t):
        u = m.group(1) or m.group(2)
        if re.search(r"fonts\.(googleapis|gstatic)|jsdelivr|cdnjs|unpkg|fontawesome|typekit", u) or u.lower().split("?")[0].endswith(FONT_EXT + (".css",)):
            problems.append(f"{rel(f)}: runtime external dependency {u} (breaks offline / blocked CDN / file://)")
    for m in re.finditer(r"(@import\s+url\(|url\()\s*['\"]?(https?://[^)'\"]+)", t):
        u = m.group(2)
        if re.search(r"fonts\.(googleapis|gstatic)|jsdelivr|cdnjs|unpkg|fontawesome|typekit", u) or u.lower().endswith(FONT_EXT + (".css",)):
            problems.append(f"{os.path.relpath(f, root)}: runtime external dependency {u} (breaks offline / blocked CDN / file://)")
    for m in re.finditer(r"font-family\s*:\s*([^;}{]+)", t):
        first = m.group(1).split(",")[0].strip().strip("'\"").lower()
        if first and first not in GENERIC and first not in declared and not first.startswith("var("):
            problems.append(f"{os.path.relpath(f, root)}: first-choice font '{first}' has no @font-face in the build (dead declaration)")
if re.search(r"font-family", " ".join(text.values())) and not fontfiles and declared:
    problems.append("@font-face declared but no font files in the build")
print("font files: " + (", ".join(os.path.basename(f) for f in fontfiles) or "none") + f"; @font-face families: {sorted(declared) or 'none'}")
print("\n".join(sorted(set(problems))) if problems else "ok: declared fonts exist and nothing loads from a runtime CDN")
sys.exit(1 if problems else 0)
