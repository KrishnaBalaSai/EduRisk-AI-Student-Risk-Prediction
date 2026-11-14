"""
Enrollment Entity Model (Bridge between Student and Course)
"""

from datetime import datetime, date
from sqlalchemy import Column, String, Date, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from data.database import Base


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(String(64), primary_key=True, index=True)  # ENR-{student_id}-{course_id}
    student_id = Column(String(32), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(String(32), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(
        String(32),
        nullable=False,
        default="Enrolled",
        index=True  # Enrolled, Completed, Withdrawn, Dropped
    )
    enrollment_date = Column(Date, nullable=False, default=date.today)
    completion_date = Column(Date, nullable=True)
    final_grade = Column(Float, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    attendance_events = relationship("AttendanceEvent", back_populates="enrollment", cascade="all, delete-orphan")
    assessment_results = relationship("AssessmentResult", back_populates="enrollment", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Enrollment {self.id} - {self.status}>"

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "course_id": self.course_id,
            "status": self.status,
            "enrollment_date": self.enrollment_date.isoformat() if self.enrollment_date else None,
            "completion_date": self.completion_date.isoformat() if self.completion_date else None,
            "final_grade": self.final_grade,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

