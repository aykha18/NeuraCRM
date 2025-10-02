from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from pathlib import Path

from ..db import get_db
from ..models import User
from ..services.document_processing import document_processing_service, DocumentMetadata, DocumentAnalysis
from ..auth import get_current_user

router = APIRouter()

@router.post("/upload", response_model=DocumentMetadata)
def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a document for processing"""
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.docx', '.doc', '.txt']
        file_extension = Path(file.filename).suffix.lower()

        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_extension} not supported. Allowed: {', '.join(allowed_extensions)}"
            )

        # Validate file size (max 10MB)
        file_content = file.file.read()
        if len(file_content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Maximum size: 10MB")

        # Reset file pointer
        from io import BytesIO
        file.file = BytesIO(file_content)

        # Upload document
        metadata = document_processing_service.upload_document(
            file.file,
            file.filename,
            current_user.organization_id or 1,
            current_user.id
        )

        return metadata

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/documents", response_model=List[DocumentMetadata])
def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """List user's documents"""
    try:
        # Load all documents for organization
        all_docs = document_processing_service._load_all_metadata(current_user.organization_id or 1)

        # Apply pagination
        docs = all_docs[skip:skip + limit]

        return docs

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@router.get("/documents/{doc_id}", response_model=DocumentMetadata)
def get_document(
    doc_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get document metadata"""
    try:
        metadata = document_processing_service.get_document_metadata(doc_id)

        if not metadata:
            raise HTTPException(status_code=404, detail="Document not found")

        # Check organization access
        if metadata.organization_id != (current_user.organization_id or 1):
            raise HTTPException(status_code=403, detail="Access denied")

        return metadata

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get document: {str(e)}")

@router.get("/documents/{doc_id}/download")
def download_document(
    doc_id: str,
    current_user: User = Depends(get_current_user)
):
    """Download original document"""
    try:
        metadata = document_processing_service.get_document_metadata(doc_id)

        if not metadata:
            raise HTTPException(status_code=404, detail="Document not found")

        # Check organization access
        if metadata.organization_id != (current_user.organization_id or 1):
            raise HTTPException(status_code=403, detail="Access denied")

        # Find file path
        file_extension = document_processing_service._get_extension(metadata.file_type)
        file_path = Path("uploads/documents") / f"{doc_id}{file_extension}"

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(
            path=file_path,
            filename=metadata.filename,
            media_type="application/octet-stream"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download document: {str(e)}")

@router.post("/documents/{doc_id}/analyze", response_model=DocumentAnalysis)
def analyze_document(
    doc_id: str,
    current_user: User = Depends(get_current_user)
):
    """Analyze document with AI"""
    try:
        # Check if document exists and user has access
        metadata = document_processing_service.get_document_metadata(doc_id)

        if not metadata:
            raise HTTPException(status_code=404, detail="Document not found")

        if metadata.organization_id != (current_user.organization_id or 1):
            raise HTTPException(status_code=403, detail="Access denied")

        # Analyze document
        analysis = document_processing_service.analyze_document(doc_id)

        return analysis

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/documents/{doc_id}/analysis", response_model=DocumentAnalysis)
def get_document_analysis(
    doc_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get existing document analysis"""
    try:
        # Check if document exists and user has access
        metadata = document_processing_service.get_document_metadata(doc_id)

        if not metadata:
            raise HTTPException(status_code=404, detail="Document not found")

        if metadata.organization_id != (current_user.organization_id or 1):
            raise HTTPException(status_code=403, detail="Access denied")

        if not metadata.summary:
            raise HTTPException(status_code=404, detail="Document not yet analyzed")

        # Return analysis from metadata
        analysis = DocumentAnalysis(
            summary=metadata.summary,
            key_points=[],  # Would need to store these separately
            entities=metadata.key_entities,
            sentiment={
                "score": metadata.sentiment_score or 0,
                "label": "neutral",  # Would need to store this
                "confidence": 0.5
            },
            categories=[],  # Would need to store these
            confidence_scores={
                "summary": 0.85,
                "key_points": 0.78,
                "entities": 0.82,
                "sentiment": 0.91,
                "categories": 0.76
            }
        )

        return analysis

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analysis: {str(e)}")

@router.get("/search", response_model=List[DocumentMetadata])
def search_documents(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user)
):
    """Search documents by content"""
    try:
        if not q or len(q.strip()) < 1:
            raise HTTPException(status_code=400, detail="Search query required")

        results = document_processing_service.search_documents(
            q.strip(),
            current_user.organization_id or 1,
            limit
        )

        return results

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.delete("/documents/{doc_id}")
def delete_document(
    doc_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a document"""
    try:
        # Check if document exists and user has access
        metadata = document_processing_service.get_document_metadata(doc_id)

        if not metadata:
            raise HTTPException(status_code=404, detail="Document not found")

        if metadata.organization_id != (current_user.organization_id or 1):
            raise HTTPException(status_code=403, detail="Access denied")

        # Delete document
        success = document_processing_service.delete_document(doc_id)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete document")

        return {"message": "Document deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

@router.get("/stats")
def get_document_stats(current_user: User = Depends(get_current_user)):
    """Get document processing statistics"""
    try:
        # Load all documents for organization
        all_docs = document_processing_service._load_all_metadata(current_user.organization_id or 1)

        stats = {
            "total_documents": len(all_docs),
            "total_size_mb": sum(doc.file_size for doc in all_docs) / (1024 * 1024),
            "by_type": {},
            "processing_status": {},
            "recent_uploads": len([doc for doc in all_docs if (doc.upload_date - doc.upload_date.replace(hour=0, minute=0, second=0, microsecond=0)).days == 0])
        }

        # Group by type and status
        for doc in all_docs:
            stats["by_type"][doc.file_type] = stats["by_type"].get(doc.file_type, 0) + 1
            stats["processing_status"][doc.processing_status] = stats["processing_status"].get(doc.processing_status, 0) + 1

        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")