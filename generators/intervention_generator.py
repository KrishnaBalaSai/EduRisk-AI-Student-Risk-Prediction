"""
Intervention Generator
Generates interventions tied to support cases or automated early warning triggers.
Ensures strict chronological validity: Trigger -> Scheduled -> Completed.
"""

import random
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
from data.models.support_case import SupportCase
from data.models.intervention import Intervention

INTERVENTION_TYPES = [
    "Academic Counselling",
    "Attendance Follow-up",
    "Mentoring",
    "Learning Support",
    "Parent/Guardian Communication",
    "Study Plan",
    "Faculty Meeting"
]


def generate_interventions(
    support_cases: List[SupportCase],
    seed: int = 20261022
) -> List[Intervention]:
    """
    Generate interventions with strict chronological order and realistic completion statuses.
    """
    rng = random.Random(seed)
    interventions: List[Intervention] = []
    global_int_id = 1

    status_choices = ["Completed", "In Progress", "Scheduled", "Cancelled", "No Show"]
    status_weights = [0.55, 0.20, 0.15, 0.05, 0.05]

    for case in support_cases:
        # A case may spawn 1 or 2 targeted interventions
        n_interventions = 1 if rng.random() < 0.65 else 2

        for _ in range(n_interventions):
            int_id = f"INT-2026-{global_int_id:06d}"
            global_int_id += 1

            itype = rng.choice(INTERVENTION_TYPES)
            staff = case.assigned_staff

            # Chronological integrity: trigger timestamp = case.opened_at + jitter
            trigger_dt = case.opened_at + timedelta(days=rng.randint(0, 3), hours=rng.randint(1, 5))

            # Scheduled date: 2 to 14 days after trigger
            sched_date = (trigger_dt + timedelta(days=rng.randint(2, 14))).date()

            status = rng.choices(status_choices, weights=status_weights)[0]

            completion_date = None
            outcome_notes = None
            if status == "Completed":
                completion_date = sched_date + timedelta(days=rng.randint(0, 3))
                # Realistic outcome notes
                success = rng.random() < 0.60
                if success:
                    outcome_notes = "Positive engagement. Action plan established; student committed to weekly check-ins."
                else:
                    outcome_notes = "Limited engagement. Student acknowledged challenges but demonstrated difficulty adhering to action items."
            elif status == "No Show":
                outcome_notes = "Student failed to attend scheduled session. Follow-up notification sent."
            elif status == "Cancelled":
                outcome_notes = "Cancelled due to schedule conflict. Pending rescheduling."

            notes = f"Initiated following triage of case {case.id}. Focus area: {itype}."

            intervention = Intervention(
                id=int_id,
                student_id=case.student_id,
                case_id=case.id,
                intervention_type=itype,
                assigned_staff=staff,
                trigger_timestamp=trigger_dt,
                scheduled_date=sched_date,
                completion_date=completion_date,
                status=status,
                notes=notes,
                outcome_notes=outcome_notes
            )
            interventions.append(intervention)

    return interventions

