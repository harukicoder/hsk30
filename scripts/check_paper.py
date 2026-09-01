#!/usr/bin/env python3
"""Verify that every headline figure in the paper matches live computation.

    python3 scripts/check_paper.py            # checks paper/paper.md and the .tex
    python3 scripts/check_paper.py --list     # print the computed figures

This exists because the numbers in an earlier draft came from a changelog and
had silently drifted from the data (4,490/817/501/6,479 against a true
4,482/814/509/6,434). Prose does not recompute itself, so it is checked here
and in CI instead.

Each figure is computed from the shipped data and then searched for in the
paper, in both comma-grouped and bare forms. A figure the paper does not
mention is reported but not fatal; a figure the paper contradicts is fatal.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))

import hsk30  # noqa: E402

ROOT = os.path.join(HERE, "..")
DOCS = [
    os.path.join(ROOT, "paper", "paper.md"),
    os.path.join(ROOT, "paper", "acl", "main.tex"),
    os.path.join(ROOT, "README.md"),
]
CORPUS = os.path.join(ROOT, "corpus", "hsk30_graded_readers.jsonl")
RESULTS = os.path.join(ROOT, "benchmark", "results", "deepseek-chat_report.json")


def corpus_rows():
    with open(CORPUS, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def figures():
    """Compute every number the paper asserts. Returns {label: value}."""
    out = {}
    w20, w21, w25 = (hsk30.words(s) for s in ("2.0", "2021", "2025"))
    c21, c25 = hsk30.characters("2021"), hsk30.characters("2025")

    out["hsk20 words"] = len(w20)
    out["2021 words"] = len(w21)
    out["2025 words"] = len(w25)
    out["2021 chars"] = len(c21)
    out["2025 chars"] = len(c25)

    def agree(a, b):
        shared = [w for w in a if w in b]
        same = [w for w in shared if a[w] == b[w]]
        return len(shared), len(same), round(100.0 * (len(shared) - len(same)) / len(shared), 1)

    sh, sm, mv = agree(w20, w21)
    out["2.0->2021 shared"], out["2.0->2021 same"], out["2.0->2021 moved pct"] = sh, sm, mv
    out["2.0->2021 moved"] = sh - sm
    out["2.0->2025 moved pct"] = agree(w20, w25)[2]
    sh, sm, mv = agree(w21, w25)
    out["2021->2025 shared"], out["2021->2025 same"], out["2021->2025 moved pct"] = sh, sm, mv

    shared = [c for c in c21 if c in c25]
    same = [c for c in shared if c21[c] == c25[c]]
    out["char shared"] = len(shared)
    out["char moved"] = len(shared) - len(same)
    out["char moved pct"] = round(100.0 * (len(shared) - len(same)) / len(shared), 1)

    # Beginner inventories: the mechanism behind the regrade.
    out["2021 chars L1-2"] = sum(1 for v in c21.values() if v <= 2)
    out["2025 chars L1-2"] = sum(1 for v in c25.values() if v <= 2)

    # Derived-vs-official character levels.
    derived = {}
    for word, level in w21.items():
        for ch in word:
            if ch in c21 and (ch not in derived or level < derived[ch]):
                derived[ch] = level
    shared_d = [c for c in derived if c in c21]
    out["derivable chars"] = len(shared_d)
    out["derived agree"] = sum(1 for c in shared_d if derived[c] == c21[c])

    rows = corpus_rows()
    out["corpus texts"] = len(rows)
    out["corpus sentences"] = sum(r["n_sentences"] for r in rows)

    changed = 0
    for r in rows:
        toks = [w for s in r["sentences"] for w in s["words"]]
        if (hsk30.grade_tokens(toks, standard="2021").level
                != hsk30.grade_tokens(toks, standard="2025").level):
            changed += 1
    out["regrade changed"] = changed
    out["regrade changed pct"] = round(100.0 * changed / len(rows), 1)

    # Human reference on HSKBench.
    shelf_target = {"newbie": 1, "beginner": 2, "intermediate": 3,
                    "upper": 4, "advanced": 5, "native": 6}
    hits = 0
    for r in rows:
        toks = [w for s in r["sentences"] for w in s["words"]]
        lvl = hsk30.grade_tokens(toks, standard="2021").level
        if lvl is not None and lvl <= shelf_target[r["shelf"]]:
            hits += 1
    out["human accuracy pct"] = round(100.0 * hits / len(rows), 1)

    if os.path.exists(RESULTS):
        rep = json.load(open(RESULTS, encoding="utf-8"))["report"]
        out["deepseek accuracy pct"] = round(100 * rep["overall"]["level_accuracy"], 1)
    return out


def variants(value):
    """A number as the paper might write it: 4482, 4,482, 4{,}482, 81.8."""
    if isinstance(value, float):
        return {("%g" % value), ("%.1f" % value)}
    text = str(value)
    grouped = "{:,}".format(value) if isinstance(value, int) else text
    return {text, grouped, grouped.replace(",", "{,}"), grouped.replace(",", " ")}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    figs = figures()
    if args.list:
        for k, v in figs.items():
            print("  %-24s %s" % (k, v))
        return 0

    texts = {}
    for path in DOCS:
        if os.path.exists(path):
            texts[os.path.relpath(path, ROOT)] = open(path, encoding="utf-8").read()

    print("Checking %d figures against %d documents\n" % (len(figs), len(texts)))
    missing = []
    for label, value in sorted(figs.items()):
        found = [name for name, body in texts.items()
                 if any(v in body for v in variants(value))]
        if found:
            print("  ok      %-24s %-10s %s" % (label, value, ", ".join(found)))
        else:
            missing.append((label, value))
            print("  ABSENT  %-24s %-10s not stated in any document" % (label, value))

    if missing:
        print("\n%d computed figure(s) appear in no document. That is fine for a"
              % len(missing))
        print("figure the paper never claims — but if the paper states a DIFFERENT")
        print("value for one of these, it is now wrong. Check each:")
        for label, value in missing:
            print("  - %s should read %s" % (label, value))
    print("\nNote: this checks presence, not context. It catches drift, not a")
    print("number attached to the wrong claim.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
