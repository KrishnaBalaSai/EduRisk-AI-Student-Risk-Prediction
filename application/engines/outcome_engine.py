"""
Outcome Evaluation Engine
Evaluates student progression post-intervention and assigns documented ground-truth labels.
"""

from datetime import date
from typing import Dict, Any, Optional
from data.models.outcome import Outcome


class OutcomeEngine:
    @staticmethod
    def evaluate_student_outcome(
        student_id: str,
        baseline_att_rate: float,
        post_att_rate: float,
        baseline_gpa: float,
        post_gpa: float,
        is_withdrawn: bool = False,
        evaluation_date: Optional[date] = None,
        notes: Optional[str] = None
    ) -> Outcome:
        """
        Derives an Outcome entity from quantitative trajectory changes according to business rules.
        """
        eval_dt = evaluation_date or date.today()
        gpa_change = round(post_gpa - baseline_gpa, 2)
        att_change = round(post_att_rate - baseline_att_rate, 2)

        if is_withdrawn:
            label = "Course withdrawal"
            is_rec = False
        elif gpa_change >= 10.0 or (baseline_gpa < 60.0 and post_gpa >= 65.0 and att_change > 5.0):
            label = "Successful recovery"
            is_rec = True
        elif gpa_change > 0.0 or att_change > 5.0:
            label = "Improved academic performance"
            is_rec = (baseline_gpa < 60.0 and post_gpa >= 60.0)
        elif post_gpa < 60.0 or post_att_rate < 65.0:
            label = "Continued academic risk"
            is_rec = False
        else:
            label = "Course completion"
            is_rec = False

        out_id = f"OUT-{student_id}-{eval_dt.strftime('%Y%m%d')}"

        return Outcome(
            id=out_id,
            student_id=student_id,
            course_id=None,
            evaluation_date=eval_dt,
            outcome_label=label,
            gpa_change=gpa_change,
            attendance_change=att_change,
            is_recovery=is_rec,
            notes=notes or f"Evaluated under standard outcome protocol on {eval_dt.isoformat()}."
        )

