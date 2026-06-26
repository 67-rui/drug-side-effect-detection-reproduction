from scripts.build_evidence_screening_table import assign_evidence_grade


def test_direct_database_support_gets_grade_a():
    grade = assign_evidence_grade(
        database_verified=True,
        direct_literature_support=False,
        mechanistic_support=False,
    )
    assert grade == "A"


def test_mechanistic_support_without_direct_evidence_gets_grade_c():
    grade = assign_evidence_grade(
        database_verified=False,
        direct_literature_support=False,
        mechanistic_support=True,
    )
    assert grade == "C"


def test_no_support_gets_grade_d():
    grade = assign_evidence_grade(
        database_verified=False,
        direct_literature_support=False,
        mechanistic_support=False,
    )
    assert grade == "D"
