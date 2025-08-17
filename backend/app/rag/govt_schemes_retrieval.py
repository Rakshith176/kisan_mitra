"""Specialized retrieval strategy for government schemes."""

import logging
from typing import List, Dict, Any, Optional
from .models import AgriculturalChunk, QueryContext, RetrievalResult
from .govt_schemes_vector_store import GovernmentSchemesVectorStore
from .embedding_service import EmbeddingService
from .config import RAGConfig

logger = logging.getLogger(__name__)


class GovernmentSchemesRetrievalStrategy:
    """Specialized retrieval strategy for government schemes."""
    
    def __init__(self, vector_store: GovernmentSchemesVectorStore, embedding_service: EmbeddingService, config: RAGConfig = None):
        """Initialize the government schemes retrieval strategy.
        
        Args:
            vector_store: Government schemes vector store instance
            embedding_service: Embedding service instance
            config: RAG configuration, uses default if None
        """
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.config = config or RAGConfig()
        
        logger.info("Government schemes retrieval strategy initialized")
    
    async def retrieve(self, query: str, context: QueryContext) -> List[AgriculturalChunk]:
        """Retrieve relevant government scheme chunks for a query.
        
        Args:
            query: User query string
            context: Query context with user preferences
            
        Returns:
            List of relevant government scheme chunks
        """
        try:
            logger.info(f"Retrieving government scheme chunks for query: {query[:100]}...")
            
            # Stage 1: Semantic search with scheme-specific filtering
            results = await self._semantic_search_with_scheme_filtering(query, context)
            
            # Stage 2: Relevance ranking for government schemes
            final_results = self._rank_by_scheme_relevance(results, query)
            
            logger.info(f"Retrieved {len(final_results)} government scheme chunks for query")
            return final_results
            
        except Exception as e:
            logger.error(f"Failed to retrieve government scheme chunks: {e}")
            raise
    
    async def _semantic_search_with_scheme_filtering(self, query: str, context: QueryContext) -> List[Dict[str, Any]]:
        """Perform semantic search with government scheme context filtering.
        
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
            
            # Apply government scheme context filtering
            filtered_results = self._filter_by_scheme_context(initial_results, context)
            
            # Return top filtered results
            return filtered_results[:self.config.max_retrieval_results]
            
        except Exception as e:
            logger.error(f"Failed to perform government scheme semantic search: {e}")
            raise
    
    def _filter_by_scheme_context(self, results: List[Dict[str, Any]], context: QueryContext) -> List[Dict[str, Any]]:
        """Filter results based on government scheme context.
        
        Args:
            results: Search results to filter
            context: Query context with user preferences
            
        Returns:
            Filtered results
        """
        filtered_results = []
        
        for result in results:
            metadata = result.get('metadata', {})
            
            # Filter by beneficiary category if specified
            if context.beneficiary_category and metadata.get('beneficiary_type'):
                if context.beneficiary_category.lower() not in [bt.lower() for bt in metadata['beneficiary_type']]:
                    continue
            
            # Filter by scheme interest if specified
            if context.scheme_interest and metadata.get('scheme_name'):
                if not any(scheme.lower() in [sn.lower() for sn in metadata['scheme_name']] for scheme in context.scheme_interest):
                    continue
            
            # Filter by region if specified
            if context.region and metadata.get('region'):
                if context.region.lower() not in [r.lower() for r in metadata['region']]:
                    continue
            
            # Filter by budget range if specified
            if context.budget_range and metadata.get('budget_amount'):
                # Simple budget range filtering (can be enhanced)
                budget_amount = metadata['budget_amount']
                if context.budget_range == "low" and budget_amount > 100:
                    continue
                elif context.budget_range == "high" and budget_amount < 1000:
                    continue
            
            filtered_results.append(result)
        
        return filtered_results
    
    def _rank_by_scheme_relevance(self, results: List[Dict[str, Any]], query: str) -> List[AgriculturalChunk]:
        """Rank results by relevance to government schemes.
        
        Args:
            results: Search results to rank
            query: Original query
            
        Returns:
            Ranked list of AgriculturalChunk objects
        """
        # Convert results to AgriculturalChunk objects
        chunks = []
        
        for result in results:
            try:
                # Create AgriculturalChunk from result
                chunk = AgriculturalChunk(
                    content=result['content'],
                    metadata=result['metadata'],
                    chunk_index=0,  # Will be set from ID
                    source_document=result['id'].split('_')[0],  # Extract from ID
                    embedding=None  # Not needed for retrieval
                )
                
                # Set chunk_index from ID if possible
                if '_' in result['id']:
                    try:
                        chunk.chunk_index = int(result['id'].split('_')[-1])
                    except ValueError:
                        pass
                
                chunks.append(chunk)
                
            except Exception as e:
                logger.warning(f"Failed to create chunk from result: {e}")
                continue
        
        # Sort by relevance (lower distance = higher relevance)
        chunks.sort(key=lambda x: getattr(x, 'distance', float('inf')))
        
        return chunks
    
    def get_retrieval_info(self) -> Dict[str, Any]:
        """Get information about the retrieval strategy and vector store."""
        try:
            collection_info = self.vector_store.get_collection_info()
            return {
                "retrieval_strategy": "government_schemes",
                "vector_store_info": collection_info,
                "embedding_model": self.config.embedding_model,
                "max_retrieval_results": self.config.max_retrieval_results
            }
        except Exception as e:
            logger.error(f"Failed to get retrieval info: {e}")
            return {"error": str(e)}
