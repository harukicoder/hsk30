# The external sample

`sample_manifest.jsonl` identifies the 400 texts used in the paper's external
validation (§6.2). One line per text:

```json
{"source": "zh.wikipedia.org", "title": "…", "revid": 12345678,
 "sha256_text": "…", "chars": 233}
```

**Why a manifest and not the texts.** Chinese Wikipedia is CC BY-SA and Wikinews
CC BY 2.5; share-alike does not sit comfortably inside an MIT repository, and
redistributing the text is unnecessary when the revision id pins it exactly.

**Why it exists at all.** `scripts/external_collect.py` samples at random, so
re-running it draws different articles and produces different numbers. Without
a manifest the reported figures would be unreproducible in principle — anyone
checking them would be measuring a different sample and finding a different
answer, with no way to tell whether the difference was theirs or ours.

## Recovering the exact sample

Each `revid` addresses one immutable revision:

    https://zh.wikipedia.org/w/index.php?oldid=<revid>

or through the API, which is what the collector used:

    https://zh.wikipedia.org/w/api.php?action=query&format=json
      &prop=extracts&explaintext=1&exintro=1&variant=zh-cn&revids=<revid>

`sha256_text` is the first 16 hex characters of the SHA-256 of the extracted
text after whitespace normalisation, so a refetch can be checked against what
was actually graded rather than assumed identical.

## Attribution

Text from Chinese Wikipedia (CC BY-SA 4.0) and Chinese Wikinews (CC BY 2.5),
by their respective contributors. Only derived measurements are published here;
no article text is redistributed.
