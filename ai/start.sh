#!/bin/bash

# Vaani AI Backend Startup Script

echo "🚀 Starting Vaani AI Backend..."

# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "❌ Ollama is not running!"
    echo "Please start Ollama in another terminal:"
    echo "  ollama serve"
    exit 1
fi

echo "✅ Ollama is running"

# Check if models are downloaded
echo "📦 Checking for required models..."

if ! ollama list | grep -q "qwen2.5:7b"; then
    echo "⚠️  Qwen 2.5 7B not found. Downloading..."
    ollama pull qwen2.5:7b
fi

if ! ollama list | grep -q "llama3.2:3b"; then
    echo "⚠️  Llama 3.2 3B not found. Downloading..."
    ollama pull llama3.2:3b
fi

echo "✅ Models ready"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env with your settings"
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🐍 Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  Virtual environment not found. Creating..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Create logs directory
mkdir -p logs

echo "🌟 Starting FastAPI server..."
python main.py
