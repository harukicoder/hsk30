import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import hsk30, { grade, gradeTokens, budgetViolations, writingProfile, words, characters, resolve, label } from "../index.mjs";

const require = createRequire(import.meta.url);
const fixture = JSON.parse(readFileSync(new URL("./python-fixture.json", import.meta.url), "utf8"));
const close = (a, b) => Math.abs(a - b) < 1e-9;

test("CommonJS and ESM expose the same API", () => {
  const cjs = require("../index.cjs");
  assert.equal(cjs.grade, hsk30.grade);
  assert.equal(typeof cjs.gradeTokens, "function");
});

test("table sizes match the documents", () => {
  assert.equal(Object.keys(words("2025")).length, 10896);
  assert.equal(Object.keys(words("2021")).length, 10977);
  assert.equal(Object.keys(characters("2025")).length, 3088);
  assert.equal(Object.keys(characters("2021")).length, 3000);
  assert.equal(Object.keys(characters("2025", "writing")).length, 1200);
});

test("the two documents disagree where they should", () => {
  // 苹果 is level 1 in the exam syllabus and level 3 in the 2021 standard; 用 the reverse.
  assert.equal(words("2025")["苹果"], 1);
  assert.equal(words("2021")["苹果"], 3);
  assert.equal(words("2025")["用"], 3);
  assert.equal(words("2021")["用"], 1);
});

test("every result names its document", () => {
  const p = grade("我是中国人。");
  assert.equal(p.label, "1");
  assert.equal(p.standard, "2025");
  assert.equal(p.standardId, "hsk-syllabus-2025");
  assert.equal(grade("我是中国人。", { standard: "2021" }).standardId, "gf0025-2021");
});

test("traditional input is converted and recorded", () => {
  assert.equal(grade("我是中國人。").script, "traditional");
  assert.equal(grade("我是中國人。").label, "1");
});

test("standards resolve and reject", () => {
  assert.equal(resolve("exam"), "2025");
  assert.equal(resolve("3.0"), "2021");
  assert.throws(() => resolve("hsk9"), RangeError);
  assert.throws(() => characters("2.0"), RangeError);
  assert.throws(() => characters("2021", "writing"), RangeError);
  assert.equal(label(null), "beyond HSK 9");
  assert.equal(label(7), "7-9");
});

test(`grade() matches the Python package on ${fixture.grade.length} texts`, () => {
  for (const want of fixture.grade) {
    const got = grade(want.text, { standard: want.standard });
    const where = `${want.standard}: ${want.text.slice(0, 20)}`;
    assert.equal(got.level, want.level, where);
    assert.equal(got.chars, want.chars, where);
    assert.equal(got.ungraded, want.ungraded, where);
    assert.equal(got.script, want.script, where);
    for (const [lvl, v] of Object.entries(want.curve)) assert.ok(close(got.curve()[lvl], v), `${where} @${lvl}`);
  }
});

test("gradeTokens() matches the Python package", () => {
  const recs = readFileSync(new URL("../../corpus/hsk30_graded_readers.jsonl", import.meta.url), "utf8")
    .trim().split("\n").slice(0, 30).map(JSON.parse);
  const byId = new Map(recs.map(r => [r.id, r]));
  for (const want of fixture.tokens) {
    const r = byId.get(want.id);
    const toks = r.sentences.flatMap(s => s.words || []);
    const got = gradeTokens(toks, { standard: want.standard });
    assert.equal(got.level, want.level, want.id);
    assert.equal(got.chars, want.chars, want.id);
  }
});

test("budgetViolations() matches the Python package", () => {
  for (const want of fixture.budget) {
    const [share, ranked] = budgetViolations(want.text, 2);
    assert.ok(close(share, want.share));
    assert.equal(ranked.length, want.ranked.length);
    ranked.forEach(([c, l, s], i) => {
      assert.equal(c, want.ranked[i][0]);
      assert.equal(l, want.ranked[i][1]);
      assert.ok(close(s, want.ranked[i][2]));
    });
  }
});

test("writingProfile() matches the Python package", () => {
  for (const want of fixture.writing) {
    const got = writingProfile(want.text);
    assert.equal(got.level, want.level);
    assert.equal(got.outside, want.outside);
    assert.ok(close(got.ceiling, want.ceiling));
  }
});
