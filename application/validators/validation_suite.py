"""
Comprehensive Validation Suite
Orchestrates all domain validators, compares detected anomalies against injected ground truth fixtures,
and outputs formal validation reports in CSV and JSON formats.
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from data.database import get_session
from data.models.anomaly_fixture import AnomalyFixture
from application.validators.integrity_validator import IntegrityValidator
from application.validators.temporal_validator import TemporalValidator
from application.validators.reconciliation_validator import ReconciliationValidator
from application.validators.lifecycle_validator import LifecycleValidator
from application.validators.duplicate_validator import DuplicateValidator


class ValidationSuite:
    def __init__(self, session: Session = None):
        self.session = session or get_session()

    def run_all(self) -> Dict[str, Any]:
        """
        Executes all 5 validators and correlates findings with ground-truth fixtures.
        """
        timestamp = datetime.utcnow().isoformat()
        validators = [
            IntegrityValidator(self.session),
            TemporalValidator(self.session),
            ReconciliationValidator(self.session),
            LifecycleValidator(self.session),
            DuplicateValidator(self.session),
        ]

        suite_results = {
            "validation_timestamp": timestamp,
            "total_passed": 0,
            "total_failed": 0,
            "total_warnings": 0,
            "validators": {},
            "all_detected_anomalies": [],
            "ground_truth_reconciliation": {},
            "summary_status": "PASSED",
        }

        for v in validators:
            v_res = v.validate_all()
            name = v_res["validator"]
            suite_results["validators"][name] = v_res
            suite_results["total_passed"] += v_res["passed"]
            suite_results["total_failed"] += v_res["failed"]
            if "detected_anomalies" in v_res:
                suite_results["all_detected_anomalies"].extend(v_res["detected_anomalies"])

        # Compare detected anomalies against Ground Truth Fixtures
        fixtures = self.session.query(AnomalyFixture).all()
        detected_issue_types = {a["issue_type"] for a in suite_results["all_detected_anomalies"]}

        recon = {
            "expected_fixtures_count": len(fixtures),
            "detected_fixtures_count": len(suite_results["all_detected_anomalies"]),
            "fixtures": [],
        }

        all_detected = True
        for f in fixtures:
            is_found = f.issue_type in detected_issue_types
            f.detected = is_found
            if not is_found:
                all_detected = False
            recon["fixtures"].append({
                "fixture_id": f.id,
                "issue_type": f.issue_type,
                "record_id": f.record_id,
                "description": f.description,
                "detected": is_found,
                "status": "DETECTED_SUCCESSFULLY" if is_found else "UNDETECTED"
            })

        self.session.commit()
        suite_results["ground_truth_reconciliation"] = recon
        suite_results["all_anomalies_detected"] = all_detected

        return suite_results

    def export_reports(self, results: Dict[str, Any], export_dir: str = "exports") -> Dict[str, str]:
        """
        Export validation results as CSV and JSON.
        """
        out_dir = Path(export_dir)
        json_dir = out_dir / "json"
        csv_dir = out_dir / "csv"
        json_dir.mkdir(parents=True, exist_ok=True)
        csv_dir.mkdir(parents=True, exist_ok=True)

        json_path = json_dir / "validation_report.json"
        csv_path = csv_dir / "validation_report.csv"

        # Write JSON
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        # Write CSV
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Validator", "Passed", "Failed", "Errors"])
            for v_name, v_data in results["validators"].items():
                writer.writerow([
                    v_name,
                    v_data["passed"],
                    v_data["failed"],
                    "; ".join(v_data.get("errors", []))
                ])

            # Write anomaly section
            writer.writerow([])
            writer.writerow(["Fixture ID", "Issue Type", "Record ID", "Status", "Description"])
            for fix in results["ground_truth_reconciliation"].get("fixtures", []):
                writer.writerow([
                    fix["fixture_id"],
                    fix["issue_type"],
                    fix["record_id"],
                    fix["status"],
                    fix["description"]
                ])

        return {
            "json_report": str(json_path),
            "csv_report": str(csv_path),
        }

