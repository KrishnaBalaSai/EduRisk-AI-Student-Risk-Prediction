"""
Outcome Entity Model
"""

from datetime import datetime, date
from sqlalchemy import Column, String, Date, DateTime, Float, Boolean, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from data.database import Base


class Outcome(Base):
    __tablename__ = "outcomes"

    id = Column(String(32), primary_key=True, index=True)  # OUT-2026-000001
    student_id = Column(String(32), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(String(32), ForeignKey("courses.id", ondelete="SET NULL"), nullable=True, index=True)
    evaluation_date = Column(Date, nullable=False, index=True)
    outcome_label = Column(
        String(64),
        nullable=False,
        index=True
        # Improved academic performance, Continued academic risk,
        # Successful recovery, Course withdrawal, Course completion
    )
    gpa_change = Column(Float, nullable=False, default=0.0)
    attendance_change = Column(Float, nullable=False, default=0.0)
    is_recovery = Column(Boolean, nullable=False, default=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="outcomes")

    def __repr__(self):
        return f"<Outcome {self.id} ({self.outcome_label}) for {self.student_id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "course_id": self.course_id,
            "evaluation_date": self.evaluation_date.isoformat() if self.evaluation_date else None,
            "outcome_label": self.outcome_label,
            "gpa_change": self.gpa_change,
            "attendance_change": self.attendance_change,
            "is_recovery": self.is_recovery,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

