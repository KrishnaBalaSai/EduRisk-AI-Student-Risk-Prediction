"""
RiskPrediction Entity Model
"""

from datetime import datetime, date
from sqlalchemy import Column, String, Date, DateTime, Float, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from data.database import Base


class RiskPrediction(Base):
    __tablename__ = "risk_predictions"

    id = Column(String(64), primary_key=True, index=True)  # e.g. RSK-STU-2026-000001-20260930 or with version suffix
    student_id = Column(String(32), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    prediction_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    observation_window_end = Column(Date, nullable=False, index=True)
    attendance_risk = Column(Float, nullable=False)
    assessment_risk = Column(Float, nullable=False)
    lms_risk = Column(Float, nullable=False)
    support_risk = Column(Float, nullable=False)
    overall_score = Column(Float, nullable=False, index=True)
    risk_category = Column(String(32), nullable=False, index=True)  # Low Risk, Medium Risk, High Risk
    explanation = Column(Text, nullable=False)
    model_version = Column(String(32), nullable=False, default="v1.0.0-rule")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Composite index for lightning-fast latest-prediction queries
    __table_args__ = (
        Index("ix_risk_pred_student_ts", "student_id", "prediction_timestamp"),
    )

    # Relationships
    student = relationship("Student", back_populates="risk_predictions")

    def __repr__(self):
        return f"<RiskPrediction {self.id} - Student: {self.student_id} Score: {self.overall_score} ({self.risk_category})>"

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "prediction_timestamp": self.prediction_timestamp.isoformat() if self.prediction_timestamp else None,
            "observation_window_end": self.observation_window_end.isoformat() if self.observation_window_end else None,
            "attendance_risk": self.attendance_risk,
            "assessment_risk": self.assessment_risk,
            "lms_risk": self.lms_risk,
            "support_risk": self.support_risk,
            "overall_score": self.overall_score,
            "risk_category": self.risk_category,
            "explanation": self.explanation,
            "model_version": self.model_version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

