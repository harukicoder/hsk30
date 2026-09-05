# Which HSK document do the open word lists encode?

Audit run 2026-09-05. Each list fetched from its own public repository and compared
word by word against the three documents in circulation. Agreement is over
shared words only, so incompleteness is not penalised — what is measured is
whether the *level* matches.

| List | Stars | Words | HSK 2.0 | GF0025-2021 | 2025 syllabus | Best match |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `krmanik/HSK-3.0 (2025)` | 356 | 10,900 | 48.9% <sub>(n=4,804)</sub> | 58.5% <sub>(n=9,677)</sub> | 100.0% <sub>(n=10,896)</sub> | **2025 syllabus** (+41.5) |
| `krmanik/HSK-3.0 (2021)` | 356 | 10,943 | 18.2% <sub>(n=4,487)</sub> | 100.0% <sub>(n=10,909)</sub> | 58.5% <sub>(n=9,690)</sub> | **GF0025-2021** (+41.5) |
| `drkameleon/complete-hsk-vocabulary` | 294 | 10,969 | 18.2% <sub>(n=4,490)</sub> | 100.0% <sub>(n=10,914)</sub> | 58.5% <sub>(n=9,696)</sub> | **GF0025-2021** (+41.5) |
| `elkmovie/hsk30` | 115 | 10,946 | 18.2% <sub>(n=4,489)</sub> | 100.0% <sub>(n=10,916)</sub> | 58.5% <sub>(n=9,694)</sub> | **GF0025-2021** (+41.5) |
| `ivankra/hsk30` | 80 | 10,946 | 18.2% <sub>(n=4,489)</sub> | 100.0% <sub>(n=10,916)</sub> | 58.5% <sub>(n=9,694)</sub> | **GF0025-2021** (+41.5) |

`n` is the number of words the list and that document share; the percentage
is agreement over those. A high rate on a small `n` would be weak evidence,
so both are shown.

### What each repository says about itself

| List | Its own description | What the data matches |
| --- | --- | --- |
| `krmanik/HSK-3.0 (2025)` | directory named "New HSK (2025)" | 2025 syllabus, 100.0% |
| `krmanik/HSK-3.0 (2021)` | directory named "New HSK (2021)" | GF0025-2021, 100.0% |
| `drkameleon/complete-hsk-vocabulary` | "HSK 2.0/3.0"; credits elkmovie as its wordlist source | GF0025-2021, 100.0% |
| `elkmovie/hsk30` | OCR of the March 2021 MOE PDF, which it links | GF0025-2021, 100.0% |
| `ivankra/hsk30` | "HSK 3.0 … 11,092 terms"; index from the 2021 PDF | GF0025-2021, 100.0% |

### Are these lists independent?

A field with five lists that agree is better evidenced than a field with one
list copied five times. Pairwise agreement, over the words each pair shares:

| Pair | Shared words | Level disagreements | Agreement |
| --- | ---: | ---: | ---: |
| `krmanik/HSK-3.0 (2021)` vs `drkameleon/complete-hsk-vocabulary` | 10,935 | 0 | 100.0%  **identical** |
| `krmanik/HSK-3.0 (2021)` vs `elkmovie/hsk30` | 10,935 | 0 | 100.0%  **identical** |
| `krmanik/HSK-3.0 (2021)` vs `ivankra/hsk30` | 10,935 | 0 | 100.0%  **identical** |
| `drkameleon/complete-hsk-vocabulary` vs `elkmovie/hsk30` | 10,938 | 0 | 100.0%  **identical** |
| `drkameleon/complete-hsk-vocabulary` vs `ivankra/hsk30` | 10,938 | 0 | 100.0%  **identical** |
| `elkmovie/hsk30` vs `ivankra/hsk30` | 10,942 | 0 | 100.0%  **identical** |
| `krmanik/HSK-3.0 (2025)` vs `elkmovie/hsk30` | 9,698 | 4,023 | 58.5% |
| `krmanik/HSK-3.0 (2025)` vs `ivankra/hsk30` | 9,698 | 4,023 | 58.5% |
| `krmanik/HSK-3.0 (2025)` vs `drkameleon/complete-hsk-vocabulary` | 9,700 | 4,025 | 58.5% |
| `krmanik/HSK-3.0 (2025)` vs `krmanik/HSK-3.0 (2021)` | 9,694 | 4,024 | 58.5% |

Pairs marked **identical** disagree about the level of **not one word**.
They are not independent derivations; they descend from a common ancestor.

This is documented rather than hidden. `drkameleon` credits
`elkmovie/hsk30` in its README as its source for the HSK 3.0 wordlist, and
`elkmovie` states it was OCR'd with Pleco OCR from the March 2021 Ministry
of Education announcement, which it links. Every maintainer said what they
did.

The consequence is for readers. Checking a word against three of these
lists and finding agreement teaches you nothing about the standard — it
teaches you that one file propagated. Agreement here cannot detect an OCR
error, and the root list says it was "not extensively proofread".

### An external replication, which was not the point of this audit

Take the community list that encodes the 2021 standard and the community
list that encodes the 2025 syllabus, and compare those two to each other.
Neither was produced by us, and neither has any dependency on our
extraction of either document.

| Comparison | Shared words | Differ | Rate |
| --- | ---: | ---: | ---: |
| `drkameleon/complete-hsk-vocabulary` vs `krmanik/HSK-3.0 (2025)` | 9,700 | 4,025 | **41.49%** |
| Our own extractions, as published | 9,674 | 4,012 | **41.47%** |

The two rates differ by **0.02 percentage points**.

The 41.5% disagreement between the two documents called "HSK 3.0" was
first reported from our extraction of the source PDFs
(`doi:10.5281/zenodo.22239032`). It reproduces from community datasets
built independently, by different people, from the same two documents.
That is a stronger form of evidence than the original: an extraction
error on our side could produce the finding, but it could not produce it
twice in data we did not touch.

### Finding

**1 of 5 lists audited match the 2025 examination syllabus.** The only one
that does is the only one whose own directory name says 2025.

Read the other way: the same repository publishes both documents in separate
folders and each matches its label exactly, which is the control for this
method — an audit that could not tell them apart would be worthless. It can.

The rest encode an earlier document. Learners sitting the HSK from July
2026 are examined against the 2025 syllabus, which assigns a different
level to 41.5% of the vocabulary it shares with the 2021 standard. A tool
built on one of these lists will therefore disagree with the examination
about a large share of the words it labels, without saying so and without
its users having any way to find out.

*Reproduce with `python3 scripts/audit_wordlists.py`. Lists are fetched from
their own repositories under their own licences; none is redistributed here.*
