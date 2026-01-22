"""
Help Request routes - the main entry point for teacher queries.

This is where the CRITICAL concept resolution happens:
1. Accept text or voice input
2. Detect language
3. Normalize text
4. Resolve to concept_id
5. Store help request for analytics
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.teacher import Teacher
from app.models.help_request import HelpRequest, HelpResponse
from app.schemas.help_request import HelpRequestCreate, HelpRequestResponse
from app.routes.auth import get_current_teacher
from app.services.concept_resolver import ConceptResolver
from app.services.speech_service import SpeechService
from app.routes.notifications import create_notification

router = APIRouter(prefix="/help", tags=["Help"])


class HelpResponseCreate(BaseModel):
    response_text: str


class HelpResponseOut(BaseModel):
    id: str
    teacher_id: str
    teacher_name: str
    response_text: str
    created_at: str


class HelpRequestDetail(BaseModel):
    id: str
    teacher_id: str
    teacher_name: str
    original_query_text: str
    detected_language: str | None
    concept_id: str | None
    subject: str | None
    grade: str | None
    created_at: str
    responses: List[HelpResponseOut]


@router.post("/request", response_model=HelpRequestResponse)
def create_help_request(
    request: HelpRequestCreate,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher)
):
    """
    Create a new help request.
    
    CRITICAL FLOW:
    1. If voice input → transcribe with Whisper
    2. Detect language of text
    3. Normalize text (strip suffixes)
    4. Resolve to concept_id using CONCEPT_SYNONYMS
    5. Store request for analytics
    6. Return resolved concept_id for suggestions lookup
    
    The frontend should then call GET /suggestions?concept_id=X
    """
    query_text = request.query_text
    detected_language = None
    
    # Handle voice input
    if request.request_type == "voice" and request.audio_base64:
        if not SpeechService.is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Speech recognition not available"
            )
        language_hint = current_teacher.language_preference
        query_text, detected_language = SpeechService.transcribe_audio(
            request.audio_base64, 
            language_hint=language_hint
        )
    
    if not query_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either query_text or audio_base64 must be provided"
        )
    
    # CRITICAL: Resolve to concept_id
    # This is the core of the multilingual search system
    concept_id, language, normalized_text = ConceptResolver.resolve_concept(
        db, query_text, speech_language=detected_language
    )
    
    # Store help request for analytics
    help_request = HelpRequest(
        teacher_id=current_teacher.id,
        original_query_text=query_text,
        detected_language=language,
        normalized_text=normalized_text,
        concept_id=concept_id,
        subject=request.subject,
        grade=request.grade,
        request_type=request.request_type
    )
    db.add(help_request)
    db.commit()
    db.refresh(help_request)
    
    return help_request


@router.get("/recent", response_model=List[HelpRequestDetail])
def get_recent_help_requests(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher)
):
    """
    Get recent help requests for the upload page.
    Shows requests that need content contributions.
    """
    from sqlalchemy import desc
    
    help_requests = db.query(HelpRequest).order_by(
        desc(HelpRequest.created_at)
    ).limit(limit).all()
    
    results = []
    for hr in help_requests:
        requester = db.query(Teacher).filter(Teacher.id == hr.teacher_id).first()
        
        # Get responses
        responses = []
        for response in hr.responses:
            responder = db.query(Teacher).filter(Teacher.id == response.teacher_id).first()
            responses.append(HelpResponseOut(
                id=str(response.id),
                teacher_id=str(response.teacher_id),
                teacher_name=responder.name if responder else "Teacher",
                response_text=response.response_text,
                created_at=response.created_at.isoformat()
            ))
        
        results.append(HelpRequestDetail(
            id=str(hr.id),
            teacher_id=str(hr.teacher_id),
            teacher_name=requester.name if requester else "Teacher",
            original_query_text=hr.original_query_text,
            detected_language=hr.detected_language,
            concept_id=hr.concept_id,
            subject=hr.subject,
            grade=hr.grade,
            created_at=hr.created_at.isoformat(),
            responses=responses
        ))
    
    return results


@router.get("/request/{request_id}", response_model=HelpRequestDetail)
def get_help_request(
    request_id: str,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher)
):
    """
    Get a specific help request with all its responses.
    """
    help_request = db.query(HelpRequest).filter(
        HelpRequest.id == request_id
    ).first()
    
    if not help_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Help request not found"
        )
    
    # Get the teacher who made the request
    requester = db.query(Teacher).filter(Teacher.id == help_request.teacher_id).first()
    
    # Get all responses with teacher names
    responses = []
    for response in help_request.responses:
        responder = db.query(Teacher).filter(Teacher.id == response.teacher_id).first()
        responses.append(HelpResponseOut(
            id=str(response.id),
            teacher_id=str(response.teacher_id),
            teacher_name=responder.name if responder else "Teacher",
            response_text=response.response_text,
            created_at=response.created_at.isoformat()
        ))
    
    return HelpRequestDetail(
        id=str(help_request.id),
        teacher_id=str(help_request.teacher_id),
        teacher_name=requester.name if requester else "Teacher",
        original_query_text=help_request.original_query_text,
        detected_language=help_request.detected_language,
        concept_id=help_request.concept_id,
        subject=help_request.subject,
        grade=help_request.grade,
        created_at=help_request.created_at.isoformat(),
        responses=responses
    )


@router.post("/request/{request_id}/respond", response_model=HelpResponseOut)
def add_response(
    request_id: str,
    response: HelpResponseCreate,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher)
):
    """
    Add a response to a help request.
    """
    help_request = db.query(HelpRequest).filter(
        HelpRequest.id == request_id
    ).first()
    
    if not help_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Help request not found"
        )
    
    new_response = HelpResponse(
        help_request_id=help_request.id,
        teacher_id=current_teacher.id,
        response_text=response.response_text
    )
    db.add(new_response)
    db.commit()
    db.refresh(new_response)
    
    # Notify the help request author about the response
    if help_request.teacher_id != current_teacher.id:
        create_notification(
            db=db,
            teacher_id=help_request.teacher_id,
            notification_type="help_response",
            title="New Response!",
            message=f"{current_teacher.name} responded to your help request",
            reference_id=str(help_request.id),
            reference_type="help_request"
        )
    
    return HelpResponseOut(
        id=str(new_response.id),
        teacher_id=str(new_response.teacher_id),
        teacher_name=current_teacher.name,
        response_text=new_response.response_text,
        created_at=new_response.created_at.isoformat()
    )
