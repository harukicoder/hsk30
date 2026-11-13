"""Regenerate space/index.html from template.html and hsk30's character tables.

    python3 space/build.py

The Space is a static page (Hugging Face no longer hosts Gradio Spaces on the
free tier), so the tables are embedded in the page as compact JSON.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "js", "data")


def entries(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)["entries"]


def group(table):
    out = {}
    for item, level in table.items():
        out.setdefault(level, []).append(item)
    return {str(k): "".join(sorted(v)) for k, v in sorted(out.items())}


t2s = json.load(open(os.path.join(DATA, "t2s.json"), encoding="utf-8"))
data = {
    "chars": {"2025": group(entries("chars-2025.json")), "2021": group(entries("chars-2021.json"))},
    "t2s": "".join(k + v for k, v in t2s.items()),
}
blob = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
with open(os.path.join(HERE, "template.html"), encoding="utf-8") as fh:
    page = fh.read().replace("__DATA__", blob)
with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as fh:
    fh.write(page)
print("wrote space/index.html (%d bytes)" % len(page.encode("utf-8")))
