#!/bin/bash
# Vercel build script for backend
# Ensures requirements-backend.txt is used instead of pyproject.toml

set -e

echo "🔧 Backend build script starting..."

# Temporarily rename pyproject.toml so Vercel uses requirements-backend.txt
if [ -f "pyproject.toml" ]; then
    echo "📦 Temporarily hiding pyproject.toml..."
    mv pyproject.toml pyproject.toml.backup
fi

# Hide uv.lock if it exists
if [ -f "uv.lock" ]; then
    echo "📦 Temporarily hiding uv.lock..."
    mv uv.lock uv.lock.backup
fi

# Backup original requirements.txt (full dependencies for local dev)
if [ -f "requirements.txt" ]; then
    echo "💾 Backing up original requirements.txt..."
    mv requirements.txt requirements.txt.full
fi

# Use minimal backend requirements for Vercel deployment
echo "📋 Using requirements-backend.txt for Vercel deployment..."
cp requirements-backend.txt requirements.txt

echo "✅ Build preparation complete"
echo "📝 Vercel will now use requirements-backend.txt (minimal dependencies) for installation"

