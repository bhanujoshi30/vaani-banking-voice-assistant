#!/bin/bash
# Wrapper script that finds and runs vercel-build-ai.sh from repo root
# This script runs from ai/ directory (Root Directory = ai)
set -e

echo "🔧 AI Build Wrapper starting..."
echo "📂 Current directory: $(pwd)"

# Since Root Directory is set to 'ai', we need to go up to repo root
# Try to find vercel-build-ai.sh in parent directory
SCRIPT=""
if [ -f "../vercel-build-ai.sh" ]; then
    SCRIPT="../vercel-build-ai.sh"
    echo "✅ Found script at: $SCRIPT (parent directory)"
elif [ -f "./vercel-build-ai.sh" ]; then
    SCRIPT="./vercel-build-ai.sh"
    echo "✅ Found script at: $SCRIPT (current directory)"
else
    # Try to find it by going up directories
    CURRENT_DIR=$(pwd)
    PARENT_DIR=$(dirname "$CURRENT_DIR")
    if [ -f "$PARENT_DIR/vercel-build-ai.sh" ]; then
        SCRIPT="$PARENT_DIR/vercel-build-ai.sh"
        echo "✅ Found script at: $SCRIPT (absolute path)"
    else
        echo "❌ Error: Could not find vercel-build-ai.sh"
        echo "Current directory: $CURRENT_DIR"
        echo "Parent directory: $PARENT_DIR"
        echo "Files in current directory:"
        ls -la
        echo "Files in parent directory:"
        ls -la "$PARENT_DIR" 2>/dev/null || echo "Cannot access parent"
        exit 1
    fi
fi

# Change to repo root before running script
REPO_ROOT=$(dirname "$SCRIPT")
echo "📂 Changing to repo root: $REPO_ROOT"
cd "$REPO_ROOT" || exit 1
echo "📂 Now in: $(pwd)"

# Run the build script
echo "🚀 Running build script: $SCRIPT"
bash "$SCRIPT"

