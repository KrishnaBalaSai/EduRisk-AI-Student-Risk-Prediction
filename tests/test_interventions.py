"""
Test Suite: Interventions and Chronological Ordering
Verifies scheduling rules, status lifecycles, and chronological constraints.
"""

from datetime import date, datetime, timedelta
import pytest
from application.services.intervention_service import InterventionService
from application.validators.lifecycle_validator import LifecycleValidator


def test_intervention_scheduling_chronology(db_session):
    """Verify that scheduling succeeds when trigger precedes scheduled date."""
    service = InterventionService()
    now = datetime(2026, 10, 10, 9, 0, 0)
    sched_date = date(2026, 10, 15)

    intervention = service.schedule_intervention(
        student_id="STU-2026-000001",
        intervention_type="Academic Counselling",
        assigned_staff="Dr. Eleanor Vance (Lead Academic Advisor)",
        scheduled_date=sched_date,
        trigger_dt=now,
        notes="Test chronology valid"
    )

    assert intervention.scheduled_date >= intervention.trigger_timestamp.date()
    assert intervention.status == "Scheduled"


def test_intervention_precedes_trigger_violation(db_session):
    """Verify that attempting to schedule an intervention prior to trigger raises ValueError."""
    service = InterventionService()
    trigger_time = datetime(2026, 10, 20, 10, 0, 0)
    invalid_sched_date = date(2026, 10, 10)  # Before trigger!

    with pytest.raises(ValueError, match="Chronological violation"):
        service.schedule_intervention(
            student_id="STU-2026-000001",
            intervention_type="Study Plan",
            assigned_staff="David Chen (Academic Counselor)",
            scheduled_date=invalid_sched_date,
            trigger_dt=trigger_time
        )


def test_lifecycle_validator_detects_chronology_anomaly(db_session):
    """Verify LifecycleValidator detects the injected INT-ANOMALY-0001 fixture."""
    validator = LifecycleValidator(db_session)
    results = validator.validate_all()
    anomalies = [a for a in results["detected_anomalies"] if a["issue_type"] == "intervention_precedes_trigger"]
    assert len(anomalies) >= 1
    assert any("INT-ANOMALY-0001" in a["record_id"] for a in anomalies)

