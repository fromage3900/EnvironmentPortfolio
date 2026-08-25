#!/usr/bin/env python3
import pathlib
import re
import os

root_dir = pathlib.Path(__file__).parent.parent.resolve()
wix_dir = root_dir / "wix"
all_html = [p for p in wix_dir.rglob("*.html") if "_deprecated" not in p.parts]
all_css = [p for p in wix_dir.rglob("*.css") if "_deprecated" not in p.parts]
all_js = [p for p in wix_dir.rglob("*.js") if "_deprecated" not in p.parts]

broken_refs = []

def check_ref(src_file, ref_url):
    ref_clean = ref_url.split("?")[0].split("#")[0].strip()
    if not ref_clean or ref_clean.startswith(("http://", "https://", "data:", "blob:", "ws://", "wss://", "mailto:", "javascript:")):
        return
    if "%" in ref_clean or "$" in ref_clean or "{" in ref_clean or "}" in ref_clean:
        return
    # Resolve relative to src_file.parent
    target = (src_file.parent / ref_clean).resolve()
    if not target.exists():
        broken_refs.append((str(src_file.relative_to(root_dir)), ref_url, str(target)))

# Check HTML files
for html_file in all_html:
    txt = html_file.read_text(encoding="utf-8", errors="ignore")
    for attr in ["src", "poster", "href"]:
        # Find attr="..." or attr='...'
        pattern = re.compile(rf'{attr}=["\']([^"\']+)["\']', re.IGNORECASE)
        for m in pattern.findall(txt):
            if attr == "href" and not (m.endswith((".png", ".jpg", ".jpeg", ".webp", ".svg", ".css", ".js", ".webm", ".mp4", ".json")) or m.endswith(".html")):
                continue
            check_ref(html_file, m)

# Check CSS files
for css_file in all_css:
    txt = css_file.read_text(encoding="utf-8", errors="ignore")
    pattern = re.compile(r'url\(["\']?([^"\'\)]+)["\']?\)', re.IGNORECASE)
    for m in pattern.findall(txt):
        check_ref(css_file, m)

print(f"Total broken references found across {len(all_html)} HTML and {len(all_css)} CSS files: {len(broken_refs)}")
for src, ref, tgt in broken_refs:
    print(f"  {src} -> \"{ref}\" (Target missing: {tgt})")

if not broken_refs:
    print("[OK] Zero broken references detected!")
