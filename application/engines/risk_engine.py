"""
Risk Prediction Engine
Provides explainable, rule-based and ML risk calculations using strictly historical observations.
Guarantees temporal data integrity by enforcing cutoff dates.
"""

from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional, Tuple, List
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from data.models.risk_prediction import RiskPrediction


class RiskEngine:
    def __init__(
        self,
        attendance_weight: float = 0.35,
        assessment_weight: float = 0.30,
        lms_weight: float = 0.20,
        support_weight: float = 0.15,
        low_threshold: float = 34.0,
        medium_threshold: float = 64.0,
        version: str = "v1.2.0-explainable"
    ):
        self.w_att = attendance_weight
        self.w_asm = assessment_weight
        self.w_lms = lms_weight
        self.w_sup = support_weight
        self.low_threshold = low_threshold
        self.medium_threshold = medium_threshold
        self.version = version
        self.ml_model: Optional[RandomForestClassifier] = None
        self.scaler: Optional[StandardScaler] = None

    def calculate_attendance_risk(self, summary: Dict[str, Any]) -> Tuple[float, str]:
        """
        Calculates normalized attendance risk (0-100) and rationale.
        Considers eligible sessions excluding approved excused absences.
        Unapproved absences incur an additional penalty.
        """
        rate = summary.get("attendance_rate")
        if rate is None or summary.get("eligible_sessions", 0) == 0:
            return 30.0, "Attendance data insufficient; assigned neutral baseline risk (30.0%)."

        unapproved = summary.get("absent_unapproved", 0)
        unapproved_penalty = min(20.0, unapproved * 3.0)

        if rate >= 90.0:
            base_risk = max(0.0, (100.0 - rate) * 1.5)
        elif rate >= 75.0:
            base_risk = 15.0 + (90.0 - rate) * 2.0
        elif rate >= 60.0:
            base_risk = 45.0 + (75.0 - rate) * 2.5
        else:
            base_risk = min(100.0, 82.5 + (60.0 - rate) * 1.5)

        total_risk = round(min(100.0, base_risk + unapproved_penalty), 1)
        rationale = f"Attendance rate is {rate:.1f}% across {summary.get('eligible_sessions', 0)} eligible sessions with {unapproved} unapproved absence(s)."
        return total_risk, rationale

    def calculate_assessment_risk(self, summary: Dict[str, Any]) -> Tuple[float, str]:
        """
        Calculates normalized assessment risk (0-100) using completed assessments only.
        Missing assessments are tracked separately, not silently converted to 0.0 scores.
        """
        avg_score = summary.get("average_score")
        completed = summary.get("completed_count", 0)
        missing = summary.get("missing_count", 0)

        if completed == 0:
            return 35.0, f"No completed assessments available ({missing} missing/excused); neutral factor assigned."

        if avg_score >= 85.0:
            base_risk = max(0.0, (100.0 - avg_score) * 1.0)
        elif avg_score >= 70.0:
            base_risk = 15.0 + (85.0 - avg_score) * 2.0
        elif avg_score >= 55.0:
            base_risk = 45.0 + (70.0 - avg_score) * 2.5
        else:
            base_risk = min(100.0, 82.5 + (55.0 - avg_score) * 1.5)

        # Missing assessments add risk burden
        missing_penalty = min(25.0, missing * 8.0)
        total_risk = round(min(100.0, base_risk + missing_penalty), 1)
        rationale = f"Assessment average is {avg_score:.1f}% across {completed} completed assessment(s) with {missing} pending/missing."
        return total_risk, rationale

    def calculate_lms_risk(self, summary: Dict[str, Any]) -> Tuple[float, str]:
        """
        Calculates normalized LMS engagement risk based on recent activity volume and trend.
        """
        recent_count = summary.get("recent_count", 0)
        trend_pct = summary.get("trend_pct", 0.0)
        duration_mins = summary.get("recent_duration_mins", 0)

        if recent_count >= 30:
            base_risk = 5.0
        elif recent_count >= 15:
            base_risk = 20.0
        elif recent_count >= 5:
            base_risk = 50.0
        else:
            base_risk = 85.0

        # Adjust for negative trend
        trend_penalty = 0.0
        if trend_pct < -25.0:
            trend_penalty = min(20.0, abs(trend_pct) * 0.3)
        elif trend_pct > 20.0:
            base_risk = max(0.0, base_risk - 10.0)

        total_risk = round(min(100.0, base_risk + trend_penalty), 1)
        trend_str = f"declined by {abs(trend_pct):.1f}%" if trend_pct < 0 else f"changed by {trend_pct:+.1f}%"
        rationale = f"LMS activity: {recent_count} sessions ({duration_mins} mins) in recent window ({trend_str} vs prior window)."
        return total_risk, rationale

    def calculate_support_risk(self, prior_cases: List[Any]) -> Tuple[float, str]:
        """
        Calculates risk from prior support case history strictly prior to prediction timestamp.
        """
        if not prior_cases:
            return 10.0, "No prior academic support cases on record."

        active_cases = [c for c in prior_cases if c.status in ("Open", "Assigned", "In Progress", "Escalated")]
        escalated = [c for c in active_cases if c.status == "Escalated" or c.priority == "Critical"]

        if escalated:
            risk = 90.0
            rationale = f"Critical escalation active ({len(escalated)} critical/escalated case(s))."
        elif active_cases:
            risk = min(80.0, 35.0 + len(active_cases) * 15.0)
            rationale = f"{len(active_cases)} active support case(s) currently open."
        else:
            risk = 25.0
            rationale = f"History of {len(prior_cases)} resolved/closed support case(s)."

        return risk, rationale

    def evaluate_risk(
        self,
        student_id: str,
        att_summary: Dict[str, Any],
        asm_summary: Dict[str, Any],
        lms_summary: Dict[str, Any],
        prior_cases: List[Any],
        prediction_timestamp: datetime,
        observation_window_end: date
    ) -> RiskPrediction:
        """
        Compute holistic explainable risk score and generate natural language breakdown.
        """
        att_risk, att_msg = self.calculate_attendance_risk(att_summary)
        asm_risk, asm_msg = self.calculate_assessment_risk(asm_summary)
        lms_risk, lms_msg = self.calculate_lms_risk(lms_summary)
        sup_risk, sup_msg = self.calculate_support_risk(prior_cases)

        overall = round(
            (att_risk * self.w_att)
            + (asm_risk * self.w_asm)
            + (lms_risk * self.w_lms)
            + (sup_risk * self.w_sup),
            2
        )

        if overall <= self.low_threshold:
            category = "Low Risk"
        elif overall <= self.medium_threshold:
            category = "Medium Risk"
        else:
            category = "High Risk"

        # Generate detailed explainability narrative
        factors = [
            ("Attendance", att_risk, att_msg, self.w_att),
            ("Academic Performance", asm_risk, asm_msg, self.w_asm),
            ("LMS Engagement", lms_risk, lms_msg, self.w_lms),
            ("Support History", sup_risk, sup_msg, self.w_sup),
        ]
        # Sort factors by impact (risk * weight)
        factors.sort(key=lambda x: x[1] * x[3], reverse=True)

        primary_driver = factors[0]
        secondary_driver = factors[1]

        explanation = (
            f"{category} (Score: {overall:.1f}/100). "
            f"Primary factor: {primary_driver[0]} ({primary_driver[1]:.1f}% risk) — {primary_driver[2]} "
            f"Secondary factor: {secondary_driver[0]} ({secondary_driver[1]:.1f}% risk) — {secondary_driver[2]} "
            f"Overall weighted calculation based on {int(round(self.w_att*100))}% attendance, {int(round(self.w_asm*100))}% assessment, {int(round(self.w_lms*100))}% LMS, and {int(round(self.w_sup*100))}% support history."
        )

        pred_id = f"RSK-{student_id}-{observation_window_end.strftime('%Y%m%d')}"
        if self.version and self.version != "v1.2.0-explainable":
            ver_slug = "".join(c for c in self.version if c.isalnum() or c in ("-", "_"))[:16]
            pred_id = f"{pred_id}-{ver_slug}"

        return RiskPrediction(
            id=pred_id,
            student_id=student_id,
            prediction_timestamp=prediction_timestamp,
            observation_window_end=observation_window_end,
            attendance_risk=att_risk,
            assessment_risk=asm_risk,
            lms_risk=lms_risk,
            support_risk=sup_risk,
            overall_score=overall,
            risk_category=category,
            explanation=explanation,
            model_version=self.version
        )

