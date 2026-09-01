# Results

Each entry carries the raw predictions so any score can be recomputed:

```bash
python3 ../evaluate.py deepseek-chat_predictions.jsonl --per-level
```

| System | Date | Overall | HSK 1 | HSK 2 | HSK 3 | HSK 4 | HSK 5 | HSK 6 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| deepseek-chat, temp 0 | 2026-09-01 | 66.7% | 16% | 24% | 72% | 88% | 100% | 100% |
| deepseek-reasoner, temp 0 | 2026-09-01 | 64.0% | 48% | 48% | 80% | 80% | 76% | 52% |
| Human authors | — | 61.8% | — | — | — | — | — | — |
| Corpus retrieval | — | 59.3% | 12% | 56% | 84% | 60% | 64% | 80% |

**The aggregate is not the result.** The two DeepSeek models sit 2.7 points
apart overall and differ by **48 points at HSK 6**, in a direction that reverses
across the scale (+32 / +24 / +8 / −8 / −24 / −48). Reasoning buys a floor and
costs a ceiling: it is worth +21 points averaged over HSK 1–3, where staying
inside a small character inventory is a planning problem, and −27 over HSK 4–6,
where the constraint barely binds and deliberation just overshoots.

Scores at HSK 5–6 are near-vacuous: a 95% bar drawn against 2,600+ characters
is met by almost any fluent Chinese. HSK 1–2 is where systems separate.

## Submitting

Add your predictions file and a row here, with model name, version, date, and
decoding parameters. Note whether the model may have seen the public corpus.
