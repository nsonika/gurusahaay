"""
Community feed routes.
"""
from typing import List, Union
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.teacher import Teacher
from app.models.help_request import HelpRequest
from app.schemas.content import ContentResponse
from app.routes.auth import get_current_teacher
from app.services.content_service import ContentService

router = APIRouter(prefix="/community", tags=["Community"])


@router.get("/feed")
def get_community_feed(
    tab: str = Query("all", description="Filter: all, help_needed, uploads"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher)
):
    """
    Get community feed content.
    
    Tabs:
    - all: All recent content (uploads)
    - help_needed: Help requests from teachers needing assistance
    - uploads: Recent teacher uploads
    """
    # For help_needed tab, return HelpRequests
    if tab == "help_needed":
        help_requests = db.query(HelpRequest).order_by(
            desc(HelpRequest.created_at)
        ).offset(offset).limit(limit).all()
        
        # Get teacher names for each request
        results = []
        for hr in help_requests:
            teacher = db.query(Teacher).filter(Teacher.id == hr.teacher_id).first()
            results.append({
                "id": str(hr.id),
                "concept_id": hr.concept_id,
                "title": hr.original_query_text,
                "content_url": None,
                "description": hr.normalized_text,
                "content_type": "help_request",
                "language": hr.detected_language or "en",
                "subject": hr.subject,
                "grade": hr.grade,
                "source_type": "help_request",
                "is_verified": False,
                "created_at": hr.created_at.isoformat(),
                "uploader_name": teacher.name if teacher else "Teacher"
            })
        return results
    
    # For all/uploads tabs, return uploaded content
    content_list = ContentService.get_community_feed(db, tab, limit, offset)
    
    results = []
    for c in content_list:
        teacher = db.query(Teacher).filter(Teacher.id == c.uploaded_by).first()
        results.append({
            "id": str(c.id),
            "concept_id": c.concept_id,
            "title": c.title,
            "content_url": c.content_url,
            "description": c.description,
            "content_type": c.content_type,
            "language": c.language,
            "subject": c.subject,
            "grade": c.grade,
            "source_type": c.source_type,
            "is_verified": c.is_verified,
            "created_at": c.created_at.isoformat(),
            "uploader_name": teacher.name if teacher else "Teacher"
        })
    return results
