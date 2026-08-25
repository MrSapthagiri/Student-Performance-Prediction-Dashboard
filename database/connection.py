"""
Database connection management using SQLAlchemy.
Supports PostgreSQL (production) and SQLite (fallback for local dev).
"""

import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from dotenv import load_dotenv

# Load .env from project root
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_project_root, '.env'))

DATABASE_URL = os.getenv("DATABASE_URL", "")

# Auto-detect: if PostgreSQL is not reachable, fallback to SQLite
_use_sqlite = False

if DATABASE_URL and DATABASE_URL.startswith("postgresql"):
    try:
        _test_engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        with _test_engine.connect() as conn:
            conn.execute(__import__('sqlalchemy').text("SELECT 1"))
        engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)
        print("[DB] Connected to PostgreSQL")
    except Exception as e:
        print(f"[DB] PostgreSQL not available ({e}). Falling back to SQLite.")
        _use_sqlite = True
else:
    _use_sqlite = True

if _use_sqlite:
    _db_path = os.path.join(_project_root, 'data', 'student_success.db')
    os.makedirs(os.path.dirname(_db_path), exist_ok=True)
    DATABASE_URL = f"sqlite:///{_db_path}"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

    # Enable WAL mode for better concurrent access
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    print(f"[DB] Using SQLite: {_db_path}")


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Session:
    """Get a database session."""
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


def init_db():
    """Create all tables defined in models."""
    from database.models import (
        User, Student, Module, StudentModule, Intervention
    )
    Base.metadata.create_all(bind=engine)


def get_engine():
    return engine


def is_sqlite():
    return _use_sqlite
