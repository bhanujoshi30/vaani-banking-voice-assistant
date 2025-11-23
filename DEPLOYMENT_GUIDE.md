# Vercel Deployment Guide

This guide explains how to deploy the Vaani Banking Voice Assistant on Vercel with three separate projects:
1. **Frontend** - React application
2. **Backend** - FastAPI backend API
3. **AI Backend** - FastAPI AI/LLM service

## Prerequisites

- GitHub repository connected to Vercel
- Vercel account
- Environment variables configured

## Deployment Steps

### 1. Frontend Deployment

1. Go to Vercel Dashboard → **New Project**
2. Import your GitHub repository
3. **Root Directory**: Select `frontend/`
4. **Framework Preset**: Vite (auto-detected)
5. **Build Command**: `npm run build` (default)
6. **Output Directory**: `dist` (default)

#### Frontend Environment Variables

In **Settings → Environment Variables**, add:

```
VITE_API_BASE_URL=https://your-backend.vercel.app
VITE_AI_BACKEND_URL=https://your-ai-backend.vercel.app
VITE_AI_API_BASE_URL=https://your-ai-backend.vercel.app
```

Replace with your actual backend URLs after deployment.

### 2. Backend Deployment

1. Go to Vercel Dashboard → **New Project**
2. Import your GitHub repository
3. **Root Directory**: Select root directory (`vaani-banking-voice-assistant`)
4. **Framework Preset**: Other
5. Vercel will auto-detect Python from `pyproject.toml`
6. The `vercel.json` in root will configure the deployment

#### Backend Environment Variables

Add your database and other backend environment variables in **Settings → Environment Variables**.

### 3. AI Backend Deployment

**Important**: The AI backend imports from the `backend/` directory. You have two options:

#### Option A: Deploy from Root (Recommended)

1. Go to Vercel Dashboard → **New Project**
2. Import your GitHub repository
3. **Root Directory**: Select root directory (`vaani-banking-voice-assistant`)
4. **Framework Preset**: Other
5. In **Settings → General → Build & Development Settings**:
   - **Build Command**: Leave empty or `echo "AI Backend"`
   - **Output Directory**: Leave empty
   - **Install Command**: `uv sync` (or `pip install -r requirements.txt`)
6. Create a `vercel.json` file in the project root with this content:
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "ai_main.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "ai_main.py"
       }
     ]
   }
   ```
   Or copy `vercel-ai.json` to `vercel.json` in your project settings.

#### Option B: Deploy from AI Directory (Requires Refactoring)

If deploying from `ai/` directory, you'll need to:
- Refactor imports to use backend as an external API, OR
- Copy backend models to AI directory, OR
- Use a monorepo build setup

#### AI Backend Environment Variables

Add in **Settings → Environment Variables**:

```
OLLAMA_BASE_URL=http://your-ollama-server:11434
AZURE_TTS_KEY=your-azure-key
AZURE_TTS_REGION=your-region
OPENAI_API_KEY=your-openai-key (if using OpenAI)
LANGCHAIN_API_KEY=your-langchain-key
DATABASE_URL=your-database-url
REDIS_URL=your-redis-url (optional)
```

## Connecting the Projects

### 1. Update Frontend Environment Variables

After deploying backend and AI backend, update frontend environment variables with the actual Vercel URLs:

```
VITE_API_BASE_URL=https://your-backend-project.vercel.app
VITE_AI_BACKEND_URL=https://your-ai-backend-project.vercel.app
VITE_AI_API_BASE_URL=https://your-ai-backend-project.vercel.app
```

### 2. CORS Configuration

Both backend projects have been configured to allow Vercel frontend URLs:
- `https://*.vercel.app` - Allows all Vercel deployments
- `https://vaani-banking-voice-assistant-*.vercel.app` - Specific pattern

CORS is already configured in:
- `backend/app.py`
- `ai/main.py`

### 3. Redeploy Frontend

After updating environment variables, redeploy the frontend project to pick up the new URLs.

## Branch Configuration

To deploy from a specific branch:

1. Go to **Settings → Git → Production Branch**
2. Select your branch (e.g., `main`, `final_v0.10_vercel_changes`)
3. Save changes

## Troubleshooting

### CORS Errors

If you see CORS errors:
1. Check that backend CORS includes your frontend URL
2. Verify environment variables are set correctly
3. Ensure both projects are deployed

### Import Errors (AI Backend)

If AI backend can't import from backend:
- Ensure you're deploying from root directory, OR
- Refactor to use backend as external API

### Environment Variables Not Working

- Vite requires `VITE_` prefix for frontend variables
- Redeploy after adding/changing environment variables
- Check variable names match exactly (case-sensitive)

## Project URLs

After deployment, you'll have:

- **Frontend**: `https://your-frontend-project.vercel.app`
- **Backend**: `https://your-backend-project.vercel.app`
- **AI Backend**: `https://your-ai-backend-project.vercel.app`

## Notes

- All three projects can be deployed from the same GitHub repository
- Use different root directories for each project
- Environment variables are project-specific
- Preview deployments work automatically for all branches

