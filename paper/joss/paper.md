---
title: 'hsk30: reproducible grading of Chinese text difficulty against either official HSK 3.0 document'
tags:
  - Python
  - Chinese
  - Mandarin
  - readability
  - text difficulty
  - second language acquisition
  - language learning
  - corpus
authors:
  - name: Alvaro Serrano
    orcid: 0009-0006-4701-9026
    affiliation: 1
affiliations:
  - name: Independent researcher, Brighton, United Kingdom
    index: 1
date: 3 September 2026
bibliography: paper.bib
---

# Summary

`hsk30` grades the difficulty of Chinese text against the official Chinese
proficiency standards, and records which standard it used. It answers the
question a teacher or a materials designer asks constantly — *what level is this
text, and can a learner at level N read it?* — as a deterministic function of a
published national inventory, with no learned parameters and no network access.

The package ships validated machine-readable extractions of three documents: the
HSK 2.0 word list, the national grading standard 《国际中文教育中文水平等级标准》
(GF0025-2021), and the examination syllabus published in November 2025 and in
force since July 2026, including its separate 1,200-character handwriting
inventory. It grades raw strings or pre-segmented tokens, reports per-level
coverage curves rather than a single label, flags vocabulary that exceeds a
level budget, and profiles a whole corpus shelf at once. Alongside the library it
distributes an aligned 132-text graded-reader corpus with per-word pinyin and
gloss under CC BY 4.0, and `WriteToLevel`, a difficulty-controlled generation
benchmark in which the grader serves as the evaluation metric rather than as the
source of labels.

# Statement of need

Chinese reading material is levelled by HSK, and tools that assign such levels
are widely used. Almost all of them are closed, hosted, and silent about their
source: they report that a text is "HSK 3.0 level 4" without saying which
document produced that number, what threshold was applied, or how the text was
segmented. None of those choices is neutral, and none can be audited.

The specific problem this package exists to solve is that "HSK 3.0" does not
identify a document. Two official publications carry the name, four years apart,
and they assign different levels to 41.5% of the vocabulary and 40.7% of the
characters they share; grading authentic graded readers against one rather than
the other changes the assigned level of roughly half of them [@serrano2026whichhsk].
A level reported without naming its source is therefore not reproducible, and
comparisons between tools that do not name their sources are not meaningful.
`hsk30` records the standard on every result, and refuses to default silently
where the choice matters.

A second need is methodological. Evaluating whether a language model can write to
a target difficulty requires a difficulty metric that is not itself a learned
model trained on similar text, or the evaluation becomes circular
[@imperial2023flesch; @barayan2025analyzing]. A transparent set-membership check
against a published government inventory is exactly such a metric: compliance is
checkable exactly, without a judge and without a trained scorer. `WriteToLevel`
is built on that property, and is distributed with the package so that the metric
and the benchmark cannot drift apart.

The package is dependency-free and runs offline against the standard library
alone. This is deliberate: the intended users include classroom teachers and
small programmes for whom an install that requires a build toolchain, an account
or an internet connection is an install that does not happen.

# State of the field

Automatic readability assessment for Chinese is dominated by supervised
classification over engineered linguistic features. CRIE extracts eighty-two
multilevel indices trained on Taiwanese school textbooks [@sung2016crie], and
more recent work applies pretrained transformers with feature fusion
[@yang2025chinese]. These approaches model more than vocabulary coverage and will
outperform a coverage threshold on many tasks.

`hsk30` is deliberately not in that tradition. It is a transparent, deterministic
function of an official published standard, auditable line by line in a way a
classifier is not, and stable across runs and versions. Where a learned model
answers *how hard does this look*, `hsk30` answers *what does this standard say*
— a different and narrower question, but the one that placement, curriculum
mapping and examination alignment actually turn on.

The closest adjacent resource is `HSKBenchmark` [@yang2026hskbenchmark], which
tunes and evaluates models across HSK levels 3 to 6 and scores grammar coverage
and syntactic complexity. It draws its grammar inventory from the 2021 standard
while building its corpus from textbook series aligned to earlier outlines, and
does not state which document defines its levels — an instance of precisely the
ambiguity this package is built to make visible.

# Quality control

The library carries 39 tests, run on every push against Python 3.9 through 3.13,
and executable either under `pytest` or as a plain script with no test framework
installed. The syllabus extraction self-validates: its per-level entry counts are
asserted against the cumulative totals published in the source document, and the
build fails if they diverge. A separate script re-derives every figure quoted in
the accompanying papers from live computation, so that published numbers and
shipped data cannot drift apart silently.

# Acknowledgements

The corpus was authored with the assistance of a large language model, disclosed
in full in its datasheet. No other funding or institutional support was involved.

# References
