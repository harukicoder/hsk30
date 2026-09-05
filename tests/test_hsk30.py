"""Tests for the hsk30 grader.

Runs under pytest, or standalone (``python3 tests/test_hsk30.py``) so the suite
works on a machine with nothing installed.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

import hsk30
from hsk30 import BAND, LEVELS

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.join(HERE, "..", "corpus", "hsk30_graded_readers.jsonl")
REFERENCE = os.path.join(HERE, "..", "corpus", "reference_grades.json")


def _corpus():
    with open(CORPUS, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def _tokens(row):
    return [w for s in row["sentences"] for w in s["words"]]


# ---- the standard itself ---------------------------------------------------

def test_2021_character_list_matches_the_published_shape():
    """GF0025-2021: 3,000 hanzi, exactly 300 per level 1-6, 1,200 at 7-9."""
    chars = hsk30.characters("2021")
    assert len(chars) == 3000
    counts = {lvl: sum(1 for v in chars.values() if v == lvl) for lvl in LEVELS}
    assert [counts[l] for l in (1, 2, 3, 4, 5, 6)] == [300] * 6
    assert counts[BAND] == 1200


def test_2025_syllabus_matches_its_published_totals():
    """The exam syllabus advertises cumulative 300/500/1k/2k/3.6k/5.4k/11k."""
    words = hsk30.words("2025")
    assert len(words) == 10896          # 11,000 entries, 104 homograph rows
    assert len(hsk30.characters("2025")) == 3088
    # Distinct-word counts sit just under the entry counts they derive from.
    counts = {lvl: sum(1 for v in words.values() if v == lvl) for lvl in LEVELS}
    assert counts[1] == 300
    assert sum(counts.values()) == 10896


def test_default_standard_is_the_syllabus_in_force():
    assert hsk30.DEFAULT_STANDARD == "2025"
    assert hsk30.grade("我是中国人。").standard == "2025"


def test_standard_names_resolve():
    assert hsk30.resolve("3.0") == "2021"
    assert hsk30.resolve("exam") == "2025"
    assert hsk30.resolve("2.0") == "2.0"
    try:
        hsk30.resolve("4.0")
    except ValueError:
        pass
    else:
        raise AssertionError("unknown standard should raise")


def test_hsk20_has_no_character_grading():
    try:
        hsk30.characters("2.0")
    except ValueError:
        pass
    else:
        raise AssertionError("HSK 2.0 grades no characters")


def test_the_two_hsk30_documents_genuinely_disagree():
    """The paper's central claim, pinned so it cannot drift."""
    a, b = hsk30.words("2021"), hsk30.words("2025")
    shared = [w for w in a if w in b]
    same = [w for w in shared if a[w] == b[w]]
    moved = 100.0 * (len(shared) - len(same)) / len(shared)
    assert 40 < moved < 43, moved      # 41.5%


def test_word_lists_load():
    assert len(hsk30.words("2021")) == 10977
    assert len(hsk30.words("2.0")) == 4991


def test_variant_and_affix_entries_survive_extraction():
    """The standard writes some entries with notation, and they are still words.

    爸爸｜爸, 第（第二）, …极了 and 称1 all carry characters outside the CJK
    ideograph range. An extraction that filters raw rows to pure hanzi drops
    every one of them — 61 words, including six kinship terms that are HSK 1 —
    and the loss is invisible to a count assertion, because the count simply
    becomes whatever survived. This test names them instead.
    """
    words = hsk30.words("2021")
    for w in ("爸爸", "妈妈", "哥哥", "姐姐", "弟弟", "妹妹"):
        assert words.get(w) == 1, "%s missing from the 2021 list" % w
    # single-character variants of the same entries
    for w in ("爸", "妈", "哥", "姐"):
        assert w in words, "%s missing from the 2021 list" % w


def test_band_is_never_split():
    """No level 8 or 9 exists; a vendor advertising one invented it."""
    for standard in ("2021", "2025"):
        assert set(hsk30.words(standard).values()) <= set(LEVELS)
        assert 8 not in hsk30.characters(standard).values()
    assert hsk30.label(BAND) == "7-9"
    assert hsk30.label(3) == "3"
    assert hsk30.label(None) == "beyond HSK 9"


# ---- grading ---------------------------------------------------------------

