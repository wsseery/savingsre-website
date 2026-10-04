#!/usr/bin/env python3
"""
Fetch a JavaScript-rendered page with headless Chromium (Playwright) and print its text or links.
therealdeal.com is client-rendered, so plain WebFetch returns an empty shell; this does not.
Usage:
  python3 market/tools/render_fetch.py URL                    # article text (main element), first 9000 chars
  python3 market/tools/render_fetch.py URL --links REGEX      # JSON list of {href,text} for matching links
Only hosts on the allowlist below can be fetched.
"""
import sys, re, json, argparse
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

ALLOW = ("therealdeal.com", "bisnow.com", "mortgagenewsdaily.com", "freddiemac.com", "floridarealtors.org",
         "miamirealtors.com", "insurancejournal.com", "commercialobserver.com", "cbre.com", "floir.gov", "millionluxury.com")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"

ap = argparse.ArgumentParser(); ap.add_argument("url"); ap.add_argument("--links"); ap.add_argument("--max", type=int, default=9000)
a = ap.parse_args()
host = urlparse(a.url).hostname or ""
if urlparse(a.url).scheme != "https" or not any(host == h or host.endswith("." + h) for h in ALLOW):
    sys.exit(f"refused: {host} not on allowlist")
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(user_agent=UA, viewport={"width": 1366, "height": 900})
    resp = pg.goto(a.url, wait_until="domcontentloaded", timeout=45000)
    pg.wait_for_timeout(3000)
    if resp and resp.status >= 400:
        print(f"HTTP {resp.status}")
    if a.links:
        rx = re.compile(a.links); seen = set(); out = []
        for el in pg.query_selector_all("a"):
            href = el.get_attribute("href") or ""; txt = " ".join((el.inner_text() or "").split())
            if rx.search(href) and len(txt) > 30 and href not in seen:
                seen.add(href); out.append({"href": href, "text": txt[:200]})
        print(json.dumps(out, ensure_ascii=False, indent=0))
    else:
        el = pg.query_selector("main") or pg.query_selector("body")
        print(" ".join((el.inner_text() or "").split())[: a.max])
    b.close()
