"""Grade Chinese text against the HSK 3.0 standard.

    >>> import hsk30
    >>> hsk30.grade("我每天早上七点起床，然后去公园跑步。").label
    '3'

Grades against 《国际中文教育中文水平等级标准》 (GF0025-2021), the Chinese
Proficiency Grading Standards for International Chinese Language Education,
issued by the Ministry of Education and the State Language Commission and in
force as a national language standard since **1 July 2021**.

It is not a renumbering of HSK 2.0: of the 4,482 words both list, only 814 keep
their level.  Tooling calibrated to HSK 2.0 is therefore not approximately
right — it is wrong for four words in five.

NOTE ON VERSIONS.  The 2021 grading standard is *not* the HSK 3.0 exam
syllabus.  A separate 406-page exam syllabus (新版HSK考试大纲) was published in
November 2025 and takes effect in July 2026; it uses different lists —
cumulative word counts 300/500/1,000/2,000/3,600/5,400/11,000 against this
standard's 485/1,227/2,171/3,143/4,199/5,317/10,916, and roughly 3,079
recognition characters against this standard's 3,000.  This package grades
against the 2021 standard.  Do not describe its output as the exam syllabus.
"""

from .data import BAND, DEFAULT_STANDARD, LEVELS, characters, label, resolve, words
from .grade import (
    DEFAULT_BUDGET,
    DEFAULT_THRESHOLD,
    Profile,
    ShelfProfile,
    budget_violations,
    grade,
    grade_tokens,
    hanzi,
    is_proper_noun,
    is_proper_noun_ascii,
    WritingProfile,
    profile_shelf,
    writing_profile,
    strip_punct,
)

__version__ = "0.1.1"

__all__ = [
    "BAND", "LEVELS", "DEFAULT_BUDGET", "DEFAULT_THRESHOLD", "DEFAULT_STANDARD",
    "resolve",
    "Profile", "ShelfProfile", "WritingProfile", "writing_profile",
    "budget_violations", "characters", "grade", "grade_tokens", "hanzi",
    "is_proper_noun", "is_proper_noun_ascii", "label", "profile_shelf", "strip_punct", "words",
    "__version__",
]