def test_simple_text_grades_low():
    assert hsk30.grade("我是中国人。", standard="2021").level == 1


def test_academic_text_grades_high():
    assert hsk30.grade("这项研究揭示了神经网络的内在缺陷。", standard="2021").level >= 5


def test_coverage_curve_is_monotonic():
    profile = hsk30.grade("我每天早上七点起床，然后去公园跑步。", standard="2021")
    curve = [profile.coverage_at(l) for l in LEVELS]
    assert curve == sorted(curve)
    assert curve[-1] <= 1.0


def test_ungraded_characters_count_against_coverage():
    """Off-list characters sit in the denominator but never accumulate."""
    profile = hsk30.grade("犇犇犇犇犇犇犇犇犇犇我", standard="2021")
    assert profile.ungraded == 10
    assert profile.chars == 11
    assert profile.level is None  # cannot reach 95% at any level


def test_non_chinese_input_is_ignored():
    assert hsk30.grade("hello, world! 123").chars == 0
    assert hsk30.grade("").level is None
    assert hsk30.grade(None).chars == 0


def test_punctuation_is_not_graded():
    assert hsk30.grade("我。是，中！国？人").chars == 5


# ---- proper nouns ----------------------------------------------------------

def test_proper_noun_detection_handles_tone_marks():
    assert hsk30.is_proper_noun("Běijīng")
    assert hsk30.is_proper_noun("Ōuzhōu")   # the case the ASCII test misses
    assert hsk30.is_proper_noun("Ā Q Zhèngzhuàn")
    assert not hsk30.is_proper_noun("wǒ")
    assert not hsk30.is_proper_noun("")


def test_legacy_ascii_detector_misses_accented_capitals():
    """Documents the original prototype's behaviour, kept for reproduction."""
    assert hsk30.is_proper_noun_ascii("Beijing")
    assert not hsk30.is_proper_noun_ascii("Ōuzhōu")


def test_proper_nouns_are_excluded_from_difficulty():
    tokens = [
        {"hz": "我", "py": "wǒ"},
        {"hz": "是", "py": "shì"},
        {"hz": "李明。", "py": "Lǐ Míng"},
    ]
    assert hsk30.grade_tokens(tokens).chars == 2
    assert hsk30.grade_tokens(tokens, exclude_proper_nouns=False).chars == 4


# ---- budgets ---------------------------------------------------------------

def test_budget_names_the_blocking_characters():
    share, offenders = hsk30.budget_violations("我每天去公园跑步", target=2, standard="2021")
    assert share > 0
    assert all(lvl is None or lvl > 2 for _, lvl, _ in offenders)
    shares = [s for _, _, s in offenders]
    assert shares == sorted(shares, reverse=True)


def test_text_within_target_has_no_offenders():
    share, offenders = hsk30.budget_violations("我是人", target=6)
    assert share == 0.0 and offenders == []


# ---- collections -----------------------------------------------------------

def test_shelf_reports_median_not_pooled():
    """Nine easy texts and one very hard one: the median must stay easy."""
    profiles = ([hsk30.grade("我是中国人。", standard="2021")] * 9
                + [hsk30.grade("罄竹难书的谬误", standard="2021")])
    shelf = hsk30.profile_shelf(profiles)
    assert shelf.median == 1
    assert shelf.n == 10


def test_empty_shelf_is_safe():
    shelf = hsk30.profile_shelf([])
    assert shelf.n == 0 and shelf.median is None


# ---- corpus + port fidelity ------------------------------------------------

def test_corpus_is_well_formed():
    rows = _corpus()
    assert len(rows) == 102
    assert sum(r["n_sentences"] for r in rows) == 1185
    assert {r["shelf"] for r in rows} == {
        "newbie", "beginner", "intermediate", "upper", "advanced", "native"}
    for r in rows:
        assert r["id"] and r["text"] and r["sentences"]
        # every sentence's hanzi is the concatenation of its word tokens
        for s in r["sentences"]:
            assert s["hz"] == "".join(w["hz"] for w in s["words"])


def test_python_reproduces_the_javascript_reference_exactly():
    """Legacy detector, all 102 texts, level and character count."""
    if not os.path.exists(REFERENCE):
        return
    with open(REFERENCE, encoding="utf-8") as fh:
        ref = json.load(fh)
    for row in _corpus():
        profile = hsk30.grade_tokens(
            _tokens(row), detector=hsk30.is_proper_noun_ascii, standard="2021")
        expected = ref[row["id"]]
        assert profile.level == expected["level"], row["id"]
        assert profile.chars == expected["chars"], row["id"]


