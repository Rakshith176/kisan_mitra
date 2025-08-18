#!/usr/bin/env python3
"""Script to process government scheme PDFs using specialized chunking strategy."""

import asyncio
import logging
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from rag.govt_schemes_processor import GovernmentSchemesProcessor
from rag.config import RAGConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def process_government_schemes():
    """Process government scheme PDFs using specialized chunking."""
    try:
        # Initialize the government schemes processor
        processor = GovernmentSchemesProcessor()
        logger.info("Government schemes processor initialized successfully")
        
        # Path to government schemes directory
        govt_schemes_dir = Path("../pdfs/govt_schemes")
        
        if not govt_schemes_dir.exists():
            logger.error(f"Government schemes directory not found: {govt_schemes_dir}")
            return
        
        # Process all PDFs in the directory
        logger.info(f"Processing government scheme documents in: {govt_schemes_dir}")
        results = await processor.process_directory(govt_schemes_dir)
        
        if not results:
            logger.warning("No government scheme documents were processed successfully")
            return
        
        # Display processing results
        logger.info("\n" + "="*60)
        logger.info("GOVERNMENT SCHEMES PROCESSING COMPLETE")
        logger.info("="*60)
        
        total_chunks = 0
        for doc_name, chunks in results.items():
            logger.info(f"\nDocument: {doc_name}")
            logger.info(f"Chunks created: {len(chunks)}")
            
            # Show chunk metadata summary
            if chunks:
                summary = processor.chunker.get_chunking_summary(chunks)
                logger.info(f"Section types: {summary.get('section_types', {})}")
                logger.info(f"Scheme names: {summary.get('scheme_names', {})}")
                logger.info(f"Budget ranges: {summary.get('budget_ranges', {})}")
                logger.info(f"Beneficiary types: {summary.get('beneficiary_types', {})}")
            
            total_chunks += len(chunks)
        
        logger.info(f"\nTotal documents processed: {len(results)}")
        logger.info(f"Total chunks created: {total_chunks}")
        
        # Test querying the processed schemes
        logger.info("\n" + "="*60)
        logger.info("TESTING GOVERNMENT SCHEME QUERIES")
        logger.info("="*60)
        
        test_queries = [
            "What are the budget allocations for agriculture in 2025-26?",
            "How can small farmers benefit from government schemes?",
            "What are the eligibility criteria for PM KISAN?",
            "What irrigation schemes are available for farmers?",
            "How to apply for crop insurance schemes?"
        ]
        
        for query in test_queries:
            logger.info(f"\nQuery: {query}")
            
            # Create context for the query
            context = {
                "crops": ["rice", "wheat"],
                "season": "kharif",
                "language": "en",
                "location": "Karnataka",
                "farm_size": 2.5,
                "experience_years": 5,
                "beneficiary_category": "small_farmer",
                "scheme_interest": ["pm_kisan", "pmksy"],
                "budget_range": "0-1000 crore",
                "region": "south"
            }
            
            try:
                response = await processor.query_schemes(query, context)
                
                if response.chunks:
                    logger.info(f"Found {len(response.chunks)} relevant chunks")
                    logger.info(f"Summary: {response.summary}")
                    logger.info(f"Suggested actions: {response.suggested_actions[:2]}")  # Show first 2 actions
                    logger.info(f"Source documents: {response.source_documents}")
                else:
                    logger.info("No relevant information found")
                    
            except Exception as e:
                logger.error(f"Error querying schemes: {e}")
        
        logger.info("\n" + "="*60)
        logger.info("GOVERNMENT SCHEMES PROCESSING AND TESTING COMPLETE")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"Error processing government schemes: {e}")
        raise


async def main():
    """Main function."""
    await process_government_schemes()


if __name__ == "__main__":
    asyncio.run(main())
