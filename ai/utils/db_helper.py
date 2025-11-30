"""
Database helper for AI backend
Connects to the existing banking backend database
"""
import sys
from pathlib import Path
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy.orm import Session

# Add backend to path (handle multiple possible locations)
# Note: In Vercel deployment, backend is deployed separately, so this may not exist
backend_paths = [
    Path(__file__).parent.parent.parent / "backend",  # python/backend/
    Path(__file__).parent.parent.parent.parent / "backend",  # backend/ (if utils is deeper)
]

backend_path = None
for path in backend_paths:
    if path.exists() and (path / "db" / "config.py").exists():
        backend_path = path
        break

# Only try to import if backend path exists (for local development)
if backend_path:
    sys.path.insert(0, str(backend_path))
    try:
        from db.config import load_database_config
        from db.engine import create_db_engine, get_session_factory
        _db_available = True
    except ImportError as e:
        import logging
        logging.warning(f"Database modules not available: {e}")
        _db_available = False
        # Create dummy functions
        def load_database_config():
            raise RuntimeError("Database not available")
        def create_db_engine(config):
            raise RuntimeError("Database not available")
        def get_session_factory(engine):
            raise RuntimeError("Database not available")
else:
    _db_available = False
    import logging
    logging.warning("Backend path not found, database features will be unavailable")
    # Create dummy functions
    def load_database_config():
        raise RuntimeError("Database not available - backend path not found")
    def create_db_engine(config):
        raise RuntimeError("Database not available - backend path not found")
    def get_session_factory(engine):
        raise RuntimeError("Database not available - backend path not found")


# Create database engine and session factory (lazy initialization)
# Don't create at import time - create on first use to avoid connection errors during import
_engine = None
_SessionLocal = None
_config = None

def _init_db():
    """Initialize database connection (lazy)"""
    global _engine, _SessionLocal, _config
    if _engine is None:
        try:
            _config = load_database_config()
            _engine = create_db_engine(_config)
            _SessionLocal = get_session_factory(_engine)
        except Exception as e:
            # Log error but don't crash - database might not be available in all environments
            import logging
            logging.warning(f"Failed to initialize database: {e}")
            # Create a dummy session factory that will fail on use
            _SessionLocal = None
    return _engine, _SessionLocal

def get_engine():
    """Get database engine (lazy initialization)"""
    engine, _ = _init_db()
    return engine

def get_session_factory():
    """Get session factory (lazy initialization)"""
    _, session_factory = _init_db()
    return session_factory

# For backward compatibility, try to initialize but don't fail
if _db_available:
    try:
        config = load_database_config()
        engine = create_db_engine(config)
        SessionLocal = get_session_factory(engine)
    except Exception as e:
        import logging
        logging.warning(f"Database initialization failed: {e}")
        # Database not available - will be initialized on first use
        engine = None
        SessionLocal = None
else:
    config = None
    engine = None
    SessionLocal = None


@contextmanager
def get_db() -> Iterator[Session]:
    """
    Database session dependency for AI tools
    Yields a database session and ensures proper cleanup
    """
    # Lazy initialization - try to get session factory if not already initialized
    if SessionLocal is None:
        try:
            _init_db()
        except Exception as e:
            import logging
            logging.error(f"Database initialization failed: {e}")
            raise
    
    if SessionLocal is None:
        raise RuntimeError("Database session factory not available. Check database configuration.")
    
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


__all__ = ["get_db", "SessionLocal", "engine"]
