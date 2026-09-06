#!/usr/bin/env python3
"""Find a dataset's standard declaration, then check the data against the claim.

    python3 scripts/check_declaration.py path/to/data.json
    python3 scripts/check_declaration.py --all          # the shipped tables
    python3 scripts/check_declaration.py --registry     # list known identifiers

Implements `spec/README.md`. Two jobs, and the second is the one that matters:

1. **Find the declaration.** A ``standard`` key in a JSON object, a sibling
   ``standard.json``, a ``# standard: ...`` comment, or a ``standard`` column.
2. **Test it.** The three mainland documents grade 531 short words at three
   different levels, so the data reveals which one it encodes regardless of what
   it says. A file declaring ``gf0025-2021`` and matching it on 58.5% of shared
   words has mislabelled itself, and saying so is the whole point — a
   declaration nobody can check is a comment.

Undeclared data is not an error. It is fingerprinted and told which identifier
it should declare, which is more useful than a complaint.

Accepts word lists as ``{word: level}``, ``[{"word": w, "level": n}, ...]``,
``[[w, n], ...]``, or two-column CSV/TSV. Anything it cannot read it says so
about, rather than guessing.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import hsk30  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTRY = os.path.join(HERE, "..", "spec", "standards.json")

#: Registry identifier -> the argument hsk30.words() takes. Only the mainland
#: documents are gradeable here; the Taiwan inventories are not redistributed,
#: so a declaration naming them is resolved but cannot be verified.
GRADEABLE = {
    "hsk-2012": "2.0",
    "gf0025-2021": "2021",
    "hsk-syllabus-2025": "2025",
}


def registry():
    with open(REGISTRY, encoding="utf-8") as fh:
        return json.load(fh)


# ------------------------------------------------------------------ finding it

def find_declaration(path):
    """Return (identifier, where_it_was_found) or (None, reason)."""
    sibling = os.path.join(os.path.dirname(os.path.abspath(path)), "standard.json")
    if os.path.exists(sibling):
        try:
            d = json.load(open(sibling, encoding="utf-8"))
            if d.get("standard"):
                return d["standard"], "sibling standard.json"
        except (ValueError, OSError):
            pass

    if path.lower().endswith(".json"):
        try:
            d = json.load(open(path, encoding="utf-8"))
        except (ValueError, OSError) as exc:
            return None, "unreadable JSON: %s" % exc
        if isinstance(d, dict) and d.get("standard"):
            return d["standard"], "top-level \"standard\" key"
        return None, "JSON with no \"standard\" key and no sibling standard.json"

    # text formats: a comment line anywhere in the first 20 lines
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            head = [next(fh, "") for _ in range(20)]
    except OSError as exc:
        return None, str(exc)
    for line in head:
        m = re.match(r"^\s*[#;/]+\s*standard\s*[:=]\s*([A-Za-z0-9._-]+)", line)
        if m:
            return m.group(1), "comment line"
    return None, "no declaration found"


# ------------------------------------------------------------------ reading it

def _level(value):
    """An int level from whatever shape a dataset uses to express one.

    Levels appear as ints, as strings, and as tagged strings inside a list --
    drkameleon writes ["n7"] for new-HSK level 7 and ["o5"] for old-HSK level 5,
    so a naive isinstance(v, int) test reads none of them.
    """
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        m = re.match(r"^n?(\d)$", value)          # "3" or "n3"; "o3" is old HSK
        return int(m.group(1)) if m else None
    if isinstance(value, list):
        for item in value:
            lv = _level(item)
            if lv is not None:
                return lv
    return None


def read_pairs(path):
    """Best effort {word: level}. Returns (mapping, note)."""
    if path.lower().endswith(".json"):
        try:
            d = json.load(open(path, encoding="utf-8"))
        except (ValueError, OSError) as exc:
            return {}, "unreadable: %s" % exc
        body = d.get("words", d) if isinstance(d, dict) else d

        if isinstance(body, dict):
            out = {k: v for k, v in body.items() if isinstance(v, int)}
            if out:
                return out, "JSON object of word -> level"
            # level-keyed: {"hsk1": [...], "hsk2": [...]} or {"1": [...]}
            out = {}
            for key, vals in body.items():
                m = re.search(r"(\d)", str(key))
                if not m or not isinstance(vals, list):
                    continue
                lvl = int(m.group(1))
                for w in vals:
                    if isinstance(w, str) and w:
                        out.setdefault(w, lvl)
            if out:
                return out, "JSON object of level -> word list"

        if isinstance(body, list):
            out = {}
            for row in body:
                if isinstance(row, dict):
                    w = row.get("word") or row.get("simplified") or row.get("s")
                    lv = _level(row.get("level"))
                    if lv is None:
                        lv = _level(row.get("l"))
                    if w and lv is not None:
                        out.setdefault(w, lv)
                elif isinstance(row, (list, tuple)) and len(row) >= 2:
                    w, lv = row[0], row[1]
                    if isinstance(w, str) and isinstance(lv, int):
                        out.setdefault(w, lv)
            if out:
                return out, "JSON array of entries"
        return {}, "JSON shape not recognised"

    # delimited text
    delim = "\t" if path.lower().endswith((".tsv", ".txt")) else ","
    out = {}
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            rows = [r for r in csv.reader(fh, delimiter=delim)
                    if r and not r[0].lstrip().startswith("#")]
    except OSError as exc:
        return {}, str(exc)
    for r in rows:
        if len(r) < 2:
            continue
        w, lv = r[0].strip(), r[1].strip()
        # hanzi() returns a *list* of the CJK characters in a string, so
        # "".join(...) == w is the test for "every character is an ideograph".
        # Comparing the list to the string silently rejected every row.
        if w and lv.isdigit() and "".join(hsk30.hanzi(w)) == w:
            out.setdefault(w, min(int(lv), 7))
    return out, "delimited, two columns"


# ------------------------------------------------------------------ testing it

def agreement(words, std_key):
    ref = hsk30.words(std_key)
    shared = [w for w in words if w in ref]
    if not shared:
        return 0.0, 0
    agree = sum(1 for w in shared if words[w] == ref[w])
    return 100.0 * agree / len(shared), len(shared)


def best_match(words):
    scored = []
    for ident, key in GRADEABLE.items():
        rate, n = agreement(words, key)
        scored.append((rate, n, ident))
    scored.sort(reverse=True)
    return scored


def check(path, reg):
    print(path)
    ident, where = find_declaration(path)
    known = reg["standards"]

    if ident:
        if ident in known:
            print("  declared   %s  (%s)" % (ident, where))
            print("             %s" % known[ident]["name_zh"])
        else:
            print("  declared   %s  (%s)  -- NOT IN REGISTRY" % (ident, where))
            print("             open a PR adding it, or correct the identifier")
    else:
        print("  declared   nothing  (%s)" % where)

    words, note = read_pairs(path)
    if not words:
        print("  data       could not be read as a word list (%s)" % note)
        if ident:
            print("  VERDICT    UNVERIFIED. Declaration found, but the data could")
            print("             not be read, so the claim stands untested.")
            return 2
        print("  VERDICT    UNDECLARED, and unreadable by this tool. Nothing to")
        print("             check the data against, and nothing claimed.")
        return 1

    scored = best_match(words)
    print("  data       %d entries, %s" % (len(words), note))
    for rate, n, cand in scored:
        mark = "<--" if cand == ident else "   "
        print("    %-20s %5.1f%%  over %6d shared  %s" % (cand, rate, n, mark))

    top_rate, _, top = scored[0]

    if not ident:
        print("  VERDICT    undeclared. The data matches %s." % top)
        print("             Add:  \"standard\": \"%s\"" % top)
        return 1

    if ident not in GRADEABLE:
        print("  VERDICT    declared %s, which this tool cannot verify" % ident)
        print("             (the Taiwan inventories are not redistributed here)")
        return 0

    declared_rate = next(r for r, _, c in scored if c == ident)
    if ident == top and declared_rate >= 95.0:
        print("  VERDICT    ok. Declaration matches the data (%.1f%%)." % declared_rate)
        return 0
    if ident == top:
        print("  VERDICT    declaration is the best match but only %.1f%%."
              % declared_rate)
        print("             Likely a partial or modified extraction; consider")
        print("             \"coverage\": \"partial\".")
        return 0
    print("  VERDICT    MISLABELLED. Declares %s (%.1f%%) but matches %s (%.1f%%)."
          % (ident, declared_rate, top, top_rate))
    return 1


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help="dataset files to check")
    ap.add_argument("--all", action="store_true", help="check the shipped tables")
    ap.add_argument("--registry", action="store_true", help="list known identifiers")
    args = ap.parse_args()

    reg = registry()

    if args.registry:
        print("Registry %s  (%s)" % (reg["registry_version"], REGISTRY))
        print()
        for ident, d in reg["standards"].items():
            inv = ", ".join("%s %s" % (k, v) for k, v in d.get("inventories", {}).items())
            print("  %-20s %s" % (ident, d["name_zh"]))
            print("  %-20s %s | in force %s | %s"
                  % ("", d.get("name_en", ""), d.get("in_force_from", "?"), inv))
            print()
        amb = reg.get("$ambiguous_names", {})
        for name, ids in amb.items():
            if name.startswith("$"):
                continue
            print("  AMBIGUOUS: \"%s\" -> %s" % (name, ", ".join(ids)))
        return 0

    paths = list(args.paths)
    if args.all or not paths:
        data = os.path.join(HERE, "..", "src", "hsk30", "data")
        paths = [os.path.join(data, f) for f in sorted(os.listdir(data))
                 if f.endswith("_words.tsv")]

    failed = unverified = 0
    for p in paths:
        rc = check(p, reg)
        failed += 1 if rc == 1 else 0
        unverified += 1 if rc == 2 else 0
        print()

    # An unverified declaration is not a verified one. Reporting "all verified"
    # when nothing could be read is the same class of unchecked claim this
    # whole convention exists to prevent, so it gets its own exit code.
    if failed:
        print("%d file(s) undeclared or mislabelled" % failed)
    if unverified:
        print("%d file(s) declared but NOT verified — a declaration nobody "
              "checked is a comment" % unverified)
    if not failed and not unverified:
        print("all declarations verified against the data")
    return 1 if failed else (2 if unverified else 0)


if __name__ == "__main__":
    raise SystemExit(main())
