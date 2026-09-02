"""Grade Chinese text against the HSK 3.0 character standard.

The central question this answers is: *what HSK level does a reader need in
order to read this passage?*  The answer is a coverage threshold, not an
average — a reader follows a text when they know enough of it to infer the
rest, and 95% character coverage is the conventional bar for that.

Method, and why each part is the way it is
------------------------------------------

**Character-level, not word-level.**  Word-level grading is unusable on
segmented Chinese: real segmenters emit phrase tokens (我的, 七点, 蓝色) that
are not entries in any graded word list, which pushes the "unknown" share past
95% at every level and reports ordinary beginner text as off-scale.  HSK 3.0
grades 3,000 characters separately from its words precisely because the
character inventory is what gates reading.

**Proper nouns are excluded when they can be identified.**  A reader does not
need the puppy's name in their vocabulary — it is glossed in place.  Counting
names as difficulty graded a story called "My Puppy Doudou" at HSK 4 on a
beginner shelf, entirely on the strength of 豆豆.  Identification needs pinyin
(names are romanised with a leading capital), so it is available through
:func:`grade_tokens` and not through :func:`grade` on a bare string.

**Ungraded characters count against you.**  A character outside the 3,000 never
contributes to cumulative coverage but does count in the denominator, so a text
full of off-list characters correctly grades as beyond the standard.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from .data import BAND, DEFAULT_STANDARD, LEVELS, characters, label, resolve

#: The comprehensible-input threshold.  Below this a reader is decoding rather
#: than reading; the figure is the standard one in the reading-acquisition
#: literature and is what the reference implementation has always used.
DEFAULT_THRESHOLD = 0.95

#: A single above-target character occupying more than this share of a short
#: text blocks the 95% bar on its own, regardless of everything else.
DEFAULT_BUDGET = 0.05

#: CJK Unified Ideographs.  Deliberately not including extensions A-F: the
#: standard grades none of them, so a text using them is off-scale by
#: definition and counting them as "ungraded" is the correct outcome.
_HANZI = re.compile(r"[一-鿿]")

_PUNCT = re.compile(
    r"[，。！？；：、“”‘’（）〈〉《》【】…—·「」『』!?.,;:()\"'\-\s]"
)


def strip_punct(text: str) -> str:
    """Drop punctuation.  Tokens carry it so they can be joined without gaps."""
    return _PUNCT.sub("", str(text or ""))


def hanzi(text: str) -> List[str]:
    """Every gradeable character in ``text``, in order, duplicates kept."""
    return _HANZI.findall(str(text or ""))


def is_proper_noun(pinyin: str) -> bool:
    """Names are romanised with a leading capital: Běijīng, Lǐ Bái, Dòudou.

    Tone marks sit on the first letter often enough to matter, so the test
    folds to NFD before asking whether the letter is uppercase.  An ASCII
    ``^[A-Z]`` test — see :func:`is_proper_noun_ascii` — silently misses
    Ōuzhōu, Ōuyà and Ā Q Zhèngzhuàn, and 欧 and 洲 are both HSK 7-9
    characters, so missing one place name can move a whole text two levels.
    """
    text = str(pinyin or "").strip()
    if not text:
        return False
    first = unicodedata.normalize("NFD", text[0])[0]
    return first.isupper()


def is_proper_noun_ascii(pinyin: str) -> bool:
    """The original prototype's ASCII-only test, kept for exact reproduction.

    Retained so published figures computed before the accent-aware fix can be
    regenerated exactly.  Prefer :func:`is_proper_noun` for new work.
    """
    return bool(re.match(r"[A-Z]", str(pinyin or "").strip()))


@dataclass(frozen=True)
class Profile:
    """The grading of one passage."""

    level: Optional[int]
    """Level needed to reach ``threshold`` coverage; ``None`` means off-scale."""

    chars: int
    """Gradeable characters counted, after exclusions."""

    counts: Mapping[Optional[int], int] = field(repr=False)
    """Character frequency per level; the ``None`` key holds ungraded ones."""

    threshold: float = DEFAULT_THRESHOLD

    standard: str = DEFAULT_STANDARD
    """Which document graded this: ``"2025"`` (exam) or ``"2021"`` (standard)."""


    @property
    def label(self) -> str:
        """``"3"``, ``"7-9"``, or ``"beyond HSK 9"``."""
        return label(self.level)

    def coverage_at(self, level: int) -> float:
        """Share of the text a reader at ``level`` knows."""
        if not self.chars:
            return 0.0
        cum = 0
        for candidate in LEVELS:
            cum += self.counts.get(candidate, 0)
            if candidate == level:
                break
        return cum / self.chars

    def curve(self) -> Dict[int, float]:
        """Cumulative coverage at every level — the full readability curve."""
        return {lvl: self.coverage_at(lvl) for lvl in LEVELS}

    @property
    def ungraded(self) -> int:
        """Characters outside the 3,000."""
        return self.counts.get(None, 0)


def _coverage_level(
    counts: Mapping[Optional[int], int], total: int, threshold: float
) -> Optional[int]:
    """Lowest level whose cumulative coverage reaches ``threshold``."""
    if not total:
        return None
    cum = 0
    for level in LEVELS:
        cum += counts.get(level, 0)
        if cum / total >= threshold:
            return level
    return None


def _profile_from_chars(
    chars: Iterable[str], threshold: float, standard: str = DEFAULT_STANDARD
) -> Profile:
    standard = resolve(standard)
    table = characters(standard)
    counts: Dict[Optional[int], int] = {}
    total = 0
    for ch in chars:
        total += 1
        lvl = table.get(ch)
        counts[lvl] = counts.get(lvl, 0) + 1
    return Profile(
        level=_coverage_level(counts, total, threshold),
        chars=total,
        counts=counts,
        threshold=threshold,
        standard=standard,
    )


def grade(
    text: str,
    threshold: float = DEFAULT_THRESHOLD,
    exclude: Optional[Iterable[str]] = None,
    standard: str = DEFAULT_STANDARD,
) -> Profile:
    """Grade a raw string.

    ``exclude`` accepts substrings to drop before grading — pass known proper
    nouns here when you have them, since a bare string carries no pinyin and
    they cannot be detected automatically.

    ``standard`` selects the document: ``"2025"`` (the exam syllabus in force,
    the default) or ``"2021"`` (the national grading standard).  Roughly half of
    real texts grade differently under the two, so state which you used.

    For handwriting, use :func:`writing_profile` instead — a coverage threshold
    is the wrong instrument there, for the reason documented on that function.

    >>> grade("我是中国人。").label
    '1'
    """
    body = str(text or "")
    for term in exclude or ():
        if term:
            body = body.replace(str(term), "")
    return _profile_from_chars(hanzi(body), threshold, standard)


def grade_tokens(
    tokens: Sequence[Mapping[str, str]],
    threshold: float = DEFAULT_THRESHOLD,
    exclude_proper_nouns: bool = True,
    hz_key: str = "hz",
    py_key: str = "py",
    detector: Callable[[str], bool] = is_proper_noun,
    standard: str = DEFAULT_STANDARD,
) -> Profile:
    """Grade word-annotated text, excluding proper nouns by their pinyin.

    Each token is a mapping with a hanzi field and a pinyin field, the shape
    aligned corpora use::

        [{"hz": "我", "py": "wǒ"}, {"hz": "李明。", "py": "Lǐ Míng"}]

    ``detector`` selects the proper-noun policy; pass
    :func:`is_proper_noun_ascii` to reproduce pre-fix figures, or your own
    callable to apply a different rule (for instance, one that keeps common
    place names in the count).
    """
    chars: List[str] = []
    for token in tokens:
        if exclude_proper_nouns and detector(token.get(py_key, "")):
            continue
        chars.extend(hanzi(strip_punct(token.get(hz_key, ""))))
    return _profile_from_chars(chars, threshold, standard)


def budget_violations(
    text: str,
    target: int,
    budget: float = DEFAULT_BUDGET,
    threshold: float = DEFAULT_THRESHOLD,
    standard: str = DEFAULT_STANDARD,
) -> Tuple[float, List[Tuple[str, Optional[int], float]]]:
    """Report which characters push ``text`` above ``target``.

    Returns the total above-target share and the offending characters, worst
    first, each as ``(character, level, share)``.  Reaching a 95% bar means
    keeping the total above-target share under 5%, so any single character over
    that budget blocks the target on its own — which is how a short passage
    silently regresses when a "harmless" edit repeats one hard character a
    fourth time.
    """
    table = characters(standard)
    chars = hanzi(text)
    total = len(chars)
    if not total:
        return 0.0, []
    over: Dict[str, int] = {}
    for ch in chars:
        lvl = table.get(ch)
        if lvl is None or lvl > target:
            over[ch] = over.get(ch, 0) + 1
    share = sum(over.values()) / total
    ranked = sorted(
        ((ch, table.get(ch), n / total) for ch, n in over.items()),
        key=lambda row: (-row[2], row[0]),
    )
    return share, ranked


@dataclass(frozen=True)
class WritingProfile:
    """How much of a text a learner could write by hand, level by level."""

    chars: int
    writable: Dict[int, float]
    """Cumulative share of the whole text writable at each level."""
    ceiling: float
    """Share writable at any level — the rest is outside the curriculum."""
    outside: int
    """Characters no HSK level requires a learner to hand-write."""
    level: Optional[int] = None
    """Level needed to write ``threshold`` of the *writable* characters.

    Computed over the writable subset, not the whole text, because the whole
    text can never reach a 95% bar (see :func:`writing_profile`). Read it
    together with ``ceiling``: "you need HSK 4 handwriting for the part of this
    text the curriculum covers, and it covers 62% of it".  ``None`` means no
    character in the text is writable at any level.
    """
    threshold: float = DEFAULT_THRESHOLD

    def at(self, level: int) -> float:
        return self.writable.get(level, 0.0)

    @property
    def label(self) -> str:
        return label(self.level) if self.level is not None else "nothing writable"


def writing_profile(text: str, standard: str = "2025",
                    threshold: float = DEFAULT_THRESHOLD) -> WritingProfile:
    """Grade a text for HANDWRITING rather than reading.

    **Why this is not just `grade(kind="writing")`.**  The obvious design is to
    reuse the 95% coverage threshold against the 书写字 list.  It does not work,
    and the failure is total rather than marginal: the syllabus grades 3,088
    characters for recognition but only 1,200 for writing, so a median text has
    just under 60% of its characters in the writing curriculum at all.  Across
    our 102-text corpus, *every single text* fails a 95% bar at every level.  A
    metric that returns the same answer for all inputs measures nothing.

    So the answer is split into two numbers that are each well defined:

    * ``ceiling`` — how much of the text the curriculum covers at all.
      ``1 - ceiling`` is the portion no HSK level asks a learner to produce by
      hand, which for ordinary prose is substantial and is a fact about the
      standard, not about the text.
    * ``level`` — among the characters that *are* writable, the level needed to
      write ``threshold`` of them.  Restricting the denominator to the writable
      subset is what makes a single level meaningful here; applied to the whole
      text the same question has no answer.

    Reported together they say: "you need HSK 4 handwriting for the part of this
    text the curriculum covers, and it covers 62% of it."  Either number alone
    misleads — the level flatters the text, the ceiling reads as a failure.
    """
    table = characters(standard, kind="writing")
    chars = hanzi(text)
    total = len(chars)
    if not total:
        return WritingProfile(0, {lvl: 0.0 for lvl in LEVELS}, 0.0, 0, None, threshold)

    counts: Dict[Optional[int], int] = {}
    for ch in chars:
        lvl = table.get(ch)
        counts[lvl] = counts.get(lvl, 0) + 1

    cumulative, running = {}, 0
    for lvl in LEVELS:
        running += counts.get(lvl, 0)
        cumulative[lvl] = running / total
    outside = counts.get(None, 0)
    writable_total = total - outside

    # The level is computed over the writable subset; see the docstring.
    level = _coverage_level(counts, writable_total, threshold) if writable_total else None
    return WritingProfile(total, cumulative, running / total, outside, level, threshold)


@dataclass(frozen=True)
class ShelfProfile:
    """The grading of a *collection* — a graded-reader shelf, a textbook unit."""

    median: Optional[int]
    iqr_low: Optional[int]
    iqr_high: Optional[int]
    pooled: Optional[int]
    easy_share: float
    n: int
    chars: int

    @property
    def label(self) -> str:
        return label(self.median)

    @property
    def span_label(self) -> str:
        """``"HSK 2"``, ``"HSK 2-3"``, or ``"HSK 4 to 7-9"``."""
        lo, hi = label(self.iqr_low), label(self.iqr_high)
        if lo == hi:
            return f"HSK {lo}"
        # "HSK 3-7-9" is unreadable, so a range ending in the band gets "to".
        return f"HSK {lo} to {hi}" if "-" in hi else f"HSK {lo}-{hi}"


def profile_shelf(profiles: Sequence[Profile]) -> ShelfProfile:
    """Summarise a collection of graded texts.

    Reports the **median text**, not the pooled figure.  Pooling every
    character in a shelf lets a handful of hard texts speak for all of them: it
    reported "HSK 3" for a beginner shelf on which 16 of 22 texts individually
    read at HSK 1-2, describing nothing actually on the shelf.

    Reports the **interquartile** range, not the middle 80%.  A wider window
    lets genuine misfiles speak for the shelf — four outliers stretched one
    beginner shelf to "HSK 1-5" and told learners the wrong thing about the
    other eighteen texts.
    """
    if not profiles:
        return ShelfProfile(None, None, None, None, 0.0, 0, 0)

    # None sorts after the band, so off-scale texts sit at the hard end rather
    # than being dropped or treated as easy.
    off_scale = BAND + 1
    ranked = sorted((p.level if p.level is not None else off_scale) for p in profiles)
    n = len(ranked)

    def unpack(value: int) -> Optional[int]:
        return None if value > BAND else value

    counts: Dict[Optional[int], int] = {}
    total = 0
    for p in profiles:
        for lvl, count in p.counts.items():
            counts[lvl] = counts.get(lvl, 0) + count
        total += p.chars

    easy = counts.get(1, 0) + counts.get(2, 0)
    return ShelfProfile(
        median=unpack(ranked[n // 2]),
        iqr_low=unpack(ranked[int(n * 0.25)]),
        iqr_high=unpack(ranked[min(n - 1, -(-n * 3 // 4) - 1)]),
        pooled=_coverage_level(counts, total, profiles[0].threshold),
        easy_share=(easy / total) if total else 0.0,
        n=n,
        chars=total,
    )
