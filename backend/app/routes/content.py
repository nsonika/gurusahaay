"""
Content routes - upload and feedback.
"""
import tempfile
import os
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.teacher import Teacher
from app.models.content import UploadedContent, ContentInteraction
from app.models.help_request import HelpRequest
from app.schemas.content import ContentUploadRequest, ContentResponse, ContentFeedbackRequest
from app.routes.auth import get_current_teacher
from sqlalchemy import func
from app.services.content_service import ContentService
from app.services.points_service import PointsService
from app.services.concept_resolver import ConceptResolver
from app.services.cloudinary_service import CloudinaryService
from app.routes.notifications import create_notification

router = APIRouter(prefix="/content", tags=["Content"])


@router.get("/cloudinary-status")
def check_cloudinary_status():
    """Check if Cloudinary is configured and available."""
    return {
        "configured": CloudinaryService.is_configured(),
        "message": "Cloudinary is ready" if CloudinaryService.is_configured() else "Cloudinary not configured"
    }


@router.get("/{content_id}", response_model=ContentResponse)
def get_content_by_id(
    content_id: str,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher)
):
    """
    Get content details by ID.
    """
    content = db.query(UploadedContent).filter(UploadedContent.id == content_id).first()
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Get uploader name
    uploader = db.query(Teacher).filter(Teacher.id == content.uploaded_by).first()
    
    # Get likes count
    likes_count = db.query(func.count(ContentInteraction.id)).filter(
        ContentInteraction.content_id == content.id,
        ContentInteraction.interaction_type == "like"
    ).scalar() or 0
    
    # Get views count
    views_count = db.query(func.count(ContentInteraction.id)).filter(
        ContentInteraction.content_id == content.id,
        ContentInteraction.interaction_type == "view"
    ).scalar() or 0
    
    # Check if current user has liked
    user_liked = db.query(ContentInteraction).filter(
        ContentInteraction.content_id == content.id,
        ContentInteraction.teacher_id == current_teacher.id,
        ContentInteraction.interaction_type == "like"
    ).first() is not None
    
    return ContentResponse(
        id=content.id,
        concept_id=content.concept_id,
        title=content.title,
        content_url=content.content_url,
        description=content.description,
        content_type=content.content_type,
        language=content.language,
        subject=content.subject,
        grade=content.grade,
        source_type=content.source_type,
        is_verified=content.is_verified,
        created_at=content.created_at,
        uploader_name=uploader.name if uploader else "Teacher",
        likes_count=likes_count,
        views_count=views_count,
        user_liked=user_liked
    )


