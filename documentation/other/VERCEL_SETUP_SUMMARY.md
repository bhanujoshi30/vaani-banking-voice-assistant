# Vercel Setup Summary

## Changes Made

### ✅ Backend CORS Updated
- **File**: `backend/app.py`
- **Change**: Added Vercel frontend URLs to CORS origins
- **Allows**: All Vercel deployments (`https://*.vercel.app`)

### ✅ AI Backend CORS Updated
- **File**: `backend/ai/main.py`
- **Change**: Added Vercel frontend URLs to CORS origins
- **Allows**: All Vercel deployments (`https://*.vercel.app`)

### ✅ AI Backend Entry Point Created
- **File**: `ai_main.py` (root directory)
- **Purpose**: Entry point for deploying AI backend from root directory
- **Allows**: AI backend to access backend directory imports

### ✅ Configuration Files Created
- `backend/ai/vercel.json` - For deploying AI backend from `backend/ai/` directory
- `vercel-ai.json` - Alternative config for deploying AI backend from root
- `backend/ai/.vercelignore` - Excludes large files from AI backend deployment

## Deployment Instructions

### 1. Frontend Project
- **Root Directory**: `frontend/`
- **Framework**: Vite (auto-detected)
- **Environment Variables**:
  ```
  VITE_API_BASE_URL=https://your-backend.vercel.app
  VITE_AI_BACKEND_URL=https://your-ai-backend.vercel.app
  VITE_AI_API_BASE_URL=https://your-ai-backend.vercel.app
  ```

### 2. Backend Project
- **Root Directory**: Root (`vaani-banking-voice-assistant`)
- **Uses**: `vercel.json` (points to `main.py`)
- **Environment Variables**: Add your database and backend config

### 3. AI Backend Project
- **Root Directory**: Root (`vaani-banking-voice-assistant`)
- **Configuration**: 
  - Option 1: Copy `vercel-ai.json` content to `vercel.json` in Vercel dashboard
  - Option 2: Manually set entry point to `ai_main.py` in Vercel settings
- **Environment Variables**: Add Ollama, Azure TTS, OpenAI, etc.

## Important Notes

1. **AI Backend Imports**: The AI backend imports from `backend/` directory, so it must be deployed from root directory (not from `ai/` subdirectory).

2. **Environment Variables**: Update frontend environment variables AFTER deploying backend and AI backend to get their actual URLs.

3. **CORS**: Both backends now allow all Vercel deployments. You can restrict to specific domains if needed.

4. **Branch Configuration**: Set production branch in **Settings → Git → Production Branch** for each project.

## Next Steps

1. Deploy Backend project first
2. Deploy AI Backend project
3. Deploy Frontend project with environment variables pointing to backend URLs
4. Test the connection between all three projects

## Troubleshooting

- **CORS Errors**: Check that backend URLs are correct in frontend env vars
- **Import Errors**: Ensure AI backend is deployed from root directory
- **Build Errors**: Check that all dependencies are in `pyproject.toml` or `requirements.txt`

