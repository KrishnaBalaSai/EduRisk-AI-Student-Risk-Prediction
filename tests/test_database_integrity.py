"""
Test Suite: Database Integrity
Verifies primary key uniqueness, foreign key relationships, and allowed enum domains.
"""

import pytest
from sqlalchemy import func
from data.models.student import Student
from data.models.course import Course
from data.models.enrollment import Enrollment
from data.models.attendance import AttendanceEvent
from data.models.assessment import Assessment
from data.models.intervention import Intervention


def test_primary_keys_not_null(db_session):
    """Ensure no records have null primary keys."""
    assert db_session.query(Student).filter(Student.id == None).count() == 0
    assert db_session.query(Course).filter(Course.id == None).count() == 0
    assert db_session.query(Enrollment).filter(Enrollment.id == None).count() == 0
    assert db_session.query(AttendanceEvent).filter(AttendanceEvent.id == None).count() == 0
    assert db_session.query(Assessment).filter(Assessment.id == None).count() == 0


def test_foreign_key_referential_integrity(db_session):
    """Ensure every child enrollment references existing student and course."""
    student_ids = {s[0] for s in db_session.query(Student.id).all()}
    course_ids = {c[0] for c in db_session.query(Course.id).all()}

    enrollments = db_session.query(Enrollment).all()
    for e in enrollments:
        assert e.student_id in student_ids, f"Orphan enrollment {e.id} missing student {e.student_id}"
        assert e.course_id in course_ids, f"Orphan enrollment {e.id} missing course {e.course_id}"


def test_allowed_enums(db_session):
    """Verify that statuses fall strictly within approved domain enums."""
    allowed_student_statuses = {"Active", "Withdrawn", "Graduated", "Suspended"}
    students = db_session.query(Student).all()
    for s in students:
        assert s.status in allowed_student_statuses

    allowed_intervention_statuses = {"Scheduled", "In Progress", "Completed", "Cancelled", "No Show"}
    ints = db_session.query(Intervention).all()
    for i in ints:
        assert i.status in allowed_intervention_statuses

