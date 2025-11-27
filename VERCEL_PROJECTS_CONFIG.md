# Vercel Projects Configuration Guide

## Two Separate Vercel Projects

### 1. Backend Project (Banking API)
- **Root Directory**: Empty (repo root)
- **Build Command**: `bash vercel-build.sh`
- **Output Directory**: Not set (N/A)
- **Purpose**: Deploys backend API (`backend/app.py`)

### 2. AI Project (AI Backend)
- **Root Directory**: `ai` (subdirectory)
- **Build Command**: `bash build.sh` ⚠️ **Should use this**
- **Output Directory**: `.vercel/output`
- **Purpose**: Deploys AI backend (`ai/main.py`)

## Critical Configuration for AI Project

Since the AI project has **Root Directory = `ai`**, Vercel runs commands from the `ai/` directory.

### Option 1: Use Wrapper Script (Recommended)
**Build Command**: `bash build.sh`
- Uses `ai/build.sh` wrapper
- Finds `vercel-build-ai.sh` in parent directory
- Changes to repo root before running

### Option 2: Use Relative Path
**Build Command**: `bash ../vercel-build-ai.sh`
- Directly references root script
- Requires script to handle being called from `ai/` directory

### Option 3: Use Script in ai/ Directory
**Build Command**: `bash vercel-build-ai.sh`
- Uses `ai/vercel-build-ai.sh`
- Script must handle repo root context

## Current Issue

The Vercel dashboard shows:
- **Build Command**: `bash vercel-build-ai.sh`
- **Root Directory**: `ai`

This means Vercel looks for `ai/vercel-build-ai.sh`, which exists, but we need to verify it works correctly.

## Recommended Fix

### For AI Project in Vercel Dashboard:

1. **Build Command**: Change to `bash build.sh`
   - This uses the wrapper script that handles path resolution
   
2. **OR** Keep `bash vercel-build-ai.sh` but ensure:
   - `ai/vercel-build-ai.sh` exists and works correctly
   - It changes to repo root before building

3. **Output Directory**: Keep `.vercel/output` ✅

4. **Root Directory**: Keep `ai` ✅

## Verification

After updating settings, check build logs for:
- `🔧 AI Backend build script starting...`
- `📂 Working directory: /vercel/path0` (should be repo root, not ai/)
- `✅ Build Output API structure complete`

