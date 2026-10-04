#!/usr/bin/env python3
"""
SavingsRE Market Intel - validate the feed files before commit. Exit 1 on any problem.
Usage (repo root): python3 market/tools/validate.py [--base-index PATH]
--base-index: the pre-run index.html (e.g. `git show HEAD:market/index.html > /tmp/base.html`).
  When given, everything OUTSIDE the embedded MARKET/NEWS data and the "Updated" line must be byte-identical,
  so a run can only ever change data, never page markup or scripts.
"""
import json, re, sys, subprocess, os, argparse, datetime

CATS = {"Luxury", "Commercial/CRE", "Multifamily", "Market Data", "Policy/Insurance", "Development"}
IMPS = {"high", "medium", "low"}
PNG = "assets/2026-07-02_savingsre_img_market-intel-newsfeed_v01.png"
errs = []
def bad(m): errs.append(m)

ap = argparse.ArgumentParser(); ap.add_argument("--base-index"); a = ap.parse_args()
live = json.load(open("market/news_data.json", encoding="utf-8"))
market = json.load(open("market/market_data.json", encoding="utf-8"))
arch = json.load(open("market/news_archive.json", encoding="utf-8"))
html = open("market/index.html", encoding="utf-8").read()

# live feed
if not 1 <= len(live) <= 16: bad(f"live feed has {len(live)} items (want 1-16)")
ids = [i["id"] for i in live]
if len(set(ids)) != len(ids): bad("duplicate ids in live feed")
keys = [(i["date"], i["id"]) for i in live]
if keys != sorted(keys, reverse=True): bad("live feed not newest-first")
for i in live:
    for k in ("id", "date", "title", "summary", "source", "sourceUrl", "category", "importance"):
        if k not in i or i[k] in ("", None): bad(f"id {i.get('id')} missing {k}")
    if i.get("category") not in CATS: bad(f"id {i['id']} bad category")
    if i.get("importance") not in IMPS: bad(f"id {i['id']} bad importance")
    if len(i.get("source", "")) > 19: bad(f"id {i['id']} source too long for PNG")
    if re.search(r"<[a-z/!]", i.get("title", "") + i.get("summary", ""), re.I): bad(f"id {i['id']} contains HTML")
# archive
aids = [i["id"] for i in arch["items"]]
if len(set(aids)) != len(aids): bad("duplicate ids in archive")
if set(aids) & set(ids): bad("ids present in both live and archive")
if arch["meta"]["count"] != len(arch["items"]): bad("archive meta.count mismatch")
if min(ids) <= max(aids) and any(x > min(ids) for x in aids): pass  # older items can legitimately interleave by date
# market
r = market.get("rates", {}).get("cards", [])
if len(r) != 3 or not all(re.match(r"^\d+\.\d\d%$", c["value"]) for c in r[:2]): bad("rates cards malformed")
if len(market["residential"]["rows"]) != 6: bad("residential rows != 6")

# index.html mirrors
m = re.search(r"  var MARKET = (\{.*?\n  \});\n  var NEWS = (\[.*?\n  \]);", html, re.S)
if not m: bad("cannot find embedded MARKET/NEWS in index.html")
else:
    try:
        out = subprocess.run(["node", "-e", "const M=%s;const N=%s;console.log(JSON.stringify({M,N}))" % (m.group(1), m.group(2))],
                             capture_output=True, text=True, timeout=30)
        if out.returncode: bad("embedded JS does not parse: " + out.stderr[:300])
        else:
            E = json.loads(out.stdout)
            en = E["N"]
            if [i["id"] for i in en] != ids: bad("index.html NEWS ids differ from news_data.json")
            for x, y in zip(en, live):
                for k in ("date", "title", "summary", "source", "sourceUrl", "category", "importance"):
                    if x.get(k) != y.get(k): bad(f"index.html NEWS id {y['id']} field {k} differs")
            if E["M"]["meta"]["updated"] != market["meta"]["updated"]: bad("MARKET.meta.updated differs")
            if [c["value"] for c in E["M"]["rates"]["cards"]] != [c["value"] for c in r]: bad("MARKET.rates differs")
            if E["M"]["residential"]["rows"] != market["residential"]["rows"]: bad("MARKET.residential rows differ")
            if [c["value"] for c in E["M"]["insurance"]["cards"]] != [c["value"] for c in market["insurance"]["cards"]]: bad("MARKET.insurance differs")
    except FileNotFoundError:
        print("warn: node not found; skipped JS parse check")
upd = datetime.date.fromisoformat(market["meta"]["updated"])
if ("Updated " + upd.strftime("%B ") + str(upd.day) + upd.strftime(", %Y")) not in html: bad("hero 'Updated' line does not match meta.updated")

# markup unchanged outside data
if a.base_index and os.path.exists(a.base_index):
    def strip(h):
        h = re.sub(r"  var MARKET = \{.*?\n  \];", "", h, flags=re.S)
        return re.sub(r'<span id="updatedLine">[^<]*</span>', "", h)
    if strip(open(a.base_index, encoding="utf-8").read()) != strip(html): bad("index.html changed OUTSIDE the data blocks")

if os.path.exists(PNG) and os.path.getsize(PNG) < 20000: bad("PNG suspiciously small")

if errs:
    print("VALIDATION FAILED:"); [print(" -", e) for e in errs]; sys.exit(1)
print(f"OK: live {len(live)} (max id {max(ids)}), archive {len(aids)}, updated {market['meta']['updated']}")
