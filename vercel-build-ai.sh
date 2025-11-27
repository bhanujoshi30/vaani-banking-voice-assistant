#!/bin/bash
# Vercel build script for AI Backend
# Uses Build Output API to control exactly what gets deployed
# Includes limited PDFs for RAG (2 loans + 1 investment)

set -euo pipefail

# Ensure we're in the repo root directory
# Script is at root, but might be called from ai/ directory
SCRIPT_PATH="$0"
if [[ "$SCRIPT_PATH" == ../* ]]; then
    # Called with relative path like ../vercel-build-ai.sh
    # Get absolute path and go to root
    SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
    cd "$SCRIPT_DIR" || exit 1
else
    # Called directly, go to script's directory (root)
    cd "$(dirname "$(readlink -f "$SCRIPT_PATH" 2>/dev/null || echo "$SCRIPT_PATH")")" || exit 1
fi

echo "🔧 AI Backend build script starting..."
echo "📂 Working directory: $(pwd)"
echo "📋 Files in current directory:"
ls -la | head -10

# Remove requirements.txt, pyproject.toml, and main.py IMMEDIATELY to prevent Vercel auto-detection
echo "🔒 Removing Python detection files to prevent Vercel auto-detection..."
rm -f requirements.txt pyproject.toml main.py 2>/dev/null || true

# Create Build Output API structure IMMEDIATELY to tell Vercel we're using Build Output API
OUTPUT_DIR=".vercel/output"
FUNCTION_DIR="$OUTPUT_DIR/functions/api/index.func"
PYTHON_DIR="$FUNCTION_DIR/python"

echo "📁 Creating Build Output API structure..."
mkdir -p "$PYTHON_DIR"
echo "✅ Output directory created: $OUTPUT_DIR"

# Remove ChromaDB files to reduce size (they'll be rebuilt on first use from PDFs)
echo "🗑️  Removing ChromaDB vector database files (will be rebuilt on first use)..."
rm -rf ai/chroma_db/*/data_level*.bin 2>/dev/null || true
rm -rf ai/chroma_db/*/header.bin 2>/dev/null || true
rm -rf ai/chroma_db/*/length.bin 2>/dev/null || true
rm -rf ai/chroma_db/*/link_lists.bin 2>/dev/null || true
find ai/chroma_db -name "*.bin" -delete 2>/dev/null || true
find ai/chroma_db -name "*.sqlite3" -delete 2>/dev/null || true
echo "✅ ChromaDB files removed (will be rebuilt from PDFs on first use)"

# Keep only essential PDFs for RAG (2 loans + 1 investment)
echo "📚 Keeping only essential PDFs for RAG..."
LOAN_PDFS_DIR="backend/documents/loan_products"
INVEST_PDFS_DIR="backend/documents/investment_schemes"

# Keep only 2 loan PDFs: home_loan and personal_loan (most common)
if [ -d "$LOAN_PDFS_DIR" ]; then
    cd "$LOAN_PDFS_DIR"
    # List of PDFs to keep
    KEEP_LOANS=("home_loan_product_guide.pdf" "personal_loan_product_guide.pdf")
    # Remove all PDFs that are not in the keep list
    for pdf in *.pdf; do
        if [ -f "$pdf" ]; then
            KEEP=false
            for keep_pdf in "${KEEP_LOANS[@]}"; do
                if [ "$pdf" = "$keep_pdf" ]; then
                    KEEP=true
                    break
                fi
            done
            if [ "$KEEP" = false ]; then
                rm -f "$pdf" 2>/dev/null || true
            fi
        fi
    done
    cd - > /dev/null
    echo "✅ Kept loan PDFs: home_loan_product_guide.pdf, personal_loan_product_guide.pdf"
fi

# Keep only 1 investment PDF: PPF (most common)
if [ -d "$INVEST_PDFS_DIR" ]; then
    cd "$INVEST_PDFS_DIR"
    # Remove all PDFs except PPF
    for pdf in *.pdf; do
        if [ -f "$pdf" ] && [ "$pdf" != "ppf_scheme_guide.pdf" ]; then
            rm -f "$pdf" 2>/dev/null || true
        fi
    done
    cd - > /dev/null
    echo "✅ Kept investment PDF: ppf_scheme_guide.pdf"
fi

# requirements.txt and pyproject.toml already removed at start of script
# This ensures Vercel doesn't try to auto-detect Python

echo "🧹 Cleaning previous build output (keeping structure)..."
# Don't remove the entire output dir - just clean the python directory
rm -rf "$PYTHON_DIR"/*
mkdir -p "$PYTHON_DIR"

echo "📦 Installing AI backend dependencies into function bundle..."
echo "📋 Installing from: ai/requirements-vercel.txt"
python3 -m pip install \
        --no-compile \
        --no-cache-dir \
        -r ai/requirements-vercel.txt \
        -t "$PYTHON_DIR" 2>&1 | tee /tmp/pip-install.log | head -100
echo "✅ Dependencies installed. Checking size..."
du -sh "$PYTHON_DIR" 2>/dev/null || echo "⚠️  Could not check size"

echo "📁 Copying AI backend source code into bundle..."
# Copy ai directory (this includes ai/__init__.py we created)
cp -R ai "$PYTHON_DIR/"
# Copy backend directory (needed for imports)
cp -R backend "$PYTHON_DIR/" 2>/dev/null || echo "⚠️  Backend directory not found (OK for AI-only deployment)"
# Copy ai_main.py (as fallback)
cp ai_main.py "$PYTHON_DIR/" 2>/dev/null || echo "⚠️  ai_main.py not found (using direct import)"

# Clean up unnecessary files
find "$PYTHON_DIR" -type d -name '__pycache__' -prune -exec rm -rf {} + 2>/dev/null || true
find "$PYTHON_DIR" -type f -name '*.pyc' -delete 2>/dev/null || true
find "$PYTHON_DIR" -type f -name '*.pyo' -delete 2>/dev/null || true

# Remove test files
find "$PYTHON_DIR" -name "test_*.py" -delete 2>/dev/null || true
find "$PYTHON_DIR" -name "*_test.py" -delete 2>/dev/null || true

# Remove ChromaDB files from bundle (they'll be rebuilt)
find "$PYTHON_DIR/ai/chroma_db" -name "*.bin" -delete 2>/dev/null || true
find "$PYTHON_DIR/ai/chroma_db" -name "*.sqlite3" -delete 2>/dev/null || true

# Remove other PDFs from bundle (keep only the 3 we need)
find "$PYTHON_DIR/backend/documents/loan_products" -name "*.pdf" ! -name "home_loan_product_guide.pdf" ! -name "personal_loan_product_guide.pdf" -delete 2>/dev/null || true
find "$PYTHON_DIR/backend/documents/investment_schemes" -name "*.pdf" ! -name "ppf_scheme_guide.pdf" -delete 2>/dev/null || true

echo "📝 Creating serverless function entrypoint..."
cat > "$FUNCTION_DIR/index.py" <<'PYCODE'
"""
Vercel serverless function entrypoint for AI Backend
Simplified approach: Always ensure app is a FastAPI instance
"""
import os
import sys

# CRITICAL: Add python directory to path FIRST (before any imports)
python_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "python")
if python_dir not in sys.path:
    sys.path.insert(0, python_dir)

# Import FastAPI first to ensure it's available for fallback
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Try importing the actual app - if this fails, we'll create a fallback FastAPI app
try:
    # Strategy 1: Try ai_main.py (recommended path)
    try:
        from ai_main import app
        # Verify app is a FastAPI instance
        if not isinstance(app, FastAPI):
            raise TypeError(f"app is not a FastAPI instance, got {type(app)}")
    except (ImportError, TypeError) as e1:
        # Strategy 2: Try direct import from ai.main
        try:
            from ai.main import app
            if not isinstance(app, FastAPI):
                raise TypeError(f"app is not a FastAPI instance, got {type(app)}")
        except (ImportError, TypeError) as e2:
            # Both imports failed - create fallback FastAPI app
            app = FastAPI(title="AI Backend - Import Error")
            
            # Add CORS middleware
            app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_origin_regex=r"https://.*\.vercel\.app",
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
            
            @app.get("/")
            @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
            async def error_handler(path: str = ""):
                return {
                    "error": "Failed to import application",
                    "path": path,
                    "python_dir": python_dir,
                    "import_error_1": str(e1),
                    "import_error_2": str(e2)
                }
except Exception as e:
    # Ultimate fallback - ensure we ALWAYS have a FastAPI app
    app = FastAPI(title="AI Backend - Critical Error")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_origin_regex=r"https://.*\.vercel\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    @app.get("/")
    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
    async def critical_error(path: str = ""):
        return {
            "error": "Critical initialization error",
            "exception": str(e)
        }

# Ensure app is always a FastAPI instance (safety check)
if not isinstance(app, FastAPI):
    # This should never happen, but if it does, create a new FastAPI app
    app = FastAPI(title="AI Backend - Type Error")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_origin_regex=r"https://.*\.vercel\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    @app.get("/")
    async def type_error():
        return {"error": "App type error - app was not a FastAPI instance"}

# Export app - Vercel expects this at module level
__all__ = ["app"]
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
echo "   RAG enabled with: 2 loan PDFs + 1 investment PDF"
echo "   Vector store will be built on first use using OpenAI embeddings"
echo "   Bundle size: $(du -sh "$OUTPUT_DIR" | cut -f1)"

# Ensure Build Output API is properly recognized
# Vercel should use ONLY .vercel/output and not try to build source files
echo "✅ Build Output API structure complete"
echo "   Vercel should use .vercel/output only (no additional builds needed)"
