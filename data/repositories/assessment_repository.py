"""
Assessment and Assessment Result Repository
"""

from typing import List, Optional, Dict, Any
from datetime import date
from sqlalchemy.orm import Session, joinedload
from data.models.assessment import Assessment
from data.models.assessment_result import AssessmentResult
from data.repositories.base_repository import BaseRepository


class AssessmentRepository(BaseRepository[Assessment]):
    def __init__(self, session: Optional[Session] = None):
        super().__init__(Assessment, session)

    def get_by_course(self, course_id: str) -> List[Assessment]:
        return self.session.query(Assessment).filter(Assessment.course_id == course_id).order_by(Assessment.due_date.asc()).all()


class AssessmentResultRepository(BaseRepository[AssessmentResult]):
    def __init__(self, session: Optional[Session] = None):
        super().__init__(AssessmentResult, session)

    def get_by_student(self, student_id: str, cutoff_date: Optional[date] = None) -> List[AssessmentResult]:
        query = (
            self.session.query(AssessmentResult)
            .join(Assessment, AssessmentResult.assessment_id == Assessment.id)
            .filter(AssessmentResult.student_id == student_id)
        )
        if cutoff_date:
            # Only consider assessments due on or before cutoff_date (strict temporal cutoff!)
            query = query.filter(Assessment.due_date <= cutoff_date)
        return query.order_by(Assessment.due_date.asc()).all()

    def get_student_assessment_summary(self, student_id: str, cutoff_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Calculates graded assessment average, completion count, and missing count.
        Completed assessments with valid non-null scores are averaged.
        """
        results = self.get_by_student(student_id, cutoff_date)
        if not results:
            return {
                "total_assessments": 0,
                "completed_count": 0,
                "missing_count": 0,
                "average_score": None,
            }

        valid_scores = [r.score for r in results if r.score is not None and r.status in ("Graded", "Submitted", "Late")]
        missing_count = sum(1 for r in results if r.status == "Missing" or r.score is None)

        avg_score = round(sum(valid_scores) / len(valid_scores), 2) if valid_scores else None

        return {
            "total_assessments": len(results),
            "completed_count": len(valid_scores),
            "missing_count": missing_count,
            "average_score": avg_score,
        }

