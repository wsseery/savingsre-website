# FlexMLS Link Regeneration — Agentic AI Script (v2)

> Paste this as the task/prompt in any agentic AI browser (Claude Cowork, Comet, ChatGPT Operator, etc.). The user must be logged into FlexMLS at flr.flexmls.com before running.
>
> **Revised May 9, 2026** based on real-run findings: Share button does NOT produce search URLs — must use Email → "Just give me the link" → Get Link instead.

---

## TASK OVERVIEW

You are an automation agent helping Bill Seery regenerate his 11 FlexMLS saved search share links. These links power the SavingsRE investor website (savingsre.com) and monthly email campaigns. They expire ~30 days after generation and must be regenerated.

**Goal:** Visit each of the 11 saved searches in FlexMLS, generate a fresh shareable public link, and output all 11 new URLs as a structured JSON block ready to paste back into Perplexity Computer.

---

## PRE-REQUISITES (CONFIRM BEFORE STARTING)

1. The user is logged into **flr.flexmls.com** (Beaches MLS for Florida)
2. The user has these 11 saved searches already created in their FlexMLS account:
   - WSS-MF-2plus-Under1M
   - WSS-MF-2plus-1Mto3M
   - WSS-MF-5plus-All
   - WSS-MF-20plus-All
   - WSS-COM-Retail
   - WSS-COM-Industrial
   - WSS-COM-Office
   - WSS-COM-MixedUse
   - WSS-COM-Land
   - WSS-LUX-Oceanfront
   - WSS-LUX-CountryClub

**Verify all 11 exist** by typing `WSS-` into the saved-searches filter box on the Saved Searches list page. You should see exactly these 11 (plus any other unrelated searches that happen to start with WSS-). If any of the 11 are missing, stop and ask the user to recreate them using the criteria in the appendix.

---

## STEP-BY-STEP PROCEDURE

### Step 1 — Navigate to Saved Searches
1. Go to flr.flexmls.com
2. Wait for the page to fully load (FlexMLS uses iframes — be patient)
3. Click "Search" in the top navigation → look for "Saved Searches" or "My Searches"
4. The list shows all of the user's saved searches (could be 1,000+)
5. Use the **"Find a saved search"** filter box at the top — type `WSS-` to narrow the list to just the 11 SavingsRE searches. Filter is real-time after a 1–2 second delay.

### Step 2 — For Each Saved Search

**IMPORTANT:** Do NOT use the **Share** button. The Share → Permalink option produces a single-listing URL, not a search URL. Always use the **Email** workflow described below.

Repeat this for all 11 searches:

1. **Click on the search name** (e.g., `WSS-MF-2plus-Under1M`) to open it. The search runs and displays results.
2. **Note the result count** from the top toolbar (e.g., "Results: 210"). Record this number.
3. Click the **Email** button (top-right toolbar — NOT Share).
4. On the "Listings to Email" page, in the **left sidebar**:
   - Select the **All Results (N)** radio button. **CRITICAL:** by default FlexMLS often lands on "Selected (200)" because it auto-selects the first 200 visible rows. If you don't switch to "All Results", your link will only contain 200 listings instead of the full set.
   - Leave **Version = Public**.
   - Leave **Documents** and **Open Houses** checked.
5. In the main panel, confirm the dropdown **"How would you like to send this email?"** is set to **Just give me the link** (this is the default).
6. **Ignore the Recipients/contact fields** — leave them blank. The "Notify me the first time the recipient views this page" checkbox can be left as-is; it doesn't affect the link.
7. Click the **Get Link** button (bottom-right of the page).
8. The page refreshes and shows: "An email was not sent by Flexmls" with a "Click to view listing(s)" link and a "valid until [date]" line.
9. Click **Copy To Clipboard**. The clipboard contains text like:

   ```
   Follow this link to see the page:
   https://www.flexmls.com/link.html?XXXXXXXXXXXX,15,1
   This link is valid until M/D/YYYY.
   ```

10. **Extract just the URL** and **strip the trailing `,15,1`** plus the surrounding "Follow this link…" / "This link is valid until…" text. Final form: `https://www.flexmls.com/link.html?XXXXXXXXXXXX`
11. Record the search name, result count, and clean URL.
12. Click **Saved Searches** in the top nav to return to the list, then move to the next search.

### Step 3 — Output the Results

After all 11 searches are processed, output the results as a **JSON block** in this exact format (no `,15,1` suffix, no surrounding text):

```json
{
  "regenerated_on": "YYYY-MM-DD",
  "searches": [
    { "search_name": "WSS-MF-2plus-Under1M", "result_count": 0, "mls_url": "https://www.flexmls.com/link.html?XXXXX" },
    { "search_name": "WSS-MF-2plus-1Mto3M", "result_count": 0, "mls_url": "https://www.flexmls.com/link.html?XXXXX" },
    { "search_name": "WSS-MF-5plus-All", "result_count": 0, "mls_url": "https://www.flexmls.com/link.html?XXXXX" },
    { "search_name": "WSS-MF-20plus-All", "result_count": 0, "mls_url": "https://www.flexmls.com/link.html?XXXXX" },
    { "search_name": "WSS-COM-Retail", "result_count": 0, "mls_url": "https://www.flexmls.com/link.html?XXXXX" },
    { "search_name": "WSS-COM-Industrial", "result_count": 0, "mls_url": "https://www.flexmls.com/link.html?XXXXX" },
    { "search_name": "WSS-COM-Office", "result_count": 0, "mls_url": "https://www.flexmls.com/link.html?XXXXX" },
    { "search_name": "WSS-COM-MixedUse", "result_count": 0, "mls_url": "https://www.flexmls.com/link.html?XXXXX" },
    { "search_name": "WSS-COM-Land", "result_count": 0, "mls_url": "https://www.flexmls.com/link.html?XXXXX" },
    { "search_name": "WSS-LUX-Oceanfront", "result_count": 0, "mls_url": "https://www.flexmls.com/link.html?XXXXX" },
    { "search_name": "WSS-LUX-CountryClub", "result_count": 0, "mls_url": "https://www.flexmls.com/link.html?XXXXX" }
  ]
}
```

