# JOSS submission

A short software paper for the [Journal of Open Source Software](https://joss.theoj.org),
which peer-reviews research software in public and issues a Crossref DOI.

**Note for submission:** `paper/joss/paper.md` is the only file named `paper.md`
in this repository, deliberately. JOSS's bot searches for that filename and takes
the first match, so the research paper's markdown mirror lives at
`paper/whichhsk.md` to keep the search unambiguous. Do not rename it back.

## NOT ELIGIBLE UNTIL 1 MARCH 2027

JOSS's 2026 rules require **at least six months of public development history**
before submission, with releases and public issues, and state no exceptions.
This repository went public on 1 September 2026. Submitting before roughly
**1 March 2027** invites a desk rejection, which would be recorded permanently
on JOSS's public review repository.

Two things about the wait are worth knowing. Solo development is not a barrier —
contributions from others are "especially welcome, though not essential."
Demonstrated research impact is a priority consideration rather than a hard gate,
and "credible near-term significance" counts. So the six months are best spent
generating exactly the adoption evidence that strengthens the case: the CLTA
newsletter, the Utah dual-language immersion programme, and third-party use.

## Before submitting

- [x] OSI-approved licence (MIT), in `LICENSE`
- [x] Public repository, issues open to anyone
- [x] `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md`
- [x] Automated tests (39) and CI on Python 3.9–3.13
- [x] Installation and usage documented in `README.md`
- [x] Archived release with a DOI — `10.5281/zenodo.22234657`
- [x] Paper under 1,000 words, describing the software rather than new results
- [x] AI usage disclosure — required since 2026; incomplete disclosure is
      treated as an ethical breach
- [ ] Six months of public history — **earliest 1 March 2027**
- [ ] Evidence of external adoption to cite as realized impact
- [ ] Submit at https://joss.theoj.org/papers/new — needs a GitHub login

## What reviewers will do

Review happens as a public GitHub issue against a checklist covering
documentation, tests, community guidelines and the paper itself. Outcomes are
accept, minor revisions, or major revisions; JOSS does not reject submissions
that need major work. Expect questions rather than a verdict.
