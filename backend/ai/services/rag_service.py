"""
RAG (Retrieval-Augmented Generation) Service
Handles document ingestion, vector storage, and retrieval for Q&A
"""
import json
import os
import time
from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from utils import logger
from utils.demo_logging import demo_logger
from services.semantic_chunker import SemanticChunker


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
        
        # Initialize text splitter (fallback for simple splitting)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        
        # Initialize semantic chunker for intelligent chunking
        self.semantic_chunker = SemanticChunker(
            min_chunk_size=200,
            max_chunk_size=2000
        )
        
        # Vector store will be initialized when needed
        self.vectorstore = None
        self._context_cache: OrderedDict[str, Tuple[str, float]] = OrderedDict()
        self._cache_max_size = 128
        self._cache_ttl_seconds = 120
        
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
    
    def chunk_documents(self, documents: List[Document], use_semantic: bool = True) -> List[Document]:
        """
        Split documents into chunks using semantic chunking
        
        Args:
            documents: List of documents to chunk
            use_semantic: If True, use semantic chunking; otherwise use character-based splitting
            
        Returns:
            List of chunked documents with enriched metadata
        """
        if use_semantic:
            # Use semantic chunker for intelligent, section-based chunking
            chunks = self.semantic_chunker.chunk_documents(documents)
            logger.info("documents_chunked_semantic", 
                       original_count=len(documents),
                       chunk_count=len(chunks))
        else:
            # Fallback to character-based splitting
            chunks = self.text_splitter.split_documents(documents)
            logger.info("documents_chunked_character", 
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
            # Filter complex metadata (lists, dicts) that ChromaDB doesn't support
            from langchain_community.vectorstores.utils import filter_complex_metadata
            
            # Filter metadata to only include simple types (str, int, float, bool, None)
            filtered_documents = filter_complex_metadata(documents)
            
            # Create new vector store
            vectorstore = Chroma.from_documents(
                documents=filtered_documents,
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
            # Demo logging: RAG retrieval start
            demo_logger.rag_retrieval(
                query=query,
                collection=self.collection_name,
                k=k,
                filter=filter,
                language=getattr(self, '_language', 'en-IN'),
            )
            
            if filter:
                # Log filter details for debugging
                logger.info(
                    "retrieval_with_filter",
                    query_preview=query[:100],
                    filter=filter,
                    k=k
                )
                results = self.vectorstore.similarity_search(
                    query, k=k, filter=filter
                )
                
                # Log retrieved document metadata for verification
                if results:
                    retrieved_loan_types = [doc.metadata.get("loan_type", "N/A") for doc in results]
                    retrieved_sources = [doc.metadata.get("source", "N/A") for doc in results]
                    logger.info(
                        "retrieval_results_with_filter",
                        query_length=len(query),
                        results_count=len(results),
                        expected_filter=filter.get("loan_type", "N/A"),
                        retrieved_loan_types=retrieved_loan_types,
                        retrieved_sources=retrieved_sources[:3],  # First 3 sources
                        content_previews=[doc.page_content[:150].replace("\n", " ") for doc in results[:2]]
                    )
                    
                    # Verify filter worked correctly
                    expected_loan_type = filter.get("loan_type", "").upper()
                    mismatched = [
                        (i, doc.metadata.get("loan_type", ""))
                        for i, doc in enumerate(results)
                        if doc.metadata.get("loan_type", "").upper() != expected_loan_type
                    ]
                    if mismatched:
                        logger.warning(
                            "filter_mismatch_detected",
                            expected=expected_loan_type,
                            mismatched_indices_and_types=mismatched,
                            query=query[:100]
                        )
            else:
                results = self.vectorstore.similarity_search(query, k=k)
            
            # Demo logging: RAG results
            demo_logger.rag_results(results)
            
            logger.info("retrieval_completed", query_length=len(query), results=len(results))
            return results
            
        except Exception as e:
            logger.error("retrieval_error", error=str(e), filter=filter)
            demo_logger.error("RAG retrieval failed", error=str(e), filter=filter)
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
            # Demo logging: RAG retrieval with scores
            demo_logger.rag_retrieval(
                query=query,
                collection=self.collection_name,
                k=k,
                with_scores=True,
            )
            
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            
            # Extract documents and scores for demo logging
            documents = [doc for doc, score in results]
            scores = [score for doc, score in results]
            demo_logger.rag_results(documents, scores=scores)
            
            logger.info("retrieval_with_scores_completed", 
                       query_length=len(query),
                       results=len(results))
            return results
        except Exception as e:
            logger.error("retrieval_error", error=str(e))
            demo_logger.error("RAG retrieval with scores failed", error=str(e))
            return []
    
    def _normalize_query(self, query: str) -> str:
        return " ".join(query.split()).lower()

    def _make_cache_key(self, query: str, k: int, metadata_filter: Optional[Dict[str, Any]]) -> str:
        filter_part = ""
        if metadata_filter:
            try:
                filter_part = json.dumps(metadata_filter, sort_keys=True)
            except TypeError:
                filter_part = str(sorted(metadata_filter.items()))
        return f"{self._normalize_query(query)}|k={k}|f={filter_part}"

    def _get_cached_context(self, cache_key: str) -> Optional[str]:
        cached = self._context_cache.get(cache_key)
        if not cached:
            return None
        context, expires_at = cached
        if time.time() < expires_at:
            self._context_cache.move_to_end(cache_key)
            logger.info("rag_context_cache_hit", cache_key=cache_key)
            return context
        self._context_cache.pop(cache_key, None)
        return None

    def _store_cached_context(self, cache_key: str, context: str) -> None:
        self._context_cache[cache_key] = (context, time.time() + self._cache_ttl_seconds)
        self._context_cache.move_to_end(cache_key)
        if len(self._context_cache) > self._cache_max_size:
            evicted_key, _ = self._context_cache.popitem(last=False)
            logger.debug("rag_context_cache_evict", cache_key=evicted_key)

    def get_context_for_query(self, query: str, k: int = 4, filter: Optional[Dict[str, Any]] = None) -> str:
        """
        Get formatted context string for a query
        
        Args:
            query: Search query
            k: Number of documents to retrieve
            filter: Optional metadata filter to narrow retrieval scope
            
        Returns:
            Formatted context string
        """
        cache_key = self._make_cache_key(query, k, filter)
        cached_context = self._get_cached_context(cache_key)
        if cached_context is not None:
            return cached_context

        documents = self.retrieve(query, k=k, filter=filter)
        
        if not documents:
            return ""
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get("source", "Unknown")
            loan_type = doc.metadata.get("loan_type", "")
            scheme_type = doc.metadata.get("scheme_type", "")
            doc_type = doc.metadata.get("document_type", "")
            
            # Format the type label
            if doc_type == "investment":
                type_label = scheme_type.replace("_", " ").title() if scheme_type else "Investment"
            else:
                type_label = loan_type.replace("_", " ").title() if loan_type else "Loan"
            
            context_parts.append(
                f"[Source {i}: {type_label} - {source}]\n{doc.page_content}\n"
            )
        
        context = "\n".join(context_parts)
        logger.info(
            "context_generated",
            query_length=len(query),
            context_length=len(context),
            sources=len(documents),
            cache_hit=False,
            metadata_filtered=bool(filter),
        )
        self._store_cached_context(cache_key, context)
        
        return context


# Global RAG service instances cache: (documents_type, language) -> RAGService
_rag_service_cache: Dict[Tuple[str, str], RAGService] = {}


def get_rag_service(documents_type: str = None, language: str = "en-IN") -> RAGService:
    """
    Get or create RAG service instance
    
    Args:
        documents_type: "loan" or "investment" - determines which documents to load.
                        If None, defaults to "loan" for backward compatibility.
        language: "en-IN" or "hi-IN" - determines which language vector database to use.
                 Defaults to "en-IN".
    """
    global _rag_service_cache
    
    if documents_type is None:
        documents_type = "loan"
    
    # Normalize language code
    if language not in ["en-IN", "hi-IN"]:
        language = "en-IN"  # Default to English if invalid language
    
    # Create cache key
    cache_key = (documents_type, language)
    
    # Check if service already exists in cache
    if cache_key in _rag_service_cache:
        return _rag_service_cache[cache_key]
    
    # Determine documents path and collection name based on type and language
    ai_dir = Path(__file__).parent.parent
    base_docs_dir = ai_dir.parent / "backend" / "documents"
    
    if language == "hi-IN":
        # Hindi documents
        if documents_type == "investment":
            documents_path = base_docs_dir / "investment_schemes_hindi"
            collection_name = "investment_schemes_hindi"
            persist_directory = "./chroma_db/investment_schemes_hindi"
        else:
            documents_path = base_docs_dir / "loan_products_hindi"
            collection_name = "loan_products_hindi"
            persist_directory = "./chroma_db/loan_products_hindi"
    else:
        # English documents (default)
        if documents_type == "investment":
            documents_path = base_docs_dir / "investment_schemes"
            collection_name = "investment_schemes"
            persist_directory = "./chroma_db/investment_schemes"
        else:
            documents_path = base_docs_dir / "loan_products"
            collection_name = "loan_products"
            persist_directory = "./chroma_db/loan_products"
    
    # Create new service
    rag_service = RAGService(
        documents_path=str(documents_path),
        collection_name=collection_name,
        persist_directory=persist_directory
    )
    rag_service._documents_type = documents_type  # Store type for reference
    rag_service._language = language  # Store language for reference
    rag_service.initialize()
    
    # Cache the service
    _rag_service_cache[cache_key] = rag_service
    
    return rag_service


def initialize_rag(force_rebuild: bool = False) -> None:
    """Initialize RAG service (to be called on startup)"""
    service = get_rag_service()
    if force_rebuild:
        service.initialize(force_rebuild=True)
