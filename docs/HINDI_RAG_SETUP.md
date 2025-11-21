# Hindi RAG Vector Database Setup

This document explains the dual-language RAG system that supports both Hindi and English vector databases.

## Overview

The system now maintains separate vector databases for Hindi and English documents:
- **English**: `./chroma_db/loan_products` and `./chroma_db/investment_schemes`
- **Hindi**: `./chroma_db/loan_products_hindi` and `./chroma_db/investment_schemes_hindi`

The RAG service automatically routes queries to the correct language-specific vector database based on the user's language selection.

## Architecture Changes

### 1. RAG Service (`ai/services/rag_service.py`)

- Modified `get_rag_service()` to accept a `language` parameter (`"en-IN"` or `"hi-IN"`)
- Each language and document type combination gets its own RAGService instance
- Vector databases are stored in separate directories with language-specific collection names

### 2. Agent Updates

- `loan_agent.py` and `investment_agent.py` now pass the `language` parameter to `get_rag_service()`
- The language is extracted from the state: `language = state.get("language", "en-IN")`

### 3. Document Structure

Documents are organized as follows:
```
backend/documents/
├── loan_products/          # English loan documents
├── loan_products_hindi/    # Hindi loan documents
├── investment_schemes/      # English investment documents
└── investment_schemes_hindi/ # Hindi investment documents
```

## Setup Instructions

### Step 1: Create Hindi Documents

#### For Loan Products:
```bash
cd backend/documents
python create_loan_product_docs_hindi.py
```

This will create PDFs in `backend/documents/loan_products_hindi/`:
- `home_loan_product_guide.pdf`
- `personal_loan_product_guide.pdf`
- `auto_loan_product_guide.pdf`
- `education_loan_product_guide.pdf`
- `business_loan_product_guide.pdf`
- `gold_loan_product_guide.pdf`
- `loan_against_property_guide.pdf`

#### For Investment Schemes:
```bash
cd backend/documents
python create_investment_scheme_docs_hindi.py
```

This will create PDFs in `backend/documents/investment_schemes_hindi/`:
- `ppf_scheme_guide.pdf`
- `nps_scheme_guide.pdf`
- `ssy_scheme_guide.pdf`

### Step 2: Ingest Hindi Documents into Vector Database

```bash
cd ai
python ingest_documents_hindi.py
```

This script will:
1. Load all Hindi PDFs from both `loan_products_hindi/` and `investment_schemes_hindi/`
2. Split them into chunks
3. Create embeddings using sentence-transformers
4. Store them in separate Chroma vector databases:
   - `./chroma_db/loan_products_hindi/`
   - `./chroma_db/investment_schemes_hindi/`

### Step 3: Verify Setup

The ingestion script will test retrieval with a sample Hindi query. You should see:
- ✅ Loan vector database created successfully!
- ✅ Investment vector database created successfully!
- ✅ Retrieval test successful!

## How It Works

### Language Detection and Routing

1. When a user query comes in, the `language` is extracted from the state (defaults to `"en-IN"`)
2. The agent calls `get_rag_service(documents_type="loan", language=language)`
3. The RAG service:
   - Checks the cache for an existing service instance for this `(documents_type, language)` combination
   - If not found, creates a new RAGService with:
     - Language-specific document path
     - Language-specific collection name
     - Language-specific persist directory
   - Initializes the vector store (loads existing or creates new)

### Query Processing

When a query is made:
1. The query is embedded using the same embedding model (works for both Hindi and English)
2. Similarity search is performed in the language-specific vector database
3. Retrieved documents are returned in the same language as the query
4. The LLM receives context in the correct language, ensuring responses match

## Benefits

1. **Language-Specific Context**: Hindi queries retrieve Hindi documents, ensuring consistent language in responses
2. **Better Accuracy**: Embeddings and retrieval work better when query and documents are in the same language
3. **Scalability**: Easy to add more languages by creating new document folders and vector databases
4. **Separation of Concerns**: Each language has its own isolated vector database

## Troubleshooting

### Issue: Hindi documents not found
**Solution**: Run the document creation scripts first:
```bash
python backend/documents/create_loan_product_docs_hindi.py
python backend/documents/create_investment_scheme_docs_hindi.py
```

### Issue: Vector database not found
**Solution**: Run the ingestion script:
```bash
python ai/ingest_documents_hindi.py
```

### Issue: Wrong language database being used
**Check**: Verify that agents are passing the language parameter:
```python
rag_service = get_rag_service(documents_type="loan", language=language)
```

## Future Enhancements

- Add support for more languages (e.g., Tamil, Telugu, Bengali)
- Implement language detection from user query
- Add translation fallback if documents in requested language are not available
- Create unified ingestion script that processes both languages

