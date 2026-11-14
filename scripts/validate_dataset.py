"""
Dataset Validation Script
Runs full validation suite across primary keys, foreign keys, enums, lifecycles, and negative scenarios.
Usage:
    python -m scripts.validate_dataset
"""

import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from application.validators.validation_suite import ValidationSuite


def main():
    print("=" * 65)
    print("  EduRisk AI — Comprehensive Dataset Validation")
    print("=" * 65)

    suite = ValidationSuite()
    print("Running domain validators across database records...")
    results = suite.run_all()
    paths = suite.export_reports(results, export_dir=str(project_root / "exports"))

    print("-" * 65)
    print(f"Total Checks Passed        : {results['total_passed']:,}")
    print(f"Total Identified Inconsist.: {results['total_failed']:,}")
    print(f"Negative Scenarios Found   : {results['ground_truth_reconciliation']['detected_fixtures_count']} / {results['ground_truth_reconciliation']['expected_fixtures_count']}")
    print(f"All 5 Mandatory Anomalies  : {'✅ DETECTED 100%' if results['all_anomalies_detected'] else '❌ PARTIAL'}")
    print("-" * 65)

    print("\nAnomalies Audit Breakdown:")
    for fix in results["ground_truth_reconciliation"].get("fixtures", []):
        icon = "✅" if fix["detected"] else "❌"
        print(f"  {icon} [{fix['issue_type']}] on {fix['record_id']} -> {fix['status']}")

    print("\nExported Reports:")
    print(f"  • JSON Report : {paths['json_report']}")
    print(f"  • CSV Report  : {paths['csv_report']}")
    print("=" * 65)


if __name__ == "__main__":
    main()

