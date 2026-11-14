"""
Master Dataset Generator
Orchestrates end-to-end synthetic dataset generation adhering to the strict dependency order:
Students -> Courses -> Enrollments -> Attendance -> Assessments -> Assessment Results ->
LMS Activity -> Support Cases -> Interventions -> Outcomes.
"""

import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from data.database import get_session, session_scope, init_db
from generators.enrollment_generator import (
    generate_students,
    generate_courses,
    generate_enrollments,
)
from generators.attendance_generator import generate_attendance_events
from generators.assessment_generator import (
    generate_assessments,
    generate_assessment_results,
)
from generators.lms_generator import generate_lms_activity
from generators.support_generator import generate_support_cases
from generators.intervention_generator import generate_interventions
from generators.outcome_generator import generate_outcomes
from generators.anomaly_generator import inject_anomalies

logger = logging.getLogger(__name__)

PROFILES = {
    "starter": {
        "student_count": 100,
        "course_count": 20,
        "enrollment_count": 300,
    },
    "full": {
        "student_count": 5000,
        "course_count": 200,
        "enrollment_count": 20000,
    },
}


class MasterGenerator:
    def __init__(self, profile_name: str = "starter", seed: int = 20261022):
        self.profile_name = profile_name.lower()
        if self.profile_name not in PROFILES:
            raise ValueError(f"Unknown profile: {profile_name}. Expected 'starter' or 'full'.")
        self.config = PROFILES[self.profile_name]
        self.seed = seed

    def generate(self, inject_anomalies_flag: bool = True) -> Dict[str, Any]:
        """
        Generate complete in-memory dataset according to deterministic configuration.

        Enrollment count contract:
        When anomaly injection is enabled, Anomaly #3 (withdrawn_student_active) adds
        exactly 1 extra enrollment record.  To keep the persisted total at the configured
        target (e.g. 20,000), the baseline generator is asked for target_count - 1 so that
        baseline + anomaly = target_count.  When injection is disabled the full target_count
        is used directly.
        """
        logger.info(
            "Starting data generation with profile: %s (seed: %d)",
            self.profile_name,
            self.seed,
        )

        # 1. Students
        students, archetypes = generate_students(
            count=self.config["student_count"],
            seed=self.seed
        )
        student_map = {s.id: s for s in students}

        # 2. Courses
        courses = generate_courses(
            count=self.config["course_count"],
            seed=self.seed
        )
        course_map = {c.id: c for c in courses}

        # 3. Enrollments
        # Reserve 1 slot for the withdrawn_student_active anomaly enrollment when injection
        # is active, so the grand total persisted to the database equals enrollment_count.
        _enr_anomaly_slots = 1 if inject_anomalies_flag else 0
        enrollments = generate_enrollments(
            students=students,
            courses=courses,
            target_count=self.config["enrollment_count"] - _enr_anomaly_slots,
            archetypes=archetypes,
            seed=self.seed
        )
        student_enrollments: Dict[str, list] = {}
        for enr in enrollments:
            student_enrollments.setdefault(enr.student_id, []).append(enr)

        # 4. Attendance Events
        attendance_events = generate_attendance_events(
            enrollments=enrollments,
            course_map=course_map,
            student_map=student_map,
            archetypes=archetypes,
            seed=self.seed
        )

        # 5. Assessments
        assessments = generate_assessments(
            courses=courses,
            seed=self.seed
        )

        # 6. Assessment Results
        assessment_results = generate_assessment_results(
            assessments=assessments,
            enrollments=enrollments,
            student_map=student_map,
            archetypes=archetypes,
            seed=self.seed
        )

        # 7. LMS Activity
        lms_activities = generate_lms_activity(
            students=students,
            student_enrollments=student_enrollments,
            archetypes=archetypes,
            seed=self.seed
        )

        # 8. Support Cases
        support_cases = generate_support_cases(
            students=students,
            archetypes=archetypes,
            seed=self.seed
        )

        # 9. Interventions
        interventions = generate_interventions(
            support_cases=support_cases,
            seed=self.seed
        )
        student_interventions: Dict[str, list] = {}
        for it in interventions:
            student_interventions.setdefault(it.student_id, []).append(it)

        # 10. Outcomes
        outcomes = generate_outcomes(
            students=students,
            student_interventions=student_interventions,
            archetypes=archetypes,
            seed=self.seed
        )

        dataset = {
            "students": students,
            "courses": courses,
            "enrollments": enrollments,
            "attendance_events": attendance_events,
            "assessments": assessments,
            "assessment_results": assessment_results,
            "lms_activities": lms_activities,
            "support_cases": support_cases,
            "interventions": interventions,
            "outcomes": outcomes,
            "archetypes": archetypes,
            "anomaly_fixtures": [],
            "injected_entities": {},
        }

        # 11. Negative Scenarios Injection (if requested)
        if inject_anomalies_flag:
            fixtures, injected = inject_anomalies(
                students=students,
                courses=courses,
                enrollments=enrollments,
                attendance_events=attendance_events,
                assessments=assessments,
                assessment_results=assessment_results,
                interventions=interventions
            )
            dataset["anomaly_fixtures"] = fixtures
            dataset["injected_entities"] = injected

        return dataset

    def persist_to_database(self, dataset: Dict[str, Any], session: Optional[Session] = None, clean_first: bool = True) -> Dict[str, int]:
        """
        Persist generated dataset to database in batches to maintain high throughput.
        If clean_first is True, resets existing tables before persisting.
        """
        from data.database import get_engine, Base
        engine = get_engine()
        if clean_first:
            Base.metadata.drop_all(bind=engine)
            Base.metadata.create_all(bind=engine)
        else:
            init_db(engine)
        owns_session = False
        if session is None:
            session = get_session()
            owns_session = True

        counts = {}

        try:
            # Order of persistence respecting foreign keys
            entity_keys = [
                ("students", dataset["students"]),
                ("courses", dataset["courses"]),
                ("enrollments", dataset["enrollments"]),
                ("attendance_events", dataset["attendance_events"]),
                ("assessments", dataset["assessments"]),
                ("assessment_results", dataset["assessment_results"]),
                ("lms_activities", dataset["lms_activities"]),
                ("support_cases", dataset["support_cases"]),
                ("interventions", dataset["interventions"]),
                ("outcomes", dataset["outcomes"]),
            ]

            batch_size = 1000

            for key, entities in entity_keys:
                for i in range(0, len(entities), batch_size):
                    batch = entities[i : i + batch_size]
                    session.bulk_save_objects(batch)
                session.commit()
                counts[key] = len(entities)
                logger.info("Persisted %d records for %s", len(entities), key)

            # Persist injected negative scenarios if present
            if dataset.get("anomaly_fixtures"):
                session.bulk_save_objects(dataset["anomaly_fixtures"])
                session.commit()
                counts["anomaly_fixtures"] = len(dataset["anomaly_fixtures"])

            injected = dataset.get("injected_entities", {})
            for key, entities in injected.items():
                if entities:
                    session.bulk_save_objects(entities)
                    session.commit()
                    counts[f"injected_{key}"] = len(entities)

            return counts

        finally:
            if owns_session:
                session.close()
