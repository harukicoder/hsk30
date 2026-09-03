# Chinese CEFR Labels Inherit an Ambiguity

A short note extending the main paper to the CEFR. If "HSK 3.0" names two
documents that disagree, and Chinese is placed on the CEFR through HSK, does
the disagreement survive projection onto six coarser bands?

It does. 46.1% of the corpus changes CEFR band depending on which document was
used, 44.1% under a correspondence that compresses HSK levels, and 42 of the 47
movements are upward — the corpus is not relabelled noisily, it is relabelled
harder.

Written for the multilingual CEFR resource community, which as of 2025 covers
thirteen languages and no Chinese.

```bash
python3 ../../scripts/cefr_mapping.py        # regenerates every figure here
./build.sh                                   # builds main.pdf
```

The note is explicit that its labels are algorithmic projections, not
expert-assigned CEFR levels, and that the corpus is LLM-assisted. It proposes a
constraint on future Chinese CEFR entries, not a dataset entry.
