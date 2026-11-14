"""
Support Case Application Service
Manages support case lifecycles, triage queues, staff assignments, and escalation workflows.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from data.models.support_case import SupportCase
from data.repositories.support_repository import SupportRepository
from data.repositories.student_repository import StudentRepository


class SupportService:
    def __init__(
        self,
        support_repo: Optional[SupportRepository] = None,
        student_repo: Optional[StudentRepository] = None
    ):
        self.support_repo = support_repo or SupportRepository()
        self.student_repo = student_repo or StudentRepository()

    def get_all_cases(self, limit: int = 1000) -> List[SupportCase]:
        return self.support_repo.get_all(limit=limit)

    def get_case_by_id(self, case_id: str) -> Optional[SupportCase]:
        return self.support_repo.get_by_id(case_id)

    def get_cases_for_student(self, student_id: str) -> List[SupportCase]:
        return self.support_repo.get_by_student(student_id)

    def get_cases_by_status(self, status: str) -> List[SupportCase]:
        return self.support_repo.get_by_status(status)

    def create_case(
        self,
        student_id: str,
        trigger_reason: str,
        priority: str = "Medium",
        assigned_staff: str = "Unassigned",
        risk_prediction_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> SupportCase:
        """
        Create a new support case while ensuring duplicate active cases are prevented.
        """
        student = self.student_repo.get_by_id(student_id)
        if not student:
            raise ValueError(f"Student {student_id} does not exist.")

        # Check for active case to avoid duplicate open tickets
        active_cases = self.support_repo.get_active_cases_for_student(student_id)
        if active_cases:
            existing = active_cases[0]
            existing.notes = (existing.notes or "") + f"\n[{datetime.utcnow().strftime('%Y-%m-%d')}] Additional trigger: {trigger_reason}"
            if priority in ("High", "Critical"):
                existing.priority = priority
            return self.support_repo.update(existing)

        case_count = self.support_repo.count() + 1
        case_id = f"CAS-2026-{case_count:06d}"

        case = SupportCase(
            id=case_id,
            student_id=student_id,
            risk_prediction_id=risk_prediction_id,
            trigger_reason=trigger_reason,
            status="Open",
            priority=priority,
            assigned_staff=assigned_staff,
            opened_at=datetime.utcnow(),
            resolved_at=None,
            notes=notes or f"Case initiated via early warning trigger: {trigger_reason}"
        )
        return self.support_repo.create(case)

    def update_case_status(
        self,
        case_id: str,
        new_status: str,
        notes: Optional[str] = None
    ) -> SupportCase:
        case = self.support_repo.get_by_id(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found.")

        valid_statuses = ["Open", "Assigned", "In Progress", "Resolved", "Closed", "Escalated"]
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status: {new_status}. Allowed: {valid_statuses}")

        case.status = new_status
        if notes:
            case.notes = (case.notes or "") + f"\n[{datetime.utcnow().strftime('%Y-%m-%d')}] Status changed to {new_status}: {notes}"

        if new_status in ("Resolved", "Closed"):
            case.resolved_at = datetime.utcnow()

        return self.support_repo.update(case)

    def assign_staff(self, case_id: str, staff_name: str) -> SupportCase:
        case = self.support_repo.get_by_id(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found.")
        case.assigned_staff = staff_name
        if case.status == "Open":
            case.status = "Assigned"
        return self.support_repo.update(case)

