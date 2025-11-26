# Vercel AI Backend Deployment Fix

## Issues Identified

1. **404 Error on `/api/chat`**: The AI backend is not deployed on Vercel, or deployed incorrectly
2. **OpenAI Not Being Used**: Even though `OPENAI_ENABLED`, `OPENAI_API_KEY`, and `OPENAI_MODEL` are set in Vercel, the code wasn't checking `OPENAI_ENABLED` to automatically switch to OpenAI

## Fixes Applied

### 1. Auto-Detect OpenAI Provider ✅

**File**: `ai/config.py`

Updated the `Settings` class to automatically use OpenAI when `OPENAI_ENABLED=true` and `OPENAI_API_KEY` is set:

```python
def model_post_init(self, __context):
    """Post-initialization: auto-detect provider based on OpenAI settings"""
    # Check LLM_PROVIDER env var first (takes precedence)
    llm_provider_env = os.getenv("LLM_PROVIDER", "").lower()
    if llm_provider_env in ("ollama", "openai"):
        object.__setattr__(self, "llm_provider", llm_provider_env)
    # Auto-detect provider: if OpenAI is enabled and API key is set, use OpenAI
    elif self.openai_enabled and self.openai_api_key:
        object.__setattr__(self, "llm_provider", "openai")
```

**Result**: Now when `OPENAI_ENABLED=true` and `OPENAI_API_KEY` is set in Vercel, the system will automatically use OpenAI instead of Ollama.

## Deployment Instructions

### Option 1: Deploy AI Backend as Separate Vercel Project (Recommended)

1. **Create New Vercel Project**:
   - Go to Vercel Dashboard → **New Project**
   - Import your GitHub repository
   - **Root Directory**: Select root directory (`vaani-banking-voice-assistant`)
   - **Framework Preset**: Other

2. **Configure Build Settings**:
   - In **Settings → General → Build & Development Settings**:
     - **Build Command**: Leave empty (or use default)
     - **Output Directory**: Leave empty
     - **Install Command**: `pip install -r requirements.txt` (or `uv sync` if using uv)

3. **Set Vercel Configuration**:
   - Copy `vercel-ai.json` content to `vercel.json` in the project root, OR
   - Manually configure in Vercel dashboard:
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

4. **Set Environment Variables**:
   Go to **Settings → Environment Variables** and add:
   ```
   OPENAI_ENABLED=true
   OPENAI_API_KEY=sk-your-actual-api-key-here
   OPENAI_MODEL=gpt-3.5-turbo
   LLM_PROVIDER=openai  # Optional: explicitly set (OPENAI_ENABLED will auto-set this)
   CORS_ALLOWED_ORIGINS=https://tech-tonic-ai.com,https://www.tech-tonic-ai.com
   ```

5. **Deploy**:
   - Click **Deploy** or push a commit to trigger deployment
   - Copy the deployment URL (e.g., `https://your-ai-backend.vercel.app`)

6. **Update Frontend Configuration**:
   - Go to your Frontend Vercel project
   - **Settings → Environment Variables**
   - Update `VITE_AI_BACKEND_URL` to your AI backend URL:
     ```
     VITE_AI_BACKEND_URL=https://your-ai-backend.vercel.app
     ```
   - Redeploy frontend

### Option 2: Use Same Vercel Project (Advanced)

If you want to deploy both backends in the same project, you'll need to:
1. Modify `vercel-build.sh` to build both backends
2. Configure routes to route `/api/chat` to AI backend and other routes to banking backend
3. This is more complex and not recommended

## Verification Steps

1. **Check AI Backend Health**:
   ```bash
   curl https://your-ai-backend.vercel.app/health
   ```
   Should return:
   ```json
   {
     "status": "healthy",
     "version": "1.0.0",
     "ollama_status": false,
     "azure_tts_available": false
   }
   ```

2. **Test Chat Endpoint**:
   ```bash
   curl -X POST https://your-ai-backend.vercel.app/api/chat \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Hello",
       "session_id": "test-123",
       "language": "en-IN"
     }'
   ```

3. **Check Vercel Logs**:
   - Go to Vercel Dashboard → Your AI Backend Project → **Logs**
   - Look for: `"llm_service_initialized", provider="openai (cloud)"`
   - This confirms OpenAI is being used

## Environment Variables Summary

### Required for OpenAI:
- `OPENAI_ENABLED=true` ✅ (Already set in Vercel)
- `OPENAI_API_KEY=sk-...` ✅ (Already set in Vercel)
- `OPENAI_MODEL=gpt-3.5-turbo` ✅ (Already set in Vercel)

### Optional (but recommended):
- `LLM_PROVIDER=openai` (Explicitly set provider - will override auto-detection)

### CORS Configuration:
- `CORS_ALLOWED_ORIGINS=https://tech-tonic-ai.com,https://www.tech-tonic-ai.com`

## Troubleshooting

### Still Getting 404?
- Verify AI backend is deployed separately from banking backend
- Check that `vercel.json` (or Vercel config) points to `ai_main.py`
- Check Vercel logs for deployment errors

### Still Using Ollama?
- Check Vercel environment variables are set correctly
- Verify `OPENAI_ENABLED=true` (not `True` or `1`)
- Check logs for: `"llm_service_initialized", provider="openai (cloud)"`
- If you see `"ollama (local)"`, the provider detection isn't working

### CORS Errors?
- Add your frontend domain to `CORS_ALLOWED_ORIGINS` in AI backend Vercel project
- Ensure `allow_credentials=True` in CORS middleware

## Next Steps

1. ✅ Code fix applied (auto-detect OpenAI)
2. ⏳ Deploy AI backend as separate Vercel project
3. ⏳ Set `LLM_PROVIDER=openai` in Vercel (optional, but recommended)
4. ⏳ Update frontend `VITE_AI_BACKEND_URL` environment variable
5. ⏳ Test `/api/chat` endpoint
6. ⏳ Verify OpenAI API calls in Vercel logs

