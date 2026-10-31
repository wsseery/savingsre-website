#!/usr/bin/env python3
"""Build the SavingsRE segment landing pages from data/landing-segments.json.

    python3 scripts/build_landing_pages.py          # build everything
    python3 scripts/build_landing_pages.py --check  # build, then fail if any live page is stale

Writes:
  listings/<slug>/index.html   one landing page per segment
  listings/index.html          the hub page linking every segment
  weekly/<old>.html            redirect stubs for the retired /weekly/ pages
  sitemap.xml                  the block between the LANDING markers

Nothing here is edited by hand except data/landing-segments.json (copy, criteria,
weekly numbers, commentary) and data/landing-config.json (form + site settings).
The weekly refresh only ever touches each segment's "weekly" object.
No third-party dependencies: standard library only.
"""
import datetime as dt
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "landing-segments.json"
CONFIG = ROOT / "data" / "landing-config.json"
HEADER = ROOT / "_templates" / "site-header.html"
OUT = ROOT / "listings"
SITE = "https://savingsre.com"

CATEGORIES = [
    ("commercial-lease", "Commercial Space for Lease"),
    ("commercial-sale", "Commercial Property for Sale"),
    ("multifamily", "Multifamily & Income Property"),
    ("residential-sale", "Homes & Condos for Sale"),
    ("residential-lease", "Homes for Rent"),
]
CAT_LABEL = dict(CATEGORIES)

e = html.escape


def money_date(d):
    """2026-10-31 -> October 31, 2026"""
    return dt.date.fromisoformat(d).strftime("%B %-d, %Y")


def page_url(seg):
    return f"{SITE}/listings/{seg['slug']}/" if seg["slug"] else f"{SITE}/listings/"


def is_live(seg):
    w = seg.get("weekly") or {}
    return bool(w.get("mls_url")) and w.get("result_count") is not None and bool(w.get("date"))


def jsonld(seg, cfg):
    url = page_url(seg)
    graph = [
        {
            "@type": "CollectionPage",
            "@id": url + "#page",
            "url": url,
            "name": seg["title"],
            "description": seg["description"],
            "inLanguage": "en-US",
            "isPartOf": {"@id": SITE + "/#website"},
            "about": {"@type": "Place", "name": "Palm Beach, Broward and Miami-Dade Counties, Florida"},
            "provider": {"@id": SITE + "/#agent"},
            "breadcrumb": {"@id": url + "#breadcrumb"},
        },
        {
            "@type": "BreadcrumbList",
            "@id": url + "#breadcrumb",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": "Listings", "item": SITE + "/listings/"},
                {"@type": "ListItem", "position": 3, "name": seg["h1"], "item": url},
            ],
        },
        cfg["agent_jsonld"],
    ]
    w = seg.get("weekly") or {}
    if w.get("date"):
        graph[0]["dateModified"] = w["date"]
    if seg.get("faqs"):
        graph.append({
            "@type": "FAQPage",
            "@id": url + "#faq",
            "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in seg["faqs"]
            ],
        })
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=1, ensure_ascii=False)


def head(title, desc, canonical, robots, extra=""):
    t, d = e(title), e(desc)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <!-- Google Tag Manager -->
  <script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
  new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
  j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
  'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
  }})(window,document,'script','dataLayer','GTM-K4HVBNM');</script>
  <!-- End Google Tag Manager -->
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{t}</title>
  <meta name="description" content="{d}">
  <link rel="canonical" href="{canonical}">
  <meta name="robots" content="{robots}">
  <meta property="og:title" content="{t}">
  <meta property="og:description" content="{d}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{SITE}/assets/savingsre-og-default_v01.png">
  <meta property="og:site_name" content="SavingsRE">
  <meta property="og:locale" content="en_US">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{t}">
  <meta name="twitter:description" content="{d}">
  <meta name="twitter:image" content="{SITE}/assets/savingsre-og-default_v01.png">
  <meta name="geo.region" content="US-FL">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400;1,600&family=Montserrat:wght@300;400;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/css/site.css?v=20261015">
  <link rel="stylesheet" href="/assets/css/landing.css?v=20261031c">
  <script defer src="/assets/js/site.js?v=20261015"></script>
{extra}</head>
<body>
  <!-- Google Tag Manager (noscript) -->
  <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-K4HVBNM"
  height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
  <!-- End Google Tag Manager (noscript) -->
