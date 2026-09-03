# hsk30

[![Paper](https://img.shields.io/badge/paper-zenodo.22239032-b31b1b.svg)](https://doi.org/10.5281/zenodo.22239032)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22234657.svg)](https://doi.org/10.5281/zenodo.22234657)
[![PyPI](https://img.shields.io/pypi/v/hsk30.svg)](https://pypi.org/project/hsk30/)
[![tests](https://github.com/harukicoder/hsk30/actions/workflows/tests.yml/badge.svg)](https://github.com/harukicoder/hsk30/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Grade Chinese text against HSK — against **either** document that gets called
"HSK 3.0", and it will tell you which one it used.

```bash
pip install hsk30
```

```python
import hsk30

hsk30.grade("我每天早上七点起床，然后去公园跑步。").label
# '3'      ← graded against the 2026 examination syllabus, the default

hsk30.grade("...", standard="2021").label
# the GF0025-2021 national grading standard instead
```

> **"HSK 3.0" is two different documents, and the choice changes the answer.**
> They disagree on **41.5%** of shared vocabulary and **40.7%** of shared
> characters. Regrading 102 authentic graded readers against one rather than
> the other changes the level of **48% of them**, almost always upward. This
> library defaults to the examination syllabus in force since July 2026 and
> records `profile.standard` on every result. See [Versions](#versions).

```bash
$ hsk30 "我每天早上七点起床，然后去公园跑步。" --curve --target 2
HSK 3  (16 characters, 0 ungraded)
  HSK 1      68.8%  ############################
  HSK 2      87.5%  ###################################
  HSK 3     100.0%  ########################################
  target HSK 2: misses the 95% bar (12.5% above target)
    步  HSK 3      6.2%  <- over budget on its own
    每  HSK 3      6.2%  <- over budget on its own
```

No dependencies. Python 3.9+.

## Why this exists

Most Chinese-learning tools report an "HSK 3.0 level" without saying which
document produced it. There are two, published four years apart:

| Comparison | Shared words | Same level | Moved |
| --- | ---: | ---: | ---: |
| HSK 2.0 → GF0025-2021 | 4,482 | 814 | 3,668 (81.8%) |
| HSK 2.0 → 2025 syllabus | 4,802 | 2,349 | 2,453 (51.1%) |
| **GF0025-2021 → 2025 syllabus** | **9,674** | **5,662** | **4,012 (41.5%)** |

Judged against the 2021 standard, HSK 2.0 looks almost entirely regraded.
Judged against the examination syllabus, barely half moved. The syllabus is
markedly more conservative, and it is the document learners are actually tested
on.

Every figure in this README is produced by `python3 scripts/reproduce.py`.

## What it does

Answers one question: **what HSK level does a reader need to read this text?**
The answer is the level at which cumulative character coverage reaches 95% —
the point at which a reader can follow a passage and infer the rest.

```python
p = hsk30.grade("这项研究揭示了神经网络的内在缺陷。")
p.level        # 6
p.label        # '6'
p.chars        # 16
p.ungraded     # characters outside the 3,000
p.curve()      # cumulative coverage at every level
```

### Three decisions that matter

**Character-level, not word-level.** Word-level grading is unusable on
segmented Chinese. Real segmenters emit phrase tokens (我的, 七点, 蓝色) that
are not entries in any graded word list, pushing "unknown" past 95% at every
level and reporting ordinary beginner text as off-scale. HSK 3.0 grades 3,000
characters separately from its words precisely because the character inventory
is what gates reading.

**The official character list, not a derived one.** Deriving character levels
from the lowest-level word containing each character agrees with the 2021
official list on 2,962 of 2,969 characters — and gets the family terms wrong. 哥, 妈,
妹, 弟 are level-1 characters whose only listed words (哥哥, 妈妈) sit at
level 4. Also wrong: 王, 第, 零. This package ships the official list.

**Proper nouns are excluded when identifiable.** A reader does not need the
puppy's name in their vocabulary; it is glossed in place. Counting names as
difficulty graded a story called "My Puppy Doudou" at HSK 4 on a beginner
shelf, entirely on the strength of 豆豆. Detection needs pinyin, so it is
available through `grade_tokens`:

```python
hsk30.grade_tokens([
    {"hz": "我", "py": "wǒ"},
    {"hz": "李明。", "py": "Lǐ Míng"},   # excluded
]).chars   # 1
```

### Levels 7, 8 and 9 are one band

Neither document splits them — in the 2021 standard they share a single
5,599-word list and 1,200 characters. This package carries the band as level `7` and renders it
`"7-9"`. A vendor advertising an "HSK 8 word list" invented the split.

### Reading is not writing

HSK 3.0 grades characters twice: **认读字** (recognition, 3,088 — what gates
reading) and **书写字** (writing, 1,200 — what a learner must produce by hand).
The second is a strict subset of the first, on a different curve: 100 across
levels 1–2, then 150 per level, 500 across 7–9.

```python
p = hsk30.writing_profile("他在图书馆认真地准备考试。")
p.label      # '3'   — level needed for the part the curriculum covers
p.ceiling    # 0.417 — and it covers 42% of the text
p.outside    # 7 characters no HSK level asks you to hand-write
```

Read those two numbers together: *"HSK 3 handwriting for the part of this text
the curriculum covers, and it covers 42% of it."* The text reads at HSK 3.

**Why two numbers.** The obvious design is a single level from a 95% coverage
bar over the whole text. It fails completely: only 1,200 of the 3,088 graded
characters are writable, so a median text has ~60% of its characters in the
writing curriculum at all, and **every text in the corpus misses a 95% bar at
every level**. A metric returning the same answer for every input measures
nothing.

Restricting the denominator to the writable subset makes a level meaningful
again, and the ceiling carries the part that restriction drops. Either number
alone misleads — the level flatters the text, the ceiling reads as failure.

### Character budgets

Reaching a 95% bar means keeping the above-target share under 5%, so a single
character over that budget blocks the target on its own:

```python
share, offenders = hsk30.budget_violations(text, target=3)
```

This is how a short passage silently regresses when an otherwise harmless edit
repeats one hard character a fourth time.

### Grading collections

```python
shelf = hsk30.profile_shelf([hsk30.grade(t) for t in texts])
shelf.label        # median text — not the pooled figure
shelf.span_label   # 'HSK 2-3', the interquartile range
```

Reports the **median text**. Pooling every character in a shelf lets a handful
of hard texts speak for all of them: it reported "HSK 3" for a beginner shelf
on which 13 of 22 texts individually read at HSK 1–2, describing nothing
actually on the shelf.

## What's in this repository

| Path | Contents |
| --- | --- |
| `src/hsk30/` | The library and its six graded lists (MIT) |
| `corpus/` | 102 aligned graded readers + a 30-text held-out split (CC BY 4.0) |
| `benchmark/` | WriteToLevel — controlled-difficulty generation |
| `paper/` | The accompanying paper and its figures |
| `scripts/reproduce.py` | Recomputes every published figure |
| `scripts/extract_syllabus_2025.py` | Parses the official syllabus PDF |
| `corpus/syllabus2025/PROVENANCE.md` | Where the 2025 tables come from, and their rights position |

## WriteToLevel

Generating text *at* a level turns out to be much harder than grading it.
Human authors writing to an explicit target hit it **61.8%** of the time,
overshooting at the easy end and undershooting at the hard end. WriteToLevel scores
that task objectively — the grader is the metric, the way a compiler is the
metric for generated code. See [`benchmark/README.md`](https://github.com/harukicoder/hsk30/blob/main/benchmark/README.md).

## Versions

Three documents are routinely conflated, including by commercial HSK sites.
They are different, and it matters which one a tool grades against.

| `standard=` | Document | Date | Words | Characters |
| --- | --- | --- | ---: | ---: |
| `"2.0"` | HSK 2.0 exam lists | 2009–10 | 4,991 | — |
| `"2021"` | 《国际中文教育中文水平等级标准》 (GF0025-2021) | in force 1 Jul 2021 | 10,916 | 3,000 |
| `"2025"` *(default)* | 新版HSK考试大纲 | pub. Nov 2025, in force Jul 2026 | 10,896 | 3,088 |

The 2021 document is a national language standard (语言文字规范) from the
Ministry of Education and the State Language Commission. The 2025 document is
the examination syllabus from the Center for Language Education and Cooperation
(中外语言交流合作中心) and governs the test learners actually sit — which is why
it is the default.

HSK 2.0 graded no characters separately, so `characters("2.0")` raises.

**The 2025 lists are extracted from the official 406-page PDF** by
`scripts/extract_syllabus_2025.py`, which self-validates: parsed per-level entry
counts reproduce the published cumulative totals (300 / 500 / 1,000 / 2,000 /
3,600 / 5,400 / 11,000) exactly. Two notes from doing it — the syllabus numbers
11,000 *entries* but only 10,896 distinct words (homographs like 所/所2 get
their own rows), and it grades **3,088** recognition characters, not the 3,079
widely reported.

## Where to find it

| | |
| --- | --- |
| Package | [`pip install hsk30`](https://pypi.org/project/hsk30/) |
| Paper | [doi:10.5281/zenodo.22239032](https://doi.org/10.5281/zenodo.22239032) |
| Archived release | [doi:10.5281/zenodo.22234657](https://doi.org/10.5281/zenodo.22234657) |
| Corpus | [harukicoder/hsk30-graded-readers](https://huggingface.co/datasets/harukicoder/hsk30-graded-readers) on HuggingFace |
| Source | [github.com/harukicoder/hsk30](https://github.com/harukicoder/hsk30) |

## Data sources

| Source | Provides | Licence |
| --- | --- | --- |
| [ivankra/hsk30](https://github.com/ivankra/hsk30) | HSK 3.0 word and character lists | MIT |
| [drkameleon/complete-hsk-vocabulary](https://github.com/drkameleon/complete-hsk-vocabulary) | HSK 2.0 levels, pinyin, glosses | MIT |

Both are transcriptions of 《国际中文教育中文水平等级标准》. Regenerate the
shipped tables with `python3 scripts/gen_data.py` (needs network).

## Limitations

- **Simplified characters only.** Convert traditional text with OpenCC first.
- **Coverage is not comprehension.** 95% character coverage is a necessary
  condition for fluent reading, not a sufficient one; grammar, register and
  world knowledge are not modelled.
- **Proper-noun detection needs pinyin.** `grade()` on a bare string cannot
  identify names; pass them via `exclude=`, or use `grade_tokens()`.
- **CJK Extension A–F characters are treated as ungraded**, which is correct
  under the standard but means literary text scores off-scale readily.
- **Authored segmentation** in the corpus groups some phrases a segmenter
  would split.

## Development

```bash
git clone https://github.com/harukicoder/hsk30 && cd hsk30
pip install -e ".[dev]"
pytest                          # or: python3 tests/test_hsk30.py
python3 scripts/reproduce.py    # every figure in the paper
```

The library is a port of the implementation that runs
[pinyora.com](https://pinyora.com). It reproduces that implementation's output
on all 102 corpus texts exactly (`test_python_reproduces_the_javascript_reference_exactly`),
with one deliberate fix: the original's ASCII-only `^[A-Z]` proper-noun test
missed names romanised with an accented capital — Ōuzhōu, Ōuyà, Ā Q Zhèngzhuàn
— and since 欧 and 洲 are both HSK 7–9 characters, missing one place name moved
a text two levels. The legacy behaviour remains available as
`is_proper_noun_ascii`.

## Citation

Cite the paper:

```bibtex
@misc{serrano2026whichhsk,
  title     = {Which {HSK} 3.0? Two Official Documents, and Half of All
               Grading Decisions Change},
  author    = {Serrano, Alvaro},
  year      = {2026},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.22239032},
  note      = {Preprint}
}
```

Or the software and data specifically:

```bibtex
@software{serrano2026hsk30,
  title     = {hsk30: grading Chinese text against either document called HSK 3.0},
  author    = {Serrano, Alvaro},
  year      = {2026},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.22234657},
  url       = {https://doi.org/10.5281/zenodo.22234657}
}
```

The DOI above is the *concept* DOI: it always resolves to the latest version.
To cite this exact release, use `10.5281/zenodo.22234658`.

## Licence

MIT for the code and the derived level tables; **CC BY 4.0** for the corpus
(see `corpus/LICENSE`).
