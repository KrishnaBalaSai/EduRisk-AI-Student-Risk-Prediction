"""
Test Suite: Edge Cases and Negative Scenarios
Verifies missing data treatment, withdrawn student lifecycle, and denominator anomalies.
"""

import pytest
from application.engines.risk_engine import RiskEngine
from application.validators.lifecycle_validator import LifecycleValidator
from application.validators.reconciliation_validator import ReconciliationValidator


def test_missing_data_not_treated_as_zero_failure():
    """Verify missing assessments receive neutral baseline rather than failing 0% grade."""
    engine = RiskEngine()
    asm_summary_empty = {
        "average_score": None,
        "completed_count": 0,
        "missing_count": 1
    }
    risk_score, rationale = engine.calculate_assessment_risk(asm_summary_empty)
    # Neutral baseline must be moderate (e.g. 35.0), NOT 100.0 (catastrophic failure)
    assert 25.0 <= risk_score <= 45.0
    assert "No completed assessments available" in rationale


def test_lifecycle_validator_detects_withdrawn_student_active(db_session):
    """Verify LifecycleValidator detects withdrawn student with active enrollment (ANOMALY 3)."""
    validator = LifecycleValidator(db_session)
    results = validator.validate_all()
    anomalies = [a for a in results["detected_anomalies"] if a["issue_type"] == "withdrawn_student_active"]
    assert len(anomalies) >= 1


def test_reconciliation_validator_detects_bad_denominator(db_session):
    """Verify ReconciliationValidator detects duplicate session dates (ANOMALY 2)."""
    validator = ReconciliationValidator(db_session)
    results = validator.validate_all()
    anomalies = [a for a in results["detected_anomalies"] if a["issue_type"] == "wrong_attendance_denominator"]
    assert len(anomalies) >= 1


def test_reconciliation_validator_detects_missing_as_zero(db_session):
    """Verify ReconciliationValidator detects missing data assigned score 0.0 (ANOMALY 5)."""
    validator = ReconciliationValidator(db_session)
    results = validator.validate_all()
    anomalies = [a for a in results["detected_anomalies"] if a["issue_type"] == "missing_data_as_failure"]
    assert len(anomalies) >= 1

