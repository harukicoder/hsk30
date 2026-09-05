#!/usr/bin/env python3
"""Grade a programme's own texts under both HSK 3.0 documents, and report the difference.

    python3 scripts/levelling_report.py --dir path/to/texts \\
        --for "Utah State Board of Education" -o report.md

    python3 scripts/levelling_report.py --jsonl shelf.jsonl --for "Ole Miss" -o report.md

Input is either a directory of UTF-8 ``.txt`` files, one text per file, or a
JSON Lines file whose objects carry ``text`` and optionally ``id`` and
``shelf``. Nothing is uploaded and nothing is retained: this runs entirely on
the machine it is invoked on, which is the answer to the first question any
school asks about sending its materials somewhere.

Why this exists. The finding published in `doi:10.5281/zenodo.22239032` is that
"HSK 3.0" names two official documents which disagree about 41.5% of the
vocabulary they share, so a levelling decision is not reproducible unless the
standard is named. That is an abstract claim until somebody sees it on their own
shelf. This turns it into a concrete one: here are your texts, here is what each
document says, and here are the ones where the two disagree.

The report is deliberately not persuasive. It states what changed, gives the
count of texts where nothing changed, and says plainly when the answer is that
the two documents agree about the whole shelf — which happens, and is a real
result rather than a failed demonstration.
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import sys
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import hsk30  # noqa: E402

#: Neither table is endorsed by any issuing body. The PRC standard publishes no
#: CEFR alignment at all, so every HSK-to-CEFR mapping in circulation was
#: reconstructed by teachers and vendors. Both are shown, and the report says
#: so, because showing one would imply an authority that does not exist.
NAIVE = {1: "A1", 2: "A2", 3: "B1", 4: "B2", 5: "C1", 6: "C2",
         7: "C2", 8: "C2", 9: "C2"}
COMPRESSED = {1: "A1", 2: "A1", 3: "A2", 4: "B1", 5: "B2", 6: "B2",
              7: "C1", 8: "C1", 9: "C2"}


def read_dir(path):
    for name in sorted(os.listdir(path)):
        if not name.lower().endswith(".txt"):
            continue
        with open(os.path.join(path, name), encoding="utf-8") as fh:
            text = fh.read().strip()
        if text:
            yield {"id": os.path.splitext(name)[0], "text": text, "shelf": None}


def read_jsonl(path):
    with open(path, encoding="utf-8") as fh:
        for i, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            text = row.get("text")
            if text is None and "sentences" in row:
                # the corpus format: sentences of word objects
                text = "".join(w.get("hz", "") for s in row["sentences"]
                               for w in s["words"])
            if not text:
                continue
            yield {"id": str(row.get("id", i)), "text": text,
                   "shelf": row.get("shelf")}


def lvl(p):
    """A level, or None when no level in range reaches the threshold."""
    return p.level if p and p.level else None


def fmt_level(n):
    return "HSK %d" % n if n else "above HSK 9"


def build(items, threshold):
    rows = []
    for it in items:
        a = hsk30.grade(it["text"], standard="2021", threshold=threshold)
        b = hsk30.grade(it["text"], standard="2025", threshold=threshold)
        rows.append({
            "id": it["id"],
            "shelf": it["shelf"],
            "chars": b.chars,
            "l2021": lvl(a),
            "l2025": lvl(b),
            "profile_2021": a,
            "profile_2025": b,
        })
    return rows


def report(rows, recipient, threshold, source_desc):
    L = []
    add = L.append
    n = len(rows)
    changed = [r for r in rows if r["l2021"] != r["l2025"]]
    harder_2021 = sum(1 for r in changed
                      if r["l2021"] and r["l2025"] and r["l2021"] > r["l2025"])

    add("# Levelling report — %s" % (recipient or "your texts"))
    add("")
    add("Prepared %s. %d texts, read from %s." % (date.today().isoformat(), n, source_desc))
    add("")
    add("This report was generated locally with the open-source `hsk30` library")
    add("(`pip install hsk30`, MIT licence). No text left the machine it was run on,")
    add("and nothing was retained. You can run it yourself: the script is")
    add("`scripts/levelling_report.py` in `github.com/harukicoder/hsk30`.")
    add("")
    add("---")
    add("")

    # ---------------------------------------------------------------- summary
    add("## What this shows")
    add("")
    add("\"HSK 3.0\" names **two different official documents**:")
    add("")
    add("- 《国际中文教育中文水平等级标准》 **GF0025-2021** — the national grading")
    add("  standard, in force since 1 July 2021.")
    add("- 新版HSK考试大纲 — the **2025 examination syllabus**, published November")
    add("  2025, in force since July 2026.")
    add("")
    add("They assign different levels to 41.5% of the vocabulary and 40.7% of the")
    add("characters they share. Most tools do not say which one they used.")
    add("")

    if not changed:
        add("**On your texts, the two documents agree everywhere.** All %d texts receive"
            % n)
        add("the same level under both. That is a real and useful result: it means your")
        add("levelling is not exposed to this ambiguity, at least on this material. It")
        add("is not the usual outcome — across a 102-text reference corpus, 48% of texts")
        add("change level — so it is worth knowing that your shelf is not among them.")
    else:
        pct = 100.0 * len(changed) / n
        add("**On your texts, %d of %d (%.0f%%) receive a different level depending on"
            % (len(changed), n, pct))
        add("which document is used.**")
        add("")
        if harder_2021:
            other = len(changed) - harder_2021
            add("Of those, %d %s graded *higher* under the 2021 standard than under"
                % (harder_2021, "is" if harder_2021 == 1 else "are"))
            add("the 2025 syllabus, and %d the other way." % other)
        add("")
        add("A text whose level changes is a text whose placement, whose assigned")
        add("reader, and whose reported CEFR band all change with a choice nobody wrote")
        add("down.")
    add("")

    # ---------------------------------------------------------------- shelves
    add("## Shelf summary")
    add("")
    add("Reported as the **median text and interquartile range**, not the pooled")
    add("figure. Pooling every character in a collection lets a handful of hard texts")
    add("speak for all of them.")
    add("")
    by_shelf = collections.defaultdict(list)
    for r in rows:
        by_shelf[r["shelf"] or "All texts"].append(r)
    add("| Collection | Texts | Under GF0025-2021 | Under 2025 syllabus |")
    add("| --- | ---: | --- | --- |")
    for shelf, group in sorted(by_shelf.items(), key=lambda kv: str(kv[0])):
        sp21 = hsk30.profile_shelf([g["profile_2021"] for g in group])
        sp25 = hsk30.profile_shelf([g["profile_2025"] for g in group])
        add("| %s | %d | %s | %s |" % (shelf, len(group), _shelf_str(sp21), _shelf_str(sp25)))
    add("")

    # ---------------------------------------------------------------- CEFR
    add("## If you report proficiency in CEFR bands")
    add("")
    add("**The PRC standard publishes no CEFR alignment.** Every HSK-to-CEFR table in")
    add("circulation was reconstructed by teachers and vendors, not issued by any")
    add("authority. Two are in common use and they disagree with each other, so both")
    add("are shown. Neither is endorsed here.")
    add("")
    add("| Table | Band under GF0025-2021 | Band under 2025 syllabus | Texts that move band |")
    add("| --- | --- | --- | ---: |")
    for name, table in (("Naive 1:1", NAIVE), ("Compressed", COMPRESSED)):
        b21 = collections.Counter(table.get(r["l2021"], "above") for r in rows)
        b25 = collections.Counter(table.get(r["l2025"], "above") for r in rows)
        moved = sum(1 for r in rows
                    if table.get(r["l2021"], "above") != table.get(r["l2025"], "above"))
        add("| %s | %s | %s | %d |" % (name, _bands(b21), _bands(b25), moved))
    add("")
    add("Detail: `doi:10.5281/zenodo.22285473`, which measures this against Taiwan's")
    add("TOCFL — the one Chinese framework that does carry an official CEFR alignment.")
    add("")

    # ---------------------------------------------------------------- detail
    add("## Text by text")
    add("")
    add("Texts where the two documents disagree are marked **→**.")
    add("")
    add("| Text | Characters | GF0025-2021 | 2025 syllabus | |")
    add("| --- | ---: | --- | --- | --- |")
    for r in rows:
        mark = "**→**" if r["l2021"] != r["l2025"] else ""
        add("| %s | %d | %s | %s | %s |" % (
            r["id"], r["chars"], fmt_level(r["l2021"]), fmt_level(r["l2025"]), mark))
    add("")

    # ---------------------------------------------------------------- method
    add("## Method, and what it does not tell you")
    add("")
    add("Grading is character-level: proper nouns are dropped by pinyin")
    add("capitalisation, punctuation is stripped, and a text's level is the lowest")
    add("level whose cumulative character inventory covers **%.0f%%** of its running"
        % (threshold * 100))
    add("characters. %.0f%% is the standard minimal-comprehension threshold in the"
        % (threshold * 100))
    add("reading literature (Laufer; Hu and Nation).")
    add("")
    add("**What this does not measure.** Vocabulary coverage is necessary for")
    add("comprehension, not sufficient. Grammar, register, discourse structure and")
    add("cultural load are unmodelled. A text can pass the threshold and still be")
    add("hard, and this report will not tell you that. It tells you one thing")
    add("precisely: whether the two official documents agree about your material.")
    add("")
    add("**No recommendation is attached.** Which document a programme should follow")
    add("depends on whether it is teaching to the national standard or preparing")
    add("students for the examination, and that is a curricular decision, not a")
    add("technical one. The only claim made here is that the choice should be")
    add("recorded, because the answer changes with it.")
    add("")
    add("---")
    add("")
    add("*Generated by `scripts/levelling_report.py` from `hsk30` version %s.*"
        % getattr(hsk30, "__version__", "0.2.0"))
    add("*Source and licence: `github.com/harukicoder/hsk30` (MIT).*")
    return "\n".join(L) + "\n"


def _shelf_str(sp):
    """Median plus the interquartile span, printed the way a librarian reads it.

    ``span_label`` is the library's own rendering of the interquartile range, so
    the report and the library cannot drift apart on how a shelf is described.
    """
    if sp.median is None:
        return "—"
    if sp.iqr_low == sp.iqr_high:
        return "HSK %s" % sp.median
    return "median HSK %s, %s" % (sp.median, sp.span_label)


def _bands(counter):
    order = ["A1", "A2", "B1", "B2", "C1", "C2", "above"]
    parts = ["%s×%d" % (b, counter[b]) for b in order if counter.get(b)]
    return ", ".join(parts) or "—"


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--dir", help="directory of UTF-8 .txt files, one text each")
    src.add_argument("--jsonl", help="JSON Lines with a 'text' field per object")
    ap.add_argument("--for", dest="recipient", default="",
                    help="name of the programme or institution, for the heading")
    ap.add_argument("--threshold", type=float, default=0.95,
                    help="coverage threshold (default 0.95)")
    ap.add_argument("-o", "--out", default="-", help="output file, or - for stdout")
    args = ap.parse_args()

    if args.dir:
        items = list(read_dir(args.dir))
        desc = "`%s`" % os.path.basename(os.path.normpath(args.dir))
    else:
        items = list(read_jsonl(args.jsonl))
        desc = "`%s`" % os.path.basename(args.jsonl)

    if not items:
        raise SystemExit("no texts found — expected .txt files or a 'text' field")

    rows = build(items, args.threshold)
    out = report(rows, args.recipient, args.threshold, desc)

    if args.out == "-":
        sys.stdout.write(out)
    else:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(out)
        changed = sum(1 for r in rows if r["l2021"] != r["l2025"])
        print("wrote %s — %d texts, %d graded differently by the two documents"
              % (args.out, len(rows), changed), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
