"""
Risk Prediction Repository
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from data.models.risk_prediction import RiskPrediction
from data.repositories.base_repository import BaseRepository


class RiskRepository(BaseRepository[RiskPrediction]):
    def __init__(self, session: Optional[Session] = None):
        super().__init__(RiskPrediction, session)

    def get_latest_for_student(self, student_id: str) -> Optional[RiskPrediction]:
        return (
            self.session.query(RiskPrediction)
            .filter(RiskPrediction.student_id == student_id)
            .order_by(RiskPrediction.prediction_timestamp.desc())
            .first()
        )

    def get_by_category(self, category: str) -> List[RiskPrediction]:
        return (
            self.session.query(RiskPrediction)
            .filter(RiskPrediction.risk_category == category)
            .order_by(RiskPrediction.overall_score.desc())
            .all()
        )

    def get_latest_all_students(self) -> List[RiskPrediction]:
        """Returns the most recent risk prediction for every student with predictions."""
        # Using subquery to find max prediction_timestamp per student
        from sqlalchemy import func
        subq = (
            self.session.query(
                RiskPrediction.student_id,
                func.max(RiskPrediction.prediction_timestamp).label("max_ts")
            )
            .group_by(RiskPrediction.student_id)
            .subquery()
        )
        return (
            self.session.query(RiskPrediction)
            .join(
                subq,
                (RiskPrediction.student_id == subq.c.student_id)
                & (RiskPrediction.prediction_timestamp == subq.c.max_ts)
            )
            .order_by(RiskPrediction.overall_score.desc())
            .all()
        )

