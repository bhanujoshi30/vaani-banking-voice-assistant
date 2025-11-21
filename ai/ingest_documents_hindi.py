"""
Hindi Document Ingestion Script
Processes Hindi loan product and investment scheme PDFs and creates vector database for RAG
Run this script to populate the Hindi vector database with documents
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
    
    # Test retrieval
    print(f"\n🔄 Testing retrieval...")
    test_query_hi = "होम लोन की ब्याज दर क्या है?"
    test_query_en = "What is the interest rate for home loans?"
    
    if loan_rag_service.vectorstore:
        results = loan_rag_service.retrieve(test_query_hi, k=2)
        if results:
            print(f"✅ Retrieval test successful!")
            print(f"\n📝 Sample query (Hindi): \"{test_query_hi}\"")
            print(f"   Found {len(results)} relevant documents:")
            for i, doc in enumerate(results, 1):
                source = doc.metadata.get("source", "Unknown")
                loan_type = doc.metadata.get("loan_type", "Unknown")
                preview = doc.page_content[:150].replace("\n", " ")
                print(f"   {i}. {source} ({loan_type})")
                print(f"      Preview: {preview}...")
        else:
            print("⚠️  Warning: Retrieval test returned no results")
    
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

