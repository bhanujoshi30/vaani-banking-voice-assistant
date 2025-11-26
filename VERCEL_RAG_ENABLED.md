# Vercel RAG Configuration - Limited Functionality

## Overview

RAG (Retrieval-Augmented Generation) is now enabled on Vercel with **limited functionality**:
- ✅ **2 Loan PDFs**: Home Loan, Personal Loan
- ✅ **1 Investment PDF**: PPF (Public Provident Fund)
- ✅ **OpenAI Embeddings**: Uses OpenAI's embedding API (no heavy ML models)
- ✅ **Lazy Initialization**: Vector store built on first use

## How It Works

### 1. PDF Selection

The build script (`vercel-build-ai.sh`) automatically keeps only:
- `backend/documents/loan_products/home_loan_product_guide.pdf`
- `backend/documents/loan_products/personal_loan_product_guide.pdf`
- `backend/documents/investment_schemes/ppf_scheme_guide.pdf`

All other PDFs are removed during build to reduce deployment size.

### 2. OpenAI Embeddings

Instead of using heavy `sentence-transformers` models, RAG now uses **OpenAI's embedding API**:
- Model: `text-embedding-ada-002`
- No local ML models needed
- Fast and reliable
- Costs ~$0.0001 per 1K tokens

### 3. Lazy Vector Store Building

The ChromaDB vector store is **built on first use**:
- First RAG query triggers document loading and chunking
- PDFs are processed and embedded using OpenAI
- Vector store is created and persisted
- Subsequent queries use the cached vector store

## Configuration

### Environment Variables Required

```
OPENAI_ENABLED=true
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-3.5-turbo
```

### What's Included

**Included:**
- ✅ FastAPI application code
- ✅ LangChain/LangGraph (agent framework)
- ✅ OpenAI integration (chat + embeddings)
- ✅ ChromaDB library
- ✅ PyPDF (PDF processing)
- ✅ 2 Loan PDFs + 1 Investment PDF

**Excluded:**
- ❌ Pre-built ChromaDB database files (built on first use)
- ❌ Other loan/investment PDFs (removed during build)
- ❌ sentence-transformers (uses OpenAI embeddings instead)
- ❌ Ollama dependencies

## Usage

### First Query (Builds Vector Store)

When a user asks about loans or investments for the first time:
1. RAG service detects no vector store exists
2. Loads PDFs from `backend/documents/`
3. Chunks documents into smaller pieces
4. Generates embeddings using OpenAI API
5. Creates ChromaDB vector store
6. Stores vector store in `ai/chroma_db/`
7. Returns results

**Note**: First query may take 10-30 seconds while building the vector store.

### Subsequent Queries

After the vector store is built:
1. RAG service loads existing vector store
2. Queries are fast (< 2 seconds)
3. Returns relevant document chunks

## Supported Queries

### Loan Queries (Limited)
- ✅ Home Loan questions
- ✅ Personal Loan questions
- ❌ Auto Loan (PDF removed)
- ❌ Business Loan (PDF removed)
- ❌ Education Loan (PDF removed)
- ❌ Gold Loan (PDF removed)
- ❌ Loan Against Property (PDF removed)

### Investment Queries (Limited)
- ✅ PPF (Public Provident Fund) questions
- ❌ NPS (PDF removed)
- ❌ SSY (PDF removed)
- ❌ Other schemes (PDFs removed)

## Adding More PDFs

To add more PDFs to RAG:

1. **Update Build Script** (`vercel-build-ai.sh`):
   ```bash
   # Add to KEEP_LOANS array
   KEEP_LOANS=("home_loan_product_guide.pdf" "personal_loan_product_guide.pdf" "auto_loan_product_guide.pdf")
   ```

2. **Redeploy**: Push changes and redeploy

3. **Rebuild Vector Store**: Delete existing vector store or wait for it to rebuild

## Troubleshooting

### RAG Not Working?

1. **Check Environment Variables**:
   - `OPENAI_ENABLED=true`
   - `OPENAI_API_KEY` is set

2. **Check Logs**:
   - Look for: `"rag_service_init", embedding_model="openai-text-embedding-ada-002"`
   - Look for: `"rag_initialized"` messages

3. **Check PDFs Exist**:
   - Verify PDFs are in `backend/documents/loan_products/` and `backend/documents/investment_schemes/`
   - Check build logs for: `"✅ Kept loan PDFs"` and `"✅ Kept investment PDF"`

### First Query Slow?

This is expected! The first query builds the vector store:
- Loading PDFs: ~2-5 seconds
- Chunking documents: ~1-2 seconds
- Generating embeddings: ~5-15 seconds (depends on document size)
- Creating vector store: ~2-5 seconds

**Total**: 10-30 seconds for first query

### Vector Store Not Persisting?

Vercel serverless functions are stateless. The vector store is rebuilt on each cold start:
- **Cold start**: Vector store rebuilt from PDFs
- **Warm function**: Uses cached vector store (if available)

To improve performance:
- Use Vercel's persistent storage (if available)
- Or use external ChromaDB service
- Or accept that first query after cold start will be slower

## Cost Considerations

### OpenAI Embeddings Cost

- **Model**: `text-embedding-ada-002`
- **Cost**: ~$0.0001 per 1K tokens
- **Estimated cost per query**: $0.001-0.01 (depends on document size)

### Example Costs

For 3 PDFs (2 loans + 1 investment):
- **Initial build**: ~$0.05-0.10 (one-time per cold start)
- **Per query**: ~$0.001-0.01

**Monthly estimate** (1000 queries): ~$1-10

## Next Steps

1. ✅ RAG enabled with OpenAI embeddings
2. ✅ Limited PDFs included (2 loans + 1 investment)
3. ✅ Build script configured
4. ⏳ Deploy and test
5. ⏳ Monitor first query performance
6. ⏳ Consider adding more PDFs if needed

