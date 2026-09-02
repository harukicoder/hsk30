"""Loaders for the graded word and character lists.

Five tables ship with the package, covering three different documents that are
routinely conflated as "HSK 3.0":

    hsk2025_chars.tsv          3,088 recognition hanzi ) 新版HSK考试大纲, the
    hsk2025_writing_chars.tsv  1,200 writing hanzi     ) EXAM syllabus, in
    hsk2025_words.tsv         10,896 graded words      ) force since Jul 2026
    hsk30_chars.tsv    3,000 graded hanzi      ) GF0025-2021, the national
    hsk30_words.tsv   10,916 graded words      ) grading standard (Jul 2021)
    hsk20_words.tsv    4,991 graded words        the superseded HSK 2.0 lists

**Two character dimensions.**  HSK 3.0 grades 认读字 (recognition — what a
learner must read) separately from 书写字 (what they must write by hand), and
the second is a strict subset of the first: all 1,200 writing characters appear
among the 3,088 recognition characters, on a different allocation curve (100
across levels 1-2, then 150 per level, 500 across 7-9).  Reading a text and
being able to write it are different questions; ``kind="writing"`` answers the
second.  Only the 2025 syllabus grades writing separately — the 2021 standard
does not.

**The choice is not cosmetic.**  The two "HSK 3.0" documents assign different
levels to 41.5% of the words they share and 40.7% of the characters, and
grading real texts against one rather than the other changes the level of
roughly half of them.  ``DEFAULT_STANDARD`` is the 2025 exam syllabus, because
that is the document in force; pass ``standard="2021"`` for the grading
standard.

HSK 3.0 grades characters separately from words, and the character list is the
one that grades a passage.  The 3,000 characters here are those of the 2021
grading standard (GF0025-2021); the November 2025 exam syllabus grades a
different set of roughly 3,079 recognition characters.  Deriving character levels from the word list
instead agrees on 2,962 of 2,969 shared characters but mis-grades the family
terms: 妈 哥 弟 妹 are level-1 characters whose only listed words (妈妈, 哥哥)
sit at level 4.  We ship the official character list rather than deriving it.
"""

from __future__ import annotations

import csv
import os
from functools import lru_cache
from typing import Dict

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

#: The document used when none is named: the examination syllabus in force.
DEFAULT_STANDARD = "2025"

#: Levels 7, 8 and 9 are a single undifferentiated list in the standard.  We
#: carry the band as 7 and always render it "7-9"; a vendor advertising an
#: "HSK 8 word list" invented the split.
BAND = 7

#: Grading order.  Note this is not ``range(1, 8)`` by accident — the band sits
#: at the end and is deliberately the last bucket coverage can fall into.
LEVELS = (1, 2, 3, 4, 5, 6, BAND)


def _load(filename: str) -> Dict[str, int]:
    with open(os.path.join(_DATA_DIR, filename), encoding="utf-8") as fh:
        reader = csv.reader(fh, delimiter="\t")
        next(reader, None)  # header
        return {row[0]: int(row[1]) for row in reader if len(row) >= 2}


#: Accepted spellings for each document.
_STANDARDS = {
    "2025": "2025", "syllabus": "2025", "exam": "2025",
    "2021": "2021", "3.0": "2021", "3": "2021", "standard": "2021",
    "2.0": "2.0", "2": "2.0",
}


def resolve(standard) -> str:
    """Normalise a standard name, or raise with the accepted spellings."""
    key = _STANDARDS.get(str(standard).lower())
    if key is None:
        raise ValueError(
            "unknown standard %r; expected one of: 2025 (the exam syllabus), "
            "2021 (the grading standard), 2.0 (superseded)" % (standard,))
    return key


@lru_cache(maxsize=None)
def characters(standard: str = DEFAULT_STANDARD,
               kind: str = "recognition") -> Dict[str, int]:
    """Graded character list — the table that grades a TEXT.

    ``kind="recognition"`` (认读字) is what gates *reading*: 3,088 characters
    under the 2025 syllabus, 3,000 under the 2021 standard.

    ``kind="writing"`` (书写字) is what gates *handwriting*: 1,200 characters,
    a strict subset of the recognition list.  Only the 2025 syllabus grades
    this separately; the 2021 standard does not, and asking for it raises.

    HSK 2.0 graded no characters separately at all.
    """
    key = resolve(standard)
    if kind not in ("recognition", "writing"):
        raise ValueError("kind must be 'recognition' or 'writing'")
    if key == "2.0":
        raise ValueError("HSK 2.0 has no separate character grading; "
                         "use standard='2025' or '2021'")
    if kind == "writing":
        if key != "2025":
            raise ValueError(
                "only the 2025 exam syllabus grades writing characters "
                "separately; the 2021 standard does not")
        return _load("hsk2025_writing_chars.tsv")
    return _load("hsk2025_chars.tsv" if key == "2025" else "hsk30_chars.tsv")


@lru_cache(maxsize=None)
def words(standard: str = DEFAULT_STANDARD) -> Dict[str, int]:
    """Graded word list for ``standard``: ``"2025"``, ``"2021"`` or ``"2.0"``."""
    return _load({
        "2025": "hsk2025_words.tsv",
        "2021": "hsk30_words.tsv",
        "2.0": "hsk20_words.tsv",
    }[resolve(standard)])


def label(level) -> str:
    """Render a level the way the standard does: ``3``, ``7-9``, or off-scale."""
    if level is None:
        return "beyond HSK 9"
    return "7-9" if level == BAND else str(level)
