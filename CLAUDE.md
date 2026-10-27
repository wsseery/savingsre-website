# CLAUDE.md — savingsre-website

Repo-local facts only. Everything else lives in
`G:\My Drive\Claude\BillSeery\00_Global\GLOBAL_INSTRUCTIONS.md` (ventures, naming, compliance)
and `RUNBOOK_MENU.md` (procedures). **Do not copy those files here — pointers only.**

Venture `02_SavingsRE` — Savings RE / United Realty Group. Live at **savingsre.com** via GitHub
Pages + `CNAME`.

## ⛔ This repo is PUBLIC — the single most important fact about it

- **Disguised listing data only.** Real addresses, owner names and real prices live in the
  separate private repo `wsseery/savingsre-private`, never here.
- Listings are referenced by **Ref code** (e.g. `A-000NN`), area and price band — not by address.
- **Redact PII**: no SSNs, DOBs, policy numbers or financial account numbers, ever.
- Before committing anything under `data/`, `mf-top3/`, `market/` or `luxury/`, confirm it is the
  disguised export and not the source ledger.

## Compliance

- Real-estate content only. **Never mix ventures** — nothing here may imply insurance advice or
  touch DialRidge product claims.
- FL real estate licence **3333692** is the one that applies here. Never cite the insurance
  licence G164863 on this site.
- Consumer-facing pages carry the matching block from `00_Global/LEGAL_DISCLAIMERS.md`.
- Never fabricate figures, cap rates, NOI, comps or client names.

## Conventions

- **LF line endings.** `.gitattributes` (`* text=auto eol=lf`) added 2026-09-03 — this repo was
  the last of the three without one. If a diff shows every file modified with symmetric
  insert/delete counts, run `git diff --ignore-all-space`; if it is empty, that is line-ending
  churn, not a change.
- **GitHub Pages lags.** After a commit, `savingsre.com/<path>` can be 30–90s stale behind the
  CDN. Verify against `raw.githubusercontent.com/wsseery/savingsre-website/main/<path>?t=<ts>`,
  which is accurate within seconds. "It's not live yet" is almost always Pages lag, not a failed
  commit.
- **In emails, reference images and PDFs by their raw.githubusercontent URL**, not the Pages URL
  — raw is live instantly and reliable across mail clients; Pages may 404 for a minute after a
  commit.
- Weekly data snapshots are refreshed by **overwriting the same path/filename**. A new filename
  creates a new file and orphans the old one.

## Related procedures (Drive, not here)

Weekly Top-3 NOI regen · weekly market-update send · High Seller Score · FL property search ·
coastal MF shortlist · property analytics · flexmls bulk enrol. All in `RUNBOOK_MENU.md` under
`02_SavingsRE`; they run in Cowork where the MLS, Remine, Agile CRM and Gmail connectors are.
Do not reimplement them here.

## Working agreement

Draft, do not ship. Nothing goes public without Bill's explicit "ship it". Commits and pushes are
Bill's from GitHub Desktop or an approved Claude Code run — never through the Cowork device
bridge, which leaves a `.git/index.lock` GitHub Desktop cannot clear.

## Content auto-merge (GLOBAL §8a)

Who may merge is set by GLOBAL_INSTRUCTIONS §8a: a content-only PR merges itself once its
required checks pass; every other PR needs Bill. Never merge by hand, never use `--admin`.
The gate is `.github/workflows/content-automerge.yml` (classification and the auto-merge
switch), `site-checks.yml` (`playwright`, `compliance-grep`) and `content-rules.yml`, with the
logic in `.github/checks/`. `python .github/checks/classify.py --git main HEAD` shows how a
branch would be classified. It stays off until `main` requires all four checks.

What keeps a post a content PR, learned from the classifier:
- **No `BlogPosting` or other new JSON-LD.** Only a pure FAQPage block is content; every other
  schema block is code under §8a. Copy the post `<style>` block byte-for-byte from an existing post.
- New pages need exactly one `btn`/`btn-*` CTA, the Real estate block from
  `00_Global/LEGAL_DISCLAIMERS.md` verbatim, and a `## Sourced figures` table in the PR body
  (`# | Figure | Source | Link`) listing every number on the page.
- Edits to existing pages stay out of `<head>`, `<header>`, `<nav>` and `<footer>`. Anything under
  `data/`, `market/`, `top3/`, `mf-top3/`, `luxury/`, `weekly/` or `links/` is code.
