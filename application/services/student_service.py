"""
Student Application Service
Coordinates student profiles, history, and search queries between presentation and repositories.
"""

from typing import List, Optional, Dict, Any
from datetime import date
from data.repositories.student_repository import StudentRepository
from data.repositories.attendance_repository import AttendanceRepository
from data.repositories.assessment_repository import AssessmentResultRepository
from data.repositories.lms_repository import LMSRepository
from data.repositories.support_repository import SupportRepository
from data.repositories.intervention_repository import InterventionRepository
from data.repositories.risk_repository import RiskRepository
from data.models.student import Student


class StudentService:
    def __init__(
        self,
        student_repo: Optional[StudentRepository] = None,
        attendance_repo: Optional[AttendanceRepository] = None,
        assessment_result_repo: Optional[AssessmentResultRepository] = None,
        lms_repo: Optional[LMSRepository] = None,
        support_repo: Optional[SupportRepository] = None,
        intervention_repo: Optional[InterventionRepository] = None,
        risk_repo: Optional[RiskRepository] = None
    ):
        self.student_repo = student_repo or StudentRepository()
        self.attendance_repo = attendance_repo or AttendanceRepository()
        self.asr_repo = assessment_result_repo or AssessmentResultRepository()
        self.lms_repo = lms_repo or LMSRepository()
        self.support_repo = support_repo or SupportRepository()
        self.intervention_repo = intervention_repo or InterventionRepository()
        self.risk_repo = risk_repo or RiskRepository()

    def get_all_students(self, limit: int = 1000, offset: int = 0) -> List[Student]:
        return self.student_repo.get_all(limit=limit, offset=offset)

    def count_students(self) -> int:
        return self.student_repo.count()

    def search_students(self, query: str, limit: int = 100) -> List[Student]:
        return self.student_repo.search(query, limit=limit)

    def get_student_by_id(self, student_id: str) -> Optional[Student]:
        return self.student_repo.get_by_id(student_id)

    def get_student_profile(self, student_id: str, cutoff_date: Optional[date] = None) -> Optional[Dict[str, Any]]:
        """
        Assemble comprehensive student 360 profile across all 10 domain entities.
        """
        student = self.student_repo.get_by_id(student_id)
        if not student:
            return None

        # Attendance summary
        att_summary = self.attendance_repo.get_student_attendance_summary(student_id, cutoff_date)
        attendance_events = self.attendance_repo.get_by_student(student_id, cutoff_date)

        # Assessment summary
        asm_summary = self.asr_repo.get_student_assessment_summary(student_id, cutoff_date)
        assessment_results = self.asr_repo.get_by_student(student_id, cutoff_date)

        # LMS recent activity
        from datetime import datetime
        cutoff_dt = datetime(cutoff_date.year, cutoff_date.month, cutoff_date.day, 23, 59, 59) if cutoff_date else datetime.utcnow()
        lms_summary = self.lms_repo.get_engagement_summary(student_id, cutoff_dt)
        lms_events = self.lms_repo.get_by_student(student_id, end_time=cutoff_dt)

        # Support Cases & Interventions
        support_cases = self.support_repo.get_by_student(student_id, cutoff_dt)
        interventions = self.intervention_repo.get_by_student(student_id)

        # Latest Risk Prediction
        latest_risk = self.risk_repo.get_latest_for_student(
    student_id,
    cutoff_date=cutoff_date or date.today()
)

        return {
            "student": student,
            "enrollments": student.enrollments,
            "attendance_summary": att_summary,
            "attendance_events": attendance_events,
            "assessment_summary": asm_summary,
            "assessment_results": assessment_results,
            "lms_summary": lms_summary,
            "lms_events": lms_events,
            "support_cases": support_cases,
            "interventions": interventions,
            "latest_risk": latest_risk,
        }

