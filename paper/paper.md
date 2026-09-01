# Which HSK 3.0? Two Official Documents, and Half of All Grading Decisions Change

**Alvaro Serrano**
*Independent researcher*

---

> **DRAFT — for the author's review.**
> Every quantitative claim is produced by `scripts/reproduce.py` and reproduces
> from the shipped data. References are verified as of September 2026 except
> where marked ⚠.

---

## Abstract

"HSK 3.0" names two different official documents. 《国际中文教育中文水平等级标准》
(GF0025-2021) is a national grading standard in force since 1 July 2021; the
新版HSK考试大纲 is the examination syllabus published in November 2025 and in
force since July 2026. They are widely conflated — by learners, by commercial
learning platforms, and by the tooling both rely on. We show the conflation is
consequential. The two documents assign different levels to **41.5% of the
10,916 and 10,896 words they respectively grade**, and to **40.7% of the 2,945
characters they share**. Grading a corpus of 102 authentic graded readers
against one rather than the other changes the assigned level of **48% of
texts**, almost always upward, and shifts five of six shelf medians by a full
level. Measured against HSK 2.0, the two disagree about their own predecessor:
81.8% of jointly graded words moved under the 2021 standard against 51.1% under
the 2025 syllabus. We contribute a validated extraction of the 2025 syllabus
(previously available only as a 406-page PDF), whose per-level counts reproduce
the official totals exactly; an open, tested, dependency-free library that
grades text against either document and reports which; an aligned 102-text
graded-reader corpus; and HSKBench, a controlled-difficulty generation
benchmark in which the grader is the metric rather than the source of labels.
Human authors writing to an explicit level target hit it 61.8% of the time.

## 1 Introduction

Graded reading material is the backbone of second-language literacy
instruction, and grading it requires answering a narrow question: what does a
reader need to know to read this text? For Chinese, the answer has been
anchored for two decades to the HSK vocabulary lists.

That anchor moved, and it is not obvious *to what*. Practitioners speak of
"HSK 3.0" as a single thing. It is not. A national grading standard was issued
in 2021 and an examination syllabus in 2025, four years apart, with different
word lists, different character inventories and different level boundaries.
Popular reference sites quote one document's level counts beside the other's
vocabulary; tools report "HSK 3.0" levels without saying which document
produced them.

We show this is not a pedantic distinction. Nearly half of real texts receive a
different level depending on which document is used, and the disagreement runs
in a consistent direction. A learner placed by a tool calibrated to the 2021
standard is being placed against a document that is not the examination they
will sit.

Contributions:

1. **A validated extraction of the 2025 examination syllabus** (§3). It is
   distributed only as a 406-page PDF. Our per-level entry counts reproduce the
   official cumulative totals exactly (300 / 500 / 1,000 / 2,000 / 3,600 /
   5,400 / 11,000), and we find it grades **3,088** recognition characters,
   correcting the 3,079 widely reported by secondary sources.
2. **A quantification of how far the documents disagree** (§4), pairwise across
   all three reference lists, for words and for characters. The syllabus's own
   development paper reports overlap but not level change; we distinguish the
   two, and show that high overlap coexists with high disagreement.
3. **A measurement of what that costs in practice** (§5): 48% of texts in an
   authentic graded-reader corpus change level.
4. **A character-level grading method and library** (§6) that grades against
   either document and records which.
5. **A corpus and a benchmark** (§7, §8), the latter measuring
   difficulty-*controlled generation*, on which human authors score 61.8%.

## 2 Background

### 2.1 Three documents

| Document | Date | Nature | Words |
| --- | --- | --- | ---: |
| HSK 2.0 examination lists | 2009–10 | Exam vocabulary, six levels | 4,991 |
| 《国际中文教育中文水平等级标准》 (GF0025-2021) | in force 1 Jul 2021 | National language standard | 10,916 |
| 新版HSK考试大纲 (HSK 3.0 exam syllabus) | pub. Nov 2025, in force Jul 2026 | The examination, 406 pp | 10,896 |

**Table 1: What "HSK 3.0" can mean.**

The 2021 standard is a 语言文字规范 issued by the Ministry of Education and the
State Language Commission, covering syllables, characters, vocabulary and
grammar across three levels and nine bands. It is the document with public
machine-readable transcriptions, and therefore the one most existing tooling
uses — including, until this work, our own.

