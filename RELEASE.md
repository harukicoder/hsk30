# Release checklist

State as of the last commit: repo **private**, CI green, package builds and
passes `twine check`, paper figures verified against live computation.

## Blocking before going public

- [ ] **CNKI novelty search.** The one verification I could not do. Search
      《世界汉语教学》, 《语言教学与研究》 and 《国际中文教育》 for a prior
      quantitative comparison of the 2021 standard against the 2025 syllabus.
      English-language and Chinese web searches found none, and the
      authoritative development paper (Feng et al., 2026) is qualitative — but
      CNKI full text was unreachable. If a prior comparison exists, §4 becomes
      a replication rather than a contribution, which changes the paper's
      framing but not its usefulness.
- [ ] **Decide on the 2025 table redistribution.** `corpus/syllabus2025/`
      ships extracted word- and character-level mappings from a government
      standard. See `corpus/syllabus2025/PROVENANCE.md`. The extraction script
      alone is unambiguously distributable; the derived tables are the open
      question.

## Going public

```bash
gh repo edit harukicoder/hsk30 --visibility public --accept-visibility-change-consequences
```

Then, in the repo settings, enable Issues and Discussions if you want the
benchmark to receive submissions.

## Zenodo DOI

Do this **before** the paper goes out — the DOI is what the paper cites.

1. Sign in at <https://zenodo.org> with GitHub.
2. Settings → GitHub → flip the switch on `harukicoder/hsk30`.
   (Only public repositories appear, so make it public first.)
3. Cut a release: `gh release create v0.1.0 --title "v0.1.0" --generate-notes`
4. Zenodo mints a DOI automatically and reads `CITATION.cff` for metadata.
5. Add the DOI badge to `README.md` and the DOI to `CITATION.cff`.

## PyPI

Name `hsk30` was free as of 2026-09-01. Build artifacts are gitignored;
regenerate them rather than committing.

```bash
python3 -m venv /tmp/rel && /tmp/rel/bin/pip install -q build twine
/tmp/rel/bin/python -m build
/tmp/rel/bin/twine check dist/*
/tmp/rel/bin/twine upload --repository testpypi dist/*   # rehearse first
/tmp/rel/bin/twine upload dist/*
```

Use a scoped API token, not your password. Test the TestPyPI install in a
clean venv before the real upload.

## HuggingFace dataset

The corpus is CC BY 4.0 and has a datasheet. Upload
`corpus/hsk30_graded_readers.jsonl` with `corpus/DATASHEET.md` as the dataset
card, and link back to the repo. Download counts are the adoption metric worth
tracking.

## Paper

- [ ] Resolve the remaining `\todo{}` markers in `paper/acl/main.tex`
- [ ] Compile with **XeLaTeX** (see `paper/acl/README.md`) — it has never been
      compiled, so budget time for the first build
- [ ] Re-run `python3 scripts/check_paper.py` after any edit to the numbers
- [ ] Decide arXiv vs Zenodo/OSF. arXiv cs.CL needs an endorsement for a first
      submission without an institutional affiliation; Zenodo and OSF do not
      gatekeep and still give a citable DOI and timestamp.

## Housekeeping

- [ ] **Rotate the DeepSeek API key** used for the benchmark runs — it passed
      through a conversation context.
- [ ] `~/.hsk30.env` holds that key at mode 600. Delete it once rotated.
