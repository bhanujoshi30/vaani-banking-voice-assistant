"""FastAPI application factory for Vaani backend."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router as api_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Sun National Bank API",
        description="Voice-first banking backend for the Vaani assistant.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)
    return app


app = create_app()


__all__ = ["create_app", "app"]


