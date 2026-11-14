"""
Anomaly Fixture Repository
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from data.models.anomaly_fixture import AnomalyFixture
from data.repositories.base_repository import BaseRepository


class AnomalyRepository(BaseRepository[AnomalyFixture]):
    def __init__(self, session: Optional[Session] = None):
        super().__init__(AnomalyFixture, session)

    def get_by_issue_type(self, issue_type: str) -> List[AnomalyFixture]:
        return self.session.query(AnomalyFixture).filter(AnomalyFixture.issue_type == issue_type).all()

    def get_undetected(self) -> List[AnomalyFixture]:
        return self.session.query(AnomalyFixture).filter(AnomalyFixture.detected == False).all()

    def mark_detected(self, fixture_id: str) -> bool:
        fixture = self.get_by_id(fixture_id)
        if fixture:
            fixture.detected = True
            self.session.commit()
            return True
        return False

