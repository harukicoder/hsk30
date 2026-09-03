#!/usr/bin/env python3
"""Do PRC-derived and Taiwan-derived CEFR labels agree on the same Chinese text?

Chinese has two proficiency ecosystems. The PRC's standard publishes no CEFR
alignment, so every HSK-to-CEFR table in use is folk knowledge. Taiwan's does:
TOCFL was built at National Taiwan Normal University with the CEFR as its
blueprint, and its levels carry an official correspondence. That gives a
reference against which the folk tables can, for the first time, be tested.

Both frameworks are applied character-level, exactly as hsk30.grade_tokens
does: proper nouns dropped by pinyin capitalisation, punctuation stripped,
lowest level whose cumulative inventory covers 95% of running characters.
Word-level grading is not an option for either -- even using the entire list,
median word coverage of this corpus is 48.5% (TOCFL) and 61.9% (HSK), because
authored segmentation groups phrases no list contains.

The TOCFL word list is NOT redistributed with this repository; SC-TOP asserts
rights over it. Download it yourself, free, from the official site:

    https://tocfl.edu.tw/tocfl/index.php/teach/download
    -> 華語八千詞表  (8000zhuyin_202409.zip)

then point this script at the .xlsx inside it:

    python3 scripts/tocfl_compare.py --xlsx path/to/華語八千詞表20240923.xlsx
"""
import argparse
import collections
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))
import hsk30  # noqa: E402
from _xlsx import Book  # noqa: E402

CORPUS = os.path.join(os.path.dirname(__file__), "..", "corpus")

# The sheets do not share a column layout: Novice 1 through Level 2 carry a
# task-domain column first, Levels 3 to 5 do not. The vocabulary column is
# located by its header, and the extraction is checked for being Chinese --
# counting non-empty cells alone passes while silently reading the pinyin.
SHEETS = [("準備級一級(Novice 1)", 1, 160), ("準備級二級(Novice 2)", 2, 234),
          ("入門級(Level 1)", 3, 347), ("基礎級(Level 2)", 4, 485),
          ("進階級(Level 3)", 5, 1173), ("高階級(Level 4)", 6, 2342),
          ("流利級(Level 5)", 7, 2776)]

# SC-TOP / NTNU published correspondence. Levels 1-2 sit below A1 by design;
# the list stops at 流利級, so it describes no C2 tier.
TOCFL_CEFR = {1: "pre-A1", 2: "pre-A1", 3: "A1", 4: "A2", 5: "B1", 6: "B2", 7: "C1"}

# Two HSK tables, neither endorsed by any issuing body. The naive one is
# ubiquitous in learner material; the compressed one encodes the objection that
# vocabulary coverage overstates communicative range.
NAIVE = {1: "A1", 2: "A2", 3: "B1", 4: "B2", 5: "C1", 6: "C2", 7: "C2", 8: "C2", 9: "C2"}
COMPRESSED = {1: "A1", 2: "A1", 3: "A2", 4: "B1", 5: "B2", 6: "B2", 7: "C1", 8: "C1", 9: "C2"}
ORDER = ["pre-A1", "A1", "A2", "B1", "B2", "C1", "C2", "above"]


def opencc_tables(path):
    """Traditional-to-simplified tables, from the OpenCC dump shipped by Pinyora."""
    src = open(path, encoding="utf-8").read()
    body = src[src.index("window.OPENCC=") + len("window.OPENCC="):].rstrip().rstrip(";")
    d = json.loads(body)
    return d["t2sC"], d["t2sP"]


def load_tocfl(xlsx, t2s_char, t2s_phrase):
    book = Book(xlsx)
    words = {}
    for sheet, level, official in SHEETS:
        rows = list(book.rows(sheet))
        col = next(i for i, h in enumerate(rows[0]) if "詞彙" in h or "Vocabulary" in h)
        raw = [r[col] for r in rows[1:] if len(r) > col and r[col].strip()]
        if len(raw) != official:
            raise SystemExit("%s: %d entries, official count is %d" % (sheet, len(raw), official))
        bad = [w for w in raw if not hsk30.hanzi(w)]
        if bad:
            raise SystemExit("%s: %d non-Chinese entries (wrong column?) e.g. %r"
                             % (sheet, len(bad), bad[:3]))
        for w in raw:
            s = t2s_phrase.get(w) or "".join(t2s_char.get(c, c) for c in w)
            words.setdefault(s, level)
    return words


