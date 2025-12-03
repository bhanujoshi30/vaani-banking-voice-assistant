"""
Database configuration utilities.

The configuration abstraction ensures we can switch between SQLite for
local prototyping and PostgreSQL (or any SQLAlchemy-supported backend)
for production deployments without touching the domain logic.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


DEFAULT_SQLITE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "vaani.db",
)


@dataclass(frozen=True)
class DatabaseConfig:
    """Container for database connection settings."""

    backend: str
    database_url: str
    echo: bool = False
    pool_size: Optional[int] = None
    max_overflow: Optional[int] = None


def _build_default_sqlite_url() -> str:
    return f"sqlite:///{DEFAULT_SQLITE_PATH}"


def load_database_config() -> DatabaseConfig:
    """
    Load database configuration from environment variables.

    Environment variables:
        DB_BACKEND: Name of the backend, e.g., ``sqlite`` or ``postgresql``.
        DATABASE_URL: Full SQLAlchemy compatible database URL.
        DB_ECHO: Enable SQL echo logging when set to ``1`` or ``true``.
        DB_POOL_SIZE: Optional integer for SQLAlchemy pool size.
        DB_MAX_OVERFLOW: Optional integer for pool overflow allowance.
    """

    backend = os.getenv("DB_BACKEND", "sqlite").lower()
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        if backend == "sqlite":
            database_url = _build_default_sqlite_url()
        else:
            raise ValueError(
                "DATABASE_URL must be provided when using non-SQLite backend."
            )

    echo_env = os.getenv("DB_ECHO", "0").lower()
    echo = echo_env in {"1", "true", "yes"}

    pool_size = _parse_optional_int(os.getenv("DB_POOL_SIZE"))
    max_overflow = _parse_optional_int(os.getenv("DB_MAX_OVERFLOW"))

    return DatabaseConfig(
        backend=backend,
        database_url=database_url,
        echo=echo,
        pool_size=pool_size,
        max_overflow=max_overflow,
    )


def _parse_optional_int(raw: Optional[str]) -> Optional[int]:
    if raw is None:
        return None
    raw = raw.strip()
    if not raw:
        return None
    return int(raw)


__all__ = ["DatabaseConfig", "load_database_config"]


