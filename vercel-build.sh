#!/bin/bash
# Vercel build script for backend
# Ensures requirements.txt is used instead of pyproject.toml

set -e

echo "🔧 Backend build script starting..."

# Temporarily rename pyproject.toml so Vercel uses requirements.txt
if [ -f "pyproject.toml" ]; then
    echo "📦 Temporarily hiding pyproject.toml..."
    mv pyproject.toml pyproject.toml.backup
fi

# Hide uv.lock if it exists
if [ -f "uv.lock" ]; then
    echo "📦 Temporarily hiding uv.lock..."
    mv uv.lock uv.lock.backup
fi

# Ensure requirements.txt exists (copy from requirements-backend.txt if needed)
if [ ! -f "requirements.txt" ]; then
    echo "📋 Creating requirements.txt from requirements-backend.txt..."
    cp requirements-backend.txt requirements.txt
fi

echo "✅ Build preparation complete"
echo "📝 Vercel will now use requirements.txt for installation"

