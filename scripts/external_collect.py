"""Collect an external, human-authored, permissively licensed Chinese sample.

The paper's regrading result is measured on a corpus the author wrote. This
collects text he did not write, from two genres, so the finding can be tested
outside its own material. Nothing here is redistributed: the script saves what
it fetched so the run is reproducible, and the texts stay local.

  zh.wikipedia.org  CC BY-SA 4.0  encyclopedic prose
  zh.wikinews.org   CC BY 2.5     news prose
"""
import json, sys, time, urllib.parse, urllib.request

UA = "hsk30-research/0.2 (alvaro.serrano.gp@gmail.com)"
MIN_CHARS, MAX_CHARS = 120, 1200


def fetch(host, n, sink, batch=50):
    out, seen = [], set()
    while len(out) < n:
        q = urllib.parse.urlencode({
            "action": "query", "format": "json", "generator": "random",
            "grnnamespace": "0", "grnlimit": str(batch), "prop": "extracts",
            "explaintext": "1", "exintro": "1", "variant": "zh-cn",
        })
        req = urllib.request.Request("https://%s/w/api.php?%s" % (host, q),
                                     headers={"User-Agent": UA})
        try:
            data = json.load(urllib.request.urlopen(req, timeout=30))
        except Exception as e:
            print("  fetch error: %s" % e, file=sys.stderr); time.sleep(2); continue
        for p in data.get("query", {}).get("pages", {}).values():
            title, text = p.get("title", ""), (p.get("extract") or "").strip()
            text = " ".join(text.split())
            if title in seen or not (MIN_CHARS <= len(text) <= MAX_CHARS):
                continue
            seen.add(title)
            row = {"source": host, "title": title, "text": text}
            out.append(row)
            sink.write(json.dumps(row, ensure_ascii=False) + "\n")
            sink.flush()
            if len(out) >= n:
                break
        print("  %s: %d" % (host, len(out)), file=sys.stderr)
        time.sleep(0.2)
    return out


if __name__ == "__main__":
    with open("external.jsonl", "w", encoding="utf-8") as fh:
        rows = fetch("zh.wikipedia.org", 250, fh) + fetch("zh.wikinews.org", 150, fh)
    print("saved %d texts" % len(rows))
