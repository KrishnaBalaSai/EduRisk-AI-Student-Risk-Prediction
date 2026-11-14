"""
Duplicate Validator
Detects duplicate events and enforces deterministic ID consistency.
"""

from typing import Dict, Any
from sqlalchemy import func
from sqlalchemy.orm import Session
from data.models.student import Student
from data.models.course import Course
from data.models.enrollment import Enrollment
from data.models.assessment_result import AssessmentResult


class DuplicateValidator:
    def __init__(self, session: Session):
        self.session = session

    def validate_all(self) -> Dict[str, Any]:
        results = {
            "validator": "DuplicateValidator",
            "passed": 0,
            "failed": 0,
            "errors": [],
        }

        # 1. Duplicate Student Emails
        dup_emails = (
            self.session.query(Student.email, func.count(Student.id))
            .group_by(Student.email)
            .having(func.count(Student.id) > 1)
            .all()
        )
        if dup_emails:
            results["failed"] += len(dup_emails)
            results["errors"].append(f"Found {len(dup_emails)} duplicate student email addresses.")
        else:
            results["passed"] += 1

        # 2. Duplicate Student-Course Enrollments
        dup_enrs = (
            self.session.query(Enrollment.student_id, Enrollment.course_id, func.count(Enrollment.id))
            .group_by(Enrollment.student_id, Enrollment.course_id)
            .having(func.count(Enrollment.id) > 1)
            .all()
        )
        if dup_enrs:
            results["failed"] += len(dup_enrs)
            results["errors"].append(f"Found {len(dup_enrs)} duplicate enrollment pairs.")
        else:
            results["passed"] += 1

        # 3. Duplicate Assessment Results per Assessment + Student
        dup_results = (
            self.session.query(AssessmentResult.assessment_id, AssessmentResult.student_id, func.count(AssessmentResult.id))
            .group_by(AssessmentResult.assessment_id, AssessmentResult.student_id)
            .having(func.count(AssessmentResult.id) > 1)
            .all()
        )
        if dup_results:
            results["failed"] += len(dup_results)
            results["errors"].append(f"Found {len(dup_results)} duplicate assessment result submissions.")
        else:
            results["passed"] += 1

        return results

