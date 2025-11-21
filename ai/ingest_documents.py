# -*- coding: utf-8 -*-
"""
Document Ingestion Script
Processes loan product PDFs and creates vector database for RAG
Run this script to populate the vector database with loan documents
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from services.rag_service import RAGService
from utils import logger


def main():
    """Main ingestion function"""
    print("=" * 60)
    print("LOAN PRODUCT DOCUMENTS INGESTION")
    print("=" * 60)
    
    # Initialize RAG service with explicit paths for loan products
    ai_dir = Path(__file__).parent
    base_docs_dir = ai_dir.parent / "backend" / "documents"
    documents_path = base_docs_dir / "loan_products"
    persist_directory = "./chroma_db/loan_products"
    collection_name = "loan_products"
    
    rag_service = RAGService(
        documents_path=str(documents_path),
        persist_directory=persist_directory,
        collection_name=collection_name
    )
    
    print(f"\n📂 Document Source: {rag_service.documents_path}")
    print(f"💾 Vector Store Path: {rag_service.persist_directory}")
    print(f"📦 Collection Name: {rag_service.collection_name}")
    print(f"📏 Chunk Size: {rag_service.chunk_size}")
    print(f"🔗 Chunk Overlap: {rag_service.chunk_overlap}")
    
    # Check if documents exist
    if not documents_path.exists():
        print(f"\n❌ ERROR: Documents folder not found at {documents_path}")
        print("   Please ensure loan product PDFs are in backend/documents/loan_products/")
        print("   Run: python backend/documents/create_loan_product_docs.py")
        return 1
    
    pdf_files = list(rag_service.documents_path.glob("*.pdf"))
    if not pdf_files:
        print(f"\n❌ ERROR: No PDF files found in {rag_service.documents_path}")
        return 1
    
    print(f"\n📄 Found {len(pdf_files)} PDF files:")
    for pdf in pdf_files:
        print(f"   • {pdf.name}")
    
    # Load documents
    print("\n🔄 Loading PDF documents...")
    documents = rag_service.load_pdf_documents()
    print(f"✅ Loaded {len(documents)} pages from PDFs")
    
    if not documents:
        print("❌ ERROR: No documents were loaded")
        return 1
    
    # Chunk documents
    print(f"\n🔄 Splitting documents into chunks...")
    chunks = rag_service.chunk_documents(documents)
    print(f"✅ Created {len(chunks)} chunks")
    
    # Create vector store
    print(f"\n🔄 Creating vector database...")
    print(f"   Using embedding model: sentence-transformers/all-MiniLM-L6-v2")
    print(f"   This may take a few minutes...")
    
    try:
        rag_service.vectorstore = rag_service.create_vector_store(chunks)
        print(f"✅ Vector database created successfully!")
        
        # Test retrieval
        print(f"\n🔄 Testing retrieval...")
        test_query = "What is the interest rate for home loans?"
        results = rag_service.retrieve(test_query, k=2)
        
        if results:
            print(f"✅ Retrieval test successful!")
            print(f"\n📝 Sample query: \"{test_query}\"")
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
        print("✅ INGESTION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"\n💡 Vector database ready at: {rag_service.persist_directory}")
        print("   You can now use RAG for loan product Q&A!")
        print("\n🚀 Start the AI backend to use RAG:")
        print("   python main.py")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR during vector store creation: {e}")
        logger.error("ingestion_failed", error=str(e))
        return 1


if __name__ == "__main__":
    exit(main())
