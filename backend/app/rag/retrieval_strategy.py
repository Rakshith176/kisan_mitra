"""Retrieval strategy for RAG system."""

import logging
from typing import List, Dict, Any, Optional
from .models import AgriculturalChunk, QueryContext, RetrievalResult
from .vector_store import VectorStore
from .embedding_service import EmbeddingService
from .config import RAGConfig

logger = logging.getLogger(__name__)


class RetrievalStrategy:
    """Strategy for retrieving relevant chunks from the vector store."""
    
    def __init__(self, vector_store: VectorStore, embedding_service: EmbeddingService, config: RAGConfig = None):
        """Initialize the retrieval strategy.
        
        Args:
            vector_store: Vector store instance
            embedding_service: Embedding service instance
            config: RAG configuration, uses default if None
        """
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.config = config or RAGConfig()
        
        logger.info("Retrieval strategy initialized")
    
    async def retrieve(self, query: str, context: QueryContext) -> List[AgriculturalChunk]:
        """Retrieve relevant chunks for a query.
        
        Args:
            query: User query string
            context: Query context with user preferences
            
        Returns:
            List of relevant agricultural chunks
        """
        try:
            logger.info(f"Retrieving chunks for query: {query[:100]}...")
            
            # Stage 1: Semantic search with filtering
            results = await self._semantic_search_with_filtering(query, context)
            
            # Stage 2: Diversity selection
            final_results = self._select_diverse_chunks(results)
            
            logger.info(f"Retrieved {len(final_results)} chunks for query")
            return final_results
            
        except Exception as e:
            logger.error(f"Failed to retrieve chunks: {e}")
            raise
    
    async def _semantic_search_with_filtering(self, query: str, context: QueryContext) -> List[Dict[str, Any]]:
        """Perform semantic search with agricultural context filtering.
        
        Args:
            query: User query
            context: Query context
            
        Returns:
            List of search results
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_service.embed(query)
            
            # Get more results initially to allow for filtering
            initial_results = self.vector_store.similarity_search(
                query_embedding=query_embedding,
                k=self.config.max_retrieval_results * 3,  # Get more to filter from
                filter_dict=None
            )
            
            # Apply agricultural context filtering
            filtered_results = self._filter_by_agricultural_context(initial_results, context)
            
            # Return top filtered results
            return filtered_results[:self.config.max_retrieval_results]
            
        except Exception as e:
            logger.error(f"Failed to perform semantic search: {e}")
            raise
    
    def _filter_by_agricultural_context(self, results: List[Dict[str, Any]], context: QueryContext) -> List[Dict[str, Any]]:
        """Filter results based on agricultural context.
        
        Args:
            results: Search results to filter
            context: Query context with user preferences
            
        Returns:
            Filtered results
        """
        filtered_results = []
        
        for result in results:
            # Filter by user's crops (if specified)
            if context.user_crops and not self._crop_matches(result, context.user_crops):
                continue
                
            # Filter by season (if specified)
            if context.current_season and not self._season_matches(result, context.current_season):
                continue
                
            # Filter by region (if specified)
            if context.region and not self._region_matches(result, context.region):
                continue
                
            filtered_results.append(result)
        
        logger.debug(f"Filtered {len(results)} results to {len(filtered_results)} based on context")
        return filtered_results
    
    def _crop_matches(self, result: Dict[str, Any], user_crops: List[str]) -> bool:
        """Check if result matches user's crop preferences.
        
        Args:
            result: Search result
            user_crops: User's crop preferences
            
        Returns:
            True if there's a match, False otherwise
        """
        if not user_crops:
            return True
        
        metadata = result.get('metadata', {})
        result_crops = metadata.get('crop_specific', [])
        result_categories = metadata.get('crop_category', [])
        
        # Check specific crops
        for user_crop in user_crops:
            if user_crop.lower() in [c.lower() for c in result_crops]:
                return True
            
            # Check crop categories
            if user_crop.lower() in [c.lower() for c in result_categories]:
                return True
        
        return False
    
    def _season_matches(self, result: Dict[str, Any], current_season: str) -> bool:
        """Check if result matches current season.
        
        Args:
            result: Search result
            current_season: Current agricultural season
            
        Returns:
            True if there's a match, False otherwise
        """
        if not current_season:
            return True
        
        metadata = result.get('metadata', {})
        result_seasons = metadata.get('season', [])
        
        # Check if current season is in result seasons or if result is all-season
        return (current_season.lower() in [s.lower() for s in result_seasons] or 
                'all_season' in [s.lower() for s in result_seasons])
    
    def _region_matches(self, result: Dict[str, Any], user_region: str) -> bool:
        """Check if result matches user's region.
        
        Args:
            result: Search result
            user_region: User's geographical region
            
        Returns:
            True if there's a match, False otherwise
        """
        if not user_region:
            return True
        
        # For now, assume all results are applicable to all regions
        # This can be enhanced with more sophisticated region matching
        return True
    
    def _select_diverse_chunks(self, results: List[Dict[str, Any]]) -> List[AgriculturalChunk]:
        """Select diverse chunks from search results.
        
        Args:
            results: Search results
            
        Returns:
            List of diverse agricultural chunks
        """
        selected_chunks = []
        used_sections = set()
        used_practice_types = set()
        
        for result in results:
            if len(selected_chunks) >= self.config.final_result_limit:
                break
            
            metadata = result.get('metadata', {})
            section = metadata.get('document_section', 'unknown')
            practice_types = metadata.get('practice_type', ['unknown'])
            
            # Prefer chunks from different sections and practice types
            if (section not in used_sections and 
                not any(pt in used_practice_types for pt in practice_types)):
                chunk = self._result_to_chunk(result)
                selected_chunks.append(chunk)
                used_sections.add(section)
                used_practice_types.update(practice_types)
            elif len(selected_chunks) < self.config.final_result_limit // 2:
                # Allow some from same section/practice type
                chunk = self._result_to_chunk(result)
                selected_chunks.append(chunk)
        
        return selected_chunks
    
    def _result_to_chunk(self, result: Dict[str, Any]) -> AgriculturalChunk:
        """Convert search result to AgriculturalChunk.
        
        Args:
            result: Search result from vector store
            
        Returns:
            AgriculturalChunk object
        """
        # This is a simplified conversion - in a real implementation,
        # you might want to reconstruct the full chunk with all metadata
        from .models import ChunkMetadata
        
        metadata = result.get('metadata', {})
        
        # Reconstruct metadata
        chunk_metadata = ChunkMetadata(
            document_type=metadata.get('document_type', 'unknown'),
            document_section=metadata.get('document_section', 'unknown'),
            crop_category=metadata.get('crop_category', []),
            crop_specific=metadata.get('crop_specific', []),
            season=metadata.get('season', []),
            practice_type=metadata.get('practice_type', ['unknown']),
            compliance_level=metadata.get('compliance_level', 'basic'),
            chunk_size_tokens=metadata.get('chunk_size_tokens', 0),
            chunk_position=metadata.get('chunk_position', 0),
            parent_section=metadata.get('parent_section', 'unknown')
        )
        
        return AgriculturalChunk(
            chunk_id=result.get('id', 'unknown'),
            content=result.get('content', ''),
            metadata=chunk_metadata,
            embeddings=None  # Not needed for retrieval results
        )
    
    def get_retrieval_stats(self) -> Dict[str, Any]:
        """Get retrieval strategy statistics.
        
        Returns:
            Dictionary with retrieval statistics
        """
        try:
            collection_info = self.vector_store.get_collection_info()
            
            return {
                "retrieval_strategy": "semantic_search_with_filtering",
                "max_retrieval_results": self.config.max_retrieval_results,
                "final_result_limit": self.config.final_result_limit,
                "vector_store_info": collection_info
            }
        except Exception as e:
            logger.error(f"Failed to get retrieval stats: {e}")
            return {"error": str(e)}
