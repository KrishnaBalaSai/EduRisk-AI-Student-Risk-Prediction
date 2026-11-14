"""
AssessmentResult Entity Model
"""

from datetime import datetime, date
from sqlalchemy import Column, String, Date, DateTime, Float, ForeignKey, Index
from sqlalchemy.orm import relationship
from data.database import Base


class AssessmentResult(Base):
    __tablename__ = "assessment_results"

    id = Column(String(96), primary_key=True, index=True)  # ASR-{assessment_id}-{student_id}
    assessment_id = Column(String(48), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(String(32), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    enrollment_id = Column(String(64), ForeignKey("enrollments.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Float, nullable=True)  # Null if missing/unsubmitted
    submission_date = Column(Date, nullable=True, index=True)
    status = Column(
        String(32),
        nullable=False,
        default="Graded",
        index=True  # Graded, Submitted, Late, Missing, Excused
    )
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index("idx_asr_student_date", "student_id", "submission_date"),
        Index("idx_asr_assessment_student", "assessment_id", "student_id"),
    )

    # Relationships
    assessment = relationship("Assessment", back_populates="results")
    student = relationship("Student")
    enrollment = relationship("Enrollment", back_populates="assessment_results")

    def __repr__(self):
        return f"<AssessmentResult {self.id} - Score: {self.score}>"

    def to_dict(self):
        return {
            "id": self.id,
            "assessment_id": self.assessment_id,
            "student_id": self.student_id,
            "enrollment_id": self.enrollment_id,
            "score": self.score,
            "submission_date": self.submission_date.isoformat() if self.submission_date else None,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