The 2025 syllabus is issued by the Center for Language Education and
Cooperation (中外语言交流合作中心) and governs the examination itself.

Both grade characters separately from words, which matters: the character
inventory is what gates reading (§6.1). Levels 7, 8 and 9 are a single
undifferentiated band in both; tools advertising an "HSK 8 word list" have
invented a split neither document makes.

### 2.2 Coverage thresholds

Hu and Nation (2000) found that around 98% coverage of running words was needed
for adequate unassisted comprehension. Laufer and Ravenhorst-Kalovski (2010)
proposed two thresholds: an optimal 98% and a **minimal 95%**, at which
comprehension is adequate *with support*. Graded readers are read with support
— glosses, a teacher, a dictionary — so we adopt 95% as the default and expose
it as a parameter. The 98% figure has since been partially challenged: Kremmel
et al. (2023) could not fully replicate it in a different population, and the
original regression rested on 66 participants. We treat 95% as a defensible
default, not a settled constant.

Note that this literature measures coverage over *words*, in English. We apply
the threshold to Chinese characters for the reasons in §6.1; that transfer is a
principled assumption, not a result.

## 3 Extracting the 2025 syllabus

The syllabus is published as a 406-page PDF with a genuine text layer, so
extraction is parsing rather than OCR. Vocabulary occupies pp. 79–354 as rows
of `序号 等级 词语 拼音 词性`; recognition characters (认读字) occupy
pp. 356–376, numbered per level.

Two details are easy to get wrong.

**The level field carries more than a level.** A row reading `1（4）` means the
word is introduced at level 1 and has a further sense or part of speech graded
at level 4. We take the primary level — when a learner first meets the word —
and retain the secondary levels.

**The published totals count entries, not words.** The syllabus numbers 11,000
entries, but homographs graded at two levels appear as separate rows (所 / 所2).
These collapse to **10,896 distinct words**, of which 74 are graded at more than
one level; we keep the lower.

Validation is exact: parsed entry counts per level reproduce the official
cumulative figures (300 / 500 / 1,000 / 2,000 / 3,600 / 5,400 / 11,000) with no
discrepancy. For characters, each level's parsed count equals that level's
maximum item index (246, 125, 284, 441, 431, 413, 1,148) with no cross-level
duplicates, giving **3,088** recognition characters. Secondary sources widely
report 3,079; we believe that figure to be incorrect.

## 4 How far the documents disagree

| Comparison | Shared words | Same level | Moved |
| --- | ---: | ---: | ---: |
| HSK 2.0 → GF0025-2021 | 4,482 | 814 | **3,668 (81.8%)** |
| HSK 2.0 → 2025 syllabus | 4,802 | 2,349 | **2,453 (51.1%)** |
| GF0025-2021 → 2025 syllabus | 9,674 | 5,662 | **4,012 (41.5%)** |

**Table 2: Pairwise level agreement.**

**Membership is not agreement.** The syllabus's developers report a 99.2%
vocabulary overlap rate with HSK 2.0 and describe the revision as optimisation
rather than replacement (Feng et al., 2026). Both characterisations concern
*membership* — whether a word appears at all. Our membership figures are lower
(96.2% of our HSK 2.0 list appears in the syllabus, 89.8% in the 2021
standard), plausibly because our HSK 2.0 list is a public reconstruction of
4,991 words rather than the official 5,000-word 词汇大纲, and because the
published overlap figure's computation is not stated. We do not dispute it.
The point is that a high overlap rate and a high level-disagreement rate are
compatible, and only the second determines whether a text is graded correctly.
The words are largely the same words; they are not at the same levels.

Three further findings follow.

**The two "HSK 3.0" documents disagree with each other on 41.5% of shared
vocabulary.** This is the central result. They are not drafts of one another;
they are separate gradings.

**They also disagree about their predecessor.** Judged against the 2021
standard, HSK 2.0 looks almost entirely regraded (81.8% moved). Judged against
the examination syllabus, barely half moved (51.1%). The syllabus is markedly
more conservative — closer to HSK 2.0 than the standard is. A practitioner who
read "81.8% of HSK vocabulary changed level" and acted on it would have
substantially overestimated the disruption to the actual examination.

