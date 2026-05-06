# SavingsRE — scripts

## Monthly FlexMLS link refresh

Each weekly page (`weekly/*.html`) loads its FlexMLS "View Current Active
Listings" button URL from `data/links.json`. Those FlexMLS share links expire
roughly every 30 days, so they need to be regenerated each month.

This directory has the workflow to do it without hand-editing JSON.

### Files

- `regen-links.js` — Node script. No external dependencies.
- `links-input.csv` — your one-row-per-segment input for the next regen.
- `../data/links.template.json` — immutable per-segment metadata (search name,
  label, criteria notes). Edit this file when search criteria change.
- `../data/links.json` — the generated artifact the site reads at runtime.

### Step-by-step

1. **Refresh the FlexMLS share links.** In FlexMLS, open each saved search
   (`WSS-MF-2plus-Under1M`, `WSS-COM-Retail`, ...) and generate a new public
   share link. Note the resulting URL and the current result count.

2. **Fill in `scripts/links-input.csv`.** One row per segment in the form:

   ```csv
   segment_slug,result_count,mls_url
   mf-small-under1m,733,https://www.flexmls.com/link.html?XXXXX&utm_source=savingsre&...
   ```

   Lines starting with `#` are ignored; the header row is optional but
   recommended. A `result_count` of `0` with an empty `mls_url` is acceptable
   for segments where the search currently returns nothing — the page will
   render the "search link will be available shortly" pending state.

3. **Regenerate the JSON:**

   ```bash
   node scripts/regen-links.js
   ```

   This writes `data/links.json` with `generated = today (UTC)` and
   `expires = today + 30 days`. Only segments with a non-empty `mls_url` get
   an `expires` date; empty links stay marked unset.

4. **Commit the resulting `data/links.json`.** Don't commit `links-input.csv`
   filled with one-shot working data unless you want it preserved between runs
   (the file is a working buffer, not a source of truth — the source of truth
   is `data/links.template.json` plus FlexMLS itself).

### Validations performed

- Slugs in the CSV that aren't in `links.template.json` cause a hard error
  (the script exits non-zero, no file written).
- Slugs in the template not present in the CSV print a warning, and the
  resulting `data/links.json` for that slug gets `result_count: 0,
  mls_url: ''`.
- Duplicate slug rows in the CSV print a warning; last occurrence wins.

### Open question — `mf-large-20plus`

The previous `data/links.json` had `result_count: 0` for this segment and a
note suggesting we drop the criteria to 10+ units. That decision is parked —
edit `data/links.template.json` (and the corresponding FlexMLS saved search)
when ready, and update the page's "Min Units" spec in
`weekly/mf-large-20plus.html` to match.