"""


def footer(cfg):
    return f"""<footer>
  <div class="footer-inner">
    <div class="footer-brand">
      <div class="footer-logo">Savings<span>RE</span></div>
      <div class="footer-info">5550 Glades Road · Boca Raton, FL 33431<br>FL License #3333692 · MLS ID 276537152</div>
    </div>
    <div class="footer-links">
      <a href="/index.html">Home</a>
      <a href="/listings/">All Listings</a>
      <a href="/investor-hub.html">Investors</a>
      <a href="/market/">Market Intel</a>
      <a href="/luxury-listings.html">List for 1.5%</a>
      <a href="mailto:bill@savingsre.com">Contact</a>
      <a href="/privacy/">Privacy</a>
      <a href="/terms/">Terms</a>
    </div>
  </div>
  <div class="footer-legal">
    {e(cfg['disclaimer'])}<br>
    William Spencer Seery Jr, PA · United Realty Group · FL License #3333692 · MLS ID 276537152. SavingsRE is a brand of William Spencer Seery Jr, PA. © {dt.date.today().year} SavingsRE. All rights reserved.
  </div>
</footer>
</body>
</html>
"""


def inquiry_form(seg, cfg):
    """The page's single call to action. Posts to Agile CRM when the form is
    configured in data/landing-config.json; otherwise shows phone and email."""
    a = cfg.get("agile") or {}
    tags = ",".join(["website-inquiry", "landing-page", seg["agile_tag"]])
    heading = e(seg.get("form_heading") or f"Ask Bill about {seg['short'].lower()}")
    intro = e(cfg["form_intro"])
    # form_consent may contain {privacy} and {terms}; they become links after escaping.
    consent = e(cfg["form_consent"]).format(
        privacy='<a href="/privacy/">Privacy Policy</a>', terms='<a href="/terms/">Terms</a>')
    if a.get("api_key") and a.get("form_name"):
        fields = f"""
      <form class="inquiry-form" id="inquiry-form" action="https://{e(a['domain'])}.agilecrm.com/formsubmit" method="GET" data-segment="{e(seg['slug'])}">
        <input type="hidden" name="_agile_form_name" value="{e(a['form_name'])}">
        <input type="hidden" name="_agile_domain" value="{e(a['domain'])}">
        <input type="hidden" name="_agile_api" value="{e(a['api_key'])}">
        <input type="hidden" name="_agile_form_id" value="{e(a.get('form_id', ''))}">
        <input type="hidden" name="_agile_redirect_url" value="{e(page_url(seg))}?inquiry=sent#inquiry">
        <input type="hidden" name="_agile_document_url" value="{e(page_url(seg))}">
        <input type="hidden" name="_agile_confirmation_msg" value="Thanks. Bill will be in touch shortly.">
        <input type="hidden" name="tags" value="{e(tags)}">
        <input type="hidden" name="{e(a.get('segment_field', 'segment'))}" value="{e(seg['h1'])}">
        <div class="form-row">
          <div class="form-group"><label for="f-first">First name</label><input id="f-first" name="first_name" autocomplete="given-name" required></div>
          <div class="form-group"><label for="f-last">Last name</label><input id="f-last" name="last_name" autocomplete="family-name"></div>
        </div>
        <div class="form-row">
          <div class="form-group"><label for="f-email">Email</label><input id="f-email" type="email" name="email" autocomplete="email" required></div>
          <div class="form-group"><label for="f-phone">Phone</label><input id="f-phone" type="tel" name="phone" autocomplete="tel"></div>
        </div>
        <div class="form-group"><label for="f-msg">What are you looking for?</label><textarea id="f-msg" name="{e(a.get('message_field', 'note'))}" rows="4" placeholder="{e(seg['form_placeholder'])}"></textarea></div>
        <p class="form-consent">{consent}</p>
        <button type="submit" class="form-submit">Send My Inquiry</button>
        <div class="form-success" id="inquiry-sent" hidden>Thanks. Your inquiry is in, and Bill will be in touch shortly.</div>
      </form>"""
    else:
        fields = """
      <div class="pending-state inquiry-fallback">
        <p>Call or text <a href="tel:+15612200402" data-cta onclick="trackPhone()">+1 (561) 220-0402</a> or email <a href="mailto:bill@savingsre.com">bill@savingsre.com</a>.</p>
      </div>"""
    return f"""
  <section class="inquiry" id="inquiry" aria-labelledby="inquiry-h">
    <div class="inquiry-inner">
      <h2 id="inquiry-h">{heading}</h2>
      <p class="inquiry-intro">{intro}</p>{fields}
    </div>
  </section>"""


def this_week(seg):
    w = seg.get("weekly") or {}
    if not is_live(seg):
        return """
  <div class="search-card week-card">
    <div class="search-card-header"><h2>This Week's Market Update</h2></div>
    <div class="search-card-body"><div class="pending-state"><p>This search is being set up. Use the form below and Bill will send you the current active listings directly.</p></div></div>
  </div>"""
    n = int(w["result_count"])
    prior = w.get("prior_count")
    delta = ""
    if isinstance(prior, int):
        diff = n - prior
        delta = f' <span class="delta">({"+" if diff > 0 else ""}{diff} vs. last week)</span>' if diff else ' <span class="delta">(unchanged vs. last week)</span>'
    paras = "\n".join(f"      <p>{e(p)}</p>" for p in w.get("commentary") or [])
    figs = ""
    if w.get("figures"):
        rows = "\n".join(
            f"          <tr><td>{e(f['label'])}</td><td>{e(f['value'])}</td><td>{e(f['source'])}</td></tr>"
            for f in w["figures"])
        figs = f"""
      <details class="figures">
        <summary>Sources for this week's figures</summary>
        <table>
          <thead><tr><th>Figure</th><th>Value</th><th>Source</th></tr></thead>
          <tbody>
{rows}
          </tbody>
        </table>
      </details>"""
    noun = "listing" if n == 1 else "listings"
    url = w["mls_url"]
    return f"""
  <div class="search-card week-card">
    <div class="search-card-header">
      <h2>This Week's Market Update</h2>
      <div class="search-meta">
        <div class="search-meta-item">Updated: <span><time datetime="{e(w['date'])}">{e(money_date(w['date']))}</time></span></div>
        <div class="search-meta-item">Active {noun}: <span>{n}</span>{delta}</div>
        <div class="search-meta-item">Source: <span>FlexMLS</span></div>
      </div>
    </div>
    <div class="search-card-body">
{paras}{figs}
      <div class="listings-link-wrap">
        <a href="{e(url)}" class="listings-link" target="_blank" rel="noopener nofollow" onclick="trackMLS('{e(seg['slug'])}')">View all {n} active {noun} on FlexMLS &rarr;</a>
        <div class="mls-note">Opens FlexMLS in a new tab: full listing details and photos, no login needed. Link refreshed {e(money_date(w['link_generated']))}.</div>
      </div>
    </div>
  </div>"""


def landing_page(seg, cfg, by_slug, header_html):
    live = is_live(seg)
    robots = "index,follow,max-image-preview:large" if live else "noindex,follow"
    extra = f'  <script type="application/ld+json">\n{jsonld(seg, cfg)}\n  </script>\n'
    out = [head(seg["title"], seg["description"], page_url(seg), robots, extra), header_html]
    out.append(f"""
