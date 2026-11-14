"""
Intervention Application Service
Coordinates intervention workflows, scheduling, completion evaluations, and chronological validation.
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any
from data.models.intervention import Intervention
from data.repositories.intervention_repository import InterventionRepository
from data.repositories.student_repository import StudentRepository
from data.repositories.support_repository import SupportRepository
from application.engines.intervention_engine import InterventionEngine


class InterventionService:
    def __init__(
        self,
        intervention_repo: Optional[InterventionRepository] = None,
        student_repo: Optional[StudentRepository] = None,
        support_repo: Optional[SupportRepository] = None,
        engine: Optional[InterventionEngine] = None
    ):
        self.intervention_repo = intervention_repo or InterventionRepository()
        self.student_repo = student_repo or StudentRepository()
        self.support_repo = support_repo or SupportRepository()
        self.engine = engine or InterventionEngine()

    def get_all_interventions(self, limit: int = 1000) -> List[Intervention]:
        return self.intervention_repo.get_all(limit=limit)

    def get_by_student(self, student_id: str) -> List[Intervention]:
        return self.intervention_repo.get_by_student(student_id)

    def get_by_status(self, status: str) -> List[Intervention]:
        return self.intervention_repo.get_by_status(status)

    def schedule_intervention(
        self,
        student_id: str,
        intervention_type: str,
        assigned_staff: str,
        scheduled_date: date,
        case_id: Optional[str] = None,
        trigger_dt: Optional[datetime] = None,
        notes: Optional[str] = None
    ) -> Intervention:
        """
        Create a new intervention with explicit chronological validation.
        Trigger timestamp must occur before scheduled_date!
        """
        student = self.student_repo.get_by_id(student_id)
        if not student:
            raise ValueError(f"Student {student_id} not found.")

        trigger_time = trigger_dt or datetime.utcnow()
        if scheduled_date < trigger_time.date():
            raise ValueError(
                f"Chronological violation: Scheduled date ({scheduled_date}) cannot precede trigger date ({trigger_time.date()})."
            )

        int_count = self.intervention_repo.count() + 1
        int_id = f"INT-2026-{int_count:06d}"

        intervention = Intervention(
            id=int_id,
            student_id=student_id,
            case_id=case_id,
            intervention_type=intervention_type,
            assigned_staff=assigned_staff,
            trigger_timestamp=trigger_time,
            scheduled_date=scheduled_date,
            completion_date=None,
            status="Scheduled",
            notes=notes or f"Scheduled {intervention_type} on {scheduled_date.isoformat()}.",
            outcome_notes=None
        )
        return self.intervention_repo.create(intervention)

    def complete_intervention(
        self,
        intervention_id: str,
        completion_date: date,
        outcome_notes: str,
        status: str = "Completed"
    ) -> Intervention:
        intervention = self.intervention_repo.get_by_id(intervention_id)
        if not intervention:
            raise ValueError(f"Intervention {intervention_id} not found.")

        if completion_date < intervention.scheduled_date:
            raise ValueError(
                f"Completion date ({completion_date}) cannot precede scheduled date ({intervention.scheduled_date})."
            )

        intervention.status = status
        intervention.completion_date = completion_date
        intervention.outcome_notes = outcome_notes
        return self.intervention_repo.update(intervention)

    def get_active_count(self) -> int:
        return len(self.intervention_repo.get_active_interventions())

    def get_success_rate(self) -> float:
        all_ints = self.intervention_repo.get_all(limit=5000)
        completed = [i for i in all_ints if i.status == "Completed"]
        if not completed:
            return 0.0
        successful = sum(
            1 for i in completed if "Positive engagement" in (i.outcome_notes or "") or "committed" in (i.outcome_notes or "")
        )
        return round((successful / len(completed)) * 100, 1)

