"""
RAG (Retrieval-Augmented Generation) API endpoints
Provides knowledge base ingestion and Q&A capabilities
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import os
import tempfile
import logging
from datetime import datetime

from api.db import get_db
from api.services.rag_service import rag_service
from api.dependencies import get_current_user
from api.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["RAG - Knowledge Base"])

@router.post("/ingest/document", response_model=Dict[str, Any])
async def ingest_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form("general"),
    tags: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ingest a document into the knowledge base"""
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.docx', '.txt']
        file_extension = os.path.splitext(file.filename)[1].lower()

        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )

        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Prepare metadata
            metadata = {
                "document_id": f"doc_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{current_user.id}",
                "title": title,
                "category": category,
                "type": file_extension[1:],  # Remove the dot
                "author": current_user.name,
                "author_id": current_user.id,
                "organization_id": current_user.organization_id,
                "tags": tags.split(',') if tags else [],
                "description": description,
                "file_name": file.filename,
                "uploaded_at": datetime.utcnow().isoformat()
            }

            # Ingest document
            result = await rag_service.ingest_document(temp_file_path, metadata, db)

            if result["status"] == "success":
                return {
                    "message": "Document ingested successfully",
                    "document_id": metadata["document_id"],
                    "chunks_processed": result["chunks_processed"],
                    "embeddings_stored": result["embeddings_stored"],
                    "metadata": metadata
                }
            else:
                raise HTTPException(status_code=500, detail=result["message"])

        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ingesting document: {e}")
        raise HTTPException(status_code=500, detail="Failed to ingest document")

@router.post("/ingest/text", response_model=Dict[str, Any])
async def ingest_text(
    title: str,
    content: str,
    category: str = "general",
    tags: Optional[str] = None,
    description: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ingest text content directly into the knowledge base"""
    try:
        # Create temporary text file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Prepare metadata
            metadata = {
                "document_id": f"text_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{current_user.id}",
                "title": title,
                "category": category,
                "type": "text",
                "author": current_user.name,
                "author_id": current_user.id,
                "organization_id": current_user.organization_id,
                "tags": tags.split(',') if tags else [],
                "description": description,
                "uploaded_at": datetime.utcnow().isoformat()
            }

            # Ingest text content
            result = await rag_service.ingest_document(temp_file_path, metadata, db)

            if result["status"] == "success":
                return {
                    "message": "Text content ingested successfully",
                    "document_id": metadata["document_id"],
                    "chunks_processed": result["chunks_processed"],
                    "embeddings_stored": result["embeddings_stored"],
                    "metadata": metadata
                }
            else:
                raise HTTPException(status_code=500, detail=result["message"])

        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except Exception as e:
        logger.error(f"Error ingesting text: {e}")
        raise HTTPException(status_code=500, detail="Failed to ingest text content")

@router.post("/qa", response_model=Dict[str, Any])
async def ask_question(
    question: str,
    category: Optional[str] = None,
    customer_context: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ask a question to the knowledge base"""
    try:
        # Prepare search filters
        filters = {"organization_id": current_user.organization_id}
        if category:
            filters["category"] = category

        # Search for relevant information
        relevant_chunks = await rag_service.search_knowledge(
            query=question,
            top_k=5,
            filters=filters
        )

        if not relevant_chunks:
            return {
                "answer": "I don't have sufficient information in our knowledge base to answer this question. Please try rephrasing or contact our support team.",
                "citations": [],
                "sources_used": 0,
                "confidence_score": 0.0,
                "question": question
            }

        # Generate answer using RAG
        result = await rag_service.generate_answer(
            query=question,
            context_chunks=relevant_chunks,
            customer_context=customer_context
        )

        return result

    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail="Failed to process question")

@router.get("/search", response_model=List[Dict[str, Any]])
async def search_knowledge(
    q: str = Query(..., description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search the knowledge base without generating an answer"""
    try:
        # Prepare search filters
        filters = {"organization_id": current_user.organization_id}
        if category:
            filters["category"] = category

        # Search for relevant information
        results = await rag_service.search_knowledge(
            query=q,
            top_k=limit,
            filters=filters
        )

        # Format results for API response
        formatted_results = []
        for result in results:
            formatted_results.append({
                "chunk_id": result.chunk_id,
                "score": result.score,
                "text": result.text,
                "metadata": result.metadata
            })

        return formatted_results

    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}")
        raise HTTPException(status_code=500, detail="Failed to search knowledge base")

@router.get("/stats", response_model=Dict[str, Any])
async def get_knowledge_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get statistics about the knowledge base"""
    try:
        # This would typically query the vector database for stats
        # For now, return basic info
        return {
            "organization_id": current_user.organization_id,
            "index_name": rag_service.index_name,
            "dimension": rag_service.dimension,
            "chunk_size": rag_service.chunk_size,
            "chunk_overlap": rag_service.chunk_overlap,
            "supported_formats": [".pdf", ".docx", ".txt"],
            "status": "active"
        }

    except Exception as e:
        logger.error(f"Error getting knowledge stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get knowledge base statistics")

@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a document and its chunks from the knowledge base"""
    try:
        # This would require implementing delete functionality in the vector database
        # For now, return not implemented
        raise HTTPException(
            status_code=501,
            detail="Document deletion not yet implemented. Please contact support."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete document")

# Health check endpoint
@router.get("/health")
async def rag_health_check():
    """Check if RAG service is healthy"""
    try:
        # Test Pinecone connection
        indexes = rag_service.pinecone.list_indexes()
        return {
            "status": "healthy",
            "service": "RAG",
            "vector_db": "connected",
            "indexes": len(indexes.names()) if hasattr(indexes, 'names') else 0,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"RAG health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "RAG",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }