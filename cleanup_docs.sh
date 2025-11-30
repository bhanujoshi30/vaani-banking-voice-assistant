#!/bin/bash
# Clean up duplicate/unnecessary documentation files

echo "Cleaning up duplicate documentation files..."

# Keep only essential docs, remove duplicates
KEEP_FILES=(
    "README.md"
    "BACKEND_DEPLOYMENT_FIX.md"
    "VERCEL_DASHBOARD_CHANGES.md"
    "DEPLOYMENT_WORKFLOW.md"
)

# Files to remove (duplicates/outdated)
REMOVE_FILES=(
    "DEPLOY_AND_TEST_NOW.md"
    "DEPLOY_NOW.md"
    "DEPLOYMENT_FIX_SUMMARY.md"
    "DEPLOYMENT_FIX.md"
    "DEPLOYMENT_GUIDE.md"
    "FINAL_DEPLOYMENT_FIX.md"
    "VERCEL_AI_BACKEND_FIX.md"
    "VERCEL_AI_PROJECT_SETUP.md"
    "VERCEL_BACKEND_SETUP.md"
    "VERCEL_BUILD_FIX.md"
    "VERCEL_BUILDS_FIXED.md"
    "VERCEL_CONFIG_UPDATE.md"
    "VERCEL_CRITICAL_FIX.md"
    "VERCEL_DEPLOYMENT_CHECKLIST.md"
    "VERCEL_DEPLOYMENT_SIZE_FIX.md"
    "VERCEL_DEPLOYMENT_STEPS.md"
    "VERCEL_DUPLICATE_BUILD_FIX.md"
    "VERCEL_MEMORY_FIX.md"
    "VERCEL_PROJECTS_CONFIG.md"
    "VERCEL_QUICK_REFERENCE.md"
    "VERCEL_RAG_ENABLED.md"
    "VERCEL_SETUP_SUMMARY.md"
    "LOCAL_VS_VERCEL.md"
)

for file in "${REMOVE_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "Removing: $file"
        rm -f "$file"
    fi
done

echo "✅ Cleanup complete"
