"""
Assessment and Assessment Results Generator
Generates realistic multi-assessment structures per course and correlated student grades.
"""

import random
from datetime import date, timedelta
from typing import List, Tuple, Dict, Any
from data.models.course import Course
from data.models.enrollment import Enrollment
from data.models.assessment import Assessment
from data.models.assessment_result import AssessmentResult

ASSESSMENT_TEMPLATES = [
    ("Quiz 1: Core Fundamentals", "Quiz", 100.0, 0.15, 3),
    ("Midterm Examination", "Midterm", 100.0, 0.30, 7),
    ("Programming / Research Assignment", "Assignment", 100.0, 0.20, 10),
    ("Final Comprehensive Project", "Project", 100.0, 0.35, 14),
]


def generate_assessments(courses: List[Course], seed: int = 20261022) -> List[Assessment]:
    """
    Generate standard 4 assessment milestones for each course.
    """
    rng = random.Random(seed)
    assessments: List[Assessment] = []

    for c in courses:
        term_start = date(2026, 9, 7) if c.semester == "Fall 2026" else date(2027, 1, 18)
        
        for seq, (title, atype, max_score, weight, week_offset) in enumerate(ASSESSMENT_TEMPLATES, start=1):
            asm_id = f"ASM-{c.id}-{seq:02d}"
            due_date = term_start + timedelta(weeks=week_offset)
            
            asm = Assessment(
                id=asm_id,
                course_id=c.id,
                title=f"{c.code} {title}",
                assessment_type=atype,
                max_score=max_score,
                weight=weight,
                due_date=due_date
            )
            assessments.append(asm)

    return assessments


def generate_assessment_results(
    assessments: List[Assessment],
    enrollments: List[Enrollment],
    student_map: Dict[str, Any],
    archetypes: Dict[str, str],
    seed: int = 20261022
) -> List[AssessmentResult]:
    """
    Generate assessment results for all students enrolled in each course's assessments.
    """
    rng = random.Random(seed)
    results: List[AssessmentResult] = []

    # Map course_id -> list of assessments
    course_asm_map: Dict[str, List[Assessment]] = {}
    for a in assessments:
        course_asm_map.setdefault(a.course_id, []).append(a)

    score_params = {
        "High_Achiever": (90.0, 5.0, 0.01),      # (mean, std, missing_prob)
        "Steady_Average": (75.0, 7.0, 0.04),
        "At_Risk": (52.0, 10.0, 0.15),
        "Chronic_Struggling": (38.0, 12.0, 0.35),
        "Withdrawn": (70.0, 8.0, 0.10),
    }

    for enr in enrollments:
        student = student_map.get(enr.student_id)
        if not student:
            continue
        course_asms = course_asm_map.get(enr.course_id, [])
        arch = archetypes.get(enr.student_id, "Steady_Average")
        mean_score, std_score, miss_prob = score_params.get(arch, (75.0, 7.0, 0.05))
        withdrawal_dt = student.withdrawal_date

        for idx, asm in enumerate(course_asms):
            # If student withdrew before assessment due date, don't grade in baseline
            if withdrawal_dt and asm.due_date > withdrawal_dt:
                continue

            asr_id = f"ASR-{asm.id}-{enr.student_id}"

            # Simulate performance degradation for At-Risk students across semester
            effective_mean = mean_score
            if arch == "At_Risk":
                effective_mean -= idx * 3.5  # Drops 52 -> 48.5 -> 45 -> 41.5
            elif arch == "High_Achiever":
                effective_mean = min(98.0, effective_mean + idx * 1.0)

            # Determine if missing or submitted
            is_missing = rng.random() < miss_prob
            if is_missing:
                score = None
                sub_date = None
                status = "Missing"
            else:
                raw_score = rng.gauss(effective_mean, std_score)
                score = round(max(0.0, min(100.0, raw_score)), 1)
                sub_date = asm.due_date - timedelta(days=rng.randint(0, 3))
                status = "Late" if rng.random() < 0.08 else "Graded"

            res = AssessmentResult(
                id=asr_id,
                assessment_id=asm.id,
                student_id=enr.student_id,
                enrollment_id=enr.id,
                score=score,
                submission_date=sub_date,
                status=status
            )
            results.append(res)

    return results

