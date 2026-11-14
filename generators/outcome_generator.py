"""
Future Outcome Generator
Generates ground-truth academic outcomes derived from behavioral trajectories and intervention impact.
Strictly separated from risk prediction input features.
"""

import random
from datetime import date
from typing import List, Dict, Any
from data.models.student import Student
from data.models.intervention import Intervention
from data.models.outcome import Outcome

OUTCOME_RULES_DOC = """
DOCUMENTED OUTCOME DERIVATION RULES:
1. Withdrawn Rule: Any student with status == 'Withdrawn' is evaluated as 'Course withdrawal'.
   is_recovery=False, gpa_change negative (-10 to -25), attendance_change negative.
2. High Achiever Rule: Students with 'High_Achiever' archetype are evaluated as 'Course completion'.
   is_recovery=False (never at risk), gpa_change positive/neutral (+1 to +5), attendance_change (0 to +2).
3. Steady Average Rule: Students with 'Steady_Average' archetype are evaluated as 'Course completion'.
   is_recovery=False, gpa_change (-2 to +5), attendance_change (-3 to +3).
4. At-Risk / Chronic with Successful Intervention:
   If the student completed an intervention and demonstrated positive engagement,
   derive 'Successful recovery' (40%) or 'Improved academic performance' (60%).
   is_recovery=True, gpa_change (+8 to +22), attendance_change (+10 to +25).
5. At-Risk / Chronic with Unsuccessful or No Intervention:
   Evaluate as 'Continued academic risk'.
   is_recovery=False, gpa_change (-15 to 0), attendance_change (-15 to -5).
"""


def generate_outcomes(
    students: List[Student],
    student_interventions: Dict[str, List[Intervention]],
    archetypes: Dict[str, str],
    evaluation_date: date = date(2027, 5, 30),
    seed: int = 20261022
) -> List[Outcome]:
    """
    Generate ground-truth future outcomes based on the documented deterministic rules.
    """
    rng = random.Random(seed)
    outcomes: List[Outcome] = []
    global_out_id = 1

    for s in students:
        out_id = f"OUT-2026-{global_out_id:06d}"
        global_out_id += 1

        arch = archetypes.get(s.id, "Steady_Average")
        interventions = student_interventions.get(s.id, [])
        has_completed_int = any(
            i.status == "Completed" and "Positive engagement" in (i.outcome_notes or "")
            for i in interventions
        )

        if s.status == "Withdrawn":
            label = "Course withdrawal"
            gpa_chg = round(rng.uniform(-25.0, -10.0), 1)
            att_chg = round(rng.uniform(-35.0, -15.0), 1)
            is_rec = False
            notes = "Student officially withdrew prior to semester conclusion."

        elif arch == "High_Achiever":
            label = "Course completion"
            gpa_chg = round(rng.uniform(1.0, 5.0), 1)
            att_chg = round(rng.uniform(0.0, 3.0), 1)
            is_rec = False
            notes = "Academic performance remained consistently superior throughout the academic year."

        elif arch == "Steady_Average":
            label = "Course completion"
            gpa_chg = round(rng.uniform(-2.0, 4.0), 1)
            att_chg = round(rng.uniform(-2.0, 3.0), 1)
            is_rec = False
            notes = "Successfully satisfied all degree curriculum requirements with satisfactory standing."

        elif arch in ("At_Risk", "Chronic_Struggling"):
            if has_completed_int and rng.random() < 0.65:
                label = "Successful recovery" if arch == "Chronic_Struggling" else "Improved academic performance"
                gpa_chg = round(rng.uniform(8.0, 20.0), 1)
                att_chg = round(rng.uniform(12.0, 26.0), 1)
                is_rec = True
                notes = "Student responded proactively to personalized academic interventions, achieving measurable recovery."
            else:
                label = "Continued academic risk"
                gpa_chg = round(rng.uniform(-18.0, -2.0), 1)
                att_chg = round(rng.uniform(-20.0, -5.0), 1)
                is_rec = False
                notes = "Persistent risk indicators remained unresolved across observation periods."

        else:
            label = "Course completion"
            gpa_chg = 0.0
            att_chg = 0.0
            is_rec = False
            notes = "Standard course progression recorded."

        outcome = Outcome(
            id=out_id,
            student_id=s.id,
            course_id=None,
            evaluation_date=evaluation_date,
            outcome_label=label,
            gpa_change=gpa_chg,
            attendance_change=att_chg,
            is_recovery=is_rec,
            notes=notes
        )
        outcomes.append(outcome)

    return outcomes

