"""
Vercel serverless function entry point for backend API.
This is the entry point that Vercel will use to serve the FastAPI application.
"""

import sys
import os

# Add the function directory to Python path (where backend code is copied)
# In Vercel's build structure, backend will be in the same directory as this file
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import the FastAPI app
from backend.app import app

# Export the app for Vercel
# Vercel's Python runtime will automatically detect and serve the FastAPI app
__all__ = ["app"]