@router.post("/{content_id}/view")
def record_view(
    content_id: str,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher)
):
    """Record a view for content."""
    content = db.query(UploadedContent).filter(UploadedContent.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Check if already viewed recently (prevent spam)
    existing = db.query(ContentInteraction).filter(
        ContentInteraction.content_id == content.id,
        ContentInteraction.teacher_id == current_teacher.id,
        ContentInteraction.interaction_type == "view"
    ).first()
    
    if not existing:
        interaction = ContentInteraction(
            content_id=content.id,
            teacher_id=current_teacher.id,
            interaction_type="view"
        )
        db.add(interaction)
        db.commit()
    
    return {"message": "View recorded"}


@router.post("/{content_id}/like")
def toggle_like(
    content_id: str,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher)
):
    """Toggle like for content."""
    content = db.query(UploadedContent).filter(UploadedContent.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Check if already liked
    existing = db.query(ContentInteraction).filter(
        ContentInteraction.content_id == content.id,
        ContentInteraction.teacher_id == current_teacher.id,
        ContentInteraction.interaction_type == "like"
    ).first()
    
    if existing:
        # Unlike
        db.delete(existing)
        db.commit()
        liked = False
    else:
        # Like
        interaction = ContentInteraction(
            content_id=content.id,
            teacher_id=current_teacher.id,
            interaction_type="like"
        )
        db.add(interaction)
        db.commit()
        liked = True
    
    # Get updated count
    likes_count = db.query(func.count(ContentInteraction.id)).filter(
        ContentInteraction.content_id == content.id,
        ContentInteraction.interaction_type == "like"
    ).scalar() or 0
    
    return {"liked": liked, "likes_count": likes_count}


@router.post("/upload", response_model=ContentResponse)
def upload_content(
    request: ContentUploadRequest,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher)
):
    """
    Upload new teaching content.
    
    Content is linked to a concept_id for proper categorization.
    Starts as unverified and can be promoted by mentors.
    
    Awards points to the uploader.
    """
    # Verify concept exists
    concept = ConceptResolver.get_concept_by_id(db, request.concept_id)
    if not concept:
        raise HTTPException(
            status_code=400,
            detail=f"Concept '{request.concept_id}' not found"
        )
    
    # Create content
    content = ContentService.upload_content(
        db=db,
        teacher_id=current_teacher.id,
        concept_id=request.concept_id,
        title=request.title,
        content_url=request.content_url,
        description=request.description,
        content_type=request.content_type,
        language=request.language,
        subject=request.subject or concept.subject,
        grade=request.grade or concept.grade
    )
    
    # Award points for upload
    PointsService.award_upload_points(db, current_teacher.id)
    
    # Notify teacher about points earned
    create_notification(
        db=db,
        teacher_id=current_teacher.id,
        notification_type="points_earned",
        title="Points Earned!",
        message=f"You earned 10 points for uploading '{request.title}'",
        reference_id=str(content.id),
        reference_type="content"
    )
    
    # Notify teachers who asked for help on this concept
    help_requests = db.query(HelpRequest).filter(
        HelpRequest.concept_id == request.concept_id,
        HelpRequest.teacher_id != current_teacher.id
    ).all()
    
    for hr in help_requests:
        create_notification(
            db=db,
            teacher_id=hr.teacher_id,
            notification_type="content_upload",
            title="Help Content Available!",
            message=f"{current_teacher.name} uploaded content for a topic you asked help for: '{concept.description_en or request.concept_id}'",
            reference_id=str(content.id),
            reference_type="content"
        )
    
    return ContentResponse(
        id=content.id,
        concept_id=content.concept_id,
        title=content.title,
        content_url=content.content_url,
        description=content.description,
        content_type=content.content_type,
        language=content.language,
        subject=content.subject,
        grade=content.grade,
        source_type=content.source_type,
        is_verified=content.is_verified,
        created_at=content.created_at,
        uploader_name=current_teacher.name
    )


