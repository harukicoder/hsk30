# Four Repositories, One List

`doi:10.5281/zenodo.22540154` — published 6 September 2026.

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

## A finding that emerged after publication

**The root of a singly-rooted ecosystem can be unreachable.**

On 6 September 2026 we tried to contribute the one-line fix this audit
recommends — a README note naming the source document — to each audited
repository. Three accepted issues:

- `krmanik/HSK-3.0` — <https://github.com/krmanik/HSK-3.0/issues/13>
- `elkmovie/hsk30` — <https://github.com/elkmovie/hsk30/issues/10>
- `ivankra/hsk30` — <https://github.com/ivankra/hsk30/issues/4>

`drkameleon/complete-hsk-vocabulary` (294 stars) accepts none. Issues,
discussions, wiki and pull requests are all disabled, and the repository's own
README still links to an issue tracker that no longer accepts issues. A prepared
branch exists at
<https://github.com/harukicoder/complete-hsk-vocabulary/tree/document-which-hsk-3.0>
and cannot be offered.

This sharpens §3.3 rather than contradicting it. The argument there was that
provenance does not survive being copied, so the fix belongs inside the data.
The corollary is stronger: **where a widely-used dataset has closed every
inbound channel, no external party can correct it at all**, and everything
downstream inherits whatever it says for as long as it says it. A convention
that travels inside the file is not merely more durable than a README — for a
repository in this state it is the only mechanism available, because there is
nobody to ask.

We have not emailed the maintainer. Four channels closed is a decision, and
routing around it would be a poor way to open a conversation about care.

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
