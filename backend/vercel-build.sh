#!/bin/bash
# Wrapper script for Vercel build when Root Directory is set to "backend"
# This script calls the root-level vercel-build.sh script

set -euo pipefail

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Go to repo root (one level up from backend/)
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT" || exit 1

echo "📂 Changed to repo root: $(pwd)"
echo "🔧 Calling root-level vercel-build.sh..."

# Call the root-level build script
bash "$REPO_ROOT/vercel-build.sh"

