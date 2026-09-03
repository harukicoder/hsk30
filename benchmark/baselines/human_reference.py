#!/usr/bin/env python3
"""How often does text authored to an explicit level target actually hit it?

The 102 corpus texts were each written for a shelf with a nominal HSK band.
Scoring them the way WriteToLevel scores a model gives a reference point for
authored text — and it is not 100%.

This is NOT a human baseline, and must not be reported as one: the corpus was
drafted with LLM assistance and then edited to level by the author, as its
datasheet discloses. What it measures is an authoring loop with a human in it,
which still overshoots, most often at the easy end — the practical argument for
putting an objective grader in that loop.

    python3 benchmark/baselines/human_reference.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "src"))

import hsk30

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.join(HERE, "..", "..", "corpus", "hsk30_graded_readers.jsonl")

# The band each shelf advertises, which is also what its URL and heading claim.
SHELF_TARGET = {
    "newbie": 1, "beginner": 2, "intermediate": 3,
    "upper": 4, "advanced": 5, "native": 6,
}


def main() -> None:
    with open(CORPUS, encoding="utf-8") as fh:
        rows = [json.loads(line) for line in fh if line.strip()]

    print("shelf         n   target  hit   mean signed error")
    total_hit = 0
    all_errs = []
    for shelf, target in SHELF_TARGET.items():
        items = [r for r in rows if r["shelf"] == shelf]
        errs, hits = [], 0
        for r in items:
            toks = [w for s in r["sentences"] for w in s["words"]]
            lvl = hsk30.grade_tokens(toks).level
            measured = lvl if lvl is not None else hsk30.BAND + 1
            errs.append(measured - target)
            if lvl is not None and lvl <= target:
                hits += 1
        total_hit += hits
        all_errs.extend(errs)
        print("  %-11s %2d   HSK %d  %3d/%-2d  %+.2f"
              % (shelf, len(items), target, hits, len(items),
                 sum(errs) / len(errs)))
    print("\n  overall human level accuracy: %.1f%% (%d/%d)"
          % (100 * total_hit / len(rows), total_hit, len(rows)))
    print("  overall mean signed error:   %+.2f levels" % (sum(all_errs) / len(all_errs)))
    print("  overall mean absolute error: %.2f levels"
          % (sum(abs(e) for e in all_errs) / len(all_errs)))


if __name__ == "__main__":
    main()