@router.post("/{content_id}/feedback")
def add_feedback(
    content_id: UUID,
    request: ContentFeedbackRequest,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher)
):
    """
    Add feedback for a piece of content.
    
    Feedback is used for:
    - Ranking content in suggestions
    - Quality control
    - Rewarding helpful content creators
    """
    # Verify content exists
    content = db.query(UploadedContent).filter(UploadedContent.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Add feedback
    feedback = ContentService.add_feedback(
        db=db,
        content_id=content_id,
        teacher_id=current_teacher.id,
        worked=request.worked,
        rating=request.rating,
        comment=request.comment
    )
    
    # Award points to feedback giver
    PointsService.award_feedback_points(db, current_teacher.id)
    
    # If content helped, award points to content creator
    if request.worked and content.uploaded_by:
        PointsService.award_helped_points(db, content.uploaded_by)
    
    return {"message": "Feedback recorded", "feedback_id": str(feedback.id)}


@router.post("/{content_id}/view")
def record_view(
    content_id: UUID,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher)
):
    """Record that a teacher viewed content."""
    content = db.query(UploadedContent).filter(UploadedContent.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    ContentService.record_interaction(db, content_id, current_teacher.id, "view")
    return {"message": "View recorded"}


@router.post("/upload-file")
async def upload_file_to_cloudinary(
    file: UploadFile = File(...),
    title: str = Form(...),
    concept_id: str = Form(...),
    content_type: str = Form(...),  # 'video' or 'document'
    description: str = Form(""),
    language: str = Form("en"),
    help_request_id: str = Form(None),  # Optional: ID of help request being responded to
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher)
):
    """
    Upload a video or document file to Cloudinary.
    
    The file is uploaded to Cloudinary and the URL is stored in the database.
    """
    # Check if Cloudinary is configured
    if not CloudinaryService.is_configured():
        raise HTTPException(
            status_code=503,
            detail="File upload service not configured. Please set Cloudinary credentials."
        )
    
    # Verify concept exists
    concept = ConceptResolver.get_concept_by_id(db, concept_id)
    if not concept:
        raise HTTPException(
            status_code=400,
            detail=f"Concept '{concept_id}' not found"
        )
    
    # Validate file type
    allowed_video_types = ["video/mp4", "video/webm", "video/quicktime", "video/x-msvideo"]
    allowed_doc_types = ["application/pdf", "application/msword", 
                         "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    
    if content_type == "video" and file.content_type not in allowed_video_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid video type. Allowed: mp4, webm, mov, avi"
        )
    
    if content_type == "document" and file.content_type not in allowed_doc_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid document type. Allowed: pdf, doc, docx"
        )
    
    # Save file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename or "")[1]) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        # Upload to Cloudinary
        upload_result = CloudinaryService.upload_file(
            file_path=tmp_path,
            file_type=content_type,
            public_id=f"{current_teacher.id}_{title[:30].replace(' ', '_')}"
        )
        
        # Create content record in database
        db_content = ContentService.upload_content(
            db=db,
            teacher_id=current_teacher.id,
            concept_id=concept_id,
            title=title,
            content_url=upload_result["url"],
            description=description,
            content_type=content_type,
            language=language,
            subject=concept.subject,
            grade=concept.grade
        )
        
        # Award points for upload
        PointsService.award_upload_points(db, current_teacher.id)
        
        # Notify teacher about points earned
        create_notification(
            db=db,
            teacher_id=current_teacher.id,
            notification_type="points_earned",
            title="Points Earned!",
            message=f"You earned 10 points for uploading '{title}'",
            reference_id=str(db_content.id),
            reference_type="content"
        )
        
        # Notify teachers who asked for help on this concept
        notified_teachers = set()
        
        # If responding to a specific help request, notify that teacher first
        if help_request_id:
            specific_hr = db.query(HelpRequest).filter(
                HelpRequest.id == help_request_id,
                HelpRequest.teacher_id != current_teacher.id
            ).first()
            if specific_hr:
                create_notification(
                    db=db,
                    teacher_id=specific_hr.teacher_id,
                    notification_type="help_response",
                    title="Someone Helped You!",
                    message=f"{current_teacher.name} uploaded content to help with your request: '{specific_hr.original_query_text}'",
                    reference_id=str(db_content.id),
                    reference_type="content"
                )
                notified_teachers.add(str(specific_hr.teacher_id))
        
        # Also notify other teachers who asked for help on the same concept
        help_requests = db.query(HelpRequest).filter(
            HelpRequest.concept_id == concept_id,
            HelpRequest.teacher_id != current_teacher.id
        ).all()
        
        for hr in help_requests:
            if str(hr.teacher_id) not in notified_teachers:
                create_notification(
                    db=db,
                    teacher_id=hr.teacher_id,
                    notification_type="content_upload",
                    title="Help Content Available!",
                    message=f"{current_teacher.name} uploaded content for a topic you asked help for: '{concept.description_en or concept_id}'",
                    reference_id=str(db_content.id),
                    reference_type="content"
                )
                notified_teachers.add(str(hr.teacher_id))
        
        return {
            "message": "File uploaded successfully",
            "content_id": str(db_content.id),
            "url": upload_result["url"],
            "public_id": upload_result["public_id"]
        }
        
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
