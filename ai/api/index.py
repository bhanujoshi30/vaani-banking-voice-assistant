"""
Minimal FastAPI entrypoint for Vercel validation.
This file exists only to satisfy Vercel's pre-build validation.
The actual deployment uses Build Output API structure in .vercel/output/
"""

# ALWAYS create a proper FastAPI app - never use MockApp
# If Build Output API is used, this won't be executed, but if Vercel falls back
# to this file, we need a real FastAPI app
import sys
from pathlib import Path

# Try to import the real app
try:
    # Add parent directory to path
    ai_path = Path(__file__).parent.parent
    if str(ai_path) not in sys.path:
        sys.path.insert(0, str(ai_path))
    
    # Try importing from ai/main.py
    from ai.main import app
except Exception:
    # If import fails, create a minimal FastAPI app (never MockApp)
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        
        app = FastAPI(title="AI Backend - Fallback")
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_origin_regex=r"https://.*\.vercel\.app",
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @app.get("/")
        async def root():
            return {"message": "AI Backend - Using fallback entrypoint", "note": "Build Output API should be used"}
    except ImportError:
        # Last resort - import FastAPI from installed packages
        # This should never happen if dependencies are installed
        raise ImportError("FastAPI is required but not installed. Please ensure dependencies are installed.")

__all__ = ["app"]

