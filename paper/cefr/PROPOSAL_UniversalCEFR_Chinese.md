# A first Chinese entry for UniversalCEFR

**Alvaro Serrano** · 3 September 2026 · alvaro.serrano.gp@gmail.com
ORCID 0009-0006-4701-9026

A feasibility note, written after establishing that my existing corpus does not
meet UniversalCEFR's inclusion criteria. It proposes a route that does, and is
explicit about which parts I cannot supply alone.

---

## 1. Why the obvious route fails

Chinese is normally placed on the CEFR through HSK. That route is unsound, and
measurably so: "HSK 3.0" names two official PRC documents that assign different
levels to 41.5% of the vocabulary they share, and grading the same texts against
one rather than the other moves 46.1% of them into a different CEFR band —
directionally, not noisily (`doi:10.5281/zenodo.22285474`).

The deeper problem is upstream of any correspondence table. **The PRC standard
does not align itself to the CEFR at all.** Every HSK-to-CEFR mapping in
circulation is folk knowledge, reconstructed by teachers and vendors. No amount
of care in choosing the table repairs a mapping that no issuing body has ever
endorsed.

## 2. Taiwan publishes precisely what the PRC does not

Chinese has a second proficiency ecosystem, and its structure is worth setting
beside the first.

| | PRC | Taiwan |
| --- | --- | --- |
| Standard | 《国际中文教育中文水平等级标准》 GF0025-2021 | 臺灣華語文能力基準 (TBCL), NAER |
| Examination | 新版HSK考试大纲 (2025) | TOCFL, SC-TOP |
| Standard-to-exam correspondence | **not published** | **published**; TOCFL score reports carry a TBCL column |
| CEFR alignment | **none** | **explicit**, by design |
| Word list | 11,092 words | 14,425 words, 3,100 characters, 496 grammar points |

TBCL was developed at Taiwan's National Academy for Educational Research over
six years and more than a hundred expert consultation meetings, and was designed
to align to both CEFR and ACTFL. TOCFL was built at National Taiwan Normal
University using the CEFR as its blueprint.

This is the substantive point of the proposal: **a Chinese CEFR label derived
through the Taiwan framework is one step from an official alignment; one derived
through HSK is two steps, and the second step is invented.**

That is now measured rather than argued. Labelling the same 102 texts through
each framework — both character-level, same 95% threshold, so only the
framework varies — disagrees on **95.1%** of them, and every one of the 97
disagreements runs the same way: the HSK route places the text higher, by one
band in 52 cases, two in 38 and three in 7. Switching to the compressed HSK
table halves the disagreement to 50.0%, which is the first quantitative support
I know of for the long-standing practitioner claim that HSK levels overstate
CEFR. A control rules out the obvious artifact: TOCFL's character inventory has
to be derived from its words, so the same derivation was applied to the PRC's
own words, where an official list exists to check against — it reproduces the
official grade on 102 of 102 texts. Reproducible from
`scripts/tocfl_compare.py`; details in `doi:10.5281/zenodo.22285474`.

## 3. Meeting the three inclusion criteria

**Permissive licence.** Text is drawn from sources under their own permissive
licences — Chinese Wikipedia and Wikinews (CC BY-SA), Tatoeba (CC BY). The TBCL
and TOCFL lists are *used to produce* labels and are never redistributed; NAER
asserts all rights reserved over the integrated system, and the proposal is
designed so that nothing of theirs ships. What ships is other people's
CC-licensed text plus labels, which are our own work. Anyone can obtain the
lists free from the official sites to reproduce the labelling.

**Human authorship.** Every candidate source is human-written. Nothing is
generated, and nothing from my existing LLM-assisted corpus enters this dataset.

**Expert-validated labels.** This is the criterion I cannot satisfy alone, and I
would rather say so than dress up an algorithmic projection as expert judgement.
The proposal is a two-stage design: bands assigned automatically from the
TBCL/TOCFL inventories, then a stratified sample independently rated by
CEFR-qualified Chinese assessors, with inter-annotator agreement reported and
the automatic labels accepted only where agreement holds. Without that second
stage this is derived data, not gold data, and should not be included.

## 4. Four things that will bite

**TBCL is not a clean 1:1 with CEFR.** It has seven levels, and in listening,
reading and writing its levels 1 and 2 sit *below* A1. Any mapping must handle
a floor that CEFR does not describe, rather than pretending the scales are
congruent. TOCFL's six levels map more directly but carry two novice bands
below A1 for the same reason.

**Traditional versus Simplified.** TBCL and TOCFL are Traditional; HSK is
Simplified. The dataset should ship both scripts, converted with OpenCC, with
the original script recorded. Handling this explicitly is itself a contribution:
any serious Chinese CEFR resource has to, and most existing work quietly picks
one.

**Level spread.** Encyclopedic text is almost uniformly B2 and above. Wikipedia
alone yields no A1 or A2 tier at all. A usable spread needs mixed sources —
Tatoeba for the bottom, Wikinews for the middle, Wikipedia for the top — and
the source mix has to be reported per band, because it confounds genre with
level.

**Word lists are not readability models.** Coverage is necessary, not
sufficient. Grammar, register and discourse structure are unmodelled, and the
TBCL grammar-point inventory is the obvious extension once the vocabulary tier
works.

## 5. Division of labour

What I would bring: the grading implementation and its validation against
published per-level totals (already done for the PRC syllabus, whose counts my
extraction reproduces exactly); the extraction and validation of the TBCL and
TOCFL inventories; the OpenCC pipeline; source acquisition and licence
tracking; and the reproducibility harness, on the pattern already in place,
where every published figure regenerates from a script.

What I would need from the network: CEFR-qualified Chinese assessors for the
validation stage, and a judgement on whether a two-stage design of this kind
clears the gold-standard bar or falls short of it.

## 6. Questions

1. Does a label derived from an officially CEFR-aligned national framework,
   validated on a sample by qualified raters, meet the gold-standard criterion —
   or does the criterion require direct expert assignment of every label?
2. Should a Chinese entry be TBCL-based, TOCFL-based, or carry both, given the
   two are officially cross-referenced but not identical?
3. Does the schema have a field for the source standard and its version? Two
   Chinese entries could agree on source dataset, language, granularity,
   production category and licence and still disagree on nearly half the bands.
4. Is CC BY-SA text acceptable, given the share-alike obligation?

## 7. What already exists

- `hsk30` — MIT, dependency-free, `pip install hsk30`; grades against either PRC
  document and records which. `doi:10.5281/zenodo.22234657`
- The comparison paper, `doi:10.5281/zenodo.22239032`
- The CEFR note, `doi:10.5281/zenodo.22285474`, which carries the cross-framework
  measurement above
- A validated extraction of the TOCFL 7,517-word list, every level matching the
  official per-level counts, with the traditional-to-simplified pipeline in place
- A validated extraction of the 2025 PRC syllabus from a 406-page PDF, whose
  per-level counts reproduce the official cumulative totals exactly — the same
  method the TBCL and TOCFL extractions would use

---

*Prepared 3 September 2026. Figures cited above are reproducible from
`github.com/harukicoder/hsk30`.*
