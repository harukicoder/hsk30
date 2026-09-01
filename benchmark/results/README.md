# Results

Each entry carries the raw predictions so any score can be recomputed:

```bash
python3 ../evaluate.py deepseek-chat_predictions.jsonl --per-level
```

| System | Date | Overall | HSK 1 | HSK 2 | HSK 3 | HSK 4 | HSK 5 | HSK 6 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| deepseek-chat, temp 0 | 2026-09-01 | 66.7% | 16% | 24% | 72% | 88% | 100% | 100% |
| Human authors | — | 61.8% | — | — | — | — | — | — |
| Corpus retrieval | — | 59.3% | 12% | 56% | 84% | 60% | 64% | 80% |

**The aggregate is not the result.** Scores at HSK 5–6 are near-vacuous: a 95%
coverage bar drawn against 2,600+ characters is met by almost any fluent
Chinese. HSK 1–2 is where the constraint binds and where systems separate.

## Submitting

Add your predictions file and a row here, with model name, version, date, and
decoding parameters. Note whether the model may have seen the public corpus.
