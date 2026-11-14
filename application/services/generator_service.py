"""
Generator Application Service
Encapsulates synthetic dataset generation and schema initialization for the presentation layer.
Adheres strictly to Three-Tier Architecture.
"""

from typing import Dict, Any
from generators.master_generator import MasterGenerator


class GeneratorService:
    @staticmethod
    def generate_and_persist(
        profile_name: str = "starter",
        seed: int = 20261022,
        inject_anomalies: bool = True,
        clean_first: bool = True
    ) -> Dict[str, int]:
        """
        Orchestrates in-memory generation and database persistence through the application layer.
        """
        generator = MasterGenerator(profile_name=profile_name, seed=seed)
        dataset = generator.generate(inject_anomalies_flag=inject_anomalies)
        return generator.persist_to_database(dataset, clean_first=clean_first)

