"use strict";
// hsk30 for JavaScript: grade Chinese text against a named HSK document.
//
// A port of the Python package (github.com/harukicoder/hsk30) that reads the
// same tables and gives the same answers; test/parity.test.mjs checks that
// against grades the Python package computed for the shipped corpus.
//
// "HSK 3.0" names two documents that place 41.5% of their shared vocabulary
// at different levels: the 2025 examination syllabus, which the exam uses
// from 13 December 2026, and the 2021 national grading standard
// (GF0025-2021). Every result therefore records which one graded it.

const DEFAULT_STANDARD = "2025";
const DEFAULT_THRESHOLD = 0.95;
const DEFAULT_BUDGET = 0.05;
const BAND = 7; // levels 7, 8 and 9 are one list; rendered "7-9"
const LEVELS = Object.freeze([1, 2, 3, 4, 5, 6, BAND]);

const STANDARDS = {
  "2025": "2025", syllabus: "2025", exam: "2025",
  "2021": "2021", "3.0": "2021", "3": "2021", standard: "2021",
  "2.0": "2.0", "2": "2.0", "2010": "2.0",
  "2012": "2012",
};

/** Canonical registry identifiers (spec/standards.json). */
const IDENTIFIERS = Object.freeze({
  "2025": "hsk-syllabus-2025",
  "2021": "gf0025-2021",
  "2012": "hsk-2012",
  "2.0": "hsk-2010",
});

// Tables load on first use, so a page that grades against one document does
// not pay for the other four.
const cache = new Map();
function table(name) {
  if (!cache.has(name)) {
    const raw = require("./data/" + name + ".json");
    cache.set(name, raw.entries || raw);
  }
  return cache.get(name);
}

function resolve(standard) {
  const key = STANDARDS[String(standard).toLowerCase()];
  if (!key) {
    throw new RangeError(
      `unknown standard ${JSON.stringify(standard)}; expected one of: 2025 (the exam syllabus), ` +
      "2021 (the grading standard), 2012 (HSK 2.0, 2012 revision), " +
      "2.0 (HSK 2.0, original 2009-10 lists)");
  }
  return key;
}

/** Graded word list: { word: level }. */
function words(standard = DEFAULT_STANDARD) {
  return table("words-" + resolve(standard));
}

/** Graded character list: { character: level }. kind is "recognition" or "writing". */
function characters(standard = DEFAULT_STANDARD, kind = "recognition") {
  const key = resolve(standard);
  if (kind !== "recognition" && kind !== "writing") {
    throw new RangeError("kind must be 'recognition' or 'writing'");
  }
  if (key === "2.0" || key === "2012") {
    throw new RangeError("HSK 2.0 has no separate character grading; use standard '2025' or '2021'");
  }
  if (kind === "writing") {
    if (key !== "2025") {
      throw new RangeError("only the 2025 exam syllabus grades writing characters separately; the 2021 standard does not");
    }
    return table("writing-2025");
  }
  return table("chars-" + key);
}

/** "3", "7-9", or "beyond HSK 9" for null. */
function label(level) {
  if (level === null || level === undefined) return "beyond HSK 9";
  return level === BAND ? "7-9" : String(level);
}

