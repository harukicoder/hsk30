#!/usr/bin/env python3
"""How stable is a Chinese text's CEFR band?

Chinese is normally placed on the CEFR through HSK. But "HSK 3.0" names two
official documents, and they disagree. This regrades the corpus against each
and reports how often the CEFR band moves as a result.

Two published correspondences are used. Neither is official -- China's own
standard declines to map itself to the CEFR -- so both are stated as
assumptions and every figure is reported under each. The result is meant to
survive the choice, not to depend on it.

    python3 scripts/cefr_mapping.py [--json]
"""
import argparse
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import hsk30  # noqa: E402

CORPUS = os.path.join(os.path.dirname(__file__), "..", "corpus")

# The 1:1 reading, ubiquitous in learner-facing material: HSK n -> the nth CEFR
# band. HSK 3.0 levels 7-9 are a single band, mapped to C2.
NAIVE = {1: "A1", 2: "A2", 3: "B1", 4: "B2", 5: "C1", 6: "C2",
         7: "C2", 8: "C2", 9: "C2"}

# The reading practitioners report: vocabulary coverage overstates
# communicative range, and HSK 6 lands nearer B2 than C2.
COMPRESSED = {1: "A1", 2: "A1", 3: "A2", 4: "B1", 5: "B2", 6: "B2",
              7: "C1", 8: "C1", 9: "C2"}

MAPPINGS = (("naive", NAIVE), ("compressed", COMPRESSED))
BANDS = ["A1", "A2", "B1", "B2", "C1", "C2"]


def load(name):
    with open(os.path.join(CORPUS, name), encoding="utf-8") as fh:
        return [json.loads(line) for line in fh]


def levels(rows):
    """Grade each text under both documents.

    Grades the corpus's own authored segmentation, as scripts/reproduce.py
    does. Passing raw strings instead re-tokenises and yields 52.9% rather
    than the published 48.0%; the two are not comparable.
    """
    out = []
    for r in rows:
        toks = [w for s in r["sentences"] for w in s["words"]]
        out.append((r["id"],
                    hsk30.grade_tokens(toks, standard="2021").level,
                    hsk30.grade_tokens(toks, standard="2025").level))
    return out


def analyse(rows, name):
    pairs = levels(rows)
    n = len(pairs)
    report = {"split": name, "texts": n,
              "hsk_level_changed": sum(1 for _, a, b in pairs if a != b)}
    report["hsk_level_changed_pct"] = round(100.0 * report["hsk_level_changed"] / n, 1)

    for label, m in MAPPINGS:
        moved = [(i, m.get(a), m.get(b)) for i, a, b in pairs if m.get(a) != m.get(b)]
        harder = sum(1 for _, a, b in moved
                     if a in BANDS and b in BANDS and BANDS.index(b) > BANDS.index(a))
        report[label] = {
            "changed": len(moved),
            "changed_pct": round(100.0 * len(moved) / n, 1),
            "harder_under_2025": harder,
            "easier_under_2025": len(moved) - harder,
            "band_2021": {b: sum(1 for _, a, _ in pairs if m.get(a) == b) for b in BANDS},
            "band_2025": {b: sum(1 for _, _, c in pairs if m.get(c) == b) for b in BANDS},
        }
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    report = [analyse(load("hsk30_graded_readers.jsonl"), "graded_readers"),
              analyse(load("hsk30_heldout.jsonl"), "held_out")]

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return

    for r in report:
        print("\n%s (n=%d)" % (r["split"], r["texts"]))
        print("  HSK level changes:            %3d  (%.1f%%)"
              % (r["hsk_level_changed"], r["hsk_level_changed_pct"]))
        for label, _ in MAPPINGS:
            d = r[label]
            print("  CEFR band changes, %-10s %3d  (%.1f%%)   harder %d / easier %d"
                  % (label + ":", d["changed"], d["changed_pct"],
                     d["harder_under_2025"], d["easier_under_2025"]))
    print("\nNeither mapping is official. The finding is that the band moves,")
    print("not where it moves to.")


if __name__ == "__main__":
    main()
