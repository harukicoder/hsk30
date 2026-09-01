#!/usr/bin/env python3
"""Regenerate the shipped HSK tables from their upstream sources.

    python3 scripts/gen_data.py            # fetch and write src/hsk30/data/*.tsv
    python3 scripts/gen_data.py --check    # verify the shipped files still match

Needs network access.  Both sources are MIT-licensed transcriptions of
《国际中文教育中文水平等级标准》 (GF0025-2021), the national grading standard in
force since 1 July 2021 — NOT the November 2025 HSK exam syllabus, which is a
separate document with different lists.

Two rules encoded here that are easy to get wrong:

* **Levels 7-9 are one band.**  The standard does not split them.  They are
  stored as level 7 and always rendered "7-9".
* **A word graded at two levels keeps the lower one** — that is the level at
  which a learner is first expected to know it.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sys
import urllib.request

SRC_WORDS_30 = "https://raw.githubusercontent.com/ivankra/hsk30/master/hsk30.csv"
SRC_CHARS_30 = "https://raw.githubusercontent.com/ivankra/hsk30/master/hsk30-chars.csv"
SRC_VOCAB = ("https://raw.githubusercontent.com/drkameleon/"
             "complete-hsk-vocabulary/main/complete.min.json")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "src", "hsk30", "data")
BAND = 7


def fetch(url: str) -> str:
    with urllib.request.urlopen(url, timeout=180) as response:
        return response.read().decode("utf-8")


def is_han(text: str) -> bool:
    # The word list carries a few latin-letter entries (CD, T恤) that could
    # never match a character-level lookup anyway.
    return bool(text) and all("一" <= ch <= "鿿" for ch in text)


def hsk30_words():
    levels = {}
    for row in csv.DictReader(io.StringIO(fetch(SRC_WORDS_30))):
        word = (row.get("Simplified") or "").strip()
        raw = (row.get("Level") or "").strip()
        if not word or not raw or not is_han(word):
            continue
        level = BAND if raw.startswith("7") else int(raw)
        if word not in levels or level < levels[word]:
            levels[word] = level
    return levels


def hsk30_chars():
    levels = {}
    for row in csv.DictReader(io.StringIO(fetch(SRC_CHARS_30))):
        hz = (row.get("Hanzi") or "").strip()
        raw = (row.get("Level") or "").strip()
        if not hz or not raw or not is_han(hz):
            continue
        levels[hz] = BAND if raw.startswith("7") else int(raw)
    return levels


def hsk20_words():
    levels = {}
    for entry in json.loads(fetch(SRC_VOCAB)):
        word = (entry.get("s") or "").strip()
        if not is_han(word):
            continue
        old = [l for l in (entry.get("l") or []) if l.startswith("o")]
        if not old:
            continue
        try:
            level = int(old[0][1:])
        except ValueError:
            continue
        if 1 <= level <= 6:
            levels[word] = level
    return levels


def render(table, key_header: str) -> str:
    rows = "\n".join("%s\t%d" % (k, table[k]) for k in sorted(table))
    return "%s\tlevel\n%s\n" % (key_header, rows)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="compare against the shipped files instead of writing")
    args = ap.parse_args()

    outputs = {
        "hsk30_chars.tsv": (render(hsk30_chars(), "character"), 3000),
        "hsk30_words.tsv": (render(hsk30_words(), "word"), 10916),
        "hsk20_words.tsv": (render(hsk20_words(), "word"), 4991),
    }

    failed = False
    for name, (content, expected) in outputs.items():
        path = os.path.join(DATA, name)
        count = content.count("\n") - 1
        if count != expected:
            print("warning: %s has %d rows, expected %d" % (name, count, expected))
        if args.check:
            with open(path, encoding="utf-8") as fh:
                current = fh.read()
            status = "ok" if current == content else "DIFFERS"
            if current != content:
                failed = True
            print("  %-18s %s (%d rows)" % (name, status, count))
        else:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(content)
            print("  wrote %-18s %d rows" % (name, count))

    if args.check and failed:
        print("\nShipped data differs from upstream. Rerun without --check to update.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
