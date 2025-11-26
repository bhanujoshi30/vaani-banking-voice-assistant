# Vercel Duplicate Build Issue - Root Cause & Fix

## Root Cause Identified ✅

The build script is running successfully and creating `.vercel/output` (~102MB), but **Vercel is STILL auto-detecting Python** and trying to build source files AFTER the Build Output API completes.

### The Problem

1. ✅ Build script runs: Creates `.vercel/output` with optimized bundle
2. ❌ Vercel THEN scans source files: Sees `requirements.txt` and `pyproject.toml`
3. ❌ Vercel auto-detects Python: Tries to install from `requirements.txt` (full version)
4. ❌ Result: 4.3GB deployment (fails)

### Why This Happens

Vercel processes files in this order:
1. Clones repo
2. Applies `.vercelignore` (removes ignored files)
3. **Scans for Python files** (if `requirements.txt` or `pyproject.toml` exists)
4. Runs `buildCommand` (our script)
5. **BUT**: If Python was detected in step 3, Vercel STILL tries to build

The issue is that `requirements.txt` exists at the root, so Vercel detects Python BEFORE our build script runs.

## Solution Applied

### 1. Updated Root `.vercelignore` ✅

Added `requirements.txt` to root `.vercelignore`:
```
requirements.txt
```

This prevents Vercel from seeing `requirements.txt` when scanning for Python projects.

### 2. Updated `ai/.vercelignore` ✅

Added Python detection files:
```
requirements.txt
pyproject.toml
uv.lock
../requirements.txt
../pyproject.toml
```

This ensures that when deploying from `ai/` directory, these files are excluded.

### 3. Build Script Removes Files ✅

The build script now removes `requirements.txt` and `pyproject.toml` at the START:
```bash
rm -f requirements.txt pyproject.toml 2>/dev/null || true
```

## Expected Behavior After Fix

1. ✅ Vercel clones repo
2. ✅ `.vercelignore` removes `requirements.txt` and `pyproject.toml`
3. ✅ Vercel doesn't detect Python (no `requirements.txt`)
4. ✅ Build script runs
5. ✅ Creates `.vercel/output` (~100-200MB)
6. ✅ Vercel uses Build Output API ONLY
7. ✅ Deployment succeeds

## Next Deployment

After pushing these changes:
- `requirements.txt` will be excluded by `.vercelignore`
- Vercel won't auto-detect Python
- Only Build Output API will be used
- Deployment should succeed

## Verification

Check build logs - you should see:
```
🔒 Removing Python detection files...
📁 Creating Build Output API structure...
✅ Build output ready for deployment
```

And you should **NOT** see:
```
Installing required dependencies from requirements.txt...
```

If you still see that, Vercel is still auto-detecting Python.