**Characters diverge similarly.** The 2021 standard grades exactly 3,000
characters (300 per level 1–6, 1,200 at 7–9); the syllabus grades 3,088 with a
markedly uneven distribution (246 / 125 / 284 / 441 / 431 / 413 / 1,148). Of the
2,945 characters both grade, **1,200 (40.7%) sit at different levels**; 55 are
unique to the standard and 143 to the syllabus.

For completeness, within the HSK 2.0 → 2021 comparison the instability is
concentrated above the beginner band: 91% of HSK 2.0 level-1 words keep their
level, against 35% at level 2 and 11–23% from level 3 upward. The beginner
foundation is stable under every comparison, which may explain why the scale of
the change has attracted little attention — the material people inspect first
is the material that barely moved.

## 5 What it costs in practice

Pairwise list agreement is suggestive; what matters is whether real texts grade
differently. We regraded all 102 texts of our corpus (§7) under both documents,
holding the method, threshold and proper-noun policy constant so that the
document is the only variable.

| | Texts |
| --- | ---: |
| Unchanged | 53 (52.0%) |
| **Changed** | **49 (48.0%)** |
|   … harder under the syllabus | 43 |
|   … easier under the syllabus | 6 |

**Table 3: Regrading 102 texts, 2021 standard → 2025 syllabus.**

Shifts are almost all a single level (42 texts +1, one +2, six −1). The effect
at shelf level is systematic rather than noisy:

| Shelf | 2021 standard | 2025 syllabus |
| --- | :--: | :--: |
| newbie | HSK 2 | HSK 3 |
| beginner | HSK 2 | HSK 3 |
| intermediate | HSK 3 | HSK 4 |
| upper | HSK 4 | HSK 5 |
| advanced | HSK 4 | HSK 5 |
| native | HSK 5 | HSK 5 |

**Table 4: Median measured level per shelf.** Five of six shift by a full level.

The direction is consistent, and the mechanism is simple. The syllabus grades
**371 characters at levels 1–2 combined, against the 2021 standard's 600** — a
beginner inventory 38% smaller. A text that reaches 95% coverage within 600
characters frequently cannot reach it within 371, so it lands a level higher.

This is the *same fact* the syllabus's developers describe as "significantly
reducing the vocabulary difficulty of the entry stage" (显著降低了入门阶段的
词汇难度; Feng et al., 2026), viewed from the other side. Less is demanded of a
beginning learner, which is a pedagogical improvement; the arithmetic
consequence is that beginner material grades higher. Both statements are true,
and a tool that reports levels needs to model the second while its users read
about the first.

The practical consequence is that a placement or material-selection decision
made with a tool calibrated to the 2021 standard will, about half the time,
disagree with the same decision made against the examination the learner sits.
**Any tool reporting an "HSK 3.0 level" should state which document it used.**
Ours records it on every result.

## 6 Method

### 6.1 Character-level, not word-level

Word-level grading fails on segmented Chinese for a mundane reason: segmenters
emit tokens absent from any graded list. Phrase tokens such as 我的, 七点 and
蓝色 are natural segmentation output but not list entries, so the "unknown"
share exceeds 95% at every level and ordinary beginner text grades as
off-scale. Both documents' separate character gradings resolve this, and
reflect a fact about Chinese: the character inventory, not the word inventory,
gates reading.

### 6.2 The official character list, not a derived one

Deriving a character's level from the lowest-level word containing it agrees
with the 2021 standard's official list on 2,962 of 2,969 derivable characters —
and misgrades seven: 哥, 妈, 妹, 弟, 王, 第, 零. The failure is systematic. 哥,
妈, 妹 and 弟 are level-1 characters whose only listed words are the
reduplicated 哥哥 and 妈妈, graded at level 4. Derivation therefore misgrades
precisely the vocabulary a beginner meets first. We ship the official lists.

### 6.3 Proper nouns

Names should not count towards difficulty: a reader does not need a character's
name in productive vocabulary, because it is glossed in place. In our corpus a
text titled *My Puppy Doudou* graded two levels high entirely on 豆豆, the dog's
name.

Proper nouns are romanised with a leading capital, making them detectable where
pinyin is available. One practical trap: an ASCII `^[A-Z]` test silently fails
on accented capitals — Ōuzhōu (欧洲), Ōuyà (欧亚), Ā Q Zhèngzhuàn (阿Q正传).
Since 欧 and 洲 are both advanced-band characters, missing one place name moved
a text two levels. Our implementation folds to NFD; the legacy behaviour is
retained so earlier figures remain reproducible.

