#!/usr/bin/env python3
"""Extract Taiwan's TBCL character and word lists into a machine-readable form.

TBCL (臺灣華語文能力基準) is Taiwan's national Chinese proficiency standard,
developed at the National Academy for Educational Research over six years. It is
the counterpart of the PRC's GF0025-2021, and the standard that TOCFL score
reports carry a correspondence to. No machine-readable extraction of it appears
to exist.

NAER asserts all rights over the lists, so nothing of theirs is redistributed
here. Download the official spreadsheets yourself, free, from

    https://coct.naer.edu.tw/page.jsp?ID=41
      漢字表 (character list) .xlsx
      詞語表 (word list) .xlsx

then point this script at them.

    python3 scripts/tbcl_extract.py --chars tbcl_chars.xlsx --words tbcl_words.xlsx

## The starred levels

Both lists grade into seven levels, but levels 1 to 4 each appear in two forms:
第N級 and 第N*級. Levels 5 to 7 have no starred form. The two together make the
official per-level totals -- level 1 has 163 unstarred plus 83 starred
characters, and the published figure for TBCL level 1 is 246 -- so a reader who
filters on 第N級 alone silently loses 442 of 3,100 characters and 1,398 of
14,452 words.

**What the asterisk denotes is not established here.** It does not track the
word list's own 核心詞 (core word) marking: both forms contain core and
non-core entries. Until it is settled from the official reference guide, this
extraction records the flag and treats a starred entry as belonging to its
numbered level, which is the reading the published level-1 character total
supports.
"""
import argparse
import collections
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _xlsx import Book  # noqa: E402

HAN = re.compile(r"[一-鿿]")
LEVEL = re.compile(r"^第([1-7])(\*?)級$")

#: Published totals, used as the extraction's own check.
EXPECTED = {"characters": 3100, "words": 14452}
#: NAER publishes 246 characters at level 1; the split is 163 + 83 starred.
EXPECTED_L1_CHARS = 246


def extract(path, word_col_names, level_col_names):
    book = Book(path)
    sheet = list(book.sheets)[0]
    rows = list(book.rows(sheet))
    header = rows[0]
    def find(names):
        for i, h in enumerate(header):
            if h.strip() in names:
                return i
        raise SystemExit("%s: no column among %s in %s" % (path, names, header))
    wc, lc = find(word_col_names), find(level_col_names)

    out = []
    for r in rows[1:]:
        if len(r) <= max(wc, lc):
            continue
        item, raw = r[wc].strip(), r[lc].strip()
        m = LEVEL.match(raw)
        if not item or not m:
            continue
        out.append({"item": item, "level": int(m.group(1)),
                    "starred": m.group(2) == "*"})
    return out


def check(kind, rows):
    n = len(rows)
    if n != EXPECTED[kind]:
        raise SystemExit("%s: extracted %d, official total is %d"
                         % (kind, n, EXPECTED[kind]))
    bad = [r["item"] for r in rows if not HAN.search(r["item"])]
    if bad:
        raise SystemExit("%s: %d non-Chinese entries, e.g. %r" % (kind, len(bad), bad[:3]))
    if kind == "characters":
        l1 = sum(1 for r in rows if r["level"] == 1)
        if l1 != EXPECTED_L1_CHARS:
            raise SystemExit("characters: level 1 has %d, NAER publishes %d"
                             % (l1, EXPECTED_L1_CHARS))


def report(kind, rows):
    per = collections.Counter(r["level"] for r in rows)
    star = collections.Counter(r["level"] for r in rows if r["starred"])
    total, cum = 0, []
    for lv in range(1, 8):
        total += per[lv]; cum.append(total)
    print("\n%s: %d entries, %d unique" % (kind, len(rows), len({r["item"] for r in rows})))
    print("  %-10s %s" % ("per level", [per[l] for l in range(1, 8)]))
    print("  %-10s %s" % ("of which *", [star[l] for l in range(1, 8)]))
    print("  %-10s %s" % ("cumulative", cum))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--chars", required=True, help="official 漢字表 .xlsx")
    ap.add_argument("--words", required=True, help="official 詞語表 .xlsx")
    ap.add_argument("--out", help="write JSON here (nothing is written by default)")
    args = ap.parse_args()

    chars = extract(args.chars, {"漢字", "字"}, {"級別"})
    words = extract(args.words, {"word", "詞語"}, {"ji", "級別"})
    check("characters", chars)
    check("words", words)
    report("characters", chars)
    report("words", words)
    print("\nBoth reconcile with the official totals, starred levels included.")

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump({"characters": chars, "words": words}, fh, ensure_ascii=False)
        print("wrote %s -- do not redistribute; NAER asserts rights" % args.out)


if __name__ == "__main__":
    main()
