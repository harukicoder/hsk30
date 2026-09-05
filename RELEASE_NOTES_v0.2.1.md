## The 2021 word list was missing 爸爸

**If you use `hsk30.words("2021")`, upgrade.** If you only use `hsk30.grade()`,
nothing changed for you — character grading was always correct.

### What was wrong

`scripts/gen_data.py` filtered rows to pure hanzi *before* normalising the
notation the standard itself uses for variants and affixes. Entries written
`爸爸｜爸`, `第（第二）`, `…极了` and `称1` all contain a character outside the
CJK ideograph range, so the filter rejected them — **61 entries in total**,
including `爸爸`, `妈妈`, `哥哥`, `姐姐`, `弟弟` and `妹妹`, every one of them
HSK level 1.

The regression guard asserted `10916`, which is the count that survived the bug,
so it passed forever.

### What changed

| | before | after |
| --- | ---: | ---: |
| `words("2021")` | 10,916 | **10,977** |
| shared with the 2025 syllabus | 9,674 | **9,698** |
| …of which graded differently | 4,012 (41.5%) | **4,023 (41.5%)** |
| character derivation agreement | 2,962 of 2,969 | **2,971 of 2,971** |

`characters("2021")` is unchanged at 3,000 and was always correct. No level of
any previously present word changed; the fix is purely additive.

`gen_data.py` now reads upstream's `hsk30-expanded.csv`, which already resolves
the variant notation onto separate rows of clean hanzi. Re-deriving that
normalisation here would only have been a second chance to get it wrong.

### A published claim this invalidated

§6.2 of the paper reported that deriving character levels from words misgrades
seven characters, and explained it by 哥哥 and 妈妈 being "graded at level 4."
They are graded at level 1 — they were missing from our list. That claim was an
artifact of this bug and has been corrected in the paper, which now reports that
derivation agrees on every character it can reach, and gives the real reason to
ship the official list: **29 of the standard's 3,000 characters appear in no
listed word at all**, every one a surname or place-name element in the 7–9 band.

### How it was found

By auditing four widely-used community HSK word lists against ours and noticing
that ours was the short one. That audit is in `paper/audit/`, and it also
reproduces this project's central finding — the 41.5% disagreement — from data
none of it produced, to within 0.01 percentage points.

### Also in this release

- `scripts/audit_wordlists.py` — audits the open HSK datasets against all three
  documents, live, in one command
- `scripts/standard_fingerprint.py` — a twelve-word probe that identifies which
  document any black-box tool implements
- `scripts/levelling_report.py` — grades a collection under both documents and
  reports where they disagree, locally, with nothing uploaded
- A regression test that names the six kinship terms, because a count assertion
  is exactly what let this through
