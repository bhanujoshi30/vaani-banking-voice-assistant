"""FastAPI application factory for Vaani backend."""

from __future__ import annotations

import logging
import os
import sys
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router as api_router
from .utils.demo_logging import demo_logger


def setup_logging():
    """Configure logging for the application."""
    # Configure root logger to INFO level
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Add console handler with formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Explicitly set INFO level for voice verification loggers
    logging.getLogger("backend.db.services.auth").setLevel(logging.INFO)
    logging.getLogger("backend.db.services.ai_voice_verification").setLevel(logging.INFO)
    logging.getLogger("backend.db.services.voice_verification").setLevel(logging.INFO)
    
    # Reduce noise from other loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

def _build_allowed_origins() -> list[str]:
    """Return the merged list of allowed CORS origins (exact matches only).
    
    Uses sensible defaults for local/production environments and extends them with
    any comma-separated origins specified via the ``CORS_ALLOWED_ORIGINS``
    environment variable.
    """
    default_origins = [
        # Local development
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        # Production domains
        "https://tech-tonic-ai.com",
        "https://www.tech-tonic-ai.com",
        "https://sunnationalbank.online",
        "https://www.sunnationalbank.online",
        "https://test.sunnationalbank.online",
        "https://www.test.sunnationalbank.online",
    ]

    extra_origins = os.getenv("CORS_ALLOWED_ORIGINS", "")
    if extra_origins:
        default_origins.extend(
            origin.strip()
            for origin in extra_origins.split(",")
            if origin.strip() and "*" not in origin.strip()  # Skip wildcards
        )

    # Remove duplicates while preserving order
    seen: set[str] = set()
    merged = []
    for origin in default_origins:
        if origin not in seen:
            merged.append(origin)
            seen.add(origin)
    return merged


def create_app() -> FastAPI:
    # Setup logging first
    setup_logging()
    
    logger = logging.getLogger(__name__)
    logger.info("Logging configured - INFO level enabled for voice verification")
    
    app = FastAPI(
        title="Sun National Bank API",
        description="Voice-first banking backend for the Vaani assistant.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://tech-tonic-ai.com",
            "https://www.tech-tonic-ai.com"
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["Health"])
    async def health_check():
        """Lightweight health probe used by Vercel and external monitors."""
        return {"status": "healthy"}

    @app.get("/", tags=["Health"])
    async def root_status():
        """Default landing route returning a friendly status payload."""
        return {
            "status": "ok",
            "service": "Sun National Bank API",
            "docs": "/docs",
        }
    
    # Add demo logging middleware
    @app.middleware("http")
    async def demo_logging_middleware(request: Request, call_next):
        """Middleware to log API requests/responses for demo"""
        start_time = time.time()
        
        # Log request
        demo_logger.api_request(
            method=request.method,
            path=request.url.path,
            query_params=str(request.query_params) if request.query_params else None,
            client_ip=request.client.host if request.client else None,
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Log response
        demo_logger.api_response(
            status_code=response.status_code,
            duration_ms=duration_ms,
            content_type=response.headers.get("content-type"),
        )
        
        return response

    app.include_router(api_router)
    
    @app.on_event("startup")
    async def startup_event():
        logger.info("Backend application started - voice verification logging enabled")
    
    return app


app = create_app()


__all__ = ["create_app", "app"]


