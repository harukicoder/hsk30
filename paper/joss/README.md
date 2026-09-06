# JOSS submission

A short software paper for the [Journal of Open Source Software](https://joss.theoj.org),
which peer-reviews research software in public and issues a Crossref DOI.

**Note for submission:** `paper/joss/paper.md` is the only file named `paper.md`
in this repository, deliberately. JOSS's bot searches for that filename and takes
the first match, so the research paper's markdown mirror lives at
`paper/whichhsk.md` to keep the search unambiguous. Do not rename it back.

## NOT ELIGIBLE UNTIL 1 MARCH 2027

Re-verified against JOSS's own documentation on 6 September 2026. The rule is
explicit and there is no discretion in it:

> "The repository must have been public for more than six months prior to
> submission, with active development spanning that period."

> "Projects developed privately are not eligible until there is a public record
> of open development: at least six months of public history prior to
> submission, with evidence of releases, public issues and pull requests."

The review-criteria page is more specific still about what a reviewer is told to
flag. *Unacceptable:* "All or most commits concentrated in the last few weeks
before submission." Repositories "made public days before submission" are to be
"flagged immediately to the handling editor for potential desk rejection, rather
than proceeding with full review."

**This repository's history as of today: first commit 1 September 2026, 66
commits, all within six days.** That is the exact pattern the criteria name. A
submission now would be desk-rejected, and the rejection would sit permanently
on JOSS's public review repository — a worse outcome than not submitting, since
the record is the point.

**Earliest defensible submission: 1 March 2027.**

Two things about the wait are worth knowing. Solo development is not a barrier —
contributions from others are "especially welcome, though not essential."
Demonstrated research impact is a priority consideration rather than a hard gate,
and "credible near-term significance" counts. So the six months are best spent
generating exactly the adoption evidence that strengthens the case: the CLTA
newsletter, the Utah dual-language immersion programme, and third-party use.

The wait also wants *shape*. What the criteria reward is development distributed
over the period, releases or version tags, and public issues and pull requests —
not a second burst in February. Tag releases as they happen and let the issue
tracker carry real discussion.

## Before submitting

- [x] OSI-approved licence (MIT), in `LICENSE`
- [x] Public repository, issues open to anyone
- [x] `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md`
- [x] Automated tests (44) and CI on Python 3.9–3.13
- [x] Installation and usage documented in `README.md`
- [x] Archived release with a DOI — concept `10.5281/zenodo.22234657`,
      v0.2.1 `10.5281/zenodo.22539582`
- [x] Paper describes the software rather than new results
- [x] AI usage disclosure — required since 2026; incomplete disclosure is
      treated as an ethical breach
- [x] Every citation key in `paper.md` resolves in `paper.bib` (9 entries)
- [ ] **Word count.** The paper is ~1,090 words, of which ~276 are the mandatory
      AI usage disclosure; the substantive paper is ~814. JOSS asks for
      250–1,000 and does not say whether the required disclosure counts toward
      it. Ask the handling editor, or trim to 1,000 including the disclosure,
      before submitting — do not guess.
- [ ] Six months of public history — **earliest 1 March 2027**
- [ ] Evidence of external adoption to cite as realized impact
- [ ] Submit at https://joss.theoj.org/papers/new — needs a GitHub login

## What reviewers will do

Review happens as a public GitHub issue against a checklist covering
documentation, tests, community guidelines and the paper itself. Outcomes are
accept, minor revisions, or major revisions; JOSS does not reject submissions
that need major work. Expect questions rather than a verdict.

That public thread is part of why this venue is worth waiting for: named
reviewers, a named editor, and a dated record of independent experts examining
the work — which is a different artifact from an acceptance letter, and in some
ways a better one.
