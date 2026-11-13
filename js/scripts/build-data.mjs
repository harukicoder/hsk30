// Build js/data/*.json from the tables the Python package ships, so the two
// implementations can never grade against different data.
//
//   node js/scripts/build-data.mjs
//
// Each JSON file keeps the `# standard:` declaration of the table it came
// from (spec/README.md): a level means nothing without the document it was
// read from, and a declaration that lives only in a README does not survive
// being copied.
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const SRC = join(here, "..", "..", "src", "hsk30", "data");
const OUT = join(here, "..", "data");

const TABLES = {
  "words-2025": "hsk2025_words.tsv",
  "words-2021": "hsk30_words.tsv",
  "words-2012": "hsk2012_words.tsv",
  "words-2.0": "hsk20_words.tsv",
  "chars-2025": "hsk2025_chars.tsv",
  "chars-2021": "hsk30_chars.tsv",
  "writing-2025": "hsk2025_writing_chars.tsv",
};

function read(file) {
  const declaration = {};
  const entries = {};
  let header = true;
  for (const line of readFileSync(join(SRC, file), "utf8").split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    if (trimmed.startsWith("#")) {
      const m = trimmed.match(/^#\s*([a-z_]+)\s*:\s*(.+)$/i);
      if (m) declaration[m[1]] = m[2].trim();
      continue;
    }
    if (header) { header = false; continue; }
    const [key, level] = line.split("\t");
    if (key && level) entries[key] = Number(level);
  }
  return { declaration, entries };
}

mkdirSync(OUT, { recursive: true });
for (const [name, file] of Object.entries(TABLES)) {
  const { declaration, entries } = read(file);
  writeFileSync(join(OUT, name + ".json"),
    JSON.stringify({ source: file, ...declaration, entries }) + "\n");
  console.log(`${name}: ${Object.keys(entries).length} (${declaration.standard || "no declaration"})`);
}

// Traditional-to-simplified pairs restricted to gradeable characters.
const t2s = {};
let header = true;
for (const line of readFileSync(join(SRC, "t2s.tsv"), "utf8").split(/\r?\n/)) {
  if (!line.trim() || line.trim().startsWith("#")) continue;
  if (header) { header = false; continue; }
  const [trad, simp] = line.split("\t");
  if (trad && simp) t2s[trad] = simp;
}
writeFileSync(join(OUT, "t2s.json"), JSON.stringify(t2s) + "\n");
console.log(`t2s: ${Object.keys(t2s).length}`);
