"""
Student Repository
"""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from data.models.student import Student
from data.repositories.base_repository import BaseRepository


class StudentRepository(BaseRepository[Student]):
    def __init__(self, session: Optional[Session] = None):
        super().__init__(Student, session)

    def get_by_email(self, email: str) -> Optional[Student]:
        return self.session.query(Student).filter(Student.email == email).first()

    def get_by_cohort(self, cohort: str) -> List[Student]:
        return self.session.query(Student).filter(Student.cohort == cohort).all()

    def get_by_status(self, status: str) -> List[Student]:
        return self.session.query(Student).filter(Student.status == status).all()

    def search(self, query_str: str, limit: int = 100) -> List[Student]:
        term = f"%{query_str}%"
        return (
            self.session.query(Student)
            .filter(
                (Student.id.ilike(term))
                | (Student.first_name.ilike(term))
                | (Student.last_name.ilike(term))
                | (Student.email.ilike(term))
                | (Student.cohort.ilike(term))
            )
            .limit(limit)
            .all()
        )

    def get_student_with_relations(self, student_id: str) -> Optional[Student]:
        return (
            self.session.query(Student)
            .options(
                joinedload(Student.enrollments),
                joinedload(Student.support_cases),
                joinedload(Student.interventions),
                joinedload(Student.risk_predictions),
            )
            .filter(Student.id == student_id)
            .first()
        )

