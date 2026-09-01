"""Command line interface: ``hsk30 <text>``."""

from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .data import DEFAULT_STANDARD, LEVELS, label
from .grade import budget_violations, grade


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="hsk30",
        description="Grade Chinese text against the HSK 3.0 character standard.",
    )
    ap.add_argument("text", nargs="?", help="text to grade; omit to read stdin")
    ap.add_argument("-f", "--file", help="read text from a file")
    ap.add_argument("-t", "--target", type=int, metavar="LEVEL",
                    help="report which characters push the text above LEVEL")
    ap.add_argument("--threshold", type=float, default=0.95,
                    help="coverage threshold (default: 0.95)")
    ap.add_argument("-s", "--standard", default=DEFAULT_STANDARD,
                    choices=["2025", "2021"],
                    help="2025 = the exam syllabus in force (default); "
                         "2021 = the national grading standard")
    ap.add_argument("--curve", action="store_true",
                    help="show cumulative coverage at every level")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    ap.add_argument("--version", action="version", version="hsk30 " + __version__)
    args = ap.parse_args(argv)

    if args.file:
        with open(args.file, encoding="utf-8") as fh:
            text = fh.read()
    elif args.text:
        text = args.text
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        ap.error("no text given; pass a string, use --file, or pipe stdin")

    profile = grade(text, threshold=args.threshold, standard=args.standard)
    payload = {
        "level": profile.level,
        "label": profile.label,
        "characters": profile.chars,
        "ungraded": profile.ungraded,
        "threshold": profile.threshold,
        "standard": profile.standard,
    }
    if args.curve:
        payload["coverage"] = {label(l): round(profile.coverage_at(l), 4) for l in LEVELS}
    if args.target is not None:
        share, offenders = budget_violations(
            text, args.target, threshold=args.threshold, standard=args.standard)
        payload["target"] = args.target
        payload["above_target_share"] = round(share, 4)
        payload["offenders"] = [
            {"character": ch, "level": label(lvl), "share": round(sh, 4)}
            for ch, lvl, sh in offenders
        ]

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if profile.chars == 0:
        print("no gradeable characters found")
        return 1

    source = ("2026 exam syllabus" if profile.standard == "2025"
              else "GF0025-2021 grading standard")
    print("HSK %s  (%d characters, %d ungraded)  [%s]"
          % (profile.label, profile.chars, profile.ungraded, source))
    if args.curve:
        for lvl in LEVELS:
            cov = profile.coverage_at(lvl)
            bar = "#" * int(round(cov * 40))
            print("  HSK %-4s %6.1f%%  %s" % (label(lvl), cov * 100, bar))
    if args.target is not None:
        share, offenders = budget_violations(
            text, args.target, threshold=args.threshold, standard=args.standard)
        verdict = "reaches" if share <= (1 - args.threshold) else "misses"
        print("  target HSK %d: %s the %.0f%% bar (%.1f%% above target)"
              % (args.target, verdict, args.threshold * 100, share * 100))
        for ch, lvl, sh in offenders[:12]:
            flag = "  <- over budget on its own" if sh > (1 - args.threshold) else ""
            print("    %s  HSK %-4s %5.1f%%%s" % (ch, label(lvl), sh * 100, flag))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
