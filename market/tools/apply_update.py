#!/usr/bin/env python3
"""
SavingsRE Market Intel - apply an update payload to the live feed files.

Usage (from repo root):
  python3 market/tools/apply_update.py market/tools/_incoming.json [--today YYYY-MM-DD]

Payload (any key may be omitted or null):
{
  "news": [ {"date","title","summary","source","sourceUrl","category","importance"}, ... ],
  "rates": {"updated":"YYYY-MM-DD","date":"Oct 2, 2026","cards":[{"label","value","sub"} x3]},
  "insurance": {"updated":"YYYY-MM-DD","trend":"...","cards":[...],"note":"..."},
  "residential": {"month":"September 2026","source":"...","note":"...","index_note":"...","rows":[{area,sfMedian,sfYoy,condoMedian,closedYoy,homesYoy} x6]}
}

What it does (deterministically, so the model never hand-edits JSON/JS):
  - validates every news item; drops duplicates of anything already live or archived (by URL or title)
  - assigns ids (max+1), keeps the 16 newest live, APPENDS rotated items to news_archive.json (+archivedOn)
  - replaces rates / insurance / residential blocks in market_data.json AND the embedded MARKET in index.html
  - regenerates the embedded NEWS array in index.html, bumps meta.updated + the hero "Updated" line
Exit codes: 0 = changes written, 3 = nothing new (no files touched), 2 = invalid payload.
"""
import json, re, sys, datetime, argparse, os

CATS = {"Luxury", "Commercial/CRE", "Multifamily", "Market Data", "Policy/Insurance", "Development"}
IMPS = {"high", "medium", "low"}
LIVE_MAX = 16
MAX_SOURCE = 19          # longer sources overlap the headline in the email PNG
ROOT = "market"

def die(msg, code=2):
    print("ERROR:", msg); sys.exit(code)

def url_key(u):
    """Article-specific URLs dedupe by URL; generic landing pages (e.g. freddiemac.com/pmms) only by title."""
    from urllib.parse import urlparse
    u = (u or "").rstrip("/")
    return u if len([s for s in urlparse(u).path.split("/") if s]) >= 2 else None

def norm(t):
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()

