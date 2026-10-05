"""compliance-grep and data-leak: what a change ADDS to this public repo.

  safety_checks.py <base-sha>

Compares the working tree (HEAD) against <base-sha> and looks only at what the
change adds, so text already on the site never blocks an unrelated change.
Exits non-zero on any finding, with every finding listed.

Rules, all from this repo's CLAUDE.md (mirrored by hand, 2026-10-04):
  - Never cite the insurance licence G164863 on this site.
  - Never mix ventures: nothing touches DialRidge; AlphaGen's GA4 tag never
    appears here.
  - Disguised listing data only: no real addresses, owner names, MLS numbers,
    parcel or folio IDs in published data. No SSNs anywhere.

AlphaGen is cross-promoted on many existing pages, so a new mention is a note
for a human to look at, not a failure.
"""

import os
import re
import subprocess
import sys


def run(args):
    return subprocess.run(args, check=True, capture_output=True,
                          encoding="utf-8", errors="replace").stdout


EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"


def resolve(base):
    """A first push (before = 000...) or a root commit has no parent to compare
    with; compare against the empty tree, so everything counts as added."""
    try:
        run(["git", "rev-parse", "--verify", "--quiet", base + "^{tree}"])
        return base
    except subprocess.CalledProcessError:
        return EMPTY_TREE


def changed(base):
    out = run(["git", "diff", "--name-status", "--no-renames", base, "HEAD"])
    return [line.split("\t", 1)[1] for line in out.splitlines() if not line.startswith("D")]


def text_of(ref, path):
    try:
        if ref is None:
            with open(path, encoding="utf-8") as f:
                return f.read()
        return run(["git", "show", f"{ref}:{path}"])
    except (subprocess.CalledProcessError, FileNotFoundError, UnicodeDecodeError):
        return None


TEXT_EXT = re.compile(r"\.(html?|xml|txt|csv|json|md|js|css|svg)$", re.I)

FAIL_TERMS = {
    "G164863": "the insurance licence (CLAUDE.md: never cite it on this site)",
    "dialridge": "DialRidge (CLAUDE.md: never mix ventures)",
    "G-RG0E11KB0Q": "AlphaGen's GA4 tag",
}
NOTE_TERMS = {"alphagen": "AlphaGen mention: check it is the approved cross-promotion"}

# Keys whose values identify a real property or person. A null or empty value
# is fine; any value is a finding.
SENSITIVE_KEY = re.compile(
    r'"(address|street|street_address|full_address|owner[a-z_]*|seller_name|'
    r'mls|mls_number|mls_id|listing_id|parcel[a-z_]*|folio[a-z_]*|apn)"\s*:\s*"([^"]+)"', re.I)
SSN = re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)")


def count(rx, text):
    return len(rx.findall(text or ""))


def main():
    base = resolve(sys.argv[1])
    failures, notes = [], []
    for path in changed(base):
        if path.startswith(".github/") or not TEXT_EXT.search(path):
            if path.lower().endswith(".pdf"):
                notes.append(f"`{path}`: PDF not searched; open it and confirm it is the "
                             "disguised version before it is linked")
            continue
        after = text_of(None, path)
        if after is None:
            continue
        before = text_of(base, path) or ""

        for term, why in {**FAIL_TERMS, **NOTE_TERMS}.items():
            rx = re.compile(re.escape(term), re.I)
            added = count(rx, after) - count(rx, before)
            if added > 0:
                (failures if term in FAIL_TERMS else notes).append(
                    f"`{path}`: adds `{term}` ({added}x): {why}")

        if count(SSN, after) > count(SSN, before):
            failures.append(f"`{path}`: adds something shaped like an SSN (###-##-####)")

        old = {(k.lower(), v) for k, v in SENSITIVE_KEY.findall(before)}
        new = sorted({(k.lower(), v) for k, v in SENSITIVE_KEY.findall(after)} - old)
        if new:
            sample = "; ".join(f"{k}={v}" for k, v in new[:3])
            more = f" (+{len(new) - 3} more)" if len(new) > 3 else ""
            failures.append(f"`{path}`: adds {len(new)} identifying listing field(s): "
                            f"{sample}{more}. Public data must be the disguised export "
                            "(Ref code, area, price band)")

    lines = ["### compliance-grep: " + ("**failed**" if failures else "**passed**"), ""]
    lines += [f"- {f}" for f in failures] or ["Nothing banned or identifying added."]
    if notes:
        lines += ["", "**Notes (not failures)**"] + [f"- {n}" for n in notes]
    text = "\n".join(lines)
    print(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(text + "\n")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
