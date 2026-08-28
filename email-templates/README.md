# SavingsRE — Agile CRM email templates

Version-controlled source for the live Agile CRM nurture emails. These files are the
**authoritative copy**: the bodies in Agile were written from exactly these bytes, and the
SHA-256 values below were verified against the CRM after the write.

## Why these are evergreen

Every one of these emails sits in a **timer-based nurture loop** — it fires relative to when a
contact enters the flow, not on a calendar date. Anything with a figure baked into it therefore
keeps sending that figure for months. So these templates contain **no dated data at all**: no
county medians, no mortgage rates, no insurance percentages, no reference numbers, no
"updated <date>" stamps, no dated headlines.

Where a number belongs, the email links to the page that carries the live one:

- `savingsre.com/market/` — county medians, commercial and multifamily cap rates and vacancy,
  mortgage and jumbo pricing, coastal insurance filings
- `savingsre.com/top3/` — the twelve curated income and commercial lists

The only figures that survive are **durable**: the 1.5% listing commission against a typical 3%
listing side, and the screen definitions that name a list (8%+ cap, $800K–$2M, and so on).
Those describe the offer and the screens, not the market.

**If you edit these, keep them evergreen.** Adding a live figure re-introduces the problem.

## Mapping

| File | Agile campaign | Workflow ID | Node idx | Subject |
|---|---|---|---|---|
| `monthly-newsletter.html` / `.txt` | Following up loop 052721 | `4553655391420416` | 6, 17 | Your SavingsRE monthly: market data, Top Investments, 1.5% |
| `monthly-checkin.html` / `.txt` | Following up loop 052721 | `4553655391420416` | 18 | Your South Florida search shortcuts — always current |
| `new-subscriber-seller.html` / `.txt` | New Subscriber Seller | `6193359810527232` | 1, 9 | List at 1.5%, not 3% — plus your free home valuation |
| `quarterly-seller.html` / `.txt` | Quarterly Seller 2 | `4812159061655552` | 3 | Your quarterly seller update: list at 1.5%, not 3% |

## How these reach production

They are **not** deployed by this repo. They are written into Agile CRM via the workflow API:

1. `GET /core/api/workflows/<id>` — `j.rules` is a JSON **string**; parse it.
2. `rules.nodes[i].JsonValues` is an array of `{name, value}` pairs. Patch `subject`,
   `html_email` and `text_email` in place.
3. `JSON.stringify` rules back onto `j`, then `POST /core/api/workflows` with the whole object.
4. Re-`GET` and compare SHA-256 against the values below.

The Agile campaign canvas is not needed and tends to freeze; the API path is the supported one.

## Checksums as written to Agile

| File | Bytes | SHA-256 (first 16) |
|---|---:|---|
| `monthly-newsletter.html` | 20,909 | `be9387437f2a2881` |
| `monthly-newsletter.txt` | 7,114 | `2a3383722469bfbf` |
| `monthly-checkin.html` | 12,817 | `d0be765bf01c7018` |
| `monthly-checkin.txt` | 4,988 | `4c0c1c34124d9bb6` |
| `new-subscriber-seller.html` | 15,363 | `e43832a4063f6450` |
| `new-subscriber-seller.txt` | 5,495 | `abe19b10b2065021` |
| `quarterly-seller.html` | 16,748 | `83da658dfbcd0398` |
| `quarterly-seller.txt` | 6,206 | `fdbba00f97cada49` |

## Compliance invariants

Every template carries, and must keep:

- `{{{first_name}}}` — Agile merge fields are **triple**-braced. Double braces print literally.
- `{{{unsubscribe_link}}}`
- FL Real Estate License #3333692, MLS ID 276537152, United Realty Group, Equal Housing Opportunity
- AlphaGen Insurance Agency named as a **separate** business, FL Insurance License #G164863,
  with insurance explicitly not real estate, mortgage, tax or financial advice
- "Commission rates are negotiable and are not set by law", with 1.5% identified as the
  seller's-side commission and the million-dollar figure labelled an illustration

The **Buyer Representation Terms** block appears in the two investor-audience templates
(`monthly-newsletter`, `monthly-checkin`) and is deliberately **absent** from the two seller
templates — asserting an exclusive buyer-representation relationship on a seller audience is the
wrong claim. Recipients who click through to a listing page get the clause from the site footer.

## Format invariants

- HTML is a **fragment** — no doctype, no `<html>`, no `<head>`, no `<body>`. Agile's
  `html_email` field wants a fragment; a full document breaks rendering.
- 640px, inline styles only, table layout.
- Palette: navy `#0b2545`, gold `#c9a227`, green CTA `#137a4c`.
- Every outbound link carries `utm_source=agilecrm&utm_medium=email` plus an **undated**
  `utm_campaign` and a per-CTA `utm_content`.