Detection requires pinyin, so the exclusion is available for annotated text and
not bare strings — a limitation, not a design choice.

### 6.4 Thresholds and character budgets

A text's level is the lowest level at which cumulative character coverage
reaches the threshold. Characters outside the graded inventory count in the
denominator but never accumulate, so off-standard text correctly grades beyond
the scale.

One consequence is not obvious to authors: reaching a 95% bar means holding the
above-target share below 5%, so **any single character exceeding that budget
blocks the target alone**. In a 75-character passage a fourth repetition of one
advanced character suffices. We observed exactly this — a stylistic edit
repeating 糕 a fourth time silently regressed a text from level 3 to level 5.
The library reports offending characters and their shares.

### 6.5 Grading collections

Pooling a shelf's characters lets a few hard texts speak for all: pooling
reported "HSK 3" for a shelf on which 16 of 22 texts individually read at
HSK 1–2. We report the **median text**, and the interquartile range rather than
a wider window — four misfiles stretched one shelf's middle-80% range to
"HSK 1–5", misinforming learners about the other eighteen texts.

## 7 The corpus

We release 102 word-aligned graded texts: 1,185 sentences, 8,682 tokens, 14,417
graded characters, on six shelves (22/22/22/12/12/12), mean length rising from
49 to about 290 characters. Every token carries hanzi, pinyin and gloss; every
sentence a translation.

The texts were **drafted with large-language-model assistance and then
reviewed, edited and re-levelled by the author**; the datasheet discloses this
fully. They are pedagogical material written to a level target, not naturally
occurring Chinese, and should not be used as a sample of native usage or to
train a general language model.

## 8 HSKBench

### 8.1 Why not level prediction

The obvious benchmark is level prediction. When gold labels come from the
grader under test, this measures only whether a model memorised a character
list: circular and uninformative.

We invert the relationship. **The grader is the metric, not the label.** The
task is generation: produce a coherent passage on a topic, at a length,
readable at a target level. Scoring runs the grader over the output as a
compiler is run over generated code — deterministic, no judge model, no API.

### 8.2 Task and metrics

150 tasks: six target levels × 25 topics, five topics held out from the
corpus's domains. Primary metric is **level accuracy**, the share of outputs
whose measured level does not exceed the target. We also report mean signed
error (separating *too hard* from *too easy*, which behave differently), length
compliance, and single-character budget violations. Unanswered tasks score as
failures. Coherence is excluded from the automatic score: judging it needs a
human or a model and would make results unreproducible; the length constraint
blocks the degenerate strategy of emitting a few easy characters.

### 8.3 A human reference point

The corpus texts were each written to a shelf with a nominal target, so human
authors can be scored on the same task.

| System | Level accuracy | Mean signed error |
| --- | ---: | ---: |
| deepseek-chat (temp 0) | **66.7%** | +0.24 |
| Human authors | 61.8% | +0.27 |
| Corpus retrieval (no model) | 59.3% | +0.27 |

**Table 5: Overall results.** All three cluster within seven points, and all
three overshoot on average.

Human accuracy fails *directionally*: authors overshoot by 1.23 levels on the
easiest shelf and undershoot by 0.75 on the hardest, regressing toward middle
difficulty regardless of instruction. Writing to a level target is a genuinely
hard control problem for people — the practical argument for an objective
grader in the authoring loop, and what makes the benchmark non-trivial.

### 8.4 The aggregate score is misleading

The overall figures in Table 5 hide the result that matters. Broken down by
target level, `deepseek-chat` does not degrade gracefully — it inverts.

| Target | HSK 1 | HSK 2 | HSK 3 | HSK 4 | HSK 5 | HSK 6 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Accuracy | 16% | 24% | 72% | 88% | **100%** | **100%** |
| Signed error | +1.56 | +0.92 | +0.40 | −0.16 | −0.72 | −0.56 |

**Table 6: Level accuracy by target,** `deepseek-chat` at temperature 0.

Perfect scores at HSK 5–6 are not evidence of skill. At those levels the
constraint is nearly vacuous: almost any fluent Chinese passage satisfies a
95% coverage bar drawn against 2,600-plus characters, so the task reduces to
writing Chinese at all. The constraint only begins to bite at HSK 3, and by
HSK 1 the model fails **21 of 25 times**.

