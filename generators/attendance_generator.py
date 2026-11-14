"""
Attendance Event Generator
Generates weekly attendance sessions over the academic year with realistic status distributions.
"""

import random
from datetime import date, timedelta
from typing import List, Dict, Any
from data.models.enrollment import Enrollment
from data.models.attendance import AttendanceEvent


def generate_attendance_events(
    enrollments: List[Enrollment],
    course_map: Dict[str, Any],
    student_map: Dict[str, Any],
    archetypes: Dict[str, str],
    seed: int = 20261022
) -> List[AttendanceEvent]:
    """
    Generate weekly attendance events for each active enrollment across the course term.
    """
    rng = random.Random(seed)
    attendance_events: List[AttendanceEvent] = []

    # Distribution table: [Present, Late, Absent_Approved, Absent_Unapproved]
    dist_table = {
        "High_Achiever": [0.93, 0.04, 0.02, 0.01],
        "Steady_Average": [0.80, 0.08, 0.06, 0.06],
        "At_Risk": [0.55, 0.12, 0.08, 0.25],
        "Chronic_Struggling": [0.35, 0.10, 0.05, 0.50],
        "Withdrawn": [0.70, 0.05, 0.05, 0.20],
    }
    choices = ["Present", "Late", "Absent_Approved", "Absent_Unapproved"]

    for enr in enrollments:
        student = student_map.get(enr.student_id)
        course = course_map.get(enr.course_id)
        if not student or not course:
            continue

        arch = archetypes.get(enr.student_id, "Steady_Average")
        weights = dist_table.get(arch, dist_table["Steady_Average"])

        # Determine term start and end dates
        if course.semester == "Fall 2026":
            term_start = date(2026, 9, 7)  # First Monday
            term_weeks = 14
        else:
            term_start = date(2027, 1, 18)
            term_weeks = 14

        withdrawal_dt = student.withdrawal_date

        for week in range(term_weeks):
            session_dt = term_start + timedelta(weeks=week)

            # If student withdrew before this session, handle according to lifecycle:
            # In baseline data, withdrawn students do not attend sessions after withdrawal!
            if withdrawal_dt and session_dt > withdrawal_dt:
                continue

            # Deterministic status selection
            status = rng.choices(choices, weights=weights)[0]

            # Session type
            session_type = "Lab" if (week % 4 == 0) else "Lecture"

            notes = None
            if status == "Absent_Approved":
                notes = rng.choice(["Medical Certificate Submitted", "Official University Athlete Leave", "Family Emergency Approved"])
            elif status == "Absent_Unapproved":
                notes = "Unnotified Absence"

            att_id = f"ATT-{enr.id}-{session_dt.isoformat()}"
            event = AttendanceEvent(
                id=att_id,
                enrollment_id=enr.id,
                student_id=enr.student_id,
                course_id=enr.course_id,
                session_date=session_dt,
                status=status,
                session_type=session_type,
                notes=notes
            )
            attendance_events.append(event)

    return attendance_events
