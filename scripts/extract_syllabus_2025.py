#!/usr/bin/env python3
"""Extract the vocabulary and character lists from the 2025 HSK exam syllabus.

    python3 scripts/extract_syllabus_2025.py path/to/syllabus.pdf

The syllabus (新版HSK考试大纲, 中外语言交流合作中心, published 2025-11, in force
2026-07) is distributed only as a 406-page PDF.  It has a real text layer, so
this is parsing rather than OCR.

Two tables are extracted:

  词汇大纲  pp. 79-354   11,000 words: 序号 等级 词语 拼音 词性
  汉字大纲  pp. 356-376   recognition characters (认读字) per level
  汉字大纲  pp. 377-384   writing characters (书写字) per level

**The level field carries more than a level.**  A row reading ``1（4）`` means
the word is introduced at level 1 and has a further sense or part of speech
graded at level 4.  We take the *primary* level — the one before the first
parenthesis — because that is when a learner first meets the word, which is
what grading a text requires.  Secondary levels are kept in the output for
anyone who needs them.

**Two character dimensions, not one.** HSK 3.0 grades 认读字 (recognition —
what a learner must read) separately from 书写字 (what they must write by
hand). The two are not nested the way intuition suggests: the syllabus lists
3,088 recognition characters against 1,200 writing characters, and the writing
list is allocated on a different curve (100 at level 1, then 150 per level, 500
across 7-9). Reading difficulty and production difficulty are different
questions, and only the first has ever been extractable.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

BAND = 7
VOCAB_PAGES = (79, 354)
CHAR_PAGES = (355, 376)   # 认读字 — recognition
WRITING_PAGES = (377, 384)  # 书写字 — writing

# 序号 等级 词语 拼音 词性  →  41 1 都 dōu 副
ROW = re.compile(r"^\s*(\d+)\s+(\d+(?:-9)?(?:（[^）]*）)*)\s+(\S+)\s+(\S+)\s*(.*)$")
LEVEL_HEAD = re.compile(r"HSK（(.+?)）认读字")
WRITING_HEAD = re.compile(r"HSK（(.+?)）书写字")
CHAR_ITEM = re.compile(r"(\d+)\.\s*([一-鿿])")

CN_NUM = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6}


def parse_level(token: str):
    """``'4（5）'`` → ``(4, [5])``;  ``'7-9'`` → ``(7, [])``."""
    primary, _, rest = token.partition("（")
    primary = primary.strip()
    level = BAND if primary.startswith("7") else int(primary)
    extra = []
    for m in re.finditer(r"([0-9]+(?:-9)?)", rest):
        raw = m.group(1)
        extra.append(BAND if raw.startswith("7") else int(raw))
    return level, extra


def clean_word(word: str) -> str:
    """Strip homograph markers: 所2 → 所.  Keep only Han characters."""
    word = re.sub(r"[0-9]+$", "", word.strip())
    return word if all("一" <= c <= "鿿" for c in word) and word else ""


def page_text(reader, index: int) -> str:
    try:
        return reader.pages[index].extract_text() or ""
    except Exception:
        return ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf")
    ap.add_argument("--out", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "corpus", "syllabus2025"))
    args = ap.parse_args()

    try:
        import pypdf
    except ImportError:
        print("needs pypdf: pip install pypdf", file=sys.stderr)
        return 1

    reader = pypdf.PdfReader(args.pdf)
    if len(reader.pages) != 406:
        print("warning: expected 406 pages, found %d — page ranges may be wrong"
              % len(reader.pages), file=sys.stderr)

    # ---- vocabulary ----
    # The syllabus numbers 11,000 *entries*, not 11,000 distinct words: a
    # homograph graded at two levels gets two rows (所 / 所2).  We validate on
    # entries, because that is what the published totals count, and separately
    # reduce to distinct words at their lowest level, which is what grading a
    # text needs.
    words, seen_index, dupes, entries = {}, set(), [], []
    for page in range(VOCAB_PAGES[0], VOCAB_PAGES[1] + 1):
        for line in page_text(reader, page - 1).split("\n"):
            m = ROW.match(line)
            if not m:
                continue
            index, level_tok, raw_word = m.group(1), m.group(2), m.group(3)
            word = clean_word(raw_word)
            if not word:
                continue
            level, extra = parse_level(level_tok)
            if index in seen_index:
                continue
            seen_index.add(index)
            entries.append(level)
            if word in words and words[word]["level"] != level:
                dupes.append((word, words[word]["level"], level))
                if level >= words[word]["level"]:
                    continue
            words[word] = {"level": level, "also": extra,
                           "pinyin": m.group(4), "pos": m.group(5).strip()}

    # ---- recognition characters ----
    chars, current = {}, None
    for page in range(CHAR_PAGES[0], CHAR_PAGES[1] + 1):
        text = page_text(reader, page - 1)
        for line in text.split("\n"):
            head = LEVEL_HEAD.search(line)
            if head:
                label = head.group(1)
                current = BAND if "七" in label else CN_NUM.get(label[0])
            for m in CHAR_ITEM.finditer(line):
                if current:
                    chars.setdefault(m.group(2), current)

    # ---- writing characters ----
    # The level 1-2 heading is combined ("HSK（一级）~（二级）书写字"), so the
    # first band covers both levels; we record it as level 1, which is where a
    # learner first meets those characters.
    writing, current = {}, None
    for page in range(WRITING_PAGES[0], WRITING_PAGES[1] + 1):
        for line in page_text(reader, page - 1).split("\n"):
            head = WRITING_HEAD.search(line)
            if head:
                label = head.group(1)
                current = BAND if "七" in label else CN_NUM.get(label[0])
            for m in CHAR_ITEM.finditer(line):
                if current:
                    writing.setdefault(m.group(2), current)

    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "syllabus2025_words.tsv"), "w",
              encoding="utf-8") as fh:
        fh.write("word\tlevel\talso\tpinyin\tpos\n")
        for w in sorted(words):
            d = words[w]
            fh.write("%s\t%d\t%s\t%s\t%s\n" % (
                w, d["level"], ",".join(str(x) for x in d["also"]),
                d["pinyin"], d["pos"]))
    with open(os.path.join(args.out, "syllabus2025_chars.tsv"), "w",
              encoding="utf-8") as fh:
        fh.write("character\tlevel\n")
        for c in sorted(chars):
            fh.write("%s\t%d\n" % (c, chars[c]))
    with open(os.path.join(args.out, "syllabus2025_writing_chars.tsv"), "w",
              encoding="utf-8") as fh:
        fh.write("character\tlevel\n")
        for c in sorted(writing):
            fh.write("%s\t%d\n" % (c, writing[c]))

    # ---- validate against the counts the syllabus itself advertises ----
    counts = {}
    for level in entries:
        counts[level] = counts.get(level, 0) + 1
    char_counts = {}
    for lvl in chars.values():
        char_counts[lvl] = char_counts.get(lvl, 0) + 1

    OFFICIAL = {1: 300, 2: 200, 3: 500, 4: 1000, 5: 1600, 6: 1800, BAND: 5600}
    print("VOCABULARY  %d entries, %d distinct words" % (len(entries), len(words)))
    print("  level  entries  official  ok")
    ok = True
    cum = 0
    for lvl in (1, 2, 3, 4, 5, 6, BAND):
        got, want = counts.get(lvl, 0), OFFICIAL[lvl]
        cum += got
        flag = "yes" if got == want else "NO"
        if got != want:
            ok = False
        print("  %-6s %6d  %8d  %s   (cumulative %d)"
              % ("7-9" if lvl == BAND else lvl, got, want, flag, cum))
    print("  %d entries collapse into %d distinct words (%d homograph rows)"
          % (len(entries), len(words), len(entries) - len(words)))
    if dupes:
        print("  %d words graded at more than one level; kept the lower: %s"
              % (len(dupes), ", ".join(d[0] for d in dupes[:8])))
    print("\nRECOGNITION CHARACTERS (认读字)  %d" % len(chars))
    for lvl in (1, 2, 3, 4, 5, 6, BAND):
        print("  %-6s %5d" % ("7-9" if lvl == BAND else lvl, char_counts.get(lvl, 0)))

    wcounts = {}
    for lvl in writing.values():
        wcounts[lvl] = wcounts.get(lvl, 0) + 1
    print("\nWRITING CHARACTERS (书写字)  %d" % len(writing))
    for lvl in (1, 2, 3, 4, 5, 6, BAND):
        if wcounts.get(lvl):
            print("  %-6s %5d" % ("7-9" if lvl == BAND else lvl, wcounts[lvl]))
    overlap = sum(1 for c in writing if c in chars)
    print("  %d of %d also appear in the recognition list" % (overlap, len(writing)))
    only_write = [c for c in writing if c not in chars]
    if only_write:
        print("  %d writable but NOT in the recognition list: %s"
              % (len(only_write), "".join(sorted(only_write))[:40]))
    print("\nwrote %s" % os.path.relpath(args.out))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
