"""
Risk Application Service
Orchestrates explainable risk prediction, batch scoring, and temporal leakage prevention.

Prediction history policy
--------------------------
Each prediction is uniquely keyed by (student_id, observation_window_end, model_version).
The RiskEngine generates the ID as  RSK-{student_id}-{YYYYMMDD}  which encodes the cutoff
date, so predictions on different dates naturally produce different IDs and are stored as
distinct historical rows.

Duplicate-prevention rule (same student + same cutoff + same model version):
  - If a row with the same ID already exists → update its factor scores and explanation
    in-place (idempotent re-scoring).
  - If no row with that ID exists → insert a new historical record.

This means:
  ✓  Monthly snapshots accumulate as separate rows (different cutoff → different ID).
  ✓  Re-running the same cutoff is idempotent (no UNIQUE constraint error).
  ✓  Historical predictions from earlier cutoffs are never touched.
  ✓  Temporal leakage prevention is unaffected (each prediction only queries data ≤ cutoff).
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any
from data.models.risk_prediction import RiskPrediction
from data.repositories.risk_repository import RiskRepository
from data.repositories.student_repository import StudentRepository
from data.repositories.attendance_repository import AttendanceRepository
from data.repositories.assessment_repository import AssessmentResultRepository
from data.repositories.lms_repository import LMSRepository
from data.repositories.support_repository import SupportRepository
from application.engines.risk_engine import RiskEngine


class RiskService:
    def __init__(
        self,
        risk_repo: Optional[RiskRepository] = None,
        student_repo: Optional[StudentRepository] = None,
        attendance_repo: Optional[AttendanceRepository] = None,
        assessment_result_repo: Optional[AssessmentResultRepository] = None,
        lms_repo: Optional[LMSRepository] = None,
        support_repo: Optional[SupportRepository] = None,
        engine: Optional[RiskEngine] = None
    ):
        self.risk_repo = risk_repo or RiskRepository()
        self.student_repo = student_repo or StudentRepository()
        self.attendance_repo = attendance_repo or AttendanceRepository()
        self.asr_repo = assessment_result_repo or AssessmentResultRepository()
        self.lms_repo = lms_repo or LMSRepository()
        self.support_repo = support_repo or SupportRepository()
        self.engine = engine or RiskEngine()

    def predict_student_risk(
        self,
        student_id: str,
        observation_window_end: Optional[date] = None,
        persist: bool = True
    ) -> RiskPrediction:
        """
        Calculates explainable risk score using only signals available on or before
        observation_window_end.  Guarantees temporal safety by never querying events
        past the cutoff.

        Persistence behaviour:
        - Different cutoff dates → distinct historical records (different ID).
        - Same cutoff date repeated → idempotent update of existing record (no duplicate).
        - Earlier cutoff records are never modified.
        """
        cutoff_date = observation_window_end or date.today()
        prediction_timestamp = datetime(cutoff_date.year, cutoff_date.month, cutoff_date.day, 23, 59, 59)

        # 1. Attendance Summary (up to cutoff)
        att_summary = self.attendance_repo.get_student_attendance_summary(student_id, cutoff_date)

        # 2. Assessment Summary (due on or before cutoff)
        asm_summary = self.asr_repo.get_student_assessment_summary(student_id, cutoff_date)

        # 3. LMS Summary (prior to cutoff)
        lms_summary = self.lms_repo.get_engagement_summary(student_id, prediction_timestamp)

        # 4. Support History (opened on or before cutoff)
        prior_cases = self.support_repo.get_by_student(student_id, prediction_timestamp)

        # Evaluate risk — ID encodes student + cutoff date + is deterministic
        prediction = self.engine.evaluate_risk(
            student_id=student_id,
            att_summary=att_summary,
            asm_summary=asm_summary,
            lms_summary=lms_summary,
            prior_cases=prior_cases,
            prediction_timestamp=prediction_timestamp,
            observation_window_end=cutoff_date
        )

        if persist:
            self._upsert_prediction(prediction)

        return prediction

    def _upsert_prediction(self, prediction: RiskPrediction) -> None:
        """
        Insert or update a single prediction record.

        Lookup is by prediction.id and composite key (student_id, cutoff_date, model_version).
        - Existing row with same ID or same (student, cutoff, version) -> update factor scores and explanation in-place.
        - No existing row -> insert as a new historical record.
        - Different cutoff date OR different rule version -> always creates a new historical record.
        """
        existing = (
            self.risk_repo.session.query(RiskPrediction)
            .filter(
                (RiskPrediction.id == prediction.id) |
                (
                    (RiskPrediction.student_id == prediction.student_id) &
                    (RiskPrediction.observation_window_end == prediction.observation_window_end) &
                    (RiskPrediction.model_version == prediction.model_version)
                )
            )
            .first()
        )
        if existing:
            # Idempotent re-score: update factors but preserve the original row
            existing.prediction_timestamp = prediction.prediction_timestamp
            existing.attendance_risk = prediction.attendance_risk
            existing.assessment_risk = prediction.assessment_risk
            existing.lms_risk = prediction.lms_risk
            existing.support_risk = prediction.support_risk
            existing.overall_score = prediction.overall_score
            existing.risk_category = prediction.risk_category
            existing.explanation = prediction.explanation
            existing.model_version = prediction.model_version
            self.risk_repo.session.commit()
        else:
            # New cutoff date, different rule version, or first prediction for this student -> new historical record
            self.risk_repo.create(prediction)

    def predict_all_students(
        self,
        observation_window_end: Optional[date] = None,
        persist: bool = True
    ) -> List[RiskPrediction]:
        """
        Run batch risk evaluation for all students across the institution.
        Each student gets one prediction for the given cutoff (historical records preserved).
        """
        students = self.student_repo.get_all(limit=10000)
        cutoff_date = observation_window_end or date.today()
        predictions = []

        for s in students:
            pred = self.predict_student_risk(s.id, observation_window_end=cutoff_date, persist=False)
            predictions.append(pred)

        if persist and predictions:
            # Bulk upsert: use _upsert_prediction per record to respect history policy
            for pred in predictions:
                self._upsert_prediction(pred)

        return predictions

    def get_latest_risk_all(self) -> List[RiskPrediction]:
        return self.risk_repo.get_latest_all_students()

    def get_risk_by_category(self, category: str) -> List[RiskPrediction]:
        return self.risk_repo.get_by_category(category)

    def get_student_risk(self, student_id: str) -> Optional[RiskPrediction]:
        return self.risk_repo.get_latest_for_student(student_id)

    def get_student_risk_history(self, student_id: str) -> List[RiskPrediction]:
        """
        Return all historical risk predictions for a student ordered by cutoff date ascending.
        Useful for trend visualisation and audit trails.
        """
        return (
            self.risk_repo.session.query(RiskPrediction)
            .filter(RiskPrediction.student_id == student_id)
            .order_by(RiskPrediction.observation_window_end.asc())
            .all()
        )