This is a limitation of the benchmark as much as a finding about the model, and
it has a direct consequence: **the aggregate score should not be reported
alone.** A system that answered only the top three levels would score 96%. We
report the per-level curve as the primary result and treat HSK 1–2 as the
discriminating region. Future versions should either reweight by level or drop
the levels where the constraint does not bind.

### 8.5 How generation fails

The failure at low levels is not one hard word. Across the 21 HSK 1 failures,
the median text carries **seven distinct above-target characters** totalling
15.2% of its characters — three times the 5% budget — while the *largest single*
offending character contributes a median of only 3.3%, comfortably under it.
Almost no failure has a single blocking character.

This is diffuse accumulation, and it distinguishes model failure from the
authoring failures in §6.4, where one repeated hard character (糕, 豆豆, 蜡烛)
carried the whole overshoot and could be fixed by one edit. A model missing
HSK 1 by 15% cannot be repaired by substituting a word; it has written at the
wrong level throughout.

The directional bias is shared with human authors, though: both overshoot on
easy targets and undershoot on hard ones, regressing toward middle difficulty
regardless of the instruction. Whatever produces that bias is not specific to
people.

Length compliance was 73.3% and single-character budget violations 2.7%.
Held-out topics scored 63.3% against 67.5% on corpus-adjacent topics, a gap
small enough to suggest the task is not topic-bound.

## 9 Related work

**Lexical coverage thresholds.** Hu and Nation (2000); Laufer and
Ravenhorst-Kalovski (2010), whose minimal 95% threshold we adopt; Kremmel et
al. (2023) on the limits of replication.

**The documents' own literature.** Feng et al. (2026), writing in
*International Chinese Language Education*, give the authoritative account of
the syllabus's development. It is qualitative: it reports a high overlap rate,
states that the syllabus was benchmarked against the 2021 standard (对标《等级
标准》), and describes new vocabulary as distributed across levels with orderly
continuity — but does not quantify how many words changed level, nor compare
the two documents word by word. We are not aware of a published quantitative
comparison of the kind in §4, in either language.

**The problem is live in deployed tools.** Commercial HSK text checkers grade
against "the new HSK 3.0 standard" without naming which document, and at least
one does so with greedy longest-match word segmentation over a bundled word
list — the approach §6.1 shows to be unusable for grading — while publishing no
data provenance or version. We name no vendor; the pattern is general.

**Chinese readability assessment.** The dominant approach is supervised
classification over engineered features. CRIE (Sung et al., 2016) extracts 82
multilevel features, trained on Taiwanese school textbooks; a CFL variant
classified 1,578 texts against expert CEFR judgements at 74.97% exact accuracy.
Recent work applies pretrained transformers with feature fusion (Yang et al.,
2025). Our method is deliberately not in this tradition: it is a transparent,
deterministic function of an official published standard, with no training data
and no learned parameters. It answers a narrower question — what a reader must
*know* — and is auditable in a way a classifier is not, which matters when a
placement decision must be explained to a learner.

**Difficulty-controlled generation.** Controlling generated readability is
active, largely in English and against CEFR: readability-controlled
simplification, CEFR-guided prompting with lexical constraints, RL approaches
optimising a readability reward. Our contribution is narrower and more
reproducible: because the target is an explicit character inventory rather than
a learned readability model, compliance is checkable exactly and without a
judge. HSKBench is, to our knowledge, the first difficulty-controlled
generation benchmark for Chinese grounded in an official national standard.

> ⚠ **Verification status.** Chinese-language searches were run and located the
> authoritative development paper (Feng et al., 2026), which is qualitative; no
> prior quantitative level-comparison was found. **CNKI full text was not
> reachable**, so a definitive novelty claim still requires a CNKI search of
> 《世界汉语教学》, 《语言教学与研究》 and 《国际中文教育》. Also confirm full
> metadata for the readability-controlled-generation references before citing
> them individually.

## 10 Limitations

- **Coverage is not comprehension.** 95% character coverage is necessary, not
  sufficient. Grammar, register, discourse and world knowledge are unmodelled;
  a syntactically complex text of level-1 characters grades as level 1.
- **The threshold is imported from word-level English research.** Establishing
  the character-level threshold empirically for L2 Chinese would be a
  contribution in itself.
- **Corpus scale.** 102 texts is adequate as a reference and validation set,
  inadequate for training. The regrading result (§5) rests on it, and would be
  strengthened by replication on a larger and independently authored corpus.
