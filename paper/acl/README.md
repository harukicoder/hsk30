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

Easiest, and works from a tablet: upload `main.tex` + `refs.bib` + the ACL
style files to [Overleaf](https://overleaf.com), set the compiler to **XeLaTeX**
in Menu → Settings.

Locally, with TeX Live installed:

```bash
xelatex main && bibtex main && xelatex main && xelatex main
```

## Before submitting

- Switch `\usepackage[review]{acl}` to `\usepackage[final]{acl}` and uncheck
  anonymity if the venue is not double-blind.
- BEA is typically **8 pages plus unlimited references**; check the current
  call, and check whether it is anonymous — the author block is filled in.
- Resolve the three `\todo{}` markers (they compile as visible red text and
  are impossible to miss).
- Re-run `python3 ../../scripts/reproduce.py` and confirm every number in the
  tables still matches. None of them are typed by hand upstream; do not let
  them become hand-typed here.
