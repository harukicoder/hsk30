#!/usr/bin/env python3
"""Identify which HSK standard a black-box tool implements, from its own output.

    python3 scripts/standard_fingerprint.py --probe          # the probe set
    python3 scripts/standard_fingerprint.py --probe --paste  # just the words
    python3 scripts/standard_fingerprint.py --identify 1,2,1,1,2,3,1,2,1,1,2,1

Three documents are in circulation and tools rarely say which they use:

  HSK 2.0     the 2012 examination syllabus, 4,991 words, superseded
  GF0025-2021 the national grading standard, in force since July 2021
  2025        the examination syllabus, in force since July 2026

A learner reading a tool's "HSK 4" cannot tell which of the three produced it,
and the answer changes real decisions. This script builds the smallest set of
probe words that tells them apart, and matches an observed answer back to a
standard.

**How it works.** 531 short words are assigned a different level by each of the
three documents. Ask a tool for a dozen of them and its answers form a
fingerprint. Compare that fingerprint to what each document says and the closest
match identifies the implementation — with a margin, so "no standard fits" is a
reportable answer rather than a forced choice.

**What it cannot tell you.** A tool may apply a standard correctly and still
differ from this script on a whole *text*, because text grading also involves a
coverage threshold, proper-noun handling and segmentation. This identifies the
*word list*, which is the part that is supposed to be fixed by a published
document. That is the narrower and more defensible claim.
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import hsk30  # noqa: E402

STANDARDS = ("2.0", "2021", "2025")
NAMES = {
    "2.0": "HSK 2.0 (2012 syllabus, superseded)",
    "2021": "GF0025-2021 (national grading standard)",
    "2025": "2025 examination syllabus (in force since July 2026)",
}


def table():
    """Every word, with its level under each of the three documents."""
    lists = {s: hsk30.words(s) for s in STANDARDS}
    keys = set()
    for d in lists.values():
        keys |= set(d)
    return {w: tuple(lists[s].get(w) for s in STANDARDS) for w in keys}


def candidates(rows, max_len=2):
    """Words present in all three documents, at three distinct levels.

    Restricted to one and two-character words, because a probe has to survive
    the tool's own segmentation. A four-character idiom that a tool splits into
    two words returns two levels and tells us nothing.
    """
    out = []
    for w, lv in rows.items():
        if len(w) > max_len or any(v is None for v in lv):
            continue
        if len(set(lv)) == 3:
            out.append((w, lv))
    return out


def choose(cands, n):
    """Greedy: take the word that best separates the standards still confusable.

    Selection maximises, in order: how far apart the three levels are; how low
    the lowest of them is; and brevity. Spread matters because a one-level
    difference is what a tool's own rounding could produce, while a three-level
    difference is not. A low minimum matters because a probe graded HSK 6 by
    every document is invisible to a beginner-oriented tool that only covers
    levels 1 to 3.
    """
    scored = sorted(
        cands,
        key=lambda t: (-(max(t[1]) - min(t[1])), min(t[1]), len(t[0]), t[0]),
    )
    picked, seen = [], set()
    for w, lv in scored:
        if lv in seen:            # a fingerprint column already covered
            continue
        picked.append((w, lv))
        seen.add(lv)
        if len(picked) >= n:
            break
    return picked


def print_probe(probe, paste):
    if paste:
        print(" ".join(w for w, _ in probe))
        return

    print("HSK standard fingerprint — %d probe words" % len(probe))
    print()
    print("Ask the tool for the level of each word below, in this order, then run")
    print("  python3 scripts/standard_fingerprint.py --identify <levels, comma separated>")
    print()
    print("  %-3s %-6s %-9s %-13s %-9s" % ("#", "word", "HSK 2.0", "GF0025-2021", "2025"))
    print("  " + "-" * 46)
    for i, (w, lv) in enumerate(probe, 1):
        print("  %-3d %-5s %-9s %-13s %-9s" % (i, w, lv[0], lv[1], lv[2]))
    print()
    print("Paste-ready:  " + " ".join(w for w, _ in probe))
    print()
    print("If the tool reports no level for a word, enter 0 for that position.")


def identify(probe, observed):
    if len(observed) != len(probe):
        raise SystemExit("expected %d levels, got %d" % (len(probe), len(observed)))

    scores = {}
    for i, s in enumerate(STANDARDS):
        expected = [lv[i] for _, lv in probe]
        hits = sum(1 for e, o in zip(expected, observed) if o == e)
        scores[s] = hits

    ranked = sorted(scores.items(), key=lambda kv: -kv[1])
    best, best_hits = ranked[0]
    second, second_hits = ranked[1]
    n = len(probe)

    print("Observed fingerprint: %s" % ",".join(str(o) for o in observed))
    print()
    print("  %-52s %s" % ("Standard", "matches"))
    print("  " + "-" * 62)
    for s, h in ranked:
        bar = "#" * h
        print("  %-52s %2d/%-2d %s" % (NAMES[s], h, n, bar))
    print()

    if best_hits <= n // 2:
        print("VERDICT: no standard fits.")
        print()
        print("The best match agrees on only %d of %d probes, which is close to what" % (best_hits, n))
        print("chance would give. The tool is most likely applying a list of its own —")
        print("a vendor-internal levelling, or a merge of several sources. That is a")
        print("legitimate thing to do and an illegitimate thing to leave unstated,")
        print("because a user reading \"HSK 4\" will assume one of the three documents.")
        return

    if best_hits == second_hits:
        print("VERDICT: ambiguous between %s and %s (%d/%d each)."
              % (best, second, best_hits, n))
        print("Run more probes: --probe -n 24")
        return

    conf = 100.0 * best_hits / n
    print("VERDICT: %s" % NAMES[best])
    print("  agrees on %d of %d probes (%.0f%%), next best %s at %d."
          % (best_hits, n, conf, second, second_hits))
    print()
    if best == "2.0":
        print("Note: HSK 2.0 was superseded in 2021 and again in 2025. A tool on this")
        print("list is grading against a syllabus no current examination uses.")
    elif best == "2021":
        print("Note: GF0025-2021 is the national *grading standard*, not the")
        print("examination syllabus. Learners sitting the HSK from July 2026 are")
        print("examined against the 2025 document, which assigns a different level to")
        print("41.5% of the vocabulary the two share.")
    else:
        print("Note: this is the current examination syllabus. It differs from the")
        print("2021 national standard on 41.5% of shared vocabulary, so a tool on this")
        print("list will disagree with one on GF0025-2021 about roughly half of texts.")


def summarise(rows):
    """How much room there is to tell the documents apart, stated once."""
    lists = {s: hsk30.words(s) for s in STANDARDS}
    print("Vocabulary of the three documents")
    print()
    for s in STANDARDS:
        print("  %-52s %6d words" % (NAMES[s], len(lists[s])))
    print()
    both = set(lists["2021"]) & set(lists["2025"])
    differ = sum(1 for w in both if lists["2021"][w] != lists["2025"][w])
    print("  2021 and 2025 share %d words and disagree about %d of them (%.1f%%)."
          % (len(both), differ, 100.0 * differ / len(both)))
    only21 = set(lists["2021"]) - set(lists["2025"])
    only25 = set(lists["2025"]) - set(lists["2021"])
    print("  %d words are in the 2021 standard only; %d in the 2025 syllabus only."
          % (len(only21), len(only25)))
    c = candidates(rows)
    print("  %d short words are assigned three *different* levels by the three"
          % len(c))
    print("  documents, which is what makes a short probe possible.")


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--probe", action="store_true", help="print the probe set")
    ap.add_argument("--paste", action="store_true",
                    help="with --probe, print only the words on one line")
    ap.add_argument("--identify", metavar="LEVELS",
                    help="comma-separated levels the tool reported, 0 for none")
    ap.add_argument("-n", type=int, default=12, help="probe size (default 12)")
    ap.add_argument("--summary", action="store_true",
                    help="how far apart the three documents are")
    args = ap.parse_args()

    rows = table()
    probe = choose(candidates(rows), args.n)

    if args.summary:
        summarise(rows)
        return 0
    if args.identify:
        identify(probe, [int(x) for x in args.identify.replace(" ", "").split(",")])
        return 0
    if args.probe or True:
        print_probe(probe, args.paste)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
