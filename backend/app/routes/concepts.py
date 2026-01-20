"""
Concepts routes - list available concepts for selection.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.concept import ConceptResponse
from app.services.concept_resolver import ConceptResolver

router = APIRouter(prefix="/concepts", tags=["Concepts"])


@router.get("", response_model=List[ConceptResponse])
def get_concepts(
    language: Optional[str] = Query(None, description="Filter by language (en, kn, hi)"),
    db: Session = Depends(get_db)
):
    """
    Get all available concepts.
    
    Optionally filter by language to only show concepts
    that have synonyms in that language.
    
    Returns localized description based on language parameter.
    
    Used for:
    - Predefined problem selection
    - Content upload concept selection
    """
    concepts = ConceptResolver.get_all_concepts(db, language)
    
    # Attach synonyms to each concept
    result = []
    for concept in concepts:
        synonyms = ConceptResolver.get_synonyms_for_concept(db, concept.concept_id, language)
        
        # Get localized description based on language
        description = concept.description_en  # Default to English
        if language == "hi" and concept.description_hi:
            description = concept.description_hi
        elif language == "kn" and concept.description_kn:
            description = concept.description_kn
        
        concept_dict = {
            "concept_id": concept.concept_id,
            "subject": concept.subject,
            "description_en": concept.description_en,
            "description_hi": getattr(concept, 'description_hi', None),
            "description_kn": getattr(concept, 'description_kn', None),
            "description": description,  # Localized description
            "grade": concept.grade,
            "synonyms": [{"language": s.language, "term": s.term} for s in synonyms]
        }
        result.append(concept_dict)
    
    return result


@router.get("/{concept_id}", response_model=ConceptResponse)
def get_concept(concept_id: str, db: Session = Depends(get_db)):
    """
    Get a specific concept by ID.
    """
    concept = ConceptResolver.get_concept_by_id(db, concept_id)
    if not concept:
        return {"concept_id": concept_id, "subject": "", "description_en": None, "grade": None, "synonyms": []}
    
    synonyms = ConceptResolver.get_synonyms_for_concept(db, concept.concept_id)
    return {
        "concept_id": concept.concept_id,
        "subject": concept.subject,
        "description_en": concept.description_en,
        "grade": concept.grade,
        "synonyms": [{"language": s.language, "term": s.term} for s in synonyms]
    }