// CJK Unified Ideographs only. The standards grade none of the extensions,
// so a character from one is off-scale by definition.
const HANZI = /[一-鿿]/gu;
const PUNCT = /[，。！？；：、“”‘’（）〈〉《》【】…—·「」『』!?.,;:()"'\-\s]/gu;

function hanzi(text) {
  return String(text ?? "").match(HANZI) || [];
}

function stripPunct(text) {
  return String(text ?? "").replace(PUNCT, "");
}

/** Names are romanised with a leading capital, tone mark or not (Ōuzhōu). */
function isProperNoun(pinyin) {
  const text = String(pinyin ?? "").trim();
  if (!text) return false;
  const first = text[0].normalize("NFD")[0];
  return first !== first.toLowerCase() && first === first.toUpperCase();
}

function coverageLevel(counts, total, threshold) {
  if (!total) return null;
  let cum = 0;
  for (const level of LEVELS) {
    cum += counts.get(level) || 0;
    if (cum / total >= threshold) return level;
  }
  return null;
}

class Profile {
  constructor({ level, chars, counts, threshold, standard, script = "simplified" }) {
    /** Level needed to reach `threshold` coverage; null means off-scale. */
    this.level = level;
    /** Gradeable characters counted. */
    this.chars = chars;
    /** Map of level -> character count; the null key holds ungraded ones. */
    this.counts = counts;
    this.threshold = threshold;
    /** Which document graded this: "2025" (exam) or "2021" (standard). */
    this.standard = standard;
    /** Canonical identifier of that document, e.g. "hsk-syllabus-2025". */
    this.standardId = IDENTIFIERS[standard];
    /** "simplified", or "traditional" when characters were converted first. */
    this.script = script;
    Object.freeze(this);
  }
  get label() { return label(this.level); }
  get ungraded() { return this.counts.get(null) || 0; }
  /** Share of the text a reader at `level` knows. */
  coverageAt(level) {
    if (!this.chars) return 0;
    let cum = 0;
    for (const candidate of LEVELS) {
      cum += this.counts.get(candidate) || 0;
      if (candidate === level) break;
    }
    return cum / this.chars;
  }
  /** Cumulative coverage at every level. */
  curve() {
    const out = {};
    for (const level of LEVELS) out[label(level)] = this.coverageAt(level);
    return out;
  }
  toJSON() {
    return {
      level: this.level, label: this.label, chars: this.chars,
      ungraded: this.ungraded, threshold: this.threshold,
      standard: this.standard, standardId: this.standardId,
      script: this.script, curve: this.curve(),
    };
  }
}

function profileFromChars(chars, threshold, standard) {
  const key = resolve(standard);
  const tbl = characters(key);
  const counts = new Map();
  let total = 0;
  for (const ch of chars) {
    total += 1;
    const lvl = Object.prototype.hasOwnProperty.call(tbl, ch) ? tbl[ch] : null;
    counts.set(lvl, (counts.get(lvl) || 0) + 1);
  }
  return { level: coverageLevel(counts, total, threshold), chars: total, counts, threshold, standard: key };
}

/**
 * Map traditional characters to simplified, for grading only. The result is
 * an upper bound on coverage: conversion is many-to-one (乾, 幹, 榦 → 干).
 */
function convertTraditional(text) {
  const t2s = table("t2s");
  let out = "";
  for (const ch of String(text ?? "")) out += Object.prototype.hasOwnProperty.call(t2s, ch) ? t2s[ch] : ch;
  return out;
}

/** True when the text contains a character only the traditional script uses. */
function looksTraditional(text) {
  const t2s = table("t2s");
  for (const ch of String(text ?? "")) if (Object.prototype.hasOwnProperty.call(t2s, ch)) return true;
  return false;
}

/**
 * Grade a raw string.
 * @param {string} text
 * @param {{threshold?: number, exclude?: string[], standard?: string, script?: "auto"|"simplified"|"traditional"}} [options]
 */
function grade(text, options = {}) {
  const { threshold = DEFAULT_THRESHOLD, exclude = [], standard = DEFAULT_STANDARD, script = "auto" } = options;
  let body = String(text ?? "");
  for (const term of exclude || []) if (term) body = body.split(String(term)).join("");
  if (!["auto", "simplified", "traditional"].includes(script)) {
    throw new RangeError(`script must be 'auto', 'simplified' or 'traditional', not ${JSON.stringify(script)}`);
  }
  let seen = script;
  if (script === "auto") seen = looksTraditional(body) ? "traditional" : "simplified";
  if (seen === "traditional") body = convertTraditional(body);
  return new Profile({ ...profileFromChars(hanzi(body), threshold, standard), script: seen });
}

/**
 * Grade word-annotated text, excluding proper nouns by their pinyin.
 * tokens: [{ hz: "我", py: "wǒ" }, { hz: "李明。", py: "Lǐ Míng" }]
 */
function gradeTokens(tokens, options = {}) {
  const {
    threshold = DEFAULT_THRESHOLD, excludeProperNouns = true,
    hzKey = "hz", pyKey = "py", detector = isProperNoun, standard = DEFAULT_STANDARD,
  } = options;
  const chars = [];
  for (const token of tokens || []) {
    if (excludeProperNouns && detector(token[pyKey] || "")) continue;
    chars.push(...hanzi(stripPunct(token[hzKey] || "")));
  }
  return new Profile(profileFromChars(chars, threshold, standard));
}

/**
 * Which characters push `text` above `target`: [share, [[char, level, share], ...]],
 * worst first.
 */
function budgetViolations(text, target, options = {}) {
  const { standard = DEFAULT_STANDARD } = options;
  const tbl = characters(standard);
  const chars = hanzi(text);
  const total = chars.length;
  if (!total) return [0, []];
  const over = new Map();
  for (const ch of chars) {
    const lvl = Object.prototype.hasOwnProperty.call(tbl, ch) ? tbl[ch] : null;
    if (lvl === null || lvl > target) over.set(ch, (over.get(ch) || 0) + 1);
  }
  let sum = 0;
  for (const n of over.values()) sum += n;
  const ranked = [...over.entries()]
    .map(([ch, n]) => [ch, Object.prototype.hasOwnProperty.call(tbl, ch) ? tbl[ch] : null, n / total])
    .sort((a, b) => b[2] - a[2] || (a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0));
  return [sum / total, ranked];
}

/**
 * Grade a text for handwriting. Returns the share writable at each level, the
 * ceiling (share the writing curriculum covers at all) and the level needed to
 * write `threshold` of the writable characters.
 */
function writingProfile(text, options = {}) {
  const { standard = "2025", threshold = DEFAULT_THRESHOLD } = options;
  const tbl = characters(standard, "writing");
  const chars = hanzi(text);
  const total = chars.length;
  const writable = {};
  if (!total) {
    for (const lvl of LEVELS) writable[label(lvl)] = 0;
    return { chars: 0, writable, ceiling: 0, outside: 0, level: null, label: "nothing writable", threshold };
  }
  const counts = new Map();
  for (const ch of chars) {
    const lvl = Object.prototype.hasOwnProperty.call(tbl, ch) ? tbl[ch] : null;
    counts.set(lvl, (counts.get(lvl) || 0) + 1);
  }
  let running = 0;
  for (const lvl of LEVELS) { running += counts.get(lvl) || 0; writable[label(lvl)] = running / total; }
  const outside = counts.get(null) || 0;
  const writableTotal = total - outside;
  const level = writableTotal ? coverageLevel(counts, writableTotal, threshold) : null;
  return {
    chars: total, writable, ceiling: running / total, outside, level,
    label: level === null ? "nothing writable" : label(level), threshold,
  };
}

module.exports = {
  DEFAULT_STANDARD, DEFAULT_THRESHOLD, DEFAULT_BUDGET, BAND, LEVELS, IDENTIFIERS,
  resolve, words, characters, label, hanzi, stripPunct, isProperNoun,
  convertTraditional, looksTraditional, grade, gradeTokens, budgetViolations,
  writingProfile, Profile,
};
