"""
Database connection, session management, and engine configuration.
Supports MySQL 8+ via PyMySQL with automatic fallback to SQLite for local development.
"""

import os
import logging
from pathlib import Path
from contextlib import contextmanager
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session

logger = logging.getLogger(__name__)

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_password")
DB_NAME = os.getenv("DB_NAME", "edurisk_db")
DB_SQLITE_PATH = os.getenv("DB_SQLITE_PATH", "edurisk.db")

Base = declarative_base()
_engine = None
_SessionFactory = None


def get_db_url(force_sqlite: bool = False) -> str:
    """Resolve database URL based on configuration and availability."""
    if force_sqlite or DB_TYPE == "sqlite":
        # Resolve path relative to project root
        project_root = Path(__file__).resolve().parent.parent
        sqlite_file = project_root / DB_SQLITE_PATH
        return f"sqlite:///{sqlite_file.as_posix()}"
    
    # MySQL connection string
    return f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"


def create_db_engine(force_sqlite: bool = False):
    """Create SQLAlchemy engine with appropriate dialect and connection pooling."""
    url = get_db_url(force_sqlite=force_sqlite)
    
    if "sqlite" in url:
        return create_engine(
            url,
            connect_args={"check_same_thread": False},
            echo=False
        )
    else:
        try:
            engine = create_engine(
                url,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
                pool_recycle=3600,
                echo=False
            )
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Successfully connected to MySQL database: %s", DB_NAME)
            return engine
        except Exception as exc:
            logger.warning(
                "MySQL connection failed (%s). Falling back to SQLite database for zero-downtime execution.",
                exc
            )
            sqlite_url = get_db_url(force_sqlite=True)
            return create_engine(
                sqlite_url,
                connect_args={"check_same_thread": False},
                echo=False
            )


def get_engine():
    """Singleton getter for SQLAlchemy engine."""
    global _engine
    if _engine is None:
        _engine = create_db_engine()
    return _engine


def get_session_factory():
    """Singleton getter for session factory."""
    global _SessionFactory
    if _SessionFactory is None:
        engine = get_engine()
        _SessionFactory = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=engine)
        )
    return _SessionFactory


def get_session():
    """Retrieve a new database session."""
    factory = get_session_factory()
    return factory()


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db(engine=None):
    """Create all tables in the database if they do not exist."""
    if engine is None:
        engine = get_engine()
    # Import all models to ensure they are registered with Base.metadata
    from data.models import (
        student,
        course,
        enrollment,
        attendance,
        assessment,
        assessment_result,
        lms_activity,
        support_case,
        intervention,
        outcome,
        risk_prediction,
        anomaly_fixture
    )
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema initialized successfully.")

