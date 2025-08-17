"""
Specialized document processor for government scheme documents.
Integrates with the existing RAG system while using specialized chunking.
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from .pdf_extractor import PDFExtractor
from .govt_schemes_chunker import GovernmentSchemesChunker
from .embedding_service import EmbeddingService
from .govt_schemes_vector_store import GovernmentSchemesVectorStore
from .models import AgriculturalChunk, RAGResponse
from .config import RAGConfig

logger = logging.getLogger(__name__)


class GovernmentSchemesProcessor:
    """
    Specialized processor for government scheme documents.
    Uses the same retrieval method but with optimized chunking for policy documents.
    """
    
    def __init__(self, config: RAGConfig = None):
        """Initialize the government schemes processor.
        
        Args:
            config: RAG configuration, uses default if None
        """
        self.config = config or RAGConfig()
        self.pdf_extractor = PDFExtractor()
        self.chunker = GovernmentSchemesChunker(config)
        self.embedding_service = EmbeddingService(config)
        self.vector_store = GovernmentSchemesVectorStore(config)
        
        logger.info("Government schemes processor initialized successfully")
    
    async def process_document(self, pdf_path: Path, document_type: str = None) -> List[AgriculturalChunk]:
        """
        Process a government scheme PDF document.
        
        Args:
            pdf_path: Path to the PDF file
            document_type: Type of document (auto-detected if None)
            
        Returns:
            List of processed chunks
        """
        try:
            logger.info(f"Processing government scheme document: {pdf_path}")
            
            # Extract text from PDF
            text_content = self.pdf_extractor.extract(str(pdf_path))
            if not text_content:
                logger.warning(f"No text content extracted from {pdf_path}")
                return []
            
            # Auto-detect document type if not provided
            if not document_type:
                document_type = self._detect_document_type(pdf_path.name, text_content)
            
            # Chunk the document using specialized chunker
            chunks = self.chunker.chunk_document(text_content, document_type)
            
            if not chunks:
                logger.warning(f"No chunks created from {pdf_path}")
                return []
            
            # Generate embeddings for chunks
            logger.info("Generating embeddings for government scheme chunks...")
            for chunk in chunks:
                logger.info(f"Generating embedding for chunk {chunk.source_document}_{chunk.chunk_index}")
                embedding_vector = self.embedding_service.embed(chunk.content)
                logger.info(f"Embedding generated: type={type(embedding_vector)}, length={len(embedding_vector) if embedding_vector else 'None'}")
                chunk.embedding = embedding_vector
                logger.info(f"Chunk embedding set: {chunk.embedding is not None}")
            
            # Store chunks in vector store
            await self._store_chunks(chunks)
            
            # Get chunking summary
            summary = self.chunker.get_chunking_summary(chunks)
            logger.info(f"Document processing summary: {summary}")
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing government scheme document {pdf_path}: {e}")
            return []
    
    async def process_directory(self, directory_path: Path) -> Dict[str, List[AgriculturalChunk]]:
        """
        Process all government scheme documents in a directory.
        
        Args:
            directory_path: Path to directory containing PDF files
            
        Returns:
            Dictionary mapping document names to chunks
        """
        try:
            logger.info(f"Processing government scheme documents in: {directory_path}")
            
            pdf_files = list(directory_path.glob("*.pdf"))
            if not pdf_files:
                logger.warning(f"No PDF files found in {directory_path}")
                return {}
            
            results = {}
            total_chunks = 0
            
            for pdf_file in pdf_files:
                logger.info(f"Processing {pdf_file.name}")
                chunks = await self.process_document(pdf_file)
                if chunks:
                    results[pdf_file.name] = chunks
                    total_chunks += len(chunks)
            
            logger.info(f"Processed {len(results)} documents with {total_chunks} total chunks")
            return results
            
        except Exception as e:
            logger.error(f"Error processing government scheme directory {directory_path}: {e}")
            return {}
    
    async def query_schemes(
        self, 
        query: str, 
        context: Dict[str, Any] = None
    ) -> RAGResponse:
        """
        Query government schemes using the existing retrieval method.
        
        Args:
            query: User query about government schemes
            context: Additional context (user profile, location, etc.)
            
        Returns:
            RAG response with relevant scheme information
        """
        try:
            logger.info(f"Querying government schemes: {query}")
            
            # Use specialized government schemes retrieval strategy
            from .govt_schemes_retrieval import GovernmentSchemesRetrievalStrategy
            retrieval_strategy = GovernmentSchemesRetrievalStrategy(self.vector_store, self.embedding_service, self.config)
            
            # Create query context
            from .models import QueryContext
            query_context = QueryContext(
                query=query,
                user_crops=context.get("crops", []) if context else [],
                current_season=context.get("season") if context else None,
                language=context.get("language", "en") if context else "en",
                location=context.get("location") if context else None,
                farm_size=context.get("farm_size") if context else None,
                experience_years=context.get("experience_years") if context else None,
                beneficiary_category=context.get("beneficiary_category") if context else None,
                scheme_interest=context.get("scheme_interest", []) if context else [],
                budget_range=context.get("budget_range") if context else None,
                region=context.get("region") if context else None
            )
            
            # Retrieve relevant chunks using the correct method name
            chunks = await retrieval_strategy.retrieve(query, query_context)
            
            if not chunks:
                logger.warning("No relevant chunks found for government scheme query")
                return RAGResponse(
                    query=query,
                    chunks=[],
                    confidence_score=0.0,
                    source_documents=[],
                    processing_time=0.0
                )
            
            # Generate summary and suggested actions
            summary = self._generate_scheme_summary(chunks, query)
            suggested_actions = self._generate_suggested_actions(chunks, query_context)
            
            # Create metadata summary
            metadata_summary = self._create_metadata_summary(chunks)
            
            return RAGResponse(
                query=query,
                chunks=chunks,
                summary=summary,
                suggested_actions=suggested_actions,
                confidence_score=0.8,  # Default confidence score
                source_documents=list(set(chunk.source_document for chunk in chunks)),
                metadata_summary=metadata_summary,
                processing_time=0.1  # Default processing time
            )
            
        except Exception as e:
            logger.error(f"Error querying government schemes: {e}")
            return RAGResponse(
                query=query,
                chunks=[],
                confidence_score=0.0,
                source_documents=[],
                processing_time=0.0
            )
    
    def _detect_document_type(self, filename: str, content: str) -> str:
        """Auto-detect document type based on filename and content."""
        filename_lower = filename.lower()
        content_lower = content.lower()
        
        if "dfg" in filename_lower or "budget" in filename_lower or "allocation" in filename_lower:
            return "budget_analysis"
        elif "empowering" in filename_lower or "farmer" in filename_lower:
            return "farmer_empowerment"
        elif "scheme" in filename_lower or "program" in filename_lower:
            return "scheme_guidelines"
        elif "policy" in filename_lower or "guidelines" in filename_lower:
            return "policy_document"
        else:
            return "government_scheme"
    
    async def _store_chunks(self, chunks: List[AgriculturalChunk]) -> None:
        """Store chunks in the vector store."""
        try:
            # Convert chunks to the format expected by the existing vector store
            # We need to create chunks with the expected structure
            from .models import AgriculturalChunk as OriginalChunk, ChunkMetadata as OriginalMetadata
            
            # Create chunks with the original structure
            original_chunks = []
            for i, chunk in enumerate(chunks):
                # Create original metadata structure with all required fields
                original_metadata = OriginalMetadata(
                    document_type=chunk.metadata.document_type,
                    document_section=chunk.metadata.document_section,
                    crop_category=chunk.metadata.crop_category,
                    crop_specific=chunk.metadata.crop_specific,
                    season=chunk.metadata.season,
                    practice_type=chunk.metadata.practice_type,
                    region=chunk.metadata.region,
                    beneficiary_type=chunk.metadata.beneficiary_type,
                    scheme_name=chunk.metadata.scheme_name,
                    budget_amount=chunk.metadata.budget_amount,
                    budget_unit=chunk.metadata.budget_unit,
                    implementation_phase=chunk.metadata.implementation_phase,
                    eligibility_criteria=chunk.metadata.eligibility_criteria,
                    benefits=chunk.metadata.benefits,
                    application_process=chunk.metadata.application_process,
                    contact_info=chunk.metadata.contact_info,
                    validity_period=chunk.metadata.validity_period,
                    language=chunk.metadata.language
                )
                
                # Create original chunk structure with all required fields
                original_chunk = OriginalChunk(
                    content=chunk.content,
                    metadata=original_metadata,
                    embedding=chunk.embedding,
                    chunk_index=chunk.chunk_index,
                    source_document=chunk.source_document
                )
                
                original_chunks.append(original_chunk)
            
            # Store using the existing method
            self.vector_store.store_chunks(original_chunks)
            logger.info(f"Stored {len(chunks)} government scheme chunks in vector store")
            
        except Exception as e:
            logger.error(f"Error storing government scheme chunks: {e}")
            # Continue processing even if storage fails
            logger.warning("Continuing with processing despite storage failure")
    
    def _generate_scheme_summary(self, chunks: List[AgriculturalChunk], query: str) -> str:
        """Generate a summary of retrieved government scheme information."""
        if not chunks:
            return "No government scheme information found."
        
        # Extract key information from chunks
        schemes = set()
        budgets = []
        beneficiaries = set()
        
        for chunk in chunks:
            if chunk.metadata.scheme_name:
                schemes.update(chunk.metadata.scheme_name)
            if chunk.metadata.budget_amount:
                budgets.append(f"{chunk.metadata.budget_amount} {chunk.metadata.budget_unit}")
            if chunk.metadata.beneficiary_type:
                beneficiaries.update(chunk.metadata.beneficiary_type)
        
        summary_parts = []
        
        if schemes:
            summary_parts.append(f"Relevant schemes: {', '.join(schemes)}")
        
        if budgets:
            summary_parts.append(f"Budget allocations: {', '.join(budgets)}")
        
        if beneficiaries:
            summary_parts.append(f"Target beneficiaries: {', '.join(beneficiaries)}")
        
        summary_parts.append(f"Found information from {len(chunks)} document sections")
        
        return ". ".join(summary_parts) + "."
    
    def _generate_suggested_actions(self, chunks: List[AgriculturalChunk], context) -> List[str]:
        """Generate suggested actions based on retrieved scheme information."""
        actions = []
        
        # Check for application processes
        for chunk in chunks:
            if chunk.metadata.application_process:
                actions.append("Review application process and requirements")
                break
        
        # Check for eligibility criteria
        for chunk in chunks:
            if chunk.metadata.eligibility_criteria:
                actions.append("Verify eligibility criteria for schemes")
                break
        
        # Check for contact information
        for chunk in chunks:
            if chunk.metadata.contact_info:
                actions.append("Contact scheme authorities for detailed information")
                break
        
        # General actions
        actions.extend([
            "Check scheme deadlines and validity periods",
            "Prepare required documents for application",
            "Monitor scheme updates and announcements"
        ])
        
        return actions[:5]  # Limit to 5 actions
    
    def _create_metadata_summary(self, chunks: List[AgriculturalChunk]) -> Dict[str, Any]:
        """Create a summary of metadata from retrieved chunks."""
        summary = {
            "total_chunks": len(chunks),
            "schemes_covered": [],
            "budget_total": 0.0,
            "beneficiary_types": set(),
            "document_sections": set(),
            "crop_categories": set(),
            "practice_types": set()
        }
        
        for chunk in chunks:
            metadata = chunk.metadata
            
            if metadata.scheme_name:
                summary["schemes_covered"].extend(metadata.scheme_name)
            
            if metadata.budget_amount:
                summary["budget_total"] += metadata.budget_amount
        
            if metadata.beneficiary_type:
                summary["beneficiary_types"].update(metadata.beneficiary_type)
            
            summary["document_sections"].add(metadata.document_section)
            
            if metadata.crop_category:
                summary["crop_categories"].update(metadata.crop_category)
            
            if metadata.practice_type:
                summary["practice_types"].update(metadata.practice_type)
        
        # Convert sets to lists for JSON serialization
        summary["beneficiary_types"] = list(summary["beneficiary_types"])
        summary["document_sections"] = list(summary["document_sections"])
        summary["crop_categories"] = list(summary["crop_categories"])
        summary["practice_types"] = list(summary["practice_types"])
        
        return summary
