# Backend Deployment Guide

## Quick Start

### Deploy and Test (One Command)

```bash
./deploy.sh
```

This script will:
1. ✅ Verify prerequisites (Vercel CLI, login status)
2. ✅ Build locally (catches errors early)
3. ✅ Deploy to Vercel production
4. ✅ Wait for deployment to be ready
5. ✅ Test all endpoints automatically
6. ✅ Show comprehensive results

## What Gets Tested

- **Health Check** (`/health`) - Should return 200
- **Root Endpoint** (`/`) - Should return 200
- **Login Endpoint** (`/api/v1/auth/login`) - Should return 200 with access_token

## Manual Testing

After deployment, test a specific URL:

```bash
./test_deploy.sh https://your-deployment-url.vercel.app
```

Or use the Python test suite:

```bash
python3 test_backend_deployment.py
```

## Troubleshooting

### Deployment Fails

**Check:**
1. Are you logged in? Run `vercel login`
2. Is the build successful? Check `vercel-build.sh` output
3. Check Vercel dashboard for build logs

### Tests Fail

**Check:**
1. Wait a few more seconds (deployment might still be activating)
2. Check runtime logs: `vercel logs [deployment-url]`
3. Verify environment variables are set in Vercel dashboard

### URL Not Found

The script tries multiple methods to extract the URL. If it fails:
1. Check `vercel ls` for recent deployments
2. Check Vercel dashboard for the deployment URL
3. Manually test with: `./test_deploy.sh [url]`

## Vercel Dashboard Configuration

### Backend Project Settings

1. **Settings** → **Build and Deployment**
2. **Build Command**: `bash vercel-build.sh` (Override: ON)
3. **Output Directory**: `.vercel/output` (Override: ON) ⚠️ **CRITICAL**
4. **Root Directory**: Empty
5. **Save**

## Files

- `deploy.sh` - Main deployment script (use this)
- `vercel-build.sh` - Build script (creates `.vercel/output`)
- `test_deploy.sh` - Quick test script
- `test_backend_deployment.py` - Full Python test suite

## Success Criteria

✅ All tests pass:
- Health check returns 200
- Root endpoint returns 200
- Login returns 200 with token
- No FUNCTION_INVOCATION_FAILED errors

## Next Steps

After successful deployment:
1. Commit the working solution
2. Update Vercel dashboard settings (one-time)
3. Future deployments: Just run `./deploy.sh`

