#!/usr/bin/env python3
"""Recompute every figure quoted in the paper, from the shipped data.

    python3 scripts/reproduce.py            # human-readable
    python3 scripts/reproduce.py --json     # machine-readable

Nothing in the paper is transcribed by hand.  An earlier draft of this work
quoted 4,490 / 817 / 501 / 6,479 for the migration counts; the true figures are
4,482 / 814 / 509 / 6,434.  The numbers had been copied from a changelog
written against an earlier regeneration of the source lists and never rechecked.
This script exists so that cannot happen again.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

import hsk30
from hsk30 import BAND, LEVELS

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.join(HERE, "..", "corpus", "hsk30_graded_readers.jsonl")
SHELVES = ["newbie", "beginner", "intermediate", "upper", "advanced", "native"]


def load_corpus():
    with open(CORPUS, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def compare(a_name, b_name):
    """Level agreement between any two of the three documents."""
    a, b = hsk30.words(a_name), hsk30.words(b_name)
    both = [w for w in a if w in b]
    same = [w for w in both if a[w] == b[w]]
    return {
        "a": a_name, "b": b_name,
        "a_total": len(a), "b_total": len(b),
        "shared": len(both),
        "same_level": len(same),
        "moved": len(both) - len(same),
        "moved_pct": round(100.0 * (len(both) - len(same)) / len(both), 1),
        "only_a": len(a) - len(both),
        "only_b": len(b) - len(both),
    }


def compare_characters():
    """The two 'HSK 3.0' documents grade different character inventories."""
    a, b = hsk30.characters("2021"), hsk30.characters("2025")
    both = [c for c in a if c in b]
    same = [c for c in both if a[c] == b[c]]
    return {
        "chars_2021": len(a), "chars_2025": len(b),
        "shared": len(both), "same_level": len(same),
        "moved": len(both) - len(same),
        "moved_pct": round(100.0 * (len(both) - len(same)) / len(both), 1),
        "only_2021": len(a) - len(both), "only_2025": len(b) - len(both),
        "by_level_2025": {str(l): sum(1 for v in b.values() if v == l) for l in LEVELS},
    }


def regrade(rows):
    """Does the choice of document change how real texts grade?  It does."""
    shifts, changed = Counter(), []
    for r in rows:
        toks = [w for s in r["sentences"] for w in s["words"]]
        a = hsk30.grade_tokens(toks, standard="2021")
        b = hsk30.grade_tokens(toks, standard="2025")
        ka = BAND + 1 if a.level is None else a.level
        kb = BAND + 1 if b.level is None else b.level
        shifts[kb - ka] += 1
        if a.level != b.level:
            changed.append({"id": r["id"], "shelf": r["shelf"],
                            "std2021": a.label, "syl2025": b.label})
    n = len(rows)
    return {
        "texts": n,
        "unchanged": shifts[0],
        "changed": n - shifts[0],
        "changed_pct": round(100.0 * (n - shifts[0]) / n, 1),
        "harder": sum(v for k, v in shifts.items() if k > 0),
        "easier": sum(v for k, v in shifts.items() if k < 0),
        "shift_distribution": dict(sorted(shifts.items())),
        "examples": changed[:10],
        "shelf_medians": {
            shelf: {
                std: hsk30.label(hsk30.profile_shelf([
                    hsk30.grade_tokens(
                        [w for s in r["sentences"] for w in s["words"]], standard=std)
                    for r in rows if r["shelf"] == shelf]).median)
                for std in ("2021", "2025")
            } for shelf in SHELVES
        },
    }


HELDOUT = os.path.join(HERE, "..", "corpus", "hsk30_heldout.jsonl")


def robustness(rows):
    """Is the regrading result an artefact of the 95% threshold, or of this corpus?

    Neither. It survives every threshold from 0.80 to 1.00 and replicates on a
    disjoint set of texts that played no part in establishing it.
    """
    def changed(items, threshold):
        n = h = e = 0
        for r in items:
            toks = [w for s in r["sentences"] for w in s["words"]]
            a = hsk30.grade_tokens(toks, threshold=threshold, standard="2021").level
            b = hsk30.grade_tokens(toks, threshold=threshold, standard="2025").level
            if a == b:
                continue
            n += 1
            ka = BAND + 1 if a is None else a
            kb = BAND + 1 if b is None else b
            if kb > ka:
                h += 1
            else:
                e += 1
        return {"changed": n, "pct": round(100.0 * n / len(items), 1),
                "harder": h, "easier": e}

    sweep = {("%.2f" % t): changed(rows, t)
             for t in (0.80, 0.85, 0.90, 0.95, 0.98, 1.00)}

    held = None
    if os.path.exists(HELDOUT):
        with open(HELDOUT, encoding="utf-8") as fh:
            items = [json.loads(line) for line in fh if line.strip()]
        main_ids = {r["id"] for r in rows}
        assert not (main_ids & {r["id"] for r in items}), "held-out set is not disjoint"
        held = dict(changed(items, 0.95), n=len(items))
    return {"threshold_sweep": sweep, "heldout": held}


def migration():
    """How HSK 2.0 and the 2021 grading standard disagree."""
    old, new = hsk30.words("2.0"), hsk30.words("2021")
    both = [w for w in old if w in new]
    same = [w for w in both if old[w] == new[w]]
    moved = [w for w in both if old[w] != new[w]]

    matrix = defaultdict(Counter)
    for w in both:
        matrix[old[w]][new[w]] += 1

    harder = sum(1 for w in moved if new[w] > old[w])
    easier = sum(1 for w in moved if new[w] < old[w])
    to_band = sum(1 for w in moved if new[w] == BAND)

    return {
        "hsk20_total": len(old),
        "hsk30_total": len(new),
        "graded_by_both": len(both),
        "same_level": len(same),
        "moved": len(moved),
        "moved_pct": round(100.0 * len(moved) / len(both), 1),
        "dropped": len(old) - len(both),
        "added": len(new) - len(both),
        "moved_harder": harder,
        "moved_easier": easier,
        "moved_into_band": to_band,
        "hsk30_by_level": {str(l): sum(1 for v in new.values() if v == l) for l in LEVELS},
        "hsk20_by_level": {str(l): sum(1 for v in old.values() if v == l) for l in range(1, 7)},
        "matrix": {str(o): {str(n): c for n, c in sorted(row.items())}
                   for o, row in sorted(matrix.items())},
    }


def characters_summary():
    chars = hsk30.characters("2021")
    by_level = Counter(chars.values())
    return {
        "total": len(chars),
        "by_level": {str(l): by_level[l] for l in LEVELS},
    }


def derived_vs_official():
    """Why the official character list is shipped instead of a derived one.

    Deriving a character's level from the lowest-level word containing it is
    the obvious shortcut.  It is nearly right, and wrong in a way that matters:
    the characters it misgrades are the commonest words in a beginner's life.
    """
    chars, words = hsk30.characters("2021"), hsk30.words("2021")
    derived = {}
    for word, level in words.items():
        for ch in word:
            if ch in chars and (ch not in derived or level < derived[ch]):
                derived[ch] = level
    shared = [c for c in derived if c in chars]
    agree = [c for c in shared if derived[c] == chars[c]]
    disagree = sorted(c for c in shared if derived[c] != chars[c])
    return {
        "characters_derivable": len(shared),
        "agree": len(agree),
        "disagree": len(disagree),
        "disagreements": [
            {"char": c, "official": chars[c], "derived": derived[c]} for c in disagree
        ],
    }


def corpus_summary(rows):
    shelves = {}
    for name in SHELVES:
        items = [r for r in rows if r["shelf"] == name]
        profiles = [
            hsk30.grade_tokens([w for s in r["sentences"] for w in s["words"]],
                               standard="2021")
            for r in items
        ]
        shelf = hsk30.profile_shelf(profiles)
        shelves[name] = {
            "n": shelf.n,
            "median": hsk30.label(shelf.median),
            "iqr": shelf.span_label,
            "pooled": hsk30.label(shelf.pooled),
            "easy_share": round(100 * shelf.easy_share, 1),
            "mean_chars": round(sum(p.chars for p in profiles) / len(profiles)),
        }
    all_profiles = [
        hsk30.grade_tokens([w for s in r["sentences"] for w in s["words"]],
                           standard="2021")
        for r in rows
    ]
    dist = Counter(hsk30.label(p.level) for p in all_profiles)
    return {
        "texts": len(rows),
        "sentences": sum(r["n_sentences"] for r in rows),
        "characters": sum(p.chars for p in all_profiles),
        "tokens": sum(len(s["words"]) for r in rows for s in r["sentences"]),
        "shelves": shelves,
        "label_distribution": dict(sorted(dist.items())),
    }


def port_fidelity(rows):
    """The Python library against the original JavaScript, text by text."""
    path = os.path.join(HERE, "..", "corpus", "reference_grades.json")
    if not os.path.exists(path):
        return {"available": False}
    with open(path, encoding="utf-8") as fh:
        ref = json.load(fh)
    legacy_mismatch, fix_changes = [], []
    for r in rows:
        toks = [w for s in r["sentences"] for w in s["words"]]
        legacy = hsk30.grade_tokens(
            toks, detector=hsk30.is_proper_noun_ascii, standard="2021")
        if legacy.level != ref[r["id"]]["level"] or legacy.chars != ref[r["id"]]["chars"]:
            legacy_mismatch.append(r["id"])
        fixed = hsk30.grade_tokens(toks, standard="2021")
        if fixed.level != legacy.level:
            fix_changes.append(
                {"id": r["id"], "before": hsk30.label(legacy.level),
                 "after": hsk30.label(fixed.level)}
            )
    return {
        "available": True,
        "texts": len(rows),
        "legacy_mismatches": legacy_mismatch,
        "accent_fix_changes": fix_changes,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args()

    rows = load_corpus()
    report = {
        "version": hsk30.__version__,
        "characters": characters_summary(),
        "migration": migration(),
        "standards": {
            "hsk20_vs_2021": compare("2.0", "2021"),
            "hsk20_vs_2025": compare("2.0", "2025"),
            "std2021_vs_syl2025": compare("2021", "2025"),
            "characters": compare_characters(),
        },
        "regrade": regrade(rows),
        "robustness": robustness(rows),
        "derived_vs_official": derived_vs_official(),
        "corpus": corpus_summary(rows),
        "port_fidelity": port_fidelity(rows),
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return

    st = report["standards"]
    print("WHICH DOCUMENT?  level agreement between the three")
    print("  comparison                       shared   same    moved")
    for key, lab in [("hsk20_vs_2021", "HSK 2.0  vs  GF0025-2021"),
                     ("hsk20_vs_2025", "HSK 2.0  vs  2025 syllabus"),
                     ("std2021_vs_syl2025", "GF0025-2021 vs 2025 syllabus")]:
        c_ = st[key]
        print("  %-32s %6d %6d  %5d (%.1f%%)"
              % (lab, c_["shared"], c_["same_level"], c_["moved"], c_["moved_pct"]))
    ch = st["characters"]
    print("  characters 2021 (%d) vs 2025 (%d): shared %d, same level %d, moved %d (%.1f%%)"
          % (ch["chars_2021"], ch["chars_2025"], ch["shared"], ch["same_level"],
             ch["moved"], ch["moved_pct"]))
    print()
    rg = report["regrade"]
    print("DOES IT CHANGE REAL GRADING?  %d texts, 2021 standard -> 2025 syllabus"
          % rg["texts"])
    print("  unchanged %d   changed %d (%.1f%%)   harder %d   easier %d"
          % (rg["unchanged"], rg["changed"], rg["changed_pct"],
             rg["harder"], rg["easier"]))
    print("  shelf medians:")
    for shelf, m_ in rg["shelf_medians"].items():
        flag = "" if m_["2021"] == m_["2025"] else "   <- shifts"
        print("    %-13s 2021 HSK %-4s  2025 HSK %-4s%s"
              % (shelf, m_["2021"], m_["2025"], flag))
    print()

    rb = report["robustness"]
    print("ROBUSTNESS")
    print("  threshold  changed  harder  easier")
    for th, v in rb["threshold_sweep"].items():
        mark = "   <- reported" if th == "0.95" else ""
        print("    %s     %3d (%.1f%%)  %3d    %3d%s"
              % (th, v["changed"], v["pct"], v["harder"], v["easier"], mark))
    if rb["heldout"]:
        h = rb["heldout"]
        print("  held-out replication (%d disjoint texts, 0.95): %d changed (%.1f%%), "
              "harder %d, easier %d" % (h["n"], h["changed"], h["pct"],
                                        h["harder"], h["easier"]))
    print()

    m, c, d = report["migration"], report["characters"], report["derived_vs_official"]
    print("CHARACTER STANDARD (GF0025-2021)")
    print("  %d graded characters: %s" % (
        c["total"], ", ".join("L%s=%d" % (k, v) for k, v in c["by_level"].items())))
    print()
    print("MIGRATION  HSK 2.0 -> 3.0")
    print("  HSK 2.0 list              %6d words" % m["hsk20_total"])
    print("  HSK 3.0 list              %6d words" % m["hsk30_total"])
    print("  graded by both            %6d" % m["graded_by_both"])
    print("    kept their level        %6d" % m["same_level"])
    print("    moved                   %6d  (%.1f%%)" % (m["moved"], m["moved_pct"]))
    print("      harder / easier       %6d / %d" % (m["moved_harder"], m["moved_easier"]))
    print("      into the 7-9 band     %6d" % m["moved_into_band"])
    print("  dropped from 3.0          %6d" % m["dropped"])
    print("  new in 3.0                %6d" % m["added"])
    print()
    print("DERIVED CHARACTER LEVELS vs THE OFFICIAL LIST")
    print("  agree on %d of %d; %d disagree: %s" % (
        d["agree"], d["characters_derivable"], d["disagree"],
        " ".join("%s(official %d, derived %d)" % (x["char"], x["official"], x["derived"])
                 for x in d["disagreements"])))
    print()
    co = report["corpus"]
    print("CORPUS  %d texts, %d sentences, %d tokens, %d graded characters"
          % (co["texts"], co["sentences"], co["tokens"], co["characters"]))
    print("  shelf         n  median  IQR            pooled  HSK1-2%  mean chars")
    for name in SHELVES:
        s = co["shelves"][name]
        print("  %-12s %2d  %6s  %-14s %6s  %6.1f  %10d"
              % (name, s["n"], s["median"], s["iqr"], s["pooled"],
                 s["easy_share"], s["mean_chars"]))
    print("  label distribution: %s" % co["label_distribution"])
    print()
    pf = report["port_fidelity"]
    if pf["available"]:
        print("PORT FIDELITY  (Python vs the original JavaScript, %d texts)" % pf["texts"])
        print("  legacy-mode mismatches: %d" % len(pf["legacy_mismatches"]))
        print("  texts changed by the accent-aware fix: %s" % (
            ", ".join("%s %s->%s" % (x["id"], x["before"], x["after"])
                      for x in pf["accent_fix_changes"]) or "none"))


if __name__ == "__main__":
    main()
