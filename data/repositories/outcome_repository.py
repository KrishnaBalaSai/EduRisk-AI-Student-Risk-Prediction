"""
Outcome Repository
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from data.models.outcome import Outcome
from data.repositories.base_repository import BaseRepository


class OutcomeRepository(BaseRepository[Outcome]):
    def __init__(self, session: Optional[Session] = None):
        super().__init__(Outcome, session)

    def get_by_student(self, student_id: str) -> List[Outcome]:
        return self.session.query(Outcome).filter(Outcome.student_id == student_id).order_by(Outcome.evaluation_date.desc()).all()

    def get_by_label(self, label: str) -> List[Outcome]:
        return self.session.query(Outcome).filter(Outcome.outcome_label == label).all()

    def get_recovery_rate(self) -> float:
        total = self.count()
        if total == 0:
            return 0.0
        recoveries = self.session.query(Outcome).filter(Outcome.is_recovery == True).count()
        return round((recoveries / total) * 100, 2)

