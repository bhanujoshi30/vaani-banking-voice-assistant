#!/bin/bash
# Wrapper script for Vercel build when Root Directory is set to "backend"
# This script runs the build and creates output in backend/.vercel/output

set -euo pipefail

# Get the directory where this script is located (backend/)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "📂 Build context: backend/ directory"
echo "📂 Repo root: $REPO_ROOT"
echo "📂 Backend directory: $SCRIPT_DIR"

# Change to repo root to access files
cd "$REPO_ROOT" || exit 1

# Create output directory in backend/ (where Vercel expects it)
OUTPUT_DIR="backend/.vercel/output"
FUNCTION_DIR="$OUTPUT_DIR/functions/api/index.func"

echo "📦 Creating output directory: $OUTPUT_DIR"
rm -rf "$OUTPUT_DIR"
mkdir -p "$FUNCTION_DIR"

# Install dependencies into function directory
echo "📦 Installing Python dependencies..."
python3 -m pip install \
    --no-compile \
    --no-cache-dir \
    -r requirements-backend.txt \
    -t "$FUNCTION_DIR" \
    --upgrade

# Copy backend source code
echo "📁 Copying backend source code..."
# Create backend directory in function bundle
mkdir -p "$FUNCTION_DIR/backend"
# Copy backend contents, excluding .vercel directory to avoid circular copy
# Copy all Python files and directories from backend, excluding .vercel and __pycache__
for item in backend/* backend/.[!.]*; do
    # Skip if glob didn't match
    [ ! -e "$item" ] && continue
    item_name=$(basename "$item")
    # Skip .vercel, __pycache__, and other unwanted items
    [ "$item_name" = ".vercel" ] && continue
    [ "$item_name" = "__pycache__" ] && continue
    [ "$item_name" = "*.pyc" ] && continue
    echo "  Copying: $item_name"
    cp -r "$item" "$FUNCTION_DIR/backend/" 2>/dev/null || {
        echo "    Warning: Failed to copy $item_name"
    }
done
# Ensure __init__.py exists in backend directory if it's missing
[ ! -f "$FUNCTION_DIR/backend/__init__.py" ] && touch "$FUNCTION_DIR/backend/__init__.py"

# Copy API entry point
echo "📝 Creating API entry point..."
# Copy api/index.py to the function directory root (not into api/ subdirectory)
cp api/index.py "$FUNCTION_DIR/index.py"

# Clean up Python cache files
find "$FUNCTION_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$FUNCTION_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true
find "$FUNCTION_DIR" -type f -name "*.pyo" -delete 2>/dev/null || true
find "$FUNCTION_DIR" -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true
find "$FUNCTION_DIR" -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

# Create function configuration for Vercel
echo "⚙️ Creating function configuration..."
cat > "$FUNCTION_DIR/.vc-config.json" <<'JSON'
{
    "runtime": "python3.12",
    "handler": "index.app"
}
JSON

# Create build output configuration
echo "🛣️ Creating build output configuration..."
cat > "$OUTPUT_DIR/config.json" <<'JSON'
{
    "version": 3,
    "routes": [
        {
            "src": "/(.*)",
            "dest": "/api/index"
        }
    ]
}
JSON

echo "✅ Build complete! Output created at: $OUTPUT_DIR"

