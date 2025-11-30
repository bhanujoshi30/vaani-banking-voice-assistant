# Vercel Dashboard Changes Required

## Overview

You have **TWO separate Vercel projects** that need different configurations:

1. **Backend Project** (Banking API) - for `api.sunnationalbank.online` / `api.tech-tonic-ai.com`
2. **AI Project** (AI Backend) - for AI chat functionality

---

## 🔧 Project 1: Backend Project (Banking API)

### Vercel Dashboard Steps:

1. **Go to**: Your Backend Vercel Project → **Settings** → **Build and Deployment**

2. **Framework Settings**:
   - **Framework Preset**: `Other` or `FastAPI` (either works)
   - **Build Command**: 
     - Value: `bash vercel-build.sh`
     - **Override**: ✅ **Turn ON** (blue toggle)
   - **Output Directory**: 
     - Value: Leave empty or `N/A`
     - **Override**: ⚠️ **Turn OFF** (gray toggle)
   - **Install Command**: 
     - Value: `pip install -r requirements.txt` (default)
     - **Override**: ⚠️ **Turn OFF** (gray toggle)
   - **Development Command**: 
     - Value: `None` (default)
     - **Override**: ⚠️ **Turn OFF** (gray toggle)

3. **Root Directory**:
   - **Value**: Leave **EMPTY** (not `ai`, not `backend`, just empty)
   - **Include files outside root**: Can be enabled or disabled

4. **Click "Save"** button

### ✅ Expected Result:
- Build uses `vercel-build.sh` script
- Creates `.vercel/output` structure
- Backend API endpoints work

---

## 🤖 Project 2: AI Project (AI Backend)

### Vercel Dashboard Steps:

1. **Go to**: Your AI Backend Vercel Project → **Settings** → **Build and Deployment**

2. **Framework Settings**:
   - **Framework Preset**: `Other` or `FastAPI` (either works)
   - **Build Command**: 
     - Value: `bash vercel-build-ai.sh`
     - **Override**: ✅ **Turn ON** (blue toggle) ⚠️ **CRITICAL**
   - **Output Directory**: 
     - Value: `.vercel/output`
     - **Override**: ✅ **Turn ON** (blue toggle) ⚠️ **CRITICAL**
   - **Install Command**: 
     - Value: `pip install -r requirements.txt` (default)
     - **Override**: ⚠️ **Turn OFF** (gray toggle) - Let build script handle it
   - **Development Command**: 
     - Value: `None` (default)
     - **Override**: ⚠️ **Turn OFF** (gray toggle)

3. **Root Directory**:
   - **Value**: `ai` ⚠️ **MUST BE SET TO `ai`**
   - **Include files outside root**: Can be enabled or disabled

4. **Click "Save"** button

### ✅ Expected Result:
- Build uses `ai/vercel-build-ai.sh` script (because Root Directory is `ai`)
- Script changes to repo root before building
- Creates `.vercel/output` structure at repo root
- AI backend endpoints work

---

## ⚠️ Critical Settings Summary

### Backend Project:
| Setting | Value | Override |
|---------|-------|----------|
| Build Command | `bash vercel-build.sh` | ✅ ON |
| Output Directory | Empty/N/A | ❌ OFF |
| Root Directory | Empty | - |

### AI Project:
| Setting | Value | Override |
|---------|-------|----------|
| Build Command | `bash vercel-build-ai.sh` | ✅ ON |
| Output Directory | `.vercel/output` | ✅ ON ⚠️ |
| Root Directory | `ai` | - |

---

## 🔍 How to Verify Settings Are Correct

### After Saving:

1. **Go to**: Project → **Deployments** → Latest deployment → **Build Logs**

2. **Look for these messages**:

   **Backend Project** should show:
   ```
   🔧 Backend build script starting...
   ✅ Build output ready for deployment
   ```

   **AI Project** should show:
   ```
   🔧 AI Backend build script starting...
   📂 Working directory: /vercel/path0
   ✅ Output directory created: .vercel/output
   ✅ Build Output API structure complete
   ```

3. **If you DON'T see these messages**:
   - Build script is not running
   - Vercel is auto-detecting Python
   - Check that Override toggles are ON for Build Command and Output Directory

---

## 🐛 Common Issues

### Issue 1: Build Script Not Running

**Symptoms**: Build logs show pip installing everything, no build script messages

**Fix**:
- Ensure **Build Command Override** is **ON** (blue)
- Ensure **Output Directory Override** is **ON** (blue) for AI project
- Check Root Directory is correct (`ai` for AI project, empty for Backend)

### Issue 2: Output Directory Not Found

**Symptoms**: Build fails with "output directory not found"

**Fix**:
- For AI project: Set **Output Directory** to `.vercel/output` with Override **ON**
- For Backend project: Leave Output Directory empty with Override **OFF**

### Issue 3: Wrong Script Running

**Symptoms**: Wrong build script runs or script not found

**Fix**:
- **Backend**: Build Command = `bash vercel-build.sh` (script at repo root)
- **AI**: Build Command = `bash vercel-build-ai.sh` (script in `ai/` directory because Root Directory is `ai`)

---

## 📋 Quick Checklist

### Backend Project:
- [ ] Framework Preset: Other or FastAPI
- [ ] Build Command: `bash vercel-build.sh` (Override: ON)
- [ ] Output Directory: Empty (Override: OFF)
- [ ] Root Directory: Empty
- [ ] Save settings

### AI Project:
- [ ] Framework Preset: Other or FastAPI
- [ ] Build Command: `bash vercel-build-ai.sh` (Override: ON)
- [ ] Output Directory: `.vercel/output` (Override: ON) ⚠️
- [ ] Root Directory: `ai` ⚠️
- [ ] Save settings

---

## 🚀 After Making Changes

1. **Save** settings in Vercel dashboard
2. **Redeploy** both projects (or push a commit to trigger deployment)
3. **Check build logs** to verify scripts are running
4. **Test endpoints**:
   - Backend: `https://api.tech-tonic-ai.com/api/v1/auth/login`
   - AI: `https://your-ai-backend.vercel.app/health`

---

## 📝 Notes

- **Override toggles** are critical - they tell Vercel to use your custom settings instead of auto-detection
- **Output Directory** must be set for AI project to use Build Output API
- **Root Directory** affects where Vercel runs commands from
- Settings in Vercel dashboard **override** `vercel.json` files

