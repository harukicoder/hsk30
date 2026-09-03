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
inventory. It grades raw strings or pre-segmented tokens, reports coverage curves rather
than a single label, flags vocabulary exceeding a level budget, and profiles a
whole corpus at once. It also distributes an aligned 132-text graded-reader
corpus under CC BY 4.0 and `WriteToLevel`, a difficulty-controlled generation
benchmark in which the grader is the metric rather than the source of labels.

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
alone. This is deliberate: its intended users include classroom teachers and
small programmes, for whom an install requiring a build toolchain, an account or
an internet connection is an install that does not happen.

# State of the field

Automatic readability assessment for Chinese is dominated by supervised
classification over engineered features: CRIE extracts eighty-two multilevel
indices trained on Taiwanese textbooks [@sung2016crie], and recent work applies
pretrained transformers with feature fusion [@yang2025chinese]. Both model more
than vocabulary coverage and will outperform a threshold on many tasks.

`hsk30` is deliberately not in that tradition. It is a transparent, deterministic
function of an official published standard, auditable line by line in a way a
classifier is not, and stable across runs and versions. Where a learned model
answers *how hard does this look*, `hsk30` answers *what does this standard say*
— a different and narrower question, but the one that placement, curriculum
mapping and examination alignment actually turn on.

The closest adjacent resource is `HSKBenchmark` [@yang2026hskbenchmark], which
evaluates models across HSK levels 3 to 6. It draws its grammar inventory from
the 2021 standard while building its corpus from textbook series aligned to
earlier outlines, and does not state which document defines its levels — an
instance of precisely the ambiguity this package makes visible.

# Quality control

The library carries 39 tests, run on every push against Python 3.9 through 3.13,
executable under `pytest` or as a plain script with no test framework installed.
The syllabus extraction self-validates: per-level entry counts are asserted
against the totals published in the source document, and the build fails if they
diverge. A separate script re-derives every figure quoted in the accompanying
papers from live computation, so published numbers and shipped data cannot drift
apart silently.

# AI usage disclosure

Generative AI was used substantially in this project and is disclosed here in
full, as JOSS requires.

**Tools.** Anthropic's Claude, used interactively throughout development.

**Where applied.** Three distinct places. (1) The 132-text graded-reader corpus
was authored with LLM assistance; this is disclosed in the corpus datasheet and
in the limitations of the accompanying research papers, and it is the reason the
corpus is described as pedagogically constrained rather than as a sample of
natural Chinese. (2) The library implementation, test suite and extraction
scripts were written with AI assistance. (3) The papers, including this one, were
drafted with AI assistance.

**Nature of the assistance.** Implementation and drafting, directed by the
author. The problem framing is the author's: the observation that "HSK 3.0" names
two documents rather than one, and the decision to make the grader record which
document it used, originated in his own product work and are the reason the
package exists. The design decisions that shape it — grading characters rather
than words after word-level coverage proved unreachable, refusing a runtime
dependency, shipping official inventories rather than derived ones, and
self-validating extractions against published totals — were made and are
defended by the author.

**Human review.** All AI-assisted output was reviewed by the author, and that
review has repeatedly been the binding check rather than a formality. Reading the
compiled PDF is what caught that it had been built in anonymised review mode;
reading the paper is what caught a stray editing marker; and a claim that this
work's benchmark was the first of its kind was withdrawn after the author's
scrutiny surfaced earlier work [@yang2026hskbenchmark]. Automated checks passed
in every one of those cases.

# Acknowledgements

No funding or institutional support was involved.

# References
