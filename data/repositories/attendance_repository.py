"""
Attendance Repository
"""

from typing import List, Optional, Dict, Any
from datetime import date
from sqlalchemy import func
from sqlalchemy.orm import Session
from data.models.attendance import AttendanceEvent
from data.repositories.base_repository import BaseRepository


class AttendanceRepository(BaseRepository[AttendanceEvent]):
    def __init__(self, session: Optional[Session] = None):
        super().__init__(AttendanceEvent, session)

    def get_by_student(self, student_id: str, cutoff_date: Optional[date] = None) -> List[AttendanceEvent]:
        query = self.session.query(AttendanceEvent).filter(AttendanceEvent.student_id == student_id)
        if cutoff_date:
            query = query.filter(AttendanceEvent.session_date <= cutoff_date)
        return query.order_by(AttendanceEvent.session_date.asc()).all()

    def get_by_enrollment(self, enrollment_id: str, cutoff_date: Optional[date] = None) -> List[AttendanceEvent]:
        query = self.session.query(AttendanceEvent).filter(AttendanceEvent.enrollment_id == enrollment_id)
        if cutoff_date:
            query = query.filter(AttendanceEvent.session_date <= cutoff_date)
        return query.order_by(AttendanceEvent.session_date.asc()).all()

    def get_student_attendance_summary(self, student_id: str, cutoff_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Calculates eligible sessions, attended sessions, approved absences, unapproved absences, late counts.
        Attendance % is calculated as:
        (Present + Late) / (Eligible Sessions - Approved Absences) * 100
        If denominator <= 0, returns 100.0 or None.
        """
        events = self.get_by_student(student_id, cutoff_date)
        total_sessions = len(events)
        if total_sessions == 0:
            return {
                "total_sessions": 0,
                "present": 0,
                "absent_unapproved": 0,
                "absent_approved": 0,
                "late": 0,
                "attendance_rate": None,
            }

        present = sum(1 for e in events if e.status == "Present")
        late = sum(1 for e in events if e.status == "Late")
        absent_approved = sum(1 for e in events if e.status == "Absent_Approved")
        absent_unapproved = sum(1 for e in events if e.status == "Absent_Unapproved")

        # Denominator: total sessions excluding approved excused absences
        eligible_sessions = total_sessions - absent_approved
        if eligible_sessions <= 0:
            rate = 100.0
        else:
            # Late counts as 0.75 or full attendance depending on policy; here Present=1, Late=0.75
            rate = round(((present + 0.75 * late) / eligible_sessions) * 100, 2)

        return {
            "total_sessions": total_sessions,
            "eligible_sessions": eligible_sessions,
            "present": present,
            "absent_unapproved": absent_unapproved,
            "absent_approved": absent_approved,
            "late": late,
            "attendance_rate": rate,
        }

