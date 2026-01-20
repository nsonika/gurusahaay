"""
Content Service - Handles content retrieval and ranking.

Implements the MANDATORY content resolution strategy:
1. Search internal verified content FIRST
2. Only fall back to external sources if nothing found
3. Use Google Web Search via Gemini as last resort
4. Rank by language preference, feedback score, recency
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, case
from uuid import UUID
import uuid

from app.models.content import UploadedContent, ContentFeedback, ContentInteraction
from app.models.teacher import Teacher
from app.services.gemini_service import GeminiService


class ContentService:
    """
    Handles content retrieval with proper prioritization.
    
    CRITICAL: Always search by concept_id, NEVER by raw text.
    """
    
    @staticmethod
    def get_suggestions(
        db: Session,
        concept_id: str,
        teacher_language: str = "en",
        limit: int = 10
    ) -> Tuple[List[UploadedContent], str]:
        """
        Get content suggestions for a concept.
        
        Priority order:
        1. Verified internal content in teacher's language
        2. Verified internal content in other languages
        3. Unverified external content (fallback)
        
        Args:
            db: Database session
            concept_id: The resolved concept ID
            teacher_language: Teacher's preferred language
            limit: Maximum number of results
            
        Returns:
            Tuple of (content_list, source_type)
            source_type is "internal" or "external_fallback"
        """
        # Step 1: Try verified internal content first
        verified_content = db.query(UploadedContent).filter(
            UploadedContent.concept_id == concept_id,
            UploadedContent.is_verified == True,
            UploadedContent.source_type == "internal"
        ).order_by(
            # Prioritize teacher's language
            case(
                (UploadedContent.language == teacher_language, 0),
                else_=1
            ),
            desc(UploadedContent.created_at)
        ).limit(limit).all()
        
        if verified_content:
            return (verified_content, "internal")
        
        # Step 2: Try any verified content (including external that's been verified)
        any_verified = db.query(UploadedContent).filter(
            UploadedContent.concept_id == concept_id,
            UploadedContent.is_verified == True
        ).order_by(
            case(
                (UploadedContent.language == teacher_language, 0),
                else_=1
            ),
            desc(UploadedContent.created_at)
        ).limit(limit).all()
        
        if any_verified:
            return (any_verified, "internal")
        
        # Step 3: Fall back to unverified content (external)
        unverified = db.query(UploadedContent).filter(
            UploadedContent.concept_id == concept_id
        ).order_by(
            case(
                (UploadedContent.language == teacher_language, 0),
                else_=1
            ),
            desc(UploadedContent.created_at)
        ).limit(limit).all()
        
        if unverified:
            return (unverified, "external_fallback")
        
        # Step 4: Use Google Web Search via Gemini to find external content
        print(f"[ContentService] No content found for '{concept_id}', trying Google Web Search...")
        search_results = GeminiService.google_web_search(concept_id.replace("_", " "), num_results=5)
        
        if search_results:
            # Create temporary content entries from search results
            web_content = []
            for result in search_results:
                # Determine content type from URL
                url = result.get("url", "")
                content_type = "article"
                if "youtube.com" in url or "youtu.be" in url:
                    content_type = "video"
                elif url.endswith(".pdf"):
                    content_type = "document"
                
                # Create a temporary UploadedContent object (not saved to DB)
                temp_content = UploadedContent(
                    id=uuid.uuid4(),
                    title=result.get("title", "External Resource"),
                    description=result.get("snippet", "Found via Google Search"),
                    content_type=content_type,
                    file_url=url,
                    concept_id=concept_id,
                    language="en",
                    source_type="external",
                    is_verified=False
                )
                web_content.append(temp_content)
            
            print(f"[ContentService] Found {len(web_content)} results from Google Web Search")
            return (web_content, "google_search")
        
        # No content found at all
        return ([], "internal")
    
    @staticmethod
    def get_content_with_scores(
        db: Session,
        concept_id: str,
        teacher_language: str = "en",
        limit: int = 10
    ) -> List[dict]:
        """
        Get content with computed feedback scores.
        Returns dictionaries with content and score.
        """
        content_list, source = ContentService.get_suggestions(
            db, concept_id, teacher_language, limit
        )
        
        # For Google Search results, return directly without DB queries
        if source == "google_search":
            results = []
            for content in content_list:
                results.append({
                    "content": content,
                    "feedback_score": 0,
                    "success_rate": 0,
                    "uploader_name": "Google Search",
                    "source": source
                })
            return results
        
        results = []
        for content in content_list:
            # Calculate average rating
            avg_rating = db.query(func.avg(ContentFeedback.rating)).filter(
                ContentFeedback.content_id == content.id
            ).scalar() or 0
            
            # Calculate success rate (worked = True)
            total_feedback = db.query(ContentFeedback).filter(
                ContentFeedback.content_id == content.id
            ).count()
            
            worked_count = db.query(ContentFeedback).filter(
                ContentFeedback.content_id == content.id,
                ContentFeedback.worked == True
            ).count()
            
            success_rate = (worked_count / total_feedback * 100) if total_feedback > 0 else 0
            
            # Get uploader name
            uploader = db.query(Teacher).filter(Teacher.id == content.uploaded_by).first()
            uploader_name = uploader.name if uploader else "Unknown"
            
            results.append({
                "content": content,
                "feedback_score": round(avg_rating, 1),
                "success_rate": round(success_rate, 1),
                "uploader_name": uploader_name,
                "source": source
            })
        
        # Sort by feedback score (descending)
        results.sort(key=lambda x: x["feedback_score"], reverse=True)
        return results
    
    @staticmethod
    def upload_content(
        db: Session,
        teacher_id: UUID,
        concept_id: str,
        title: str,
        content_url: Optional[str],
        description: Optional[str],
        content_type: str,
        language: str,
        subject: Optional[str] = None,
        grade: Optional[str] = None
    ) -> UploadedContent:
        """
        Upload new content from a teacher.
        Internal content starts as unverified but can be promoted.
        """
        content = UploadedContent(
            uploaded_by=teacher_id,
            concept_id=concept_id,
            title=title,
            content_url=content_url,
            description=description,
            content_type=content_type,
            language=language,
            subject=subject,
            grade=grade,
            source_type="internal",
            is_verified=False  # Requires verification
        )
        db.add(content)
        db.commit()
        db.refresh(content)
        return content
    
    @staticmethod
    def add_feedback(
        db: Session,
        content_id: UUID,
        teacher_id: UUID,
        worked: bool,
        rating: int,
        comment: Optional[str] = None
    ) -> ContentFeedback:
        """Add feedback for a piece of content."""
        feedback = ContentFeedback(
            content_id=content_id,
            teacher_id=teacher_id,
            worked=worked,
            rating=rating,
            comment=comment
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback
    
    @staticmethod
    def record_interaction(
        db: Session,
        content_id: UUID,
        teacher_id: UUID,
        interaction_type: str
    ) -> ContentInteraction:
        """Record a content interaction (view, click, share, save)."""
        interaction = ContentInteraction(
            content_id=content_id,
            teacher_id=teacher_id,
            interaction_type=interaction_type
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        return interaction
    
    @staticmethod
    def get_community_feed(
        db: Session,
        tab: str = "all",
        limit: int = 20,
        offset: int = 0
    ) -> List[UploadedContent]:
        """
        Get community feed content.
        
        Tabs:
        - all: All recent content (uploads only)
        - help_needed: Returns empty - help requests handled separately
        - uploads: Recent uploads
        """
        # help_needed tab is handled by get_help_requests method
        if tab == "help_needed":
            return []
        
        query = db.query(UploadedContent).filter(
            UploadedContent.source_type == "internal"
        )
        
        return query.order_by(
            desc(UploadedContent.created_at)
        ).offset(offset).limit(limit).all()
