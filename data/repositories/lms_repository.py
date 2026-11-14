"""
LMS Activity Repository
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from data.models.lms_activity import LMSActivity
from data.repositories.base_repository import BaseRepository


class LMSRepository(BaseRepository[LMSActivity]):
    def __init__(self, session: Optional[Session] = None):
        super().__init__(LMSActivity, session)

    def get_by_student(
        self,
        student_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[LMSActivity]:
        query = self.session.query(LMSActivity).filter(LMSActivity.student_id == student_id)
        if start_time:
            query = query.filter(LMSActivity.timestamp >= start_time)
        if end_time:
            query = query.filter(LMSActivity.timestamp <= end_time)
        return query.order_by(LMSActivity.timestamp.asc()).all()

    def get_engagement_summary(
        self,
        student_id: str,
        cutoff_dt: datetime,
        lookback_days: int = 30
    ) -> Dict[str, Any]:
        """
        Calculates LMS activity events and time spent in the recent observation window (e.g. 30 days)
        compared to the prior baseline window (30-60 days ago).
        """
        start_recent = cutoff_dt - timedelta(days=lookback_days)
        start_prior = cutoff_dt - timedelta(days=lookback_days * 2)

        recent_events = self.get_by_student(student_id, start_time=start_recent, end_time=cutoff_dt)
        prior_events = self.get_by_student(student_id, start_time=start_prior, end_time=start_recent)

        recent_count = len(recent_events)
        prior_count = len(prior_events)

        recent_duration_mins = sum(e.duration_seconds for e in recent_events) // 60
        prior_duration_mins = sum(e.duration_seconds for e in prior_events) // 60

        trend_pct = 0.0
        if prior_count > 0:
            trend_pct = round(((recent_count - prior_count) / prior_count) * 100, 1)

        return {
            "recent_count": recent_count,
            "prior_count": prior_count,
            "recent_duration_mins": recent_duration_mins,
            "trend_pct": trend_pct,
        }

