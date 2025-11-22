# Document Ingestion Guide

This guide explains how to ingest documents into the RAG vector database system.

## Overview

The system uses **semantic chunking** with the FinTech RAG methodology to process financial documents. There are **2 main ingestion scripts**:

1. **English Documents**: `ai/ingest_documents_english.py`
2. **Hindi Documents**: `ai/ingest_documents_hindi.py`

Both scripts process **loan products** and **investment schemes** in a single run.

## Quick Start

### English Documents

```bash
cd ai
python ingest_documents_english.py
```

This will:
- Process English loan products (7 types)
- Process English investment schemes (PPF, NPS, SSY)
- Create vector databases with semantic chunking
- Test retrieval with metadata filtering

### Hindi Documents

```bash
cd ai
python ingest_documents_hindi.py
```

This will:
- Process Hindi loan products (7 types)
- Process Hindi investment schemes (PPF, NPS, SSY)
- Create vector databases with semantic chunking
- Test retrieval with metadata filtering

## What Gets Processed

### Loan Products (Both Languages)
- Personal Loan
- Home Loan
- Auto Loan
- Education Loan
- Gold Loan
- Business Loan (with sub-loans: MUDRA, Term, Working Capital, etc.)
- Loan Against Property (LAP)

### Investment Schemes (Both Languages)
- PPF (Public Provident Fund)
- NPS (National Pension System)
- SSY (Sukanya Samriddhi Yojana)

## Semantic Chunking Features

Both scripts use the enhanced semantic chunking methodology:

1. **Tables** (Highest Priority): Kept intact as single chunks
2. **FAQs**: Q&A pairs grouped together
3. **Sections**: Split by logical headers (Eligibility, Interest Rates, Fees, etc.)
4. **Metadata**: Normalized loan/scheme types, sections, keywords
5. **Language Detection**: Automatic detection (en/hi)

## Output

Each script creates **2 separate vector databases**:

### English
- `./chroma_db/loan_products/` - English loans
- `./chroma_db/investment_schemes/` - English investments

### Hindi
- `./chroma_db/loan_products_hindi/` - Hindi loans
- `./chroma_db/investment_schemes_hindi/` - Hindi investments

## Testing

Both scripts include retrieval tests that:
1. Show unfiltered results (semantic similarity)
2. Show filtered results (metadata filtering)
3. Verify correct loan/scheme types are retrieved

## Prerequisites

Before running ingestion, ensure PDFs are generated:

### English Documents
```bash
cd backend/documents
python create_loan_product_docs.py
python create_investment_scheme_docs.py
```

### Hindi Documents
```bash
cd backend/documents
python create_loan_product_docs_hindi.py
python create_investment_scheme_docs_hindi.py
```

## Troubleshooting

### No Documents Found
- Check that PDFs exist in the correct directories
- Run the PDF generation scripts first

### Wrong Retrieval Results
- Use metadata filtering: `filter={"loan_type": "HOME_LOAN"}`
- Rebuild vector databases to apply latest chunking improvements

### Metadata Issues
- Ensure semantic chunker is normalizing correctly
- Check that `loan_type`/`scheme_type` are uppercase (HOME_LOAN, PPF, etc.)

## Next Steps

After ingestion:
1. Start the AI backend: `python ai/main.py`
2. Test queries through the frontend or API
3. Use metadata filtering in production queries for accuracy

