# Vercel AI Backend Build Fix

## Problem

The deployment was failing with a 4.3GB size error because:
1. The `builds` section in `vercel-ai.json` was preventing the `buildCommand` from running
2. Vercel was automatically installing ALL dependencies from `requirements.txt` (full version)
3. The build script never executed to clean up files

## Solution

### 1. Removed `builds` Section ✅

**File**: `vercel-ai.json`

Changed from:
```json
{
  "version": 2,
  "buildCommand": "bash vercel-build-ai.sh",
  "builds": [...],
  "routes": [...]
}
```

To:
```json
{
  "version": 2,
  "buildCommand": "bash vercel-build-ai.sh"
}
```

**Why**: When `builds` exists, Vercel ignores `buildCommand` and uses automatic Python detection, which installs everything.

### 2. Updated Build Script to Use Build Output API ✅

**File**: `vercel-build-ai.sh`

The script now:
1. **Removes ChromaDB files** before bundling
2. **Keeps only 3 PDFs** (2 loans + 1 investment)
3. **Uses minimal requirements** (`ai/requirements-vercel.txt`)
4. **Installs dependencies** into a controlled bundle
5. **Copies only necessary files** (ai/, backend/, ai_main.py)
6. **Cleans up** test files, cache files, and unnecessary PDFs
7. **Creates Build Output API structure** (`.vercel/output/`)

### 3. Build Output API Structure

The script creates:
```
.vercel/output/
├── config.json          # Routes configuration
└── functions/
    └── api/
        └── index.func/
            ├── index.py              # Entry point
            ├── .vc-config.json       # Runtime config
            └── python/               # All dependencies + code
                ├── ai/
                ├── backend/
                └── [all packages]
```

## What Gets Deployed

### Included:
- ✅ FastAPI application (`ai/main.py`)
- ✅ AI agents and services
- ✅ LangChain/LangGraph (agent framework)
- ✅ OpenAI integration
- ✅ ChromaDB library (for vector store)
- ✅ PyPDF (for PDF processing)
- ✅ 2 Loan PDFs: `home_loan_product_guide.pdf`, `personal_loan_product_guide.pdf`
- ✅ 1 Investment PDF: `ppf_scheme_guide.pdf`
- ✅ Backend models (for database integration)

### Excluded:
- ❌ Pre-built ChromaDB database files (*.bin, *.sqlite3)
- ❌ Other loan/investment PDFs (removed during build)
- ❌ sentence-transformers (uses OpenAI embeddings)
- ❌ Ollama dependencies
- ❌ Test files
- ❌ Cache files (__pycache__, *.pyc)

## Deployment Steps

1. **Push changes** to trigger deployment
2. **Build script runs** automatically:
   - Cleans ChromaDB files
   - Keeps only 3 PDFs
   - Installs minimal dependencies
   - Creates optimized bundle
3. **Vercel deploys** the `.vercel/output` directory

## Expected Build Output

You should see in build logs:
```
🔧 AI Backend build script starting...
🗑️  Removing ChromaDB vector database files...
✅ ChromaDB files removed
📚 Keeping only essential PDFs for RAG...
✅ Kept loan PDFs: home_loan_product_guide.pdf, personal_loan_product_guide.pdf
✅ Kept investment PDF: ppf_scheme_guide.pdf
📄 Backing up full requirements.txt...
✅ Using minimal requirements: ai/requirements-vercel.txt
🧹 Cleaning previous build output...
📦 Installing AI backend dependencies...
📁 Copying AI backend source code...
📝 Creating serverless function entrypoint...
✅ Build output ready for deployment
```

## Size Reduction

**Before**: ~4.3GB (failed)
**After**: ~100-200MB (expected)

The reduction comes from:
- Minimal dependencies (no sentence-transformers, ollama, etc.)
- Only 3 PDFs instead of 10+
- No pre-built ChromaDB files
- No test files or cache

## Troubleshooting

### Build Script Not Running?

1. Check `vercel-ai.json` - should NOT have `builds` section
2. Verify `buildCommand` is set: `"buildCommand": "bash vercel-build-ai.sh"`
3. Check build logs for script output

### Still Getting Size Errors?

1. Check build logs - verify script executed
2. Verify `ai/requirements-vercel.txt` is being used
3. Check if ChromaDB files are being removed
4. Verify PDF cleanup is working

### Missing Dependencies?

If you see import errors:
1. Check `ai/requirements-vercel.txt` includes the package
2. Verify the package is compatible with `--no-deps` flag
3. May need to add transitive dependencies manually

## Next Steps

1. ✅ Build script updated to use Build Output API
2. ✅ Removed `builds` section from vercel-ai.json
3. ⏳ Deploy and verify build succeeds
4. ⏳ Check deployment size (should be < 200MB)
5. ⏳ Test `/health` endpoint
6. ⏳ Test `/api/chat` endpoint
7. ⏳ Verify RAG works (first query builds vector store)

