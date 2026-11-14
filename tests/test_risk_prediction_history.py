"""
Test Suite: Risk Prediction History Preservation
Verifies that predict_student_risk correctly manages historical records:

  A. Same student + same cutoff + same model version  → no duplicate rows, idempotent update.
  B. Same student + different cutoff dates            → separate historical records, earlier
     records are never overwritten.
  C. Factor scores and explanations remain traceable across all stored predictions.
  D. Temporal leakage prevention is unaffected by upsert behaviour.
  E. get_student_risk_history() returns the full ordered history.
"""

from datetime import date, datetime
import pytest
from application.services.risk_service import RiskService
from application.engines.risk_engine import RiskEngine
from data.models.risk_prediction import RiskPrediction


# ---------------------------------------------------------------------------
# Helper: build a RiskService wired to the shared db_session fixture
# ---------------------------------------------------------------------------

def _service(db_session) -> RiskService:
    """Return a RiskService that reuses the test session so all queries see
    the same in-process transaction."""
    from data.repositories.risk_repository import RiskRepository
    from data.repositories.student_repository import StudentRepository
    from data.repositories.attendance_repository import AttendanceRepository
    from data.repositories.assessment_repository import AssessmentResultRepository
    from data.repositories.lms_repository import LMSRepository
    from data.repositories.support_repository import SupportRepository

    return RiskService(
        risk_repo=RiskRepository(session=db_session),
        student_repo=StudentRepository(session=db_session),
        attendance_repo=AttendanceRepository(session=db_session),
        assessment_result_repo=AssessmentResultRepository(session=db_session),
        lms_repo=LMSRepository(session=db_session),
        support_repo=SupportRepository(session=db_session),
    )


def _count_predictions(db_session, student_id: str) -> int:
    return (
        db_session.query(RiskPrediction)
        .filter(RiskPrediction.student_id == student_id)
        .count()
    )


# ---------------------------------------------------------------------------
# A. Same student + same cutoff + same version → idempotent, no duplicate
# ---------------------------------------------------------------------------

class TestNoDuplicateOnRepeat:

    def test_repeated_same_cutoff_does_not_create_duplicate(self, db_session):
        """
        Calling predict_student_risk twice with the same cutoff for the same
        student must result in exactly one DB row (second call is an update).
        """
        sid = "STU-2026-000002"
        cutoff = date(2026, 9, 15)
        svc = _service(db_session)

        # Remove any pre-existing prediction for this student+cutoff
        pred_id = f"RSK-{sid}-{cutoff.strftime('%Y%m%d')}"
        existing = db_session.query(RiskPrediction).filter(RiskPrediction.id == pred_id).first()
        if existing:
            db_session.delete(existing)
            db_session.commit()

        # First prediction
        p1 = svc.predict_student_risk(sid, observation_window_end=cutoff, persist=True)
        count_after_first = _count_predictions(db_session, sid)

        # Second prediction — same parameters
        p2 = svc.predict_student_risk(sid, observation_window_end=cutoff, persist=True)
        count_after_second = _count_predictions(db_session, sid)

        assert count_after_second == count_after_first, (
            f"Second call with same cutoff created a duplicate row "
            f"(before={count_after_first}, after={count_after_second})"
        )
        assert p1.id == p2.id, "Same student + same cutoff must produce the same prediction ID"

    def test_repeated_call_does_not_raise_unique_constraint(self, db_session):
        """
        UNIQUE constraint (IntegrityError) must never surface when the same
        student + cutoff is requested more than once.
        """
        from sqlalchemy.exc import IntegrityError
        sid = "STU-2026-000003"
        cutoff = date(2026, 9, 20)
        svc = _service(db_session)

        try:
            svc.predict_student_risk(sid, observation_window_end=cutoff, persist=True)
            svc.predict_student_risk(sid, observation_window_end=cutoff, persist=True)
            svc.predict_student_risk(sid, observation_window_end=cutoff, persist=True)
        except IntegrityError as exc:
            pytest.fail(f"IntegrityError raised on repeated same-cutoff call: {exc}")


# ---------------------------------------------------------------------------
# B. Same student + different cutoffs → separate historical records
# ---------------------------------------------------------------------------

