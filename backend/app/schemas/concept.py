"""
Concept schemas.
"""
from pydantic import BaseModel
from typing import List, Optional


class ConceptSynonymResponse(BaseModel):
    language: str
    term: str

    class Config:
        from_attributes = True


class ConceptResponse(BaseModel):
    concept_id: str
    subject: str
    description_en: Optional[str]
    description_hi: Optional[str] = None
    description_kn: Optional[str] = None
    description: Optional[str] = None  # Localized description based on user's language
    grade: Optional[str]
    synonyms: List[ConceptSynonymResponse] = []

    class Config:
        from_attributes = True