def test_accent_fix_changes_exactly_one_text():
    """The improvement is real but narrow; pin it so it cannot drift silently."""
    if not os.path.exists(REFERENCE):
        return
    changed = []
    for row in _corpus():
        toks = _tokens(row)
        legacy = hsk30.grade_tokens(
            toks, detector=hsk30.is_proper_noun_ascii, standard="2021")
        if hsk30.grade_tokens(toks, standard="2021").level != legacy.level:
            changed.append(row["id"])
    assert changed == ["a8"]


def test_shelf_difficulty_increases_across_the_corpus():
    """The shelves must be ordered by difficulty, or the labels are wrong."""
    order = ["newbie", "beginner", "intermediate", "upper", "advanced", "native"]
    rows = _corpus()
    medians, easy_shares = [], []
    for shelf in order:
        profiles = [hsk30.grade_tokens(_tokens(r), standard="2021")
                    for r in rows if r["shelf"] == shelf]
        summary = hsk30.profile_shelf(profiles)
        medians.append(summary.median)
        easy_shares.append(summary.easy_share)
    assert medians == sorted(medians), medians
    # HSK 1-2 share must fall strictly: it is the continuous difficulty signal
    assert easy_shares == sorted(easy_shares, reverse=True), easy_shares


def test_heldout_split_is_disjoint_and_replicates():
    """The replication in the paper, pinned so it cannot drift."""
    path = os.path.join(HERE, "..", "corpus", "hsk30_heldout.jsonl")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as fh:
        held = [json.loads(line) for line in fh if line.strip()]
    assert len(held) == 30
    assert not ({r["id"] for r in held} & {r["id"] for r in _corpus()})

    changed = sum(
        1 for r in held
        if hsk30.grade_tokens(_tokens(r), standard="2021").level
        != hsk30.grade_tokens(_tokens(r), standard="2025").level)
    # 46.7% on the held-out set against 48.0% on the released corpus.
    assert 12 <= changed <= 16, changed


def test_regrading_survives_every_threshold():
    """Between 43% and 62% of texts change level at any threshold 0.80-1.00."""
    rows = _corpus()
    for threshold in (0.80, 0.85, 0.90, 0.95, 0.98, 1.00):
        changed = sum(
            1 for r in rows
            if hsk30.grade_tokens(_tokens(r), threshold=threshold,
                                  standard="2021").level
            != hsk30.grade_tokens(_tokens(r), threshold=threshold,
                                  standard="2025").level)
        pct = 100.0 * changed / len(rows)
        assert 40 < pct < 65, (threshold, pct)


def test_writing_characters_are_a_subset_of_recognition():
    """You cannot be asked to write a character you are not asked to read."""
    w = hsk30.characters("2025", kind="writing")
    r = hsk30.characters("2025")
    assert len(w) == 1200
    assert set(w) <= set(r), sorted(set(w) - set(r))[:10]


def test_writing_list_only_exists_for_the_2025_syllabus():
    for bad in ("2021", "2.0"):
        try:
            hsk30.characters(bad, kind="writing")
        except ValueError:
            continue
        raise AssertionError("%s should not expose writing characters" % bad)


def test_writing_profile_reports_a_curve_not_a_threshold():
    """A 95% bar is unreachable for handwriting; the curve is the answer."""
    p = hsk30.writing_profile("他在图书馆认真地准备考试。")
    assert p.chars == 12
    curve = [p.at(l) for l in LEVELS]
    assert curve == sorted(curve)          # cumulative, non-decreasing
    assert 0 < p.ceiling < 1               # some writable, much not
    assert p.outside > 0
    assert abs(curve[-1] - p.ceiling) < 1e-9


