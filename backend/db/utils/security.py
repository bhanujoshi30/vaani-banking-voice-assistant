"""Security helpers for credential hashing and verification."""

from __future__ import annotations

from passlib.context import CryptContext

_pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
    pbkdf2_sha256__default_rounds=320000,
)


def hash_password(plain_password: str) -> str:
    """Return a bcrypt hash for the provided password."""

    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check whether the provided password matches the stored hash."""

    return _pwd_context.verify(plain_password, hashed_password)


__all__ = ["hash_password", "verify_password"]


