# Semantic Chunking Implementation

## Overview

A new semantic chunking methodology has been implemented to improve the accuracy of loan and investment document retrieval. This replaces the previous character-based chunking with intelligent, section-aware chunking that preserves logical document structure.

## Key Features

### 1. **Semantic Section-Based Chunking**
- Splits documents by logical sections (Overview, Features, Eligibility, Documents, etc.)
- Preserves context within each section
- Handles both English and Hindi documents

### 2. **Sub-Loan Type Detection**
- Automatically detects sub-loan types within business loans:
  - MUDRA Loans (Shishu, Kishore, Tarun)
  - Term Loans
  - Working Capital Loans
  - Invoice Financing
  - Equipment Financing
  - Business Overdraft
- Also handles home loan sub-types (Purchase, Construction, Extension, etc.)

### 3. **Table Handling**
- Detects tables using multiple patterns
- Keeps tables as single, intact chunks
- Converts CSV-style tables to Markdown format
- Prevents table rows from being split across chunks

### 4. **FAQ Grouping**
- Detects FAQ sections automatically
- Groups Question-Answer pairs together
- Keeps FAQs in single chunks when possible

### 5. **Rich Metadata Extraction**
- **Language Detection**: Automatically detects English (`en`) or Hindi (`hi`)
- **Scheme/Loan Normalization**: Maps to standard identifiers (PPF, NPS, SSY, HOME_LOAN, BUSINESS_LOAN_MUDRA, etc.)
- **Context Headers**: Creates descriptive headers like "BUSINESS_LOAN_MUDRA - Types - MUDRA Loans"
- **Keywords**: Extracts financial terms, rates, amounts, and section names
- **Section Names**: Identifies document sections (Eligibility, Documents, Interest Rate, etc.)

## Files Created/Modified

### New Files
1. **`ai/services/semantic_chunker.py`**
   - Main semantic chunking service
   - Implements all chunking logic and metadata extraction

### Modified Files
1. **`ai/services/rag_service.py`**
   - Updated `chunk_documents()` method to use semantic chunking by default
   - Added `use_semantic` parameter (default: True)
   - Integrated `SemanticChunker` class

## Usage

The semantic chunking is now the default method. When you rebuild your vector database, it will automatically use semantic chunking:

```python
from services.rag_service import RAGService

# Initialize RAG service (semantic chunking is default)
rag_service = RAGService(
    documents_path="./backend/documents/loan_products",
    persist_directory="./chroma_db/loan_products"
)

# Load and chunk documents (uses semantic chunking)
documents = rag_service.load_pdf_documents()
chunks = rag_service.chunk_documents(documents)  # Semantic chunking by default

# Create vector store with enriched metadata
vectorstore = rag_service.create_vector_store(chunks)
```

## Metadata Structure

Each chunk now includes enriched metadata:

```json
{
  "id": "business_loan_mudra_en_01",
  "loan_type": "BUSINESS_LOAN_MUDRA",
  "language": "en",
  "section": "Types - MUDRA Loans",
  "context_header": "BUSINESS_LOAN_MUDRA - Types - MUDRA Loans",
  "sub_loan_type": "MUDRA Loans",
  "keywords": ["MUDRA", "Rs. 50,000", "Shishu", "Kishore", "Tarun"],
  "is_table": false,
  "is_faq": false,
  "source": "business_loan_product_guide.pdf",
  "document_type": "loan"
}
```

## Benefits for Business Loans

1. **Accurate Sub-Loan Retrieval**: When users ask about "MUDRA loans" or "Term loans", the system can retrieve the specific sub-loan information rather than generic business loan content.

2. **Preserved Context**: Tables and FAQs remain intact, providing complete information in single chunks.

3. **Better Search**: Rich metadata (keywords, context headers, sub-loan types) improves retrieval accuracy.

4. **Multilingual Support**: Handles both English and Hindi documents with proper language detection.

## Rebuilding Vector Database

To apply the new chunking method to your existing documents:

```bash
# For English loan products
cd ai
python ingest_documents.py

# For Hindi loan products  
python ingest_documents_hindi.py

# For investment schemes
python ingest_investment_documents.py
```

The new chunking will automatically be applied, and you'll see improved retrieval accuracy, especially for business loans with multiple sub-loan types.

## Testing

A test script is available at `ai/test_semantic_chunking.py` (requires langchain dependencies to run). The script demonstrates:
- Table detection and preservation
- FAQ grouping
- Sub-loan type detection
- Metadata extraction
- Context header generation

## Next Steps

1. Rebuild your vector databases using the ingestion scripts
2. Test queries for business loan sub-types (e.g., "What is MUDRA loan?", "Tell me about term loans")
3. Verify that retrieval accuracy has improved for complex loan documents

