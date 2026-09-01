#!/usr/bin/env python3
"""A no-model baseline: answer every task with a real text from the corpus.

For each task it returns a corpus text whose shelf targets the requested level,
rotating through that shelf so the tasks at one level draw on the whole shelf
rather than the same text 25 times.  It ignores the topic entirely, so it
scores zero on relevance — its only job is to show what the level metric looks
like for authentic human text, and to give anyone integrating the harness a
submission file that runs end to end.

    python3 benchmark/baselines/retrieval.py > /tmp/retrieval.jsonl
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.join(HERE, "..", "..", "corpus", "hsk30_graded_readers.jsonl")
TASKS = os.path.join(HERE, "..", "tasks.jsonl")

SHELF_TARGET = {
    "newbie": 1, "beginner": 2, "intermediate": 3,
    "upper": 4, "advanced": 5, "native": 6,
}


def load(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def main() -> None:
    corpus, tasks = load(CORPUS), load(TASKS)
    by_level = {}
    for row in corpus:
        by_level.setdefault(SHELF_TARGET[row["shelf"]], []).append(row)

    # Sorting each shelf by length keeps the rotation deterministic and puts
    # the length-appropriate texts first for the levels where the shelf is
    # smaller than the number of tasks.
    for pool in by_level.values():
        pool.sort(key=lambda r: (r["n_chars"], r["id"]))

    cursor = {}
    for task in tasks:
        level = task["target_level"]
        pool = by_level.get(level) or corpus
        index = cursor.get(level, 0)
        cursor[level] = index + 1
        pick = pool[index % len(pool)]
        sys.stdout.write(json.dumps(
            {"task_id": task["task_id"], "output": pick["text"]},
            ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
