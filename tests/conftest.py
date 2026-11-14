"""
Pytest Fixtures and Test Configuration
Sets up isolated test database sessions and pre-loaded starter data.
"""

import sys
from pathlib import Path
import pytest

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from data.database import get_engine, init_db, session_scope, get_session
from generators.master_generator import MasterGenerator


@pytest.fixture(scope="session")
def engine():
    eng = get_engine()
    init_db(eng)
    return eng


@pytest.fixture(scope="session")
def db_session(engine):
    session = get_session()
    # Pre-generate starter dataset if empty
    from data.models.student import Student
    if session.query(Student).count() == 0:
        gen = MasterGenerator(profile_name="starter", seed=20261022)
        dataset = gen.generate(inject_anomalies_flag=True)
        gen.persist_to_database(dataset, session=session)
    yield session
    session.close()


@pytest.fixture
def starter_dataset():
    gen = MasterGenerator(profile_name="starter", seed=20261022)
    return gen.generate(inject_anomalies_flag=False)

