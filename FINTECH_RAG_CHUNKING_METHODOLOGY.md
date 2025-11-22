# FinTech RAG Pipeline - Universal Chunking & Metadata Extraction Methodology

## Overview

This document describes the enhanced semantic chunking methodology specifically designed for **Sun National Bank Loan Product Guides** in the FinTech RAG pipeline. The system handles both English and Hindi documents with intelligent chunking and metadata extraction.

## Key Features

### 1. Global Pre-Processing Rules

- **Noise Removal:**
  - Strips HTML/XML tags (`<tags>`)
  - Removes generic headers/footers (Page numbers, URLs, phone numbers)
  - Preserves headers at document start for context

- **Language Handling:**
  - Automatic language detection (`en` or `hi`)
  - **Content Preservation:** Hindi content remains in Devanagari script
  - **Metadata Normalization:** All metadata tags normalized to English

### 2. Semantic Chunking Logic (Priority Order)

#### **Tables (Highest Priority)**
- **Trigger:** OCR artifact `"The following table:"` or Hindi equivalent `"निम्नलिखित तालिका:"`
- **Action:** Capture entire table, convert CSV-style rows to Markdown format
- **Reason:** Loan data (Interest Rates vs. Credit Score, LTV ratios) requires row/column alignment

#### **FAQs**
- **Trigger:** `Q1:`, `Q:`, `प्रश्न 1:`, `प्रश्न:`
- **Action:** Group Question + Answer into single chunk
- **Preservation:** Keeps Q&A pairs together for context

#### **Key Sections**
- **Split by headers:**
  - Eligibility / पात्रता
  - Documents Required / दस्तावेज
  - Interest Rate Structure / ब्याज दर संरचना
  - Fees & Charges / शुल्क
  - Repayment / पुनर्भुगतान

### 3. Metadata Enrichment

#### **Loan Type Normalization**

All loan types mapped to standard keys:

| Standard Key | Includes |
|-------------|----------|
| `PERSONAL_LOAN` | "Personal Loan", "व्यक्तिगत ऋण" |
| `HOME_LOAN` | "Home Loan", "गृह ऋण" |
| `AUTO_LOAN` | "Car Loan", "Vehicle Loan", "वाहन ऋण" |
| `EDUCATION_LOAN` | "Student Loan", "शिक्षा ऋण" |
| `GOLD_LOAN` | "Jewel Loan", "स्वर्ण ऋण" |
| `BUSINESS_LOAN` | "MSME", "MUDRA", "व्यापार ऋण" |
| `LAP` | "Loan Against Property", "संपत्ति पर ऋण" |

#### **Section Normalization**

- Section names normalized to English in metadata:
  - `Eligibility`, `Documents`, `Interest_Rates`, `Fees`, `FAQ`, etc.
- Original headers preserved in content (Hindi remains in Hindi)

### 4. Output Format

Each chunk follows this JSON structure:

```json
{
  "id": "home_loan_en_interest_rates_01",
  "loan_type": "HOME_LOAN",
  "language": "en",
  "section": "Interest_Rates",
  "context_header": "HOME_LOAN - Interest Rate Structure",
  "content": "Interest Rate Structure: \n| Loan Amount | Interest Rate | Tenure |\n|---|---|---|\n| Rs. 25L | 8.50% | 20 Years |...",
  "keywords": "floating rate, 8.50%, tenure"
}
```

**Hindi Example:**
```json
{
  "id": "gold_loan_hi_eligibility_01",
  "loan_type": "GOLD_LOAN",
  "language": "hi",
  "section": "Eligibility",
  "context_header": "GOLD_LOAN - पात्रता (Eligibility)",
  "content": "पात्रता मानदंड:\n| आयु | 18 से 70 वर्ष |\n| आय प्रमाण | आवश्यक नहीं |...",
  "keywords": "पात्रता, सोना, 18 वर्ष, eligibility"
}
```

## Implementation Details

### Chunk ID Format
`{loan_type}_{language}_{section}_{counter}`

Examples:
- `home_loan_en_interest_rates_01`
- `gold_loan_hi_eligibility_01`
- `personal_loan_en_fees_02`

### Context Header Format

**English:**
- `{LOAN_TYPE} - {Section Name}`
- Example: `HOME_LOAN - Interest Rate Structure`

**Hindi:**
- `{LOAN_TYPE} - {Original Section} ({English Section})`
- Example: `GOLD_LOAN - पात्रता (Eligibility)`

### Table Handling

Tables are detected and converted to Markdown format:

**Input (CSV-style):**
```
Feature,Details
Loan Amount,Rs. 10L - Rs. 50L
Interest Rate,8.50% - 9.50%
```

**Output (Markdown):**
```markdown
| Feature | Details |
|---|---|
| Loan Amount | Rs. 10L - Rs. 50L |
| Interest Rate | 8.50% - 9.50% |
```

## Usage

The semantic chunker is automatically used when ingesting documents:

```bash
cd ai
python ingest_documents.py
```

The system will:
1. Load PDF documents
2. Apply pre-processing (noise removal)
3. Detect language
4. Chunk by semantic units (tables → FAQs → sections)
5. Extract and normalize metadata
6. Generate enriched chunks with proper IDs and context headers

## Benefits

1. **Accurate Retrieval:** Tables remain intact, preserving data relationships
2. **Precise Filtering:** Normalized metadata allows filtering by loan_type, section, language
3. **Context Preservation:** FAQs and sections maintain logical grouping
4. **Multilingual Support:** Handles both English and Hindi with proper normalization
5. **Sub-Loan Detection:** Identifies MUDRA, Term Loans, etc. within business loans

## Next Steps

Rebuild your vector database to apply the enhanced chunking:

```bash
cd ai
python ingest_documents.py
python ingest_documents_hindi.py
```

The new methodology will improve retrieval accuracy, especially for:
- Interest rate queries (tables preserved)
- FAQ queries (Q&A pairs together)
- Sub-loan type queries (MUDRA, Term Loans, etc.)

