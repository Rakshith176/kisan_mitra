"""Configuration for RAG system."""

from pydantic import BaseModel, Field


class RAGConfig(BaseModel):
    """Configuration for RAG system."""
    
    # Chunking Configuration
    max_tokens: int = Field(default=512, description="Maximum tokens per chunk")
    overlap_tokens: int = Field(default=50, description="Token overlap between chunks")
    min_chunk_tokens: int = Field(default=100, description="Minimum tokens per chunk")
    
    # Embedding Configuration
    embedding_model: str = Field(default="all-MiniLM-L6-v2", description="Sentence transformer model")
    embedding_dimensions: int = Field(default=384, description="Embedding dimensions")
    
    # Retrieval Configuration
    max_retrieval_results: int = Field(default=10, description="Maximum results to retrieve")
    final_result_limit: int = Field(default=5, description="Final number of results to return")
    
    # Vector Store Configuration
    vector_store_path: str = Field(default="./chroma_db", description="Path for vector store")
    
    # Processing Configuration
    batch_size: int = Field(default=32, description="Batch size for processing")
    max_chunks_in_memory: int = Field(default=1000, description="Maximum chunks to keep in memory")


# Default configuration
default_config = RAGConfig()
