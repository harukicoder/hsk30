#!/usr/bin/env python3
"""Extract Taiwan's TBCL grammar-point list into a machine-readable form.

TBCL (臺灣華語文能力基準) publishes three inventories: characters, words, and
**496 grammar points**. ``tbcl_extract.py`` handles the first two. This handles
the third, which completes the set and for which no machine-readable version
appears to exist.

NAER asserts rights over the lists, so nothing of theirs is redistributed here.
Download the official spreadsheet yourself, free, from

    https://coct.naer.edu.tw/page.jsp?ID=41
      臺灣華語文能力基準語法點表_112-01-04.xlsx

then point this script at it.

    python3 scripts/tbcl_grammar_extract.py --xlsx tbcl_grammar.xlsx --out grammar.json

## The starred levels, again, and worse

The word and character lists grade into levels written 第N級 and 第N*級, and a
reader who filters on the unstarred form silently loses 442 of 3,100 characters.
The grammar list has the same two forms and the loss is far larger:
**212 of 496 points carry a starred level**, so the naive filter discards 43% of
the inventory and returns a plausible-looking 284.

Both forms are counted at their numbered level here, on the same evidence as
before: doing so reproduces NAER's published total of 496 exactly, and doing
otherwise does not.

## What is different about grammar

**It stops at level 5.** Characters and words run to level 7; grammar points do
not exist above 5. That is a property of the standard, not a truncation of the
file, and any tool aligning the three inventories has to handle an axis that
ends early rather than assuming they are parallel.

The list also carries a two-way band, 等別, which turns out to be a strict
function of the level -- 基礎 is levels 1 to 3 (241 points) and 進階 is levels 4
and 5 (255) -- so it adds no information beyond the level and is retained only
because it is in the source.

## What this does not give you

A grammar point is not gradeable the way a character is. Coverage over an
inventory of characters is arithmetic; deciding whether a text *uses* 表所有「的」
requires parsing. The deliverable here is the extraction, not a grammar-aware
grader, and anyone reaching for the second should know the first does not
provide it.
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _xlsx import Book  # noqa: E402

#: NAER's published total. The extraction is checked against it rather than
#: against whatever the file happens to contain, which is the only way the
#: starred-level trap shows up as a failure instead of as a plausible number.
EXPECTED_TOTAL = 496

#: Levels 1-3 are 基礎, 4-5 are 進階, and nothing exists above 5.
EXPECTED_BANDS = {"基礎": (1, 3), "進階": (4, 5)}

LEVEL = re.compile(r"^第([1-7])(\*?)級$")


def extract(path):
    book = Book(path)
    sheet = list(book.sheets)[0]
    rows = list(book.rows(sheet))
    if not rows:
        raise SystemExit("%s: no rows" % path)

    header = [c.strip() for c in rows[0]]
    def col(name):
        for i, h in enumerate(header):
            if name in h:
                return i
        raise SystemExit("%s: no column matching %r; header is %s"
                         % (path, name, header))

    i_point, i_band, i_level = col("語法點"), col("等別"), col("級別")
    i_example = col("例句")

    out = []
    for row in rows[1:]:
        if len(row) <= i_level:
            continue
        point = (row[i_point] or "").strip()
        raw = (row[i_level] or "").strip()
        m = LEVEL.match(raw)
        if not point or not m:
            continue
        out.append({
            "point": point,
            "level": int(m.group(1)),
            "starred": m.group(2) == "*",
            "band": (row[i_band] or "").strip(),
            "example": (row[i_example] or "").strip() if len(row) > i_example else "",
        })
    return out


def check(rows):
    """Validate against what NAER publishes, not against what we extracted."""
    problems = []

    if len(rows) != EXPECTED_TOTAL:
        problems.append("total is %d, NAER publishes %d -- if this is short by "
                        "roughly 212, the starred levels were dropped"
                        % (len(rows), EXPECTED_TOTAL))

    for band, (lo, hi) in EXPECTED_BANDS.items():
        levels = {r["level"] for r in rows if r["band"] == band}
        if levels and not levels <= set(range(lo, hi + 1)):
            problems.append("band %s spans levels %s, expected %d-%d"
                            % (band, sorted(levels), lo, hi))

    above = {r["level"] for r in rows if r["level"] > 5}
    if above:
        problems.append("levels above 5 present (%s); TBCL grades no grammar "
                        "above level 5" % sorted(above))

    missing = [r for r in rows if not r["point"]]
    if missing:
        problems.append("%d rows have no grammar point" % len(missing))

    return problems


def report(rows):
    per = collections.Counter(r["level"] for r in rows)
    starred = sum(1 for r in rows if r["starred"])

    print("TBCL grammar points: %d" % len(rows))
    print()
    print("  %-7s %6s %6s %11s   %s" % ("level", "new", "cum", "of which *", "band"))
    cum = 0
    for level in sorted(per):
        cum += per[level]
        s = sum(1 for r in rows if r["level"] == level and r["starred"])
        band = next((r["band"] for r in rows if r["level"] == level), "")
        print("  %-7d %6d %6d %11d   %s" % (level, per[level], cum, s, band))
    print()
    print("  starred entries: %d of %d (%.1f%%)"
          % (starred, len(rows), 100.0 * starred / len(rows)))
    print("  filtering them out would leave %d and look plausible"
          % (len(rows) - starred))
    print()
    print("  grammar stops at level %d; the character and word lists run to 7"
          % max(per))

    dupes = [p for p, c in collections.Counter(r["point"] for r in rows).items() if c > 1]
    if dupes:
        print()
        print("  names appearing more than once: %s" % ", ".join(dupes))
        print("  (the same form graded at two levels -- kept as separate entries)")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--xlsx", required=True, help="official 語法點表 .xlsx")
    ap.add_argument("--out", help="write JSON here (nothing is written by default)")
    args = ap.parse_args()

    rows = extract(args.xlsx)
    report(rows)

    problems = check(rows)
    print()
    if problems:
        for p in problems:
            print("  FAIL  %s" % p, file=sys.stderr)
        return 1
    print("  validates against NAER's published total of %d" % EXPECTED_TOTAL)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump({"grammar_points": rows}, fh, ensure_ascii=False, indent=1)
        print("  wrote %s" % args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
