"""LangChain tool for government schemes retrieval."""

import logging
from typing import Dict, Any, List
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from app.rag.govt_schemes_retrieval import GovernmentSchemesRetrievalStrategy
from app.rag.govt_schemes_vector_store import GovernmentSchemesVectorStore
from app.rag.embedding_service import EmbeddingService
from app.rag.models import QueryContext
from app.rag.config import RAGConfig

logger = logging.getLogger(__name__)


class GovernmentSchemesInput(BaseModel):
    """Input schema for government schemes tool."""
    
    query: str = Field(default="", description="The user's query about government schemes")
    beneficiary_category: str = Field(default="", description="User's beneficiary category (e.g., 'small', 'marginal', 'women', 'SC/ST')")
    scheme_interest: str = Field(default="", description="Specific schemes user is interested in (e.g., 'PM KISAN', 'PMKSY', 'PMFBY')")
    budget_range: str = Field(default="", description="Budget range preference (e.g., 'low', 'medium', 'high')")
    region: str = Field(default="", description="User's region or state")
    language: str = Field(default="en", description="Preferred language for response")


class GovernmentSchemesTool(BaseTool):
    """Tool for retrieving government scheme information."""
    
    name: str = "get_government_schemes"
    description: str = """
    Retrieve detailed information about government agricultural schemes, policies, and programs.
    
    This tool can be used in two ways:
    1. Provide a general query about government schemes
    2. Provide specific parameters (scheme_interest, beneficiary_category, region, etc.) and the tool will generate an appropriate query
    
    Use this tool when users ask about:
    - Government schemes (PM KISAN, PMKSY, PMFBY, ENAM, KCC, FPO, etc.)
    - Budget allocations and financial assistance
    - Eligibility criteria and application processes
    - Benefits and features of agricultural programs
    - Policy documents and guidelines
    - Implementation timelines and phases
    
    Parameters:
    - query: General question about schemes (optional)
    - scheme_interest: Specific scheme name (e.g., 'PM KISAN', 'insurance')
    - beneficiary_category: User category (e.g., 'SC', 'women', 'small farmers')
    - region: Geographic location (e.g., 'Bangalore', 'Karnataka')
    - budget_range: Budget preference (e.g., 'low', 'medium', 'high')
    - language: Preferred language (default: 'en')
    """
    
    args_schema: type[BaseModel] = GovernmentSchemesInput
    
    def __init__(self, config: RAGConfig = None):
        """Initialize the government schemes tool."""
        super().__init__()
        self._config = config or RAGConfig()
        self._vector_store = None
        self._embedding_service = None
        self._retrieval_strategy = None
        self._initialize_components()
    
    def _initialize_components(self) -> None:
        """Initialize the RAG components."""
        try:
            self._vector_store = GovernmentSchemesVectorStore(self._config)
            self._embedding_service = EmbeddingService(self._config)
            self._retrieval_strategy = GovernmentSchemesRetrievalStrategy(
                self._vector_store, 
                self._embedding_service, 
                self._config
            )
            logger.info("Government schemes tool components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize government schemes tool components: {e}")
            raise
    
    def _run(self, **kwargs) -> str:
        """Run the government schemes tool (synchronous wrapper for async method)."""
        import asyncio
        
        try:
            # Run the async method in a new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._arun(**kwargs))
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Error running government schemes tool: {e}")
            return f"I encountered an error retrieving government scheme information: {str(e)}"
    
    async def _arun(self, **kwargs) -> str:
        """Run the government schemes tool asynchronously."""
        try:
            # Extract input parameters
            query = kwargs.get("query", "")
            beneficiary_category = kwargs.get("beneficiary_category", "")
            scheme_interest = kwargs.get("scheme_interest", "")
            budget_range = kwargs.get("budget_range", "")
            region = kwargs.get("region", "")
            language = kwargs.get("language", "en")
            
            # Generate query from other parameters if query is empty
            if not query:
                query_parts = []
                if scheme_interest:
                    query_parts.append(f"{scheme_interest} scheme")
                if beneficiary_category:
                    query_parts.append(f"for {beneficiary_category} farmers")
                if region:
                    query_parts.append(f"in {region}")
                if budget_range:
                    query_parts.append(f"with {budget_range} budget")
                
                if query_parts:
                    query = " ".join(query_parts)
                else:
                    query = "government agricultural schemes"
                
                logger.info(f"Generated query from parameters: {query}")
            
            # Create query context
            context = QueryContext(
                query=query,
                language=language,
                beneficiary_category=beneficiary_category if beneficiary_category else None,
                scheme_interest=[scheme_interest] if scheme_interest else [],
                budget_range=budget_range if budget_range else None,
                region=region if region else None
            )
            
            # Retrieve relevant chunks
            chunks = await self._retrieval_strategy.retrieve(query, context)
            
            if not chunks:
                return "I couldn't find specific information about that government scheme topic. Please try rephrasing your question or ask about a different aspect of government agricultural programs."
            
            # Format the response
            response = self._format_government_schemes_response(chunks, query)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in government schemes tool: {e}")
            return f"I encountered an error retrieving government scheme information: {str(e)}"
    
    def _format_government_schemes_response(self, chunks: List, query: str) -> str:
        """Format the government schemes response in a user-friendly way."""
        try:
            response = f"**Government Scheme Information**\n\n"
            
            # Extract key information from chunks
            schemes = set()
            budgets = []
            beneficiaries = set()
            eligibility = []
            regions = set()
            
            for chunk in chunks[:3]:  # Top 3 chunks
                metadata = chunk.metadata
                
                # Collect scheme names
                if metadata.scheme_name:
                    schemes.update(metadata.scheme_name)
                
                # Collect budget information
                if metadata.budget_amount and metadata.budget_unit:
                    budgets.append(f"{metadata.budget_amount} {metadata.budget_unit}")
                
                # Collect beneficiary types
                if metadata.beneficiary_type:
                    beneficiaries.update(metadata.beneficiary_type)
                
                # Collect eligibility criteria
                if metadata.eligibility_criteria:
                    eligibility.extend(metadata.eligibility_criteria)
                
                # Collect regions
                if metadata.region:
                    regions.update(metadata.region)
            
            # Build comprehensive response
            if schemes:
                response += f"**Relevant Schemes:** {', '.join(schemes)}\n\n"
            
            if budgets:
                response += f"**Budget Allocations:** {', '.join(budgets)}\n\n"
            
            if beneficiaries:
                response += f"**Target Beneficiaries:** {', '.join(beneficiaries)}\n\n"
            
            if regions:
                response += f"**Applicable Regions:** {', '.join(regions)}\n\n"
            
            if eligibility:
                response += f"**Eligibility Criteria:** {', '.join(eligibility[:3])}\n\n"
            
            # Add chunk content summaries
            for i, chunk in enumerate(chunks[:2], 1):
                content_preview = chunk.content[:300] + "..." if len(chunk.content) > 300 else chunk.content
                response += f"**Details {i}:** {content_preview}\n\n"
            
            # Add next steps
            response += "**Next Steps:** Check official scheme websites, contact local agricultural offices, or visit nearest Common Service Centers for detailed application procedures."
            
            return response
            
        except Exception as e:
            logger.error(f"Error formatting government schemes response: {e}")
            return "I found government scheme information but encountered an error formatting the response. Please try asking a more specific question."
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get information about the tool and its capabilities."""
        try:
            collection_info = self._vector_store.get_collection_info() if self._vector_store else {}
            return {
                "tool_name": self.name,
                "description": self.description,
                "collection_info": collection_info,
                "capabilities": [
                    "Government scheme information retrieval",
                    "Budget allocation details",
                    "Eligibility criteria",
                    "Beneficiary information",
                    "Application processes",
                    "Policy guidelines"
                ]
            }
        except Exception as e:
            logger.error(f"Error getting tool info: {e}")
            return {"error": str(e)}
