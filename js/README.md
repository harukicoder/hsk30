# hsk30 for JavaScript

Grade Chinese text against a **named** HSK document, in Node or the browser.

```bash
npm install hsk30
```

```js
import { grade } from "hsk30";

const p = grade("我昨天去商店买了一个苹果。");
p.label        // "2"   (a level-1 reader knows 91.7% of the characters; the bar is 95%)
p.standardId   // "hsk-syllabus-2025"
p.curve()      // { "1": 0.917, "2": 1, ..., "7-9": 1 }
```

"HSK 3.0" names two official documents:

- the **2025 examination syllabus** (新版HSK考试大纲). The exam uses it from 13 December 2026, and it is the default here;
- the **2021 national grading standard** (GF0025-2021).

They place 41.5% of the words they share at different levels. For example, 苹果 is level 1 in the syllabus and level 3 in the standard, and 用 is the reverse. So every result says which document produced it:

```js
grade(text, { standard: "2021" }).standardId   // "gf0025-2021"
```

This is a port of the Python package [`hsk30`](https://github.com/harukicoder/hsk30) (`pip install hsk30`, doi:10.5281/zenodo.22234657). It reads the same tables, and its tests check that it returns the same grade as the Python package on 276 texts.

## What a grade means

A text's level is the lowest level at which a reader knows at least 95% of its characters, which is the usual comprehensible-input threshold. `null` (label `"beyond HSK 9"`) means no level reaches it. Characters are graded against the document's own character list:
- 3,088 recognition characters (认读字) in the 2025 syllabus;
- 3,000 characters in the 2021 standard.

## API

| Function | Returns |
|---|---|
| `grade(text, { standard, threshold, exclude, script })` | `Profile`: `level`, `label`, `chars`, `ungraded`, `standard`, `standardId`, `script`, `coverageAt(level)`, `curve()` |
| `gradeTokens(tokens, { standard, excludeProperNouns })` | `Profile`, leaving out proper nouns, detected from capitalised pinyin (`Lǐ Míng`, `Ōuzhōu`) |
| `budgetViolations(text, target)` | `[share, [[char, level, share], ...]]`: the characters that hold the text above `target`, worst first |
| `writingProfile(text)` | Handwriting against the 1,200 书写字. Gives the level for the writable part and the `ceiling` (share the writing list covers at all) |
| `words(standard)`, `characters(standard, kind)` | The graded tables, `{ item: level }`. Level 7 is the single 7–9 band |
| `convertTraditional(text)`, `looksTraditional(text)` | Traditional input is converted before grading, and `profile.script` records that it was. The result is an upper bound, since 乾, 幹 and 榦 all become 干 |

`standard` accepts `"2025"` (also `"exam"`, `"syllabus"`), `"2021"` (also `"3.0"`, `"standard"`), `"2012"` and `"2.0"`. The last two are word lists only, because HSK 2.0 graded no characters.

Tables load on first use, so grading against one document doesn't load the others. All the data together is about 440 KB of JSON.

## Data

The tables are generated from the Python package's data by `scripts/build-data.mjs`. Each file keeps the `standard:` declaration of its source, as identifiers from the [registry](https://github.com/harukicoder/hsk30/blob/main/spec/standards.json). The word and character levels are facts from the official documents, and no ownership of them is claimed. For the full 2025 syllabus with all 11,000 entries, homograph readings and pinyin, see [`corpus/syllabus2025`](https://github.com/harukicoder/hsk30/tree/main/corpus/syllabus2025).

MIT licence.
