#!/usr/bin/env python3
"""Do the mainland and Taiwan Chinese standards agree on what is hard?

Everything published comparing the two ecosystems is exam-choice advice: level
equivalency tables and vocabulary counts. This runs the comparison the paper
runs within the PRC, across the strait instead -- word by word and character by
character, level by level.

    python3 scripts/crossstrait.py --tbcl tbcl.json [--json]

`tbcl.json` comes from scripts/tbcl_extract.py. Neither Taiwan list is
redistributed here; NAER asserts rights over them.

Three things make the comparison awkward, and each is handled explicitly.

**Script.** TBCL is traditional, HSK simplified, so TBCL is converted with
OpenCC before matching. Conversion is many-to-one, so some traditional
distinctions collapse; the count of collapsed entries is reported rather than
hidden.

**Variants.** TBCL writes alternates with a slash -- 爸爸/爸, 姊姊/姐姐/姊/姐 --
in 365 entries. Each variant is matched separately and the entry counts once,
at its own level.

**Scales.** TBCL has seven levels. The PRC standards have nine, but grade 7, 8
and 9 as a single undifferentiated band, so they have seven distinct tiers too.
Tier 7 on both sides therefore means "the top band", and levels 1-6 line up
one to one. That correspondence is an assumption of this comparison, not a
finding, and no issuing body endorses it.

That assumption is load-bearing, so the script tests it. TBCL levels 1 and 2
sit below CEFR A1 while the PRC scale has no sub-A1 tier, so the scales may be
offset, and an offset would manufacture a direction. Shifting TBCL by one level
reverses which side grades harder. **The disagreement rate survives every shift
tested; the direction does not, and must not be reported as a finding.**
"""
import argparse
import collections
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import hsk30  # noqa: E402

DEFAULT_OPENCC = os.path.expanduser(
    "~/Documents Mac/Chinese/GITHUB_Chinese_Books/data/opencc.js")


def opencc(path):
    src = open(path, encoding="utf-8").read()
    body = src[src.index("window.OPENCC=") + len("window.OPENCC="):].rstrip().rstrip(";")
    d = json.loads(body)
    return d["t2sC"], d["t2sP"]


def to_simplified(word, t2sC, t2sP):
    return t2sP.get(word) or "".join(t2sC.get(c, c) for c in word)


def tier(level):
    """PRC levels 7-9 are one undifferentiated band; TBCL tops out at 7."""
    return 7 if level >= 7 else level


def load_tbcl(path, t2sC, t2sP):
    data = json.load(open(path, encoding="utf-8"))
    words, chars, collapsed = {}, {}, 0
    seen = set()
    for row in data["words"]:
        for variant in row["item"].split("/"):
            s = to_simplified(variant.strip(), t2sC, t2sP)
            if not s:
                continue
            if s in seen and s in words and words[s] != row["level"]:
                collapsed += 1
            seen.add(s)
            words.setdefault(s, row["level"])
    for row in data["characters"]:
        s = to_simplified(row["item"], t2sC, t2sP)
        chars.setdefault(s, row["level"])
    return words, chars, collapsed


def compare(a, b, label_a, label_b):
    shared = set(a) & set(b)
    same = sum(1 for k in shared if tier(a[k]) == tier(b[k]))
    moved = len(shared) - same
    harder_b = sum(1 for k in shared if tier(b[k]) > tier(a[k]))
    return {
        "comparison": "%s vs %s" % (label_a, label_b),
        "only_%s" % label_a: len(set(a) - set(b)),
        "only_%s" % label_b: len(set(b) - set(a)),
        "shared": len(shared),
        "same_tier": same,
        "moved": moved,
        "moved_pct": round(100.0 * moved / len(shared), 1) if shared else None,
        "harder_in_%s" % label_b: harder_b,
        "harder_in_%s" % label_a: moved - harder_b,
    }


def sensitivity(tbcl_words, prc_words):
    """Does the result depend on how the two scales are lined up?

    TBCL levels 1 and 2 are below CEFR A1 and the PRC scale has no sub-A1 tier,
    so the scales may be offset by a level. If they are, a naive 1:1 alignment
    invents a direction. This shifts one scale against the other and reports
    what changes.
    """
    shared = set(tbcl_words) & set(prc_words)
    print("\nSensitivity to the alignment assumption (words, n=%d shared)" % len(shared))
    print("  %-22s %8s %11s %11s" % ("alignment", "differ", "PRC harder", "TBCL harder"))
    for shift, label in ((0, "1:1 (as reported)"), (1, "TBCL -1 level"),
                         (2, "TBCL -2 levels"), (-1, "TBCL +1 level")):
        diff = hp = ht = 0
        for k in shared:
            a = tier(min(7, max(1, tbcl_words[k] - shift)))
            b = tier(prc_words[k])
            if a != b:
                diff += 1
                hp, ht = (hp + 1, ht) if b > a else (hp, ht + 1)
        print("  %-22s %7.1f%% %11d %11d"
              % (label, 100.0 * diff / len(shared), hp, ht))
    print("  The rate stays high under every alignment. The direction flips,")
    print("  so which ecosystem grades harder is an artifact of the assumption.")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tbcl", required=True)
    ap.add_argument("--opencc", default=DEFAULT_OPENCC)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    t2sC, t2sP = opencc(args.opencc)
    tw_words, tw_chars, collapsed = load_tbcl(args.tbcl, t2sC, t2sP)

    sets = {
        "TBCL": (tw_words, tw_chars),
        "PRC2021": (hsk30.words("2021"), hsk30.characters("2021")),
        "PRC2025": (hsk30.words("2025"), hsk30.characters("2025")),
    }

    results = []
    for a, b in (("TBCL", "PRC2021"), ("TBCL", "PRC2025"), ("PRC2021", "PRC2025")):
        results.append({"unit": "words", **compare(sets[a][0], sets[b][0], a, b)})
        results.append({"unit": "characters", **compare(sets[a][1], sets[b][1], a, b)})

    if args.json:
        print(json.dumps({"collapsed_by_conversion": collapsed,
                          "results": results}, ensure_ascii=False, indent=2))
        return

    print("Inventory sizes after conversion to simplified")
    for name, (w, c) in sets.items():
        print("  %-9s %6d words   %5d characters" % (name, len(w), len(c)))
    print("  %d traditional entries collapsed onto an existing simplified form"
          % collapsed)

    for r in results:
        print("\n%s  (%s)" % (r["comparison"], r["unit"]))
        print("  shared             %6d" % r["shared"])
        print("  same tier          %6d" % r["same_tier"])
        print("  graded differently %6d  (%.1f%%)" % (r["moved"], r["moved_pct"]))
        hb = [k for k in r if k.startswith("harder_in_")]
        for k in hb:
            print("    %-22s %5d" % (k.replace("harder_in_", "harder in "), r[k]))

    sensitivity(tw_words, sets["PRC2025"][0])
    print("\nTier 7 means the top band on both sides. Levels 1-6 are assumed to")
    print("correspond one to one; no issuing body endorses that assumption.")


if __name__ == "__main__":
    main()
