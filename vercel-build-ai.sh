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
        --no-deps \
        --no-compile \
        --no-cache-dir \
        -r ai/requirements-vercel.txt \
        -t "$PYTHON_DIR" 2>&1 | tee /tmp/pip-install.log | head -100
echo "✅ Dependencies installed. Checking size..."
du -sh "$PYTHON_DIR" 2>/dev/null || echo "⚠️  Could not check size"

echo "📁 Copying AI backend source code into bundle..."
# Copy ai directory
cp -R ai "$PYTHON_DIR/"
# Copy backend directory (needed for imports)
cp -R backend "$PYTHON_DIR/"
# Copy ai_main.py
cp ai_main.py "$PYTHON_DIR/"

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
import os
import sys
import traceback

# Print to stderr (always visible in Vercel logs)
# Also print to stdout as backup
def log_error(msg):
    msg_str = f"[ENTRYPOINT ERROR] {msg}"
    print(msg_str, file=sys.stderr, flush=True)
    print(msg_str, file=sys.stdout, flush=True)

# Log immediately
log_error("=== ENTRYPOINT STARTING ===")
log_error(f"Python version: {sys.version}")
log_error(f"Python executable: {sys.executable}")
log_error(f"Current directory: {os.getcwd()}")
log_error(f"__file__: {__file__}")

try:
    # Add python directory to path (contains all dependencies and code)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    python_dir = os.path.join(script_dir, "python")
    python_dir = os.path.abspath(python_dir)
    
    log_error(f"Script dir: {script_dir}")
    log_error(f"Python dir: {python_dir}")
    log_error(f"Python dir exists: {os.path.exists(python_dir)}")
    
    if python_dir not in sys.path:
        sys.path.insert(0, python_dir)
        log_error(f"Added {python_dir} to sys.path")
    
    log_error(f"sys.path[0]: {sys.path[0]}")
    log_error(f"sys.path length: {len(sys.path)}")
    
    if os.path.exists(python_dir):
        try:
            contents = os.listdir(python_dir)[:15]
            log_error(f"Contents of python_dir: {contents}")
        except Exception as e:
            log_error(f"Could not list python_dir: {e}")
            log_error(traceback.format_exc())
    
    # Check if ai directory exists
    ai_dir = os.path.join(python_dir, "ai")
    log_error(f"AI dir: {ai_dir}")
    log_error(f"AI dir exists: {os.path.exists(ai_dir)}")
    if os.path.exists(ai_dir):
        try:
            contents = os.listdir(ai_dir)[:15]
            log_error(f"Contents of ai dir: {contents}")
        except Exception as e:
            log_error(f"Could not list ai_dir: {e}")
            log_error(traceback.format_exc())
    
    # Check if config.py exists
    config_file = os.path.join(ai_dir, "config.py")
    log_error(f"Config file: {config_file}")
    log_error(f"Config file exists: {os.path.exists(config_file)}")
    
    # Import app directly from ai.main
    # ai/main.py is at python/ai/main.py, backend is at python/backend/
    log_error("=== Attempting to import from ai.main ===")
    
    # Try importing config first to see if that's the issue
    try:
        log_error("Testing config import...")
        from ai import config
        log_error(f"Config imported successfully: {config}")
        log_error(f"Config settings: {hasattr(config, 'settings')}")
        if hasattr(config, 'settings'):
            log_error(f"Settings object: {config.settings}")
    except Exception as config_error:
        log_error(f"Config import failed: {config_error}")
        log_error(f"Config error type: {type(config_error).__name__}")
        log_error(f"Config traceback:\n{traceback.format_exc()}")
        raise
    
    # Now try importing main
    from ai.main import app
    log_error("=== Successfully imported app from ai.main ===")
    log_error(f"App object: {app}")
    log_error(f"App type: {type(app)}")
    
except Exception as e:
    # Log the full error for debugging
    log_error("=== IMPORT FAILED ===")
    log_error(f"Error: {e}")
    log_error(f"Exception type: {type(e).__name__}")
    log_error(f"Full traceback:\n{traceback.format_exc()}")
    
    # Try fallback to ai_main
    try:
        log_error("=== Attempting fallback import from ai_main ===")
        from ai_main import app
        log_error("=== Successfully imported app from ai_main ===")
    except Exception as e2:
        log_error(f"Fallback import also failed: {e2}")
        log_error(f"Fallback error type: {type(e2).__name__}")
        log_error(f"Fallback traceback:\n{traceback.format_exc()}")
        # Re-raise the original error with more context
        raise RuntimeError(f"Failed to import app: {e}") from e

log_error("=== ENTRYPOINT COMPLETE ===")
__all__ = ("app",)
PYCODE

echo "⚙️ Writing function runtime config..."
cat > "$FUNCTION_DIR/.vc-config.json" <<'JSON'
{
    "runtime": "python3.11",
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
