"""
Course Repository
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from data.models.course import Course
from data.repositories.base_repository import BaseRepository


class CourseRepository(BaseRepository[Course]):
    def __init__(self, session: Optional[Session] = None):
        super().__init__(Course, session)

    def get_by_code(self, code: str) -> Optional[Course]:
        return self.session.query(Course).filter(Course.code == code).first()

    def get_by_department(self, department: str) -> List[Course]:
        return self.session.query(Course).filter(Course.department == department).all()

    def get_by_semester(self, semester: str) -> List[Course]:
        return self.session.query(Course).filter(Course.semester == semester).all()

