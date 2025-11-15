"""
Database layer package for the Vaani voice banking assistant.

This module exposes convenience imports for the SQLAlchemy engine and
session factory so that downstream application layers can remain
agnostic to the underlying database vendor (SQLite by default, optionally
PostgreSQL).
"""

from .config import DatabaseConfig, load_database_config
from .engine import create_db_engine, get_session_factory
from .services import AuthService, BankingService

__all__ = [
    "DatabaseConfig",
    "load_database_config",
    "create_db_engine",
    "get_session_factory",
    "AuthService",
    "BankingService",
]


