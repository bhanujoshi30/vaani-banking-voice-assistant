# Vector Database Ingestion Fix

## Issue
The vector databases were being created in the wrong location because the old `ingest_documents.py` used default paths.

## Solution
The ingestion scripts have been updated to use the correct separate directories for each collection.

## Steps to Fix

### 1. Re-run English Ingestion Scripts

```bash
cd ai

# For English loans
python ingest_documents.py

# For English investments (new script)
python ingest_investment_documents.py
```

### 2. Re-run Hindi Ingestion Script

```bash
cd ai

# For Hindi loans and investments
python ingest_documents_hindi.py
```

### 3. Verify

After running the scripts, you should see these directories created:
- `ai/chroma_db/loan_products/`
- `ai/chroma_db/investment_schemes/`
- `ai/chroma_db/loan_products_hindi/`
- `ai/chroma_db/investment_schemes_hindi/`

Each directory should contain:
- `chroma.sqlite3` (metadata database)
- UUID-named subdirectories (collection data)

### 4. Check Status

Run the system and check the startup logs. You should now see:
```
✅ All vector databases found
```

Instead of warnings about missing databases.

## What Changed

1. **`ingest_documents.py`**: Now explicitly sets `persist_directory="./chroma_db/loan_products"` and `collection_name="loan_products"`

2. **`ingest_investment_documents.py`**: New script for English investment schemes with `persist_directory="./chroma_db/investment_schemes"`

3. **`ingest_documents_hindi.py`**: Already had correct paths, no changes needed

4. **`run.sh`**: Updated to check for the correct directory paths

## Note

If you see the old `chroma_db` directory with a single `chroma.sqlite3` file, you can safely delete it after re-running the ingestion scripts, as the new structure uses separate directories for each collection.

