"""
LMS Activity Generator
Generates realistic online learning events and timestamp distributions.
"""

import random
from datetime import datetime, timedelta, date
from typing import List, Dict, Any
from data.models.student import Student
from data.models.enrollment import Enrollment
from data.models.lms_activity import LMSActivity

ACTIVITY_TYPES = [
    ("Login", 0.35, 120, 600),
    ("Content_View", 0.40, 300, 1800),
    ("Assignment_Submit", 0.08, 600, 2400),
    ("Forum_Post", 0.07, 240, 1200),
    ("Quiz_Attempt", 0.10, 900, 3600),
]


def generate_lms_activity(
    students: List[Student],
    student_enrollments: Dict[str, List[Enrollment]],
    archetypes: Dict[str, str],
    seed: int = 20261022
) -> List[LMSActivity]:
    """
    Generate realistic LMS activity logs for all students over the academic year.
    """
    rng = random.Random(seed)
    activities: List[LMSActivity] = []
    global_lms_id = 1

    event_counts = {
        "High_Achiever": (45, 65),
        "Steady_Average": (25, 40),
        "At_Risk": (12, 22),
        "Chronic_Struggling": (4, 10),
        "Withdrawn": (10, 20),
    }

    types = [t[0] for t in ACTIVITY_TYPES]
    weights = [t[1] for t in ACTIVITY_TYPES]
    durations = {t[0]: (t[2], t[3]) for t in ACTIVITY_TYPES}

    base_start = datetime(2026, 9, 1, 8, 0, 0)
    base_end = datetime(2027, 5, 20, 20, 0, 0)
    total_seconds = int((base_end - base_start).total_seconds())

    for s in students:
        arch = archetypes.get(s.id, "Steady_Average")
        min_ev, max_ev = event_counts.get(arch, (20, 35))
        n_events = rng.randint(min_ev, max_ev)

        enrs = student_enrollments.get(s.id, [])
        course_ids = [e.course_id for e in enrs] if enrs else [None]

        w_dt = s.withdrawal_date
        max_sec = total_seconds
        if w_dt:
            max_dt = datetime(w_dt.year, w_dt.month, w_dt.day, 23, 59, 59)
            if max_dt > base_start:
                max_sec = min(total_seconds, int((max_dt - base_start).total_seconds()))

        # Generate timestamps
        offsets = sorted([rng.randint(0, max(1, max_sec)) for _ in range(n_events)])

        for offset in offsets:
            act_type = rng.choices(types, weights=weights)[0]
            dur_min, dur_max = durations[act_type]
            duration = rng.randint(dur_min, dur_max)
            timestamp = base_start + timedelta(seconds=offset)
            course_id = rng.choice(course_ids) if course_ids else None

            lms_id = f"LMS-2026-{global_lms_id:06d}"
            global_lms_id += 1

            act = LMSActivity(
                id=lms_id,
                student_id=s.id,
                course_id=course_id,
                activity_type=act_type,
                duration_seconds=duration,
                timestamp=timestamp
            )
            activities.append(act)

    return activities

