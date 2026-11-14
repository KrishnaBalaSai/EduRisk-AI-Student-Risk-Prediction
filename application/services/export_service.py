"""
Data Export Service
Exports all 10 domain entities, ground truth labels, validation results, and SQL dumps
to CSV, JSON, and SQL formats.
"""

import json
import csv
from pathlib import Path
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from data.database import get_session
from data.models.student import Student
from data.models.course import Course
from data.models.enrollment import Enrollment
from data.models.attendance import AttendanceEvent
from data.models.assessment import Assessment
from data.models.assessment_result import AssessmentResult
from data.models.lms_activity import LMSActivity
from data.models.support_case import SupportCase
from data.models.intervention import Intervention
from data.models.outcome import Outcome
from data.models.anomaly_fixture import AnomalyFixture


class ExportService:
    def __init__(self, session: Session = None, base_dir: str = "exports"):
        self.session = session or get_session()
        self.base_dir = Path(base_dir)
        self.csv_dir = self.base_dir / "csv"
        self.json_dir = self.base_dir / "json"
        self.sql_dir = self.base_dir / "sql"
        self.csv_dir.mkdir(parents=True, exist_ok=True)
        self.json_dir.mkdir(parents=True, exist_ok=True)
        self.sql_dir.mkdir(parents=True, exist_ok=True)

    def export_all(self) -> Dict[str, Dict[str, str]]:
        """
        Exports all 10 entities plus ground truth and SQL dumps.
        """
        entities = [
            ("students", Student),
            ("courses", Course),
            ("enrollments", Enrollment),
            ("attendance", AttendanceEvent),
            ("assessments", Assessment),
            ("assessment_results", AssessmentResult),
            ("lms_activities", LMSActivity),
            ("support_cases", SupportCase),
            ("interventions", Intervention),
            ("outcomes", Outcome),
            ("ground_truth_anomalies", AnomalyFixture),
        ]

        manifest = {"csv": {}, "json": {}, "sql": {}}

        for name, cls in entities:
            records = self.session.query(cls).all()
            dicts = [r.to_dict() for r in records]

            # 1. JSON Export
            json_file = self.json_dir / f"{name}.json"
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(dicts, f, indent=2)
            manifest["json"][name] = str(json_file)

            # 2. CSV Export
            csv_file = self.csv_dir / f"{name}.csv"
            if dicts:
                keys = dicts[0].keys()
                with open(csv_file, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=keys)
                    writer.writeheader()
                    writer.writerows(dicts)
            else:
                with open(csv_file, "w", newline="", encoding="utf-8") as f:
                    pass
            manifest["csv"][name] = str(csv_file)

        # 3. SQL Seed Export
        sql_file = self.sql_dir / "edurisk_seed.sql"
        with open(sql_file, "w", encoding="utf-8") as f:
            f.write("-- EduRisk AI Database Seed Dump\n")
            f.write("-- Generated for MySQL 8+ / SQLAlchemy\n\n")
            for name, cls in entities:
                records = self.session.query(cls).all()
                f.write(f"\n-- Table: {cls.__tablename__} ({len(records)} rows)\n")
                for r in records[:500]:  # Up to 500 rows per table for SQL seed
                    d = r.to_dict()
                    cols = ", ".join(f"`{k}`" for k in d.keys())
                    vals = []
                    for v in d.values():
                        if v is None:
                            vals.append("NULL")
                        elif isinstance(v, (int, float)):
                            vals.append(str(v))
                        elif isinstance(v, bool):
                            vals.append("1" if v else "0")
                        else:
                            clean_str = str(v).replace("'", "''")
                            vals.append(f"'{clean_str}'")
                    vals_str = ", ".join(vals)
                    f.write(f"INSERT INTO `{cls.__tablename__}` ({cols}) VALUES ({vals_str});\n")
        manifest["sql"]["seed"] = str(sql_file)

        return manifest

