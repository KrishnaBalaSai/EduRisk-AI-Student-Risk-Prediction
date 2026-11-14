"""
Support Case Repository
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from data.models.support_case import SupportCase
from data.repositories.base_repository import BaseRepository


class SupportRepository(BaseRepository[SupportCase]):
    def __init__(self, session: Optional[Session] = None):
        super().__init__(SupportCase, session)

    def get_by_student(self, student_id: str, cutoff_dt: Optional[datetime] = None) -> List[SupportCase]:
        query = self.session.query(SupportCase).filter(SupportCase.student_id == student_id)
        if cutoff_dt:
            query = query.filter(SupportCase.opened_at <= cutoff_dt)
        return query.order_by(SupportCase.opened_at.desc()).all()

    def get_active_cases_for_student(self, student_id: str) -> List[SupportCase]:
        return (
            self.session.query(SupportCase)
            .filter(
                SupportCase.student_id == student_id,
                SupportCase.status.in_(["Open", "Assigned", "In Progress", "Escalated"]),
            )
            .all()
        )

    def get_by_status(self, status: str) -> List[SupportCase]:
        return self.session.query(SupportCase).filter(SupportCase.status == status).all()

    def get_by_staff(self, staff_name: str) -> List[SupportCase]:
        return self.session.query(SupportCase).filter(SupportCase.assigned_staff == staff_name).all()

