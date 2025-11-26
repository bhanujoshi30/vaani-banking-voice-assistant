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
"""
Vercel serverless function entrypoint for AI Backend
This file is executed when Vercel invokes the function.
"""
import os
import sys
import traceback
import importlib.util

# CRITICAL: Log to stderr immediately - Vercel captures stderr
def _log_error(msg):
    """Log error to stderr - Vercel will capture this"""
    try:
        print(f"[ENTRYPOINT ERROR] {msg}", file=sys.stderr, flush=True)
    except:
        pass

def _log_info(msg):
    """Log info to stdout - Vercel will capture this"""
    try:
        print(f"[ENTRYPOINT INFO] {msg}", file=sys.stdout, flush=True)
    except:
        pass

# Log startup
_log_info("Starting AI Backend entrypoint...")

# CRITICAL: Set up error handling FIRST, before any imports
# This ensures we can catch errors even if imports fail
_script_dir = os.path.dirname(os.path.abspath(__file__))
_python_dir = os.path.join(_script_dir, "python")
_import_errors = []

_log_info(f"Script dir: {_script_dir}")
_log_info(f"Python dir: {_python_dir}")
_log_info(f"Python dir exists: {os.path.exists(_python_dir)}")

# Function to create error app
def _create_error_app(error_msg, error_type=None, traceback_str=None, additional_info=None):
    """Create a FastAPI app that returns error information"""
    _log_error(f"Creating error app: {error_msg} (type: {error_type})")
    try:
        from fastapi import FastAPI
        _log_info("FastAPI imported successfully")
        app = FastAPI(title="AI Backend - Error")
        
        error_data = {
            "error": error_msg,
            "error_type": error_type or "Unknown",
            "python_dir": _python_dir,
            "python_dir_exists": os.path.exists(_python_dir),
            "script_dir": _script_dir,
            "current_dir": os.getcwd(),
            "sys_path": sys.path[:10] if sys.path else []
        }
        
        if traceback_str:
            error_data["traceback"] = traceback_str
            _log_error(f"Traceback: {traceback_str}")
        if additional_info:
            error_data.update(additional_info)
            _log_error(f"Additional info: {additional_info}")
        
        @app.get("/")
        @app.post("/")
        @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
        def error_handler(path: str = ""):
            _log_info(f"Error handler called for path: {path}")
            return error_data
        
        _log_info("Error app created successfully")
        return app
    except Exception as e:
        _log_error(f"Failed to create FastAPI error app: {e}")
        _log_error(traceback.format_exc())
        # If FastAPI import fails, create minimal WSGI app
        def app(environ, start_response):
            status = '500 Internal Server Error'
            headers = [('Content-type', 'application/json')]
            import json
            error_data = {"error": error_msg, "error_type": error_type or "Unknown"}
            body = json.dumps(error_data).encode('utf-8')
            start_response(status, headers)
            return [body]
        return app

# Check if python_dir exists
if not os.path.exists(_python_dir):
    _log_error(f"Python directory not found: {_python_dir}")
    app = _create_error_app(
        "Python directory not found",
        "DirectoryNotFound",
        additional_info={"python_dir": _python_dir}
    )
