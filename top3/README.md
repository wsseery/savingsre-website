# SavingsRE Top Investments — unified, self-archiving system

One renderer + one registry serve every "best investments" list (Top 3 weekly by
segment, Top 5 high-yield, Top 10 larger) from GitHub Pages. Public display only —
sensitive attributes live in a private master ledger kept OUTSIDE this repo.

## Files
- `catalog.json` — registry of all lists (label, tagline, list_size, template, collection, cadence, source).
- `index.html` — hub; renders every list grouped by collection.
- `top3.html?seg=<key>&date=<YYYY-MM-DD>` — renderer. Defaults to latest; "View week/month" dropdown browses past periods. Two card templates: `mls-financial` (address public) and `curated-generic` (no address).
- `<key>__index.json` — `{latest, dates[]}` archive index.
- `<key>__<YYYY-MM-DD>.json` — one period's public snapshot (display-safe fields only).

## Add a list/segment (no code)
1. Add an entry under `lists` in `catalog.json` (and to `order`).
2. Drop a `<key>__<date>.json` snapshot + `<key>__index.json`.
The hub and renderer pick it up automatically.

## Weekly update
Run `top_build.py` (in the private repo) → it writes the public snapshot + index here
and the private ledger there. Commit only the `top3/` files to this public repo.

URL stays `/top3/`. Old `/mf-top3/` and the former static `high-yield-multifamily.html` /
`value-multifamily.html` redirect into the renderer.
