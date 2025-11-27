# Vercel Deployment Checklist - Fix FUNCTION_INVOCATION_FAILED

## Critical Configuration

### 1. Vercel Project Settings

Go to your **AI Backend Vercel project** → **Settings** → **General**:

- ✅ **Framework Preset**: `Other`
- ✅ **Root Directory**: Leave empty (or `/`)
- ✅ **Build Command**: `bash vercel-build-ai.sh`
- ✅ **Output Directory**: `.vercel/output` ⚠️ **CRITICAL**
- ✅ **Install Command**: Leave **EMPTY** (build script handles it)

### 2. Verify vercel-ai.json

**File**: `vercel-ai.json` (root directory)

```json
{
  "version": 2,
  "buildCommand": "bash vercel-build-ai.sh",
  "outputDirectory": ".vercel/output"
}
```

### 3. Build Script Verification

**File**: `vercel-build-ai.sh`

- ✅ Creates `.vercel/output` directory
- ✅ Creates `functions/api/index.func/index.py`
- ✅ Creates `functions/api/index.func/.vc-config.json` with `"handler": "index.app"`
- ✅ Always creates FastAPI app (no MockApp)
- ✅ Type checks ensure app is FastAPI instance

### 4. Entry Point File

**File**: `.vercel/output/functions/api/index.func/index.py` (created by build script)

- ✅ Imports FastAPI at module level
- ✅ Tries to import `from ai.main import app`
- ✅ Falls back to FastAPI app if import fails
- ✅ Type checks: `isinstance(app, FastAPI)`
- ✅ Exports: `__all__ = ["app"]`

## Common Issues

### Issue 1: Build Script Not Running

**Symptoms**: Still getting FUNCTION_INVOCATION_FAILED

**Solution**:
1. Check Vercel build logs - do you see "🔧 AI Backend build script starting..."?
2. If not, Vercel is auto-detecting Python
3. Ensure `outputDirectory` is set in `vercel-ai.json`
4. Remove any `vercel.json` in root that might override settings

### Issue 2: Build Output API Not Used

**Symptoms**: Vercel uses source files instead of `.vercel/output`

**Solution**:
1. Ensure `outputDirectory: ".vercel/output"` is in config
2. Check build logs for "Build Output API structure complete"
3. Verify `.vercel/output` directory exists after build

### Issue 3: Import Errors

**Symptoms**: App imports fail, fallback FastAPI app created

**Solution**:
1. Check build logs for import errors
2. Verify `python/ai/main.py` exists in build output
3. Check that dependencies are installed in `python/` directory

## Verification Steps

### After Deployment:

1. **Check Build Logs**:
   ```
   Look for:
   - "🔧 AI Backend build script starting..."
   - "✅ Build Output API structure complete"
   - "✅ Output directory created: .vercel/output"
   ```

2. **Test Endpoint**:
   ```bash
   curl https://api.tech-tonic-ai.com/health
   ```
   Should return JSON, not 500 error

3. **Check Function Logs**:
   - Go to Vercel Dashboard → Deployment → Logs
   - Look for any Python errors or import failures

## Files Modified

1. ✅ `vercel-ai.json` - Added `outputDirectory`
2. ✅ `vercel-build-ai.sh` - Simplified entry point, type safety
3. ✅ `ai/api/index.py` - Removed MockApp
4. ✅ `api/index.py` - Removed MockApp

## Next Steps

1. ✅ Code fixes complete
2. ⏳ **Commit and push** changes
3. ⏳ **Redeploy** on Vercel
4. ⏳ **Verify** build logs show Build Output API
5. ⏳ **Test** endpoints work

