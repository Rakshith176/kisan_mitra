"""Document chunking service for agricultural documents."""

import logging
import re
from typing import List, Dict, Any
from pathlib import Path

from .models import AgriculturalChunk, ChunkMetadata
from .config import RAGConfig

logger = logging.getLogger(__name__)


class AgriculturalChunker:
    """Service for chunking agricultural documents into semantic pieces."""
    
    def __init__(self, config: RAGConfig = None):
        """Initialize the chunker.
        
        Args:
            config: RAG configuration, uses default if None
        """
        self.config = config or RAGConfig()
        
        # Agricultural domain patterns
        self.section_patterns = [
            r'^(\d+\.?\s*)([A-Z][^:]*?)(?:\s*[:.]|$)',  # Numbered sections
            r'^([A-Z][^:]*?)(?:\s*[:.]|$)',  # Capitalized sections
            r'^(\d+\.\d+\.?\s*)([^:]*?)(?:\s*[:.]|$)',  # Sub-sections
        ]
        
        # Agricultural keywords for section identification
        self.agricultural_keywords = {
            'pest_management': ['pest', 'disease', 'insect', 'fungus', 'virus', 'control'],
            'soil_health': ['soil', 'fertilizer', 'nutrient', 'organic', 'compost'],
            'irrigation': ['irrigation', 'water', 'drainage', 'moisture'],
            'harvest': ['harvest', 'yield', 'storage', 'post-harvest'],
            'cultivation': ['planting', 'sowing', 'transplanting', 'spacing'],
            'gap_certification': ['gap', 'certification', 'standard', 'compliance', 'audit']
        }
    
    def create_chunks(self, text: str, document_type: str = "unknown") -> List[AgriculturalChunk]:
        """Create chunks from document text.
        
        Args:
            text: Document text to chunk
            document_type: Type of document for metadata
            
        Returns:
            List of agricultural chunks
        """
        try:
            logger.info(f"Creating chunks for document type: {document_type}")
            
            # Clean and preprocess text
            cleaned_text = self._clean_text(text)
            
            # Identify sections
            sections = self._identify_sections(cleaned_text)
            
            # Create chunks from sections
            chunks = []
            chunk_counter = 0
            
            for section_name, section_content in sections:
                section_chunks = self._chunk_section(
                    section_content, 
                    section_name, 
                    document_type, 
                    chunk_counter
                )
                chunks.extend(section_chunks)
                chunk_counter += len(section_chunks)
            
            logger.info(f"Created {len(chunks)} chunks from document")
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to create chunks: {e}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean and preprocess text.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)]', '', text)
        
        # Normalize line breaks
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        return text.strip()
    
    def _identify_sections(self, text: str) -> List[tuple]:
        """Identify document sections.
        
        Args:
            text: Cleaned text
            
        Returns:
            List of (section_name, section_content) tuples
        """
        lines = text.split('\n')
        sections = []
        current_section = "Introduction"
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line is a section header
            section_name = self._is_section_header(line)
            if section_name:
                # Save previous section
                if current_content:
                    sections.append((current_section, '\n'.join(current_content)))
                
                # Start new section
                current_section = section_name
                current_content = []
            else:
                current_content.append(line)
        
        # Add last section
        if current_content:
            sections.append((current_section, '\n'.join(current_content)))
        
        return sections
    
    def _is_section_header(self, line: str) -> str:
        """Check if a line is a section header.
        
        Args:
            line: Line to check
            
        Returns:
            Section name if header, empty string otherwise
        """
        for pattern in self.section_patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                section_name = match.group(2) if len(match.groups()) > 1 else match.group(1)
                return section_name.strip()
        
        return ""
    
    def _chunk_section(self, content: str, section_name: str, document_type: str, start_counter: int) -> List[AgriculturalChunk]:
        """Chunk a section into smaller pieces.
        
        Args:
            content: Section content
            section_name: Name of the section
            document_type: Type of document
            start_counter: Starting chunk counter
            
        Returns:
            List of chunks for this section
        """
        chunks = []
        
        # Simple token-based chunking (approximate)
        words = content.split()
        current_chunk = []
        current_length = 0
        chunk_id = start_counter
        
        for word in words:
            current_chunk.append(word)
            current_length += len(word) + 1  # +1 for space
            
            # Check if we should create a chunk
            if current_length >= self.config.max_tokens * 4:  # Rough approximation
                chunk_text = ' '.join(current_chunk)
                chunk = self._create_chunk(
                    chunk_text, 
                    section_name, 
                    document_type, 
                    chunk_id,
                    len(current_chunk)
                )
                chunks.append(chunk)
                
                # Start new chunk with overlap
                overlap_words = current_chunk[-self.config.overlap_tokens//4:]  # Rough approximation
                current_chunk = overlap_words
                current_length = sum(len(w) + 1 for w in overlap_words)
                chunk_id += 1
        
        # Add remaining content as final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            if len(chunk_text.strip()) >= self.config.min_chunk_tokens * 4:  # Rough approximation
                chunk = self._create_chunk(
                    chunk_text, 
                    section_name, 
                    document_type, 
                    chunk_id,
                    len(current_chunk)
                )
                chunks.append(chunk)
        
        return chunks
    
    def _create_chunk(self, content: str, section_name: str, document_type: str, chunk_id: int, word_count: int) -> AgriculturalChunk:
        """Create a chunk with metadata.
        
        Args:
            content: Chunk content
            section_name: Section name
            document_type: Document type
            chunk_id: Chunk identifier
            word_count: Number of words in chunk
            
        Returns:
            Agricultural chunk
        """
        # Determine practice type from section name
        practice_type = self._classify_practice_type(section_name)
        
        # Determine crop categories (basic classification)
        crop_categories = self._extract_crop_categories(content)
        
        # Determine seasons
        seasons = self._extract_seasons(content)
        
        metadata = ChunkMetadata(
            document_type=document_type,
            document_section=section_name,
            crop_category=crop_categories,
            crop_specific=[],
            season=seasons,
            practice_type=practice_type,
            compliance_level="basic",  # Default, can be enhanced
            chunk_size_tokens=word_count,
            chunk_position=chunk_id,
            parent_section=section_name
        )
        
        return AgriculturalChunk(
            chunk_id=f"{document_type}_{section_name}_{chunk_id}",
            content=content,
            metadata=metadata
        )
    
    def _classify_practice_type(self, section_name: str) -> str:
        """Classify the practice type based on section name.
        
        Args:
            section_name: Name of the section
            
        Returns:
            Practice type classification
        """
        section_lower = section_name.lower()
        
        for practice_type, keywords in self.agricultural_keywords.items():
            if any(keyword in section_lower for keyword in keywords):
                return practice_type
        
        return "general"
    
    def _extract_crop_categories(self, content: str) -> List[str]:
        """Extract crop categories from content.
        
        Args:
            content: Chunk content
            
        Returns:
            List of crop categories
        """
        content_lower = content.lower()
        categories = []
        
        if any(word in content_lower for word in ['rice', 'wheat', 'maize', 'corn']):
            categories.append('cereals')
        if any(word in content_lower for word in ['pulses', 'beans', 'lentils', 'peas']):
            categories.append('pulses')
        if any(word in content_lower for word in ['tomato', 'potato', 'onion', 'vegetable']):
            categories.append('vegetables')
        if any(word in content_lower for word in ['mango', 'apple', 'banana', 'fruit']):
            categories.append('fruits')
        
        return categories
    
    def _extract_seasons(self, content: str) -> List[str]:
        """Extract agricultural seasons from content.
        
        Args:
            content: Chunk content
            
        Returns:
            List of applicable seasons
        """
        content_lower = content.lower()
        seasons = []
        
        if any(word in content_lower for word in ['kharif', 'monsoon', 'rainy']):
            seasons.append('kharif')
        if any(word in content_lower for word in ['rabi', 'winter', 'cold']):
            seasons.append('rabi')
        if any(word in content_lower for word in ['zaid', 'summer', 'hot']):
            seasons.append('zaid')
        
        if not seasons:
            seasons.append('all_season')
        
        return seasons