<section class="hero landing-hero">
  <div class="hero-content">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> <span aria-hidden="true">›</span> <a href="/listings/">Listings</a> <span aria-hidden="true">›</span> <span aria-current="page">{e(seg['short'])}</span></nav>
    <div class="hero-badge"><span class="hero-badge-pill">{e(CAT_LABEL[seg['category']])}</span><span class="hero-badge-dot"></span><span>Palm Beach · Broward · Miami-Dade</span></div>
    <h1>{e(seg['h1'])}</h1>
    <p class="hero-sub">{e(seg['subhead'])}</p>
  </div>
</section>
<main class="main landing-main">""")
    out.append(this_week(seg))
    intro = "\n".join(f"    <p>{e(p)}</p>" for p in seg["intro"])
    crit = "\n".join(
        f'      <div class="spec"><div class="spec-val">{e(v)}</div><div class="spec-lbl">{e(k)}</div></div>'
        for k, v in seg["criteria"])
    out.append(f"""
  <section class="detail-section" aria-labelledby="about-h">
    <h2 id="about-h">{e(seg.get('about_heading') or 'About This Search')}</h2>
{intro}
    <div class="specs-grid">
{crit}
    </div>
  </section>""")
    if seg.get("faqs"):
        qa = "\n".join(
            f"    <details class=\"faq\"><summary>{e(q)}</summary><p>{e(a)}</p></details>"
            for q, a in seg["faqs"])
        out.append(f"""
  <section class="detail-section" aria-labelledby="faq-h">
    <h2 id="faq-h">Frequently Asked Questions</h2>
{qa}
  </section>""")
    out.append(inquiry_form(seg, cfg))
    rel = [by_slug[s] for s in seg.get("related", []) if s in by_slug]
    if rel:
        links = "\n".join(f'      <li><a href="/listings/{r["slug"]}/">{e(r["h1"])}</a></li>' for r in rel)
        out.append(f"""
  <nav class="related" aria-labelledby="related-h">
    <h2 id="related-h">Related Searches</h2>
    <ul>
{links}
      <li><a href="/listings/">All property searches &rarr;</a></li>
    </ul>
  </nav>""")
    out.append(f"""
  <aside class="attribution" aria-label="Listing data attribution">
    <p>{e(cfg['attribution'])}</p>
  </aside>
