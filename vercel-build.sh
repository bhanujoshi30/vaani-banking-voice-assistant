#!/bin/bash
# Simplified Vercel build script for backend
# Uses Build Output API v3 with Python runtime

set -euo pipefail

echo "🔧 Backend build starting..."

# Detect if we're running from within backend/ directory (when Root Directory is set to "backend")
# If so, change to repo root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CURRENT_DIR="$(pwd)"

# Check if we're in backend/ directory
if [[ "$(basename "$SCRIPT_DIR")" == "backend" ]] || [[ "$(basename "$CURRENT_DIR")" == "backend" ]]; then
    # We're in backend/ directory, go up to repo root
    if [[ -f "../backend/app.py" ]]; then
        cd .. || exit 1
        echo "📂 Changed to repo root: $(pwd)"
    else
        echo "❌ Error: Cannot find repo root. Current directory: $(pwd)"
        exit 1
    fi
elif [[ -f "backend/app.py" ]]; then
    # We're already at repo root
    echo "📂 Already at repo root: $(pwd)"
else
    # Try to find repo root
    if [[ -f "$SCRIPT_DIR/backend/app.py" ]]; then
        cd "$SCRIPT_DIR" || exit 1
        echo "📂 Changed to script directory (repo root): $(pwd)"
    elif [[ -f "$CURRENT_DIR/backend/app.py" ]]; then
        cd "$CURRENT_DIR" || exit 1
        echo "📂 Using current directory as repo root: $(pwd)"
    else
        echo "❌ Error: Cannot find backend/app.py. Current directory: $(pwd), Script dir: $SCRIPT_DIR"
        exit 1
    fi
fi

OUTPUT_DIR=".vercel/output"
FUNCTION_DIR="$OUTPUT_DIR/functions/api"

# Clean previous build
rm -rf "$OUTPUT_DIR"
mkdir -p "$FUNCTION_DIR"

# Install dependencies into function directory
echo "📦 Installing Python dependencies..."
if [[ ! -f "requirements-backend.txt" ]]; then
    echo "❌ Error: requirements-backend.txt not found in $(pwd)"
    exit 1
fi

python3 -m pip install \
    --no-compile \
    --no-cache-dir \
    -r requirements-backend.txt \
    -t "$FUNCTION_DIR" \
    --upgrade

# Copy backend source code
echo "📁 Copying backend source code..."
if [[ ! -d "backend" ]]; then
    echo "❌ Error: backend/ directory not found in $(pwd)"
    exit 1
fi
cp -r backend "$FUNCTION_DIR/"

# Copy API entry point
echo "📝 Creating API entry point..."
if [[ ! -f "api/index.py" ]]; then
    echo "❌ Error: api/index.py not found in $(pwd)"
    exit 1
fi
mkdir -p "$FUNCTION_DIR/api"
cp api/index.py "$FUNCTION_DIR/api/"

# Clean up Python cache files and unnecessary files
find "$FUNCTION_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$FUNCTION_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true
find "$FUNCTION_DIR" -type f -name "*.pyo" -delete 2>/dev/null || true
find "$FUNCTION_DIR" -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true
find "$FUNCTION_DIR" -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

# Create function configuration for Vercel
echo "⚙️ Creating function configuration..."
cat > "$FUNCTION_DIR/.vc-config.json" <<'JSON'
{
    "runtime": "python3.12"
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
            "dest": "/api"
        }
    ]
}
JSON

echo "✅ Build complete!"
