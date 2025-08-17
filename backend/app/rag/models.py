"""Data models for RAG system."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ChunkMetadata(BaseModel):
    """Metadata for agricultural document chunks."""
    
    # Document Information
    document_type: str = Field(..., description="Type of document (e.g., 'bharat_gap', 'farmer_handbook', 'government_scheme')")
    document_section: str = Field(..., description="Section within document (e.g., 'pest_management', 'soil_health', 'budget_allocation')")
    
    # Agricultural Context
    crop_category: List[str] = Field(default_factory=list, description="General crop categories")
    crop_specific: List[str] = Field(default_factory=list, description="Specific crop names")
    season: List[str] = Field(default_factory=list, description="Applicable seasons")
    
    # Practice Information
    practice_type: str = Field(..., description="Types of agricultural practices")
    region: List[str] = Field(default_factory=list, description="Geographic regions")
    
    # Government Scheme Specific Fields
    beneficiary_type: List[str] = Field(default_factory=list, description="Types of beneficiaries (e.g., 'small_farmers', 'women', 'SC/ST')")
    scheme_name: List[str] = Field(default_factory=list, description="Names of government schemes (e.g., 'pm_kisan', 'pmksy')")
    budget_amount: Optional[float] = Field(default=None, description="Budget allocation amount")
    budget_unit: Optional[str] = Field(default=None, description="Budget unit (e.g., 'crore', 'lakh')")
    implementation_phase: Optional[str] = Field(default=None, description="Implementation phase or timeline")
    eligibility_criteria: List[str] = Field(default_factory=list, description="Eligibility criteria for schemes")
    benefits: List[str] = Field(default_factory=list, description="Benefits and features of schemes")
    application_process: List[str] = Field(default_factory=list, description="Application and enrollment process")
    contact_info: List[str] = Field(default_factory=list, description="Contact information and helpline details")
    validity_period: Optional[str] = Field(default=None, description="Validity period of schemes")
    
    # Language
    language: str = Field(default="en", description="Language of the content")


class AgriculturalChunk(BaseModel):
    """A chunk of agricultural document content."""
    
    content: str = Field(..., description="The actual text content of the chunk")
    metadata: ChunkMetadata = Field(..., description="Metadata for the chunk")
    chunk_index: int = Field(..., description="Index of the chunk in the document")
    source_document: str = Field(..., description="Source document name")
    embedding: Optional[List[float]] = Field(default=None, description="Vector embedding of the chunk")


class QueryContext(BaseModel):
    """Context for agricultural queries."""
    
    query: str = Field(..., description="The user's query")
    user_crops: List[str] = Field(default_factory=list, description="Crops the user is interested in")
    current_season: Optional[str] = Field(default=None, description="Current agricultural season")
    language: str = Field(default="en", description="Preferred language for response")
    location: Optional[str] = Field(default=None, description="User's location")
    farm_size: Optional[float] = Field(default=None, description="User's farm size in acres")
    experience_years: Optional[int] = Field(default=None, description="Years of farming experience")
    
    # Government Scheme Specific Context
    beneficiary_category: Optional[str] = Field(default=None, description="User's beneficiary category")
    scheme_interest: List[str] = Field(default_factory=list, description="Schemes user is interested in")
    budget_range: Optional[str] = Field(default=None, description="Budget range user is looking for")
    region: Optional[str] = Field(default=None, description="User's region")


class RetrievalResult(BaseModel):
    """Result of a retrieval operation."""
    
    chunks: List[AgriculturalChunk] = Field(..., description="Retrieved chunks")
    total_chunks: int = Field(..., description="Total number of chunks retrieved")
    query_similarity_scores: List[float] = Field(default_factory=list, description="Similarity scores for retrieved chunks")
    metadata_filters: Dict[str, Any] = Field(default_factory=dict, description="Metadata filters applied")
    retrieval_strategy: str = Field(..., description="Strategy used for retrieval")
    processing_time: float = Field(..., description="Time taken for retrieval in seconds")


class RAGResponse(BaseModel):
    """Complete RAG system response."""
    
    query: str = Field(..., description="Original user query")
    chunks: List[AgriculturalChunk] = Field(..., description="Retrieved relevant chunks")
    summary: Optional[str] = Field(default=None, description="Generated summary of retrieved information")
    suggested_actions: List[str] = Field(default_factory=list, description="Suggested actions based on retrieved information")
    confidence_score: float = Field(..., description="Confidence score for the response")
    source_documents: List[str] = Field(default_factory=list, description="Source documents used")
    metadata_summary: Dict[str, Any] = Field(default_factory=dict, description="Summary of metadata from retrieved chunks")
    processing_time: float = Field(..., description="Total processing time in seconds")
