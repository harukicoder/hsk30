# Publishing the correction — three things, in this order

Written 5 September 2026. Everything is staged and committed; nothing below
needs a code change. Total time about 25 minutes.

The order matters. The **software** goes first because it is the only one with
users who currently have wrong data. The paper follows because it should cite
the fixed release. The audit goes last because it cites both.

---

# 1. The library — `hsk30` v0.2.1

**Why this one is urgent and the others are not.** 196 people have run
`pip install hsk30`. Every one of them has a 2021 word list missing 爸爸, 妈妈,
哥哥, 姐姐, 弟弟 and 妹妹. Character grading is unaffected, so
`hsk30.grade(text)` was always right — but `hsk30.words("2021")` was not, and
anyone using it for word-level work got a silently short list.

### 1.1 Cut the GitHub release

Version is already bumped to `0.2.1` in `pyproject.toml` and `CITATION.cff`, and
pushed.

```bash
gh release create v0.2.1 --title "v0.2.1 — the 2021 word list was missing 爸爸" --notes-file RELEASE_NOTES_v0.2.1.md
```

That single command triggers `.github/workflows/publish.yml`, which runs the
tests and the paper-figure check and then publishes to PyPI over Trusted
Publishing. No token, nothing to paste.

**Watch it:**

```bash
gh run watch
```

**Confirm it landed** (allow a minute for the index):

```bash
curl -s https://pypi.org/pypi/hsk30/json | python3 -c "import json,sys;print(json.load(sys.stdin)['info']['version'])"
```

Should print `0.2.1`.

### 1.2 Add the Zenodo version — manually

**The GitHub–Zenodo webhook is not installed.** I checked:

```bash
gh api repos/harukicoder/hsk30/hooks
```

returns `[]`. So cutting the release above will **not** create a Zenodo record
by itself. You did v0.2.0 by hand and you will do this one the same way.

1. Go to <https://zenodo.org/records/22261498> — the v0.2.0 record.
2. Top right, **New version**. This keeps the concept DOI `10.5281/zenodo.22234657`
   and mints a fresh version DOI.
3. **Delete** the old file `hsk30v0.2.0.tar.gz` from the new draft.
4. Upload the new tarball. Build it first:

   **Already built for you** — it is at
   `dist/hsk30-0.2.1.tar.gz` (158 KB), and I verified it ships the corrected
   list: 10,977 rows, with 爸爸, 妈妈, 哥哥, 姐姐, 弟弟 and 妹妹 all present at
   level 1.

   To rebuild it from scratch if you ever need to:

   ```bash
   cd "/Users/alvaroserrano/Documents Mac/Career/2026_CODER/new_projects/hsk30"
   python3 -m pip install --user build
   python3 -m build
   ```
5. **Version** field: `0.2.1`
6. **Publication date**: today.
7. Everything else is carried over from `.zenodo.json` and the previous version —
   leave it.
8. **Publish.**

Optional, if you want this to stop being manual: on Zenodo, **GitHub** in the
account menu → **Sync now** → toggle `harukicoder/hsk30` on → re-check
`gh api repos/harukicoder/hsk30/hooks` returns a URL. Zenodo only captures
releases created *after* the hook exists, so this would take effect from v0.2.2.

---

# 2. The paper — a corrected v3

### 2.1 What changed, and why it is a new version rather than an edit

§6.2 of the deposited v2 says derivation misgrades seven characters and blames
哥哥 and 妈妈 being "graded at level 4." They are level 1. They were missing from
our own word list. The published claim was an artifact of our bug.

The corrected §6.2 reports that derivation agrees on **all 2,971** characters it
can reach, gives the real reason to ship the official list (29 of the 3,000
characters appear in no listed word — all surname and place-name elements in the
7–9 band), and states the correction in the paper itself.

Counts in the comparison table move; **the headline percentages do not.** 41.5%
of shared words and 40.7% of shared characters still differ.

### 2.2 Publish it

The PDF is built and current: `paper/acl/main.pdf`.

```bash
cd "/Users/alvaroserrano/Documents Mac/Career/2026_CODER/new_projects/hsk30/paper/acl"
cp main.pdf ~/Desktop/Serrano_2026_Which_HSK_3.0.pdf
```