</main>
{inquiry_script()}""")
    out.append(footer(cfg))
    return "".join(out)



def inquiry_script():
    """Submit handler shared by segment pages and the hub: GTM lead event + inline confirmation."""
    return """<script>
(function () {
  var f = document.getElementById('inquiry-form');
  if (location.search.indexOf('inquiry=sent') > -1) {
    var ok = document.getElementById('inquiry-sent'); if (ok) ok.hidden = false;
  }
  if (!f) return;
  f.addEventListener('submit', function (ev) {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ event: 'generate_lead', form_name: 'landing_inquiry', segment: f.getAttribute('data-segment') });
    // Send in the background and confirm on this page, so visitors are not left on
    // Agile's unbranded thank-you page. Without fetch, the normal GET submit still works.
    if (!window.fetch || !window.URLSearchParams || !window.FormData) return;
    ev.preventDefault();
    var btn = f.querySelector('[type=submit]'); if (btn) btn.disabled = true;
    var url = f.action + '?' + new URLSearchParams(new FormData(f)).toString();
    fetch(url, { method: 'GET', mode: 'no-cors', credentials: 'omit' }).then(function () {
      var ok = document.getElementById('inquiry-sent');
      Array.prototype.forEach.call(f.children, function (c) { if (c !== ok) c.hidden = true; });
      if (ok) { ok.hidden = false; ok.setAttribute('tabindex', '-1'); ok.focus(); }
    }).catch(function () { f.submit(); });
  });
})();
</script>
"""

def hub_page(segs, cfg, header_html):
    title = "South Florida Property Searches: Sale & Lease | SavingsRE"
    desc = ("Weekly-updated searches for commercial, multifamily and residential property for sale "
            "and for lease in Palm Beach, Broward and Miami-Dade, with market commentary from Bill Seery.")
    live = [s for s in segs if is_live(s)]
    items = [{"@type": "ListItem", "position": i + 1, "url": page_url(s), "name": s["h1"]}
             for i, s in enumerate(live)]
    ld = json.dumps({"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "@id": SITE + "/listings/#page", "url": SITE + "/listings/",
         "name": title, "description": desc, "provider": {"@id": SITE + "/#agent"},
         "mainEntity": {"@type": "ItemList", "itemListElement": items}},
        cfg["agent_jsonld"]]}, indent=1, ensure_ascii=False)
    out = [head(title, desc, SITE + "/listings/", "index,follow",
                f'  <script type="application/ld+json">\n{ld}\n  </script>\n'), header_html]
    out.append("""
