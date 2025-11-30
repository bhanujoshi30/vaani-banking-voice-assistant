# Backend Deployment Guide

## Overview

This document describes the simplified deployment strategy for the backend API on Vercel.

## Architecture

- **Framework**: FastAPI
- **Runtime**: Python 3.12
- **Build System**: Vercel Build Output API v3
- **Entry Point**: `api/index.py`

## File Structure

```
.
├── api/
│   └── index.py          # Vercel serverless function entry point
├── backend/              # Backend source code
│   ├── app.py           # FastAPI application factory
│   ├── api/             # API routes
│   └── db/              # Database models and services
├── vercel-build.sh       # Build script
├── vercel.json          # Vercel configuration (root project)
└── requirements-backend.txt  # Python dependencies
```

## Build Process

1. **Build Script** (`vercel-build.sh`):
   - Installs Python dependencies from `requirements-backend.txt`
   - Copies backend source code to function directory
   - Creates Vercel Build Output API v3 structure
   - Configures Python runtime

2. **Entry Point** (`api/index.py`):
   - Imports the FastAPI app from `backend.app`
   - Exports it for Vercel's Python runtime

3. **Vercel Configuration** (`vercel.json`):
   - Specifies build command: `bash vercel-build.sh`
   - Output directory: `.vercel/output`
   - Routes all requests to `/api` function

## Environment Variables

Required environment variables (set in Vercel Dashboard):

- `CORS_ALLOWED_ORIGINS` - Comma-separated list of allowed origins
- `DATABASE_URL` - PostgreSQL connection string
- `DB_BACKEND` - Database backend (`postgresql`)
- `JWT_SECRET_KEY` - Secret key for JWT tokens
- `OPENAI_ENABLED` - Enable OpenAI integration (`true`/`false`)
- `OPENAI_API_KEY` - OpenAI API key (if enabled)
- `OPENAI_MODEL` - OpenAI model name (e.g., `gpt-3.5-turbo`)
- `VOICE_VERIFICATION_ENABLED` - Enable voice verification (`true`/`false`)
- `AI_BASE_URL` - Base URL for AI backend service

## Deployment Steps

1. **Set Environment Variables** in Vercel Dashboard:
   - Go to Project Settings → Environment Variables
   - Add all required variables listed above

2. **Configure Build Settings**:
   - Framework Preset: `Other` or `FastAPI` (either works)
   - Build Command: `bash vercel-build.sh` (override enabled ✅)
   - Output Directory: `.vercel/output` (override enabled ✅)
   - Install Command: Leave empty (override disabled ❌)

3. **Root Directory Settings**:
   - **Option A (Recommended)**: Leave Root Directory **EMPTY**
     - "Include files outside root directory": Can be enabled or disabled
     - Build Command: `bash vercel-build.sh`
   - **Option B**: Set Root Directory to `backend` (Current Setup)
     - "Include files outside root directory": **MUST be ENABLED** ✅
     - Build Command: `bash vercel-build.sh` (uses `backend/vercel-build.sh` wrapper)
     - The wrapper script automatically navigates to repo root and calls the main build script

3. **Deploy**:
   - Push to your git branch
   - Vercel will automatically build and deploy
   - Or use `vercel --prod` from CLI

## Testing

After deployment, test the health endpoint:

```bash
curl https://your-domain.vercel.app/health
```

Expected response:
```json
{"status": "healthy"}
```

## Troubleshooting

### Build Failures

1. Check build logs in Vercel Dashboard
2. Verify Python version (should be 3.12)
3. Check that all dependencies are in `requirements-backend.txt`

### Runtime Errors

1. Check function logs in Vercel Dashboard
2. Verify environment variables are set correctly
3. Check database connection string format

### CORS Issues

1. Verify `CORS_ALLOWED_ORIGINS` includes your frontend domain
2. Check that origins don't include wildcards (not supported)
3. Ensure CORS middleware is configured in `backend/app.py`

## Notes

- The build script uses `--no-compile` and `--no-cache-dir` to reduce build time
- Python cache files (`__pycache__`, `*.pyc`) are cleaned during build
- The deployment uses Vercel's Build Output API v3 for better control

