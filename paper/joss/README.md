# JOSS submission

A short software paper for the [Journal of Open Source Software](https://joss.theoj.org),
which peer-reviews research software in public and issues a Crossref DOI.

**Note for submission:** this repository contains two files named `paper.md` —
`paper/paper.md` is the research paper (the HSK 3.0 comparison), and this one is
the software paper. JOSS asks for the paper's path in the submission form; give
it `paper/joss/paper.md` explicitly so the bot does not pick the wrong one.

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
