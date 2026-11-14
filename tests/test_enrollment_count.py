"""
Test Suite: Enrollment Count Correctness
Verifies that the full profile generates exactly 20,000 enrollments after anomaly injection,
and that the starter profile total remains consistent.
"""

import pytest
from generators.master_generator import MasterGenerator


def test_full_profile_enrollment_count_with_anomalies():
    """
    Full profile with anomaly injection enabled must persist exactly 20,000 enrollments.
    The withdrawn_student_active anomaly contributes +1 enrollment; the baseline generator
    is asked for 19,999 so that baseline + anomaly = 20,000.
    """
    gen = MasterGenerator(profile_name="full", seed=20261022)
    dataset = gen.generate(inject_anomalies_flag=True)

    baseline_count = len(dataset["enrollments"])
    anomaly_count = len(dataset["injected_entities"].get("enrollments", []))
    total_persisted = baseline_count + anomaly_count

    assert total_persisted == 20000, (
        f"Expected 20,000 total enrollments, got {total_persisted} "
        f"(baseline={baseline_count}, anomaly={anomaly_count})"
    )


def test_full_profile_enrollment_count_without_anomalies():
    """
    Full profile with anomaly injection disabled must generate exactly 20,000 baseline enrollments.
    """
    gen = MasterGenerator(profile_name="full", seed=20261022)
    dataset = gen.generate(inject_anomalies_flag=False)

    assert len(dataset["enrollments"]) == 20000, (
        f"Expected 20,000 enrollments without anomalies, got {len(dataset['enrollments'])}"
    )
    assert len(dataset["injected_entities"].get("enrollments", [])) == 0


def test_starter_profile_enrollment_count():
    """
    Starter profile with anomaly injection enabled must total exactly 300 enrollments
    (299 baseline + 1 anomaly).
    """
    gen = MasterGenerator(profile_name="starter", seed=20261022)
    dataset = gen.generate(inject_anomalies_flag=True)

    baseline_count = len(dataset["enrollments"])
    anomaly_count = len(dataset["injected_entities"].get("enrollments", []))
    total_persisted = baseline_count + anomaly_count

    assert total_persisted == 300, (
        f"Expected 300 total enrollments, got {total_persisted} "
        f"(baseline={baseline_count}, anomaly={anomaly_count})"
    )


def test_enrollment_foreign_key_integrity():
    """
    All generated enrollments (baseline + anomaly) reference valid student and course IDs.
    """
    gen = MasterGenerator(profile_name="starter", seed=20261022)
    dataset = gen.generate(inject_anomalies_flag=True)

    student_ids = {s.id for s in dataset["students"]}
    course_ids = {c.id for c in dataset["courses"]}

    all_enrs = dataset["enrollments"] + dataset["injected_entities"].get("enrollments", [])
    for enr in all_enrs:
        assert enr.student_id in student_ids, f"Enrollment {enr.id} references unknown student {enr.student_id}"
        assert enr.course_id in course_ids, f"Enrollment {enr.id} references unknown course {enr.course_id}"


def test_enrollment_uniqueness():
    """
    No two enrollment records (baseline or anomaly) share the same ID.
    """
    gen = MasterGenerator(profile_name="starter", seed=20261022)
    dataset = gen.generate(inject_anomalies_flag=True)

    all_enrs = dataset["enrollments"] + dataset["injected_entities"].get("enrollments", [])
    ids = [e.id for e in all_enrs]
    assert len(ids) == len(set(ids)), "Duplicate enrollment IDs found"

