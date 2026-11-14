"""
AttendanceEvent Entity Model
"""

from datetime import datetime, date
from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from data.database import Base


class AttendanceEvent(Base):
    __tablename__ = "attendance_events"

    id = Column(String(96), primary_key=True, index=True)  # ATT-{enrollment_id}-{date}
    enrollment_id = Column(String(64), ForeignKey("enrollments.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(String(32), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(String(32), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    session_date = Column(Date, nullable=False, index=True)
    status = Column(
        String(32),
        nullable=False,
        default="Present",
        index=True  # Present, Absent_Unapproved, Absent_Approved, Late
    )
    session_type = Column(String(32), nullable=False, default="Lecture")  # Lecture, Lab, Seminar
    notes = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index("idx_att_student_date", "student_id", "session_date"),
        Index("idx_att_enrollment_date", "enrollment_id", "session_date"),
    )

    # Relationships
    enrollment = relationship("Enrollment", back_populates="attendance_events")
    student = relationship("Student")
    course = relationship("Course")

    def __repr__(self):
        return f"<AttendanceEvent {self.id} ({self.status})>"

    def to_dict(self):
        return {
            "id": self.id,
            "enrollment_id": self.enrollment_id,
            "student_id": self.student_id,
            "course_id": self.course_id,
            "session_date": self.session_date.isoformat() if self.session_date else None,
            "status": self.status,
            "session_type": self.session_type,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

