"""Security dependencies and request context helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..db.services.auth import AuthenticatedSession, AuthService
from .dependencies import get_auth_service

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class RequestContext:
    request_id: str
    timestamp: datetime
    locale: str | None = None
    channel: str | None = None
    device_id: str | None = None
    customer_ip: str | None = None


def get_request_context(
    x_request_id: str | None = Header(default=None, alias="X-Request-ID"),
    accept_language: str | None = Header(default=None, alias="Accept-Language"),
    x_device_id: str | None = Header(default=None, alias="X-Device-ID"),
    x_psu_ip_address: str | None = Header(default=None, alias="PSU-IP-Address"),
    x_forwarded_for: str | None = Header(default=None, alias="X-Forwarded-For"),
) -> RequestContext:
    """
    Construct request context metadata according to RBI/IDRBT digital banking guidelines.
    """

    request_id = x_request_id or str(uuid4())
    locale = accept_language or "en-IN"
    customer_ip = x_psu_ip_address or x_forwarded_for

    return RequestContext(
        request_id=request_id,
        timestamp=datetime.now(timezone.utc),
        locale=locale,
        channel="voice-web",
        device_id=x_device_id,
        customer_ip=customer_ip,
    )


def get_current_session(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthenticatedSession:
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header.",
        )

    session = auth_service.validate_token(token=credentials.credentials)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
        )
    return session


RequestContextDep = Depends(get_request_context)
CurrentSessionDep = Depends(get_current_session)

__all__ = ["RequestContextDep", "CurrentSessionDep", "RequestContext"]


