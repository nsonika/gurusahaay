"""
Suggestions routes - retrieve content based on concept_id.

CRITICAL: This endpoint ONLY accepts concept_id.
It does NOT accept raw text queries.
All text resolution happens in /help/request first.

Flow:
1. Resolve concept_id
2. Search internal verified content
3. IF found → return
4. ELSE → search external (DuckDuckGo) → summarize with Gemini → store → return
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.teacher import Teacher
from app.schemas.content import SuggestionResponse, ContentResponse
from app.routes.auth import get_current_teacher
from app.services.content_service import ContentService
from app.services.concept_resolver import ConceptResolver

router = APIRouter(prefix="/suggestions", tags=["Suggestions"])


@router.get("", response_model=SuggestionResponse)
def get_suggestions(
    concept_id: str = Query(..., description="The resolved concept ID"),
    language: Optional[str] = Query(None, description="Language override"),
    problem_description: Optional[str] = Query(None, description="Detailed problem context from teacher"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher)
):
    """
    Get content suggestions for a concept.
    
    CRITICAL: This endpoint searches by concept_id ONLY.
    - NEVER pass raw Kannada/Hindi text here
    - Always resolve text to concept_id first via /help/request
    
    Priority order:
    1. Verified internal content in teacher's language
    2. Verified internal content in other languages
    3. Unverified external content (with warning label)
    
    Returns suggestions with source indicator:
    - "internal": Verified teacher content
    - "external_fallback": Unverified external content
    """
    # Verify concept exists
    concept = ConceptResolver.get_concept_by_id(db, concept_id)
    if not concept:
        raise HTTPException(
            status_code=404,
            detail=f"Concept '{concept_id}' not found"
        )
    
    # Use provided language or fall back to teacher's preference
    target_lang = language or current_teacher.language_preference

    # Get suggestions - first try with scores, then fallback to raw suggestions
    results = ContentService.get_content_with_scores(
        db,
        concept_id,
        target_lang,
        limit,
        problem_description
    )
    
    # Build response
    suggestions = []
    source = "internal"
    
    if results:
        for item in results:
            content = item["content"]
            suggestions.append(ContentResponse(
                id=content.id,
                concept_id=content.concept_id,
                title=content.title,
                content_url=content.content_url or content.file_url,
                description=content.description,
                content_type=content.content_type,
                language=content.language,
                subject=content.subject,
                grade=content.grade,
                source_type=content.source_type,
                is_verified=content.is_verified,
                created_at=content.created_at,
                uploader_name=item["uploader_name"],
                ai_summary=content.ai_summary
            ))
            source = item["source"]
    else:
        # No results from get_content_with_scores, try get_suggestions directly
        # This handles the case where Google Search returns results
        content_list, source = ContentService.get_suggestions(
            db,
            concept_id,
            target_lang,
            limit
        )
        for content in content_list:
            suggestions.append(ContentResponse(
                id=content.id,
                concept_id=content.concept_id,
                title=content.title,
                content_url=content.content_url or content.file_url,
                description=content.description,
                content_type=content.content_type,
                language=content.language,
                subject=content.subject,
                grade=content.grade,
                source_type=content.source_type,
                is_verified=content.is_verified,
                created_at=content.created_at,
                uploader_name="Google Search",
                ai_summary=content.ai_summary
            ))
    
    # Add warning message for unverified content
    message = None
    if source == "google_search":
        message = "Found via Google Search – External resources"
    elif source == "external_fallback":
        message = "Suggested – Not yet verified by mentors"
    elif source == "internal_unverified":
        message = "Found limited suggestions"
    elif not suggestions:
        message = "No content found for this topic. Consider uploading your own!"
    
    return SuggestionResponse(
        concept_id=concept_id,
        suggestions=suggestions,
        source=source,
        message=message
    )
