"""Vector store service using ChromaDB."""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

from .models import AgriculturalChunk
from .config import RAGConfig

logger = logging.getLogger(__name__)


class VectorStore:
    """Vector store service using ChromaDB for storing and retrieving agricultural chunks."""
    
    def __init__(self, config: RAGConfig = None):
        """Initialize the vector store.
        
        Args:
            config: RAG configuration, uses default if None
            
        Raises:
            ImportError: If ChromaDB is not available
        """
        if not CHROMA_AVAILABLE:
            raise ImportError(
                "ChromaDB is not available. Please install it: pip install chromadb"
            )
        
        self.config = config or RAGConfig()
        self.client = None
        self.collection = None
        self._initialize_store()
    
    def _initialize_store(self) -> None:
        """Initialize the ChromaDB client and collection."""
        try:
            # Create persist directory if it doesn't exist
            persist_path = Path(self.config.vector_store_path)
            persist_path.mkdir(parents=True, exist_ok=True)
            
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=str(persist_path),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="agricultural_chunks",
                metadata={
                    "description": "Agricultural document chunks with embeddings",
                    "embedding_dimensions": self.config.embedding_dimensions
                }
            )
            
            logger.info(f"Vector store initialized at {persist_path}")
            logger.info(f"Collection: {self.collection.name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise
    
    def store_chunks(self, chunks: List[AgriculturalChunk]) -> None:
        """Store chunks in the vector store.
        
        Args:
            chunks: List of agricultural chunks to store
            
        Raises:
            ValueError: If chunks list is empty
            RuntimeError: If vector store is not initialized
        """
        if not chunks:
            raise ValueError("Chunks list cannot be empty")
        
        if not self.collection:
            raise RuntimeError("Vector store not initialized")
        
        try:
            # Prepare data for ChromaDB
            ids = []
            texts = []
            embeddings = []
            metadatas = []
            
            for chunk in chunks:
                if not chunk.embedding:
                    logger.warning(f"Chunk {chunk.source_document}_{chunk.chunk_index} has no embedding, skipping")
                    continue
                
                # Create unique ID from source_document and chunk_index
                chunk_id = f"{chunk.source_document}_{chunk.chunk_index}"
                ids.append(chunk_id)
                texts.append(chunk.content)
                embeddings.append(chunk.embedding)
                
                # Convert metadata to dict, handling datetime objects and lists
                metadata_dict = chunk.metadata.dict()
                
                # Handle optional datetime fields gracefully
                if 'created_at' in metadata_dict and metadata_dict['created_at']:
                    metadata_dict['created_at'] = metadata_dict['created_at'].isoformat()
                else:
                    metadata_dict['created_at'] = datetime.now().isoformat()
                    
                if 'last_updated' in metadata_dict and metadata_dict['last_updated']:
                    metadata_dict['last_updated'] = metadata_dict['last_updated'].isoformat()
                else:
                    metadata_dict['last_updated'] = datetime.now().isoformat()
                
                # Convert lists to JSON strings for ChromaDB compatibility
                metadata_dict = self._prepare_metadata_for_chroma(metadata_dict)
                
                metadatas.append(metadata_dict)
            
            if not ids:
                logger.warning("No valid chunks to store")
                return
            
            # Add to collection
            self.collection.add(
                ids=ids,
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas
            )
            
            logger.info(f"Successfully stored {len(ids)} chunks in vector store")
            
        except Exception as e:
            logger.error(f"Failed to store chunks: {e}")
            raise
    
    def _prepare_metadata_for_chroma(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare metadata for ChromaDB storage by converting incompatible types.
        
        Args:
            metadata: Original metadata dictionary
            
        Returns:
            ChromaDB-compatible metadata dictionary
        """
        chroma_metadata = {}
        
        for key, value in metadata.items():
            if isinstance(value, list):
                # Convert lists to JSON strings
                chroma_metadata[key] = json.dumps(value)
            elif isinstance(value, dict):
                # Convert dicts to JSON strings
                chroma_metadata[key] = json.dumps(value)
            elif value is None:
                # Convert None to empty string
                chroma_metadata[key] = ""
            else:
                # Keep other types as is
                chroma_metadata[key] = value
        
        return chroma_metadata
    
    def _restore_metadata_from_chroma(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Restore metadata from ChromaDB storage by converting JSON strings back to lists.
        
        Args:
            metadata: ChromaDB metadata dictionary
            
        Returns:
            Restored metadata dictionary
        """
        restored_metadata = {}
        
        for key, value in metadata.items():
            if isinstance(value, str) and value.startswith('[') and value.endswith(']'):
                try:
                    # Try to parse as JSON list
                    restored_metadata[key] = json.loads(value)
                except json.JSONDecodeError:
                    # Keep as string if parsing fails
                    restored_metadata[key] = value
            elif isinstance(value, str) and value.startswith('{') and value.endswith('}'):
                try:
                    # Try to parse as JSON dict
                    restored_metadata[key] = json.loads(value)
                except json.JSONDecodeError:
                    # Keep as string if parsing fails
                    restored_metadata[key] = value
            else:
                # Keep other types as is
                restored_metadata[key] = value
        
        return restored_metadata
    
    def similarity_search(
        self, 
        query_embedding: List[float], 
        k: int = 10, 
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Perform similarity search in the vector store.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            filter_dict: Optional metadata filter
            
        Returns:
            List of search results with metadata
            
        Raises:
            RuntimeError: If vector store is not initialized
        """
        if not self.collection:
            raise RuntimeError("Vector store not initialized")
        
        try:
            # Prepare where clause for filtering
            where_clause = None
            if filter_dict:
                where_clause = self._build_where_clause(filter_dict)
            
            # Perform similarity search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                where=where_clause,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            formatted_results = []
            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    # Restore metadata from ChromaDB format
                    metadata = self._restore_metadata_from_chroma(results['metadatas'][0][i])
                    
                    result = {
                        'id': results['ids'][0][i],
                        'content': results['documents'][0][i],
                        'metadata': metadata,
                        'distance': results['distances'][0][i] if results['distances'] else None
                    }
                    formatted_results.append(result)
            
            logger.debug(f"Retrieved {len(formatted_results)} results from similarity search")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to perform similarity search: {e}")
            raise
    
    def _build_where_clause(self, filter_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Build ChromaDB where clause from filter dictionary.
        
        Args:
            filter_dict: Filter criteria
            
        Returns:
            ChromaDB where clause
        """
        where_clause = {}
        
        for key, value in filter_dict.items():
            if isinstance(value, list):
                # Handle list values (e.g., crop categories)
                if value:
                    # Convert list to JSON string for filtering
                    where_clause[key] = json.dumps(value)
            else:
                # Handle single values
                where_clause[key] = value
        
        return where_clause
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the current collection.
        
        Returns:
            Dictionary with collection information
        """
        if not self.collection:
            return {"error": "Collection not initialized"}
        
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection.name,
                "total_chunks": count,
                "embedding_dimensions": self.config.embedding_dimensions
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {"error": str(e)}
    
    def delete_collection(self) -> None:
        """Delete the current collection.
        
        Warning: This will remove all stored chunks!
        """
        if not self.collection:
            logger.warning("No collection to delete")
            return
        
        try:
            self.client.delete_collection(self.collection.name)
            self.collection = None
            logger.info("Collection deleted successfully")
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            raise
    
    def reset_collection(self) -> None:
        """Reset the collection (delete and recreate).
        
        Warning: This will remove all stored chunks!
        """
        try:
            self.delete_collection()
            self._initialize_store()
            logger.info("Collection reset successfully")
        except Exception as e:
            logger.error(f"Failed to reset collection: {e}")
            raise
