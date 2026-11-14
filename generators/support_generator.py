"""
Support Case Generator
Generates realistic academic support workflows and triage cases based on early warning indicators.
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from data.models.student import Student
from data.models.support_case import SupportCase

STAFF_MEMBERS = [
    "Dr. Eleanor Vance (Lead Academic Advisor)",
    "Marcus Holloway (Student Success Specialist)",
    "Aria Montgomery (Retention Coordinator)",
    "David Chen (Academic Counselor)",
    "Sarah Jenkins (Learning Support Coach)"
]

CASE_REASONS = [
    "Automated Risk Alert: Attendance dropped below 60% with consecutive unexcused absences",
    "Academic Warning: Failing marks on Quiz 1 and Midterm Examination",
    "Engagement Alert: Zero LMS portal activity recorded for 18 consecutive days",
    "Instructor Referral: Student visibly struggling with foundational concepts and coursework",
    "Combined Risk Trigger: Declining attendance (54%) and missed midterm assignment"
]


def generate_support_cases(
    students: List[Student],
    archetypes: Dict[str, str],
    seed: int = 20261022
) -> List[SupportCase]:
    """
    Generate realistic support cases for students demonstrating at-risk or struggling patterns.
    """
    rng = random.Random(seed)
    cases: List[SupportCase] = []
    global_case_id = 1

    case_prob = {
        "High_Achiever": 0.02,
        "Steady_Average": 0.08,
        "At_Risk": 0.70,
        "Chronic_Struggling": 0.92,
        "Withdrawn": 0.65,
    }

    status_choices = ["Open", "Assigned", "In Progress", "Resolved", "Closed", "Escalated"]
    status_weights = [0.15, 0.20, 0.25, 0.25, 0.10, 0.05]

    for s in students:
        arch = archetypes.get(s.id, "Steady_Average")
        prob = case_prob.get(arch, 0.10)

        if rng.random() < prob:
            case_id = f"CAS-2026-{global_case_id:06d}"
            global_case_id += 1

            reason = rng.choice(CASE_REASONS)
            status = rng.choices(status_choices, weights=status_weights)[0]
            staff = rng.choice(STAFF_MEMBERS)
            priority = "Critical" if arch == "Chronic_Struggling" else ("High" if arch in ("At_Risk", "Withdrawn") else "Medium")

            opened_offset_days = rng.randint(45, 90)
            opened_at = datetime(2026, 9, 1, 9, 0, 0) + timedelta(days=opened_offset_days, hours=rng.randint(0, 8))

            resolved_at = None
            if status in ("Resolved", "Closed"):
                resolved_at = opened_at + timedelta(days=rng.randint(7, 28))

            notes = (
                f"Initial triage conducted on {opened_at.strftime('%Y-%m-%d')}. "
                f"Student flagged under {priority} priority protocol due to {reason.lower()}."
            )

            case = SupportCase(
                id=case_id,
                student_id=s.id,
                risk_prediction_id=None,
                trigger_reason=reason,
                status=status,
                priority=priority,
                assigned_staff=staff,
                opened_at=opened_at,
                resolved_at=resolved_at,
                notes=notes
            )
            cases.append(case)

    return cases

