# Release checklist

State: repo **public** as of 1 September 2026, CI green, installable from
GitHub, package builds and passes `twine check`, paper figures verified against
live computation, both benchmark baselines run.

Done: public flip, topics, issues and discussions enabled, install verified
from a clean venv against the public URL.

## Blocking before going public

- [x] ~~CNKI novelty search~~ — taken as far as web access allows. The
      authoritative development paper was located and is qualitative; only
      adjacent prior work exists. CNKI full text stayed unreachable, so the
      paper states the residual risk rather than claiming more.
- [ ] ~~(superseded)~~ **CNKI novelty search.** The one verification I could not do. Search
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

`.zenodo.json` pins the record's metadata (author as "Serrano, Alvaro", title,
description, keywords, licence) so Zenodo does not infer them from the
repository. It is committed, so any release from now on carries it.

**Diagnosing a toggle that did not take.** Zenodo installs a webhook on the
repository when the switch saves. Check with:

```bash
gh api repos/harukicoder/hsk30/hooks --jq '.[].config.url'
```

An empty result means the switch is not actually on, whatever the page shows.
Zenodo only lists **public** repositories, and its list is cached — press
**Sync now** first, then toggle.

**Ordering matters.** Zenodo captures only releases created *after* the webhook
exists. A release cut beforehand is invisible to it, and re-tagging does not
help. Once the hook is confirmed, cut a fresh release.

**Fallback if the integration stays broken:** upload the release tarball to
Zenodo manually via **New upload**. It mints the same kind of DOI; you just
lose the automatic capture of future releases.

## PyPI — no token required

`.github/workflows/publish.yml` uses **Trusted Publishing**: PyPI is told to
trust this repository and workflow by name, and GitHub mints a short-lived
identity token at publish time. No API token exists in the repo, in GitHub
secrets, or anywhere you have to copy, store or transmit.

**One-time setup** (about two minutes, all on pypi.org):

1. Create an account and verify the email. PyPI requires 2FA — set it up now,
   it is required before you can publish.
2. Go to **Your projects → Publishing → Add a pending publisher**. "Pending"
   is correct: the project does not exist yet, and this creates it on first
   publish.
3. Fill in exactly:
   - PyPI project name — `hsk30`
   - Owner — `harukicoder`
   - Repository name — `hsk30`
   - Workflow name — `publish.yml`
   - Environment name — `pypi`
4. Save. Nothing else to do.

Publishing then happens automatically on every GitHub release, and only after
the test suite and the paper-figure check pass. To publish the existing
release, re-run the workflow: `gh workflow run publish.yml`.

Name `hsk30` was free as of 2026-09-01; claim it soon now the repo is public.

## HuggingFace dataset — needs a write token

No OIDC equivalent here, so a token is unavoidable.

1. Create an account at huggingface.co and verify the email.
2. **Settings → Access Tokens → Create new token**, type **Write**, name it
   something like `hsk30-upload`.
3. Copy it. It is shown once.

Then either run the upload yourself:

```bash
pip install huggingface_hub
huggingface-cli login          # paste the token at the prompt
huggingface-cli upload harukicoder/hsk30-graded-readers corpus/ --repo-type dataset
```

or put the token in a file outside the repo the way the DeepSeek key was
handled, and it can be scripted. **Do not paste it into a chat window** — a
write token can modify anything on your account, unlike the DeepSeek key which
only spent credit.

Upload `hsk30_graded_readers.jsonl` and `hsk30_heldout.jsonl`, with
`DATASHEET.md` as the dataset card and a link back to the repo. Download counts
are the adoption metric worth tracking.

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
