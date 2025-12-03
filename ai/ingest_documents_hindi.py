# -*- coding: utf-8 -*-
"""
Hindi Document Ingestion Script (Combined)
Processes Hindi loan product and investment scheme PDFs and creates vector databases for RAG
Run this script to populate both Hindi loan and investment vector databases

This script processes:
- Hindi Loan Products (Personal, Home, Auto, Education, Gold, Business, LAP)
- Hindi Investment Schemes (PPF, NPS, SSY)
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from services.rag_service import RAGService
from utils import logger


def main():
    """Main ingestion function for Hindi documents"""
    print("=" * 60)
    print("हिंदी दस्तावेज इंगेस्शन")
    print("HINDI DOCUMENTS INGESTION")
    print("=" * 60)
    
    ai_dir = Path(__file__).parent
    base_docs_dir = ai_dir.parent / "backend" / "documents"
    
    # Process loan products
    print("\n📚 Processing Hindi Loan Products...")
    loan_docs_path = base_docs_dir / "loan_products_hindi"
    loan_persist_dir = "./chroma_db/loan_products_hindi"
    loan_collection = "loan_products_hindi"
    
    if not loan_docs_path.exists():
        print(f"❌ ERROR: Documents folder not found at {loan_docs_path}")
        print("   Please run: python backend/documents/create_loan_product_docs_hindi.py")
        return 1
    
    pdf_files = list(loan_docs_path.glob("*.pdf"))
    if not pdf_files:
        print(f"❌ ERROR: No PDF files found in {loan_docs_path}")
        return 1
    
    print(f"📄 Found {len(pdf_files)} PDF files for loans:")
    for pdf in pdf_files:
        print(f"   • {pdf.name}")
    
    # Create RAG service for loans
    loan_rag_service = RAGService(
        documents_path=str(loan_docs_path),
        persist_directory=loan_persist_dir,
        collection_name=loan_collection
    )
    
    print(f"\n🔄 Loading PDF documents for loans...")
    loan_documents = loan_rag_service.load_pdf_documents()
    print(f"✅ Loaded {len(loan_documents)} pages from loan PDFs")
    
    if loan_documents:
        print(f"\n🔄 Splitting loan documents into chunks...")
        loan_chunks = loan_rag_service.chunk_documents(loan_documents)
        print(f"✅ Created {len(loan_chunks)} chunks")
        
        print(f"\n🔄 Creating vector database for loans...")
        print(f"   Using embedding model: sentence-transformers/all-MiniLM-L6-v2")
        print(f"   This may take a few minutes...")
        
        try:
            loan_rag_service.vectorstore = loan_rag_service.create_vector_store(loan_chunks)
            print(f"✅ Loan vector database created successfully!")
        except Exception as e:
            print(f"\n❌ ERROR during loan vector store creation: {e}")
            logger.error("hindi_loan_ingestion_failed", error=str(e))
            return 1
    
    # Process investment schemes
    print("\n📚 Processing Hindi Investment Schemes...")
    investment_docs_path = base_docs_dir / "investment_schemes_hindi"
    investment_persist_dir = "./chroma_db/investment_schemes_hindi"
    investment_collection = "investment_schemes_hindi"
    
    if not investment_docs_path.exists():
        print(f"❌ ERROR: Documents folder not found at {investment_docs_path}")
        print("   Please run: python backend/documents/create_investment_scheme_docs_hindi.py")
        return 1
    
    pdf_files = list(investment_docs_path.glob("*.pdf"))
    if not pdf_files:
        print(f"❌ ERROR: No PDF files found in {investment_docs_path}")
        return 1
    
    print(f"📄 Found {len(pdf_files)} PDF files for investments:")
    for pdf in pdf_files:
        print(f"   • {pdf.name}")
    
    # Create RAG service for investments
    investment_rag_service = RAGService(
        documents_path=str(investment_docs_path),
        persist_directory=investment_persist_dir,
        collection_name=investment_collection
    )
    
    print(f"\n🔄 Loading PDF documents for investments...")
    investment_documents = investment_rag_service.load_pdf_documents()
    print(f"✅ Loaded {len(investment_documents)} pages from investment PDFs")
    
    if investment_documents:
        print(f"\n🔄 Splitting investment documents into chunks...")
        investment_chunks = investment_rag_service.chunk_documents(investment_documents)
        print(f"✅ Created {len(investment_chunks)} chunks")
        
        print(f"\n🔄 Creating vector database for investments...")
        print(f"   Using embedding model: sentence-transformers/all-MiniLM-L6-v2")
        print(f"   This may take a few minutes...")
        
        try:
            investment_rag_service.vectorstore = investment_rag_service.create_vector_store(investment_chunks)
            print(f"✅ Investment vector database created successfully!")
        except Exception as e:
            print(f"\n❌ ERROR during investment vector store creation: {e}")
            logger.error("hindi_investment_ingestion_failed", error=str(e))
            return 1
    
    # Comprehensive retrieval tests
    print(f"\n🔄 Running comprehensive retrieval tests...")
    print("=" * 60)
    
    # ===== LOAN TESTS =====
    if loan_rag_service.vectorstore:
        print("\n📚 LOAN RETRIEVAL TESTS (Hindi)")
        print("-" * 60)
        
        # Test 1: Multiple loan types with filters
        test_queries_loans = [
            ("होम लोन की ब्याज दर क्या है?", "HOME_LOAN", "Home Loan"),
            ("पर्सनल लोन की पात्रता क्या है?", "PERSONAL_LOAN", "Personal Loan"),
            ("MUDRA लोन क्या है?", "BUSINESS_LOAN_MUDRA", "Business Loan MUDRA"),
            ("एजुकेशन लोन के लिए कौन से दस्तावेज चाहिए?", "EDUCATION_LOAN", "Education Loan"),
            ("गोल्ड लोन की ब्याज दर क्या है?", "GOLD_LOAN", "Gold Loan"),
            ("ऑटो लोन की जानकारी दें", "AUTO_LOAN", "Auto Loan"),
        ]
        
        loan_test_results = []
        for query, expected_loan_type, loan_name in test_queries_loans:
            print(f"\n📝 Test: {loan_name}")
            print(f"   Query: \"{query}\"")
            print(f"   Expected: loan_type='{expected_loan_type}'")
            
            # Test with filter
            filtered_results = loan_rag_service.retrieve(
                query, 
                k=2, 
                filter={"loan_type": expected_loan_type}
            )
            
            if filtered_results:
                # Verify all results have correct loan_type
                correct_types = sum(1 for doc in filtered_results if doc.metadata.get("loan_type") == expected_loan_type)
                if correct_types == len(filtered_results):
                    print(f"   ✅ PASS: Found {len(filtered_results)} documents, all with correct loan_type")
                    loan_test_results.append(True)
                else:
                    print(f"   ⚠️  PARTIAL: Found {len(filtered_results)} documents, {correct_types} with correct loan_type")
                    loan_test_results.append(False)
            else:
                print(f"   ❌ FAIL: No documents found with filter")
                loan_test_results.append(False)
        
        # Test 2: Metadata quality check
        print(f"\n📊 METADATA QUALITY CHECK")
        print("-" * 60)
        all_loan_chunks = loan_rag_service.retrieve("लोन", k=50)  # Get many chunks
        if all_loan_chunks:
            loan_types_found = set()
            languages_found = set()
            sections_found = set()
            chunks_with_metadata = 0
            chunks_with_keywords = 0
            
            for doc in all_loan_chunks:
                loan_type = doc.metadata.get("loan_type")
                language = doc.metadata.get("language")
                section = doc.metadata.get("section")
                context_header = doc.metadata.get("context_header")
                keywords = doc.metadata.get("keywords")
                
                if loan_type:
                    loan_types_found.add(loan_type)
                if language:
                    languages_found.add(language)
                if section:
                    sections_found.add(section)
                if loan_type and language and section:
                    chunks_with_metadata += 1
                if keywords:
                    chunks_with_keywords += 1
            
            print(f"   Total chunks sampled: {len(all_loan_chunks)}")
            print(f"   Chunks with complete metadata: {chunks_with_metadata}/{len(all_loan_chunks)}")
            print(f"   Chunks with keywords: {chunks_with_keywords}/{len(all_loan_chunks)}")
            print(f"   Loan types found: {sorted(loan_types_found)}")
            print(f"   Languages found: {sorted(languages_found)}")
            print(f"   Sections found: {sorted(sections_found)[:10]}...")
            
            # Check for UNKNOWN_LOAN
            unknown_count = sum(1 for doc in all_loan_chunks if doc.metadata.get("loan_type") == "UNKNOWN_LOAN")
            if unknown_count > 0:
                print(f"   ⚠️  Warning: {unknown_count} chunks have UNKNOWN_LOAN type")
            else:
                print(f"   ✅ All chunks have valid loan types")
        
        # Test 3: Sub-loan type detection
        print(f"\n📝 Test: Business Loan Sub-Types")
        print(f"   Query: \"MUDRA लोन क्या है?\"")
        mudra_results = loan_rag_service.retrieve(
            "MUDRA लोन क्या है?",
            k=3,
            filter={"loan_type": "BUSINESS_LOAN_MUDRA"}
        )
        if mudra_results:
            print(f"   ✅ PASS: Found {len(mudra_results)} MUDRA loan documents")
        else:
            mudra_results_unfiltered = loan_rag_service.retrieve("MUDRA लोन", k=3)
            if mudra_results_unfiltered:
                print(f"   ⚠️  Found {len(mudra_results_unfiltered)} documents without filter")
                print(f"   Loan types: {[doc.metadata.get('loan_type') for doc in mudra_results_unfiltered]}")
        
        # Summary
        print(f"\n📊 LOAN TESTS SUMMARY")
        print(f"   Passed: {sum(loan_test_results)}/{len(loan_test_results)}")
    
    # ===== INVESTMENT TESTS =====
    if investment_rag_service.vectorstore:
        print("\n\n💼 INVESTMENT SCHEME RETRIEVAL TESTS (Hindi)")
        print("-" * 60)
        
        # Test 1: All investment schemes
        test_queries_investments = [
            ("पीपीएफ की ब्याज दर क्या है?", "PPF", "PPF"),
            ("NPS योजना के बारे में बताएं", "NPS", "NPS"),
            ("SSY की ब्याज दर क्या है?", "SSY", "SSY"),
        ]
        
        investment_test_results = []
        for query, expected_scheme, scheme_name in test_queries_investments:
            print(f"\n📝 Test: {scheme_name}")
            print(f"   Query: \"{query}\"")
            print(f"   Expected: scheme_type='{expected_scheme}'")
            
            # Try uppercase first
            filtered_results = investment_rag_service.retrieve(
                query, 
                k=2, 
                filter={"scheme_type": expected_scheme}
            )
            
            # If uppercase doesn't work, try lowercase
            if not filtered_results:
                filtered_results = investment_rag_service.retrieve(
                    query, 
                    k=2, 
                    filter={"scheme_type": expected_scheme.lower()}
                )
            
            if filtered_results:
                # Verify all results have correct scheme_type
                correct_types = sum(1 for doc in filtered_results 
                                  if doc.metadata.get("scheme_type", "").upper() == expected_scheme)
                if correct_types == len(filtered_results):
                    print(f"   ✅ PASS: Found {len(filtered_results)} documents, all with correct scheme_type")
                    investment_test_results.append(True)
                else:
                    print(f"   ⚠️  PARTIAL: Found {len(filtered_results)} documents, {correct_types} with correct scheme_type")
                    investment_test_results.append(False)
            else:
                print(f"   ❌ FAIL: No documents found with filter")
                investment_test_results.append(False)
        
        # Test 2: Metadata quality check
        print(f"\n📊 METADATA QUALITY CHECK")
        print("-" * 60)
        all_investment_chunks = investment_rag_service.retrieve("योजना", k=50)
        if all_investment_chunks:
            scheme_types_found = set()
            languages_found = set()
            sections_found = set()
            chunks_with_metadata = 0
            chunks_with_keywords = 0
            
            for doc in all_investment_chunks:
                scheme_type = doc.metadata.get("scheme_type")
                language = doc.metadata.get("language")
                section = doc.metadata.get("section")
                keywords = doc.metadata.get("keywords")
                
                if scheme_type:
                    scheme_types_found.add(scheme_type)
                if language:
                    languages_found.add(language)
                if section:
                    sections_found.add(section)
                if scheme_type and language and section:
                    chunks_with_metadata += 1
                if keywords:
                    chunks_with_keywords += 1
            
            print(f"   Total chunks sampled: {len(all_investment_chunks)}")
            print(f"   Chunks with complete metadata: {chunks_with_metadata}/{len(all_investment_chunks)}")
            print(f"   Chunks with keywords: {chunks_with_keywords}/{len(all_investment_chunks)}")
            print(f"   Scheme types found: {sorted(scheme_types_found)}")
            print(f"   Languages found: {sorted(languages_found)}")
            print(f"   Sections found: {sorted(sections_found)[:10]}...")
            
            # Check for UNKNOWN_SCHEME
            unknown_count = sum(1 for doc in all_investment_chunks 
                              if doc.metadata.get("scheme_type", "").upper() in ["UNKNOWN_SCHEME", "UNKNOWN"])
            if unknown_count > 0:
                print(f"   ⚠️  Warning: {unknown_count} chunks have unknown scheme type")
            else:
                print(f"   ✅ All chunks have valid scheme types")
        
        # Summary
        print(f"\n📊 INVESTMENT TESTS SUMMARY")
        print(f"   Passed: {sum(investment_test_results)}/{len(investment_test_results)}")
    
    # ===== FINAL SUMMARY =====
    print("\n" + "=" * 60)
    print("✅ COMPREHENSIVE TESTING COMPLETED!")
    print("=" * 60)
    
    print("\n" + "=" * 60)
    print("✅ HINDI INGESTION COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"\n💡 Vector databases ready:")
    print(f"   • Loans: {loan_persist_dir}")
    print(f"   • Investments: {investment_persist_dir}")
    print("\n🚀 Start the AI backend to use Hindi RAG:")
    print("   python main.py")
    
    return 0


if __name__ == "__main__":
    exit(main())

