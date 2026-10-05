#!/usr/bin/env python3
"""Download a Florida Realtors market-summary PDF and print its text (statewide residential row).
Usage: python3 market/tools/pdf_text.py https://www.floridarealtors.org/sites/default/files/2026-10/September-2026-Fla-single-family-summary.pdf"""
import sys, io, urllib.request
from urllib.parse import urlparse
import pdfplumber
u = sys.argv[1]
if urlparse(u).hostname not in ("www.floridarealtors.org", "floridarealtors.org") or not u.lower().endswith(".pdf"):
    sys.exit("refused: only floridarealtors.org PDFs")
req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
data = urllib.request.urlopen(req, timeout=60).read()
with pdfplumber.open(io.BytesIO(data)) as pdf:
    print("\n".join((pg.extract_text() or "") for pg in pdf.pages)[:12000])
