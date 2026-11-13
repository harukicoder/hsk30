import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const hsk30 = require("./index.cjs");

export const {
  DEFAULT_STANDARD, DEFAULT_THRESHOLD, DEFAULT_BUDGET, BAND, LEVELS, IDENTIFIERS,
  resolve, words, characters, label, hanzi, stripPunct, isProperNoun,
  convertTraditional, looksTraditional, grade, gradeTokens, budgetViolations,
  writingProfile, Profile,
} = hsk30;
export default hsk30;
