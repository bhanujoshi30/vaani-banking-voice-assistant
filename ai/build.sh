#!/bin/bash
# Wrapper script that finds and runs vercel-build-ai.sh
set -e

# Try multiple locations
SCRIPT=""
if [ -f "./vercel-build-ai.sh" ]; then
    SCRIPT="./vercel-build-ai.sh"
elif [ -f "../vercel-build-ai.sh" ]; then
    SCRIPT="../vercel-build-ai.sh"
elif [ -f "./ai/vercel-build-ai.sh" ]; then
    SCRIPT="./ai/vercel-build-ai.sh"
else
    # Find it
    SCRIPT=$(find . -name vercel-build-ai.sh -type f | head -1)
fi

if [ -z "$SCRIPT" ] || [ ! -f "$SCRIPT" ]; then
    echo "❌ Error: Could not find vercel-build-ai.sh"
    echo "Current directory: $(pwd)"
    echo "Files in current directory:"
    ls -la
    echo "Looking for script..."
    find . -name "*.sh" -type f
    exit 1
fi

echo "✅ Found script at: $SCRIPT"
bash "$SCRIPT"

