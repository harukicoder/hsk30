"""The Inspect task must score exactly as benchmark/evaluate.py does.

    pip install inspect_ai
    python benchmark/inspect/test_writetolevel.py

Replays a published baseline's outputs through Inspect's mock model and
compares level accuracy, mean signed error and length compliance with what
benchmark/evaluate.py gives for the same outputs. Needs no API key.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))
sys.path.insert(0, HERE)

from inspect_ai import eval as inspect_eval  # noqa: E402
from inspect_ai.model import ModelOutput, get_model  # noqa: E402

from writetolevel import TASKS, writetolevel  # noqa: E402

RESULTS = os.path.join(HERE, "..", "results")


def run(system: str) -> None:
    tasks = [json.loads(l) for l in open(TASKS, encoding="utf-8") if l.strip()]
    preds = {}
    for line in open(os.path.join(RESULTS, system + "_predictions.jsonl"), encoding="utf-8"):
        if line.strip():
            p = json.loads(line)
            preds.setdefault(p["task_id"], p.get("output", ""))
    outputs = [ModelOutput.from_content("mockllm/model", preds.get(t["task_id"], "")) for t in tasks]
    model = get_model("mockllm/model", custom_outputs=outputs)
    log = inspect_eval(writetolevel(), model=model, log_dir=os.path.join(HERE, ".logs"),
                       display="none", max_connections=1, max_samples=1)[0]
    assert log.status == "success", log.status
    got = {}
    for s in log.results.scores:
        for name, m in s.metrics.items():
            got[(s.name, name)] = m.value
    # Expected values from the benchmark's own scorer, computed now, so the
    # comparison holds even if the data tables are updated.
    sys.path.insert(0, os.path.join(HERE, ".."))
    import evaluate  # noqa: E402
    rows = [evaluate.score_one(t, preds.get(t["task_id"], "")) for t in tasks]
    overall = evaluate.aggregate(rows)
    want_acc = overall["level_accuracy"]
    want_err = overall["mean_signed_error"]
    want_len = overall["length_compliance"]
    acc = got[("hit", "accuracy")]
    err = got[("signed_error", "mean")]
    ln = got[("length_ok", "accuracy")]
    print(f"{system}: accuracy {acc:.4f} (evaluate.py {want_acc}), signed error {err:.3f} "
          f"(evaluate.py {want_err}), length {ln:.4f} (evaluate.py {want_len})")
    assert abs(acc - want_acc) < 1e-3
    assert abs(err - want_err) < 1e-2
    assert abs(ln - want_len) < 1e-3


if __name__ == "__main__":
    for system in sys.argv[1:] or ["deepseek-chat", "gpt-4o"]:
        run(system)
    print("ok")
