#!/usr/bin/env python3
"""CLI script to process PDFs and populate the RAG system."""

import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from rag.document_processor import DocumentProcessor
from rag.config import RAGConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def process_pdfs(pdf_dir: str, reset: bool = False):
    """Process PDFs from a directory.
    
    Args:
        pdf_dir: Directory containing PDF files
        reset: Whether to reset the vector store before processing
    """
    try:
        # Initialize document processor
        processor = DocumentProcessor()
        
        # Reset vector store if requested
        if reset:
            logger.info("Resetting vector store...")
            processor.reset_vector_store()
            logger.info("Vector store reset complete")
        
        # Find PDF files
        pdf_path = Path(pdf_dir)
        if not pdf_path.exists():
            logger.error(f"Directory not found: {pdf_dir}")
            return
        
        pdf_files = list(pdf_path.glob("*.pdf"))
        if not pdf_files:
            logger.warning(f"No PDF files found in {pdf_dir}")
            return
        
        logger.info(f"Found {len(pdf_files)} PDF files")
        
        # Process each PDF
        total_chunks = 0
        for pdf_file in pdf_files:
            logger.info(f"Processing {pdf_file.name}...")
            
            try:
                # Auto-detect document type
                if "gap" in pdf_file.name.lower():
                    doc_type = "bharat_gap"
                elif "handbook" in pdf_file.name.lower():
                    doc_type = "farmer_handbook"
                else:
                    doc_type = None
                
                # Process document
                chunks = await processor.process_document(str(pdf_file), doc_type)
                total_chunks += len(chunks)
                
                logger.info(f"  - Created {len(chunks)} chunks")
                
                # Get document info
                doc_info = processor.get_pdf_info(str(pdf_file))
                logger.info(f"  - Document info: {doc_info}")
                
            except Exception as e:
                logger.error(f"  - Failed to process {pdf_file.name}: {e}")
                continue
        
        logger.info(f"Processing complete. Total chunks created: {total_chunks}")
        
        # Get final stats
        stats = processor.get_processing_stats()
        logger.info(f"Final stats: {stats}")
        
    except Exception as e:
        logger.error(f"PDF processing failed: {e}")
        raise


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Process PDFs for RAG system")
    parser.add_argument(
        "pdf_dir", 
        help="Directory containing PDF files to process"
    )
    parser.add_argument(
        "--reset", 
        action="store_true", 
        help="Reset vector store before processing"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Process PDFs
    await process_pdfs(args.pdf_dir, args.reset)


if __name__ == "__main__":
    asyncio.run(main())
