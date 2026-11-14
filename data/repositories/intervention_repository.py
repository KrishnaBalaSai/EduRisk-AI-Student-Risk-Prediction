"""
Intervention Repository
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from data.models.intervention import Intervention
from data.repositories.base_repository import BaseRepository


class InterventionRepository(BaseRepository[Intervention]):
    def __init__(self, session: Optional[Session] = None):
        super().__init__(Intervention, session)

    def get_by_student(self, student_id: str) -> List[Intervention]:
        return (
            self.session.query(Intervention)
            .filter(Intervention.student_id == student_id)
            .order_by(Intervention.scheduled_date.desc())
            .all()
        )

    def get_by_case(self, case_id: str) -> List[Intervention]:
        return (
            self.session.query(Intervention)
            .filter(Intervention.case_id == case_id)
            .order_by(Intervention.scheduled_date.asc())
            .all()
        )

    def get_by_status(self, status: str) -> List[Intervention]:
        return self.session.query(Intervention).filter(Intervention.status == status).all()

    def get_by_type(self, intervention_type: str) -> List[Intervention]:
        return self.session.query(Intervention).filter(Intervention.intervention_type == intervention_type).all()

    def get_active_interventions(self) -> List[Intervention]:
        return (
            self.session.query(Intervention)
            .filter(Intervention.status.in_(["Scheduled", "In Progress"]))
            .all()
        )

