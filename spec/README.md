# Say which standard your data encodes

A one-field convention for Chinese proficiency datasets, and a registry of
canonical identifiers for the documents they encode.

**Version 1.0, 6 September 2026.** Public domain (CC0) — copy it, fork it,
ignore the attribution. A convention nobody can adopt freely is not a
convention.

---

## The problem, in one paragraph

"HSK 3.0" names two different official documents. 《国际中文教育中文水平等级标准》
(GF0025-2021) is a national grading standard in force since July 2021;
新版HSK考试大纲 is the examination syllabus published in November 2025 and in
force since July 2026. **They assign different levels to 41.5% of the vocabulary
they share.** An audit of the five most-used open HSK datasets found four of
them encode the 2021 standard, one encodes the 2025 syllabus, and only one says
which — in a directory name, which does not survive being imported
(`doi:10.5281/zenodo.22540154`).

So a learner reading "HSK 4" in an app cannot know what it means, and neither
can the app's author, and neither can anyone comparing two datasets.

---

## The convention

**Declare one field, named `standard`, whose value is an identifier from
[`standards.json`](standards.json).**

That is the whole requirement. Everything below is about where to put it.

```json
{
  "standard": "gf0025-2021",
  "words": [ ... ]
}
```

### Current identifiers

| Identifier | Document | In force |
| --- | --- | --- |
| `hsk-2012` | 汉语水平考试大纲 — the 2012 syllabus | 2012, superseded |
| `gf0025-2021` | 国际中文教育中文水平等级标准 — the national grading standard | 1 Jul 2021 |
| `hsk-syllabus-2025` | 中文水平考试HSK考试大纲 — the examination syllabus | Jul 2026 |
| `tbcl-2025` | 臺灣華語文能力基準 — Taiwan's standard | 2022, rev. Apr 2025 |
| `tocfl-8000-2024` | 華語八千詞 — the TOCFL word list | rev. Sep 2024 |

If your data encodes something not listed, open a pull request adding it. An
identifier is a string, not an endorsement; the registry describes what exists.

### Where the field goes, by format

The rule is: **inside the artifact a consumer actually copies.** A README does
not travel with the data.

**JSON, object at the root** — a top-level key:

```json
{ "standard": "gf0025-2021", "words": [ ... ] }
```

**JSON, array at the root** — do not change the shape and break every consumer.
Ship a sibling file named `standard.json`:

```json
{ "standard": "gf0025-2021", "applies_to": ["complete.json", "complete.min.json"] }
```

**CSV or TSV** — either a column, if every row shares one standard, or a comment
line before the header:

```
# standard: gf0025-2021
word	level
一	1
```

**Plain text** — a comment line, in whatever the format's comment syntax is:

```
# standard: gf0025-2021
```

**A package or library** — expose it at runtime, so a caller can ask:

```python
>>> hsk30.grade("我每天早上七点起床。").standard
'2025'
```

**Anything else** — the sibling `standard.json` file always works. Use it.

### Optional, if you want them

| Field | Meaning |
| --- | --- |
| `standard_registry` | URL of the registry version you resolved against |
| `retrieved` | ISO date you extracted the data |
| `coverage` | `"complete"`, `"partial"`, or a note |
| `derived_from` | Identifier or URL of an upstream dataset you took this from |

`derived_from` is worth more than it looks. The audit found four widely-used
lists that disagree about the level of *not one word* out of ~10,940 — they are
one artifact under four names, by a documented path. That is fine. What is not
fine is that a practitioner comparing three of them and finding agreement
concludes something has been corroborated.

---

## Verification: a declaration you can check

A claim nobody can test is a comment. This convention is testable, because the
three documents grade 531 short words at three different levels, so the data
itself reveals which one it encodes.

```bash
python3 scripts/check_declaration.py path/to/your/data.json
```

It finds the declaration, resolves it against the registry, then **checks the
data against the document it claims** and reports agreement. A dataset declaring
`gf0025-2021` and matching it at 58.5% has mislabelled itself, and the checker
says so rather than taking the word for it.

Undeclared data is not rejected — the checker fingerprints it and tells you
which identifier it should declare.

---

## What this is not

**Not a standard about standards.** It is one field and a list of five strings.
The registry is a convenience; the field is the point.

**Not a quality judgement.** Encoding GF0025-2021 is correct for a programme
teaching to the national standard, and encoding the 2025 syllabus is correct for
one preparing candidates for the examination. The convention is neutral about
which you should use; it asks only that a reader can tell.

**Not versioned aggressively.** Adding an identifier is a registry change and
does not change this document. If the convention itself ever needs a breaking
change, that is a failure of the original design and will be admitted as one.

---

## Adopting it

If you maintain a dataset, the whole change is one line. If you would rather
have a diff than a decision, ask and one will be opened.

If you consume datasets, `check_declaration.py` will tell you what you actually
have, which is more than most of these files currently say.

---

## Reference implementation

`hsk30` implements this. `src/hsk30/data/standard.json` declares the shipped
tables; `hsk30.grade()` returns the standard it used on every result, so no
caller can obtain a level without also obtaining what it means.

```python
>>> import hsk30
>>> p = hsk30.grade("我每天早上七点起床。", standard="2021")
>>> p.level, p.standard
(1, '2021')
```

The tables themselves declare `gf0025-2021`, `hsk-syllabus-2025` and
`hsk-2012` respectively, and `check_declaration.py` verifies each against its
own claim as part of the test suite — so this repository cannot ship a
mislabelled table without a test failing.
