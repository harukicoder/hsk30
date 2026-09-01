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
- [ ] **Publishing route — settled: Zenodo now, BEA 2027 later.** See below.

## Publishing routes, accurately

Nothing here requires anyone's permission. The only gated route is arXiv, and
it is optional.

**arXiv — needs an endorser, and got harder.** On 21 January 2026 arXiv stopped
accepting an institutional email address as a qualifier for new authors. Every
first-time submitter now needs endorsement from an established contributor to
that archive, regardless of affiliation. This is a gate on arXiv, not on
publishing. Pursue it only if an endorser turns up naturally; do not wait on it.

**Zenodo — no gatekeeping, do this first.** CERN-operated, permanent, mints a
real DOI, and reads `CITATION.cff` automatically. It cites as a dataset and
software release, which is exactly what this is. Available the day the repo
goes public.

**OSF Preprints — no gatekeeping.** A second option for the paper specifically
if you want a preprint DOI separate from the software DOI.

**BEA — the peer-review target, but the 2026 edition has passed.** BEA 2026
closed on 23 March 2026 and ran on 2–3 July 2026. **BEA 2027 is the next
window**, with a deadline likely around March 2027. Worth noting that BEA 2026
ran a shared task on *Vocabulary Difficulty Prediction for English Learners* —
the community is actively working on this exact problem, which is good for
reception and worth citing.

Peer review is stronger evidence than a preprint, but it is slow. The sequence
that gets something citable now and something reviewed later is: **Zenodo DOI
this month, BEA 2027 in March.** If a nearer venue is wanted, look at other ACL
workshops and LREC rather than waiting nine months.

## Housekeeping

- [ ] **Rotate the DeepSeek API key** used for the benchmark runs — it passed
      through a conversation context.
- [ ] `~/.hsk30.env` holds that key at mode 600. Delete it once rotated.
