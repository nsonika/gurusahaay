"""
Gemini AI Service - Uses Google's Gemini API for:
1. Auto-selecting topics based on content title/description
2. Creating new topics if none match
3. Translating text between languages
4. Smart search with multilingual support

Uses HTTP requests instead of the SDK for Python 3.14 compatibility.
"""
import os
import json
import requests
from typing import Optional, Tuple, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
# Fallback models in order of preference (only available models)
# Fallback models in order of preference
GEMINI_MODELS = ["gemini-flash-latest", "gemini-2.5-flash-lite", "gemini-2.0-flash-exp"]


class GeminiService:
    """Service for Gemini AI operations using HTTP API."""
    
    @staticmethod
    def is_available() -> bool:
        """Check if Gemini API is configured."""
        return bool(GEMINI_API_KEY)

    @staticmethod
    def _make_gemini_request(data: dict, tool_config: dict = None, retries: int = 2) -> dict:
        """Generic method to call Gemini API with fallbacks."""
        import time
        
        last_error = None
        headers = {"Content-Type": "application/json"}
        
        for model in GEMINI_MODELS:
            print(f"[GeminiService] Trying model: {model}")
            for attempt in range(retries + 1):
                try:
                    url = f"{GEMINI_BASE_URL}/{model}:generateContent?key={GEMINI_API_KEY}"
                    response = requests.post(
                        url,
                        headers=headers,
                        json=data,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        return response.json()
                    elif response.status_code == 503:
                        last_error = f"Model {model} overloaded"
                        print(f"[GeminiService] {last_error}")
                        if attempt < retries:
                            time.sleep(1)
                            continue
                        break
                    elif response.status_code == 429:
                        last_error = f"Model {model} quota exceeded"
                        print(f"[GeminiService] {last_error}")
                        break
                    else:
                        last_error = f"Gemini API error ({model}): {response.status_code} - {response.text}"
                        print(f"[GeminiService] {last_error}")
                        break
                except requests.exceptions.Timeout:
                    last_error = f"Model {model} timeout"
                    print(f"[GeminiService] {last_error}")
                    break
                except Exception as e:
                    last_error = str(e)
                    print(f"[GeminiService] Exception ({model}): {last_error}")
                    break
        
        raise Exception(last_error or "All Gemini models failed")

    @staticmethod
    def _call_gemini(prompt: str, retries: int = 2) -> str:
        """Make HTTP request to Gemini API with fallback models and retry logic."""
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        try:
            result = GeminiService._make_gemini_request(data, retries=retries)
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            raise e

    @staticmethod
    def google_web_search(query: str, num_results: int = 5) -> List[dict]:
        """
        Use Google Search via Gemini API to find educational content.
        
        Returns:
            List of search results with title, url, and snippet
        """
        if not GeminiService.is_available():
            return []
        
        try:
            # Use google_search tool with Gemini
            data = {
                "contents": [{
                    "parts": [{"text": f"Find {num_results} educational resources (videos, articles, websites) about: {query}. For each result, provide the title, URL, and a brief description. Focus on educational content suitable for teachers and students."}]
                }],
                "tools": [{
                    "google_search": {}
                }]
            }
            
            result = GeminiService._make_gemini_request(data)
            
            # Extract grounding metadata if available
            candidates = result.get("candidates", [])
            if candidates:
                candidate = candidates[0]
                grounding_metadata = candidate.get("groundingMetadata", {})
                grounding_chunks = grounding_metadata.get("groundingChunks", [])
                
                search_results = []
                for chunk in grounding_chunks[:num_results]:
                    web_info = chunk.get("web", {})
                    if web_info:
                        search_results.append({
                            "title": web_info.get("title", ""),
                            "url": web_info.get("uri", ""),
                            "snippet": ""
                        })
                
                # If we got grounding results, return them
                if search_results:
                    print(f"[GeminiService] Google Search found {len(search_results)} results for '{query}'")
                    return search_results
                
                # Otherwise, parse the text response
                text_response = candidate.get("content", {}).get("parts", [{}])[0].get("text", "")
                if text_response:
                    # Try to extract URLs from the response
                    import re
                    urls = re.findall(r'https?://[^\s\)\"\']+', text_response)
                    for i, url_found in enumerate(urls[:num_results]):
                        search_results.append({
                            "title": f"Resource {i+1}",
                            "url": url_found,
                            "snippet": ""
                        })
                    if search_results:
                        print(f"[GeminiService] Extracted {len(search_results)} URLs from response")
                        return search_results
            
            print("[GeminiService] Google Search returned no candidates")
            return []
            
        except Exception as e:
            print(f"[GeminiService] Google Search error: {e}")
            return []
    
    @staticmethod
    def suggest_topic(
        title: str,
        description: str = "",
        existing_topics: List[dict] = None
    ) -> dict:
        """
        Suggest the best matching topic for content based on title and description.
        
        Returns:
            {
                "matched_topic_id": str or None,  # ID of matched existing topic
                "matched_topic_name": str or None,  # Name of matched topic
                "confidence": float,  # 0-1 confidence score
                "suggested_new_topic": str or None,  # If no match, suggest new topic name
                "suggested_new_topic_id": str or None,  # snake_case ID for new topic
            }
        """
        if not GeminiService.is_available():
            return {
                "matched_topic_id": None,
                "matched_topic_name": None,
                "confidence": 0,
                "suggested_new_topic": None,
                "suggested_new_topic_id": None,
                "error": "Gemini API not configured"
            }
        
        try:
            # Format existing topics for the prompt
            topics_list = ""
            if existing_topics:
                for topic in existing_topics:
                    topics_list += f"- ID: {topic['id']}, Name: {topic['name']}\n"
            
            prompt = f"""You are a topic classifier for an educational content platform for teachers in India.

Given the following content title and description, find the best matching topic from the existing topics list.
If no topic matches well (confidence < 0.7), suggest a new topic name with translations.

Content Title: {title}
Content Description: {description or 'No description provided'}

Existing Topics:
{topics_list if topics_list else 'No existing topics'}

Respond in JSON format only:
{{
    "matched_topic_id": "topic_id_here" or null,
    "matched_topic_name": "Topic Name" or null,
    "confidence": 0.0 to 1.0,
    "suggested_new_topic": "New Topic Name in English" or null,
    "suggested_new_topic_id": "new_topic_id" or null,
    "suggested_new_topic_hi": "Hindi translation" or null,
    "suggested_new_topic_kn": "Kannada translation" or null,
    "synonyms_en": ["english synonym 1", "english synonym 2"] or [],
    "synonyms_hi": ["hindi synonym 1", "hindi synonym 2"] or [],
    "synonyms_kn": ["kannada synonym 1", "kannada synonym 2"] or []
}}

Rules:
1. If confidence >= 0.7, return the matched topic (no need for translations)
2. If confidence < 0.7, suggest a new topic with:
   - English name and snake_case ID
   - Hindi translation (Devanagari script)
   - Kannada translation (Kannada script)
   - Common synonyms in all 3 languages for better search
3. Topic names should be educational and descriptive
4. New topic IDs should be lowercase with underscores (e.g., "air_pollution")
5. Synonyms should include common ways teachers might search for this topic
"""
            
            result_text = GeminiService._call_gemini(prompt)
            
            # Extract JSON from response
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]
            
            result = json.loads(result_text.strip())
            return result
            
        except Exception as e:
            print(f"Gemini topic suggestion error: {e}")
            return {
                "matched_topic_id": None,
                "matched_topic_name": None,
                "confidence": 0,
                "suggested_new_topic": None,
                "suggested_new_topic_id": None,
                "error": str(e)
            }
    
    @staticmethod
    def translate_text(
        text: str,
        target_language: str = "en",
        source_language: str = None
    ) -> Tuple[str, str]:
        """
        Translate text to target language.
        
        Args:
            text: Text to translate
            target_language: Target language code (en, hi, kn)
            source_language: Source language code (auto-detect if None)
            
        Returns:
            Tuple of (translated_text, detected_source_language)
        """
        if not GeminiService.is_available():
            return text, source_language or "unknown"
        
        try:
            lang_names = {
                "en": "English",
                "hi": "Hindi",
                "kn": "Kannada"
            }
            
            target_lang_name = lang_names.get(target_language, "English")
            
            prompt = f"""Translate the following text to {target_lang_name}.
Also detect the source language.

Text: {text}

Respond in JSON format only:
{{
    "translated_text": "translated text here",
    "source_language": "en" or "hi" or "kn"
}}
"""
            
            result_text = GeminiService._call_gemini(prompt)
            
            # Extract JSON from response
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]
            
            result = json.loads(result_text.strip())
            return result.get("translated_text", text), result.get("source_language", "unknown")
            
        except Exception as e:
            print(f"Gemini translation error: {e}")
            return text, source_language or "unknown"
    
    @staticmethod
    def smart_search(
        query: str,
        existing_topics: List[dict] = None
    ) -> dict:
        """
        Smart search that understands multilingual queries and finds relevant topics.
        
        Returns:
            {
                "original_query": str,
                "translated_query": str,  # English translation
                "detected_language": str,
                "matched_topics": [{"id": str, "name": str, "relevance": float}],
                "search_keywords": [str]
            }
        """
        if not GeminiService.is_available():
            return {
                "original_query": query,
                "translated_query": query,
                "detected_language": "unknown",
                "matched_topics": [],
                "search_keywords": [query],
                "error": "Gemini API not configured"
            }
        
        try:
            # Format existing topics for the prompt
            topics_list = ""
            if existing_topics:
                for topic in existing_topics:
                    topics_list += f"- ID: {topic['id']}, Name: {topic['name']}\n"
            
            prompt = f"""You are a smart search assistant for an educational platform.

Given the search query (which may be in English, Hindi, or Kannada), find relevant topics.

Search Query: {query}

Existing Topics:
{topics_list if topics_list else 'No existing topics'}

Respond in JSON format only:
{{
    "original_query": "{query}",
    "translated_query": "English translation of query",
    "detected_language": "en" or "hi" or "kn",
    "matched_topics": [
        {{"id": "topic_id", "name": "Topic Name", "relevance": 0.0 to 1.0}}
    ],
    "search_keywords": ["keyword1", "keyword2"]
}}

Rules:
1. Translate the query to English if it's in Hindi or Kannada
2. Find all relevant topics (relevance >= 0.5)
3. Sort matched_topics by relevance (highest first)
4. Extract useful search keywords from the query
"""
            
            result_text = GeminiService._call_gemini(prompt)
            
            # Extract JSON from response
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]
            
            result = json.loads(result_text.strip())
            return result
            
        except Exception as e:
            print(f"Gemini smart search error: {e}")
            return {
                "original_query": query,
                "translated_query": query,
                "detected_language": "unknown",
                "matched_topics": [],
                "search_keywords": [query],
                "error": str(e)
            }
