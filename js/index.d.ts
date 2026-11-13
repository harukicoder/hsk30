/** A document name: "2025" (exam syllabus, default), "2021" (GF0025-2021), "2012" or "2.0". */
export type Standard = "2025" | "2021" | "2012" | "2.0" | "syllabus" | "exam" | "standard" | "3.0" | "3" | "2" | "2010";
/** 1-6, or 7 for the single 7-9 band. */
export type Level = 1 | 2 | 3 | 4 | 5 | 6 | 7;

export declare const DEFAULT_STANDARD: "2025";
export declare const DEFAULT_THRESHOLD: number;
export declare const DEFAULT_BUDGET: number;
export declare const BAND: 7;
export declare const LEVELS: readonly Level[];
/** Canonical registry identifiers, e.g. "2025" -> "hsk-syllabus-2025". */
export declare const IDENTIFIERS: Readonly<Record<"2025" | "2021" | "2012" | "2.0", string>>;

export declare function resolve(standard: Standard | string): "2025" | "2021" | "2012" | "2.0";
export declare function words(standard?: Standard): Readonly<Record<string, Level>>;
export declare function characters(standard?: Standard, kind?: "recognition" | "writing"): Readonly<Record<string, Level>>;
export declare function label(level: Level | null | undefined): string;
export declare function hanzi(text: string): string[];
export declare function stripPunct(text: string): string;
export declare function isProperNoun(pinyin: string): boolean;
export declare function convertTraditional(text: string): string;
export declare function looksTraditional(text: string): boolean;

export declare class Profile {
  /** Level needed to reach the threshold; null means beyond HSK 9. */
  readonly level: Level | null;
  readonly chars: number;
  readonly counts: ReadonlyMap<Level | null, number>;
  readonly threshold: number;
  readonly standard: "2025" | "2021";
  /** e.g. "hsk-syllabus-2025" */
  readonly standardId: string;
  readonly script: "simplified" | "traditional";
  readonly label: string;
  readonly ungraded: number;
  coverageAt(level: Level): number;
  curve(): Record<string, number>;
  toJSON(): object;
}

export interface GradeOptions {
  threshold?: number;
  exclude?: string[];
  standard?: Standard;
  script?: "auto" | "simplified" | "traditional";
}
export declare function grade(text: string, options?: GradeOptions): Profile;

export interface Token { [key: string]: string | undefined }
export interface GradeTokensOptions {
  threshold?: number;
  excludeProperNouns?: boolean;
  hzKey?: string;
  pyKey?: string;
  detector?: (pinyin: string) => boolean;
  standard?: Standard;
}
export declare function gradeTokens(tokens: Token[], options?: GradeTokensOptions): Profile;

export declare function budgetViolations(
  text: string, target: Level, options?: { standard?: Standard }
): [number, Array<[string, Level | null, number]>];

export interface WritingProfile {
  chars: number;
  writable: Record<string, number>;
  ceiling: number;
  outside: number;
  level: Level | null;
  label: string;
  threshold: number;
}
export declare function writingProfile(text: string, options?: { standard?: Standard; threshold?: number }): WritingProfile;

declare const hsk30: {
  DEFAULT_STANDARD: typeof DEFAULT_STANDARD; DEFAULT_THRESHOLD: number; DEFAULT_BUDGET: number;
  BAND: 7; LEVELS: readonly Level[]; IDENTIFIERS: typeof IDENTIFIERS;
  resolve: typeof resolve; words: typeof words; characters: typeof characters; label: typeof label;
  hanzi: typeof hanzi; stripPunct: typeof stripPunct; isProperNoun: typeof isProperNoun;
  convertTraditional: typeof convertTraditional; looksTraditional: typeof looksTraditional;
  grade: typeof grade; gradeTokens: typeof gradeTokens; budgetViolations: typeof budgetViolations;
  writingProfile: typeof writingProfile; Profile: typeof Profile;
};
export default hsk30;
