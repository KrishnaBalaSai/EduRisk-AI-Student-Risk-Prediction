"""
Analytics Application Service
Aggregates enterprise KPIs, trendlines, and chart datasets directly from database repositories.
No hardcoded values — all metrics computed dynamically.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy import func, case
from data.database import get_session
from data.models.student import Student
from data.models.course import Course
from data.models.enrollment import Enrollment
from data.models.attendance import AttendanceEvent
from data.models.assessment_result import AssessmentResult
from data.models.lms_activity import LMSActivity
from data.models.support_case import SupportCase
from data.models.intervention import Intervention
from data.models.outcome import Outcome
from data.models.risk_prediction import RiskPrediction
from data.repositories.risk_repository import RiskRepository
from data.repositories.intervention_repository import InterventionRepository


class AnalyticsService:
    def __init__(self, session=None):
        self._session = session
        self.risk_repo = RiskRepository(session=self.session)
        self.int_repo = InterventionRepository(session=self.session)
        self._cached_latest_preds = None

    @property
    def session(self):
        if self._session is None:
            self._session = get_session()
        return self._session

    def _get_latest_predictions(self) -> List[RiskPrediction]:
        if self._cached_latest_preds is None:
            self._cached_latest_preds = self.risk_repo.get_latest_all_students()
        return self._cached_latest_preds

    def get_executive_kpis(self) -> Dict[str, Any]:
        """
        Calculates all 10 core institutional KPIs via live database aggregation.
        """
        total_students = self.session.query(Student).count()
        total_courses = self.session.query(Course).count()
        total_enrollments = self.session.query(Enrollment).count()

        # Risk categories from latest predictions (reusing cached list for the request)
        latest_preds = self._get_latest_predictions()
        high_risk = sum(1 for p in latest_preds if p.risk_category == "High Risk")
        med_risk = sum(1 for p in latest_preds if p.risk_category == "Medium Risk")
        low_risk = sum(1 for p in latest_preds if p.risk_category == "Low Risk")

        # Open / active cases
        open_cases = self.session.query(SupportCase).filter(
            SupportCase.status.in_(["Open", "Assigned", "In Progress", "Escalated"])
        ).count()

        # Active interventions
        active_ints = self.session.query(Intervention).filter(
            Intervention.status.in_(["Scheduled", "In Progress"])
        ).count()

        # Intervention success rate
        completed_ints = self.session.query(Intervention).filter(Intervention.status == "Completed").all()
        if completed_ints:
            successful = sum(1 for i in completed_ints if "Positive engagement" in (i.outcome_notes or "") or "committed" in (i.outcome_notes or ""))
            success_rate = round((successful / len(completed_ints)) * 100, 1)
        else:
            success_rate = 0.0

        # Overall average attendance percentage
        total_att = self.session.query(AttendanceEvent).count()
        if total_att > 0:
            present_att = self.session.query(AttendanceEvent).filter(AttendanceEvent.status.in_(["Present", "Late"])).count()
            avg_attendance = round((present_att / total_att) * 100, 1)
        else:
            avg_attendance = 0.0

        return {
            "total_students": total_students,
            "total_courses": total_courses,
            "total_enrollments": total_enrollments,
            "high_risk_count": high_risk,
            "medium_risk_count": med_risk,
            "low_risk_count": low_risk,
            "open_support_cases": open_cases,
            "active_interventions": active_ints,
            "intervention_success_rate": success_rate,
            "average_attendance": avg_attendance,
        }

    def get_risk_distribution(self) -> Dict[str, int]:
        latest_preds = self._get_latest_predictions()
        dist = {"Low Risk": 0, "Medium Risk": 0, "High Risk": 0}
        for p in latest_preds:
            dist[p.risk_category] = dist.get(p.risk_category, 0) + 1
        return dist

    def get_attendance_trends(self) -> List[Dict[str, Any]]:
        """
        Weekly aggregate attendance trend over session dates.
        """
        records = (
            self.session.query(
                AttendanceEvent.session_date,
                AttendanceEvent.status,
                func.count(AttendanceEvent.id)
            )
            .group_by(AttendanceEvent.session_date, AttendanceEvent.status)
            .order_by(AttendanceEvent.session_date.asc())
            .all()
        )
        data = {}
        for sdate, status, cnt in records:
            dt_str = sdate.isoformat()
            data.setdefault(dt_str, {"date": dt_str, "Present": 0, "Late": 0, "Absent_Approved": 0, "Absent_Unapproved": 0})
            data[dt_str][status] = cnt
        return list(data.values())

    def get_assessment_performance_distribution(self) -> List[float]:
        results = (
            self.session.query(AssessmentResult.score)
            .filter(AssessmentResult.score != None)
            .all()
        )
        return [r[0] for r in results]

    def get_lms_engagement_by_type(self) -> Dict[str, int]:
        records = (
            self.session.query(LMSActivity.activity_type, func.count(LMSActivity.id))
            .group_by(LMSActivity.activity_type)
            .all()
        )
        return {atype: cnt for atype, cnt in records}

    def get_risk_by_course(self) -> List[Dict[str, Any]]:
        """
        Aggregate student risk predictions grouped by enrolled course.
        """
        results = (
            self.session.query(
                Course.code,
                Course.title,
                func.avg(RiskPrediction.overall_score).label("avg_risk"),
                func.count(Enrollment.student_id).label("student_count")
            )
            .join(Enrollment, Course.id == Enrollment.course_id)
            .join(RiskPrediction, Enrollment.student_id == RiskPrediction.student_id)
            .group_by(Course.id, Course.code, Course.title)
            .order_by(func.avg(RiskPrediction.overall_score).desc())
            .limit(10)
            .all()
        )
        return [
            {
                "course_code": r[0],
                "course_title": r[1],
                "avg_risk": round(float(r[2]), 1) if r[2] else 0.0,
                "student_count": r[3]
            }
            for r in results
        ]

    def get_intervention_outcomes_summary(self) -> Dict[str, int]:
        records = (
            self.session.query(Outcome.outcome_label, func.count(Outcome.id))
            .group_by(Outcome.outcome_label)
            .all()
        )
        return {label: cnt for label, cnt in records}

    def get_monthly_student_performance_trends(self) -> List[Dict[str, Any]]:
        """
        Monthly average assessment score and attendance rate.
        """
        # Attendance monthly
        att_records = (
            self.session.query(
                func.strftime("%Y-%m", AttendanceEvent.session_date).label("month"),
                func.count(AttendanceEvent.id).label("total"),
                func.sum(case((AttendanceEvent.status.in_(["Present", "Late"]), 1), else_=0)).label("attended")
            )
            .group_by("month")
            .order_by("month")
            .all()
        )
        trend = []
        for m, total, attended in att_records:
            rate = round((attended / total) * 100, 1) if total else 0.0
            trend.append({"month": m, "attendance_rate": rate})
        return trend

