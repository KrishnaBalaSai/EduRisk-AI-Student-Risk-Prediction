"""
Dataset Generation Script
Generates either 'starter' (100 students) or 'full' (5,000 students) dataset.
Usage:
    python -m scripts.generate_dataset --profile starter
    python -m scripts.generate_dataset --profile full
"""

import sys
import argparse
import time
from pathlib import Path

# Add project root
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from generators.master_generator import MasterGenerator


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic dataset for EduRisk AI")
    parser.add_argument(
        "--profile",
        type=str,
        default="starter",
        choices=["starter", "full"],
        help="Profile size: starter (100 students) or full (5,000 students)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=20261022,
        help="Deterministic random seed (default: 20261022)"
    )
    parser.add_argument(
        "--skip-anomalies",
        action="store_true",
        help="Skip injecting the 5 labelled anomaly fixtures"
    )
    args = parser.parse_args()

    print("=" * 65)
    print(f"  EduRisk AI — Synthetic Dataset Generation [{args.profile.upper()}]")
    print("=" * 65)
    print(f"Random Seed     : {args.seed}")
    print(f"Inject Anomalies: {not args.skip_anomalies}")
    print("-" * 65)

    start = time.time()
    generator = MasterGenerator(profile_name=args.profile, seed=args.seed)
    
    print("Step 1/2: Generating in-memory domain entities...")
    dataset = generator.generate(inject_anomalies_flag=not args.skip_anomalies)
    gen_duration = time.time() - start

    print(f"-> In-memory generation completed in {gen_duration:.2f}s.")
    print("Step 2/2: Batch persisting to database...")

    persist_start = time.time()
    counts = generator.persist_to_database(dataset)
    persist_duration = time.time() - persist_start

    print("\n--- Summary of Persisted Records ---")
    for entity, count in counts.items():
        print(f"  • {entity:<28}: {count:,}")
    print("-" * 65)
    print(f"Total execution time: {gen_duration + persist_duration:.2f} seconds.")
    print("✅ Dataset generation completed successfully.")
    print("=" * 65)


if __name__ == "__main__":
    main()

