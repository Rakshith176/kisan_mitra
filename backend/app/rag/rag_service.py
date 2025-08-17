"""Main RAG service combining retrieval and generation."""

import logging
from typing import List, Dict, Any, Optional
import json

from .models import AgriculturalChunk, QueryContext
from .retrieval_strategy import RetrievalStrategy
from .vector_store import VectorStore
from .embedding_service import EmbeddingService
from .config import RAGConfig

logger = logging.getLogger(__name__)


class RAGService:
    """Main RAG service that combines retrieval and generation capabilities."""
    
    def __init__(self, config: RAGConfig = None):
        """Initialize the RAG service.
        
        Args:
            config: RAG configuration, uses default if None
        """
        self.config = config or RAGConfig()
        self.vector_store = VectorStore(config)
        self.embedding_service = EmbeddingService(config)
        self.retrieval_strategy = RetrievalStrategy(
            vector_store=self.vector_store,
            embedding_service=self.embedding_service,
            config=config
        )
        
        logger.info("RAG service initialized")
    
    async def query(self, query: str, context: QueryContext = None) -> Dict[str, Any]:
        """Query the RAG system with a user question.
        
        Args:
            query: User's question
            context: Query context with user preferences
            
        Returns:
            Dictionary with query results and retrieved chunks
        """
        try:
            logger.info(f"Processing query: {query[:100]}...")
            
            # Use default context if none provided
            if context is None:
                context = QueryContext()
            
            # Retrieve relevant chunks
            chunks = await self.retrieval_strategy.retrieve(query, context)
            
            # Prepare response
            response = {
                "query": query,
                "context": context.dict(),
                "retrieved_chunks": len(chunks),
                "chunks": [self._chunk_to_dict(chunk) for chunk in chunks],
                "summary": self._generate_summary(chunks),
                "suggested_actions": self._suggest_actions(chunks, query)
            }
            
            logger.info(f"Query processed successfully. Retrieved {len(chunks)} chunks")
            return response
            
        except Exception as e:
            logger.error(f"Failed to process query: {e}")
            raise
    
    async def query_with_filter(
        self, 
        query: str, 
        filter_criteria: Dict[str, Any],
        context: QueryContext = None
    ) -> Dict[str, Any]:
        """Query the RAG system with specific filter criteria.
        
        Args:
            query: User's question
            filter_criteria: Specific filter criteria for retrieval
            context: Query context with user preferences
            
        Returns:
            Dictionary with filtered query results
        """
        try:
            logger.info(f"Processing filtered query: {query[:100]}...")
            
            # Use default context if none provided
            if context is None:
                context = QueryContext()
            
            # Retrieve chunks with filtering
            chunks = await self.retrieval_strategy.retrieve(query, context)
            
            # Apply additional filtering based on criteria
            filtered_chunks = self._apply_additional_filters(chunks, filter_criteria)
            
            # Prepare response
            response = {
                "query": query,
                "filter_criteria": filter_criteria,
                "context": context.dict(),
                "total_retrieved": len(chunks),
                "filtered_chunks": len(filtered_chunks),
                "chunks": [self._chunk_to_dict(chunk) for chunk in filtered_chunks],
                "summary": self._generate_summary(filtered_chunks),
                "filter_stats": self._get_filter_stats(chunks, filtered_chunks)
            }
            
            logger.info(f"Filtered query processed. {len(filtered_chunks)}/{len(chunks)} chunks match criteria")
            return response
            
        except Exception as e:
            logger.error(f"Failed to process filtered query: {e}")
            raise
    
    def _chunk_to_dict(self, chunk: AgriculturalChunk) -> Dict[str, Any]:
        """Convert chunk to dictionary for JSON serialization.
        
        Args:
            chunk: Agricultural chunk
            
        Returns:
            Dictionary representation of chunk
        """
        return {
            "chunk_id": chunk.chunk_id,
            "content": chunk.content,
            "metadata": {
                "document_type": chunk.metadata.document_type,
                "document_section": chunk.metadata.document_section,
                "crop_category": chunk.metadata.crop_category,
                "crop_specific": chunk.metadata.crop_specific,
                "season": chunk.metadata.season,
                "practice_type": chunk.metadata.practice_type,
                "compliance_level": chunk.metadata.compliance_level,
                "chunk_size_tokens": chunk.metadata.chunk_size_tokens,
                "parent_section": chunk.metadata.parent_section
            }
        }
    
    def _generate_summary(self, chunks: List[AgriculturalChunk]) -> Dict[str, Any]:
        """Generate a summary of retrieved chunks.
        
        Args:
            chunks: List of retrieved chunks
            
        Returns:
            Summary information
        """
        if not chunks:
            return {"message": "No chunks retrieved"}
        
        # Count document types
        doc_types = {}
        practice_types = {}
        crop_categories = set()
        seasons = set()
        
        for chunk in chunks:
            # Document types
            doc_type = chunk.metadata.document_type
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            
            # Practice types
            practice_type = chunk.metadata.practice_type
            practice_types[practice_type] = practice_types.get(practice_type, 0) + 1
            
            # Crop categories
            crop_categories.update(chunk.metadata.crop_category)
            
            # Seasons
            seasons.update(chunk.metadata.season)
        
        return {
            "total_chunks": len(chunks),
            "document_types": doc_types,
            "practice_types": practice_types,
            "crop_categories": list(crop_categories),
            "seasons": list(seasons),
            "avg_chunk_size": sum(c.metadata.chunk_size_tokens for c in chunks) / len(chunks)
        }
    
    def _suggest_actions(self, chunks: List[AgriculturalChunk], query: str) -> List[str]:
        """Suggest actions based on retrieved chunks and query.
        
        Args:
            chunks: List of retrieved chunks
            query: User's query
            
        Returns:
            List of suggested actions
        """
        suggestions = []
        
        if not chunks:
            return ["No suggestions available - no relevant information found"]
        
        # Analyze practice types
        practice_counts = {}
        for chunk in chunks:
            practice = chunk.metadata.practice_type
            practice_counts[practice] = practice_counts.get(practice, 0) + 1
        
        # Suggest actions based on dominant practice types
        for practice, count in sorted(practice_counts.items(), key=lambda x: x[1], reverse=True):
            if practice == "pest_management":
                suggestions.append("Review pest control measures and monitoring schedules")
            elif practice == "soil_health":
                suggestions.append("Check soil testing and fertilization recommendations")
            elif practice == "irrigation":
                suggestions.append("Review irrigation schedules and water management")
            elif practice == "harvest":
                suggestions.append("Plan harvest timing and post-harvest handling")
            elif practice == "cultivation":
                suggestions.append("Review planting schedules and crop management practices")
        
        # Add general suggestions
        if len(chunks) > 5:
            suggestions.append("Multiple sources found - consider cross-referencing information")
        
        if any("gap" in c.metadata.document_type.lower() for c in chunks):
            suggestions.append("GAP certification information available - review compliance requirements")
        
        return suggestions[:5]  # Limit to top 5 suggestions
    
    def _apply_additional_filters(self, chunks: List[AgriculturalChunk], filter_criteria: Dict[str, Any]) -> List[AgriculturalChunk]:
        """Apply additional filters to retrieved chunks.
        
        Args:
            chunks: List of chunks to filter
            filter_criteria: Filter criteria
            
        Returns:
            Filtered list of chunks
        """
        filtered_chunks = chunks
        
        # Filter by document type
        if "document_type" in filter_criteria:
            doc_type = filter_criteria["document_type"]
            filtered_chunks = [c for c in filtered_chunks if c.metadata.document_type == doc_type]
        
        # Filter by practice type
        if "practice_type" in filter_criteria:
            practice_type = filter_criteria["practice_type"]
            filtered_chunks = [c for c in filtered_chunks if c.metadata.practice_type == practice_type]
        
        # Filter by compliance level
        if "compliance_level" in filter_criteria:
            compliance_level = filter_criteria["compliance_level"]
            filtered_chunks = [c for c in filtered_chunks if c.metadata.compliance_level == compliance_level]
        
        # Filter by crop category
        if "crop_category" in filter_criteria:
            crop_category = filter_criteria["crop_category"]
            filtered_chunks = [c for c in filtered_chunks if crop_category in c.metadata.crop_category]
        
        return filtered_chunks
    
    def _get_filter_stats(self, original_chunks: List[AgriculturalChunk], filtered_chunks: List[AgriculturalChunk]) -> Dict[str, Any]:
        """Get statistics about filtering results.
        
        Args:
            original_chunks: Original list of chunks
            filtered_chunks: Filtered list of chunks
            
        Returns:
            Filter statistics
        """
        return {
            "original_count": len(original_chunks),
            "filtered_count": len(filtered_chunks),
            "filtered_percentage": round((len(filtered_chunks) / len(original_chunks)) * 100, 2) if original_chunks else 0,
            "chunks_removed": len(original_chunks) - len(filtered_chunks)
        }
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get RAG service statistics.
        
        Returns:
            Dictionary with service statistics
        """
        try:
            retrieval_stats = self.retrieval_strategy.get_retrieval_stats()
            vector_store_info = self.vector_store.get_collection_info()
            
            return {
                "service": "RAGService",
                "retrieval_strategy": retrieval_stats,
                "vector_store": vector_store_info,
                "embedding_model": self.embedding_service.config.embedding_model,
                "config": {
                    "max_retrieval_results": self.config.max_retrieval_results,
                    "final_result_limit": self.config.final_result_limit,
                    "embedding_dimensions": self.config.embedding_dimensions
                }
            }
        except Exception as e:
            logger.error(f"Failed to get service stats: {e}")
            return {"error": str(e)}
    
    def reset_service(self) -> None:
        """Reset the RAG service (clear vector store).
        
        Warning: This will remove all stored chunks!
        """
        try:
            self.vector_store.reset_collection()
            logger.info("RAG service reset successfully")
        except Exception as e:
            logger.error(f"Failed to reset RAG service: {e}")
            raise
