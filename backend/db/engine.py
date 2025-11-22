"""
Engine and session management helpers.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from .config import DatabaseConfig


def create_db_engine(config: DatabaseConfig) -> Engine:
    """
    Build an SQLAlchemy engine based on the provided configuration.

    Handles backend-specific options (e.g., SQLite check_same_thread) to
    ensure compatibility across different database vendors.
    """

    connect_args = {}
    if config.backend == "sqlite":
        connect_args["check_same_thread"] = False
        # Set timeout to handle concurrent access (default is 5 seconds)
        # This prevents "readonly database" errors when multiple connections try to write
        connect_args["timeout"] = 20.0

    engine_kwargs = {
        "echo": config.echo,
        "future": True,
        "connect_args": connect_args,
    }

    # SQLite doesn't benefit from connection pooling - use NullPool for SQLite
    if config.backend == "sqlite":
        from sqlalchemy.pool import NullPool
        engine_kwargs["poolclass"] = NullPool
    else:
        # For other databases, use configured pool settings
        if config.pool_size is not None:
            engine_kwargs["pool_size"] = config.pool_size
        if config.max_overflow is not None:
            engine_kwargs["max_overflow"] = config.max_overflow

    engine = create_engine(
        config.database_url,
        **engine_kwargs,
    )
    return engine


def get_session_factory(engine: Engine):
    """Return a configured session factory bound to the provided engine."""

    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


@contextmanager
def session_scope(session_factory) -> Iterator:
    """
    Provide a transactional scope for a series of operations.

    Example:
        with session_scope(SessionLocal) as session:
            # do work
    """

    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


__all__ = ["create_db_engine", "get_session_factory", "session_scope"]


