# Datasheet — HSK 3.0 Graded Reader Corpus

Following Gebru et al., *Datasheets for Datasets* (2021).

**Version** 1.1 · **Released** 2026 · **Licence** CC BY 4.0 · **Size** 102 texts,
1,185 sentences, 8,682 word tokens, 14,417 graded characters, plus a disjoint
30-text held-out split

---

## Motivation

**Why was this created?** Aligned Chinese graded-reader corpora are scarce.
Existing collections are either unaligned plain text, locked inside commercial
apps, or graded against HSK 2.0. This
corpus provides word-aligned text with pinyin and gloss at six difficulty
levels, so that readability methods can be developed and compared against
material written for actual learners.

**Who created it?** Alvaro Serrano, as the reading corpus for
[pinyora.com](https://pinyora.com), a free Mandarin reading site. No external
funding.

## Composition

Two files, identical in schema:

- `hsk30_graded_readers.jsonl` — the main corpus, 102 texts on six shelves
- `hsk30_heldout.jsonl` — 30 texts from a separate content stream, disjoint by
  id, held out so results can be replicated on material that played no part in
  establishing them

Each line is one text:

| Field | Description |
| --- | --- |
| `id` | Stable identifier (`n1`, `b16`, `a8`, …) |
| `shelf` | `newbie`, `beginner`, `intermediate`, `upper`, `advanced`, `native` |
| `shelf_index` | 1–6, the shelf's difficulty rank |
| `title` | `{hz, py, en}` |
| `description` | One-line English summary |
| `text` | The full passage, Simplified Chinese |
| `sentences` | List of `{hz, en, words[]}`; each word is `{hz, py, en}` |
| `n_sentences`, `n_chars` | Counts |

Texts per shelf: 22 / 22 / 22 / 12 / 12 / 12. Mean length rises from 49 to
about 290 characters across the shelves.

**Are difficulty labels included?** Deliberately not. A level is a function of
the text and the standard, both of which can change; baking labels in would let
a stale copy of the dataset contradict the grader. Compute them with the
[`hsk30`](https://github.com/harukicoder/hsk30) library:

```python
import hsk30, json
row = json.loads(open("hsk30_graded_readers.jsonl", encoding="utf-8").readline())
tokens = [w for s in row["sentences"] for w in s["words"]]
print(hsk30.grade_tokens(tokens).label)
```

`reference_grades.json` records the levels produced by the original JavaScript
implementation, for reproducing figures published before the accent-aware
proper-noun fix. It is provenance, not ground truth.

**Is anything missing?** There is no audio, no traditional-character variant
(convert with OpenCC), and no per-sentence grammar annotation. Segmentation is
authored rather than produced by a segmenter, so tokens sometimes group
phrases (我的, 七点) that a segmenter would split.

**Does it contain personal or offensive content?** No. Texts describe everyday
situations — school, food, weather, festivals, travel. Named characters are
invented. There is no personal data about real people.

## Collection process

**How was the text produced?** The passages were **drafted with the assistance
of large language models and then reviewed, edited, re-levelled and in several
cases rewritten by the author.** This is disclosed plainly because it bears on
how the corpus should be used: it is *pedagogical* material written to a level
target, not naturally occurring Chinese, and it should not be treated as a
sample of native usage. Editorial work included checking every gloss, fixing
level violations found by the grader, and rewriting texts whose difficulty came
from an incidental hard word rather than from their subject.

**How were the shelves assigned?** By the author at writing time, then audited
against the HSK 3.0 character standard. The audit moved no text between
shelves; it changed four texts whose measured level was driven by a single
avoidable word. Documented cases:

- `n10` graded HSK 4 because of 豆豆, **the dog's name** — which motivated
  excluding proper nouns from grading rather than editing the story.
- `c1` 乌鸦 (crow, ungraded) → 小鸟 (L2), moving it 7–9 → 3.
- `n9` 吉他 (7–9) / 弹 (L5) → 唱歌 (L1), moving it 5 → 2.
- `b16` dropped 蜡烛 (7–9), keeping 蛋糕, moving it 7–9 → 3.

Two known outliers were left in deliberately: `c2` (大熊猫, genuinely L5) and
`n11` (窗户, L4). In both, the hard word is what the text exists to teach.

**Known measurement caveat.** Human authors writing to an explicit level target
hit it only **61.8%** of the time across this corpus, overshooting at the easy
end (+1.23 levels on the newbie shelf) and undershooting at the hard end
(−0.75 on native). Shelf labels are therefore *bands*, not point claims. Use
the measured level for anything quantitative.

## Uses

**Intended.** Readability and difficulty-estimation research; evaluating
controlled-difficulty generation (see HSKBench); building and testing graded
reading tools; teaching material for HSK 1–6.

**Not appropriate.** As a sample of naturally occurring Chinese; for training a
general language model; for claims about native writing style or frequency
distributions. The texts are short, pedagogically constrained, and
LLM-assisted.

**Risk of a feedback loop.** Because the texts were LLM-assisted, a system
evaluated on how well it *matches this corpus* may be rewarded for resembling
its own training distribution. HSKBench avoids this by scoring generation
against the objective character standard rather than against these texts.

## Distribution and maintenance

Distributed with the `hsk30` repository and on HuggingFace under
**CC BY 4.0** — reuse and adaptation permitted with attribution. Maintained by
the author; corrections via GitHub issues. Regenerate from source with
`node scripts/export_corpus.js /path/to/InkPath`.

## Citation

```bibtex
@misc{serrano2026hsk30corpus,
  title  = {HSK 3.0 Graded Reader Corpus},
  author = {Serrano, Alvaro},
  year   = {2026},
  note   = {CC BY 4.0},
  url    = {https://github.com/harukicoder/hsk30}
}
```
