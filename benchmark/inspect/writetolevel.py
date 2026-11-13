"""WriteToLevel as an Inspect task.

    pip install inspect_ai hsk30
    inspect eval benchmark/inspect/writetolevel.py --model openai/gpt-4o
    inspect eval benchmark/inspect/writetolevel.py -T level=1 --model ...

Can a model write Chinese at the HSK level it was asked for? 150 tasks: six
target levels x 25 topics, five of them held out. Each asks for a passage on
a topic, readable at a given level of the HSK 3.0 exam syllabus, at roughly a
given length.

The grader is the metric, not the label: a passage hits its target when at
least 95% of its characters come from the target level or below, measured by
hsk30 against the 2025 examination syllabus. Scoring uses no model, no judge
and no API key, so any result is exactly reproducible, and the score is the
same as benchmark/evaluate.py gives for the same outputs (checked by
benchmark/inspect/check_writetolevel.py).

Metrics, as in the benchmark README:
  hit          level accuracy: measured level <= target (the headline)
  signed_error measured - target in levels; positive means too hard.
               Off-scale text counts as one step beyond the 7-9 band.
  length_ok    within the task's character tolerance
  over_budget  one character alone exceeds the 5% above-target budget

Read the per-level results, not only the aggregate: HSK 1-2 is where systems
differ. At HSK 5-6 a 95% bar is met by almost any fluent Chinese.
"""

from __future__ import annotations

import json
import os
from typing import Optional

import hsk30
from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.model import GenerateConfig
from inspect_ai.scorer import Score, Target, accuracy, mean, scorer, stderr
from inspect_ai.solver import TaskState, generate

TASKS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tasks.jsonl")

#: Text that reaches no level is scored one step beyond the 7-9 band, so
#: off-scale output is penalised rather than skipped.
OFF_SCALE = hsk30.BAND + 1


def score_text(text: str, target_level: int, target_chars: int,
               char_tolerance: int, threshold: float = 0.95) -> dict:
    """Score one output. Mirrors benchmark/evaluate.py:score_one exactly."""
    profile = hsk30.grade(text, threshold=threshold)
    measured = profile.level if profile.level is not None else OFF_SCALE
    _share, offenders = hsk30.budget_violations(text, target_level, threshold=threshold)
    return {
        "hit": profile.level is not None and profile.level <= target_level,
        "signed_error": measured - target_level,
        "length_ok": abs(profile.chars - target_chars) <= char_tolerance,
        "over_budget": any(sh > (1 - threshold) for _c, _l, sh in offenders),
        "measured_label": profile.label,
        "chars": profile.chars,
        "standard": profile.standard,
    }


def _samples(level: Optional[int], held_out: Optional[bool]) -> list[Sample]:
    out = []
    with open(TASKS, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            t = json.loads(line)
            if level is not None and t["target_level"] != int(level):
                continue
            if held_out is not None and bool(t.get("held_out_topic")) != bool(held_out):
                continue
            out.append(Sample(id=t["task_id"], input=t["prompt"],
                              target=str(t["target_level"]), metadata=t))
    return out


@scorer(metrics={
    "hit": [accuracy(), stderr()],
    "signed_error": [mean()],
    "length_ok": [accuracy()],
    "over_budget": [accuracy()],
})
def writetolevel_scorer():
    async def score(state: TaskState, target: Target) -> Score:
        t = state.metadata
        text = state.output.completion if state.output else ""
        r = score_text(text, t["target_level"], t["target_chars"],
                       t.get("char_tolerance", 0), t.get("threshold", 0.95))
        return Score(
            value={"hit": int(r["hit"]), "signed_error": r["signed_error"],
                   "length_ok": int(r["length_ok"]), "over_budget": int(r["over_budget"])},
            answer=text,
            explanation=(f"measured HSK {r['measured_label']} against target "
                         f"{hsk30.label(t['target_level'])} ({r['chars']} characters, "
                         f"graded against the {r['standard']} syllabus)"),
            metadata={"target_level": t["target_level"], "held_out_topic": t.get("held_out_topic", False)},
        )
    return score


@task
def writetolevel(level: Optional[int] = None, held_out: Optional[bool] = None) -> Task:
    """WriteToLevel. level: only one target level (1-6); held_out: only held-out
    (True) or public (False) topics."""
    return Task(
        dataset=MemoryDataset(_samples(level, held_out), name="writetolevel"),
        solver=[generate()],
        scorer=writetolevel_scorer(),
        config=GenerateConfig(temperature=0.0),
    )