---

## TROUBLESHOOTING

**Do NOT use the Share button.**
Share → Permalink generates a single-listing URL, not a search URL. Always use Email → "Just give me the link" → Get Link.

**If "Selected (N)" is auto-selected on the Email page:**
FlexMLS pre-selects the first 200 visible rows when you load a saved search. You must manually switch the radio button to **All Results (N)** before clicking Get Link, otherwise the link will be capped at 200 listings.

**If a search returns 0 results:**
Set `mls_url` to empty string `""` and `result_count` to `0`. Note this in the output — the user will know that segment has no listings this period.

**If you can't find a saved search:**
Stop immediately and report which search is missing. Provide the criteria from the appendix below so the user can recreate it.

**Saved-search filter not finding it:**
The "Find a saved search" filter has a 1–2 second delay. Wait fully before retyping. If the search still doesn't appear, scroll the list manually to verify.

---

## OUTPUT REQUIREMENTS

When you complete the task, your final response should contain:

1. **Summary statement** — "Regenerated X of 11 FlexMLS links on [date]"
2. **The JSON block** — exactly as formatted above, all 11 searches included even if a URL is empty
3. **Any notes** — if any searches had issues, list them at the end

The JSON block will be pasted directly into a Perplexity Computer conversation to update the SavingsRE website's `links.json` file and trigger a redeploy. It will also be used to update the monthly email campaign.

---

## DATA-QUALITY ITEMS TO VERIFY

Before/during regeneration, sanity-check these known issues:

**WSS-MF-2plus-1Mto3M price filter**
On the May 2026 run, this search returned 473 results but the first listing was at $799,000 — below the $1M floor. The saved search's price filter appears to be missing or misconfigured. Verify the price range is set to **$1,000,000–$3,000,000** before clicking Email/Get Link. If listings below $1M appear in results, re-save the search criteria in FlexMLS before generating the link.

---

## APPENDIX — SEARCH CRITERIA REFERENCE

If any saved search needs to be recreated, here are the exact criteria. **All searches: leave county/location blank** to cover all MLS counties (Broward, Palm Beach, Martin, St. Lucie, select Miami-Dade), **status = Active only**.

### Multifamily (Template: "2-Residential Income")

| # | Search Name | Units | Price Range |
|---|-------------|-------|-------------|
| 1 | WSS-MF-2plus-Under1M | Min: 2, no max | Max $999,999 |
| 2 | WSS-MF-2plus-1Mto3M | Min: 2, no max | $1M – $3M |
| 3 | WSS-MF-5plus-All | Min: 5, no max | None |
| 4 | WSS-MF-20plus-All | Min: 20, no max | None |

### Commercial (Template: "4-Commercial Sale", $750K minimum)

| # | Search Name | Sub-Types |
|---|-------------|-----------|
| 5 | WSS-COM-Retail | Retail, Strip Center, Shopping Center, Free Standing |
| 6 | WSS-COM-Industrial | Industrial, Warehouse, Manufacturing, Flex |
| 7 | WSS-COM-Office | Office, Medical Office, Professional |
| 8 | WSS-COM-MixedUse | Mixed Use |
| 9 | WSS-COM-Land | Commercial Land, Industrial Land, Unimproved Land |

### Residential Luxury (Template: "1-Residential")

| # | Search Name | Filter | Min Price |
|---|-------------|--------|-----------|
| 10 | WSS-LUX-Oceanfront | Waterfront = Yes (or Ocean Frontage) | $1,500,000 |
| 11 | WSS-LUX-CountryClub | Subdivision contains: Boca West OR Broken Sound OR Woodfield OR Mizner OR Ibis Golf OR Admirals Cove OR BallenIsles | $750,000 |

---

## WHAT HAPPENS AFTER YOU OUTPUT THE JSON

Bill will paste your JSON output back into a Perplexity Computer conversation. Computer will then:

1. Update `/data/links.json` in the savingsre-website GitHub repo
2. Update the `last_updated`, `generated`, and `expires` dates (expires = +30 days, matching the FlexMLS "valid until" date)
3. Commit and push to main → GitHub Pages auto-deploys → savingsre.com updates within ~1 minute
4. Use the same JSON to refresh the monthly email campaign in Agile CRM with the new links

So your job is just: **navigate FlexMLS, generate share links via the Email workflow, output the JSON.** That's it.

---

## CONTEXT / WHY THIS MATTERS

The savingsre.com website has 11 segment pages (multifamily, commercial, luxury) that each link to a live FlexMLS search. These links expire every ~30 days. Without regeneration, the buttons go dead and the site shows a "search link will be available shortly" fallback. Monthly regeneration keeps everything live.

Each segment also has its own monthly email campaign in Agile CRM that includes the same FlexMLS link. When links are regenerated, the campaign HTML is updated to use the new URLs.

Begin now. Confirm the user is logged into flr.flexmls.com and proceed through all 11 searches using the **Email → "Just give me the link" → Get Link** workflow.
