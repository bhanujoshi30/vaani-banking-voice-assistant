"""
Database helper for AI backend
Connects to the existing banking backend database
"""
import sys
from pathlib import Path
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy.orm import Session

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from db.config import load_database_config
from db.engine import create_db_engine, get_session_factory


# Create database engine and session factory
config = load_database_config()
engine = create_db_engine(config)
SessionLocal = get_session_factory(engine)


@contextmanager
def get_db() -> Iterator[Session]:
    """
    Database session dependency for AI tools
    Yields a database session and ensures proper cleanup
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


__all__ = ["get_db", "SessionLocal", "engine"]
