# SavingsRE Top 3 — weekly best-value income properties

Expandable, self-archiving Top-3 system served from GitHub Pages.

## How it works
- `index.html` — hub listing every segment (reads `segments.json`).
- `top3.html?seg=<key>&date=<YYYY-MM-DD>` — renders one segment's Top 3. Defaults to the latest week. The "View week" dropdown lets visitors browse past weeks.
- `segments.json` — registry of segments (label, tagline, search_name, browse link).
- `<key>__index.json` — per-segment archive index: `{ "latest": "YYYY-MM-DD", "dates": [...] }`.
- `<key>__<YYYY-MM-DD>.json` — one weekly snapshot (the Top-3 data for that week). These accumulate = the archive.

## Add a new segment
1. Add an entry under `segments` in `segments.json` (and to `order`).
2. Drop a `<key>__<date>.json` snapshot and a `<key>__index.json` listing that date.
That's it — the hub and renderer pick it up automatically.

## Weekly update (existing segment)
Each run writes a new `<key>__<date>.json`, updates `<key>__index.json` (append date, set `latest`), and commits. The email/page always point at the latest automatically. Old snapshots stay as the archive.

The email and any old links to `/mf-top3/mf-top3.html` redirect here.
