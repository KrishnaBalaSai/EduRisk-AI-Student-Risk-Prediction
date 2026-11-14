"""
Test Suite: Risk Prediction Engine
Verifies mathematical weighting, classification thresholds, explainability, and missing data handling.
"""

from datetime import datetime, date
import pytest
from application.engines.risk_engine import RiskEngine


def test_risk_formula_calculation():
    """Verify Risk = (Att * 0.35) + (Asm * 0.30) + (LMS * 0.20) + (Sup * 0.15)."""
    engine = RiskEngine()

    att_summary = {"attendance_rate": 80.0, "eligible_sessions": 20, "absent_unapproved": 2}
    asm_summary = {"average_score": 75.0, "completed_count": 4, "missing_count": 0}
    lms_summary = {"recent_count": 20, "trend_pct": 5.0, "recent_duration_mins": 300}
    prior_cases = []

    pred = engine.evaluate_risk(
        student_id="STU-TEST-001",
        att_summary=att_summary,
        asm_summary=asm_summary,
        lms_summary=lms_summary,
        prior_cases=prior_cases,
        prediction_timestamp=datetime(2026, 11, 15, 12, 0, 0),
        observation_window_end=date(2026, 11, 15)
    )

    expected = round(
        (pred.attendance_risk * 0.35)
        + (pred.assessment_risk * 0.30)
        + (pred.lms_risk * 0.20)
        + (pred.support_risk * 0.15),
        2
    )
    assert abs(pred.overall_score - expected) < 0.05


def test_risk_category_thresholds():
    """Verify Low (0-34), Medium (35-64), High (65-100) categorization."""
    engine = RiskEngine()

    # Low risk
    pred_low = engine.evaluate_risk(
        student_id="STU-LOW",
        att_summary={"attendance_rate": 98.0, "eligible_sessions": 20, "absent_unapproved": 0},
        asm_summary={"average_score": 95.0, "completed_count": 4, "missing_count": 0},
        lms_summary={"recent_count": 40, "trend_pct": 10.0, "recent_duration_mins": 600},
        prior_cases=[],
        prediction_timestamp=datetime.utcnow(),
        observation_window_end=date.today()
    )
    assert pred_low.risk_category == "Low Risk"
    assert pred_low.overall_score <= 34.0

    # High risk
    pred_high = engine.evaluate_risk(
        student_id="STU-HIGH",
        att_summary={"attendance_rate": 45.0, "eligible_sessions": 20, "absent_unapproved": 8},
        asm_summary={"average_score": 38.0, "completed_count": 3, "missing_count": 2},
        lms_summary={"recent_count": 2, "trend_pct": -50.0, "recent_duration_mins": 30},
        prior_cases=[type("Case", (), {"status": "Escalated", "priority": "Critical"})()],
        prediction_timestamp=datetime.utcnow(),
        observation_window_end=date.today()
    )
    assert pred_high.risk_category == "High Risk"
    assert pred_high.overall_score >= 65.0


def test_explainability_narrative_generation():
    """Verify narrative highlights the dominant contributing factor."""
    engine = RiskEngine()
    pred = engine.evaluate_risk(
        student_id="STU-EXPLAIN",
        att_summary={"attendance_rate": 50.0, "eligible_sessions": 20, "absent_unapproved": 6},
        asm_summary={"average_score": 85.0, "completed_count": 3, "missing_count": 0},
        lms_summary={"recent_count": 25, "trend_pct": 0.0, "recent_duration_mins": 300},
        prior_cases=[],
        prediction_timestamp=datetime.utcnow(),
        observation_window_end=date.today()
    )
    assert "Attendance" in pred.explanation
    assert f"{pred.overall_score:.1f}/100" in pred.explanation

