# Local Development vs Vercel Deployment

## Overview

This project uses different dependency files for local development and Vercel deployment to optimize for each environment.

## Local Development

**Uses**: `pyproject.toml` (via `uv sync`)

**Setup**:
```bash
uv venv .venv
source .venv/bin/activate
uv sync  # Reads pyproject.toml - installs ALL dependencies
python run_services.py
```

**Dependencies**: All dependencies including:
- Backend dependencies
- AI Backend dependencies (LangChain, ChromaDB, Ollama, etc.)
- Testing dependencies
- Development tools

**File**: `pyproject.toml` (primary) + `requirements.txt` (reference/backup)

## Vercel Deployment

**Uses**: `requirements-backend.txt` (minimal dependencies)

**How it works**:
1. `vercel-build.sh` runs before build
2. Hides `pyproject.toml` and `uv.lock`
3. Copies `requirements-backend.txt` → `requirements.txt`
4. Vercel installs from `requirements.txt` (minimal dependencies)

**Dependencies**: Only backend dependencies:
- FastAPI, Uvicorn
- SQLAlchemy, PostgreSQL driver
- Voice verification (Resemblyzer, Librosa)
- Authentication libraries
- **Excludes**: AI/ML libraries (LangChain, ChromaDB, PyTorch, etc.)

**Files**:
- `requirements-backend.txt` - Minimal backend dependencies
- `vercel-build.sh` - Build script that switches files
- `.vercelignore` - Excludes large files from deployment

## File Structure

```
├── pyproject.toml              # Full dependencies (local dev via uv sync)
├── requirements.txt            # Full dependencies (reference/backup)
├── requirements-backend.txt     # Minimal dependencies (Vercel deployment)
├── vercel-build.sh             # Build script (Vercel only)
└── .vercelignore              # Excludes files from Vercel
```

## Why This Approach?

1. **Local Development**: Needs all dependencies for full functionality
2. **Vercel Deployment**: Backend API doesn't need AI/ML libraries
   - Reduces deployment size from 4GB+ to ~500MB
   - Prevents Out of Memory errors
   - Faster deployments

## Important Notes

- ✅ Local development is **NOT affected** - uses `pyproject.toml` via `uv sync`
- ✅ `requirements.txt` is restored with full dependencies for reference
- ✅ Vercel uses `requirements-backend.txt` via build script
- ✅ Both environments work independently

## Troubleshooting

**Local development not working?**
- Ensure you're using `uv sync` (not `pip install -r requirements.txt`)
- Check that `pyproject.toml` exists and is valid
- Verify virtual environment is activated

**Vercel deployment failing?**
- Check `vercel-build.sh` is executable
- Verify `requirements-backend.txt` exists
- Check build logs for errors

