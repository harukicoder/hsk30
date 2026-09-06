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
date: 6 September 2026
bibliography: paper.bib
---

# Summary

`hsk30` grades the difficulty of Chinese text against the official Chinese
proficiency standards, and records which standard it used. It answers the
question a teacher or materials designer asks constantly — *what level is this
text, and can a learner at level N read it?* — as a deterministic function of a
published inventory, with no learned parameters and no network access.

It ships validated machine-readable extractions of three documents: the HSK 2.0
word list, the national grading standard 《国际中文教育中文水平等级标准》
(GF0025-2021) [@moe2021standard], and the examination syllabus in force since
July 2026 [@clec2025syllabus], including its separate 1,200-character
handwriting inventory. It grades strings or pre-segmented tokens, reports
coverage curves rather than a single label, flags characters over a level
budget, converts and grades traditional-script input, and profiles a whole
corpus at once. It also distributes an aligned 102-text graded-reader corpus
under CC BY 4.0 and `WriteToLevel`, a difficulty-controlled generation benchmark
of 150 tasks in which the grader is the metric rather than the source of labels.

# Statement of need

Chinese reading material is levelled by HSK, and the tools that assign such
levels are almost all closed, hosted, and silent about their source: they report
that a text is "HSK 3.0 level 4" without saying which document produced the
number, what threshold was applied, or how the text was segmented. None of those
choices is neutral and none can be audited.

The specific problem this package solves is that "HSK 3.0" does not identify a
document. Two official publications carry the name, four years apart, and they
assign different levels to 41.5% of the vocabulary and 40.7% of the characters
they share; grading authentic graded readers against one rather than the other
changes the level of roughly half of them [@serrano2026whichhsk]. A level
reported without naming its source is not reproducible.

The ambiguity is not hypothetical. An audit of the five most-used open HSK 3.0
word lists finds four encoding the superseded 2021 standard rather than the
syllabus students now sit, only one naming the document it contains, and across
every pair of those four zero words assigned a different level — they are one
artifact under four names [@serrano2026audit]. Agreement between them
corroborates nothing. The package therefore ships a one-field convention for
declaring the source document inside a dataset, a registry of the five documents
it recognises, and a checker that tests the declaration against the data rather
than trusting it.

A second need is methodological. Judging whether a language model can write to a
target difficulty requires a metric that is not itself a model trained on
similar text, or the evaluation is circular [@imperial2023flesch;
@barayan2025analyzing]. Set membership in a published government inventory is
such a metric: checkable exactly, with no judge and no trained scorer.
`WriteToLevel` is built on that property and ships with the package, so metric
and benchmark cannot drift apart.

The package is dependency-free and runs offline against the standard library
alone. Its intended users include classroom teachers and small programmes, for
whom an install requiring a build toolchain, an account or an internet
connection is an install that does not happen.

# State of the field

Automatic readability assessment for Chinese is dominated by supervised
classification over engineered features: CRIE extracts eighty-two multilevel
indices trained on Taiwanese textbooks [@sung2016crie], and recent work applies
pretrained transformers with feature fusion [@yang2025chinese]. Both model more
than vocabulary coverage and will outperform a threshold on many tasks.

`hsk30` is deliberately not in that tradition. It is a deterministic function of
a published standard, auditable line by line in a way a classifier is not. Where
a learned model answers *how hard does this look*, `hsk30` answers *what does
this standard say* — narrower, but the question placement and examination
alignment actually turn on.

The closest adjacent resource is `HSKBenchmark` [@yang2026hskbenchmark], which
evaluates models across HSK levels 3 to 6. It draws its grammar inventory from
the 2021 standard while building its corpus from textbooks aligned to earlier
outlines, and does not state which document defines its levels — an instance of
precisely the ambiguity this package makes visible.

# Quality control

The library carries 44 tests, run on every push against Python 3.9 through
3.13, executable under `pytest` or as a plain script with no test framework
installed. The extractions self-validate: per-level counts are asserted against
the totals published in the source documents, and the build fails if they
diverge. This is not ceremony — filtering one inventory's starred levels loses
212 of its 496 entries and returns a plausible-looking 284, and only the
assertion makes that failure loud. A separate script re-derives every figure
quoted in the accompanying papers from live computation. Documented limits are
enforced in the data rather than in prose: traditional conversion is many-to-one,
so a traditional grade is an upper bound, and the 106 characters with more than
one preimage are counted in the header of the shipped conversion table.

# AI usage disclosure

Generative AI was used substantially in this project and is disclosed here in
full, as JOSS requires.

**Tools.** Anthropic's Claude, used interactively throughout development.

**Where applied.** Three places. (1) The 102-text graded-reader corpus was
authored with LLM assistance; this is disclosed in the corpus datasheet and in
the limitations of the accompanying papers, and is why the corpus is described
as pedagogically constrained rather than as a sample of natural Chinese. (2) The
library, tests and extraction scripts were written with AI assistance. (3) The
papers, including this one, were drafted with AI assistance.

**Nature of the assistance.** Implementation and drafting, directed by the
author. The problem framing is the author's: the observation that "HSK 3.0"
names two documents rather than one, and the decision to make the grader record
which it used, originated in his own product work and are the reason the package
exists. The design decisions that shape it — grading characters rather than
words after word-level coverage proved unreachable, refusing a runtime
dependency, shipping official inventories rather than derived ones, and
self-validating extractions against published totals — were made and are
defended by the author.

**Human review.** All AI-assisted output was reviewed by the author, and that
review has repeatedly been the binding check rather than a formality. A claim
that this benchmark was the first of its kind was withdrawn after his scrutiny
surfaced earlier work [@yang2026hskbenchmark], and a normalisation bug that
silently dropped 61 reduplicated entries from one word list was found, fixed,
and disclosed as a correction to a published preprint. Automated checks passed
in both cases.

# Acknowledgements

No funding or institutional support was involved.

# References
