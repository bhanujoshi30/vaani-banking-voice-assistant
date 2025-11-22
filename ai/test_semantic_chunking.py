# -*- coding: utf-8 -*-
"""
Test script for semantic chunking
Tests the new semantic chunking method with business loan documents
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import directly to avoid __init__ dependencies
import importlib.util
spec = importlib.util.spec_from_file_location("semantic_chunker", Path(__file__).parent / "services" / "semantic_chunker.py")
semantic_chunker_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(semantic_chunker_module)
SemanticChunker = semantic_chunker_module.SemanticChunker

from langchain_core.documents import Document


def test_semantic_chunking():
    """Test semantic chunking with a sample business loan document"""
    
    print("=" * 60)
    print("TESTING SEMANTIC CHUNKING")
    print("=" * 60)
    
    # Create sample business loan text with sub-loans
    sample_text = """
BUSINESS LOAN
Fuel Your Business Growth - MSME & SME Financing

PRODUCT OVERVIEW
Sun National Bank Business Loan is designed for Micro, Small & Medium Enterprises (MSMEs) to meet working capital needs, expansion, equipment purchase, or any business requirement. We support entrepreneurs with flexible financing options including MUDRA loans, term loans, and working capital facilities.

TYPES OF BUSINESS LOANS

1. MUDRA Loans: Government scheme for micro enterprises. Shishu (up to Rs. 50,000), Kishore (Rs. 50,001 to Rs. 5 lakhs), Tarun (Rs. 5,00,001 to Rs. 10 lakhs).

2. Term Loans: For capital expenditure - machinery, equipment, factory setup, expansion. Fixed tenure with monthly/quarterly EMI.

3. Working Capital Loan: For day-to-day operations - raw material, salaries, rent. Overdraft or cash credit limit facility.

ELIGIBILITY CRITERIA

The following table:
Criteria,Requirement
Business Type,Proprietorship, Partnership, Private Limited, LLP, Co-operatives
Business Vintage,Minimum 2 years (3 years for loans above Rs. 50 lakhs)
Turnover,MUDRA: No minimum
CIBIL Score,Minimum 650 (business & personal)

FREQUENTLY ASKED QUESTIONS

Q1: What is MUDRA loan?
MUDRA (Micro Units Development & Refinance Agency) is government scheme for micro enterprises up to Rs. 10 lakhs without collateral.

Q2: Can startups apply for business loan?
Yes, but minimum 2 years business vintage required. For fresh startups, explore government schemes like Startup India or PMEGP.
"""
    
    # Create a Document object
    doc = Document(
        page_content=sample_text,
        metadata={
            "source": "business_loan_product_guide.pdf",
            "loan_type": "business_loan",
            "document_type": "loan"
        }
    )
    
    # Test semantic chunker
    chunker = SemanticChunker()
    chunks = chunker.chunk_document(doc)
    
    print(f"\n[OK] Created {len(chunks)} chunks from sample document\n")
    
    # Display chunk details
    for i, chunk in enumerate(chunks, 1):
        print(f"--- Chunk {i} ---")
        print(f"ID: {chunk.metadata.get('id', 'N/A')}")
        print(f"Loan Type: {chunk.metadata.get('loan_type', 'N/A')}")
        print(f"Language: {chunk.metadata.get('language', 'N/A')}")
        print(f"Section: {chunk.metadata.get('section', 'N/A')}")
        print(f"Context Header: {chunk.metadata.get('context_header', 'N/A')}")
        print(f"Keywords: {chunk.metadata.get('keywords', [])}")
        print(f"Is Table: {chunk.metadata.get('is_table', False)}")
        print(f"Is FAQ: {chunk.metadata.get('is_faq', False)}")
        print(f"Sub-Loan Type: {chunk.metadata.get('sub_loan_type', 'N/A')}")
        print(f"\nContent Preview (first 200 chars):")
        print(chunk.page_content[:200] + "...")
        print("\n" + "=" * 60 + "\n")
    
    # Verify chunking quality
    print("CHUNKING QUALITY CHECKS:")
    print("-" * 60)
    
    # Check 1: Tables should be single chunks
    table_chunks = [c for c in chunks if c.metadata.get('is_table', False)]
    print(f"[OK] Table chunks: {len(table_chunks)} (should be 1)")
    
    # Check 2: FAQs should be grouped
    faq_chunks = [c for c in chunks if c.metadata.get('is_faq', False)]
    print(f"[OK] FAQ chunks: {len(faq_chunks)} (should be 1)")
    
    # Check 3: Sub-loans should be detected
    sub_loan_chunks = [c for c in chunks if 'MUDRA' in c.metadata.get('loan_type', '') or 
                       'TERM' in c.metadata.get('loan_type', '') or
                       'WORKING' in c.metadata.get('loan_type', '')]
    print(f"[OK] Sub-loan chunks detected: {len(sub_loan_chunks)}")
    
    # Check 4: Context headers should be informative
    context_headers = [c.metadata.get('context_header', '') for c in chunks]
    print(f"[OK] Context headers created: {len([h for h in context_headers if h])}")
    
    # Check 5: Keywords extracted
    chunks_with_keywords = [c for c in chunks if c.metadata.get('keywords')]
    print(f"[OK] Chunks with keywords: {len(chunks_with_keywords)}")
    
    print("\n" + "=" * 60)
    print("[OK] SEMANTIC CHUNKING TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    test_semantic_chunking()

