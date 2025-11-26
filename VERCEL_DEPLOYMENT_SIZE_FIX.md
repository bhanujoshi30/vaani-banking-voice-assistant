# Vercel AI Backend Deployment Size Fix

## Problem

The AI backend deployment was failing with:
```
RangeError [ERR_OUT_OF_RANGE]: The value of "size" is out of range. It must be >= 0 && <= 4294967296. Received 4_318_545_412
```

This error occurs when the deployment package exceeds Vercel's size limits (~4GB). The issue was caused by:
1. **ChromaDB vector database files** - Multiple GB of binary files
2. **Heavy ML dependencies** - sentence-transformers, torch, etc. (not needed for OpenAI)
3. **Ollama dependencies** - Not needed when using OpenAI

## Solution

### 1. Created Minimal Requirements File ✅

**File**: `ai/requirements-vercel.txt`

This file includes only the essential dependencies for OpenAI-only deployment:
- Core LangChain/LangGraph (for agent framework)
- FastAPI/uvicorn (for API)
- ChromaDB library (for imports, but DB files excluded)
- Excludes: Ollama, sentence-transformers, heavy ML models

### 2. Created Build Script ✅

**File**: `vercel-build-ai.sh`

The build script:
- Removes ChromaDB database files (*.bin, *.sqlite3) before deployment
- Copies minimal requirements to root `requirements.txt`
- Reduces deployment size from ~4GB to ~50-100MB

### 3. Updated Vercel Configuration ✅

**File**: `vercel-ai.json`

Updated to use the build script:
```json
{
  "version": 2,
  "buildCommand": "bash vercel-build-ai.sh",
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

## Deployment Instructions

### Step 1: Configure Vercel Project

1. Go to Vercel Dashboard → Your AI Backend Project
2. **Settings → General → Build & Development Settings**:
   - **Build Command**: `bash vercel-build-ai.sh`
   - **Output Directory**: Leave empty
   - **Install Command**: Leave empty (handled by build script)

### Step 2: Set Environment Variables

Go to **Settings → Environment Variables** and ensure:
```
OPENAI_ENABLED=true
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-3.5-turbo
LLM_PROVIDER=openai  # Optional: explicitly set
CORS_ALLOWED_ORIGINS=https://tech-tonic-ai.com,https://www.tech-tonic-ai.com
```

### Step 3: Deploy

1. Push your changes or trigger a new deployment
2. The build script will automatically:
   - Remove ChromaDB database files
   - Use minimal requirements
   - Reduce deployment size

### Step 4: Verify

1. Check build logs - should show:
   ```
   🔧 AI Backend build script starting...
   🗑️  Removing ChromaDB vector database files...
   ✅ ChromaDB files removed
   📄 Using minimal requirements for OpenAI-only deployment...
   ✅ Build configuration ready
   ```

2. Check deployment size - should be under 200MB

3. Test `/health` endpoint:
   ```bash
   curl https://your-ai-backend.vercel.app/health
   ```

## Important Notes

### RAG Features

- **RAG will be disabled** on Vercel because ChromaDB database files are excluded
- The code will handle missing vector stores gracefully
- Loan/investment queries will still work but won't use RAG retrieval
- To enable RAG, you would need to:
  1. Use external ChromaDB (hosted service)
  2. Or use OpenAI embeddings with a different vector store
  3. Or include the database files (not recommended due to size)

### What's Included vs Excluded

**Included:**
- ✅ FastAPI application code
- ✅ LangChain/LangGraph (agent framework)
- ✅ OpenAI integration (via httpx)
- ✅ ChromaDB library (for imports)
- ✅ Database ORM (SQLAlchemy)

**Excluded:**
- ❌ ChromaDB database files (*.bin, *.sqlite3)
- ❌ Ollama dependencies
- ❌ sentence-transformers (huge ML models)
- ❌ PyPDF (document processing)
- ❌ Azure TTS (optional)

## Troubleshooting

### Still Getting Size Errors?

1. Check build logs - verify ChromaDB files are being removed
2. Verify `vercel-build-ai.sh` is executable: `chmod +x vercel-build-ai.sh`
3. Check `.vercelignore` excludes large files
4. Verify `requirements-vercel.txt` is being used

### RAG Not Working?

This is expected - ChromaDB database files are excluded. RAG features will be disabled. The application will still work for general chat, but loan/investment queries won't use document retrieval.

### Import Errors?

If you see import errors for ChromaDB:
- The library is included in `requirements-vercel.txt`
- But database files are excluded (this is intentional)
- RAG will gracefully handle missing databases

## Next Steps

1. ✅ Build script created
2. ✅ Minimal requirements created
3. ✅ Vercel config updated
4. ⏳ Deploy and test
5. ⏳ Verify OpenAI is being used (check logs)
6. ⏳ Test `/api/chat` endpoint

