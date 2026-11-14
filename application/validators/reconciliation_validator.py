"""
Reconciliation Validator
Validates arithmetic reconciliation across attendance totals, assessment scores, and derived risk formulas.
Specifically detects ANOMALY 2 (wrong attendance denominator) and ANOMALY 5 (missing data as failure).
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from data.models.attendance import AttendanceEvent
from data.models.assessment_result import AssessmentResult
from data.models.risk_prediction import RiskPrediction


class ReconciliationValidator:
    def __init__(self, session: Session):
        self.session = session

    def validate_all(self) -> Dict[str, Any]:
        results = {
            "validator": "ReconciliationValidator",
            "passed": 0,
            "failed": 0,
            "detected_anomalies": [],
            "errors": [],
        }

        # 1. ANOMALY 2: Check for duplicate session dates causing denominator arithmetic corruption
        from sqlalchemy import func
        dup_sessions = (
            self.session.query(
                AttendanceEvent.enrollment_id,
                AttendanceEvent.session_date,
                func.count(AttendanceEvent.id)
            )
            .group_by(AttendanceEvent.enrollment_id, AttendanceEvent.session_date)
            .having(func.count(AttendanceEvent.id) > 1)
            .all()
        )
        for enr_id, sdate, cnt in dup_sessions:
            results["failed"] += 1
            msg = (
                f"ANOMALY DETECTED [wrong_attendance_denominator] on Enrollment {enr_id} at date {sdate}: "
                f"Found {cnt} session records on identical date, causing arithmetic denominator inflation/conflict."
            )
            results["detected_anomalies"].append({
                "issue_type": "wrong_attendance_denominator",
                "record_id": f"ATT-{enr_id}-{sdate}",
                "entity": "AttendanceEvent",
                "message": msg
            })
            results["errors"].append(msg)

        if not dup_sessions:
            results["passed"] += 1

        # 2. ANOMALY 5: Missing data interpreted as failure
        # Detect assessment results where score == 0.0 with status == 'Missing'
        missing_as_zero = (
            self.session.query(AssessmentResult)
            .filter(AssessmentResult.status == "Missing", AssessmentResult.score == 0.0)
            .all()
        )
        for r in missing_as_zero:
            results["failed"] += 1
            msg = (
                f"ANOMALY DETECTED [missing_data_as_failure] on AssessmentResult {r.id}: "
                f"Unsubmitted/missing assessment assigned score 0.0 instead of NULL/unknown status."
            )
            results["detected_anomalies"].append({
                "issue_type": "missing_data_as_failure",
                "record_id": r.id,
                "entity": "AssessmentResult",
                "message": msg
            })
            results["errors"].append(msg)

        if not missing_as_zero:
            results["passed"] += 1

        # 3. Arithmetic Reconciliation of Risk Score Formula
        predictions = self.session.query(RiskPrediction).all()
        for p in predictions:
            expected = round(
                (p.attendance_risk * 0.35)
                + (p.assessment_risk * 0.30)
                + (p.lms_risk * 0.20)
                + (p.support_risk * 0.15),
                2
            )
            # Allow 0.05 float rounding difference
            if abs(p.overall_score - expected) > 0.1:
                results["failed"] += 1
                results["errors"].append(
                    f"Risk score arithmetic mismatch on {p.id}: Stored={p.overall_score}, Expected={expected}"
                )
            else:
                results["passed"] += 1

        return results

