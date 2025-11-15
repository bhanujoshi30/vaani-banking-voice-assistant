"""Dependency wiring for FastAPI endpoints."""

from __future__ import annotations

from functools import lru_cache
from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from ..db import (
    AuthService,
    BankingService,
    DatabaseConfig,
    create_db_engine,
    get_session_factory,
    load_database_config,
)
from ..db.engine import session_scope
from ..db.base import Base


@lru_cache
def get_db_config() -> DatabaseConfig:
    return load_database_config()


@lru_cache
def get_session_factory_cached():
    config = get_db_config()
    engine = create_db_engine(config)
    Base.metadata.create_all(engine)
    return get_session_factory(engine)


def get_session() -> Generator[Session, None, None]:
    factory = get_session_factory_cached()
    with session_scope(factory) as session:
        yield session


@lru_cache
def get_auth_service() -> AuthService:
    factory = get_session_factory_cached()
    return AuthService(factory)


@lru_cache
def get_banking_service() -> BankingService:
    factory = get_session_factory_cached()
    return BankingService(factory)


AuthServiceDep = Depends(get_auth_service)
BankingServiceDep = Depends(get_banking_service)


__all__ = ["AuthServiceDep", "BankingServiceDep", "get_session"]


