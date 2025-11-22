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
    # Check if Ollama is running
    if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "❌ Ollama is not running. Please start it first with: ollama serve"
        exit 1
    fi
    
    echo "✅ Ollama is running"
    
    # Check if models are available
    if ! /usr/local/bin/ollama list | grep -q "qwen2.5:7b"; then
        echo "⚠️  Model qwen2.5:7b not found. Download it with:"
        echo "   /usr/local/bin/ollama pull qwen2.5:7b"
        exit 1
    fi
    
    echo "✅ Models available"
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
