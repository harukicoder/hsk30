"""utils.process_results must score exactly as benchmark/evaluate.py does.

    python benchmark/lm_eval/writetolevel/check_writetolevel.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(BENCH, "..", "src"))
sys.path.insert(0, BENCH)
sys.path.insert(0, HERE)

import evaluate  # noqa: E402
import utils  # noqa: E402

tasks = [json.loads(l) for l in open(os.path.join(BENCH, "tasks.jsonl"), encoding="utf-8") if l.strip()]
for system in sys.argv[1:] or ["deepseek-chat", "gpt-4o", "qwen3-235b"]:
    preds = {}
    for line in open(os.path.join(BENCH, "results", system + "_predictions.jsonl"), encoding="utf-8"):
        if line.strip():
            p = json.loads(line)
            preds.setdefault(p["task_id"], p.get("output", ""))
    got = [utils.process_results(t, [preds.get(t["task_id"], "")]) for t in tasks]
    want = evaluate.aggregate([evaluate.score_one(t, preds.get(t["task_id"], "")) for t in tasks])
    n = len(got)
    acc = sum(g["level_accuracy"] for g in got) / n
    err = sum(g["signed_error"] for g in got) / n
    ln = sum(g["length_compliance"] for g in got) / n
    bv = sum(g["budget_violation"] for g in got) / n
    print(f"{system}: accuracy {acc:.4f}/{want['level_accuracy']} error {err:.3f}/{want['mean_signed_error']} "
          f"length {ln:.4f}/{want['length_compliance']} budget {bv:.4f}/{want['budget_violation_rate']}")
    assert abs(acc - want["level_accuracy"]) < 1e-3
    assert abs(err - want["mean_signed_error"]) < 1e-2
    assert abs(ln - want["length_compliance"]) < 1e-3
    assert abs(bv - want["budget_violation_rate"]) < 1e-3
print("ok")
