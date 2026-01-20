"""
AI routes - Gemini-powered features for topic suggestion, translation, and search.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.teacher import Teacher
from app.models.concept import Concept, ConceptSynonym
from app.routes.auth import get_current_teacher
from app.services.gemini_service import GeminiService

router = APIRouter(prefix="/ai", tags=["AI"])


class TopicSuggestionRequest(BaseModel):
    title: str
    description: str = ""


class TopicSuggestionResponse(BaseModel):
    matched_topic_id: Optional[str]
    matched_topic_name: Optional[str]
    confidence: float
    suggested_new_topic: Optional[str]
    suggested_new_topic_id: Optional[str]
    suggested_new_topic_hi: Optional[str] = None
    suggested_new_topic_kn: Optional[str] = None
    synonyms_en: List[str] = []
    synonyms_hi: List[str] = []
    synonyms_kn: List[str] = []
    error: Optional[str] = None


class TranslateRequest(BaseModel):
    text: str
    target_language: str = "en"
    source_language: Optional[str] = None


class TranslateResponse(BaseModel):
    translated_text: str
    source_language: str


class SmartSearchRequest(BaseModel):
    query: str


class SmartSearchResponse(BaseModel):
    original_query: str
    translated_query: str
    detected_language: str
    matched_topics: List[dict]
    search_keywords: List[str]
    error: Optional[str] = None


class CreateTopicRequest(BaseModel):
    topic_id: str
    topic_name: str
    topic_name_hi: str = None
    topic_name_kn: str = None
    synonyms_en: list = []
    synonyms_hi: list = []
    synonyms_kn: list = []
    subject: str = "General"
    grade: str = "All"


@router.get("/status")
def get_ai_status():
    """Check if Gemini AI is available."""
    return {
        "available": GeminiService.is_available(),
        "message": "Gemini AI is ready" if GeminiService.is_available() else "Gemini API key not configured"
    }


@router.post("/suggest-topic", response_model=TopicSuggestionResponse)
def suggest_topic(
    request: TopicSuggestionRequest,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher)
):
    """
    Use AI to suggest the best matching topic for content.
    If no good match, suggests a new topic to create.
    """
    # Get existing topics
    concepts = db.query(Concept).all()
    existing_topics = [
        {"id": c.concept_id, "name": c.description_en or c.concept_id.replace("_", " ").title()}
        for c in concepts
    ]
    
    result = GeminiService.suggest_topic(
        title=request.title,
        description=request.description,
        existing_topics=existing_topics
    )
    
    return TopicSuggestionResponse(**result)


@router.post("/translate", response_model=TranslateResponse)
def translate_text(
    request: TranslateRequest,
    current_teacher: Teacher = Depends(get_current_teacher)
):
    """
    Translate text between English, Hindi, and Kannada.
    """
    translated, source_lang = GeminiService.translate_text(
        text=request.text,
        target_language=request.target_language,
        source_language=request.source_language
    )
    
    return TranslateResponse(
        translated_text=translated,
        source_language=source_lang
    )


@router.post("/smart-search", response_model=SmartSearchResponse)
def smart_search(
    request: SmartSearchRequest,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher)
):
    """
    Smart search that understands multilingual queries.
    Translates and finds relevant topics.
    """
    # Get existing topics
    concepts = db.query(Concept).all()
    existing_topics = [
        {"id": c.concept_id, "name": c.description_en or c.concept_id.replace("_", " ").title()}
        for c in concepts
    ]
    
    result = GeminiService.smart_search(
        query=request.query,
        existing_topics=existing_topics
    )
    
    return SmartSearchResponse(**result)


@router.post("/create-topic")
def create_topic(
    request: CreateTopicRequest,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher)
):
    """
    Create a new topic (concept) in the database with translations and synonyms.
    Used when AI suggests a new topic that doesn't exist.
    """
    # Check if topic already exists
    existing = db.query(Concept).filter(Concept.concept_id == request.topic_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Topic already exists")
    
    # Create new concept with translations
    new_concept = Concept(
        concept_id=request.topic_id,
        description_en=request.topic_name,
        description_hi=request.topic_name_hi,
        description_kn=request.topic_name_kn,
        subject=request.subject,
        grade=request.grade
    )
    db.add(new_concept)
    
    # Add English synonyms
    for syn in [request.topic_name.lower()] + (request.synonyms_en or []):
        if syn:
            synonym = ConceptSynonym(
                concept_id=request.topic_id,
                term=syn.lower().strip(),
                language="en"
            )
            db.add(synonym)
    
    # Add Hindi synonyms
    for syn in ([request.topic_name_hi] if request.topic_name_hi else []) + (request.synonyms_hi or []):
        if syn:
            synonym = ConceptSynonym(
                concept_id=request.topic_id,
                term=syn.strip(),
                language="hi"
            )
            db.add(synonym)
    
    # Add Kannada synonyms
    for syn in ([request.topic_name_kn] if request.topic_name_kn else []) + (request.synonyms_kn or []):
        if syn:
            synonym = ConceptSynonym(
                concept_id=request.topic_id,
                term=syn.strip(),
                language="kn"
            )
            db.add(synonym)
    
    db.commit()
    
    return {
        "message": "Topic created successfully with translations",
        "topic_id": request.topic_id,
        "topic_name": request.topic_name,
        "topic_name_hi": request.topic_name_hi,
        "topic_name_kn": request.topic_name_kn,
        "synonyms_added": len(request.synonyms_en or []) + len(request.synonyms_hi or []) + len(request.synonyms_kn or []) + 3
    }
