#!/usr/bin/env python3
"""Generate the minimal Traditional-to-Simplified table needed to grade.

    python3 scripts/gen_t2s.py --opencc path/to/opencc.js
    python3 scripts/gen_t2s.py --check

Writes ``src/hsk30/data/t2s.tsv``.

**Why a minimal table rather than all of OpenCC.** The library is
dependency-free and stays that way. A full conversion table is 4,148 character
mappings, most of which describe characters no HSK document grades; carrying
them would triple the data directory to answer questions this library does not
ask. We keep only the pairs whose *simplified* form appears in an inventory we
ship — 1,368 of them — because a traditional character whose simplified form is
outside the inventory is ungraded either way, and converting it changes nothing.

**What this table is not.** It is not a general Traditional-to-Simplified
converter and must not be used as one. It has no phrase table, so it cannot
resolve the cases where correct conversion depends on context, and it silently
leaves anything outside the inventory alone. For real conversion use OpenCC.

**The lossiness is the point to document, not to hide.** Conversion is
many-to-one: 乾, 幹 and 榦 all become 干. For coverage grading that is correct —
the inventory holds 干 and that is what a learner of the simplified system must
recognise — but it means a traditional reader facing three distinct characters
is credited with knowing one. The generator counts exactly how much of this
there is and writes it into the file header, so the number is visible to anyone
who opens the data rather than buried in a paper.
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import hsk30  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "src", "hsk30", "data", "t2s.tsv")

DEFAULT_OPENCC = os.path.expanduser(
    "~/Documents Mac/Chinese/GITHUB_Chinese_Books/data/opencc.js")


def load_opencc(path):
    src = open(path, encoding="utf-8").read()
    marker = "window.OPENCC="
    body = src[src.index(marker) + len(marker):].rstrip().rstrip(";")
    return json.loads(body)["t2sC"]


def build(t2s_char):
    """Pairs whose simplified form is in an inventory we ship."""
    inventory = set(hsk30.characters("2021")) | set(hsk30.characters("2025"))
    pairs = {t: s for t, s in t2s_char.items() if s in inventory and t != s}

    preimages = collections.defaultdict(list)
    for t, s in pairs.items():
        preimages[s].append(t)
    collapsed = {s: sorted(ts) for s, ts in preimages.items() if len(ts) > 1}
    absorbed = sum(len(ts) - 1 for ts in collapsed.values())
    return pairs, collapsed, absorbed, len(inventory)


def render(pairs, collapsed, absorbed, inventory_size):
    head = [
        "# Traditional-to-Simplified pairs, restricted to characters the shipped",
        "# HSK inventories grade. NOT a general converter -- no phrase table, no",
        "# context resolution, and anything outside the inventory is left alone.",
        "# For real conversion use OpenCC, from which these pairs are derived.",
        "#",
        "# Derived from OpenCC (https://github.com/BYVoid/OpenCC), Apache-2.0.",
        "#",
        "# %d pairs, covering an inventory of %d characters." % (len(pairs), inventory_size),
        "#",
        "# CONVERSION IS MANY-TO-ONE, and this is the number that matters:",
        "#   %d simplified inventory characters have more than one traditional" % len(collapsed),
        "#   preimage, absorbing %d extra traditional forms between them." % absorbed,
        "#   A traditional reader distinguishing 乾 / 幹 / 榦 is credited with the",
        "#   single character 干. Coverage against a simplified inventory is",
        "#   therefore an UPPER BOUND for traditional text, over-crediting by at",
        "#   most those %d forms." % absorbed,
        "#",
        "traditional\tsimplified",
    ]
    rows = ["%s\t%s" % (t, pairs[t]) for t in sorted(pairs)]
    return "\n".join(head + rows) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--opencc", default=DEFAULT_OPENCC,
                    help="OpenCC table dump (traditional-to-simplified)")
    ap.add_argument("--check", action="store_true",
                    help="compare against the shipped file instead of writing")
    args = ap.parse_args()

    if not os.path.exists(args.opencc):
        raise SystemExit(
            "OpenCC dump not found at %s\n"
            "Pass --opencc, or fetch a t2s table from "
            "https://github.com/BYVoid/OpenCC" % args.opencc)

    pairs, collapsed, absorbed, inv = build(load_opencc(args.opencc))
    content = render(pairs, collapsed, absorbed, inv)

    if args.check:
        current = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        same = current == content
        print("t2s.tsv %s" % ("ok" if same else "DIFFERS"))
        return 0 if same else 1

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(content)
    print("wrote %s" % os.path.relpath(OUT, HERE))
    print("  %d pairs over an inventory of %d characters" % (len(pairs), inv))
    print("  %d simplified characters absorb %d extra traditional forms"
          % (len(collapsed), absorbed))
    worst = sorted(collapsed.items(), key=lambda kv: -len(kv[1]))[:5]
    for s, ts in worst:
        print("     %s  <-  %s" % (s, " ".join(ts)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
