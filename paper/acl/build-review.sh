#!/bin/bash
# Build the double-blind ARR submission. Derives main-review.tex from main.tex,
# so the submission cannot drift from the preprint.
#
# The guard here is the inverse of build.sh's: that one fails a preprint which
# is NOT named, this one fails a submission which IS.
set -euo pipefail
cd "$(dirname "$0")"
python3 make_review.py
tectonic -X compile main-review.tex --keep-logs
echo
echo "built main-review.pdf ($(wc -c < main-review.pdf | tr -d ' ') bytes)"
echo "overfull boxes: $(grep -c "Overfull" main-review.log || true)"
python3 - <<'PY'
import re, sys
d = open("main-review.pdf", "rb").read()
hits = [t.decode() for t in (b"Serrano", b"harukicoder", b"alvaro", b"orcid", b"zenodo")
        if t.lower() in d.lower()]
if hits:
    sys.exit("ANONYMITY BROKEN: %s appears in the PDF" % ", ".join(hits))
a = open("main-review.aux", encoding="utf-8", errors="replace").read()
m = re.search(r"newlabel\{sec:conclusion\}\{\{[^}]*\}\{(\d+)\}", a)
page = int(m.group(1)) if m else 99
print("anonymity: clean")
print("content ends on page %d (ACL limit 8)%s"
      % (page, "" if page <= 8 else "  *** OVER LIMIT ***"))
PY
