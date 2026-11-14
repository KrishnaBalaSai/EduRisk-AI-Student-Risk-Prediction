"""
Intervention Entity Model
"""

from datetime import datetime, date
from sqlalchemy import Column, String, Date, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from data.database import Base


class Intervention(Base):
    __tablename__ = "interventions"

    id = Column(String(32), primary_key=True, index=True)  # INT-2026-000001
    student_id = Column(String(32), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    case_id = Column(String(32), ForeignKey("support_cases.id", ondelete="SET NULL"), nullable=True, index=True)
    intervention_type = Column(
        String(64),
        nullable=False,
        index=True
        # Academic Counselling, Attendance Follow-up, Mentoring, Learning Support,
        # Parent/Guardian Communication, Study Plan, Faculty Meeting
    )
    assigned_staff = Column(String(128), nullable=False)
    trigger_timestamp = Column(DateTime, nullable=False, index=True)
    scheduled_date = Column(Date, nullable=False, index=True)
    completion_date = Column(Date, nullable=True)
    status = Column(
        String(32),
        nullable=False,
        default="Scheduled",
        index=True  # Scheduled, In Progress, Completed, Cancelled, No Show
    )
    notes = Column(Text, nullable=True)
    outcome_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="interventions")
    support_case = relationship("SupportCase", back_populates="interventions")

    def __repr__(self):
        return f"<Intervention {self.id} ({self.intervention_type}) - {self.status}>"

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "case_id": self.case_id,
            "intervention_type": self.intervention_type,
            "assigned_staff": self.assigned_staff,
            "trigger_timestamp": self.trigger_timestamp.isoformat() if self.trigger_timestamp else None,
            "scheduled_date": self.scheduled_date.isoformat() if self.scheduled_date else None,
            "completion_date": self.completion_date.isoformat() if self.completion_date else None,
            "status": self.status,
            "notes": self.notes,
            "outcome_notes": self.outcome_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

