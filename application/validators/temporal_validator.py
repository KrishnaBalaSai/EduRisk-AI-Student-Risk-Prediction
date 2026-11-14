"""
Temporal Validator
Detects temporal data leakage and chronological inconsistencies.
Specifically detects ANOMALY 1: Risk score uses future grades / future observation window.
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from data.models.risk_prediction import RiskPrediction
from data.models.attendance import AttendanceEvent
from data.models.assessment import Assessment
from data.models.assessment_result import AssessmentResult
from data.models.intervention import Intervention


class TemporalValidator:
    def __init__(self, session: Session):
        self.session = session

    def validate_all(self) -> Dict[str, Any]:
        results = {
            "validator": "TemporalValidator",
            "passed": 0,
            "failed": 0,
            "detected_anomalies": [],
            "errors": [],
        }

        # 1. Check for Temporal Data Leakage in Risk Predictions (ANOMALY 1)
        # Prediction timestamp must NOT precede observation window cutoff!
        predictions = self.session.query(RiskPrediction).all()
        for p in predictions:
            pred_dt = p.prediction_timestamp
            window_end = p.observation_window_end
            if pred_dt.date() < window_end:
                results["failed"] += 1
                msg = (
                    f"ANOMALY DETECTED [future_data_leakage] on {p.id}: "
                    f"Prediction timestamp ({pred_dt.date()}) is earlier than observation window end ({window_end}). "
                    f"Future information leakage detected."
                )
                results["detected_anomalies"].append({
                    "issue_type": "future_data_leakage",
                    "record_id": p.id,
                    "entity": "RiskPrediction",
                    "message": msg
                })
                results["errors"].append(msg)
            else:
                results["passed"] += 1

        # 2. Check Assessment Result Submission Dates
        # Submission date should be on or before assessment due date + reasonable grace period (e.g. 14 days)
        asm_map = {a.id: a for a in self.session.query(Assessment).all()}
        results_records = self.session.query(AssessmentResult).filter(AssessmentResult.submission_date != None).all()
        for r in results_records:
            asm = asm_map.get(r.assessment_id)
            if asm and r.submission_date:
                # If submission is absurdly in future
                if (r.submission_date - asm.due_date).days > 60:
                    results["failed"] += 1
                    results["errors"].append(f"Result {r.id} submitted {r.submission_date} is 60+ days past due date {asm.due_date}.")
                else:
                    results["passed"] += 1

        return results

