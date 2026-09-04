#!/usr/bin/env python3
"""Run a language model over the WriteToLevel tasks and write a submission.

    export ANTHROPIC_API_KEY=...
    python3 benchmark/baselines/run_model.py --model claude-opus-4-5 > preds.jsonl
    python3 benchmark/evaluate.py preds.jsonl --per-level --name claude-opus-4-5

    # any OpenAI-compatible endpoint
    export DEEPSEEK_API_KEY=...
    python3 benchmark/baselines/run_model.py --api deepseek \
        --model deepseek-chat > preds.jsonl

    # OpenRouter, which reaches several labs behind one key
    python3 benchmark/baselines/run_model.py --api openrouter \
        --model qwen/qwen3-235b-a22b-2507 > preds.jsonl

    # or point at any other compatible server
    python3 benchmark/baselines/run_model.py --api openai \
        --base-url https://host/v1/chat/completions --model some-model

No third-party packages: the request is a few lines of urllib, which keeps the
benchmark runnable without a dependency stack that would itself need pinning
for reproducibility.

**Report your decoding parameters.** Temperature materially affects
level accuracy on this task — a model that samples freely wanders off the
character budget — so a leaderboard entry without them is not reproducible.
The defaults here (temperature 0) are the ones we recommend reporting against.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
TASKS = os.path.join(HERE, "..", "tasks.jsonl")

ENDPOINTS = {
    "anthropic": "https://api.anthropic.com/v1/messages",
    "openai": "https://api.openai.com/v1/chat/completions",
    "deepseek": "https://api.deepseek.com/v1/chat/completions",
    "openrouter": "https://openrouter.ai/api/v1/chat/completions",
}

#: Which environment variable holds the key for each provider.
KEY_ENV = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}

#: A key may live in a file instead of the environment. This keeps it out of
#: shell history and out of any transcript: write it once, chmod 600, forget it.
KEY_FILES = {
    "anthropic": "~/.config/hsk30/anthropic.key",
    "openai": "~/.config/hsk30/openai.key",
    "deepseek": "~/.config/hsk30/deepseek.key",
    "openrouter": "~/.config/hsk30/openrouter.key",
}


def load_key(api):
    """Environment first, then the key file. Never echo what is found."""
    key = os.environ.get(KEY_ENV[api])
    if key:
        return key.strip()
    path = os.path.expanduser(KEY_FILES[api])
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            return fh.read().strip()
    return None


def post(url, payload, headers, timeout=120):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def call(api, model, prompt, key, temperature, max_tokens, base_url=None):
    if api == "anthropic":
        body = post(base_url or ENDPOINTS["anthropic"], {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }, {
            "content-type": "application/json",
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
        })
        return "".join(b.get("text", "") for b in body.get("content", []))
    # deepseek and openai share the chat-completions shape.
    body = post(base_url or ENDPOINTS[api], {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }, {
        "content-type": "application/json",
        "authorization": "Bearer " + key,
    })
    msg = body["choices"][0]["message"]
    # Reasoning models sometimes return a null content with the answer in a
    # separate field; treat a missing answer as empty rather than crashing the
    # run, so one bad response costs one task and not the whole submission.
    return msg.get("content") or msg.get("reasoning") or ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", required=True)
    ap.add_argument("--api", default="anthropic", choices=sorted(ENDPOINTS))
    ap.add_argument("--base-url", default=None,
                    help="override the endpoint for a compatible server")
    ap.add_argument("--tasks", default=TASKS)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--max-tokens", type=int, default=2048)
    ap.add_argument("--limit", type=int, default=0, help="first N tasks, for a smoke test")
    ap.add_argument("--retries", type=int, default=3)
    args = ap.parse_args()

    key = load_key(args.api)
    if not key:
        print("no key: set %s, or write it to %s (chmod 600)"
              % (KEY_ENV[args.api], KEY_FILES[args.api]), file=sys.stderr)
        return 1

    with open(args.tasks, encoding="utf-8") as fh:
        tasks = [json.loads(line) for line in fh if line.strip()]
    if args.limit:
        tasks = tasks[:args.limit]

    done = failed = 0
    for task in tasks:
        text = ""
        for attempt in range(args.retries):
            try:
                text = call(args.api, args.model, task["prompt"], key,
                            args.temperature, args.max_tokens, args.base_url)
                break
            except (urllib.error.HTTPError, urllib.error.URLError, KeyError) as exc:
                if attempt == args.retries - 1:
                    print("  %s failed: %s" % (task["task_id"], exc), file=sys.stderr)
                    failed += 1
                else:
                    # Back off on rate limits rather than hammering.
                    time.sleep(2 ** attempt)
        # An empty output is a legitimate result and scores as a failure; it is
        # not silently dropped, or the missing-task penalty would be dodged.
        sys.stdout.write(json.dumps(
            {"task_id": task["task_id"], "output": text.strip()},
            ensure_ascii=False) + "\n")
        sys.stdout.flush()
        done += 1
        if done % 25 == 0:
            print("  %d/%d" % (done, len(tasks)), file=sys.stderr)

    print("done: %d tasks, %d failed" % (done, failed), file=sys.stderr)
    print("model=%s api=%s temperature=%s max_tokens=%s"
          % (args.model, args.api, args.temperature, args.max_tokens), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
