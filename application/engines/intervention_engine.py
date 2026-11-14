"""
Intervention Recommendation Engine
Analyzes risk factor contributions and recommends targeted, evidence-based interventions.
"""

from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
from data.models.risk_prediction import RiskPrediction
from data.models.intervention import Intervention

STAFF_ROSTER = {
    "Attendance Follow-up": "Aria Montgomery (Retention Coordinator)",
    "Academic Counselling": "Dr. Eleanor Vance (Lead Academic Advisor)",
    "Learning Support": "Sarah Jenkins (Learning Support Coach)",
    "Mentoring": "Marcus Holloway (Student Success Specialist)",
    "Parent/Guardian Communication": "Aria Montgomery (Retention Coordinator)",
    "Study Plan": "David Chen (Academic Counselor)",
    "Faculty Meeting": "Dr. Eleanor Vance (Lead Academic Advisor)",
}


class InterventionEngine:
    @staticmethod
    def recommend_interventions(prediction: RiskPrediction) -> List[Dict[str, Any]]:
        """
        Evaluate risk prediction factor scores and produce prioritized recommendations.
        """
        recommendations = []

        # 1. Attendance Check
        if prediction.attendance_risk >= 55.0:
            rec_type = "Attendance Follow-up" if prediction.attendance_risk < 75.0 else "Parent/Guardian Communication"
            recommendations.append({
                "type": rec_type,
                "urgency": "High" if prediction.attendance_risk >= 75.0 else "Medium",
                "reason": f"Elevated attendance risk ({prediction.attendance_risk:.1f}%). Requires structured attendance intervention.",
                "assigned_staff": STAFF_ROSTER.get(rec_type, "Retention Specialist")
            })

        # 2. Assessment Check
        if prediction.assessment_risk >= 50.0:
            rec_type = "Study Plan" if prediction.assessment_risk < 70.0 else "Academic Counselling"
            recommendations.append({
                "type": rec_type,
                "urgency": "High" if prediction.assessment_risk >= 70.0 else "Medium",
                "reason": f"Assessment risk ({prediction.assessment_risk:.1f}%). Student requires targeted study plan or remedial counselling.",
                "assigned_staff": STAFF_ROSTER.get(rec_type, "Academic Counselor")
            })

        # 3. LMS Engagement Check
        if prediction.lms_risk >= 60.0:
            recommendations.append({
                "type": "Learning Support",
                "urgency": "Medium",
                "reason": f"Declining digital engagement ({prediction.lms_risk:.1f}% risk). Connect with learning coach for portal navigation.",
                "assigned_staff": STAFF_ROSTER.get("Learning Support", "Learning Coach")
            })

        # 4. Critical Support Check
        if prediction.support_risk >= 75.0 or prediction.overall_score >= 75.0:
            recommendations.append({
                "type": "Faculty Meeting",
                "urgency": "Critical",
                "reason": "Severe multifaceted risk detected. Comprehensive faculty review recommended.",
                "assigned_staff": STAFF_ROSTER.get("Faculty Meeting", "Lead Advisor")
            })

        # If overall score is medium/high but no single factor fired, default to Mentoring
        if not recommendations and prediction.overall_score >= 35.0:
            recommendations.append({
                "type": "Mentoring",
                "urgency": "Low",
                "reason": f"General proactive check-in (Risk score: {prediction.overall_score:.1f}).",
                "assigned_staff": STAFF_ROSTER.get("Mentoring", "Student Mentor")
            })

        return recommendations

    @staticmethod
    def build_intervention(
        student_id: str,
        recommendation: Dict[str, Any],
        case_id: Optional[str] = None,
        trigger_dt: Optional[datetime] = None,
        days_ahead: int = 3
    ) -> Intervention:
        """
        Create a valid, chronologically sound Intervention entity from a recommendation.
        """
        now = trigger_dt or datetime.utcnow()
        sched_date = (now + timedelta(days=days_ahead)).date()
        itype = recommendation["type"]
        staff = recommendation.get("assigned_staff", STAFF_ROSTER.get(itype, "Academic Staff"))

        int_id = f"INT-{student_id}-{sched_date.strftime('%Y%m%d')}"

        return Intervention(
            id=int_id,
            student_id=student_id,
            case_id=case_id,
            intervention_type=itype,
            assigned_staff=staff,
            trigger_timestamp=now,
            scheduled_date=sched_date,
            completion_date=None,
            status="Scheduled",
            notes=f"Created automatically from risk analysis recommendation: {recommendation['reason']}",
            outcome_notes=None
        )

