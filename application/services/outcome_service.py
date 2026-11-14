"""
Outcome Application Service
Provides queries, statistics, and ground-truth evaluation reporting.
"""

from typing import List, Optional, Dict, Any
from data.models.outcome import Outcome
from data.repositories.outcome_repository import OutcomeRepository


class OutcomeService:
    def __init__(self, outcome_repo: Optional[OutcomeRepository] = None):
        self.outcome_repo = outcome_repo or OutcomeRepository()

    def get_all_outcomes(self, limit: int = 1000) -> List[Outcome]:
        return self.outcome_repo.get_all(limit=limit)

    def get_outcomes_for_student(self, student_id: str) -> List[Outcome]:
        return self.outcome_repo.get_by_student(student_id)

    def get_distribution(self) -> Dict[str, int]:
        outcomes = self.outcome_repo.get_all(limit=10000)
        dist = {}
        for o in outcomes:
            dist[o.outcome_label] = dist.get(o.outcome_label, 0) + 1
        return dist

    def get_recovery_rate(self) -> float:
        return self.outcome_repo.get_recovery_rate()

