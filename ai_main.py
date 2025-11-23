"""
Entry point for AI Backend on Vercel
Deploys the AI backend FastAPI application
"""

import sys
from pathlib import Path

# Add ai directory to path
ai_path = Path(__file__).parent / "ai"
sys.path.insert(0, str(ai_path))

# Import the app from ai/main.py
from ai.main import app

# Export app for Vercel
__all__ = ["app"]

