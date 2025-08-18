"""Main document processing pipeline for RAG system."""

import logging
from typing import List, Dict, Any
from pathlib import Path

from .pdf_extractor import PDFExtractor
from .chunker import AgriculturalChunker
from .embedding_service import EmbeddingService
from .vector_store import VectorStore
from .models import AgriculturalChunk
from .config import RAGConfig

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Main pipeline for processing agricultural documents into RAG-ready chunks."""
    
    def __init__(self, config: RAGConfig = None):
        """Initialize the document processor.
        
        Args:
            config: RAG configuration, uses default if None
        """
        self.config = config or RAGConfig()
        self.pdf_extractor = PDFExtractor()
        self.chunker = AgriculturalChunker(config)
        self.embedding_service = EmbeddingService(config)
        self.vector_store = VectorStore(config)
        
        logger.info("Document processor initialized")
    
    async def process_document(self, pdf_path: str, document_type: str = None) -> List[AgriculturalChunk]:
        """Process a PDF document into chunks.
        
        Args:
            pdf_path: Path to the PDF file
            document_type: Type of document (auto-detected if None)
            
        Returns:
            List of processed agricultural chunks
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            ValueError: If PDF processing fails
        """
        try:
            logger.info(f"Processing document: {pdf_path}")
            
            # Auto-detect document type if not provided
            if not document_type:
                document_type = self._detect_document_type(pdf_path)
            
            # Extract text from PDF
            logger.info("Extracting text from PDF...")
            text = self.pdf_extractor.extract(pdf_path)
            logger.info(f"Extracted {len(text)} characters from PDF")
            
            # Create chunks from text
            logger.info("Creating chunks from text...")
            chunks = self.chunker.create_chunks(text, document_type)
            logger.info(f"Created {len(chunks)} chunks")
            
            # Generate embeddings for chunks
            logger.info("Generating embeddings for chunks...")
            self._generate_embeddings(chunks)
            logger.info("Embeddings generated successfully")
            
            # Store chunks in vector store
            logger.info("Storing chunks in vector store...")
            self.vector_store.store_chunks(chunks)
            logger.info("Chunks stored in vector store")
            
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to process document {pdf_path}: {e}")
            raise
    
    async def process_documents_batch(self, pdf_paths: List[str], document_types: List[str] = None) -> Dict[str, List[AgriculturalChunk]]:
        """Process multiple PDF documents in batch.
        
        Args:
            pdf_paths: List of PDF file paths
            document_types: List of document types (auto-detected if None)
            
        Returns:
            Dictionary mapping file paths to lists of chunks
        """
        if document_types and len(document_types) != len(pdf_paths):
            raise ValueError("document_types list must have same length as pdf_paths")
        
        results = {}
        
        for i, pdf_path in enumerate(pdf_paths):
            try:
                document_type = document_types[i] if document_types else None
                chunks = await self.process_document(pdf_path, document_type)
                results[pdf_path] = chunks
                
                logger.info(f"Successfully processed {pdf_path}: {len(chunks)} chunks")
                
            except Exception as e:
                logger.error(f"Failed to process {pdf_path}: {e}")
                results[pdf_path] = []  # Empty list for failed documents
        
        return results
    
    def _generate_embeddings(self, chunks: List[AgriculturalChunk]) -> None:
        """Generate embeddings for a list of chunks.
        
        Args:
            chunks: List of chunks to generate embeddings for
        """
        try:
            # Extract text content from chunks
            texts = [chunk.content for chunk in chunks]
            
            # Generate embeddings in batch
            embeddings = self.embedding_service.embed_batch(texts)
            
            # Assign embeddings to chunks
            for chunk, embedding in zip(chunks, embeddings):
                chunk.embeddings = embedding
                
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    def _detect_document_type(self, pdf_path: str) -> str:
        """Auto-detect document type from file path or content.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Detected document type
        """
        path_lower = pdf_path.lower()
        
        if 'gap' in path_lower or 'good agricultural practice' in path_lower:
            return 'bharat_gap'
        elif 'handbook' in path_lower or 'manual' in path_lower:
            return 'farmer_handbook'
        elif 'guide' in path_lower:
            return 'agricultural_guide'
        else:
            return 'agricultural_document'
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing pipeline statistics.
        
        Returns:
            Dictionary with processing statistics
        """
        try:
            vector_store_info = self.vector_store.get_collection_info()
            
            return {
                "pdf_extractor": "PyPDF2/pdfplumber",
                "chunker": "AgriculturalChunker",
                "embedding_service": self.embedding_service.config.embedding_model,
                "vector_store": vector_store_info,
                "config": {
                    "max_tokens": self.config.max_tokens,
                    "overlap_tokens": self.config.overlap_tokens,
                    "min_chunk_tokens": self.config.min_chunk_tokens,
                    "embedding_dimensions": self.config.embedding_dimensions
                }
            }
        except Exception as e:
            logger.error(f"Failed to get processing stats: {e}")
            return {"error": str(e)}
    
    def reset_vector_store(self) -> None:
        """Reset the vector store (clear all stored chunks).
        
        Warning: This will remove all stored chunks!
        """
        try:
            self.vector_store.reset_collection()
            logger.info("Vector store reset successfully")
        except Exception as e:
            logger.error(f"Failed to reset vector store: {e}")
            raise
    
    def get_pdf_info(self, pdf_path: str) -> Dict[str, Any]:
        """Get information about a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with PDF information
        """
        try:
            return self.pdf_extractor.get_pdf_info(pdf_path)
        except Exception as e:
            logger.error(f"Failed to get PDF info: {e}")
            return {"error": str(e)}
