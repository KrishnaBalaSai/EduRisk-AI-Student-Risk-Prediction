"""
CLI Runner for synthetic dataset generation.
Usage:
    python -m generators.generate_all --profile starter
    python -m generators.generate_all --profile full
"""

import argparse
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from generators.master_generator import MasterGenerator


def main():
    parser = argparse.ArgumentParser(description="EduRisk AI Synthetic Dataset Generator")
    parser.add_argument(
        "--profile",
        type=str,
        default="starter",
        choices=["starter", "full"],
        help="Dataset size profile: 'starter' (100 students) or 'full' (5,000 students)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=20261022,
        help="Deterministic random seed (default: 20261022)",
    )
    parser.add_argument(
        "--no-anomalies",
        action="store_true",
        help="Skip injecting the 5 labelled negative scenarios",
    )
    args = parser.parse_args()

    print(f"=== EduRisk AI Synthetic Dataset Generator ===")
    print(f"Profile: {args.profile.upper()}")
    print(f"Seed: {args.seed}")
    print(f"Inject Anomalies: {not args.no_anomalies}")
    print("-" * 50)

    start_time = time.time()
    generator = MasterGenerator(profile_name=args.profile, seed=args.seed)
    dataset = generator.generate(inject_anomalies_flag=not args.no_anomalies)
    gen_time = time.time() - start_time

    print(f"Dataset generated in {gen_time:.2f} seconds.")
    print("\nPersisting entities to database...")

    persist_start = time.time()
    counts = generator.persist_to_database(dataset)
    persist_time = time.time() - persist_start

    print("\n--- Generation Summary ---")
    for entity, count in counts.items():
        print(f"  {entity:<25}: {count:,} records")
    print("-" * 50)
    print(f"Total time elapsed: {gen_time + persist_time:.2f} seconds.")
    print("Generation completed successfully.")


if __name__ == "__main__":
    main()

