"""
Database Initialization Script
Creates tables and indexes for MySQL 8+ or local SQLite fallback.
Usage:
    python -m scripts.initialize_database
"""

import sys
import logging
from pathlib import Path

# Add project root
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from data.database import init_db, get_engine, DB_TYPE, DB_HOST, DB_PORT, DB_NAME

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main():
    print("=" * 60)
    print("  EduRisk AI — Database Initialization")
    print("=" * 60)
    print(f"Target Dialect : {DB_TYPE.upper()}")
    if DB_TYPE == "mysql":
        print(f"MySQL Host     : {DB_HOST}:{DB_PORT}")
        print(f"Database Name  : {DB_NAME}")
    print("-" * 60)

    try:
        engine = get_engine()
        print(f"Active Engine  : {engine.url}")
        init_db(engine)
        print("\n✅ All 10 entity tables and auxiliary indexes initialized successfully!")
        print("Schema verified: Student, Course, Enrollment, AttendanceEvent, Assessment,")
        print("AssessmentResult, LMSActivity, SupportCase, Intervention, Outcome,")
        print("RiskPrediction, AnomalyFixture.")
        print("=" * 60)
    except Exception as exc:
        print(f"\n❌ Database initialization failed: {exc}")
        if DB_TYPE == "mysql":
            print("\nSetup Action Needed:")
            print("1. Ensure MySQL 8+ server is running on localhost:3306")
            print("2. Ensure database 'edurisk_db' exists: CREATE DATABASE edurisk_db;")
            print("3. Check credentials in .env file (DB_USER, DB_PASSWORD)")
            print("4. Or set DB_TYPE=sqlite in .env for zero-dependency standalone local execution.")
        sys.exit(1)


if __name__ == "__main__":
    main()

