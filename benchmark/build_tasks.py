#!/usr/bin/env python3
"""Generate the HSKBench task set.

Deterministic: the committed tasks.jsonl is exactly what this emits.  Rerun
after editing TOPICS or LENGTHS, and commit the result.

    python3 benchmark/build_tasks.py
"""

from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "tasks.jsonl")

# Topics a Chinese teacher actually assigns.  Held-out topics are marked so a
# system tuned on the public corpus can be tested on unseen subject matter.
TOPICS = [
    ("daily_routine",   "a person's ordinary weekday", False),
    ("family",          "members of a family and what they do", False),
    ("food",            "a meal and the food in it", False),
    ("weather",         "the weather and how it changes plans", False),
    ("school",          "a day at school or university", False),
    ("shopping",        "buying something in a shop or online", False),
    ("travel",          "a short trip to another city", False),
    ("transport",       "getting somewhere by bus, train or bicycle", False),
    ("hobbies",         "a pastime someone enjoys", False),
    ("animals",         "a pet or an animal someone sees", False),
    ("seasons",         "a season and what people do in it", False),
    ("friendship",      "two friends and something they do together", False),
    ("health",          "feeling unwell and going to a doctor", False),
    ("work",            "a job and an ordinary day doing it", False),
    ("city_life",       "living in a big city", False),
    ("festivals",       "a Chinese festival and how it is celebrated", False),
    ("sport",           "playing or watching a sport", False),
    ("music",           "listening to or playing music", False),
    ("cooking",         "cooking a dish step by step", False),
    ("money",           "saving money or deciding what to buy", False),
    ("technology",      "using a phone or computer in daily life", True),
    ("environment",     "protecting the environment", True),
    ("history",         "something that happened long ago", True),
    ("books",           "reading a book and what it was about", True),
    ("films",           "watching a film and what happened in it", True),
]

# Length in characters, scaled so the task is realistic at each level: a
# beginner passage that runs 300 characters is not a beginner passage.
LENGTHS = {1: (60, 20), 2: (90, 25), 3: (140, 35), 4: (220, 50), 5: (280, 60), 6: (320, 70)}

PROMPT = (
    "Write a coherent passage in Simplified Chinese about {desc}. "
    "It must be readable by a learner at HSK level {level}: at least 95% of "
    "its characters must come from HSK levels 1-{level} of the HSK 3.0 "
    "grading standard (《国际中文教育中文水平等级标准》, GF0025-2021). "
    "Aim for about {chars} characters (±{tol}). "
    "Write only the passage — no pinyin, no translation, no commentary."
)


def main() -> None:
    tasks = []
    for level in sorted(LENGTHS):
        chars, tol = LENGTHS[level]
        for topic, desc, held_out in TOPICS:
            tasks.append({
                "task_id": "%s-L%d" % (topic, level),
                "topic": topic,
                "target_level": level,
                "target_chars": chars,
                "char_tolerance": tol,
                "held_out_topic": held_out,
                "threshold": 0.95,
                "prompt": PROMPT.format(desc=desc, level=level, chars=chars, tol=tol),
            })
    with open(OUT, "w", encoding="utf-8") as fh:
        for task in tasks:
            fh.write(json.dumps(task, ensure_ascii=False) + "\n")
    held = sum(1 for t in tasks if t["held_out_topic"])
    print("wrote %s" % os.path.relpath(OUT))
    print("  %d tasks: %d levels x %d topics" % (len(tasks), len(LENGTHS), len(TOPICS)))
    print("  %d on held-out topics, %d on public-corpus topics" % (held, len(tasks) - held))


if __name__ == "__main__":
    main()
