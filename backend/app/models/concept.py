"""
Concept and ConceptSynonym models.

CRITICAL: This is the core of the multilingual search system.
- Concept: Canonical representation of a teaching topic
- ConceptSynonym: Maps multiple language terms to one concept_id

Example:
  concept_id: SCI_BIO_PHOTOSYNTHESIS
  synonyms: ["photosynthesis", "ದ್ಯುತಿಸಂಶ್ಲೇಷಣೆ", "प्रकाश संश्लेषण"]
  
All searches resolve to concept_id FIRST, then query content.
"""
import uuid
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Concept(Base):
    __tablename__ = "concepts"
    
    # Human-readable ID like SCI_BIO_PHOTOSYNTHESIS
    concept_id = Column(Text, primary_key=True)
    subject = Column(Text, nullable=False)  # science, math, english, etc.
    description_en = Column(Text)  # English description
    description_hi = Column(Text)  # Hindi description
    description_kn = Column(Text)  # Kannada description
    grade = Column(Text)  # Grade level: 1-12 or "all"
    
    # Relationship to synonyms
    synonyms = relationship("ConceptSynonym", back_populates="concept")


class ConceptSynonym(Base):
    """
    Maps terms in any language to a canonical concept_id.
    This enables multilingual concept-based search without embeddings.
    """
    __tablename__ = "concept_synonyms"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    concept_id = Column(Text, ForeignKey("concepts.concept_id"), nullable=False)
    language = Column(Text, nullable=False)  # en, kn, hi
    term = Column(Text, nullable=False)  # The actual word/phrase
    
    # Relationship back to concept
    concept = relationship("Concept", back_populates="synonyms")
