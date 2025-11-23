"""
Entry point for Vercel deployment.
For local development, use: python -m uvicorn backend.app:app --reload
"""

import logging
import uvicorn

from backend.app import app

# Configure logging for Vercel
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Export app for Vercel
# Vercel will use this app object directly
__all__ = ["app"]


def main():
    """Local development entry point."""
    # Configure uvicorn logging
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["default"]["fmt"] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    uvicorn.run(
        "backend.app:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"  # Set uvicorn log level to info
    )


if __name__ == "__main__":
    main()
