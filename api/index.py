"""
Vercel serverless function entry point for backend API.
This is the entry point that Vercel will use to serve the FastAPI application.
"""

import sys
import os

# Get the directory where this file is located (the function directory)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add current directory to Python path (where backend code is copied)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import the FastAPI app from backend module
# The backend directory should be in the same directory as this file
try:
    from backend.app import app
except ImportError as e:
    # If import fails, create a diagnostic error app
    from fastapi import FastAPI
    import traceback
    
    error_app = FastAPI(title="Backend Import Error")
    
    @error_app.get("/")
    @error_app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
    async def import_error(path: str = ""):
        import traceback as tb
        return {
            "error": "Failed to import backend.app",
            "message": str(e),
            "current_dir": current_dir,
            "sys_path": sys.path[:5],  # First 5 entries
            "files_in_dir": os.listdir(current_dir) if os.path.exists(current_dir) else "Directory not found",
            "traceback": "".join(tb.format_exception(type(e), e, e.__traceback__))
        }
    
    app = error_app

# Export the app for Vercel
# Vercel's Python runtime will automatically detect and serve the FastAPI app
__all__ = ["app"]

