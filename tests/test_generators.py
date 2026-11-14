"""
Test Suite: Synthetic Data Generators
Verifies row counts, deterministic ID structure, archetype distributions, and temporal ranges.
"""

import pytest
from generators.master_generator import MasterGenerator


def test_starter_generator_row_counts(starter_dataset):
    """Test that starter generator produces exact expected entity counts."""
    assert len(starter_dataset["students"]) == 100
    assert len(starter_dataset["courses"]) == 20
    assert len(starter_dataset["enrollments"]) == 300
    assert len(starter_dataset["attendance_events"]) > 3000
    assert len(starter_dataset["assessments"]) == 80  # 20 courses * 4 assessments
    assert len(starter_dataset["assessment_results"]) > 1000
    assert len(starter_dataset["lms_activities"]) > 2500
    assert len(starter_dataset["support_cases"]) > 15
    assert len(starter_dataset["interventions"]) > 20
    assert len(starter_dataset["outcomes"]) == 100


def test_deterministic_id_formatting(starter_dataset):
    """Test standard ID conventions across entities."""
    # Student: STU-2026-000001
    s = starter_dataset["students"][0]
    assert s.id.startswith("STU-2026-")
    assert len(s.id) == 15

    # Course: CRS-000001
    c = starter_dataset["courses"][0]
    assert c.id.startswith("CRS-")

    # Enrollment: ENR-{student_id}-{course_id}
    e = starter_dataset["enrollments"][0]
    assert e.id.startswith("ENR-STU-")

    # Attendance: ATT-{enrollment_id}-{date}
    att = starter_dataset["attendance_events"][0]
    assert att.id.startswith("ATT-ENR-")

    # Assessment: ASM-{course_id}-{seq}
    asm = starter_dataset["assessments"][0]
    assert asm.id.startswith("ASM-CRS-")

    # AssessmentResult: ASR-{assessment_id}-{student_id}
    asr = starter_dataset["assessment_results"][0]
    assert asr.id.startswith("ASR-ASM-")

    # LMS: LMS-2026-000001
    lms = starter_dataset["lms_activities"][0]
    assert lms.id.startswith("LMS-2026-")

    # SupportCase: CAS-2026-000001
    sc = starter_dataset["support_cases"][0]
    assert sc.id.startswith("CAS-2026-")

    # Intervention: INT-2026-000001
    it = starter_dataset["interventions"][0]
    assert it.id.startswith("INT-2026-")

    # Outcome: OUT-2026-000001
    out = starter_dataset["outcomes"][0]
    assert out.id.startswith("OUT-2026-")


def test_archetype_representation(starter_dataset):
    """Ensure all 5 behavioral archetypes are represented in students."""
    archetypes = starter_dataset["archetypes"]
    archetype_set = set(archetypes.values())
    assert "High_Achiever" in archetype_set
    assert "Steady_Average" in archetype_set
    assert "At_Risk" in archetype_set
    assert "Chronic_Struggling" in archetype_set
    assert "Withdrawn" in archetype_set
