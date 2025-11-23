# Vercel Backend Deployment Setup

## Important: Install Command Configuration

For backend deployment, you **MUST** change the Install Command in Vercel project settings:

### Steps:

1. Go to your Backend project in Vercel Dashboard
2. Go to **Settings** → **General**
3. Scroll to **Build & Development Settings**
4. Find **Install Command**
5. Change from `uv sync` to:
   ```
   pip install -r requirements-backend.txt
   ```
6. Click **Save**

## Why?

The `pyproject.toml` includes dependencies for all three components (Backend, AI Backend, Frontend). The backend only needs a subset of these dependencies. Using `requirements-backend.txt` installs only what's needed, reducing deployment size from 4GB+ to under 500MB.

## Files Created:

- `requirements-backend.txt` - Minimal backend dependencies only
- `.vercelignore` - Excludes large files and AI/ML libraries

## Dependencies Included:

- FastAPI, Uvicorn (web server)
- SQLAlchemy, PostgreSQL driver (database)
- Resemblyzer, Librosa, Soundfile (voice verification)
- Authentication and security libraries
- Basic utilities

## Dependencies Excluded:

- PyTorch, NVIDIA CUDA libraries (huge, not needed)
- LangChain, LangGraph (AI backend only)
- ChromaDB (AI backend only)
- Transformers, Sentence-transformers (AI backend only)
- Ollama (AI backend only)

