# ACL / BEA submission build

`main.tex` is the paper in ACL format. **It has not been compiled** — the
machine it was written on has no TeX toolchain — so treat the first build as a
proofing pass, not a formality.

## Two things that are not the default

**Use XeLaTeX, not pdfLaTeX.** The paper quotes Chinese throughout
(《国际中文教育中文水平等级标准》, 欧洲, 哥哥). `main.tex` loads `xeCJK` and
sets a CJK font; pdfLaTeX will fail on these.

**Get the ACL style files.** `acl.sty`, `acl_natbib.bst` and `anthology.bib`
are not in this repository. Download the official template from
<https://github.com/acl-org/acl-style-files> and drop `acl.sty` and
`acl_natbib.bst` beside `main.tex`.

## Building

```bash
./build.sh
```

Fetches the ACL style files if absent and compiles with
[tectonic](https://tectonic-typesetting.github.io) (`brew install tectonic`).
It reports overfull boxes and fails on BibTeX errors, so a broken build cannot
pass silently.

**Verified building on macOS, 1 September 2026:** 7 pages, zero overfull boxes,
zero unresolved citations, Chinese rendering correctly in Songti SC.

From a tablet, or without installing anything: upload `main.tex`, `refs.bib`
and the two ACL style files to [Overleaf](https://overleaf.com) and set the
compiler to **XeLaTeX** in Menu → Settings.

## Notes from the first build

All three anticipated hazards were resolved on 1 September 2026:

- **hyperref** — `acl.sty` loads it at line 195, so `main.tex` declares
  nothing. Do not add it; loading twice causes an option clash.
- **`\bibliographystyle`** — `acl.sty` also issues this. Declaring it again in
  `main.tex` makes BibTeX abort with *"Illegal, another \bibstyle command"*.
  This bit once; the line is gone.
- **The CJK font** — set to `Songti SC`, which ships with macOS. On Overleaf or
  Linux use `Noto Serif CJK SC`.
- **Table widths** — the seven-column results table fits the single-column
  layout unmodified. No `\resizebox` needed.

## The one that nearly shipped

`acl.sty` has two modes and both compile cleanly to the same page count:

- **`[final]`** — named author block, no line numbers. **Preprints and
  camera-ready. This build must stay here.**
- **`[review]`** — prints *"Anonymous ACL submission"* and line numbers. For
  double-blind submission only.

The paper was written in `[review]`, which is right for submitting to a venue
and wrong for anything deposited. A PDF that does not carry the author's name
is not evidence of authorship, and the difference is one header line most
people skim past — it reached two published Zenodo versions before anyone
noticed. `check_authorship.py` now fails the build on an anonymised PDF.

Switch to `[review]` only when submitting somewhere anonymous, and switch back
immediately afterwards.

## Before submitting

- Switch `\usepackage[review]{acl}` to `\usepackage[final]{acl}` and uncheck
  anonymity if the venue is not double-blind.
- BEA is typically **8 pages plus unlimited references**; check the current
  call, and check whether it is anonymous — the author block is filled in.
- ~~Resolve the `\todo{}` markers~~ — all resolved. The macro is removed, so a
  stray `\todo` will now fail the build rather than print quietly in red.
- Re-run `python3 ../../scripts/reproduce.py` and confirm every number in the
  tables still matches. None of them are typed by hand upstream; do not let
  them become hand-typed here.
