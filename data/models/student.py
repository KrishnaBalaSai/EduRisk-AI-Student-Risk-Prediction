"""
Student Entity Model
"""

from datetime import datetime, date
from sqlalchemy import Column, String, Date, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from data.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(String(32), primary_key=True, index=True)  # STU-2026-000001
    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=False)
    email = Column(String(128), unique=True, nullable=False, index=True)
    cohort = Column(String(32), nullable=False, index=True)
    status = Column(
        String(32),
        nullable=False,
        default="Active",
        index=True  # Active, Withdrawn, Graduated, Suspended
    )
    enrollment_date = Column(Date, nullable=False, default=date.today)
    withdrawal_date = Column(Date, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")
    lms_activities = relationship("LMSActivity", back_populates="student", cascade="all, delete-orphan")
    support_cases = relationship("SupportCase", back_populates="student", cascade="all, delete-orphan")
    interventions = relationship("Intervention", back_populates="student", cascade="all, delete-orphan")
    outcomes = relationship("Outcome", back_populates="student", cascade="all, delete-orphan")
    risk_predictions = relationship("RiskPrediction", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student {self.id} ({self.first_name} {self.last_name}) - {self.status}>"

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "cohort": self.cohort,
            "status": self.status,
            "enrollment_date": self.enrollment_date.isoformat() if self.enrollment_date else None,
            "withdrawal_date": self.withdrawal_date.isoformat() if self.withdrawal_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