def js(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ") + '"'

def long_date(iso):
    d = datetime.date.fromisoformat(iso)
    return d.strftime("%B ") + str(d.day) + d.strftime(", %Y")

def dump(path, obj, trailing_nl):
    s = json.dumps(obj, indent=2, ensure_ascii=False)
    with open(path, "w", encoding="utf-8") as f:
        f.write(s + ("\n" if trailing_nl else ""))

def ends_nl(path):
    with open(path, "rb") as f:
        f.seek(-1, 2); return f.read(1) == b"\n"

def cards_js(cards, indent="      "):
    return ",\n".join(indent + "{label:%s,value:%s,sub:%s}" % (js(c["label"]), js(c["value"]), js(c["sub"])) for c in cards)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("payload")
    ap.add_argument("--today", default=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).date().isoformat())
    a = ap.parse_args()
    today = a.today
    P = json.load(open(a.payload, encoding="utf-8"))

    fn = {k: os.path.join(ROOT, k) for k in ("news_data.json", "market_data.json", "news_archive.json", "index.html")}
    nl = {k: ends_nl(v) for k, v in fn.items() if k.endswith(".json")}
    live = json.load(open(fn["news_data.json"], encoding="utf-8"))
    market = json.load(open(fn["market_data.json"], encoding="utf-8"))
    arch = json.load(open(fn["news_archive.json"], encoding="utf-8"))
    html = open(fn["index.html"], encoding="utf-8").read()

    known_urls = {url_key(i.get("sourceUrl")) for i in live + arch["items"]} - {None}
    known_titles = {norm(i.get("title")) for i in live + arch["items"]}
    max_id = max(i["id"] for i in live + arch["items"])
    changed = []

    # ---- news ----
    new = []
    for n, it in enumerate(P.get("news") or []):
        for k in ("date", "title", "summary", "source", "sourceUrl", "category", "importance"):
            if not str(it.get(k, "")).strip(): die(f"news[{n}] missing {k}")
        try: datetime.date.fromisoformat(it["date"])
        except ValueError: die(f"news[{n}] bad date {it['date']}")
        if it["date"] > today: die(f"news[{n}] date {it['date']} is after today {today}")
        if it["category"] not in CATS: die(f"news[{n}] bad category {it['category']}")
        if it["importance"] not in IMPS: die(f"news[{n}] bad importance {it['importance']}")
        if len(it["source"]) > MAX_SOURCE: die(f"news[{n}] source '{it['source']}' > {MAX_SOURCE} chars (overlaps PNG headline)")
        if not it["sourceUrl"].startswith("https://"): die(f"news[{n}] sourceUrl must be https")
        uk = url_key(it["sourceUrl"])
        if (uk and uk in known_urls) or norm(it["title"]) in known_titles:
            print("skip duplicate:", it["title"]); continue
        if uk: known_urls.add(uk)
        known_titles.add(norm(it["title"]))
        new.append({k: it[k].strip() for k in ("date", "title", "summary", "source", "sourceUrl", "category", "importance")})
    for it in sorted(new, key=lambda x: x["date"]):
        max_id += 1; it["id"] = max_id
    new = [{"id": i["id"], **{k: i[k] for k in ("date", "title", "summary", "source", "sourceUrl", "category", "importance")}} for i in new]
    dropped = []
    if new:
        allitems = sorted(new + live, key=lambda x: (x["date"], x["id"]), reverse=True)
        live, dropped = allitems[:LIVE_MAX], allitems[LIVE_MAX:]
        for d in dropped:
            arch["items"].append({**d, "archivedOn": today})
        arch["items"].sort(key=lambda x: (x["date"], x["id"]), reverse=True)
        arch["meta"]["updated"] = today
        arch["meta"]["count"] = len(arch["items"])
        changed.append(f"news +{len(new)} (ids {', '.join(str(i['id']) for i in new)}), archived {len(dropped)}")

    # ---- rates ----
    R = P.get("rates")
    if R:
        if len(R.get("cards", [])) != 3: die("rates.cards must have 3 cards")
        old = market.get("rates", {})
        if old.get("cards") != R["cards"] or old.get("updated") != R["updated"]:
            market["rates"] = {"updated": R["updated"], "cards": R["cards"]}
            html, c = re.subn(r'rates:\{date:"[^"]*",cards:\[\n.*?\n    \]\}',
                              lambda m: 'rates:{date:%s,cards:[\n%s\n    ]}' % (js(R["date"]), cards_js(R["cards"])), html, count=1, flags=re.S)
            if c != 1: die("could not locate rates block in index.html")
            changed.append(f"rates {R['cards'][0]['value']} / {R['cards'][1]['value']} ({R['updated']})")

    # ---- insurance ----
    I = P.get("insurance")
    if I:
        if market.get("insurance") != I:
            market["insurance"] = I
            html, c = re.subn(r'insurance:\{trend:.*?\],note:"(?:[^"\\]|\\.)*"\}',
                              lambda m: 'insurance:{trend:%s,cards:[\n%s\n    ],note:%s}' % (js(I["trend"]), cards_js(I["cards"]), js(I["note"])), html, count=1, flags=re.S)
            if c != 1: die("could not locate insurance block in index.html")
            changed.append("insurance cards")

    # ---- residential ----
    S = P.get("residential")
    if S:
        if len(S.get("rows", [])) != 6: die("residential.rows must have 6 rows")
        res = market["residential"]
        if res.get("rows") != S["rows"] or res.get("source") != S["source"]:
            res["rows"], res["source"] = S["rows"], S["source"]
            if S.get("note"): res["note"] = S["note"]
            rows = ",\n".join('        {area:%s,sfMedian:%s,sfYoy:%s,condoMedian:%s,closedYoy:%s,homesYoy:%s}' % tuple(js(r[k]) for k in ("area", "sfMedian", "sfYoy", "condoMedian", "closedYoy", "homesYoy")) for r in S["rows"])
            html, c = re.subn(r'(    residential:\{\n      columns:[^\n]*\n      rows:\[\n).*?(\n      \],\n      note:)"(?:[^"\\]|\\.)*"',
                              lambda m: m.group(1) + rows + m.group(2) + js(S.get("index_note") or S["source"]), html, count=1, flags=re.S)
            if c != 1: die("could not locate residential block in index.html")
            html = re.sub(r'(period:"Single-family & condo county medians — )[A-Z][a-z]+ \d{4}', lambda m: m.group(1) + S["month"], html, count=1)
            market["meta"]["period"] = re.sub(r"Residential through [^;]+", "Residential through " + S["month"], market["meta"]["period"])
            changed.append(f"residential -> {S['month']}")

    if not changed:
        print("NO_CHANGES"); sys.exit(3)

    # ---- meta + mirrors ----
    if market.get("rates", {}).get("updated"):
        market["meta"]["period"] = re.sub(r"rates as of [A-Za-z]+ \d+, \d{4}", "rates as of " + long_date(market["rates"]["updated"]), market["meta"]["period"])
    market["meta"]["updated"] = today
    lines = ["    {id:%d,date:%s,title:%s,summary:%s,source:%s,sourceUrl:%s,category:%s,importance:%s}" % (
        i["id"], js(i["date"]), js(i["title"]), js(i["summary"]), js(i["source"]), js(i["sourceUrl"]), js(i["category"]), js(i["importance"])) for i in live]
    html, c = re.subn(r"  var NEWS = \[\n.*?\n  \];", lambda m: "  var NEWS = [\n" + ",\n".join(lines) + "\n  ];", html, count=1, flags=re.S)
    if c != 1: die("could not locate NEWS block in index.html")
    html, c = re.subn(r'(    meta:\{updated:")\d{4}-\d\d-\d\d', lambda m: m.group(1) + today, html, count=1)
    if c != 1: die("could not locate MARKET.meta.updated in index.html")
    html = re.sub(r'(<span id="updatedLine">Updated )[^<]*(</span>)', lambda m: m.group(1) + long_date(today) + m.group(2), html, count=1)

    dump(fn["news_data.json"], live, nl["news_data.json"])
    dump(fn["market_data.json"], market, nl["market_data.json"])
    dump(fn["news_archive.json"], arch, nl["news_archive.json"])
    open(fn["index.html"], "w", encoding="utf-8").write(html)
    print("CHANGED: " + "; ".join(changed))
    print(f"live {len(live)} (max id {max(i['id'] for i in live)}), archive {arch['meta']['count']}")

if __name__ == "__main__":
    main()