- **LLM-assisted corpus**, disclosed in the datasheet. HSKBench avoids the
  resulting feedback loop by scoring against the standard rather than the
  texts, but the corpus itself carries the caveat.
- **The transcriptions are not the documents.** The 2021 lists come from public
  MIT transcriptions of a scanned PDF; the 2025 lists from our own extraction,
  validated against published totals but not against an official machine-readable
  release, which does not exist.
- **Simplified characters only**; traditional text must be converted first.
- **Proper-noun exclusion needs pinyin**, and place names are a grey area:
  excluding 欧洲 (Europe) is defensible under the glossed-in-place principle and
  debatable under a vocabulary-knowledge one. The policy is a parameter.
- **Single annotator.** Shelf assignments and editorial decisions are the
  author's; there is no second annotator and no inter-annotator agreement.

## 11 Conclusion

"HSK 3.0" names two official documents that disagree on 41.5% of their shared
vocabulary and 40.7% of their shared characters, and choosing between them
changes the assigned level of nearly half of real texts, almost always upward.
The distinction is invisible in most current tooling, which reports "HSK 3.0"
levels without saying which document produced them. We release a validated
extraction of the examination syllabus, a tested grader that works against
either document and records which, an aligned corpus, and a benchmark measuring
the harder half of the problem — producing text at a level rather than
measuring it — on which human authors score 61.8%.

## Reproducibility

All figures: `python3 scripts/reproduce.py`. The 2021 lists regenerate from
upstream with `python3 scripts/gen_data.py --check`; the 2025 lists with
`python3 scripts/extract_syllabus_2025.py <pdf>`, which self-validates against
the syllabus's published totals. The library reproduces the original JavaScript
implementation on all 102 texts (`tests/test_hsk30.py`, 25 tests). Code MIT;
corpus CC BY 4.0.

## References

Verified as of September 2026 unless marked ⚠.

- Center for Language Education and Cooperation (中外语言交流合作中心) (2025).
  新版HSK考试大纲 [HSK Examination Syllabus]. Published November 2025, in force
  July 2026.
- Feng, L., Huang, L., Xie, N., Yu, T., Liu, S., Zhang, H., & Yun, T. (2026).
  《中文水平考试HSK考试大纲》（HSK 3.0）研制解读 [Interpretation of the
  development of the HSK 3.0 examination syllabus]. *International Chinese
  Language Education* (国际中文教育), 11(1).
- Hu, M., & Nation, P. (2000). Unknown vocabulary density and reading
  comprehension. *Reading in a Foreign Language*, 13(1), 403–430.
- Kremmel, B., et al. (2023). Unknown Vocabulary Density and Reading
  Comprehension: Replicating Hu and Nation (2000). *Language Learning*.
  doi:10.1111/lang.12622
- Laufer, B., & Ravenhorst-Kalovski, G. C. (2010). Lexical threshold revisited.
  *Reading in a Foreign Language*, 22(1), 15–30. ERIC EJ887873.
- Ministry of Education of the PRC & State Language Commission (2021).
  《国际中文教育中文水平等级标准》 (GF0025-2021). In force 1 July 2021.
- Sung, Y.-T., Chang, T.-H., et al. (2016). CRIE: An automated analyzer for
  Chinese texts. *Behavior Research Methods*. doi:10.3758/s13428-015-0649-1
- Yang, X., Yang, J., & Li, X. (2025). Chinese Automatic Readability Assessment
  Using Adaptive Pre-training and Linguistic Feature Fusion. *COLING 2025*.
  aclanthology.org/2025.coling-main.605

## Ethics and data statement

The corpus contains no personal data and describes invented characters in
everyday situations; its LLM-assisted authorship is disclosed in the datasheet.
Word and character lists derive from published national standards: the 2021
lists via MIT-licensed public transcriptions, the 2025 lists via our own
extraction from the official PDF. No human subjects were involved.

⚠ **Competing interests:** an intended application is a Chinese-learning website
operated by the author; disclose if the venue requires it.

⚠ **Redistribution of the 2025 lists** should be confirmed before release. The
extracted word–level mappings are factual data from a public government
standard, and the 2021 equivalents are already redistributed under MIT by third
parties, but the compilation right has not been assessed. The extraction script
is unambiguously distributable; the derived tables may warrant a licence review.
