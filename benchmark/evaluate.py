#!/usr/bin/env python3
"""Score a submission against WriteToLevel.

    python3 benchmark/evaluate.py predictions.jsonl [--per-level] [--json]

A submission is JSONL, one object per task::

    {"task_id": "food-L2", "output": "我今天吃了米饭和鸡蛋。..."}

Scoring is deterministic — no model, no judge, no API key.  The grader in this
repository *is* the metric, the way a compiler is the metric for generated
code.  That is the point: a benchmark whose labels came from the same grader
being tested would only measure whether a model had memorised a character
list.  Here the model must produce text that survives an objective check.

Coherence is deliberately NOT scored here.  It needs human or model judgement
and would make the metric unreproducible; run it separately and report it
alongside.  A submission that games the level metric with incoherent text will
be obvious to any reader, and the length constraint blocks the degenerate
"write three easy characters" strategy.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

import hsk30
from hsk30 import BAND

HERE = os.path.dirname(os.path.abspath(__file__))
TASKS = os.path.join(HERE, "tasks.jsonl")

#: A text that reaches no level is scored one step beyond the band, so a system
#: that emits off-scale text is penalised rather than silently skipped.
OFF_SCALE = BAND + 1


def load_jsonl(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def score_one(task, output):
    text = str(output or "")
    profile = hsk30.grade(text, threshold=task.get("threshold", 0.95))
    measured = profile.level if profile.level is not None else OFF_SCALE
    target = task["target_level"]
    share, offenders = hsk30.budget_violations(
        text, target, threshold=task.get("threshold", 0.95))
    tol = task.get("char_tolerance", 0)
    length_ok = abs(profile.chars - task["target_chars"]) <= tol
    return {
        "task_id": task["task_id"],
        "target_level": target,
        "measured_level": profile.level,
        "measured_label": profile.label,
        "hit": profile.level is not None and profile.level <= target,
        "signed_error": measured - target,
        "chars": profile.chars,
        "length_ok": length_ok,
        "above_target_share": round(share, 4),
        "over_budget_chars": [
            {"character": ch, "level": hsk30.label(lvl), "share": round(sh, 4)}
            for ch, lvl, sh in offenders if sh > (1 - task.get("threshold", 0.95))
        ],
        "empty": profile.chars == 0,
        "held_out_topic": task.get("held_out_topic", False),
    }


def aggregate(rows):
    if not rows:
        return {}
    n = len(rows)
    hits = sum(1 for r in rows if r["hit"])
    errs = [r["signed_error"] for r in rows]
    return {
        "n": n,
        "level_accuracy": round(hits / n, 4),
        "mean_signed_error": round(sum(errs) / n, 3),
        "mean_abs_error": round(sum(abs(e) for e in errs) / n, 3),
        "too_hard": round(sum(1 for e in errs if e > 0) / n, 4),
        "too_easy": round(sum(1 for e in errs if e < 0) / n, 4),
        "length_compliance": round(sum(1 for r in rows if r["length_ok"]) / n, 4),
        "budget_violation_rate": round(
            sum(1 for r in rows if r["over_budget_chars"]) / n, 4),
        "empty_outputs": sum(1 for r in rows if r["empty"]),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Score a submission against WriteToLevel.")
    ap.add_argument("predictions", help="JSONL of {task_id, output}")
    ap.add_argument("--tasks", default=TASKS)
    ap.add_argument("--per-level", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--name", default=None, help="system name for the report")
    args = ap.parse_args()

    tasks = {t["task_id"]: t for t in load_jsonl(args.tasks)}
    preds = load_jsonl(args.predictions)

    seen, rows, unknown = set(), [], []
    for pred in preds:
        tid = pred.get("task_id")
        if tid not in tasks:
            unknown.append(tid)
            continue
        if tid in seen:
            continue  # first submission for a task wins
        seen.add(tid)
        rows.append(score_one(tasks[tid], pred.get("output", "")))

    missing = sorted(set(tasks) - seen)
    # Unanswered tasks score as failures, or a system could game the metric by
    # answering only the easy levels.
    for tid in missing:
        rows.append({
            "task_id": tid, "target_level": tasks[tid]["target_level"],
            "measured_level": None, "measured_label": "missing", "hit": False,
            "signed_error": OFF_SCALE - tasks[tid]["target_level"], "chars": 0,
            "length_ok": False, "above_target_share": 1.0, "over_budget_chars": [],
            "empty": True, "held_out_topic": tasks[tid].get("held_out_topic", False),
        })

    report = {
        "system": args.name or os.path.basename(args.predictions),
        "overall": aggregate(rows),
        "public_topics": aggregate([r for r in rows if not r["held_out_topic"]]),
        "held_out_topics": aggregate([r for r in rows if r["held_out_topic"]]),
        "missing_tasks": len(missing),
        "unknown_task_ids": len(unknown),
    }
    if args.per_level:
        by_level = defaultdict(list)
        for r in rows:
            by_level[r["target_level"]].append(r)
        report["per_level"] = {str(k): aggregate(v) for k, v in sorted(by_level.items())}

    if args.json:
        print(json.dumps({"report": report, "items": rows}, ensure_ascii=False, indent=2))
        return 0

    o = report["overall"]
    print("WriteToLevel — %s" % report["system"])
    print("  tasks scored          %d (%d missing, %d unknown ids)"
          % (o["n"], report["missing_tasks"], report["unknown_task_ids"]))
    print("  level accuracy        %.1f%%" % (100 * o["level_accuracy"]))
    print("  mean signed error     %+.2f levels  (+ = too hard)" % o["mean_signed_error"])
    print("  too hard / too easy   %.1f%% / %.1f%%"
          % (100 * o["too_hard"], 100 * o["too_easy"]))
    print("  length compliance     %.1f%%" % (100 * o["length_compliance"]))
    print("  budget violations     %.1f%%" % (100 * o["budget_violation_rate"]))
    print("  public / held-out     %.1f%% / %.1f%%"
          % (100 * report["public_topics"]["level_accuracy"],
             100 * report["held_out_topics"]["level_accuracy"]))
    if args.per_level:
        print("\n  target   n   accuracy   signed err")
        for lvl, agg in report["per_level"].items():
            print("  HSK %-4s %3d   %6.1f%%   %+9.2f"
                  % (lvl, agg["n"], 100 * agg["level_accuracy"],
                     agg["mean_signed_error"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
