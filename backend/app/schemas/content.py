"""
Content schemas.
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class ContentUploadRequest(BaseModel):
    concept_id: str
    title: str
    content_url: Optional[str] = None
    description: Optional[str] = None
    content_type: str = "tip"  # video, document, activity, tip
    language: str = "en"
    subject: Optional[str] = None
    grade: Optional[str] = None


class ContentResponse(BaseModel):
    id: UUID
    concept_id: str
    title: str
    content_url: Optional[str]
    description: Optional[str]
    content_type: Optional[str]
    language: str
    subject: Optional[str]
    grade: Optional[str]
    source_type: str
    is_verified: bool
    created_at: datetime
    
    # Computed fields for display
    feedback_score: Optional[float] = None
    uploader_name: Optional[str] = None
    ai_summary: Optional[str] = None
    likes_count: int = 0
    views_count: int = 0
    user_liked: bool = False

    class Config:
        from_attributes = True


class ContentFeedbackRequest(BaseModel):
    worked: bool
    rating: int  # 1-5
    comment: Optional[str] = None


class SuggestionResponse(BaseModel):
    """
    Response for suggestions endpoint.
    Contains prioritized content based on concept_id.
    """
    concept_id: str
    suggestions: List[ContentResponse]
    source: str  # "internal" or "external_fallback"
    message: Optional[str] = None  # e.g., "Suggested – Not yet verified"
