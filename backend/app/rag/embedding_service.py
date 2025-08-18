"""Embedding service using sentence transformers."""

import logging
from typing import List, Union
from sentence_transformers import SentenceTransformer
import numpy as np

from .config import RAGConfig

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using sentence transformers."""
    
    def __init__(self, config: RAGConfig = None):
        """Initialize the embedding service.
        
        Args:
            config: RAG configuration, uses default if None
        """
        self.config = config or RAGConfig()
        self.model = None
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the sentence transformer model."""
        try:
            logger.info(f"Loading embedding model: {self.config.embedding_model}")
            self.model = SentenceTransformer(self.config.embedding_model)
            logger.info(f"Model loaded successfully. Dimensions: {self.model.get_sentence_embedding_dimension()}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def embed(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """Generate embeddings for text.
        
        Args:
            text: Single text string or list of text strings
            
        Returns:
            Single embedding vector or list of embedding vectors
        """
        if not self.model:
            raise RuntimeError("Embedding model not loaded")
        
        try:
            # Convert single string to list for batch processing
            if isinstance(text, str):
                text = [text]
                single_input = True
            else:
                single_input = False
            
            # Generate embeddings
            embeddings = self.model.encode(text, convert_to_tensor=False)
            
            # Convert to list format
            if hasattr(embeddings, 'tolist'):
                embeddings = embeddings.tolist()
            
            # Return single embedding if single input
            if single_input:
                return embeddings[0]
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    def embed_batch(self, texts: List[str], batch_size: int = None) -> List[List[float]]:
        """Generate embeddings for a batch of texts.
        
        Args:
            texts: List of text strings
            batch_size: Batch size for processing, uses config default if None
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        batch_size = batch_size or self.config.batch_size
        all_embeddings = []
        
        try:
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                logger.debug(f"Processing batch {i//batch_size + 1}, size: {len(batch)}")
                
                batch_embeddings = self.embed(batch)
                all_embeddings.extend(batch_embeddings)
                
        except Exception as e:
            logger.error(f"Failed to process batch embeddings: {e}")
            raise
        
        return all_embeddings
    
    def get_dimensions(self) -> int:
        """Get the embedding dimensions.
        
        Returns:
            Number of dimensions in the embedding vectors
        """
        if not self.model:
            raise RuntimeError("Embedding model not loaded")
        return self.model.get_sentence_embedding_dimension()
    
    def is_loaded(self) -> bool:
        """Check if the model is loaded.
        
        Returns:
            True if model is loaded, False otherwise
        """
        return self.model is not None
