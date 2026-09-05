# Which Chinese Standard?

A short note comparing the mainland and Taiwan proficiency standards word by
word. Everything published on this comparison is exam-choice guidance; no
item-level comparison of the inventories appears to exist.

```bash
# 1. download the official spreadsheets, free, from the issuing bodies
#    TBCL   https://coct.naer.edu.tw/page.jsp?ID=41   (漢字表, 詞語表 .xlsx)
#    TOCFL  https://tocfl.edu.tw/tocfl/index.php/teach/download
python3 ../../scripts/tbcl_extract.py --chars tbcl_chars.xlsx \
        --words tbcl_words.xlsx --out tbcl.json
python3 ../../scripts/crossstrait.py --tbcl tbcl.json
./build.sh
```

Neither Taiwan inventory is redistributed. NAER and SC-TOP assert rights over
them, so the code ships and the data does not.

## The two things this note is careful about

**It validates before it claims.** The pipeline is run over the two mainland
documents first, where the answer is already published, and reproduces
`doi:10.5281/zenodo.22239032` exactly — 41.5% of shared words and 40.7% of
shared characters. Only then is it pointed across the strait.

**It refuses the headline it could have had.** At a 1:1 level alignment the
mainland syllabus appears to grade shared vocabulary harder by 4,783 words to
598. Shifting TBCL by one level reverses that to 1,234 against 2,421. The
disagreement *rate* survives every alignment tested; the *direction* does not,
and is not claimed. `crossstrait.py` prints the sensitivity table on every run
so the figure cannot be quoted without it.
