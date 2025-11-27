# Terminal-Based Deployment & Testing Workflow

## 🚀 Quick Start

### Deploy and Test in One Command

```bash
./deploy_and_test.sh
```

This script will:
1. ✅ Build locally (catches errors early)
2. ✅ Deploy to Vercel production
3. ✅ Wait for deployment
4. ✅ Test health, root, and login endpoints
5. ✅ Save deployment URL for future use

### Quick Test (After Deployment)

```bash
# Test last deployment
./quick_test.sh

# Test specific URL
./quick_test.sh https://api.sunnationalbank.online
```

## 📋 Detailed Workflow

### Step 1: Make Code Changes

Edit your code files:
- `backend/app.py`
- `vercel-build.sh`
- etc.

### Step 2: Deploy and Test

```bash
./deploy_and_test.sh
```

**What happens:**
1. Builds locally first (fast feedback)
2. Deploys to Vercel (1-2 minutes)
3. Tests all endpoints automatically
4. Shows results immediately

### Step 3: Iterate

If tests fail:
1. Fix the code
2. Run `./deploy_and_test.sh` again
3. Repeat until all tests pass ✅

### Step 4: Freeze Solution

Once everything works:

```bash
# Commit the working solution
git add .
git commit -m "fix: backend deployment with error handling and logging"
git push
```

## 🔧 Manual Commands

### Deploy Only

```bash
vercel --prod
```

### Test Specific Endpoint

```bash
# Health check
curl https://your-deployment.vercel.app/health

# Login
curl -X POST https://your-deployment.vercel.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john.doe@example.com","password":"SecurePass123!"}'
```

### View Deployment Logs

```bash
vercel logs [deployment-url]
```

### List Recent Deployments

```bash
vercel ls
```

## 📊 Test Results

The `deploy_and_test.sh` script tests:

1. **Health Check** (`/health`)
   - Expected: `200 OK` with `{"status": "healthy"}`

2. **Root Endpoint** (`/`)
   - Expected: `200 OK` with service info

3. **Login Endpoint** (`/api/v1/auth/login`)
   - Expected: `200 OK` with `access_token`

## 🐛 Troubleshooting

### Build Fails Locally

**Error**: Build script fails
**Fix**: Check `vercel-build.sh` for errors, fix and retry

### Deployment Fails

**Error**: Vercel deployment fails
**Fix**: 
```bash
# Check logs
vercel logs [deployment-url]

# Try deploying again
vercel --prod
```

### Tests Fail After Deployment

**Error**: Endpoints return 500 or timeout
**Fix**:
1. Check runtime logs: `vercel logs [deployment-url]`
2. Look for initialization errors
3. Fix code and redeploy

### Vercel CLI Not Logged In

**Error**: "Not logged in"
**Fix**:
```bash
vercel login
```

## 📝 Files Created

- `deploy_and_test.sh` - Main deployment and test script
- `quick_test.sh` - Quick test script for existing deployments
- `.last_deployment_url.txt` - Saves last deployment URL
- `test_backend_deployment.py` - Full Python test suite

## 🎯 Workflow Summary

```
Make Changes → ./deploy_and_test.sh → Check Results → Fix if Needed → Repeat → Commit
```

**Time per iteration**: ~2-3 minutes (vs 5-10 minutes with manual dashboard workflow)

## ✅ Success Criteria

All tests pass when:
- ✅ Health check returns 200
- ✅ Root endpoint returns 200
- ✅ Login returns 200 with access_token
- ✅ No FUNCTION_INVOCATION_FAILED errors
- ✅ Runtime logs show successful initialization

## 🚀 Next Steps After Success

1. **Commit working solution**:
   ```bash
   git add .
   git commit -m "fix: backend deployment working"
   git push
   ```

2. **Update Vercel Dashboard** (one-time):
   - Set Build Command override: ON
   - Set Output Directory: `.vercel/output` (override: ON)
   - Save settings

3. **Future deployments**:
   - Just run `./deploy_and_test.sh` from terminal
   - No need to go to dashboard!

