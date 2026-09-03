# Contributing

Corrections are more welcome than features. This package makes factual claims
about two published national standards, and a wrong entry in a word list is a
worse bug than a crash — it is silent.

## Reporting a problem

Open an issue at https://github.com/harukicoder/hsk30/issues. There is no
template and no triage process; a plain description is fine.

For a **data error** — a word or character at the wrong level, a missing entry,
a wrong pinyin — please say which standard (`2.0`, `2021`, or `2025`) and, if
you can, cite the page or section of the official document. Data errors are
treated as the highest priority, because everything downstream inherits them.

For a **grading disagreement**, include the text and the level you expected.
Coverage grading is deliberately simple, so a surprising level is often correct
behaviour applied to a text that breaks an assumption; either way the case is
worth recording.

## Asking a question

Open an issue and label it however you like, or email
alvaro.serrano.gp@gmail.com. Questions about which standard applies to your
situation are in scope — that ambiguity is the reason this package exists.

## Contributing code

1. Fork, branch, and open a pull request against `main`.
2. Run the tests: `python3 tests/test_hsk30.py` (no dependencies) or
   `python3 -m pytest` if you have it. CI runs both on Python 3.9 through 3.13.
3. Add a test for anything you change. The suite pins published figures
   deliberately, so a test that fails after your change may mean the change is
   wrong, or may mean a published number needs correcting — say which you
   think it is.
4. If you change anything that appears in the paper, run
   `python3 scripts/check_paper.py`, which verifies published figures against
   live computation.

Keep the runtime dependency-free. The package installs and runs offline with
only the standard library, and that is a feature for classroom use.

## Changing the data

Data files under `src/hsk30/data/` are extracted from official publications by
scripts in `scripts/`. Please change the extractor and regenerate, rather than
hand-editing a TSV, so that the provenance chain stays intact. The extraction
self-validates against the official per-level totals; if your change breaks that
check, it is the change that is wrong.

## Scope

Out of scope: a segmenter, a learned readability model, and anything that
requires a network call at runtime. The value of this package is that it is a
transparent, deterministic function of a published standard, and each of those
would compromise that.