else:
    _log_info("Python directory exists, proceeding with imports...")
    # Add python_dir to sys.path
    if _python_dir not in sys.path:
        sys.path.insert(0, _python_dir)
        _log_info(f"Added {_python_dir} to sys.path")
    
    _log_info(f"sys.path: {sys.path[:5]}")
    
    # Try to import the app using multiple strategies
    app = None
    
    # Strategy 1: Try importing ai.main directly
    _log_info("Strategy 1: Attempting direct import of ai.main...")
    try:
        import ai.main
        _log_info("Successfully imported ai.main module")
        app = ai.main.app
        _log_info(f"Got app from ai.main: {type(app)}")
        _import_errors.append("SUCCESS: Imported from ai.main")
    except SystemExit as e:
        # SystemExit means Python tried to exit - catch it!
        _log_error(f"SystemExit during import: {e}")
        error_tb = traceback.format_exc()
        _log_error(error_tb)
        app = _create_error_app(
            f"SystemExit during import: {e}",
            "SystemExit",
            error_tb,
            {"exit_code": e.code if hasattr(e, 'code') else None}
        )
    except KeyboardInterrupt:
        # Keyboard interrupt - shouldn't happen but catch it
        _log_error("KeyboardInterrupt during import")
        error_tb = traceback.format_exc()
        _log_error(error_tb)
        app = _create_error_app(
            "KeyboardInterrupt during import",
            "KeyboardInterrupt",
            error_tb
        )
    except BaseException as e:
        # Catch ALL exceptions including SystemExit, KeyboardInterrupt, etc.
        _log_error(f"ai.main import failed: {type(e).__name__}: {str(e)}")
        error_tb = traceback.format_exc()
        _log_error(error_tb)
        _import_errors.append(f"ai.main import failed: {type(e).__name__}: {str(e)}")
        
        # Strategy 2: Try importing ai_main.py
        _log_info("Strategy 2: Attempting import of ai_main...")
        try:
            import ai_main
            _log_info("Successfully imported ai_main module")
            app = ai_main.app
            _log_info(f"Got app from ai_main: {type(app)}")
            _import_errors.append("SUCCESS: Imported from ai_main (fallback)")
        except BaseException as e2:
            _log_error(f"ai_main import failed: {type(e2).__name__}: {str(e2)}")
            _log_error(traceback.format_exc())
            _import_errors.append(f"ai_main import failed: {type(e2).__name__}: {str(e2)}")
            
            # Strategy 3: Try using importlib to load module more safely
            try:
                ai_main_path = os.path.join(_python_dir, "ai_main.py")
                if os.path.exists(ai_main_path):
                    spec = importlib.util.spec_from_file_location("ai_main", ai_main_path)
                    if spec and spec.loader:
                        ai_main_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(ai_main_module)
                        app = ai_main_module.app
                        _import_errors.append("SUCCESS: Imported via importlib")
                    else:
                        raise ImportError("Could not create module spec")
                else:
                    raise ImportError("ai_main.py not found")
            except BaseException as e3:
                _import_errors.append(f"importlib import failed: {type(e3).__name__}: {str(e3)}")
                
                # Strategy 4: Try importing ai.main using importlib with proper package setup
                try:
                    ai_main_path = os.path.join(_python_dir, "ai", "main.py")
                    ai_init_path = os.path.join(_python_dir, "ai", "__init__.py")
                    if os.path.exists(ai_main_path):
                        # First, set up the ai package if it doesn't exist
                        if 'ai' not in sys.modules:
                            # Create ai package
                            ai_pkg = type(sys)('ai')
                            ai_pkg.__path__ = [os.path.join(_python_dir, "ai")]
                            sys.modules['ai'] = ai_pkg
                        
                        # Now load ai.main
                        spec = importlib.util.spec_from_file_location("ai.main", ai_main_path)
                        if spec and spec.loader:
                            ai_main_module = importlib.util.module_from_spec(spec)
                            sys.modules['ai.main'] = ai_main_module
                            spec.loader.exec_module(ai_main_module)
                            app = ai_main_module.app
                            _import_errors.append("SUCCESS: Imported ai.main via importlib")
                        else:
                            raise ImportError("Could not create module spec for ai.main")
                    else:
                        raise ImportError(f"ai/main.py not found at {ai_main_path}")
                except BaseException as e4:
                    _import_errors.append(f"ai.main importlib import failed: {type(e4).__name__}: {str(e4)}")
                    
                    # All strategies failed - create error app
                    app = _create_error_app(
                        "Failed to import main application",
                        type(e).__name__,
                        error_tb,
                        {
                            "primary_error": str(e),
                            "all_import_attempts": _import_errors,
                            "files_checked": {
                                "ai_main.py": os.path.exists(os.path.join(_python_dir, "ai_main.py")),
                                "ai/main.py": os.path.exists(os.path.join(_python_dir, "ai", "main.py")),
                                "python_dir": os.path.exists(_python_dir)
                            }
                        }
                    )

# Ensure app is defined and valid
_log_info("Validating app object...")
if app is None:
    _log_error("App is None after all import attempts")
    app = _create_error_app(
        "Critical: App is None after all import attempts",
        "AppNotDefined",
        additional_info={"import_attempts": _import_errors}
    )
else:
    _log_info(f"App object exists: {type(app)}")
    # Verify app is a valid FastAPI app
    try:
        # Check if app has the expected FastAPI attributes
        has_router = hasattr(app, 'router')
        has_call = hasattr(app, '__call__')
        _log_info(f"App has router: {has_router}, has __call__: {has_call}")
        
        if not has_router and not has_call:
            # App might not be a valid FastAPI app
            _log_error("App imported but not a valid FastAPI application")
            app = _create_error_app(
                "App imported but not a valid FastAPI application",
                "InvalidApp",
                additional_info={
                    "app_type": str(type(app)),
                    "app_attrs": [attr for attr in dir(app) if not attr.startswith('_')][:10],
                    "import_attempts": _import_errors
                }
            )
        else:
            _log_info("App validation passed - ready to serve")
    except Exception as e:
        # If checking app fails, create error app
        _log_error(f"Error validating app: {e}")
        _log_error(traceback.format_exc())
        app = _create_error_app(
            f"Error validating app: {e}",
            "AppValidationError",
            additional_info={"import_attempts": _import_errors}
        )

_log_info("Entrypoint initialization complete")

# Final safety check - ensure app is always defined
try:
    if 'app' not in locals() or app is None:
        _log_error("CRITICAL: App not defined after all attempts")
        app = _create_error_app(
            "Critical: App not defined",
            "AppNotDefined",
            additional_info={"import_attempts": _import_errors}
        )
except Exception as e:
    _log_error(f"CRITICAL: Exception in final check: {e}")
    _log_error(traceback.format_exc())
    # Last resort - create minimal app
    try:
        from fastapi import FastAPI
        app = FastAPI()
        @app.get("/")
        def error():
            return {"error": "Critical initialization error", "details": str(e)}
    except:
        def app(environ, start_response):
            start_response('500 Internal Server Error', [('Content-type', 'application/json')])
            return [b'{"error":"Critical initialization failure"}']

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