<section class="hero landing-hero">
  <div class="hero-content">
    <div class="hero-badge"><span class="hero-badge-pill">Updated Weekly</span><span class="hero-badge-dot"></span><span>Palm Beach · Broward · Miami-Dade</span></div>
    <h1>South Florida Property Searches</h1>
    <p class="hero-sub">Commercial, multifamily and residential property for sale and for lease, refreshed every week with a short market note.</p>
  </div>
</section>
<main class="main landing-main">""")
    for cat, label in CATEGORIES:
        group = [s for s in segs if s["category"] == cat and is_live(s)]
        extra = [x for x in cfg.get("hub_extra", []) if x["category"] == cat]
        if not group and not extra:
            continue
        cards = []
        for s in group:
            w = s["weekly"]
            cards.append(f"""      <a class="hub-card" href="/listings/{s['slug']}/">
        <span class="hub-title">{e(s['h1'])}</span>
        <span class="hub-sub">{e(s['subhead'])}</span>
        <span class="hub-meta">{int(w['result_count'])} active · updated {e(money_date(w['date']))}</span>
      </a>""")
        for x in extra:
            cards.append(f"""      <a class="hub-card" href="{e(x['href'])}">
        <span class="hub-title">{e(x['title'])}</span>
        <span class="hub-sub">{e(x['sub'])}</span>
        <span class="hub-meta">Updated weekly</span>
      </a>""")
        out.append(f"""
  <section class="hub-group" aria-labelledby="h-{cat}">
    <h2 id="h-{cat}">{e(label)}</h2>
    <div class="hub-grid">
{chr(10).join(cards)}
    </div>
  </section>""")
    hub_seg = {"slug": "", "short": "South Florida property", "h1": "General inquiry (listings hub)",
               "agile_tag": "seg-general", "form_heading": "Not sure which search fits? Ask Bill",
               "form_placeholder": "e.g. what you want to buy, sell or lease, where, and your budget"}
    out.append(inquiry_form(hub_seg, cfg))
    out.append(f"""
  <aside class="attribution" aria-label="Listing data attribution"><p>{e(cfg['attribution'])}</p></aside>
</main>
{inquiry_script()}""")
    out.append(footer(cfg))
    return "".join(out)


def legal_page(slug, cfg, header_html):
    """/privacy/ and /terms/ — body text lives in data/legal/<slug>.html (an HTML fragment)."""
    meta = cfg["legal_pages"][slug]
    body = (ROOT / "data" / "legal" / f"{slug}.html").read_text()
    out = [head(meta["title"], meta["description"], f"{SITE}/{slug}/", "index,follow"), header_html]
    out.append(f"""
<section class="hero landing-hero">
  <div class="hero-content">
    <h1>{e(meta['h1'])}</h1>
    <p class="hero-sub">Last updated {e(money_date(meta['updated']))}</p>
  </div>
</section>
<main class="main landing-main legal">
{body}
</main>
""")
    out.append(footer(cfg))
    return "".join(out)


def redirect_stub(target):
    t = e(target)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Moved | SavingsRE</title>
  <link rel="canonical" href="{t}">
  <meta name="robots" content="noindex,follow">
  <meta http-equiv="refresh" content="0; url={t}">
</head>
<body>
  <p>This search has moved to <a href="{t}">{t}</a>.</p>
</body>
</html>
"""