def test_most_corpus_text_is_not_fully_writable():
    """The gap between reading and writing requirements is large and real."""
    rows = _corpus()
    ceilings = [hsk30.writing_profile(r["text"]).ceiling for r in rows]
    median = sorted(ceilings)[len(ceilings) // 2]
    # Median text has roughly 60% of its characters in the writing curriculum.
    assert 0.45 < median < 0.75, median
    assert all(c < 0.95 for c in ceilings), max(ceilings)


def test_writing_level_discriminates_between_texts():
    """The whole point: a metric that gives every text the same answer is dead.

    Computed over the whole text a 95% bar is unreachable and every text
    returns None. Computed over the writable subset it spreads across levels.
    """
    rows = _corpus()
    levels = {hsk30.writing_profile(r["text"]).label for r in rows}
    assert len(levels) >= 4, levels
    assert "nothing writable" not in levels


def test_writing_level_is_computed_over_the_writable_subset():
    """A text of purely level-1 writable characters writes at level 1, however
    much of it sits outside the curriculum."""
    p = hsk30.writing_profile("我是中国人。")
    assert p.label == "1"
    assert p.ceiling == 1.0          # every character is writable here
    assert p.outside == 0


def test_ceiling_and_level_answer_different_questions():
    p = hsk30.writing_profile("他在图书馆认真地准备考试。")
    assert p.label == "3"            # writable part needs HSK 3 handwriting
    assert p.ceiling < 0.5           # but under half the text is writable
    assert p.outside == 7


def test_empty_text_has_a_safe_writing_profile():
    p = hsk30.writing_profile("")
    assert p.chars == 0 and p.ceiling == 0.0 and p.at(1) == 0.0
    assert p.level is None and p.label == "nothing writable"


def test_the_pooling_example_the_paper_cites_is_accurate():
    """§6.5 claims pooling overstates the beginner shelf. Pin the exact numbers.

    An earlier draft said 16 of 22; the true figure is 13, and the claim is only
    true against the 2021 standard. Both are now asserted, because a rhetorical
    example that drifts is worse than no example.
    """
    rows = [r for r in _corpus() if r["shelf"] == "beginner"]
    assert len(rows) == 22
    profiles = [hsk30.grade_tokens(_tokens(r), standard="2021") for r in rows]
    shelf = hsk30.profile_shelf(profiles)
    assert hsk30.label(shelf.pooled) == "3"
    assert hsk30.label(shelf.median) == "2"
    assert sum(1 for p in profiles if p.level and p.level <= 2) == 13


def test_the_vacuity_argument_cites_the_right_inventory_size():
    """§8.4 argues HSK 5-6 is near-vacuous because the inventory is large.

    An earlier draft said "2,600-plus characters", which is wrong under either
    standard. The 2025 syllabus grades 1,940 at HSK 6 or below.
    """
    chars = hsk30.characters("2025")
    assert sum(1 for v in chars.values() if v <= 6) == 1940
    assert sum(1 for v in chars.values() if v <= 5) == 1527


def test_the_writable_ceiling_is_invariant_across_difficulty():
    """§6.6's central claim: the ceiling does not vary with text difficulty.

    If this ever fails, the paper's "it is a property of the standard, not of
    the text" no longer holds and the section needs rewriting.
    """
    rows = _corpus()
    shelves = ["newbie", "beginner", "intermediate", "upper", "advanced", "native"]
    medians = []
    for shelf in shelves:
        ceilings = sorted(hsk30.writing_profile(r["text"]).ceiling
                          for r in rows if r["shelf"] == shelf)
        medians.append(ceilings[len(ceilings) // 2])
    # Every shelf lands in a narrow band; the paper quotes 57.7-62.5%.
    assert all(0.55 < m < 0.65 for m in medians), [round(m, 3) for m in medians]
    assert max(medians) - min(medians) < 0.06, max(medians) - min(medians)


def test_level_two_adds_almost_no_writing_requirement():
    """The allocation quirk §6.6 reports: HSK 2 advances reading, not writing."""
    rec = hsk30.characters("2025")
    wri = hsk30.characters("2025", kind="writing")
    lvl2 = [c for c, v in rec.items() if v == 2]
    assert len(lvl2) == 125
    assert sum(1 for c in lvl2 if c in wri) == 5


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items())
             if n.startswith("test_") and callable(f)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print("  ok   %s" % name)
        except Exception as exc:  # noqa: BLE001 - standalone runner
            failed += 1
            print("  FAIL %s: %s" % (name, exc))
    print("\n%d passed, %d failed, %d total" % (len(tests) - failed, failed, len(tests)))
    raise SystemExit(1 if failed else 0)
