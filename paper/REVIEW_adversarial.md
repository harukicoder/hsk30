# Reading "Which HSK 3.0?" as a hostile ARR reviewer

Written 4 September 2026, before the 12 October cycle. The exercise is to break
the paper, not to praise it. Ordered by how much damage each point does.

---

## 1. The "Human authors" baseline is not human — fix before resubmitting anywhere

Table 4 reports a system called **Human authors** at 61.8% level accuracy, and
§8.3 calls it "a human reference point". `benchmark/baselines/human_reference.py`
computes it over the 102 corpus texts. §9 of the same paper states those texts
were "drafted with large-language-model assistance and then reviewed, edited and
re-levelled by the author".

So the benchmark compares two language models against a baseline it labels human
and which is LLM-drafted. A reviewer who reads §9 and Table 4 in the same sitting
finds a contradiction inside one paper, in the section where the paper is arguing
that its measurement is trustworthy. This is the kind of finding that costs more
than the point itself, because it invites the reviewer to reread everything else
looking for the same thing.

It is also, on the evidence, an honest slip rather than a claim: the docstring
says "*human* authors" in the same file that grades LLM-assisted text, so nobody
noticed the two facts were adjacent.

**The fix is a relabel, not a retraction.** What the row actually measures is
*text authored to an explicit level target with human review in the loop* — which
remains a meaningful reference, and still supports the paper's argument that an
objective grader is needed in the authoring loop. It just is not a human
baseline, and must not be called one.

Downstream: the abstract says "Human authors writing to an explicit level target
hit it 61.8% of the time." That sentence has to change too.

## 2. The headline result is measured on the author's own corpus

The paper's central claim — 48% of texts change level — is computed on 102 texts
the author wrote, LLM-assisted, to level targets defined by one of the two
standards being compared. The held-out 30 come from "a separate content stream",
which is still the author's own material.

A reviewer will say this is close to circular, and they will not be wrong to ask.
The defence in the paper is that method, threshold and proper-noun policy are
held constant so the document is the only variable — which is a good defence of
*internal* validity and no defence at all of external validity.

**This is the single most valuable thing that could be fixed before 12 October.**
Regrading a few hundred texts the author did not write — Chinese Wikipedia,
Wikinews, Tatoeba, all human-authored and permissively licensed — would convert
the strongest objection into a strengthened result. The machinery already exists:
`scripts/tocfl_compare.py` reads external corpora, and the OpenCC pipeline is in
place. If the effect holds on natural text, the paper is materially stronger. If
it does not, that is worth knowing before a reviewer finds it.

## 3. Two models from one family is not a benchmark

§8 evaluates `deepseek-chat` and `deepseek-reasoner`. Same lab, same family. The
"reasoning buys a floor and costs a ceiling" finding is genuinely interesting and
rests entirely on a single chat/reasoner pair from one vendor — it may be a
property of DeepSeek's reasoning tuning rather than of reasoning.

The omission a Chinese-NLP reviewer will name immediately is **Qwen**, which is
the obvious Chinese-native baseline. GPT and Claude would also be expected.

Adding two or three models is cheap relative to what it buys, and the harness
already exists in `benchmark/baselines/run_model.py`.

## 4. Track choice will decide acceptance more than quality will

Submitted to an ACL main-conference track this reads as a niche resource paper
about one language's proficiency standards, and risks a "limited general
interest" rejection that says nothing about whether the work is right.

The honest fits, best first:

- **Resources and Evaluation** track — where a validated extraction, a corpus
  and a benchmark are the expected contribution
- **LREC** — a resource venue where this is squarely in scope
- **BEA workshop** — educational applications, and the most sympathetic
  audience, though a workshop rather than a main venue

ARR lets the track be chosen at submission. Choose Resources and Evaluation.

## 5. Anonymisation is a real work item, and the last attempt at it failed

ACL venues review double-blind even where non-anonymous preprints are permitted.
The paper currently names the author, links `github.com/harukicoder/hsk30`, cites
its own Zenodo DOIs, and refers to "our own tooling" and an author-operated
website in the ethics statement. All of that has to be scrubbed for the
submission build while the preprint keeps its name.

The last time this repository built in `[review]` mode, the resulting PDF said
"Anonymous ACL submission" and was deposited to Zenodo that way, twice. The
guard in `build.sh` now fails a build that is *not* named — which is exactly
backwards for a submission build and will need inverting for the anonymous one.

## 6. Smaller things a careful reviewer will still raise

**No confidence intervals anywhere.** 48% of 102 texts carries roughly a ±10
point interval. Every headline percentage in the paper is a point estimate on a
small sample, presented without one.

**The 3,079 correction is unsourced.** "Secondary sources widely report 3,079;
we believe that figure to be incorrect" — a reviewer cannot check a claim about
sources that are not cited. Name two.

**Shelf medians depend on the author's shelf assignment**, with no
inter-annotator agreement, as the limitations admit. The result survives this —
the shift is measured within a fixed partition, so the partition needs only to be
stable, not correct — but the paper does not say so, and a reviewer will not
supply that argument for it.

**Scope.** Extraction, comparison, method, corpus and benchmark is a lot for one
paper. Some reviewer will say it is two. The benchmark is the separable half.

## 7. What is genuinely strong, and should not be diluted

The provenance discipline is unusual and reviewers will notice it: figures that
regenerate from a script, an extraction validated against published totals, a
threshold sweep and a disjoint replication offered before anyone asked. The
limitations section is unusually candid. The 371-versus-600 beginner-character
mechanism is a real explanation rather than a restatement of the effect, and
"reasoning buys a floor and costs a ceiling" is a genuine finding that would
survive on its own.

The paper's problem is not that it overclaims. It is that its best result rests
on material the author produced.
