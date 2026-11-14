"""
Test Suite: Deterministic Reproducibility
Verifies that identical seed (20261022) produces identical primary keys, row counts, and data.
"""

import pytest
from generators.master_generator import MasterGenerator
from scripts.verify_reproducibility import canonicalize_entities, compute_entity_hash


def test_seed_reproducibility():
    """Verify two generator instances with seed 20261022 produce identical hashes."""
    seed = 20261022
    gen1 = MasterGenerator(profile_name="starter", seed=seed)
    gen2 = MasterGenerator(profile_name="starter", seed=seed)

    data1 = gen1.generate(inject_anomalies_flag=False)
    data2 = gen2.generate(inject_anomalies_flag=False)

    for entity_name in ["students", "courses", "enrollments", "attendance_events", "assessments"]:
        list1 = canonicalize_entities(data1[entity_name])
        list2 = canonicalize_entities(data2[entity_name])

        assert len(list1) == len(list2), f"Length mismatch on {entity_name}"
        hash1 = compute_entity_hash(list1)
        hash2 = compute_entity_hash(list2)
        assert hash1 == hash2, f"Hash mismatch on {entity_name}"