class TestSeparateHistoricalRecords:

    def test_different_cutoffs_create_separate_rows(self, db_session):
        """
        Predictions on two different cutoff dates for the same student must
        produce two distinct rows in risk_predictions.
        """
        sid = "STU-2026-000004"
        cutoff_early = date(2026, 9, 30)
        cutoff_late  = date(2026, 10, 31)
        svc = _service(db_session)

        id_early = f"RSK-{sid}-{cutoff_early.strftime('%Y%m%d')}"
        id_late  = f"RSK-{sid}-{cutoff_late.strftime('%Y%m%d')}"

        # Clean slate for this student's two target rows
        for rid in (id_early, id_late):
            row = db_session.query(RiskPrediction).filter(RiskPrediction.id == rid).first()
            if row:
                db_session.delete(row)
        db_session.commit()

        p_early = svc.predict_student_risk(sid, observation_window_end=cutoff_early, persist=True)
        p_late  = svc.predict_student_risk(sid, observation_window_end=cutoff_late,  persist=True)

        assert p_early.id != p_late.id, "Different cutoffs must produce different prediction IDs"
        assert p_early.observation_window_end == cutoff_early
        assert p_late.observation_window_end  == cutoff_late

        # Both rows must exist in the database
        row_early = db_session.query(RiskPrediction).filter(RiskPrediction.id == id_early).first()
        row_late  = db_session.query(RiskPrediction).filter(RiskPrediction.id == id_late).first()
        assert row_early is not None, "Early prediction row was not persisted"
        assert row_late  is not None, "Late prediction row was not persisted"

    def test_later_cutoff_does_not_overwrite_earlier_record(self, db_session):
        """
        After scoring a later cutoff, the earlier prediction's score, explanation
        and observation_window_end must remain unchanged in the database.
        """
        sid = "STU-2026-000005"
        cutoff_early = date(2026, 9, 30)
        cutoff_late  = date(2026, 11, 14)
        svc = _service(db_session)

        id_early = f"RSK-{sid}-{cutoff_early.strftime('%Y%m%d')}"
        id_late  = f"RSK-{sid}-{cutoff_late.strftime('%Y%m%d')}"

        for rid in (id_early, id_late):
            row = db_session.query(RiskPrediction).filter(RiskPrediction.id == rid).first()
            if row:
                db_session.delete(row)
        db_session.commit()

        p_early = svc.predict_student_risk(sid, observation_window_end=cutoff_early, persist=True)
        early_score       = p_early.overall_score
        early_explanation = p_early.explanation
        early_window_end  = p_early.observation_window_end

        # Score with a later cutoff
        svc.predict_student_risk(sid, observation_window_end=cutoff_late, persist=True)

        # Re-fetch early row from DB
        db_session.expire_all()
        row_early = db_session.query(RiskPrediction).filter(RiskPrediction.id == id_early).first()

        assert row_early is not None, "Early prediction was deleted after later cutoff was scored"
        assert row_early.overall_score == early_score, (
            f"Early prediction score changed after later cutoff: "
            f"{early_score} → {row_early.overall_score}"
        )
        assert row_early.observation_window_end == early_window_end, (
            "Early prediction observation_window_end was mutated"
        )
        assert row_early.explanation == early_explanation, (
            "Early prediction explanation was overwritten"
        )

    def test_history_ordered_by_cutoff(self, db_session):
        """
        get_student_risk_history() must return predictions sorted by
        observation_window_end ascending.
        """
        sid = "STU-2026-000006"
        cutoffs = [date(2026, 9, 30), date(2026, 10, 31), date(2026, 11, 14)]
        svc = _service(db_session)

        # Clean the three target rows
        for cutoff in cutoffs:
            rid = f"RSK-{sid}-{cutoff.strftime('%Y%m%d')}"
            row = db_session.query(RiskPrediction).filter(RiskPrediction.id == rid).first()
            if row:
                db_session.delete(row)
        db_session.commit()

        for cutoff in cutoffs:
            svc.predict_student_risk(sid, observation_window_end=cutoff, persist=True)

        history = svc.get_student_risk_history(sid)
        # Filter to only the rows we inserted in this test
        our_ids = {f"RSK-{sid}-{c.strftime('%Y%m%d')}" for c in cutoffs}
        our_rows = [r for r in history if r.id in our_ids]

        assert len(our_rows) == 3, f"Expected 3 historical rows, found {len(our_rows)}"
        dates = [r.observation_window_end for r in our_rows]
        assert dates == sorted(dates), f"History not ordered by cutoff date: {dates}"


