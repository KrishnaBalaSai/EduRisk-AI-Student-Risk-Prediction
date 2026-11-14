"""
Risk Prediction Repository
"""

from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from data.models.risk_prediction import RiskPrediction
from data.repositories.base_repository import BaseRepository


class RiskRepository(BaseRepository[RiskPrediction]):
    def __init__(self, session: Optional[Session] = None):
        super().__init__(RiskPrediction, session)

    def get_latest_for_student(
        self,
        student_id: str,
        cutoff_date: Optional[date] = None
    ) -> Optional[RiskPrediction]:
        query = self.session.query(RiskPrediction).filter(
            RiskPrediction.student_id == student_id
        )

        if cutoff_date:
            query = query.filter(
                RiskPrediction.observation_window_end <= cutoff_date
            )

        return query.order_by(
            RiskPrediction.prediction_timestamp.desc()
        ).first()

    def get_by_category(self, category: str) -> List[RiskPrediction]:
        return (
            self.session.query(RiskPrediction)
            .filter(RiskPrediction.risk_category == category)
            .order_by(RiskPrediction.overall_score.desc())
            .all()
        )

    def get_latest_all_students(self) -> List[RiskPrediction]:
        """Returns the most recent risk prediction for every student."""
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
