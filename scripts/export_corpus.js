#!/usr/bin/env node
/* Export the aligned graded-reader corpus from the Pinyora source tree.
 *
 *   node scripts/export_corpus.js /path/to/InkPath
 *
 * Writes two files:
 *   corpus/hsk30_graded_readers.jsonl  the dataset itself, no derived labels
 *   corpus/reference_grades.json       levels computed by the ORIGINAL
 *                                      JavaScript implementation, used only to
 *                                      verify the Python port reproduces it
 *
 * Labels are kept out of the dataset on purpose: they are a function of the
 * grader and the standard, both of which can be re-run, and baking them in
 * would let a stale copy of the dataset disagree with the library.
 */
const vm = require("vm");
const fs = require("fs");
const path = require("path");

const root = process.argv[2];
if (!root) {
  console.error("usage: node scripts/export_corpus.js /path/to/InkPath");
  process.exit(1);
}

const STORY_FILES = [
  "data/stories.js", "data/stories-extra.js", "data/stories-curated.js",
  "data/stories-volume-2.js", "data/stories-volume-3.js", "data/stories-volume-4.js"
];
const SHELVES = ["newbie", "beginner", "intermediate", "upper", "advanced", "native"];

const sandbox = { window: {}, console };
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(path.join(root, "data/hsk-levels.js"), "utf8"), sandbox);
STORY_FILES.forEach(f =>
  vm.runInContext(fs.readFileSync(path.join(root, f), "utf8"), sandbox));

const CHARS = sandbox.window.HSK30_CHARS;
const STORIES = sandbox.window.STORIES.filter(s => s && s.id && Array.isArray(s.sentences));
const BAND = 7, LEVELS = [1, 2, 3, 4, 5, 6, BAND];
const PUNCT = /[，。！？；：、“”‘’（）〈〉《》【】…—·「」『』!?.,;:()"'\-\s]/g;
const isProperNoun = w => /^[A-Z]/.test(String((w && w.py) || ""));

/* The reference implementation, transcribed unchanged from build.js. */
function referenceGrade(story) {
  const counts = {};
  let total = 0;
  for (const sentence of story.sentences || []) {
    for (const word of sentence.words || []) {
      if (isProperNoun(word)) continue;
      for (const ch of String(word.hz || "").replace(PUNCT, "")) {
        if (!/[一-鿿]/.test(ch)) continue;
        total++;
        const level = CHARS[ch];
        const key = level === undefined ? "none" : level;
        counts[key] = (counts[key] || 0) + 1;
      }
    }
  }
  let cum = 0;
  for (const level of LEVELS) {
    cum += counts[level] || 0;
    if (total && cum / total >= 0.95) return { level, chars: total };
  }
  return { level: null, chars: total };
}

const out = [];
const reference = {};
for (const story of STORIES) {
  const sentences = (story.sentences || []).map(s => ({
    hz: (s.words || []).map(w => w.hz).join(""),
    en: s.en || "",
    words: (s.words || []).map(w => ({ hz: w.hz, py: w.py || "", en: w.en || "" }))
  }));
  const grade = referenceGrade(story);
  reference[story.id] = grade;
  out.push({
    id: story.id,
    shelf: story.level,
    shelf_index: SHELVES.indexOf(story.level) + 1,
    title: story.title,
    description: story.description || "",
    text: sentences.map(s => s.hz).join(""),
    sentences,
    n_sentences: sentences.length,
    n_chars: grade.chars
  });
}

out.sort((a, b) => a.shelf_index - b.shelf_index || a.id.localeCompare(b.id, "en", { numeric: true }));
fs.mkdirSync("corpus", { recursive: true });
fs.writeFileSync("corpus/hsk30_graded_readers.jsonl",
  out.map(r => JSON.stringify(r)).join("\n") + "\n");
fs.writeFileSync("corpus/reference_grades.json",
  JSON.stringify(reference, null, 1) + "\n");

console.log("wrote corpus/hsk30_graded_readers.jsonl  %d texts", out.length);
console.log("wrote corpus/reference_grades.json");
const byShelf = {};
out.forEach(r => { byShelf[r.shelf] = (byShelf[r.shelf] || 0) + 1; });
console.log("  shelves:", JSON.stringify(byShelf));
console.log("  sentences:", out.reduce((a, r) => a + r.n_sentences, 0));
console.log("  characters:", out.reduce((a, r) => a + r.n_chars, 0));
