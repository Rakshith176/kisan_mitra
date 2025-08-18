"""FastAPI router for RAG endpoints."""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from pydantic import BaseModel

from .rag_service import RAGService
from .document_processor import DocumentProcessor
from .models import QueryContext
from .config import RAGConfig

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["RAG"])

# Global instances (in production, use dependency injection)
rag_service = None
doc_processor = None


def get_rag_service() -> RAGService:
    """Get RAG service instance."""
    global rag_service
    if rag_service is None:
        rag_service = RAGService()
    return rag_service


def get_doc_processor() -> DocumentProcessor:
    """Get document processor instance."""
    global doc_processor
    if doc_processor is None:
        doc_processor = DocumentProcessor()
    return doc_processor


# Request/Response Models
class QueryRequest(BaseModel):
    """Request model for RAG queries."""
    query: str
    user_crops: Optional[List[str]] = None
    current_season: Optional[str] = None
    user_region: Optional[str] = None
    language: str = "en"


class FilteredQueryRequest(QueryRequest):
    """Request model for filtered RAG queries."""
    filter_criteria: Dict[str, Any] = {}


class DocumentProcessRequest(BaseModel):
    """Request model for document processing."""
    document_type: Optional[str] = None


class DocumentProcessResponse(BaseModel):
    """Response model for document processing."""
    success: bool
    message: str
    chunks_created: int
    document_info: Dict[str, Any]


class QueryResponse(BaseModel):
    """Response model for RAG queries."""
    query: str
    context: Dict[str, Any]
    retrieved_chunks: int
    chunks: List[Dict[str, Any]]
    summary: Dict[str, Any]
    suggested_actions: List[str]


# Endpoints
@router.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """Query the RAG system with a user question."""
    try:
        rag_service = get_rag_service()
        
        # Create query context
        context = QueryContext(
            user_crops=request.user_crops,
            current_season=request.current_season,
            user_region=request.user_region,
            language=request.language
        )
        
        # Process query
        result = await rag_service.query(request.query, context)
        
        return QueryResponse(**result)
        
    except Exception as e:
        logger.error(f"Failed to process RAG query: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


@router.post("/query/filtered", response_model=QueryResponse)
async def query_rag_filtered(request: FilteredQueryRequest):
    """Query the RAG system with specific filter criteria."""
    try:
        rag_service = get_rag_service()
        
        # Create query context
        context = QueryContext(
            user_crops=request.user_crops,
            current_season=request.current_season,
            user_region=request.user_region,
            language=request.language
        )
        
        # Process filtered query
        result = await rag_service.query_with_filter(
            request.query, 
            request.filter_criteria, 
            context
        )
        
        # Convert to standard response format
        response = {
            "query": result["query"],
            "context": result["context"],
            "retrieved_chunks": result["filtered_chunks"],
            "chunks": result["chunks"],
            "summary": result["summary"],
            "suggested_actions": result.get("suggested_actions", [])
        }
        
        return QueryResponse(**response)
        
    except Exception as e:
        logger.error(f"Failed to process filtered RAG query: {e}")
        raise HTTPException(status_code=500, detail=f"Filtered query processing failed: {str(e)}")


@router.post("/documents/process", response_model=DocumentProcessResponse)
async def process_document(
    file: UploadFile = File(...),
    document_type: Optional[str] = Form(None)
):
    """Process a PDF document and add it to the RAG system."""
    try:
        doc_processor = get_doc_processor()
        
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Save uploaded file temporarily
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        try:
            # Process document
            chunks = await doc_processor.process_document(temp_path, document_type)
            
            # Get document info
            doc_info = doc_processor.get_pdf_info(temp_path)
            
            return DocumentProcessResponse(
                success=True,
                message=f"Document processed successfully. Created {len(chunks)} chunks.",
                chunks_created=len(chunks),
                document_info=doc_info
            )
            
        finally:
            # Clean up temporary file
            Path(temp_path).unlink(missing_ok=True)
        
    except Exception as e:
        logger.error(f"Failed to process document: {e}")
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")


@router.post("/documents/process/batch")
async def process_documents_batch(
    files: List[UploadFile] = File(...),
    document_types: Optional[List[str]] = Form(None)
):
    """Process multiple PDF documents in batch."""
    try:
        doc_processor = get_doc_processor()
        
        # Validate files
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF")
        
        # Prepare file paths and types
        file_paths = []
        temp_paths = []
        
        try:
            for i, file in enumerate(files):
                # Save uploaded file temporarily
                temp_path = f"/tmp/{file.filename}"
                with open(temp_path, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)
                
                file_paths.append(temp_path)
                temp_paths.append(temp_path)
            
            # Process documents
            results = await doc_processor.process_documents_batch(
                file_paths, 
                document_types
            )
            
            # Prepare response
            response = {
                "total_files": len(files),
                "successful_files": sum(1 for chunks in results.values() if chunks),
                "failed_files": sum(1 for chunks in results.values() if not chunks),
                "total_chunks_created": sum(len(chunks) for chunks in results.values()),
                "file_results": [
                    {
                        "filename": Path(path).name,
                        "chunks_created": len(chunks),
                        "success": bool(chunks)
                    }
                    for path, chunks in results.items()
                ]
            }
            
            return response
            
        finally:
            # Clean up temporary files
            for temp_path in temp_paths:
                Path(temp_path).unlink(missing_ok=True)
        
    except Exception as e:
        logger.error(f"Failed to process documents batch: {e}")
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")


@router.get("/stats")
async def get_rag_stats():
    """Get RAG system statistics."""
    try:
        rag_service = get_rag_service()
        doc_processor = get_doc_processor()
        
        stats = {
            "rag_service": rag_service.get_service_stats(),
            "document_processor": doc_processor.get_processing_stats()
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get RAG stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.post("/reset")
async def reset_rag_system():
    """Reset the RAG system (clear all stored chunks)."""
    try:
        rag_service = get_rag_service()
        rag_service.reset_service()
        
        return {"message": "RAG system reset successfully"}
        
    except Exception as e:
        logger.error(f"Failed to reset RAG system: {e}")
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for RAG system."""
    try:
        rag_service = get_rag_service()
        doc_processor = get_doc_processor()
        
        # Check if services are initialized
        rag_ok = rag_service is not None
        doc_ok = doc_processor is not None
        
        return {
            "status": "healthy" if rag_ok and doc_ok else "unhealthy",
            "rag_service": "ok" if rag_ok else "error",
            "document_processor": "ok" if doc_ok else "error",
            "timestamp": "2024-01-01T00:00:00Z"  # In production, use actual timestamp
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }
