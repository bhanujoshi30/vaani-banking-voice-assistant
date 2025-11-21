"""
RAG (Retrieval-Augmented Generation) Service
Handles document ingestion, vector storage, and retrieval for Q&A
"""
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from utils import logger


class OllamaEmbeddings(Embeddings):
    """Custom Ollama embeddings wrapper"""
    
    def __init__(self, model: str = "nomic-embed-text"):
        import ollama
        self.model = model
        self.client = ollama
        
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents"""
        embeddings = []
        for text in texts:
            response = self.client.embed(model=self.model, input=text)
            embeddings.append(response['embedding'])
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        response = self.client.embed(model=self.model, input=text)
        return response['embedding']


class RAGService:
    """Service for RAG operations - document loading, storage, and retrieval"""
    
    def __init__(
        self,
        documents_path: str = None,
        persist_directory: str = "./chroma_db",
        collection_name: str = "loan_products",
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """
        Initialize RAG service
        
        Args:
            documents_path: Path to documents folder (default: ../backend/documents/loan_products/)
            persist_directory: Path to store vector database
            collection_name: Name of the Chroma collection
            chunk_size: Size of text chunks for splitting
            chunk_overlap: Overlap between chunks
        """
        # Set default documents path to backend/documents/loan_products
        if documents_path is None:
            ai_dir = Path(__file__).parent.parent
            documents_path = ai_dir.parent / "backend" / "documents" / "loan_products"
        
        self.documents_path = Path(documents_path)
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize embeddings - use sentence-transformers (reliable, no external dependencies)
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            logger.info("rag_service_init", embedding_model="all-MiniLM-L6-v2")
        except Exception as e:
            logger.error("embeddings_init_failed", error=str(e))
            raise
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        
        # Vector store will be initialized when needed
        self.vectorstore: Optional[Chroma] = None
        
    def load_pdf_documents(self) -> List[Document]:
        """
        Load all PDF documents from the documents folder
        
        Returns:
            List of Document objects
        """
        documents = []
        pdf_files = list(self.documents_path.glob("*.pdf"))
        
        logger.info("loading_pdfs", count=len(pdf_files), path=str(self.documents_path))
        
        for pdf_path in pdf_files:
            try:
                loader = PyPDFLoader(str(pdf_path))
                docs = loader.load()
                
                # Add metadata - detect if it's loan or investment based on path/filename
                is_investment = "investment" in str(self.documents_path).lower() or "_scheme_guide" in pdf_path.stem
                
                for doc in docs:
                    doc.metadata["source"] = pdf_path.name
                    if is_investment:
                        doc.metadata["scheme_type"] = pdf_path.stem.replace("_scheme_guide", "")
                        doc.metadata["document_type"] = "investment"
                    else:
                        doc.metadata["loan_type"] = pdf_path.stem.replace("_product_guide", "")
                        doc.metadata["document_type"] = "loan"
                
                documents.extend(docs)
                logger.info("pdf_loaded", file=pdf_path.name, pages=len(docs), type="investment" if is_investment else "loan")
                
            except Exception as e:
                logger.error("pdf_load_error", file=pdf_path.name, error=str(e))
        
        return documents
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks
        
        Args:
            documents: List of documents to chunk
            
        Returns:
            List of chunked documents
        """
        chunks = self.text_splitter.split_documents(documents)
        logger.info("documents_chunked", 
                   original_count=len(documents),
                   chunk_count=len(chunks))
        return chunks
    
    def create_vector_store(self, documents: List[Document]) -> Chroma:
        """
        Create vector store from documents
        
        Args:
            documents: List of documents to add to vector store
            
        Returns:
            Chroma vector store instance
        """
        try:
            # Create new vector store
            vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                collection_name=self.collection_name,
                persist_directory=self.persist_directory
            )
            
            logger.info("vectorstore_created",
                       document_count=len(documents),
                       collection=self.collection_name)
            
            return vectorstore
            
        except Exception as e:
            logger.error("vectorstore_creation_error", error=str(e))
            raise
    
    def load_vector_store(self) -> Optional[Chroma]:
        """
        Load existing vector store from disk
        
        Returns:
            Chroma vector store or None if doesn't exist
        """
        try:
            if Path(self.persist_directory).exists():
                vectorstore = Chroma(
                    collection_name=self.collection_name,
                    embedding_function=self.embeddings,
                    persist_directory=self.persist_directory
                )
                logger.info("vectorstore_loaded", collection=self.collection_name)
                return vectorstore
            else:
                logger.warning("vectorstore_not_found", path=self.persist_directory)
                return None
        except Exception as e:
            logger.error("vectorstore_load_error", error=str(e))
            return None
    
    def initialize(self, force_rebuild: bool = False) -> None:
        """
        Initialize the RAG system - load or create vector store
        
        Args:
            force_rebuild: If True, rebuild vector store even if exists
        """
        # Try to load existing vector store
        if not force_rebuild:
            self.vectorstore = self.load_vector_store()
            if self.vectorstore:
                logger.info("rag_initialized", mode="loaded_existing")
                return
        
        # Load and process documents
        logger.info("rag_building", mode="creating_new")
        documents = self.load_pdf_documents()
        
        if not documents:
            logger.warning("no_documents_found", path=str(self.documents_path))
            return
        
        # Chunk documents
        chunks = self.chunk_documents(documents)
        
        # Create vector store
        self.vectorstore = self.create_vector_store(chunks)
        logger.info("rag_initialized", mode="created_new", chunks=len(chunks))
    
    def retrieve(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Retrieve relevant documents for a query
        
        Args:
            query: Search query
            k: Number of documents to retrieve
            filter: Optional metadata filter
            
        Returns:
            List of relevant documents
        """
        if not self.vectorstore:
            logger.error("vectorstore_not_initialized")
            return []
        
        try:
            if filter:
                results = self.vectorstore.similarity_search(
                    query, k=k, filter=filter
                )
            else:
                results = self.vectorstore.similarity_search(query, k=k)
            
            logger.info("retrieval_completed", query_length=len(query), results=len(results))
            return results
            
        except Exception as e:
            logger.error("retrieval_error", error=str(e))
            return []
    
    def retrieve_with_scores(
        self,
        query: str,
        k: int = 4
    ) -> List[tuple[Document, float]]:
        """
        Retrieve documents with similarity scores
        
        Args:
            query: Search query
            k: Number of documents to retrieve
            
        Returns:
            List of (document, score) tuples
        """
        if not self.vectorstore:
            logger.error("vectorstore_not_initialized")
            return []
        
        try:
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            logger.info("retrieval_with_scores_completed", 
                       query_length=len(query),
                       results=len(results))
            return results
        except Exception as e:
            logger.error("retrieval_error", error=str(e))
            return []
    
    def get_context_for_query(self, query: str, k: int = 4) -> str:
        """
        Get formatted context string for a query
        
        Args:
            query: Search query
            k: Number of documents to retrieve
            
        Returns:
            Formatted context string
        """
        documents = self.retrieve(query, k=k)
        
        if not documents:
            return ""
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get("source", "Unknown")
            loan_type = doc.metadata.get("loan_type", "").replace("_", " ").title()
            context_parts.append(
                f"[Source {i}: {loan_type} - {source}]\n{doc.page_content}\n"
            )
        
        context = "\n".join(context_parts)
        logger.info("context_generated", 
                   query_length=len(query),
                   context_length=len(context),
                   sources=len(documents))
        
        return context


# Global RAG service instance
_rag_service: Optional[RAGService] = None


def get_rag_service(documents_type: str = None) -> RAGService:
    """
    Get or create RAG service instance
    
    Args:
        documents_type: "loan" or "investment" - determines which documents to load.
                        If None, defaults to "loan" for backward compatibility.
    """
    global _rag_service
    
    if documents_type is None:
        documents_type = "loan"
    
    # Determine documents path based on type
    if documents_type == "investment":
        ai_dir = Path(__file__).parent.parent
        documents_path = ai_dir.parent / "backend" / "documents" / "investment_schemes"
        collection_name = "investment_schemes"
    else:
        documents_path = None  # Will use default loan_products path
        collection_name = "loan_products"
    
    # Create new service if doesn't exist or if collection type changed
    if _rag_service is None or getattr(_rag_service, '_documents_type', None) != documents_type:
        _rag_service = RAGService(
            documents_path=str(documents_path) if documents_path else None,
            collection_name=collection_name
        )
        _rag_service._documents_type = documents_type  # Store type for reference
        _rag_service.initialize()
    
    return _rag_service


def initialize_rag(force_rebuild: bool = False) -> None:
    """Initialize RAG service (to be called on startup)"""
    service = get_rag_service()
    if force_rebuild:
        service.initialize(force_rebuild=True)