def update_sitemap(segs):
    path = ROOT / "sitemap.xml"
    xml = path.read_text()
    start, end = "<!-- LANDING:START -->", "<!-- LANDING:END -->"
    today = dt.date.today().isoformat()
    urls = [f"  <url><loc>{SITE}/listings/</loc><lastmod>{today}</lastmod><changefreq>weekly</changefreq><priority>0.8</priority></url>",
            f"  <url><loc>{SITE}/privacy/</loc><changefreq>yearly</changefreq><priority>0.2</priority></url>",
            f"  <url><loc>{SITE}/terms/</loc><changefreq>yearly</changefreq><priority>0.2</priority></url>"]
    for s in segs:
        if is_live(s):
            urls.append(f"  <url><loc>{page_url(s)}</loc><lastmod>{s['weekly']['date']}</lastmod>"
                        f"<changefreq>weekly</changefreq><priority>0.7</priority></url>")
    block = start + "\n" + "\n".join(urls) + "\n  " + end
    if start in xml:
        xml = re.sub(re.escape(start) + r".*?" + re.escape(end), lambda m: block, xml, flags=re.S)
    else:
        xml = xml.replace("</urlset>", "  " + block + "\n</urlset>")
    path.write_text(xml)


def validate(segs):
    problems, seen = [], set()
    for s in segs:
        for k in ("slug", "search_name", "category", "title", "h1", "short", "subhead",
                  "description", "intro", "criteria", "agile_tag", "form_placeholder"):
            if not s.get(k):
                problems.append(f"{s.get('slug', '?')}: missing {k}")
        if s["slug"] in seen:
            problems.append(f"duplicate slug {s['slug']}")
        seen.add(s["slug"])
        if s["category"] not in CAT_LABEL:
            problems.append(f"{s['slug']}: unknown category {s['category']}")
        if len(s["title"]) > 65:
            problems.append(f"{s['slug']}: title {len(s['title'])} chars (keep <= 65)")
        if not 70 <= len(s["description"]) <= 160:
            problems.append(f"{s['slug']}: description {len(s['description'])} chars (70-160)")
        w = s.get("weekly") or {}
        if is_live(s):
            if not w.get("commentary"):
                problems.append(f"{s['slug']}: live but no commentary")
            if not w.get("link_generated"):
                problems.append(f"{s['slug']}: live but no link_generated date")
    return problems


def main():
    data = json.loads(DATA.read_text())
    cfg = json.loads(CONFIG.read_text())
    segs = data["segments"]
    problems = validate(segs)
    if problems:
        print("Data problems:\n  " + "\n  ".join(problems))
        sys.exit(1)
    header_html = HEADER.read_text()
    by_slug = {s["slug"]: s for s in segs}
    for s in segs:
        d = OUT / s["slug"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(landing_page(s, cfg, by_slug, header_html))
    (OUT / "index.html").write_text(hub_page(segs, cfg, header_html))
    for slug in cfg.get("legal_pages", {}):
        (ROOT / slug).mkdir(exist_ok=True)
        (ROOT / slug / "index.html").write_text(legal_page(slug, cfg, header_html))
    for old, slug in cfg.get("weekly_redirects", {}).items():
        if slug in by_slug:
            (ROOT / "weekly" / old).write_text(redirect_stub(page_url(by_slug[slug])))
    update_sitemap(segs)
    live = sum(is_live(s) for s in segs)
    print(f"Built {len(segs)} landing pages ({live} live, {len(segs) - live} pending) + hub + "
          f"{len(cfg.get('weekly_redirects', {}))} redirects.")
    if "--check" in sys.argv:
        today = dt.date.today()
        stale = [s["slug"] for s in segs if is_live(s)
                 and (today - dt.date.fromisoformat(s["weekly"]["date"])).days > 8]
        if stale:
            print("Stale (over 8 days since the last weekly update): " + ", ".join(stale))
            sys.exit(2)


if __name__ == "__main__":
    main()
