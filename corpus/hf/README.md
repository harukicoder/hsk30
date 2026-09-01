---
license: cc-by-4.0
language:
  - zh
  - en
pretty_name: HSK 3.0 Graded Reader Corpus
size_categories:
  - n<1K
task_categories:
  - text-classification
  - text-generation
tags:
  - chinese
  - mandarin
  - hsk
  - readability
  - graded-reader
  - language-learning
  - second-language-acquisition
  - parallel-corpus
configs:
  - config_name: main
    data_files: hsk30_graded_readers.jsonl
  - config_name: heldout
    data_files: hsk30_heldout.jsonl
---

# HSK 3.0 Graded Reader Corpus

132 word-aligned Chinese graded readers with per-word pinyin and English gloss,
arranged on six difficulty shelves: **102 texts** in the main split and a
**disjoint 30-text held-out split**.

Aligned Chinese graded-reader corpora are scarce. Existing collections are
unaligned plain text, locked inside commercial apps, or graded against HSK 2.0,
which has been superseded twice.

## Loading

```python
from datasets import load_dataset

ds = load_dataset("harukicoder/hsk30-graded-readers", "main")
held = load_dataset("harukicoder/hsk30-graded-readers", "heldout")
```

Each record has `id`, `shelf`, `title` (hanzi / pinyin / English), `text`, and
`sentences` — each sentence carrying its own English translation and a list of
word tokens with `hz`, `py` and `en`.

## Difficulty labels are deliberately not included

A level is a function of the text *and the standard*, and "HSK 3.0" names two
different official documents that disagree on 41.5% of shared vocabulary.
Baking labels in would let a stale copy of this dataset contradict the grader.
Compute them instead:

```python
import hsk30                      # pip install hsk30

tokens = [w for s in record["sentences"] for w in s["words"]]
hsk30.grade_tokens(tokens).label              # 2026 exam syllabus
hsk30.grade_tokens(tokens, standard="2021").label   # 2021 grading standard
```

Roughly half of these texts grade differently under the two documents.

## Provenance, stated plainly

The passages were **drafted with large-language-model assistance and then
reviewed, edited, re-levelled and in several cases rewritten by the author.**
They are pedagogical material written to a level target — not naturally
occurring Chinese — and should not be used as a sample of native usage, or to
train a general language model.

Because they are LLM-assisted, a system evaluated on how well it *matches* this
corpus may be rewarded for resembling its own training distribution. The
accompanying benchmark avoids this by scoring against the official character
standard rather than against these texts.

Human authors writing to an explicit level target hit it only **61.8%** of the
time across this corpus, overshooting on easy material and undershooting on
hard. Treat the shelf labels as bands, not point claims.

Full datasheet (Gebru et al. format): `DATASHEET.md`, alongside this file.

## Related

- **Grader:** [`pip install hsk30`](https://pypi.org/project/hsk30/) — grades text
  against either HSK 3.0 document
- **Archived release with DOI:** [10.5281/zenodo.22234657](https://doi.org/10.5281/zenodo.22234657)
- **Source, benchmark and paper:** [github.com/harukicoder/hsk30](https://github.com/harukicoder/hsk30)

## Citation

```bibtex
@dataset{serrano2026hsk30corpus,
  title     = {HSK 3.0 Graded Reader Corpus},
  author    = {Serrano, Alvaro},
  year      = {2026},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.22234657},
  note      = {CC BY 4.0}
}
```
