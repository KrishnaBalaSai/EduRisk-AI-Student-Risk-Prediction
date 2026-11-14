"""
Dataset Reproducibility Verification Script
Verifies that fixed seed 20261022 produces 100% bit-for-bit identical business entities across independent runs.
Usage:
    python -m scripts.verify_reproducibility
"""

import sys
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List

# Add project root
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from generators.master_generator import MasterGenerator

EXCLUDED_VOLATILE_FIELDS = {"created_at", "updated_at"}


def canonicalize_entities(entities: List[Any]) -> List[Dict[str, Any]]:
    """
    Extract dictionary representations, exclude volatile timestamps, and sort canonically by primary key.
    """
    canonical_list = []
    for e in entities:
        d = e.to_dict()
        # Remove volatile generation timestamps
        for field in EXCLUDED_VOLATILE_FIELDS:
            d.pop(field, None)
        canonical_list.append(d)

    # Stable sort by ID
    canonical_list.sort(key=lambda x: str(x.get("id", "")))
    return canonical_list


def compute_entity_hash(canonical_list: List[Dict[str, Any]]) -> str:
    """
    Compute deterministic SHA-256 digest of canonically serialized JSON.
    """
    canonical_json = json.dumps(canonical_list, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def main():
    print("=" * 70)
    print("  EduRisk AI — Deterministic Reproducibility Verification")
    print("=" * 70)
    seed = 20261022
    profile = "starter"

    print(f"Seed Configuration : {seed}")
    print(f"Target Profile     : {profile.upper()}")
    print("-" * 70)

    # RUN 1
    print("Executing Run #1...")
    gen1 = MasterGenerator(profile_name=profile, seed=seed)
    data1 = gen1.generate(inject_anomalies_flag=False)

    # RUN 2
    print("Executing Run #2 with identical seed...")
    gen2 = MasterGenerator(profile_name=profile, seed=seed)
    data2 = gen2.generate(inject_anomalies_flag=False)

    entities_to_compare = [
        "students",
        "courses",
        "enrollments",
        "attendance_events",
        "assessments",
        "assessment_results",
        "lms_activities",
        "support_cases",
        "interventions",
        "outcomes",
    ]

    print("\nComparing Canonical SHA-256 Hashes and ID Sequences:")
    print("-" * 70)
    print(f"{'Entity':<22} | {'Count':<7} | {'IDs Match':<10} | {'SHA-256 Hash Status'}")
    print("-" * 70)

    all_matched = True
    report_details = []

    for name in entities_to_compare:
        list1 = canonicalize_entities(data1[name])
        list2 = canonicalize_entities(data2[name])

        count1 = len(list1)
        count2 = len(list2)
        count_match = (count1 == count2)

        ids1 = [x["id"] for x in list1]
        ids2 = [x["id"] for x in list2]
        id_match = (ids1 == ids2)

        hash1 = compute_entity_hash(list1)
        hash2 = compute_entity_hash(list2)
        hash_match = (hash1 == hash2)

        if not (count_match and id_match and hash_match):
            all_matched = False
            status = "❌ MISMATCH"
        else:
            status = "✅ MATCH (100% Identical)"

        print(f"{name:<22} | {count1:<7} | {'True' if id_match else 'False':<10} | {status}")

        report_details.append({
            "entity": name,
            "count_run1": count1,
            "count_run2": count2,
            "id_match": id_match,
            "hash_run1": hash1,
            "hash_run2": hash2,
            "status": "MATCH" if hash_match else "MISMATCH"
        })

    print("-" * 70)
    final_verdict = "PASSED — 100% BIT-FOR-BIT REPRODUCIBLE" if all_matched else "FAILED"
    print(f"Overall Reproducibility Result: {final_verdict}")
    print("=" * 70)

    # Save reproducibility report to docs/
    report_path = project_root / "docs" / "reproducibility_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "seed": seed,
            "profile": profile,
            "overall_status": final_verdict,
            "entities": report_details
        }, f, indent=2)
    print(f"Detailed reproducibility report saved to: {report_path}")

    if not all_matched:
        sys.exit(1)


if __name__ == "__main__":
    main()

