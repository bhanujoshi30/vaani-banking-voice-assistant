#!/bin/bash
# Quick start script for AI backend

cd "$(dirname "$0")"

echo "🚀 Starting Vaani AI Backend..."

# Check LLM provider from .env
if [ -f .env ]; then
    LLM_PROVIDER=$(grep "^LLM_PROVIDER=" .env | cut -d '=' -f2 | tr -d ' ')
else
    LLM_PROVIDER="ollama"
fi

echo "📡 LLM Provider: ${LLM_PROVIDER}"

# Only check Ollama if using it as provider
if [ "${LLM_PROVIDER}" = "ollama" ]; then
    DOKKU_HOST_IP=""
    if [ -f /proc/net/route ]; then
        DOKKU_HOST_IP=$(awk '($1 == "00000000" && $3 != "00000000") {
            hex = $3
            a = "0x" substr(hex, 7, 2)
            b = "0x" substr(hex, 5, 2)
            c = "0x" substr(hex, 3, 2)
            d = "0x" substr(hex, 1, 2)
            printf "%d.%d.%d.%d\n", a, b, c, d
        }' /proc/net/route)
    fi

    # Also set OLLAMA_HOST for the ollama CLI tool, prioritizing existing env var, then discovered IP, then localhost.
    export OLLAMA_HOST=${OLLAMA_HOST:-${DOKKU_HOST_IP:-127.0.0.1}}
    
    # Prefer a configured OLLAMA_BASE_URL, fall back to discovered host IP, then finally localhost.
    OLLAMA_BASE_URL=${OLLAMA_BASE_URL:-http://${DOKKU_HOST_IP:-127.0.0.1}:11434}
    echo "📡 Checking Ollama at ${OLLAMA_BASE_URL}"

    ok=2
    # Try Python (available in most images you use via dokku run); fall back to curl if present.
    if command -v python3 >/dev/null 2>&1; then
        python3 - <<'PY' "${OLLAMA_BASE_URL}"
import sys, urllib.request
url = sys.argv[1].rstrip('/') + "/api/tags"
try:
    urllib.request.urlopen(url, timeout=3)
    sys.exit(0)
except Exception:
    sys.exit(1)
PY
        ok=$?
    elif command -v curl >/dev/null 2>&1; then
        curl -fsS "${OLLAMA_BASE_URL}/api/tags" >/dev/null 2>&1
        ok=$?
    else
        # Neither python3 nor curl present; leave ok=2 to indicate unknown
        ok=2
    fi

    if [ "$ok" -eq 0 ]; then
        echo "✅ Ollama reachable at ${OLLAMA_BASE_URL}"
    else
        echo "⚠️ Ollama not reachable at ${OLLAMA_BASE_URL}"
        if [ "${STRICT_OLLAMA_CHECK:-0}" = "1" ]; then
            echo "Exiting because STRICT_OLLAMA_CHECK=1"
            exit 1
        else
            echo "Continuing startup without Ollama (runtime calls may fail)"
        fi
    fi

    # prefer explicit OLLAMA_CLI, otherwise detect from PATH
    OLLAMA_CLI=${OLLAMA_CLI:-$(command -v ollama || true)}
    if [ -n "$OLLAMA_CLI" ] && [ -x "$OLLAMA_CLI" ]; then
        OLLAMA_MODEL=${OLLAMA_MODEL:-qwen2.5:7b}
        if ! "$OLLAMA_CLI" list 2>/dev/null | grep -q "$OLLAMA_MODEL"; then
            echo "⚠️ Model ${OLLAMA_MODEL} not found. To pull: $OLLAMA_CLI pull ${OLLAMA_MODEL}"
            if [ "${STRICT_OLLAMA_CHECK:-0}" = "1" ]; then
                echo "Exiting because STRICT_OLLAMA_CHECK=1 and model missing"
                exit 1
            else
                echo "Continuing without the model (development mode)"
            fi
        else
            echo "✅ Models available (via ${OLLAMA_CLI})"
        fi
    else
        echo "⚠️ ollama CLI not found; skipping model check."
    fi

    if [ "$ok" -eq 0 ]; then
        echo "✅ Ollama reachable at ${OLLAMA_BASE_URL}"
    else
        echo "⚠️ Ollama not reachable at ${OLLAMA_BASE_URL}"
        if [ "${STRICT_OLLAMA_CHECK:-0}" = "1" ]; then
            echo "Exiting because STRICT_OLLAMA_CHECK=1"
            exit 1
        else
            echo "Continuing startup without Ollama (runtime calls may fail)"
        fi
    fi

    # prefer explicit OLLAMA_CLI, otherwise detect from PATH
    OLLAMA_CLI=${OLLAMA_CLI:-$(command -v ollama || true)}
    if [ -n "$OLLAMA_CLI" ] && [ -x "$OLLAMA_CLI" ]; then
        if ! "$OLLAMA_CLI" list 2>/dev/null | grep -q "qwen2.5:7b"; then
            echo "⚠️ Model qwen2.5:7b not found. To pull: $OLLAMA_CLI pull qwen2.5:7b"
            [ "${STRICT_OLLAMA_CHECK:-0}" = "1" ] && exit 1 || true
        else
            echo "✅ Models available (via ollama CLI)"
        fi
    else
        echo "⚠️ ollama CLI not found; skipping model check."
    fi

elif [ "${LLM_PROVIDER}" = "openai" ]; then
    # Check if OpenAI API key is set
    if ! grep -q "^OPENAI_API_KEY=sk-" .env 2>/dev/null; then
        echo "⚠️  OpenAI API key not found in .env"
        echo "   Add your OpenAI API key to .env file:"
        echo "   OPENAI_API_KEY=sk-your-key-here"
        exit 1
    fi
    echo "✅ OpenAI API key configured"
else
    echo "❌ Unknown LLM_PROVIDER: ${LLM_PROVIDER}"
    echo "   Valid options: ollama, openai"
    exit 1
fi

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
fi

# Create logs directory
mkdir -p logs

# Check if vector databases exist, suggest ingestion if not
echo "🔍 Checking vector databases..."
VDB_ENGLISH_LOANS="./chroma_db/loan_products"
VDB_ENGLISH_INVEST="./chroma_db/investment_schemes"
VDB_HINDI_LOANS="./chroma_db/loan_products_hindi"
VDB_HINDI_INVEST="./chroma_db/investment_schemes_hindi"

MISSING_DBS=0

if [ ! -d "$VDB_ENGLISH_LOANS" ] || [ -z "$(ls -A $VDB_ENGLISH_LOANS 2>/dev/null)" ]; then
    echo "⚠️  English loan vector database not found"
    MISSING_DBS=$((MISSING_DBS + 1))
fi

if [ ! -d "$VDB_ENGLISH_INVEST" ] || [ -z "$(ls -A $VDB_ENGLISH_INVEST 2>/dev/null)" ]; then
    echo "⚠️  English investment vector database not found"
    MISSING_DBS=$((MISSING_DBS + 1))
fi

if [ ! -d "$VDB_HINDI_LOANS" ] || [ -z "$(ls -A $VDB_HINDI_LOANS 2>/dev/null)" ]; then
    echo "⚠️  Hindi loan vector database not found"
    MISSING_DBS=$((MISSING_DBS + 1))
fi

if [ ! -d "$VDB_HINDI_INVEST" ] || [ -z "$(ls -A $VDB_HINDI_INVEST 2>/dev/null)" ]; then
    echo "⚠️  Hindi investment vector database not found"
    MISSING_DBS=$((MISSING_DBS + 1))
fi

if [ $MISSING_DBS -gt 0 ]; then
    echo ""
    echo "💡 Note: Vector databases will be created automatically on first use."
    echo "   To pre-create them, run:"
    echo "   - python ingest_documents_english.py (for English loans & investments)"
    echo "   - python ingest_documents_hindi.py (for Hindi loans & investments)"
    echo ""
else
    echo "✅ All vector databases found"
fi

echo "🌟 Starting server on http://localhost:8001"
python main.py
