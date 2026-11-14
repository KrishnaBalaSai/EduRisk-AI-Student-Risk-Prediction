"""
Assessment Entity Model
"""

from datetime import datetime, date
from sqlalchemy import Column, String, Date, DateTime, Float, ForeignKey, Index
from sqlalchemy.orm import relationship
from data.database import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(String(48), primary_key=True, index=True)  # ASM-{course_id}-{seq}
    course_id = Column(String(32), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(128), nullable=False)
    assessment_type = Column(
        String(32),
        nullable=False,
        default="Assignment",
        index=True  # Quiz, Assignment, Midterm, Final Exam, Project
    )
    max_score = Column(Float, nullable=False, default=100.0)
    weight = Column(Float, nullable=False, default=0.20)
    due_date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    course = relationship("Course", back_populates="assessments")
    results = relationship("AssessmentResult", back_populates="assessment", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Assessment {self.id} ({self.title})>"

    def to_dict(self):
        return {
            "id": self.id,
            "course_id": self.course_id,
            "title": self.title,
            "assessment_type": self.assessment_type,
            "max_score": self.max_score,
            "weight": self.weight,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

