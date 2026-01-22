"""
Concept Resolution Service - THE CORE OF MULTILINGUAL SEARCH

This service implements the critical concept-based search logic:
1. Detect language of input
2. Normalize text (strip suffixes)
3. Match against CONCEPT_SYNONYMS table
4. If no match, use Gemini to translate and retry
5. Return canonical concept_id

CRITICAL RULES:
- NEVER search raw Kannada/Hindi text
- ALWAYS resolve to concept_id first
- All content queries use concept_id
"""
import re
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.concept import Concept, ConceptSynonym
from app.services.gemini_service import GeminiService


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def similarity_ratio(s1: str, s2: str) -> float:
    """Calculate similarity ratio between two strings (0-1)."""
    distance = levenshtein_distance(s1.lower(), s2.lower())
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0
    return 1.0 - (distance / max_len)


class ConceptResolver:
    """
    Resolves user input (in any language) to a canonical concept_id.
    This enables multilingual search without vector embeddings.
    """
    
    # Common Kannada suffixes to strip for normalization
    KANNADA_SUFFIXES = [
        "ಗಳು",      # plural
        "ಕ್ರಿಯೆ",    # action/process
        "ವನ್ನು",    # accusative
        "ದಲ್ಲಿ",    # locative
        "ಯಲ್ಲಿ",    # locative variant
        "ಯಿಂದ",    # instrumental
        "ಗೆ",       # dative
        "ಯ",        # genitive
    ]
    
    # Common Hindi suffixes to strip
    HINDI_SUFFIXES = [
        "ों",       # plural oblique
        "ें",       # plural
        "ियाँ",     # feminine plural
        "ियों",     # feminine plural oblique
        "ना",       # infinitive
        "ने",       # oblique infinitive
        "में",      # locative
        "से",       # instrumental
        "को",       # dative
        "का",       # genitive masculine
        "की",       # genitive feminine
        "के",       # genitive plural
    ]
    
    # Common English stop words to filter out
    ENGLISH_STOP_WORDS = {
        "i", "me", "my", "we", "our", "you", "your", "he", "she", "it", "they",
        "what", "which", "who", "whom", "this", "that", "these", "those",
        "am", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "having", "do", "does", "did", "doing",
        "a", "an", "the", "and", "but", "if", "or", "because", "as", "until",
        "while", "of", "at", "by", "for", "with", "about", "against", "between",
        "into", "through", "during", "before", "after", "above", "below", "to",
        "from", "up", "down", "in", "out", "on", "off", "over", "under", "again",
        "further", "then", "once", "here", "there", "when", "where", "why", "how",
        "all", "each", "few", "more", "most", "other", "some", "such", "no", "nor",
        "not", "only", "own", "same", "so", "than", "too", "very", "can", "will",
        "just", "should", "now", "want", "need", "help", "understand", "learn",
        "teach", "explain", "know", "tell", "show", "please", "could", "would"
    }
    
    @staticmethod
    def extract_keywords(text: str) -> List[str]:
        """
        Extract meaningful keywords from English text by removing stop words.
        Returns list of keywords sorted by length (longer = more specific).
        """
        words = text.lower().split()
        keywords = [w for w in words if w not in ConceptResolver.ENGLISH_STOP_WORDS and len(w) > 2]
        # Sort by length descending (longer words are usually more specific)
        return sorted(keywords, key=len, reverse=True)
    
    @staticmethod
    def detect_language(text: str) -> str:
        """
        Detect the language of input text.
        Uses Unicode ranges for script detection.
        
        Returns: 'kn' (Kannada), 'hi' (Hindi), or 'en' (English/default)
        """
        # Kannada Unicode range: U+0C80 to U+0CFF
        kannada_pattern = re.compile(r'[\u0C80-\u0CFF]')
        # Devanagari (Hindi) Unicode range: U+0900 to U+097F
        hindi_pattern = re.compile(r'[\u0900-\u097F]')
        
        kannada_count = len(kannada_pattern.findall(text))
        hindi_count = len(hindi_pattern.findall(text))
        
        if kannada_count > hindi_count and kannada_count > 0:
            return "kn"
        elif hindi_count > 0:
            return "hi"
        return "en"
    
    @staticmethod
    def normalize_text(text: str, language: str) -> str:
        """
        Normalize text by:
        1. Converting to lowercase (for English)
        2. Stripping common suffixes
        3. Removing extra whitespace
        
        This improves matching against concept synonyms.
        """
        text = text.strip()
        
        if language == "en":
            text = text.lower()
        elif language == "kn":
            for suffix in ConceptResolver.KANNADA_SUFFIXES:
                if text.endswith(suffix):
                    text = text[:-len(suffix)]
                    break
        elif language == "hi":
            for suffix in ConceptResolver.HINDI_SUFFIXES:
                if text.endswith(suffix):
                    text = text[:-len(suffix)]
                    break
        
        # Remove extra whitespace
        text = " ".join(text.split())
        return text
    
    @staticmethod
    def resolve_concept(db: Session, text: str, speech_language: Optional[str] = None) -> Tuple[Optional[str], str, str]:
        """
        Main resolution function.
        
        Args:
            db: Database session
            text: User input in any language
            speech_language: Optional language detected by speech engine
            
        Returns:
            Tuple of (concept_id, detected_language, normalized_text)
            concept_id is None if no match found
        """
        # Step 1: Detect language
        language = ConceptResolver.detect_language(text)
        
        # If script detection says "en" but speech engine detected "kn" or "hi",
        # it's likely transliterated text (Hinglish/Kanglish).
        # In this case, trust the speech engine.
        if language == "en" and speech_language in ["kn", "hi"]:
            language = speech_language
            print(f"[ConceptResolver] Overriding script language 'en' with speech language '{language}' (Transliteration detected)")
            
        print(f"[ConceptResolver] Input: '{text}' | Language: {language}")
        
        # Step 2: Normalize text
        normalized = ConceptResolver.normalize_text(text, language)
        print(f"[ConceptResolver] Normalized: '{normalized}'")
        
        # Step 3: Try exact match first (case-insensitive for English)
        if language == "en":
            synonym = db.query(ConceptSynonym).filter(
                func.lower(ConceptSynonym.term) == normalized.lower()
            ).first()
        else:
            # For Kannada/Hindi, try exact match
            synonym = db.query(ConceptSynonym).filter(
                ConceptSynonym.term == normalized
            ).first()
        
        if synonym:
            print(f"[ConceptResolver] ✓ Step 3: EXACT MATCH found -> {synonym.concept_id}")
            return (synonym.concept_id, language, normalized)
        print(f"[ConceptResolver] Step 3: Exact match - no match")
        
        # Step 4: Try partial match (contains)
        if language == "en":
            synonym = db.query(ConceptSynonym).filter(
                func.lower(ConceptSynonym.term).contains(normalized.lower())
            ).first()
        else:
            synonym = db.query(ConceptSynonym).filter(
                ConceptSynonym.term.contains(normalized)
            ).first()
        
        if synonym:
            print(f"[ConceptResolver] ✓ Step 4: PARTIAL MATCH found -> {synonym.concept_id}")
            return (synonym.concept_id, language, normalized)
        print(f"[ConceptResolver] Step 4: Partial match - no match")
        
        # Step 4.5: For English, extract keywords and try matching each
        if language == "en":
            keywords = ConceptResolver.extract_keywords(normalized)
            print(f"[ConceptResolver] Step 5: Keywords extracted: {keywords}")
            for keyword in keywords:
                # Try exact match with keyword
                synonym = db.query(ConceptSynonym).filter(
                    func.lower(ConceptSynonym.term) == keyword.lower()
                ).first()
                if synonym:
                    print(f"[ConceptResolver] ✓ Step 5: KEYWORD MATCH '{keyword}' -> {synonym.concept_id}")
                    return (synonym.concept_id, language, normalized)
                
                # Try if synonym contains keyword
                synonym = db.query(ConceptSynonym).filter(
                    func.lower(ConceptSynonym.term).contains(keyword.lower())
                ).first()
                if synonym:
                    print(f"[ConceptResolver] ✓ Step 5: KEYWORD PARTIAL MATCH '{keyword}' -> {synonym.concept_id}")
                    return (synonym.concept_id, language, normalized)
            print(f"[ConceptResolver] Step 5: Keyword match - no match")
        
        # Step 5: Try matching normalized text against any synonym
        # This handles cases where user types partial term
        synonyms = db.query(ConceptSynonym).filter(
            ConceptSynonym.language == language
        ).all()
        
        for syn in synonyms:
            syn_normalized = ConceptResolver.normalize_text(syn.term, language)
            if language == "en":
                if normalized.lower() in syn_normalized.lower() or syn_normalized.lower() in normalized.lower():
                    print(f"[ConceptResolver] ✓ Step 6: SYNONYM SCAN MATCH '{syn.term}' -> {syn.concept_id}")
                    return (syn.concept_id, language, normalized)
            else:
                if normalized in syn_normalized or syn_normalized in normalized:
                    print(f"[ConceptResolver] ✓ Step 6: SYNONYM SCAN MATCH '{syn.term}' -> {syn.concept_id}")
                    return (syn.concept_id, language, normalized)
        print(f"[ConceptResolver] Step 6: Synonym scan - no match")
        
        # Step 6: Fuzzy matching for typos (English only)
        # Use Levenshtein distance to find close matches
        if language == "en" and len(normalized) >= 4:
            best_match = None
            best_score = 0.0
            threshold = 0.7  # 70% similarity required
            
            all_synonyms = db.query(ConceptSynonym).filter(
                ConceptSynonym.language == "en"
            ).all()
            
            for syn in all_synonyms:
                score = similarity_ratio(normalized, syn.term)
                if score > best_score and score >= threshold:
                    best_score = score
                    best_match = syn
            
            if best_match:
                print(f"[ConceptResolver] ✓ Step 7: FUZZY MATCH (score: {best_score:.2f}) '{best_match.term}' -> {best_match.concept_id}")
                return (best_match.concept_id, language, normalized)
            print(f"[ConceptResolver] Step 7: Fuzzy match - no match")
        
        # Step 8: If no match, try Gemini AI to find the best topic
        if GeminiService.is_available():
            try:
                # Get all existing topics for Gemini to match against
                all_concepts = db.query(Concept).all()
                existing_topics = [
                    {"id": c.concept_id, "name": c.description_en or c.concept_id.replace("_", " ").title()}
                    for c in all_concepts
                ]
                
                # Use smart search to find the best matching topic
                search_result = GeminiService.smart_search(text, existing_topics)
                
                if search_result.get("matched_topics") and len(search_result["matched_topics"]) > 0:
                    best_topic = search_result["matched_topics"][0]
                    # Require 0.95+ relevance for a good match (must be very confident)
                    if best_topic.get("id") and best_topic.get("relevance", 0) >= 0.95:
                        print(f"[ConceptResolver] ✓ Step 8: GEMINI SMART SEARCH (relevance: {best_topic.get('relevance')}) -> {best_topic['id']}")
                        return (best_topic["id"], language, normalized)
                    else:
                        print(f"[ConceptResolver] Step 8: Gemini match rejected (relevance {best_topic.get('relevance', 0)} < 0.95)")
                
                # No good match - try to create a new concept
                print(f"[ConceptResolver] Step 9: Creating new concept...")
                topic_suggestion = GeminiService.suggest_topic(text, "", existing_topics)
                
                if topic_suggestion.get("suggested_new_topic_id") and topic_suggestion.get("suggested_new_topic"):
                    new_concept_id = topic_suggestion["suggested_new_topic_id"].upper()
                    new_concept_name = topic_suggestion["suggested_new_topic"]
                    
                    # Check if concept already exists
                    existing = db.query(Concept).filter(Concept.concept_id == new_concept_id).first()
                    if not existing:
                        # Create new concept
                        new_concept = Concept(
                            concept_id=new_concept_id,
                            description_en=new_concept_name,
                            description_hi=topic_suggestion.get("suggested_new_topic_hi"),
                            description_kn=topic_suggestion.get("suggested_new_topic_kn"),
                            subject="General",
                            grade="1-12"
                        )
                        db.add(new_concept)
                        
                        # Add synonyms
                        import uuid
                        synonyms_to_add = []
                        
                        # Add English synonyms
                        for syn in topic_suggestion.get("synonyms_en", [new_concept_name.lower()]):
                            synonyms_to_add.append(ConceptSynonym(
                                id=uuid.uuid4(),
                                concept_id=new_concept_id,
                                language="en",
                                term=syn.lower()
                            ))
                        
                        # Add Hindi synonyms
                        for syn in topic_suggestion.get("synonyms_hi", []):
                            synonyms_to_add.append(ConceptSynonym(
                                id=uuid.uuid4(),
                                concept_id=new_concept_id,
                                language="hi",
                                term=syn
                            ))
                        
                        # Add Kannada synonyms
                        for syn in topic_suggestion.get("synonyms_kn", []):
                            synonyms_to_add.append(ConceptSynonym(
                                id=uuid.uuid4(),
                                concept_id=new_concept_id,
                                language="kn",
                                term=syn
                            ))
                        
                        for syn in synonyms_to_add:
                            db.add(syn)
                        
                        db.commit()
                        print(f"[ConceptResolver] ✓ Step 9: CREATED NEW CONCEPT '{new_concept_id}' ({new_concept_name})")
                        return (new_concept_id, language, normalized)
                    else:
                        print(f"[ConceptResolver] ✓ Step 9: Concept '{new_concept_id}' already exists")
                        return (new_concept_id, language, normalized)
                
                print(f"[ConceptResolver] Step 9: Could not create new concept")
                
                # Fallback: If non-English, try translation approach
                if language != "en":
                    translated_text, _ = GeminiService.translate_text(text, target_language="en")
                    if translated_text and translated_text != text:
                        translated_normalized = ConceptResolver.normalize_text(translated_text, "en")
                        
                        # Try exact match with translated text
                        synonym = db.query(ConceptSynonym).filter(
                            func.lower(ConceptSynonym.term) == translated_normalized.lower()
                        ).first()
                        
                        if synonym:
                            print(f"[ConceptResolver] ✓ Step 8: GEMINI TRANSLATION EXACT MATCH '{translated_normalized}' -> {synonym.concept_id}")
                            return (synonym.concept_id, language, normalized)
                        
                        # Try partial match with translated text
                        synonym = db.query(ConceptSynonym).filter(
                            func.lower(ConceptSynonym.term).contains(translated_normalized.lower())
                        ).first()
                        
                        if synonym:
                            print(f"[ConceptResolver] ✓ Step 8: GEMINI TRANSLATION PARTIAL MATCH '{translated_normalized}' -> {synonym.concept_id}")
                            return (synonym.concept_id, language, normalized)
                print(f"[ConceptResolver] Step 8: Gemini translation - no match")
            except Exception as e:
                print(f"[ConceptResolver] Step 8: Gemini AI error: {e}")
        
        # No match found
        print(f"[ConceptResolver] ✗ NO MATCH FOUND for '{text}'")
        return (None, language, normalized)
    
    @staticmethod
    def get_concept_by_id(db: Session, concept_id: str) -> Optional[Concept]:
        """Get a concept by its ID."""
        return db.query(Concept).filter(Concept.concept_id == concept_id).first()
    
    @staticmethod
    def get_all_concepts(db: Session, language: Optional[str] = None) -> List[Concept]:
        """
        Get all concepts, optionally filtered by language.
        If language is specified, only returns concepts that have synonyms in that language.
        """
        if language:
            concept_ids = db.query(ConceptSynonym.concept_id).filter(
                ConceptSynonym.language == language
            ).distinct().all()
            concept_ids = [c[0] for c in concept_ids]
            return db.query(Concept).filter(Concept.concept_id.in_(concept_ids)).all()
        return db.query(Concept).all()
    
    @staticmethod
    def get_synonyms_for_concept(db: Session, concept_id: str, language: Optional[str] = None) -> List[ConceptSynonym]:
        """Get all synonyms for a concept, optionally filtered by language."""
        query = db.query(ConceptSynonym).filter(ConceptSynonym.concept_id == concept_id)
        if language:
            query = query.filter(ConceptSynonym.language == language)
        return query.all()
