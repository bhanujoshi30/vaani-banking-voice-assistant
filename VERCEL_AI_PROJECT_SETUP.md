# Vercel AI Backend Project Setup - CRITICAL

## Problem

The build script isn't running because Vercel is auto-detecting Python and using the wrong configuration file.

## Solution: Configure Vercel Project Settings

Since `vercel-ai.json` exists but Vercel looks for `vercel.json` by default, you have two options:

### Option 1: Rename vercel-ai.json to vercel.json (Recommended)

**In your AI Backend Vercel project:**

1. Go to **Vercel Dashboard** → Your AI Backend Project
2. **Settings** → **General**
3. **Root Directory**: Leave empty (root of repo)
4. **Build & Development Settings**:
   - **Framework Preset**: `Other`
   - **Build Command**: `bash vercel-build-ai.sh`
   - **Output Directory**: Leave empty
   - **Install Command**: Leave empty (handled by build script)
   - **Python Version**: `3.12` (or default)

5. **OR** rename `vercel-ai.json` to `vercel.json` in the repo (but this conflicts with backend)

### Option 2: Use Project Settings Override (Better)

**In Vercel Dashboard:**

1. Go to **Settings** → **General**
2. **Build & Development Settings**:
   - **Override**: Enable "Override" toggle
   - **Build Command**: `bash vercel-build-ai.sh`
   - **Output Directory**: `.vercel/output` (if Build Output API)
   - **Install Command**: Leave empty
   - **Python Version**: `3.12`

3. **Important**: Make sure "Override" is enabled so it uses your build command instead of auto-detection

### Option 3: Use vercel.json with Conditional Logic

Create a single `vercel.json` that detects which project it is, but this is complex.

## Current Issue

The logs show:
- "WARN! Due to `builds` existing..." - but we removed builds
- "Installing required dependencies from requirements.txt" - using full requirements.txt
- No output from our build script

This means:
1. Vercel is using a different config (maybe root vercel.json)
2. OR project settings aren't configured correctly
3. OR buildCommand isn't being recognized

## Fix Steps

1. **Go to Vercel Dashboard** → AI Backend Project
2. **Settings** → **General** → **Build & Development Settings**
3. **Enable "Override"** toggle
4. Set **Build Command**: `bash vercel-build-ai.sh`
5. **Save** settings
6. **Redeploy**

## Verify Build Script Runs

After redeploying, check build logs for:
```
🔧 AI Backend build script starting...
📂 Working directory: ...
📋 Files in current directory: ...
```

If you don't see these messages, the build script isn't running.

## Alternative: Use Build Output API Properly

If the buildCommand still doesn't work, we might need to:
1. Remove buildCommand from vercel-ai.json
2. Configure everything in Vercel dashboard
3. Or use a different approach

