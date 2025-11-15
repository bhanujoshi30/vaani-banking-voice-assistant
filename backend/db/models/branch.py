"""Branch metadata for Sun National Bank."""

from __future__ import annotations

import uuid

from sqlalchemy import Column, String, UniqueConstraint

from ..base import Base
from ..utils.types import GUID


class Branch(Base):
    """Represents a bank branch for account assignment and compliance checks."""

    __tablename__ = "branches"
    __table_args__ = (
        UniqueConstraint("code", name="uq_branch_code"),
        UniqueConstraint("ifsc_code", name="uq_branch_ifsc"),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String(120), nullable=False)
    code = Column(String(20), nullable=False)
    ifsc_code = Column(String(20), nullable=False)
    address_line1 = Column(String(255), nullable=False)
    city = Column(String(120), nullable=False)
    state = Column(String(120), nullable=False)
    postal_code = Column(String(10), nullable=False)
    phone_number = Column(String(20), nullable=True)


__all__ = ["Branch"]


