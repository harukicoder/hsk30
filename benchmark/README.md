# WriteToLevel

**Can a model write Chinese at a level it was asked for?**

Grading text is easy. *Generating* text that lands on a difficulty target is
not — and it is what teachers, textbook authors and reading apps actually need.
WriteToLevel measures it.

## The task

150 tasks: 6 target levels × 25 topics. Each asks for a coherent passage on a
topic, readable at a given HSK 3.0 level, at roughly a given length.

```json
{"task_id": "food-L2", "target_level": 2, "target_chars": 90,
 "char_tolerance": 25, "held_out_topic": false, "threshold": 0.95,
 "prompt": "Write a coherent passage in Simplified Chinese about a meal ..."}
```

20 topics come from the domains covered by the public corpus; **5 are held out**
(technology, environment, history, books, films) so a system tuned on the corpus
can be tested on unseen subject matter.

## Why it isn't circular

The obvious benchmark — "predict the HSK level of this text" — is worthless
when the labels come from the grader being tested. It measures whether a model
memorised a character list.

WriteToLevel inverts this. **The grader is the metric, not the label.** A model
must produce text that survives an objective check, the way generated code must
survive a compiler. Scoring involves no model, no judge and no API key, so any
result is exactly reproducible.

## Scoring

```bash
python3 benchmark/evaluate.py predictions.jsonl --per-level
```

Submissions are JSONL, one object per task:

```json
{"task_id": "food-L2", "output": "我今天吃了米饭和鸡蛋。..."}
```

| Metric | Meaning |
| --- | --- |
| **Level accuracy** | Share of tasks where the measured level ≤ the target. The headline. |
| **Mean signed error** | Measured − target, in levels. Positive means too hard. |
| **Too hard / too easy** | The direction of failure, which differs sharply by level. |
| **Length compliance** | Within the stated tolerance. Blocks the degenerate "write three easy characters" strategy. |
| **Budget violations** | Share of outputs where one character alone exceeds the 5% above-target budget. |
| **Public / held-out** | Accuracy split by topic origin. |

Unanswered tasks score as failures — otherwise a system could answer only the
easy levels. Off-scale output is scored one step beyond the 7–9 band.

**Coherence is not scored here**, deliberately. Judging it needs a human or a
model and would make the metric unreproducible. Run it separately and report it
alongside; a submission that games the level metric with incoherent text is
obvious to any reader, and the length constraint rules out the trivial attack.

## Reference points

| System | Level accuracy | Mean signed error |
| --- | --- | --- |
| deepseek-chat (temp 0) | **66.7%** | +0.24 |
| deepseek-reasoner (temp 0) | 64.0% | +0.49 |
| Human authors (corpus, written to target) | 61.8% | +0.27 |
| Corpus retrieval (no model, ignores topic) | 59.3% | +0.27 |

**Read the per-level curve, not the aggregate.** `deepseek-chat` scores
16 / 24 / 72 / 88 / 100 / 100 across HSK 1–6; `deepseek-reasoner` scores
48 / 48 / 80 / 80 / 76 / 52. They are 2.7 points apart overall and 48 apart at
HSK 6. The perfect scores at the top are
not skill: at HSK 5–6 a 95% bar drawn against the 1,940 characters graded at
HSK 6 or below is satisfied by
almost any fluent Chinese, so the constraint barely binds. **HSK 1–2 is the
discriminating region**, and a system answering only the top three levels would
score 96%. Always report `--per-level`.

The human figure is the number to beat, and it is not 100%. Careful authors
working to an explicit level target still miss it four times in ten, and
systematically: **+1.23 levels too hard** on the easiest shelf, **−0.75 too
easy** on the hardest. Authors regress toward the middle regardless of the
target. That is the practical argument for an objective grader in the authoring
loop.

Reproduce both:

```bash
python3 benchmark/baselines/human_reference.py
python3 benchmark/baselines/retrieval.py > /tmp/retrieval.jsonl
python3 benchmark/evaluate.py /tmp/retrieval.jsonl --per-level
```

## Running a model

```bash
export DEEPSEEK_API_KEY=...          # or ANTHROPIC_API_KEY / OPENAI_API_KEY
python3 benchmark/baselines/run_model.py --api deepseek --model deepseek-chat > preds.jsonl
python3 benchmark/evaluate.py preds.jsonl --per-level --name deepseek-chat
```

No third-party packages. **Report decoding parameters** — temperature
materially affects level accuracy, since a model sampling freely wanders off
the character budget. The default here is temperature 0.

## Submitting

Open a pull request adding your scored report to `benchmark/results/`, with the
model name, version, date, decoding parameters, and whether the model saw the
public corpus. Include the raw predictions file so the score can be recomputed.

## Regenerating the tasks

```bash
python3 benchmark/build_tasks.py
```

Deterministic — the committed `tasks.jsonl` is exactly what this emits.
