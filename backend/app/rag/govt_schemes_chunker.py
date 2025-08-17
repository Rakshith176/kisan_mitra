"""
Specialized chunking strategy for government scheme documents.
Optimized for policy documents, budget allocations, and scheme guidelines.
"""

import logging
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

from .models import AgriculturalChunk, ChunkMetadata
from .config import RAGConfig

logger = logging.getLogger(__name__)


class GovernmentSchemesChunker:
    """
    Specialized chunker for government scheme documents.
    Optimized for policy documents, budget allocations, and scheme guidelines.
    """
    
    def __init__(self, config: RAGConfig = None):
        """Initialize the government schemes chunker.
        
        Args:
            config: RAG configuration, uses default if None
        """
        self.config = config or RAGConfig()
        
        # Government document patterns
        self.section_patterns = [
            # Budget and allocation patterns
            r'^(Rs\.?\s*\d+\.?\d*\s*(?:crore|lakh|thousand|million|billion))',
            r'^(₹\s*\d+\.?\d*\s*(?:crore|lakh|thousand|million|billion))',
            r'^(Budget\s*Allocation|Allocation|Budget)',
            
            # Scheme identification patterns
            r'^(Scheme|Program|Initiative|Mission|Campaign)',
            r'^(PM\s*KISAN|PMKSY|PMFBY|eNAM|KCC|FPO)',
            r'^(Pradhan Mantri|Prime Minister|Central|State)',
            
            # Policy section patterns
            r'^(\d+\.?\s*)([A-Z][^:]*?)(?:\\s*[:.]|$)',
            r'^([A-Z][^:]*?)(?:\\s*[:.]|$)',
            r'^(Objective|Goal|Target|Aim|Purpose)',
            
            # Financial and implementation patterns
            r'^(Implementation|Execution|Monitoring|Evaluation)',
            r'^(Eligibility|Criteria|Requirements|Conditions)',
            r'^(Benefits|Advantages|Features|Highlights)',
            r'^(Application|Registration|Enrollment|Process)',
            
            # Geographic and demographic patterns
            r'^(State|District|Village|Region|Zone)',
            r'^(Small|Marginal|Landless|Women|Youth|SC/ST)',
            
            # Time-based patterns
            r'^(FY\s*\d{4}-\d{2}|Financial Year|Year)',
            r'^(Phase|Stage|Period|Duration|Timeline)',
        ]
        
        # Compile regex patterns
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.section_patterns]
        
        # Scheme-specific keywords for better categorization
        self.scheme_keywords = {
            "pm_kisan": ["PM KISAN", "Pradhan Mantri Kisan Samman Nidhi", "KISAN", "Samman Nidhi"],
            "pmksy": ["PMKSY", "Pradhan Mantri Krishi Sinchayee Yojana", "Krishi Sinchayee", "Irrigation"],
            "pmfby": ["PMFBY", "Pradhan Mantri Fasal Bima Yojana", "Fasal Bima", "Crop Insurance"],
            "enam": ["eNAM", "National Agriculture Market", "Electronic Trading", "Mandi"],
            "kcc": ["KCC", "Kisan Credit Card", "Credit Card", "Loan"],
            "fpo": ["FPO", "Farmer Producer Organization", "Producer Organization"],
            "soil_health": ["Soil Health Card", "Soil Testing", "Soil Health"],
            "organic_farming": ["Organic Farming", "Paramparagat Krishi Vikas Yojana", "PKVY"],
            "horticulture": ["Horticulture", "Mission for Integrated Development", "MIDH"],
            "dairy": ["Dairy", "National Dairy Plan", "NDP", "Milk"],
            "fisheries": ["Fisheries", "Blue Revolution", "Pradhan Mantri Matsya Sampada Yojana"],
            "weather": ["Weather", "Climate", "Rainfall", "Temperature", "Forecast"],
            "market": ["Market", "Price", "Mandi", "Trading", "Export"],
            "technology": ["Technology", "Digital", "ICT", "Mobile", "App"],
            "infrastructure": ["Infrastructure", "Road", "Storage", "Cold Storage", "Warehouse"],
            "research": ["Research", "ICAR", "KVK", "Extension", "Training"]
        }
        
        # Budget allocation patterns
        self.budget_patterns = [
            r'Rs\.?\s*(\d+\.?\d*)\s*(crore|lakh|thousand|million|billion)',
            r'₹\s*(\d+\.?\d*)\s*(crore|lakh|thousand|million|billion)',
            r'(\d+\.?\d*)\s*(crore|lakh|thousand|million|billion)\s*rupees?',
            r'Budget.*?(\d+\.?\d*)\s*(crore|lakh|thousand|million|billion)',
            r'Allocation.*?(\d+\.?\d*)\s*(crore|lakh|thousand|million|billion)'
        ]
        
        # Eligibility and beneficiary patterns
        self.eligibility_patterns = [
            r'(Small|Marginal|Landless|Women|Youth|SC/ST|OBC|General)\s*farmers?',
            r'Farmers?\s*with\s*(?:land\s*holding|farm\s*size)\s*(?:up\s*to|less\s*than|maximum)\s*(\d+\.?\d*)\s*(?:hectares?|acres?)',
            r'(?:Eligible|Qualified|Qualifying)\s*farmers?',
            r'(?:Age|Income|Land|Education)\s*(?:criteria|requirement|condition)'
        ]
        
        # Implementation timeline patterns
        self.timeline_patterns = [
            r'(FY\s*\d{4}-\d{2}|Financial Year\s*\d{4}-\d{2})',
            r'(Phase\s*[IVX]+|Stage\s*\d+)',
            r'(Implementation|Execution|Rollout)\s*(?:period|duration|timeline)',
            r'(Start|Begin|Launch|Complete|End)\s*date'
        ]
    
    def chunk_document(self, text: str, document_type: str = "government_scheme") -> List[AgriculturalChunk]:
        """
        Chunk government scheme document into semantic pieces.
        
        Args:
            text: Document text content
            document_type: Type of document (default: government_scheme)
            
        Returns:
            List of agricultural chunks with metadata
        """
        try:
            logger.info(f"Chunking government scheme document: {document_type}")
            
            # Clean and preprocess text
            cleaned_text = self._preprocess_text(text)
            
            # Split into sections based on patterns
            sections = self._split_into_sections(cleaned_text)
            
            # Create chunks from sections
            chunks = []
            for i, section in enumerate(sections):
                if len(section.strip()) < self.config.min_chunk_tokens:
                    continue
                
                # Create chunk with specialized metadata
                chunk = self._create_chunk(section, document_type, i)
                chunks.append(chunk)
            
            logger.info(f"Created {len(chunks)} chunks from government scheme document")
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking government scheme document: {e}")
            return []
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for better chunking."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers
        text = re.sub(r'Page\s+\d+', '', text)
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
        
        # Clean up bullet points and lists
        text = re.sub(r'^\s*[•·▪▫]\s*', '- ', text, flags=re.MULTILINE)
        
        return text.strip()
    
    def _split_into_sections(self, text: str) -> List[str]:
        """Split text into sections based on government document patterns."""
        sections = []
        current_section = ""
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line starts a new section
            is_new_section = False
            for pattern in self.compiled_patterns:
                if pattern.match(line):
                    is_new_section = True
                    break
            
            if is_new_section and current_section:
                # Save current section and start new one
                sections.append(current_section.strip())
                current_section = line
            else:
                # Add to current section
                current_section += " " + line
        
        # Add the last section
        if current_section.strip():
            sections.append(current_section.strip())
        
        return sections
    
    def _create_chunk(self, content: str, document_type: str, chunk_index: int) -> AgriculturalChunk:
        """Create a chunk with specialized metadata for government schemes."""
        
        # Extract metadata from content
        metadata = self._extract_scheme_metadata(content)
        
        # Create chunk metadata
        chunk_metadata = ChunkMetadata(
            document_type=document_type,
            document_section=metadata.get("section_type", "general"),
            crop_category=metadata.get("crop_categories", []),
            crop_specific=metadata.get("crop_specific", []),
            season=metadata.get("seasons", []),
            practice_type=metadata.get("practice_types", []),
            region=metadata.get("regions", []),
            beneficiary_type=metadata.get("beneficiary_types", []),
            scheme_name=metadata.get("scheme_names", []),
            budget_amount=metadata.get("budget_amount"),
            budget_unit=metadata.get("budget_unit"),
            implementation_phase=metadata.get("implementation_phase"),
            eligibility_criteria=metadata.get("eligibility_criteria", []),
            benefits=metadata.get("benefits", []),
            application_process=metadata.get("application_process", []),
            contact_info=metadata.get("contact_info", []),
            validity_period=metadata.get("validity_period"),
            language="en"
        )
        
        return AgriculturalChunk(
            content=content,
            metadata=chunk_metadata,
            chunk_index=chunk_index,
            source_document=document_type
        )
    
    def _extract_scheme_metadata(self, content: str) -> Dict[str, Any]:
        """Extract specialized metadata from government scheme content."""
        metadata = {}
        
        # Extract scheme names
        scheme_names = []
        for scheme_key, keywords in self.scheme_keywords.items():
            for keyword in keywords:
                if keyword.lower() in content.lower():
                    scheme_names.append(scheme_key)
                    break
        
        if scheme_names:
            metadata["scheme_names"] = scheme_names
        
        # Extract budget information
        for pattern in self.budget_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                amount, unit = matches[0]
                metadata["budget_amount"] = float(amount)
                metadata["budget_unit"] = unit
                break
        
        # Extract beneficiary types
        beneficiary_types = []
        for pattern in self.eligibility_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            beneficiary_types.extend(matches)
        
        if beneficiary_types:
            metadata["beneficiary_types"] = list(set(beneficiary_types))
        
        # Extract implementation timeline
        for pattern in self.timeline_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                metadata["implementation_phase"] = matches[0]
                break
        
        # Determine section type
        section_type = self._classify_section_type(content)
        metadata["section_type"] = section_type
        
        # Extract crop categories
        crop_keywords = ["rice", "wheat", "maize", "pulses", "oilseeds", "vegetables", "fruits", "cotton", "sugarcane"]
        crop_categories = []
        for crop in crop_keywords:
            if crop.lower() in content.lower():
                crop_categories.append(crop)
        
        if crop_categories:
            metadata["crop_categories"] = crop_categories
        
        # Extract practice types
        practice_keywords = ["irrigation", "fertilizer", "pest_management", "soil_health", "market_access", "credit", "insurance"]
        practice_types = []
        for practice in practice_keywords:
            if practice.lower() in content.lower():
                practice_types.append(practice)
        
        if practice_types:
            metadata["practice_types"] = practice_types
        
        # Extract regions
        region_keywords = ["north", "south", "east", "west", "central", "northeast", "himalayan", "coastal", "arid"]
        regions = []
        for region in region_keywords:
            if region.lower() in content.lower():
                regions.append(region)
        
        if regions:
            metadata["regions"] = regions
        
        return metadata
    
    def _classify_section_type(self, content: str) -> str:
        """Classify the type of section based on content."""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["budget", "allocation", "fund", "financial", "rupee", "crore", "lakh"]):
            return "budget_allocation"
        elif any(word in content_lower for word in ["objective", "goal", "target", "aim", "purpose"]):
            return "objectives"
        elif any(word in content_lower for word in ["eligibility", "criteria", "requirement", "condition", "qualification"]):
            return "eligibility"
        elif any(word in content_lower for word in ["benefit", "advantage", "feature", "highlight", "incentive"]):
            return "benefits"
        elif any(word in content_lower for word in ["application", "registration", "enrollment", "process", "procedure"]):
            return "application_process"
        elif any(word in content_lower for word in ["implementation", "execution", "monitoring", "evaluation", "timeline"]):
            return "implementation"
        elif any(word in content_lower for word in ["contact", "phone", "email", "address", "website"]):
            return "contact_info"
        elif any(word in content_lower for word in ["scheme", "program", "initiative", "mission", "campaign"]):
            return "scheme_overview"
        else:
            return "general"
    
    def get_chunking_summary(self, chunks: List[AgriculturalChunk]) -> Dict[str, Any]:
        """Get summary statistics for government scheme chunks."""
        if not chunks:
            return {}
        
        summary = {
            "total_chunks": len(chunks),
            "document_types": {},
            "section_types": {},
            "scheme_names": {},
            "budget_ranges": {},
            "beneficiary_types": {},
            "crop_categories": {},
            "practice_types": {},
            "regions": {},
            "avg_chunk_size": 0
        }
        
        total_size = 0
        
        for chunk in chunks:
            metadata = chunk.metadata
            
            # Count document types
            doc_type = metadata.document_type
            summary["document_types"][doc_type] = summary["document_types"].get(doc_type, 0) + 1
            
            # Count section types
            section_type = metadata.document_section
            summary["section_types"][section_type] = summary["section_types"].get(section_type, 0) + 1
            
            # Count scheme names
            if metadata.scheme_name:
                for scheme in metadata.scheme_name:
                    summary["scheme_names"][scheme] = summary["scheme_names"].get(scheme, 0) + 1
            
            # Count budget ranges
            if metadata.budget_amount:
                if metadata.budget_amount < 100:
                    range_key = "0-100 crore"
                elif metadata.budget_amount < 1000:
                    range_key = "100-1000 crore"
                elif metadata.budget_amount < 10000:
                    range_key = "1000-10000 crore"
                else:
                    range_key = "10000+ crore"
                summary["budget_ranges"][range_key] = summary["budget_ranges"].get(range_key, 0) + 1
            
            # Count beneficiary types
            if metadata.beneficiary_type:
                for beneficiary in metadata.beneficiary_type:
                    summary["beneficiary_types"][beneficiary] = summary["beneficiary_types"].get(beneficiary, 0) + 1
            
            # Count crop categories
            if metadata.crop_category:
                for crop in metadata.crop_category:
                    summary["crop_categories"][crop] = summary["crop_categories"].get(crop, 0) + 1
            
            # Count practice types
            if metadata.practice_type:
                for practice in metadata.practice_type:
                    summary["practice_types"][practice] = summary["practice_types"].get(practice, 0) + 1
            
            # Count regions
            if metadata.region:
                for region in metadata.region:
                    summary["regions"][region] = summary["regions"].get(region, 0) + 1
            
            total_size += len(chunk.content)
        
        summary["avg_chunk_size"] = total_size / len(chunks) if chunks else 0
        
        return summary
