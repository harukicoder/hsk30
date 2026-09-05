# Zenodo deposit — copy and paste

Everything below goes into the Zenodo upload form for `paper/audit/main.pdf`.
Nothing here needs editing; the two fields you must set by hand are marked.

---

## Upload

**File:** `paper/audit/main.pdf` — rename to
`Serrano_2026_Four_Repositories_One_List.pdf` before uploading.

**Resource type:** Preprint

**Title**

```
Four Repositories, One List: The Open HSK 3.0 Datasets Encode a Document the Examination No Longer Uses
```

**Publication date:** the date you upload.

---

## Creators

```
Family name: Serrano
Given names: Alvaro
ORCID: 0009-0006-4701-9026
Affiliation: Independent researcher
```

---

## Description

Paste as-is. Zenodo accepts basic HTML in this field.

```html
<p>Tools that show a learner an HSK level almost never derive it from the issuing
body's PDF. They take it from a small number of open datasets. We audit the five
most-starred, comparing each word by word against the three documents in
circulation: the 2012 syllabus, the GF0025-2021 national grading standard, and
the 2025 examination syllabus in force since July 2026.</p>

<p><strong>Four of the five encode GF0025-2021, and only one encodes the
examination.</strong> Worse for anyone treating their agreement as
corroboration, the four are not independent: across every pair, over roughly
10,940 shared words, they disagree about the level of <strong>not one
word</strong>. They are one list. The derivation is documented rather than
hidden — one repository credits another as its source, and that one links the
March 2021 ministry PDF it was OCR'd from — so the ecosystem is not careless; it
is <em>singly rooted</em>, which is a different and more durable problem. A
consumer three hops downstream sees only "HSK 3.0".</p>

<p>The audit also yields an external replication we did not set out to obtain.
Comparing a community 2021 list to a community 2025 list — neither ours, from
different maintainers — reproduces the disagreement rate reported in
doi:10.5281/zenodo.22239032 to within <strong>0.01 percentage points</strong>
(41.49% against 41.48%), on data with no dependency on our extraction.</p>

<p>Auditing other people's lists also surfaced a defect in our own: our
extraction of the 2021 standard had filtered rows to pure hanzi before
normalising the standard's variant notation, silently dropping 61 entries
including 爸爸, 妈妈, 哥哥, 姐姐, 弟弟 and 妹妹, all of them HSK 1. The
correction is described in the paper and has been applied upstream.</p>

<p>The audit re-runs against the live repositories in one command. No audited
list is redistributed.</p>
```

---

## Keywords

Add one at a time:

```
Chinese
HSK
HSK 3.0
language proficiency standards
readability assessment
open data
data provenance
reproducibility
computational linguistics
second language acquisition
```

---

## Licence

**Creative Commons Attribution 4.0 International (CC BY 4.0)** — the same as
your other four deposits.

---

## Related works

Add each as a separate row. The relation is in the left dropdown, the identifier
in the field beside it.

| Relation | Identifier | Resource type |
| --- | --- | --- |
| **Is supplement to** | `10.5281/zenodo.22239032` | Preprint |
| **Cites** | `10.5281/zenodo.22239032` | Preprint |
| **Cites** | `10.5281/zenodo.22286842` | Preprint |
| **Is supplemented by** | `10.5281/zenodo.22234657` | Software |
| **Is documented by** | `https://github.com/harukicoder/hsk30` | Software |

The first row is the important one — it tells DataCite this paper belongs to the
same body of work as the original, which is how a reader arriving at either one
finds the other.

---

## Two fields to set by hand

1. **Version** — leave blank for a first deposit.
2. **Publication date** — Zenodo defaults to today; that is correct.

---

## After publishing

1. **Add it to ORCID.** Works → Add → Add work from DOI, paste the new DOI, set
   Work type to **Preprint**. Same as the other four.
2. **Send me the DOI.** It fills the `[deposit pending]` cell in §4.3 of the
   endeavor statement and the pending row in `Exhibit_Index.md` §C.
3. **Update `CITATION.cff`** if you want the audit listed among the references —
   not required.

---

## What this deposit is worth in the petition

Under the USCIS Policy Manual, prong one is established in part by showing
"widespread interest in adoption or licensing of the technology … or **how the
technology stands to impact the development of similar technology by other
companies**." Every other work in this file argues from the documents. This one
measures the field's own software and names it. It is the closest thing in the
record to that sentence.

The external replication does separate work: it answers the standing objection
that a self-published finding rests on the author's own unchecked extraction.
After this, it does not.
