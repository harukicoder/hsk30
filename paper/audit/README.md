# Four Repositories, One List

An audit of the open HSK 3.0 word lists the field actually builds on.

**The finding.** Of the five most-starred open HSK 3.0 datasets, four encode
GF0025-2021 (the national grading standard) and one encodes the 2025
examination syllabus. The four are not independent: across every pair, over
~10,940 shared words, they disagree about the level of **not one word**. The
derivation is documented — `drkameleon` credits `elkmovie`, and `elkmovie`
links the March 2021 ministry PDF it was OCR'd from — so this is not hidden
copying. It is a singly-rooted ecosystem, which is a different problem:
agreement between these lists cannot corroborate anything, and the root is no
longer the document learners are examined against.

**The by-product.** Comparing a community 2021 list to a community 2025 list,
from different maintainers, reproduces the 41.5% disagreement first reported in
`doi:10.5281/zenodo.22239032` to within **0.02 percentage points** — on data
with no dependency on our own extraction.

## Reproducing

```bash
python3 ../../scripts/audit_wordlists.py --md AUDIT.md
```

Fetches each list live from its own repository, caches under `.cache/`, and
writes the full table. No audited list is redistributed.

```bash
./build.sh          # the paper; needs tectonic
```

## A companion, for tools that publish no list at all

```bash
python3 ../../scripts/standard_fingerprint.py --probe
```

Twelve words that the three documents grade differently. Ask any black-box tool
for their levels, then:

```bash
python3 ../../scripts/standard_fingerprint.py --identify 5,5,2,5,5,6,3,6,5,5,6,4
```

It reports which document the tool implements, with a margin — and says "no
standard fits" rather than forcing a choice.

## A note on fairness

An earlier draft of this paper characterised two of the audited repositories
unfairly, because it described their data without reading their READMEs. Both
document their provenance carefully. The correction is recorded in the paper's
ethics statement rather than quietly applied.
