# JOSS submission

A short software paper for the [Journal of Open Source Software](https://joss.theoj.org),
which peer-reviews research software in public and issues a Crossref DOI.

**Note for submission:** `paper/joss/paper.md` is the only file named `paper.md`
in this repository, deliberately. JOSS's bot searches for that filename and takes
the first match, so the research paper's markdown mirror lives at
`paper/whichhsk.md` to keep the search unambiguous. Do not rename it back.

## Before submitting

- [x] OSI-approved licence (MIT), in `LICENSE`
- [x] Public repository, issues open to anyone
- [x] `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md`
- [x] Automated tests (39) and CI on Python 3.9–3.13
- [x] Installation and usage documented in `README.md`
- [x] Archived release with a DOI — `10.5281/zenodo.22234657`
- [x] Paper under 1,000 words, describing the software rather than new results
- [ ] Submit at https://joss.theoj.org/papers/new — needs a GitHub login

## What reviewers will do

Review happens as a public GitHub issue against a checklist covering
documentation, tests, community guidelines and the paper itself. Outcomes are
accept, minor revisions, or major revisions; JOSS does not reject submissions
that need major work. Expect questions rather than a verdict.
