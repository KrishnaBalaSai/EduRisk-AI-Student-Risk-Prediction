"""
Enrollment Repository
"""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from data.models.enrollment import Enrollment
from data.repositories.base_repository import BaseRepository


class EnrollmentRepository(BaseRepository[Enrollment]):
    def __init__(self, session: Optional[Session] = None):
        super().__init__(Enrollment, session)

    def get_by_student(self, student_id: str) -> List[Enrollment]:
        return (
            self.session.query(Enrollment)
            .options(joinedload(Enrollment.course))
            .filter(Enrollment.student_id == student_id)
            .all()
        )

    def get_by_course(self, course_id: str) -> List[Enrollment]:
        return (
            self.session.query(Enrollment)
            .options(joinedload(Enrollment.student))
            .filter(Enrollment.course_id == course_id)
            .all()
        )

    def get_by_student_and_course(self, student_id: str, course_id: str) -> Optional[Enrollment]:
        return (
            self.session.query(Enrollment)
            .filter(Enrollment.student_id == student_id, Enrollment.course_id == course_id)
            .first()
        )

    def get_active_enrollments(self) -> List[Enrollment]:
        return self.session.query(Enrollment).filter(Enrollment.status == "Enrolled").all()

