"""
SupportCase Entity Model
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from data.database import Base


class SupportCase(Base):
    __tablename__ = "support_cases"

    id = Column(String(32), primary_key=True, index=True)  # CAS-2026-000001
    student_id = Column(String(32), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    risk_prediction_id = Column(String(32), nullable=True)  # Reference to RiskPrediction
    trigger_reason = Column(String(255), nullable=False)
    status = Column(
        String(32),
        nullable=False,
        default="Open",
        index=True  # Open, Assigned, In Progress, Resolved, Closed, Escalated
    )
    priority = Column(
        String(32),
        nullable=False,
        default="Medium",
        index=True  # Low, Medium, High, Critical
    )
    assigned_staff = Column(String(128), nullable=False, default="Unassigned")
    opened_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="support_cases")
    interventions = relationship("Intervention", back_populates="support_case")

    def __repr__(self):
        return f"<SupportCase {self.id} ({self.status}) for {self.student_id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "risk_prediction_id": self.risk_prediction_id,
            "trigger_reason": self.trigger_reason,
            "status": self.status,
            "priority": self.priority,
            "assigned_staff": self.assigned_staff,
            "opened_at": self.opened_at.isoformat() if self.opened_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

