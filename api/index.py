"""
Minimal FastAPI entrypoint for Vercel validation.
This file exists only to satisfy Vercel's pre-build validation.
The actual deployment uses Build Output API structure in .vercel/output/
"""

# This is a placeholder - actual app is deployed via Build Output API
# Vercel will use .vercel/output/functions/api/index.func/index.py instead
try:
    from fastapi import FastAPI
    app = FastAPI()

    @app.get("/")
    def root():
        return {"message": "AI Backend - Using Build Output API"}
except ImportError:
    # FastAPI not available in source - Build Output API will handle actual deployment
    # Create a minimal app object for Vercel validation
    class MockApp:
        pass
    app = MockApp()

