"""
Anomaly Fixture Generator
Injects labelled negative scenarios strictly AFTER valid baseline data is generated.
Preserves baseline records and provides ground-truth fixtures for validation verification.
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Tuple
from data.models.student import Student
from data.models.course import Course
from data.models.enrollment import Enrollment
from data.models.attendance import AttendanceEvent
from data.models.assessment import Assessment
from data.models.assessment_result import AssessmentResult
from data.models.intervention import Intervention
from data.models.risk_prediction import RiskPrediction
from data.models.anomaly_fixture import AnomalyFixture


def inject_anomalies(
    students: List[Student],
    courses: List[Course],
    enrollments: List[Enrollment],
    attendance_events: List[AttendanceEvent],
    assessments: List[Assessment],
    assessment_results: List[AssessmentResult],
    interventions: List[Intervention],
) -> Tuple[List[AnomalyFixture], Dict[str, Any]]:
    """
    Inject exactly the 5 required negative scenarios with clear ground-truth labels.
    Returns:
    - List of AnomalyFixture records for verification
    - Injected entity records to be inserted into the database
    """
    fixtures: List[AnomalyFixture] = []
    injected_entities: Dict[str, List[Any]] = {
        "risk_predictions": [],
        "attendance_events": [],
        "enrollments": [],
        "interventions": [],
        "assessment_results": [],
    }

    # 1. ANOMALY 1: Risk score uses future grades (Temporal data leakage)
    # Prediction timestamp is 2026-10-15, but uses assessment due on 2026-12-15
    target_student = students[0]
    leak_pred_id = "RSK-ANOMALY-0001"
    leak_prediction = RiskPrediction(
        id=leak_pred_id,
        student_id=target_student.id,
        prediction_timestamp=datetime(2026, 10, 15, 10, 0, 0),
        observation_window_end=date(2026, 12, 20),  # Leakage! Window is in future of prediction timestamp
        attendance_risk=30.0,
        assessment_risk=85.0,
        lms_risk=20.0,
        support_risk=15.0,
        overall_score=43.75,
        risk_category="Medium Risk",
        explanation="Calculated using final exam grades dated 2026-12-15 prior to assessment completion.",
        model_version="v-leak-test"
    )
    injected_entities["risk_predictions"].append(leak_prediction)
    fixtures.append(
        AnomalyFixture(
            id="ANM-000001",
            issue_type="future_data_leakage",
            entity_type="RiskPrediction",
            record_id=leak_pred_id,
            ground_truth_label="ANOMALY_TEMPORAL_LEAKAGE",
            description="Prediction timestamp (2026-10-15) precedes observation window cutoff (2026-12-20) or uses future assessment records.",
            detected=False
        )
    )

    # 2. ANOMALY 2: Attendance percentage uses wrong denominator
    # Creates an invalid attendance event with duplicate/impossible date or an arithmetic mismatch
    target_enr = enrollments[0]
    bad_att_id = f"ATT-ANOMALY-{target_enr.id}-BAD-DENOM"
    bad_att_event = AttendanceEvent(
        id=bad_att_id,
        enrollment_id=target_enr.id,
        student_id=target_enr.student_id,
        course_id=target_enr.course_id,
        session_date=date(2026, 9, 7),  # Duplicate date for same enrollment (causing denominator count conflict)
        status="Absent_Unapproved",
        session_type="Lecture",
        notes="ANOMALY_FIXTURE: Duplicate session date injected to induce denominator distortion"
    )
    injected_entities["attendance_events"].append(bad_att_event)
    fixtures.append(
        AnomalyFixture(
            id="ANM-000002",
            issue_type="wrong_attendance_denominator",
            entity_type="AttendanceEvent",
            record_id=bad_att_id,
            ground_truth_label="ANOMALY_ATTENDANCE_DENOMINATOR",
            description="Duplicate session date for same enrollment creates discrepancy between total scheduled sessions and eligible attendance denominator.",
            detected=False
        )
    )

    # 3. ANOMALY 3: Withdrawn student remains active
    # Student marked Withdrawn on 2026-10-01 has an active Enrollment marked 'Enrolled' in 2027
    withdrawn_student = next((s for s in students if s.status == "Withdrawn"), students[-1])
    # Ensure withdrawal date is set
    if not withdrawn_student.withdrawal_date:
        withdrawn_student.status = "Withdrawn"
        withdrawn_student.withdrawal_date = date(2026, 10, 1)

    active_course = courses[-1]
    bad_enr_id = f"ENR-ANOMALY-{withdrawn_student.id}-{active_course.id}"
    bad_enrollment = Enrollment(
        id=bad_enr_id,
        student_id=withdrawn_student.id,
        course_id=active_course.id,
        status="Enrolled",  # Lifecycle anomaly: Withdrawn student remains actively enrolled!
        enrollment_date=date(2027, 1, 15),
        completion_date=None,
        final_grade=None
    )
    injected_entities["enrollments"].append(bad_enrollment)
    fixtures.append(
        AnomalyFixture(
            id="ANM-000003",
            issue_type="withdrawn_student_active",
            entity_type="Enrollment",
            record_id=bad_enr_id,
            ground_truth_label="ANOMALY_WITHDRAWN_STUDENT_ACTIVE",
            description=f"Student {withdrawn_student.id} withdrew on {withdrawn_student.withdrawal_date} but holds active enrollment {bad_enr_id} with status 'Enrolled'.",
            detected=False
        )
    )

    # 4. ANOMALY 4: Intervention precedes its trigger
    # Intervention scheduled on 2026-09-10, but trigger timestamp is 2026-10-25
    bad_int_id = "INT-ANOMALY-0001"
    bad_intervention = Intervention(
        id=bad_int_id,
        student_id=target_student.id,
        case_id=None,
        intervention_type="Academic Counselling",
        assigned_staff="Dr. Eleanor Vance (Lead Academic Advisor)",
        trigger_timestamp=datetime(2026, 10, 25, 14, 0, 0),
        scheduled_date=date(2026, 9, 10),  # Chronological violation: scheduled BEFORE trigger!
        completion_date=date(2026, 9, 11),
        status="Completed",
        notes="ANOMALY_FIXTURE: Intervention scheduled prior to trigger timestamp.",
        outcome_notes="Premature session logged before trigger condition occurred."
    )
    injected_entities["interventions"].append(bad_intervention)
    fixtures.append(
        AnomalyFixture(
            id="ANM-000004",
            issue_type="intervention_precedes_trigger",
            entity_type="Intervention",
            record_id=bad_int_id,
            ground_truth_label="ANOMALY_CHRONOLOGY_VIOLATION",
            description="Intervention scheduled_date (2026-09-10) is prior to trigger_timestamp (2026-10-25).",
            detected=False
        )
    )

    # 5. ANOMALY 5: Missing data interpreted as failure
    # Assessment result where score is 0.0 with status 'Missing' or excused, treated as raw zero
    bad_asr_id = f"ASR-ANOMALY-{target_student.id}-ZERO-MISS"
    sample_asm = assessments[0]
    bad_result = AssessmentResult(
        id=bad_asr_id,
        assessment_id=sample_asm.id,
        student_id=target_student.id,
        enrollment_id=enrollments[0].id,
        score=0.0,  # Missing data recorded as zero failure!
        submission_date=None,
        status="Missing",
    )
    injected_entities["assessment_results"].append(bad_result)
    fixtures.append(
        AnomalyFixture(
            id="ANM-000005",
            issue_type="missing_data_as_failure",
            entity_type="AssessmentResult",
            record_id=bad_asr_id,
            ground_truth_label="ANOMALY_MISSING_DATA_AS_ZERO",
            description="Missing assessment submission has score explicitly hardcoded to 0.0 instead of NULL/excused representation.",
            detected=False
        )
    )

    return fixtures, injected_entities

