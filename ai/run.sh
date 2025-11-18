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

echo "🌟 Starting server on http://localhost:8001"
python main.py