# ---------------------------------------------------------------------------
# C. Factor scores and explanations are traceable in every persisted row
# ---------------------------------------------------------------------------

class TestFactorTraceability:

    def test_all_factor_scores_persisted(self, db_session):
        """
        Every stored prediction must carry non-null, in-range factor scores and
        a non-empty explanation string.
        """
        sid = "STU-2026-000007"
        cutoff = date(2026, 10, 15)
        svc = _service(db_session)

        rid = f"RSK-{sid}-{cutoff.strftime('%Y%m%d')}"
        row = db_session.query(RiskPrediction).filter(RiskPrediction.id == rid).first()
        if row:
            db_session.delete(row)
        db_session.commit()

        pred = svc.predict_student_risk(sid, observation_window_end=cutoff, persist=True)

        db_session.expire_all()
        stored = db_session.query(RiskPrediction).filter(RiskPrediction.id == rid).first()
        assert stored is not None

        for factor_name, value in [
            ("attendance_risk",  stored.attendance_risk),
            ("assessment_risk",  stored.assessment_risk),
            ("lms_risk",         stored.lms_risk),
            ("support_risk",     stored.support_risk),
            ("overall_score",    stored.overall_score),
        ]:
            assert value is not None,              f"{factor_name} is None in DB"
            assert 0.0 <= value <= 100.0,          f"{factor_name}={value} is out of [0, 100]"

        assert stored.explanation,                 "explanation is empty"
        assert stored.observation_window_end == cutoff, "observation_window_end mismatch"
        assert stored.student_id == sid,           "student_id mismatch"
        assert stored.risk_category in ("Low Risk", "Medium Risk", "High Risk"), \
            f"Unexpected risk_category: {stored.risk_category}"

    def test_explanation_references_primary_factor(self, db_session):
        """
        The stored explanation must mention at least one factor name, confirming the
        narrative is generated and not a placeholder.
        """
        sid = "STU-2026-000008"
        cutoff = date(2026, 10, 20)
        svc = _service(db_session)

        rid = f"RSK-{sid}-{cutoff.strftime('%Y%m%d')}"
        row = db_session.query(RiskPrediction).filter(RiskPrediction.id == rid).first()
        if row:
            db_session.delete(row)
        db_session.commit()

        pred = svc.predict_student_risk(sid, observation_window_end=cutoff, persist=True)

        factor_names = ["Attendance", "Academic Performance", "LMS Engagement", "Support History"]
        assert any(fn in pred.explanation for fn in factor_names), (
            f"Explanation does not mention any factor: {pred.explanation[:200]}"
        )
        assert f"{pred.overall_score:.1f}/100" in pred.explanation, \
            "Explanation does not contain the formatted overall score"

    def test_model_version_is_persisted(self, db_session):
        """
        model_version must be stored and must match the engine's declared version.
        """
        sid = "STU-2026-000009"
        cutoff = date(2026, 10, 25)
        svc = _service(db_session)

        rid = f"RSK-{sid}-{cutoff.strftime('%Y%m%d')}"
        row = db_session.query(RiskPrediction).filter(RiskPrediction.id == rid).first()
        if row:
            db_session.delete(row)
        db_session.commit()

        pred = svc.predict_student_risk(sid, observation_window_end=cutoff, persist=True)

        db_session.expire_all()
        stored = db_session.query(RiskPrediction).filter(RiskPrediction.id == rid).first()
        assert stored.model_version == svc.engine.version, (
            f"Stored model_version '{stored.model_version}' does not match "
            f"engine version '{svc.engine.version}'"
        )


# ---------------------------------------------------------------------------
# D. Temporal leakage prevention unaffected by upsert behaviour
# ---------------------------------------------------------------------------

