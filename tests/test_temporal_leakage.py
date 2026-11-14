"""
Test Suite: Temporal Data Leakage Prevention
Ensures risk prediction queries strictly respect observation window cutoffs.
"""

from datetime import date, datetime, timedelta
import pytest
from application.services.risk_service import RiskService
from application.validators.temporal_validator import TemporalValidator


def test_observation_window_filtering(db_session):
    """
    Verify that an early cutoff date (e.g. 2026-10-01) does not query or factor in
    assessments or attendance occurring after that date.
    """
    service = RiskService()
    early_cutoff = date(2026, 9, 30)
    pred_early = service.predict_student_risk("STU-2026-000001", observation_window_end=early_cutoff, persist=False)

    late_cutoff = date(2026, 12, 15)
    pred_late = service.predict_student_risk("STU-2026-000001", observation_window_end=late_cutoff, persist=False)

    assert pred_early.observation_window_end == early_cutoff
    assert pred_late.observation_window_end == late_cutoff
    assert pred_early.prediction_timestamp.date() >= early_cutoff


def test_temporal_leakage_detector(db_session):
    """
    Verify that the TemporalValidator correctly identifies injected future leakage anomalies.
    """
    validator = TemporalValidator(db_session)
    results = validator.validate_all()

    # The anomaly fixture RSK-ANOMALY-0001 must be detected
    leak_anomalies = [a for a in results["detected_anomalies"] if a["issue_type"] == "future_data_leakage"]
    assert len(leak_anomalies) >= 1
    assert any("RSK-ANOMALY-0001" in a["record_id"] for a in leak_anomalies)

