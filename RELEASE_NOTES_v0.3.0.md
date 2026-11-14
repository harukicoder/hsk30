## hsk30 0.3.0: ready for the 13 December exam

HSK 3.0 launches worldwide on **13 December 2026**, on the 2025 examination syllabus, which is the default here. Earlier releases said that syllabus had been "in force since July 2026"; that was wrong, and every docstring, help text and paper now gives the right date.

Grading results for existing callers do not change: no word, character or level in the 2025 or 2021 tables moved.

### New in the library

- **Traditional characters.** `grade()` converts traditional input before grading and records it in `profile.script` (`script="auto"` by default). The result is an upper bound, because conversion is many-to-one; the docstring says by how much. `convert_traditional()` and `looks_traditional()` are public.
- **Both HSK 2.0 editions.** `words("2012")` is the late-2012 revision (4,995 words). `words("2.0")` (also `"2010"`) stays the original 2009–10 lists. The two editions disagree on 316 of the 4,796 words they share.
- **Every table names its document.** Each data file opens with a `# standard:` line using the identifiers in `spec/standards.json`, so a copied table still says which document it is.

### New in the repository

- **The full 2025 syllabus, all 11,000 entries** (`corpus/syllabus2025/syllabus2025_entries.tsv`), with homograph readings as separate rows (还 hái, level 1; 还 huán, level 3). It was regenerated from the PDF the official site links, which was revised in place on 30 October 2026; PROVENANCE.md records its SHA-256. That revision changes no word or level, only pinyin. About 65 rows whose pinyin contains a space (你好 nǐ hǎo) had it cut at the space in the old table; that is fixed.
- **JavaScript.** `npm install hsk30` ([js/](js/)): the same grader for web apps and browser extensions. Its tests check that it gives the same grades as this package on 276 texts.
- **WriteToLevel in the evaluation harnesses.** It is packaged as an Inspect task (`benchmark/inspect/`) and an lm-evaluation-harness task (`benchmark/lm_eval/`), and the data is on Hugging Face as `harukicoder/writetolevel`. Both reproduce `evaluate.py` exactly.
- **A declaration convention and checker** (`spec/`, `scripts/check_declaration.py`), so a dataset can state which HSK document it encodes, and the checker tests that claim against the data.
- **A free demo** at huggingface.co/spaces/harukicoder/hsk-level-checker.

### Packaging

`__version__` now matches the package version; it said 0.2.0 in 0.2.1. The licence metadata now uses an SPDX expression (`license = "MIT"`), as current setuptools requires.

Archived as doi:10.5281/zenodo.24210442 (concept DOI 10.5281/zenodo.22234657).
