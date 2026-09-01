#!/bin/bash
# Build the paper. Fetches the ACL style files if absent, then compiles.
#
#   ./build.sh
#
# Needs tectonic (brew install tectonic / see tectonic-typesetting.github.io).
# Tectonic is used rather than a full TeX Live because it is a single binary
# and fetches only the packages this document actually needs.
#
# XeTeX is required, not pdfTeX: the paper quotes Chinese and loads xeCJK.
# Tectonic uses XeTeX internally, so this is handled.
set -euo pipefail
cd "$(dirname "$0")"

BASE="https://raw.githubusercontent.com/acl-org/acl-style-files/master"
for f in acl.sty acl_natbib.bst; do
  if [ ! -f "$f" ]; then
    echo "fetching $f"
    curl -sSfL -o "$f" "$BASE/$f"
  fi
done

# The CJK font is the one portability hazard. Songti SC ships with macOS;
# Noto Serif CJK SC is the usual Linux and Overleaf equivalent.
if ! grep -q "setCJKmainfont" main.tex; then
  echo "warning: no CJK font declared; Chinese will not render" >&2
fi

tectonic -X compile main.tex --keep-logs

echo
echo "built main.pdf ($(wc -c < main.pdf | tr -d ' ') bytes)"
grep -c "Overfull" main.log | xargs echo "overfull boxes:"
if grep -qiE "error" main.blg 2>/dev/null; then
  echo "BIBTEX ERRORS — check main.blg" >&2
  exit 1
fi
echo "bibliography: clean"
