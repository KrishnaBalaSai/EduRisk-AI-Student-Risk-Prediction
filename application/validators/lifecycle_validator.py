"""
Lifecycle Validator
Validates student state transitions, course enrollments, and intervention chronology.
Specifically detects ANOMALY 3 (withdrawn student active) and ANOMALY 4 (intervention precedes trigger).
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from data.models.student import Student
from data.models.enrollment import Enrollment
from data.models.intervention import Intervention
from data.models.support_case import SupportCase


class LifecycleValidator:
    def __init__(self, session: Session):
        self.session = session

    def validate_all(self) -> Dict[str, Any]:
        results = {
            "validator": "LifecycleValidator",
            "passed": 0,
            "failed": 0,
            "detected_anomalies": [],
            "errors": [],
        }

        # 1. ANOMALY 3: Withdrawn student remains active
        # Find students who are Withdrawn but hold an enrollment with status == 'Enrolled'
        withdrawn_students = self.session.query(Student).filter(Student.status == "Withdrawn").all()
        for ws in withdrawn_students:
            active_enrs = [e for e in ws.enrollments if e.status == "Enrolled"]
            for bad_enr in active_enrs:
                results["failed"] += 1
                msg = (
                    f"ANOMALY DETECTED [withdrawn_student_active] on Enrollment {bad_enr.id}: "
                    f"Student {ws.id} officially withdrew on {ws.withdrawal_date} but holds active status 'Enrolled'."
                )
                results["detected_anomalies"].append({
                    "issue_type": "withdrawn_student_active",
                    "record_id": bad_enr.id,
                    "entity": "Enrollment",
                    "message": msg
                })
                results["errors"].append(msg)

        if not any(e for ws in withdrawn_students for e in ws.enrollments if e.status == "Enrolled"):
            results["passed"] += 1

        # 2. ANOMALY 4: Intervention precedes its trigger
        # scheduled_date cannot precede trigger_timestamp date!
        interventions = self.session.query(Intervention).all()
        for it in interventions:
            trigger_d = it.trigger_timestamp.date()
            if it.scheduled_date < trigger_d:
                results["failed"] += 1
                msg = (
                    f"ANOMALY DETECTED [intervention_precedes_trigger] on Intervention {it.id}: "
                    f"Scheduled date ({it.scheduled_date}) is earlier than trigger date ({trigger_d}). Chronological violation."
                )
                results["detected_anomalies"].append({
                    "issue_type": "intervention_precedes_trigger",
                    "record_id": it.id,
                    "entity": "Intervention",
                    "message": msg
                })
                results["errors"].append(msg)
            else:
                results["passed"] += 1

        # 3. Check for Closed Support Cases with active interventions
        closed_cases = self.session.query(SupportCase).filter(SupportCase.status == "Closed").all()
        for cc in closed_cases:
            active_ints = [i for i in cc.interventions if i.status in ("Scheduled", "In Progress")]
            if active_ints:
                results["failed"] += len(active_ints)
                results["errors"].append(
                    f"Closed support case {cc.id} has {len(active_ints)} active intervention(s) without being reopened."
                )
            else:
                results["passed"] += 1

        return results