def derive_characters(words):
    """A character's level is the lowest level of any word containing it.

    TOCFL publishes no character list at this tier. --control measures what
    this derivation costs by applying it to the PRC's own words, where an
    official list exists to check against.
    """
    chars = {}
    for word, level in words.items():
        for ch in hsk30.hanzi(word):
            if level < chars.get(ch, 99):
                chars[ch] = level
    return chars


def chars_of(tokens):
    out = []
    for t in tokens:
        if hsk30.is_proper_noun(t.get("py", "")):
            continue
        out.extend(hsk30.hanzi(hsk30.strip_punct(t.get("hz", ""))))
    return out


def level_at(chars, cumulative, maxlevel, threshold=0.95):
    if not chars:
        return None
    for level in range(1, maxlevel + 1):
        if sum(1 for c in chars if c in cumulative[level]) / len(chars) >= threshold:
            return level
    return None


def load_corpus(name):
    with open(os.path.join(CORPUS, name), encoding="utf-8") as fh:
        for line in fh:
            row = json.loads(line)
            yield [w for s in row["sentences"] for w in s["words"]]


def control():
    """Is the gap a framework effect, or an artifact of deriving characters?

    Apply the identical derivation to the PRC's own words and grade against
    that, holding the framework fixed. If grades move, the comparison is
    confounded.
    """
    derived = derive_characters(hsk30.words("2025"))
    cum = {l: {c for c, v in derived.items() if v <= l} for l in range(1, 10)}
    shifts = collections.Counter()
    for tokens in load_corpus("hsk30_graded_readers.jsonl"):
        official = hsk30.grade_tokens(tokens, standard="2025").level or 10
        shifts[(level_at(chars_of(tokens), cum, 9) or 10) - official] += 1
    n = sum(shifts.values())
    print("\nControl -- PRC framework, official vs derived character inventory")
    print("  official characters %d, derived %d"
          % (len(hsk30.characters("2025")), len(derived)))
    print("  identical grade on %d/%d texts (%.1f%%); shifts %s"
          % (shifts[0], n, 100.0 * shifts[0] / n, {k: shifts[k] for k in sorted(shifts)}))
    if shifts[0] == n:
        print("  derivation changes nothing here, so the Taiwan gap below is not its artifact")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--xlsx", required=True, help="official TOCFL 8,000-word workbook")
    ap.add_argument("--opencc", default=os.path.expanduser(
        "~/Documents Mac/Chinese/GITHUB_Chinese_Books/data/opencc.js"),
        help="OpenCC table dump (traditional-to-simplified)")
    ap.add_argument("--control", action="store_true", help="run the derivation control")
    args = ap.parse_args()

    t2sC, t2sP = opencc_tables(args.opencc)
    words = load_tocfl(args.xlsx, t2sC, t2sP)
    chars = derive_characters(words)
    cum = {l: {c for c, v in chars.items() if v <= l} for l in range(1, 8)}

    print("TOCFL: 7,517 entries -> %d unique after traditional-to-simplified,"
          " %d derived characters" % (len(words), len(chars)))
    print("PRC 2025: %d official characters" % len(hsk30.characters("2025")))

    if args.control:
        control()

    for name, label in (("hsk30_graded_readers.jsonl", "graded readers"),
                        ("hsk30_heldout.jsonl", "held-out")):
        rows = list(load_corpus(name))
        tw = [TOCFL_CEFR.get(level_at(chars_of(t), cum, 7), "above") for t in rows]
        hsk = [hsk30.grade_tokens(t, standard="2025").level for t in rows]
        n = len(rows)
        print("\n== %s (n=%d) ==" % (label, n))
        for table_name, table in (("naive 1:1", NAIVE), ("compressed", COMPRESSED)):
            prc = [table.get(l, "above") for l in hsk]
            diff = [(a, h) for a, h in zip(tw, prc) if a != h]
            higher_tw = sum(1 for a, h in diff if ORDER.index(a) > ORDER.index(h))
            gaps = collections.Counter(ORDER.index(a) - ORDER.index(h) for a, h in zip(tw, prc))
            print("  %-11s differs %3d/%d (%5.1f%%)  Taiwan higher %2d / PRC higher %2d  gaps %s"
                  % (table_name, len(diff), n, 100.0 * len(diff) / n,
                     higher_tw, len(diff) - higher_tw, {k: gaps[k] for k in sorted(gaps)}))
        print("  TOCFL bands (official):  %s"
              % dict(sorted(collections.Counter(tw).items(), key=lambda x: ORDER.index(x[0]))))

    print("\nNeither HSK table is official. Taiwan's correspondence is.")


if __name__ == "__main__":
    main()
