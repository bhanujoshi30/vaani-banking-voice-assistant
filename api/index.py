# Vercel Python function entrypoint
# Dependencies are installed by Vercel automatically
import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import FastAPI app
try:
    from backend.app import app
except ImportError as e:
    # If import fails, try adding current directory
    import sys
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    from backend.app import app

