"""
Integrity Validator
Validates primary key uniqueness, foreign key relationships, and enum constraints.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from data.models.student import Student
from data.models.course import Course
from data.models.enrollment import Enrollment
from data.models.attendance import AttendanceEvent
from data.models.assessment import Assessment
from data.models.assessment_result import AssessmentResult
from data.models.lms_activity import LMSActivity
from data.models.support_case import SupportCase
from data.models.intervention import Intervention
from data.models.outcome import Outcome


class IntegrityValidator:
    def __init__(self, session: Session):
        self.session = session

    def validate_all(self) -> Dict[str, Any]:
        results = {
            "validator": "IntegrityValidator",
            "passed": 0,
            "failed": 0,
            "errors": [],
        }

        # 1. Check Primary Key Uniqueness & Nulls across key entities
        entities = [
            ("Student", Student),
            ("Course", Course),
            ("Enrollment", Enrollment),
            ("AttendanceEvent", AttendanceEvent),
            ("Assessment", Assessment),
            ("AssessmentResult", AssessmentResult),
            ("LMSActivity", LMSActivity),
            ("SupportCase", SupportCase),
            ("Intervention", Intervention),
            ("Outcome", Outcome),
        ]

        for name, cls in entities:
            # Check for null IDs
            null_count = self.session.query(cls).filter(cls.id == None).count()
            if null_count > 0:
                results["failed"] += 1
                results["errors"].append(f"Entity {name} contains {null_count} records with NULL primary key.")
            else:
                results["passed"] += 1

        # 2. Check Foreign Key Integrity: Enrollments -> Students & Courses
        student_ids = set(r[0] for r in self.session.query(Student.id).all())
        course_ids = set(r[0] for r in self.session.query(Course.id).all())
        enrollments = self.session.query(Enrollment).all()

        orphan_enr_s = [e.id for e in enrollments if e.student_id not in student_ids]
        orphan_enr_c = [e.id for e in enrollments if e.course_id not in course_ids]

        if orphan_enr_s:
            results["failed"] += len(orphan_enr_s)
            results["errors"].append(f"Found {len(orphan_enr_s)} enrollments with non-existent student IDs.")
        else:
            results["passed"] += 1

        if orphan_enr_c:
            results["failed"] += len(orphan_enr_c)
            results["errors"].append(f"Found {len(orphan_enr_c)} enrollments with non-existent course IDs.")
        else:
            results["passed"] += 1

        # 3. Check Foreign Key Integrity: Attendance -> Enrollments
        enr_ids = set(e.id for e in enrollments)
        attendance_records = self.session.query(AttendanceEvent).all()
        orphan_att = [a.id for a in attendance_records if a.enrollment_id not in enr_ids]
        if orphan_att:
            results["failed"] += len(orphan_att)
            results["errors"].append(f"Found {len(orphan_att)} attendance events referencing missing enrollments.")
        else:
            results["passed"] += 1

        # 4. Check Allowed Enums
        allowed_att_status = {"Present", "Late", "Absent_Approved", "Absent_Unapproved"}
        invalid_att = [a.id for a in attendance_records if a.status not in allowed_att_status]
        if invalid_att:
            results["failed"] += len(invalid_att)
            results["errors"].append(f"Found {len(invalid_att)} attendance events with invalid status enum.")
        else:
            results["passed"] += 1

        allowed_int_status = {"Scheduled", "In Progress", "Completed", "Cancelled", "No Show"}
        interventions = self.session.query(Intervention).all()
        invalid_int = [i.id for i in interventions if i.status not in allowed_int_status]
        if invalid_int:
            results["failed"] += len(invalid_int)
            results["errors"].append(f"Found {len(invalid_int)} interventions with invalid status enum.")
        else:
            results["passed"] += 1

        return results

