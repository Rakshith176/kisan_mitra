"""PDF text extraction service."""

import logging
from pathlib import Path
from typing import Optional

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Service for extracting text from PDF documents."""
    
    def __init__(self):
        """Initialize the PDF extractor."""
        if not PYPDF2_AVAILABLE and not PDFPLUMBER_AVAILABLE:
            raise ImportError(
                "Neither PyPDF2 nor pdfplumber is available. "
                "Please install one: pip install PyPDF2 or pip install pdfplumber"
            )
        
        logger.info(f"PDF extractor initialized. PyPDF2: {PYPDF2_AVAILABLE}, pdfplumber: {PDFPLUMBER_AVAILABLE}")
    
    def extract(self, pdf_path: str) -> str:
        """Extract text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            ValueError: If PDF file is invalid or empty
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if not pdf_path.is_file():
            raise ValueError(f"Path is not a file: {pdf_path}")
        
        try:
            # Try pdfplumber first (better text extraction)
            if PDFPLUMBER_AVAILABLE:
                text = self._extract_with_pdfplumber(pdf_path)
            else:
                text = self._extract_with_pypdf2(pdf_path)
            
            if not text or not text.strip():
                raise ValueError(f"PDF file appears to be empty or unreadable: {pdf_path}")
            
            logger.info(f"Successfully extracted {len(text)} characters from {pdf_path}")
            return text
            
        except Exception as e:
            logger.error(f"Failed to extract text from {pdf_path}: {e}")
            raise
    
    def _extract_with_pdfplumber(self, pdf_path: Path) -> str:
        """Extract text using pdfplumber (preferred method).
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content
        """
        text_parts = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(f"--- Page {page_num + 1} ---\n{page_text}")
                    else:
                        logger.warning(f"Page {page_num + 1} returned no text")
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                    continue
        
        return "\n\n".join(text_parts)
    
    def _extract_with_pypdf2(self, pdf_path: Path) -> str:
        """Extract text using PyPDF2 (fallback method).
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content
        """
        text_parts = []
        
        with open(pdf_path, 'rb') as file:
            try:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    try:
                        page = pdf_reader.pages[page_num]
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(f"--- Page {page_num + 1} ---\n{page_text}")
                        else:
                            logger.warning(f"Page {page_num + 1} returned no text")
                    except Exception as e:
                        logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                        continue
                        
            except Exception as e:
                raise ValueError(f"Failed to read PDF file: {e}")
        
        return "\n\n".join(text_parts)
    
    def get_pdf_info(self, pdf_path: str) -> dict:
        """Get basic information about a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with PDF information
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        info = {
            "file_path": str(pdf_path),
            "file_size_mb": round(pdf_path.stat().st_size / (1024 * 1024), 2),
            "extractor_available": {
                "pdfplumber": PDFPLUMBER_AVAILABLE,
                "pypdf2": PYPDF2_AVAILABLE
            }
        }
        
        try:
            if PDFPLUMBER_AVAILABLE:
                with pdfplumber.open(pdf_path) as pdf:
                    info["total_pages"] = len(pdf.pages)
                    info["extractor_used"] = "pdfplumber"
            elif PYPDF2_AVAILABLE:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    info["total_pages"] = len(pdf_reader.pages)
                    info["extractor_used"] = "pypdf2"
        except Exception as e:
            logger.warning(f"Could not get page count: {e}")
            info["total_pages"] = "unknown"
        
        return info
