# Proposal: a BEA 2027 shared task on difficulty-controlled Chinese

**Status:** draft, not yet submitted. Pitch target is the BEA Shared Task
Chairs; for BEA 2026 those were Victoria Yaneva and Bashar Alhafni, under
General Chair Ekaterina Kochmar. Verify the 2027 committee before sending.

## Why this task, and why now

BEA 2026 ran a shared task on **Vocabulary Difficulty Prediction for English
Learners** (Felice and Skidmore, British Council), covering three L1s —
Spanish, German and Mandarin — and drawing 23 teams. The direction was
*Mandarin speakers learning English*. The reverse direction has no equivalent.

Meanwhile Chinese has just undergone a standards migration with no analogue in
English. Two official documents are both called "HSK 3.0": the GF0025-2021
national grading standard and the examination syllabus in force since July
2026. They assign different levels to 41.5% of the words and 40.7% of the
characters they share, and grading real texts against one rather than the other
changes the level of roughly half of them. Chinese language education is
currently calibrated to a moving and widely misidentified target, and that is a
tractable, well-posed, publicly-documented problem.

Related infrastructure exists for other languages and does not cover Chinese.
UniversalCEFR spans 13 languages against CEFR; Chinese is not among them, and
would need HSK-to-CEFR grounding that this work supplies.

## Proposed tracks

### Track A — Controlled-difficulty generation

Given a topic, a target length and a target HSK level, generate a coherent
passage a learner at that level can read.

Scoring is deterministic and needs no judge model: a passage passes if 95% of
its characters fall within the target level of the official graded character
inventory. This is the `hsk30` grader used as a metric, in the way a compiler
is a metric for generated code. Reference implementation, task set and
evaluation harness already exist as WriteToLevel.

Established reference points:

| System | Level accuracy |
| --- | ---: |
| deepseek-chat (temp 0) | 66.7% |
| Human authors writing to target | 61.8% |
| Corpus retrieval (no model) | 59.3% |

The aggregate understates the difficulty. Per level, `deepseek-chat` scores
16 / 24 / 72 / 88 / 100 / 100 across HSK 1–6: the constraint is near-vacuous at
the top and bites hard at the bottom. **HSK 1–2 is the discriminating region**,
and a task weighted there would not be saturated on day one.

This mirrors the TSAR 2025 shared task on readability-controlled simplification
(CEFR, English), and extends it to a non-alphabetic writing system where the
constraint is a character inventory rather than a word list.

### Track B — Out-of-list level prediction

Given a word absent from a graded list, predict the level it belongs at.

This is not a lookup. The 2025 syllabus introduced 1,222 words not present in
the 2021 standard, each with an official level assignment: real gold labels,
assigned by the standard's authors, for words a system cannot have memorised
from the earlier list. It is the direct Chinese counterpart of BEA 2026's
vocabulary difficulty prediction, with the migration supplying a natural
held-out split.

It is also useful beyond the task. Anyone extending graded material past the
official lists — textbook authors, app developers, test writers — has to make
exactly this judgement, currently by hand.

## What is already in place

- Graded lists for all three documents, MIT, `pip install hsk30`
- An aligned 102-text corpus with per-word pinyin and gloss, CC BY 4.0, plus a
  disjoint 30-text held-out split
- 150 generation tasks, a deterministic scorer, and three reference systems
- A validated extraction of the 2025 syllabus, whose per-level counts reproduce
  the official totals exactly
- Reproducibility harness: every published figure regenerates from the data

Nothing here needs to be built before a call goes out.

## What is needed

**Co-organisers**, particularly from groups already working on
readability-controlled generation and multilingual proficiency assessment. The
Chinese expertise and infrastructure are in place; experience running a BEA
shared task and reach into the participant community are not.

**A second annotator** for any human-judgement component, and ideally
practising Chinese teachers to validate that measured levels match classroom
intuition.

## Open questions for co-organisers

1. Weight Track A toward HSK 1–2, or report per-level and let the curve speak?
2. Should Track A score coherence at all? It is excluded now because judging it
   needs a human or a model and would make results unreproducible.
3. Traditional characters: convert and grade, or exclude?
4. Is Track B better framed as regression on a difficulty scale, as in BEA 2026,
   than as classification into levels?
