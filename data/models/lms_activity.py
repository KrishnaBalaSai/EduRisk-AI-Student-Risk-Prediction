"""
LMSActivity Entity Model
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship
from data.database import Base


class LMSActivity(Base):
    __tablename__ = "lms_activities"

    id = Column(String(32), primary_key=True, index=True)  # LMS-2026-000001
    student_id = Column(String(32), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(String(32), ForeignKey("courses.id", ondelete="SET NULL"), nullable=True, index=True)
    activity_type = Column(
        String(32),
        nullable=False,
        index=True  # Login, Content_View, Assignment_Submit, Forum_Post, Quiz_Attempt
    )
    duration_seconds = Column(Integer, nullable=False, default=120)
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index("idx_lms_student_time", "student_id", "timestamp"),
    )

    # Relationships
    student = relationship("Student", back_populates="lms_activities")
    course = relationship("Course", back_populates="lms_activities")

    def __repr__(self):
        return f"<LMSActivity {self.id} ({self.activity_type}) at {self.timestamp}>"

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "course_id": self.course_id,
            "activity_type": self.activity_type,
            "duration_seconds": self.duration_seconds,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

