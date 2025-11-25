# ⚠️ CRITICAL: Vercel AI Backend Build Not Running

## Problem

The build script `vercel-build-ai.sh` is **NOT running**. Vercel is:
1. Auto-detecting Python
2. Installing from full `requirements.txt` (4.3GB)
3. Ignoring our build script

## Root Cause

Vercel project settings are not configured to use the build script. The `buildCommand` in `vercel-ai.json` is being ignored.

## IMMEDIATE FIX REQUIRED

### Step 1: Go to Vercel Dashboard

1. Open your **AI Backend Vercel project**
2. Go to **Settings** → **General**

### Step 2: Configure Build Settings

**Build & Development Settings**:

1. **Framework Preset**: `Other`
2. **Root Directory**: Leave empty (or `/`)
3. **Build Command**: `bash vercel-build-ai.sh` ⚠️ **MUST SET THIS**
4. **Output Directory**: `.vercel/output` ⚠️ **MUST SET THIS**
5. **Install Command**: Leave **EMPTY** (build script handles it)
6. **Python Version**: `3.12` (or default)

### Step 3: Enable Override (If Available)

If there's an **"Override"** toggle, **enable it** to force Vercel to use your build command instead of auto-detection.

### Step 4: Save and Redeploy

1. **Save** settings
2. **Redeploy** (or push a commit)

## Verify It's Working

After redeploying, check build logs. You should see:

```
🔧 AI Backend build script starting...
📂 Working directory: /vercel/path0
📋 Files in current directory:
📁 Creating Build Output API structure...
✅ Output directory created: .vercel/output
🗑️  Removing ChromaDB vector database files...
```

**If you DON'T see these messages**, the build script still isn't running.

## Alternative: Check Project Configuration

If the above doesn't work:

1. **Check Root Directory**: Make sure it's set to repo root (not `ai/`)
2. **Check Config File**: Vercel might be using root `vercel.json` instead of `vercel-ai.json`
3. **Try Renaming**: Temporarily rename `vercel-ai.json` to `vercel.json` (backup root one first)

## Why This Happens

Vercel has two ways to build:
1. **Auto-detection**: Sees Python files → installs dependencies automatically
2. **Build Output API**: Uses `.vercel/output` directory created by build script

When `buildCommand` isn't properly configured, Vercel defaults to auto-detection, which installs EVERYTHING.

## Expected Result

After fixing:
- ✅ Build script runs first
- ✅ Only minimal dependencies installed (~100-200MB)
- ✅ Only 3 PDFs included
- ✅ Deployment succeeds