class TestTemporalLeakageUnaffected:

    def test_upsert_does_not_affect_temporal_cutoff(self, db_session):
        """
        When the same student is scored at an early cutoff and then again at a
        late cutoff, the EARLY prediction must not change — proving that the
        upsert never touches rows from earlier observation windows.
        Specifically validates that future data cannot back-propagate into
        historical predictions through an incorrect upsert path.
        """
        sid = "STU-2026-000010"
        early = date(2026, 9, 1)
        late  = date(2026, 11, 14)
        svc   = _service(db_session)

        for cutoff in (early, late):
            rid = f"RSK-{sid}-{cutoff.strftime('%Y%m%d')}"
            row = db_session.query(RiskPrediction).filter(RiskPrediction.id == rid).first()
            if row:
                db_session.delete(row)
        db_session.commit()

        p_early = svc.predict_student_risk(sid, observation_window_end=early, persist=True)
        early_score = p_early.overall_score
        early_att   = p_early.attendance_risk
        early_asm   = p_early.assessment_risk

        # Score with a later window (may see more data → different score)
        svc.predict_student_risk(sid, observation_window_end=late, persist=True)

        # Re-score early window a second time (idempotent update path)
        p_early_rescore = svc.predict_student_risk(sid, observation_window_end=early, persist=True)

        assert p_early_rescore.overall_score == early_score, (
            "Re-scoring early cutoff after a late cutoff produced a different score — "
            "temporal leakage through upsert suspected."
        )
        assert p_early_rescore.attendance_risk == early_att
        assert p_early_rescore.assessment_risk == early_asm


# ---------------------------------------------------------------------------
# E. Engine-level: prediction ID encodes student + cutoff date
# ---------------------------------------------------------------------------

class TestPredictionIdContract:

    def test_prediction_id_encodes_student_and_cutoff(self):
        """
        RiskEngine.evaluate_risk() must produce an ID of the form
        RSK-{student_id}-{YYYYMMDD}, encoding both the student and the cutoff.
        This is what makes different cutoff dates produce different IDs without
        any additional logic.
        """
        engine = RiskEngine()
        sid    = "STU-2026-000001"
        cutoff = date(2026, 9, 30)
        pred   = engine.evaluate_risk(
            student_id=sid,
            att_summary={"attendance_rate": 85.0, "eligible_sessions": 10, "absent_unapproved": 1},
            asm_summary={"average_score": 78.0, "completed_count": 3, "missing_count": 0},
            lms_summary={"recent_count": 20, "trend_pct": 0.0, "recent_duration_mins": 200},
            prior_cases=[],
            prediction_timestamp=datetime(2026, 9, 30, 23, 59, 59),
            observation_window_end=cutoff,
        )
        expected_id = f"RSK-{sid}-{cutoff.strftime('%Y%m%d')}"
        assert pred.id == expected_id, f"Expected ID '{expected_id}', got '{pred.id}'"

    def test_different_cutoffs_produce_different_ids(self):
        """
        Two evaluate_risk() calls with different cutoff dates for the same
        student must produce distinct IDs.
        """
        engine  = RiskEngine()
        sid     = "STU-2026-000001"
        summary = dict(
            att_summary={"attendance_rate": 85.0, "eligible_sessions": 10, "absent_unapproved": 0},
            asm_summary={"average_score": 78.0, "completed_count": 3, "missing_count": 0},
            lms_summary={"recent_count": 20, "trend_pct": 0.0, "recent_duration_mins": 200},
            prior_cases=[],
        )
        cutoff_a = date(2026, 9, 30)
        cutoff_b = date(2026, 10, 31)

        pred_a = engine.evaluate_risk(
            student_id=sid,
            prediction_timestamp=datetime(2026, 9, 30, 23, 59, 59),
            observation_window_end=cutoff_a,
            **summary,
        )
        pred_b = engine.evaluate_risk(
            student_id=sid,
            prediction_timestamp=datetime(2026, 10, 31, 23, 59, 59),
            observation_window_end=cutoff_b,
            **summary,
        )
        assert pred_a.id != pred_b.id, (
            "Different cutoff dates must produce different prediction IDs"
        )
        assert cutoff_a.strftime("%Y%m%d") in pred_a.id
        assert cutoff_b.strftime("%Y%m%d") in pred_b.id


