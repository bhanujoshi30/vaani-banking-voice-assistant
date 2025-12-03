# Step-by-Step Vercel Deployment Guide

Complete guide to deploy Frontend and Backend on Vercel.

---

## 📋 Prerequisites

- ✅ GitHub repository: `bhanujoshi30/vaani-banking-voice-assistant`
- ✅ Two Vercel projects already created (Frontend & Backend)
- ✅ Access to Vercel dashboard

---

## 🎯 PART 1: Backend Deployment

### Step 1: Configure Backend Project

1. Go to **Vercel Dashboard** → Select your **Backend Project**
2. Go to **Settings** → **General**
3. Verify these settings:
   - **Root Directory**: Root (`vaani-banking-voice-assistant`) or leave empty
   - **Framework Preset**: Other
   - **Build Command**: Leave empty (Vercel will use `vercel.json`)
   - **Output Directory**: Leave empty
   - **Install Command**: `uv sync` (or `pip install -r requirements.txt`)

### Step 2: Verify vercel.json

Ensure `vercel.json` exists in root with:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ]
}
```

### Step 3: Set Backend Environment Variables

Go to **Settings** → **Environment Variables** and add:

#### Database Configuration
```
DB_BACKEND=postgresql
DATABASE_URL=your-postgresql-connection-string
```
**OR** for SQLite (not recommended for production):
```
DB_BACKEND=sqlite
DATABASE_URL=sqlite:///./vaani.db
```

**Note**: For production, use PostgreSQL. Get a free database from:
- [Supabase](https://supabase.com) (Recommended)
- [Neon](https://neon.tech)
- [Railway](https://railway.app)
- [Render](https://render.com)

#### Optional Database Settings
```
DB_ECHO=0
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
```

### Step 4: Deploy Backend

1. Go to **Deployments** tab
2. Click **Redeploy** on latest deployment OR
3. Push a commit to trigger auto-deployment

### Step 5: Get Backend URL

After deployment:
1. Go to **Deployments** → Click on latest deployment
2. Copy the **Production URL** (e.g., `https://your-backend-project.vercel.app`)
3. **Save this URL** - you'll need it for frontend configuration

---

## 🎨 PART 2: Frontend Deployment

### Step 1: Configure Frontend Project

1. Go to **Vercel Dashboard** → Select your **Frontend Project**
2. Go to **Settings** → **General**
3. Verify these settings:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Vite (should auto-detect)
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `dist` (default)
   - **Install Command**: `npm install` (default)

### Step 2: Set Frontend Environment Variables

Go to **Settings** → **Environment Variables** and add:

#### Required Variables
```
VITE_API_BASE_URL=https://your-backend-project.vercel.app
VITE_AI_BACKEND_URL=https://your-ai-backend-project.vercel.app
VITE_AI_API_BASE_URL=https://your-ai-backend-project.vercel.app
```

**Important**: 
- Replace `your-backend-project.vercel.app` with your actual backend URL from Step 5 above
- Replace `your-ai-backend-project.vercel.app` with your AI backend URL (if deployed separately)
- If AI backend is not deployed yet, use the backend URL temporarily

#### Environment Variable Settings
- ✅ **Production**: Enabled
- ✅ **Preview**: Enabled  
- ✅ **Development**: Enabled

### Step 3: Deploy Frontend

1. Go to **Deployments** tab
2. Click **Redeploy** on latest deployment OR
3. Push a commit to trigger auto-deployment

**Note**: After adding/changing environment variables, you MUST redeploy for changes to take effect.

---

## 🔗 PART 3: Connect Frontend to Backend

### Step 1: Verify CORS Configuration

The backend CORS is already configured in `backend/app.py` to allow:
- `https://*.vercel.app` (all Vercel deployments)
- Your frontend domain

### Step 2: Test Connection

1. Open your frontend URL: `https://your-frontend-project.vercel.app`
2. Open browser **Developer Tools** (F12) → **Console** tab
3. Try to login or make an API call
4. Check **Network** tab for API requests
5. Verify requests are going to your backend URL

### Step 3: Troubleshoot if Needed

**CORS Errors?**
- Check backend URL in frontend environment variables
- Verify backend CORS includes your frontend domain
- Check browser console for specific error messages

**404 Errors?**
- Verify backend URL is correct
- Check backend deployment is successful
- Verify API routes are correct

**Environment Variables Not Working?**
- Ensure variables start with `VITE_` prefix
- Redeploy frontend after adding variables
- Check variable names match exactly (case-sensitive)

---

## 📝 Environment Variables Summary

### Backend Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `DB_BACKEND` | Yes | Database type | `postgresql` or `sqlite` |
| `DATABASE_URL` | Yes | Database connection string | `postgresql://user:pass@host/db` |
| `DB_ECHO` | No | SQL query logging | `0` or `1` |
| `DB_POOL_SIZE` | No | Connection pool size | `5` |
| `DB_MAX_OVERFLOW` | No | Max pool overflow | `10` |

### Frontend Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `VITE_API_BASE_URL` | Yes | Backend API URL | `https://backend.vercel.app` |
| `VITE_AI_BACKEND_URL` | Yes | AI Backend URL | `https://ai-backend.vercel.app` |
| `VITE_AI_API_BASE_URL` | Yes | AI API URL | `https://ai-backend.vercel.app` |

---

## 🚀 Quick Deployment Checklist

### Backend
- [ ] Project created in Vercel
- [ ] Root directory set correctly
- [ ] `vercel.json` exists and is correct
- [ ] Database environment variables set
- [ ] Deployment successful
- [ ] Backend URL copied

### Frontend
- [ ] Project created in Vercel
- [ ] Root directory set to `frontend`
- [ ] Environment variables set with backend URL
- [ ] Deployment successful
- [ ] Frontend URL tested

### Connection
- [ ] Frontend can reach backend
- [ ] No CORS errors
- [ ] API calls working
- [ ] Login functionality working

---

## 🔧 Common Issues & Solutions

### Issue: Build Fails
**Solution**: 
- Check `pyproject.toml` or `requirements.txt` exists
- Verify Python version (3.11+)
- Check build logs in Vercel dashboard

### Issue: Module Not Found
**Solution**:
- Ensure all dependencies are in `pyproject.toml`
- Check import paths are correct
- Verify root directory is set correctly

### Issue: Database Connection Fails
**Solution**:
- Verify `DATABASE_URL` is correct
- Check database allows connections from Vercel IPs
- For PostgreSQL, ensure SSL is enabled if required

### Issue: Environment Variables Not Working
**Solution**:
- Frontend variables MUST start with `VITE_`
- Redeploy after adding variables
- Check variable names are exact (case-sensitive)
- Verify variables are enabled for correct environments

---

## 📞 Next Steps

1. **Test the deployment**: Try logging in and using features
2. **Monitor logs**: Check Vercel function logs for errors
3. **Set up custom domains** (optional): Add your own domain in Settings → Domains
4. **Configure branch protection** (optional): Set production branch in Settings → Git

---

## 🎉 Success!

Your frontend and backend should now be connected and working on Vercel!

**Frontend URL**: `https://your-frontend-project.vercel.app`  
**Backend URL**: `https://your-backend-project.vercel.app`

