#!/bin/bash
# Vercel build script for backend
# Uses the Build Output API to ship a single serverless function with trimmed deps

set -euo pipefail

echo "🔧 Backend build script starting..."

OUTPUT_DIR=".vercel/output"
FUNCTION_DIR="$OUTPUT_DIR/functions/api/index.func"
PYTHON_DIR="$FUNCTION_DIR/python"

if [ -f "requirements.txt" ]; then
    echo "📄 Backing up full requirements.txt and swapping in backend-only list..."
    mv requirements.txt requirements.txt.full
    cp requirements-backend.txt requirements.txt
fi

echo "🧹 Cleaning previous build output..."
rm -rf "$OUTPUT_DIR"
mkdir -p "$PYTHON_DIR"

echo "📦 Installing backend dependencies into function bundle..."
python3 -m pip install \
        --no-compile \
        --no-cache-dir \
        -r requirements-backend.txt \
        -t "$PYTHON_DIR"

echo "📁 Copying backend source code into bundle..."
cp -R backend "$PYTHON_DIR/"
find "$PYTHON_DIR/backend" -type d -name '__pycache__' -prune -exec rm -rf {} +
find "$PYTHON_DIR/backend" -type f -name '*.pyc' -delete

echo "📝 Creating serverless function entrypoint..."
cat > "$FUNCTION_DIR/index.py" <<'PYCODE'
import os
import sys

# Add python directory to path - use __file__ for relative path resolution
python_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "python")
if python_dir not in sys.path:
    sys.path.insert(0, python_dir)

from backend.app import app  # noqa: E402  # FastAPI application instance

__all__ = ("app",)
PYCODE

echo "⚙️ Writing function runtime config..."
cat > "$FUNCTION_DIR/.vc-config.json" <<'JSON'
{
    "runtime": "python3.12",
    "handler": "index.app"
}
JSON

echo "🛣️ Generating build output routes config..."
cat > "$OUTPUT_DIR/config.json" <<'JSON'
{
    "version": 3,
    "routes": [
        { "src": "/(.*)", "dest": "api/index" }
    ]
}
JSON

echo "✅ Build output ready for deployment"
