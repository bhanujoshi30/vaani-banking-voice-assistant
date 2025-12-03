# ⚠️ CRITICAL: Update Vercel Project Settings

## Problem
The `builds` section in `vercel.json` was preventing project settings from being used. I've removed it, but you **MUST** configure the project settings manually.

## Steps to Fix:

1. **Go to Vercel Dashboard** → Your Backend Project
2. **Settings** → **General**
3. **Build & Development Settings**:
   - **Framework Preset**: `Other`
   - **Root Directory**: (leave empty or set to root)
   - **Build Command**: Leave empty
   - **Output Directory**: Leave empty  
   - **Install Command**: `pip install -r requirements.txt`
   - **Python Version**: `3.12` (or leave default)

4. **Save** the settings

5. **Redeploy** the project

## Why This Works:

- Without `builds` section, Vercel respects project settings
- `Install Command: pip install -r requirements.txt` will use our minimal requirements
- `requirements.txt` contains only backend dependencies (~50 packages vs 187)
- This reduces deployment size from 4GB+ to ~500MB

## Files:

- ✅ `vercel.json` - Updated to use `functions` format (respects project settings)
- ✅ `requirements.txt` - Minimal backend dependencies
- ✅ `.vercelignore` - Excludes large files

## Next Deployment:

After updating settings, the next deployment should:
1. Use `pip install -r requirements.txt` (from project settings)
2. Install only ~50 packages instead of 187
3. Complete successfully without size errors

