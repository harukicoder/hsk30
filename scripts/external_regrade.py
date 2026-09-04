#!/usr/bin/env python3
"""Does the regrading result hold on text the author did not write?

The paper's headline figure -- 48% of texts change level depending on which
"HSK 3.0" document is used -- is measured on a 102-text corpus the author
authored. That is a fair objection, and this answers it directly: the same
comparison, run over human-authored, permissively licensed text from two
genres the author had no hand in.

    python3 scripts/external_regrade.py --texts external.jsonl [--json]

Each input line is {"source", "title", "text"}.

Two differences from the corpus run, both stated rather than hidden:

  * No proper-noun exclusion. The corpus carries per-token pinyin, so names can
    be detected by their capitalisation; external text has none. Proper nouns
    therefore count toward difficulty here, which inflates absolute levels --
    encyclopedic text is dense with names. It does not bias the comparison,
    because both gradings treat them identically and the document remains the
    only variable.

  * Different genre. These are encyclopedia and news prose, not graded readers
    written to a level target. If the effect survives that, it is not a
    property of pedagogical text either.
"""
import argparse
import collections
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import hsk30  # noqa: E402

LEVELS = list(range(1, 10))


def grade_both(text):
    a = hsk30.grade(text, standard="2021").level
    b = hsk30.grade(text, standard="2025").level
    return a, b


def report(rows, label):
    """Texts one document cannot grade at all are reported separately.

    A text that is off-scale under one document and level 7 under the other has
    not "changed level" in the sense the paper measures; it has saturated. Rolling
    the two together inflates the disagreement rate, so they are kept apart.
    """
    pairs = []
    for r in rows:
        if len(hsk30.hanzi(r["text"])) < 50:      # too short to grade meaningfully
            continue
        pairs.append(grade_both(r["text"]))
    n = len(pairs)
    if not n:
        return None
    both = [(a, b) for a, b in pairs if a is not None and b is not None]
    saturated = n - len(both)
    changed = [(a, b) for a, b in both if a != b]

    by_level = {}
    for lvl in LEVELS:
        at = [(a, b) for a, b in both if a == lvl]
        if at:
            by_level[str(lvl)] = {
                "n": len(at),
                "changed": sum(1 for a, b in at if a != b),
                "pct": round(100.0 * sum(1 for a, b in at if a != b) / len(at), 1),
            }
    return {
        "set": label, "texts": n,
        "gradeable_by_both": len(both),
        "saturated": saturated,
        "changed": len(changed),
        "changed_pct": round(100.0 * len(changed) / len(both), 1) if both else None,
        "harder_under_2025": sum(1 for a, b in changed if b > a),
        "easier_under_2025": sum(1 for a, b in changed if b < a),
        "by_2021_level": by_level,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--texts", required=True, help="JSONL of external texts")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    rows = [json.loads(l) for l in open(args.texts, encoding="utf-8") if l.strip()]
    by_source = collections.defaultdict(list)
    for r in rows:
        by_source[r.get("source", "unknown")].append(r)

    results = [report(rows, "all external")]
    for src in sorted(by_source):
        results.append(report(by_source[src], src))
    results = [r for r in results if r]

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    for r in results:
        print("\n%-24s %d texts, %d gradeable by both, %d saturated"
              % (r["set"], r["texts"], r["gradeable_by_both"], r["saturated"]))
        print("  level changes:   %4d / %d  (%.1f%%)"
              % (r["changed"], r["gradeable_by_both"], r["changed_pct"]))
        print("  harder / easier: %4d / %d"
              % (r["harder_under_2025"], r["easier_under_2025"]))
        if r["set"] == "all external" and r["by_2021_level"]:
            print("  by level graded under the 2021 standard:")
            for lvl, d in sorted(r["by_2021_level"].items(), key=lambda x: int(x[0])):
                print("    HSK %-2s  n=%-4d changed %-4d %5.1f%%"
                      % (lvl, d["n"], d["changed"], d["pct"]))
    print("\nProper nouns are counted here (no pinyin available), which raises")
    print("absolute levels but leaves the document as the only variable.")


if __name__ == "__main__":
    main()