# ---------------------------------------------------------------------------
# F. Rule versioning: different rule versions preserve separate records
# ---------------------------------------------------------------------------

class TestDifferentRuleVersionsPreserved:

    def test_different_versions_for_same_student_and_cutoff_create_separate_records(self, db_session):
        """
        When predictions are run for the same student on the same cutoff date
        using different engine rule versions (e.g. v1.2.0-explainable and v2.0.0-ml),
        both versioned records must be preserved in the database.
        The second version must NOT overwrite the first version.
        """
        sid = "STU-2026-000015"
        cutoff = date(2026, 10, 15)

        # Clean slate for this student
        existing_rows = db_session.query(RiskPrediction).filter(RiskPrediction.student_id == sid).all()
        for r in existing_rows:
            db_session.delete(r)
        db_session.commit()

        # Engine 1: Default v1.2.0-explainable
        svc_v1 = _service(db_session)
        pred_v1 = svc_v1.predict_student_risk(sid, observation_window_end=cutoff, persist=True)

        # Engine 2: New version v2.0.0-ml
        engine_v2 = RiskEngine(version="v2.0.0-ml")
        svc_v2 = _service(db_session)
        svc_v2.engine = engine_v2
        pred_v2 = svc_v2.predict_student_risk(sid, observation_window_end=cutoff, persist=True)

        # Both records must have distinct IDs
        assert pred_v1.id != pred_v2.id, (
            f"Predictions with different versions must have distinct IDs: "
            f"v1={pred_v1.id}, v2={pred_v2.id}"
        )
        assert pred_v1.model_version == "v1.2.0-explainable"
        assert pred_v2.model_version == "v2.0.0-ml"

        # Check DB: Both rows must exist simultaneously
        db_session.expire_all()
        rows = (
            db_session.query(RiskPrediction)
            .filter(
                RiskPrediction.student_id == sid,
                RiskPrediction.observation_window_end == cutoff
            )
            .all()
        )
        assert len(rows) == 2, f"Expected 2 versioned predictions for student {sid}, found {len(rows)}"

        versions_in_db = {r.model_version for r in rows}
        assert "v1.2.0-explainable" in versions_in_db
        assert "v2.0.0-ml" in versions_in_db

    def test_repeated_same_version_updates_in_place_without_touching_other_versions(self, db_session):
        """
        Re-running a prediction with version A updates version A's record in-place
        and leaves version B's record completely untouched.
        """
        sid = "STU-2026-000016"
        cutoff = date(2026, 10, 15)

        # Clean slate
        existing_rows = db_session.query(RiskPrediction).filter(RiskPrediction.student_id == sid).all()
        for r in existing_rows:
            db_session.delete(r)
        db_session.commit()

        # Run v1
        svc_v1 = _service(db_session)
        p_v1 = svc_v1.predict_student_risk(sid, observation_window_end=cutoff, persist=True)
        v1_score = p_v1.overall_score

        # Run v2
        svc_v2 = _service(db_session)
        svc_v2.engine = RiskEngine(version="v2.0.0-ml")
        p_v2 = svc_v2.predict_student_risk(sid, observation_window_end=cutoff, persist=True)
        v2_score = p_v2.overall_score

        # Re-run v1 (should update v1 without creating a third row or altering v2)
        p_v1_repeat = svc_v1.predict_student_risk(sid, observation_window_end=cutoff, persist=True)

        db_session.expire_all()
        all_rows = (
            db_session.query(RiskPrediction)
            .filter(
                RiskPrediction.student_id == sid,
                RiskPrediction.observation_window_end == cutoff
            )
            .all()
        )
        assert len(all_rows) == 2, f"Expected exactly 2 rows after re-scoring v1, found {len(all_rows)}"

        row_v2 = next(r for r in all_rows if r.model_version == "v2.0.0-ml")
        assert row_v2.overall_score == v2_score, "Version 2 prediction was mutated when re-scoring Version 1"