Keep the filename identical to v2's — Zenodo shows the file name, and a reader
comparing versions should see the same document, not what looks like a different
one.

1. Go to <https://zenodo.org/records/22285341> — the v2 record.
2. **New version.**
3. **Delete** the old `Serrano_2026_Which_HSK_3.0.pdf` from the draft, upload the
   new one.
4. **Version** field: `v3`
5. **Publication date**: today.
6. In **Additional notes** (or append to the description), paste:

```
Version 3 corrects Section 6.2. Version 2 reported that deriving character
levels from the word list misgrades seven characters, and attributed this to the
reduplicated forms 哥哥 and 妈妈 being graded at level 4. They are graded at
level 1. They were absent from the authors' extraction of the 2021 standard,
which filtered rows to pure hanzi before normalising the standard's variant
notation and so discarded 61 entries written in forms such as 爸爸｜爸,
第（第二）, …极了 and 称1 — including six kinship terms at HSK level 1.

With the extraction corrected, derivation agrees on all 2,971 characters it can
reach, and the reason to ship the official character list is instead that 29 of
the standard's 3,000 characters appear in no listed word at all, every one a
surname or place-name element in the 7-9 band.

The headline findings are unchanged: 41.5% of shared vocabulary and 40.7% of
shared characters are graded differently by the two documents. The underlying
counts move from 9,674 shared / 4,012 differing to 9,698 / 4,023, and the 2021
word list from 10,916 entries to 10,977. The corrected extraction now agrees
exactly with independently published community word lists.

The defect was found by auditing other projects' word lists against ours and
noticing that ours was the short one.
```

7. **Publish.**

**What happens to the old version:** nothing. v2 stays permanently at
`10.5281/zenodo.22285341`, with a banner pointing to the newer version. The
concept DOI `10.5281/zenodo.22239032` — the one cited everywhere — starts
resolving to v3. That is the behaviour you want and the reason to use Zenodo
versioning rather than replacing a file.

### 2.3 ORCID

Nothing to do. ORCID holds the **concept** DOI `10.5281/ZENODO.22239032`, which
now points at v3 on its own.

---

# 3. The audit — a new deposit

This is a first upload, not a version. Full copy-paste metadata is in
`paper/audit/ZENODO.md`; the short form:

```bash
cd "/Users/alvaroserrano/Documents Mac/Career/2026_CODER/new_projects/hsk30/paper/audit"
cp main.pdf ~/Desktop/Serrano_2026_Four_Repositories_One_List.pdf
```

1. Zenodo → **New upload.**
2. Upload the PDF. Resource type **Preprint**.
3. Title, description, keywords, licence: all in `paper/audit/ZENODO.md`,
   ready to paste.
4. **Related works** — add these rows. The first is the important one; it tells
   DataCite this belongs to the same body of work:

   | Relation | Identifier |
   | --- | --- |
   | Is supplement to | `10.5281/zenodo.22239032` |
   | Cites | `10.5281/zenodo.22286842` |
   | Is supplemented by | `10.5281/zenodo.22234657` |

5. **Publish.**
6. **ORCID:** Works → Add → Add work from DOI → paste the new DOI → Work type
   **Preprint**.

---

# 4. After all three

```bash
cd "/Users/alvaroserrano/Documents Mac/Career/2026_FULL_TIME/CV NIW Application"
python3 build_evidence_report.py
```

Picks up the new DOIs and the new PyPI version, and appends a dated snapshot.

Then send me the two new DOIs — the audit's, and v0.2.1's. They fill:

- `[deposit pending]` in §4.3 of the endeavor statement
- rows C-11 and C-12 in `Exhibit_Index.md`

---

# What not to do

**Do not delete or replace the v2 files in place.** Zenodo permits editing some
metadata on a published record but the point of a version is that the erroneous
text stays reachable. A silently corrected record is worse evidence than a
corrected one with its history visible — an adjudicator who can see the error
and the fix, both dated, is looking at a working method.

**Do not renumber or re-title the paper.** Same title, same filename, same
concept DOI. Only the version changes.

**Do not publish the audit before the paper's v3.** The audit's replication
section quotes 41.48% as "our own extraction," which is the corrected figure. If
someone reads the audit and then opens v2 of the paper, the numbers disagree.
