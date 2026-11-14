"""
Course Entity Model
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship
from data.database import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(String(32), primary_key=True, index=True)  # CRS-000001
    code = Column(String(32), unique=True, nullable=False, index=True)  # CS101
    title = Column(String(128), nullable=False)
    department = Column(String(64), nullable=False, index=True)
    credits = Column(Integer, nullable=False, default=3)
    instructor_name = Column(String(128), nullable=False)
    semester = Column(String(32), nullable=False, index=True)  # Fall 2026, Spring 2026
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="course", cascade="all, delete-orphan")
    lms_activities = relationship("LMSActivity", back_populates="course")

    def __repr__(self):
        return f"<Course {self.id} ({self.code}: {self.title})>"

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "title": self.title,
            "department": self.department,
            "credits": self.credits,
            "instructor_name": self.instructor_name,
            "semester": self.semester,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

