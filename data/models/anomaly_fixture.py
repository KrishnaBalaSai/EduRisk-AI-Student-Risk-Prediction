"""
AnomalyFixture Entity Model for Labelled Negative Scenarios
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Text
from data.database import Base


class AnomalyFixture(Base):
    __tablename__ = "anomaly_fixtures"

    id = Column(String(32), primary_key=True, index=True)  # ANM-000001
    issue_type = Column(String(64), nullable=False, index=True)
    # Types:
    # 1. future_data_leakage
    # 2. wrong_attendance_denominator
    # 3. withdrawn_student_active
    # 4. intervention_precedes_trigger
    # 5. missing_data_as_failure
    entity_type = Column(String(32), nullable=False)
    record_id = Column(String(96), nullable=False, index=True)
    ground_truth_label = Column(String(64), nullable=False)
    description = Column(Text, nullable=False)
    detected = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<AnomalyFixture {self.id} ({self.issue_type}) on {self.record_id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "issue_type": self.issue_type,
            "entity_type": self.entity_type,
            "record_id": self.record_id,
            "ground_truth_label": self.ground_truth_label,
            "description": self.description,
            "detected": self.detected,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

