"""
Translation service using open-source models.

Supports:
1. IndicTrans2 (AI4Bharat) - Best for Indian languages (Hindi, Kannada, etc.)
2. Argos Translate - Offline translation (limited language support)
3. LibreTranslate API - Self-hosted or public instances

Priority: IndicTrans2 > Argos > LibreTranslate > Fallback (return original)
"""
import httpx
from typing import Optional, Dict
from functools import lru_cache

from app.config import get_settings

settings = get_settings()


class TranslationService:
    """
    Handles text translation between English, Hindi, and Kannada.
    Uses open-source models - no paid API keys required.
    """
    
    # LibreTranslate public instances (free, no API key)
    LIBRETRANSLATE_URLS = [
        "https://libretranslate.com",
        "https://translate.argosopentech.com",
        "https://translate.terraprint.co",
    ]
    
    # Language code mapping
    LANG_CODES = {
        "en": "eng_Latn",  # IndicTrans2 format
        "hi": "hin_Deva",
        "kn": "kan_Knda",
    }
    
    # Cache for translations to avoid repeated API calls
    _cache: Dict[str, str] = {}
    
    @staticmethod
    def _get_cache_key(text: str, source: str, target: str) -> str:
        return f"{source}:{target}:{text}"
    
    @staticmethod
    async def translate_with_libretranslate(
        text: str,
        source_lang: str,
        target_lang: str
    ) -> Optional[str]:
        """
        Translate using LibreTranslate (open-source, free).
        
        Note: LibreTranslate has limited Kannada support.
        """
        # LibreTranslate uses 2-letter codes
        lang_map = {"en": "en", "hi": "hi", "kn": "kn"}
        source = lang_map.get(source_lang, source_lang)
        target = lang_map.get(target_lang, target_lang)
        
        for base_url in TranslationService.LIBRETRANSLATE_URLS:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(
                        f"{base_url}/translate",
                        json={
                            "q": text,
                            "source": source,
                            "target": target,
                            "format": "text"
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        return result.get("translatedText")
                        
            except Exception as e:
                print(f"LibreTranslate ({base_url}) error: {e}")
                continue
        
        return None
    
    @staticmethod
    async def translate_with_argos(
        text: str,
        source_lang: str,
        target_lang: str
    ) -> Optional[str]:
        """
        Translate using Argos Translate (offline, open-source).
        
        Requires: pip install argostranslate
        And downloading language packages.
        """
        try:
            import argostranslate.package
            import argostranslate.translate
            
            # Map to Argos language codes
            lang_map = {"en": "en", "hi": "hi", "kn": "kn"}
            source = lang_map.get(source_lang, source_lang)
            target = lang_map.get(target_lang, target_lang)
            
            # Get installed languages
            installed_languages = argostranslate.translate.get_installed_languages()
            source_lang_obj = next((l for l in installed_languages if l.code == source), None)
            target_lang_obj = next((l for l in installed_languages if l.code == target), None)
            
            if source_lang_obj and target_lang_obj:
                translation = source_lang_obj.get_translation(target_lang_obj)
                if translation:
                    return translation.translate(text)
                    
        except ImportError:
            print("Argos Translate not installed. Run: pip install argostranslate")
        except Exception as e:
            print(f"Argos Translate error: {e}")
        
        return None
    
    @staticmethod
    async def translate_with_indicnlp(
        text: str,
        source_lang: str,
        target_lang: str
    ) -> Optional[str]:
        """
        Translate using IndicTrans2 via Hugging Face Inference API.
        
        IndicTrans2 is specifically designed for Indian languages
        and provides excellent Hindi/Kannada translation.
        
        Free tier: ~30,000 characters/month
        """
        try:
            # Use Hugging Face Inference API (free tier available)
            hf_token = getattr(settings, 'huggingface_token', None)
            
            # IndicTrans2 model on Hugging Face
            model_id = "ai4bharat/indictrans2-en-indic-1B"
            if source_lang != "en":
                model_id = "ai4bharat/indictrans2-indic-en-1B"
            
            headers = {}
            if hf_token:
                headers["Authorization"] = f"Bearer {hf_token}"
            
            # Format input for IndicTrans2
            src_code = TranslationService.LANG_CODES.get(source_lang, "eng_Latn")
            tgt_code = TranslationService.LANG_CODES.get(target_lang, "hin_Deva")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"https://api-inference.huggingface.co/models/{model_id}",
                    headers=headers,
                    json={
                        "inputs": text,
                        "parameters": {
                            "src_lang": src_code,
                            "tgt_lang": tgt_code
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        return result[0].get("translation_text", result[0].get("generated_text"))
                    elif isinstance(result, dict):
                        return result.get("translation_text", result.get("generated_text"))
                        
        except Exception as e:
            print(f"IndicTrans2 error: {e}")
        
        return None
    
    @staticmethod
    async def translate(
        text: str,
        source_lang: str = "en",
        target_lang: str = "hi"
    ) -> str:
        """
        Translate text using available open-source services.
        
        Priority:
        1. Check cache
        2. IndicTrans2 (best for Indian languages)
        3. Argos Translate (offline)
        4. LibreTranslate (online, free)
        5. Return original text (fallback)
        
        Args:
            text: Text to translate
            source_lang: Source language code (en, hi, kn)
            target_lang: Target language code (en, hi, kn)
            
        Returns:
            Translated text or original if translation fails
        """
        if not text or source_lang == target_lang:
            return text
        
        # Check cache
        cache_key = TranslationService._get_cache_key(text, source_lang, target_lang)
        if cache_key in TranslationService._cache:
            return TranslationService._cache[cache_key]
        
        result = None
        
        # Try IndicTrans2 first (best for Hindi/Kannada)
        result = await TranslationService.translate_with_indicnlp(text, source_lang, target_lang)
        if result:
            print(f"Translated with IndicTrans2: {text[:30]}... -> {result[:30]}...")
            TranslationService._cache[cache_key] = result
            return result
        
        # Try Argos Translate (offline)
        result = await TranslationService.translate_with_argos(text, source_lang, target_lang)
        if result:
            print(f"Translated with Argos: {text[:30]}... -> {result[:30]}...")
            TranslationService._cache[cache_key] = result
            return result
        
        # Try LibreTranslate (online, free)
        result = await TranslationService.translate_with_libretranslate(text, source_lang, target_lang)
        if result:
            print(f"Translated with LibreTranslate: {text[:30]}... -> {result[:30]}...")
            TranslationService._cache[cache_key] = result
            return result
        
        # Fallback: return original text
        print(f"Translation failed, returning original: {text[:30]}...")
        return text
    
    @staticmethod
    async def translate_batch(
        texts: list[str],
        source_lang: str = "en",
        target_lang: str = "hi"
    ) -> list[str]:
        """
        Translate multiple texts efficiently.
        """
        results = []
        for text in texts:
            translated = await TranslationService.translate(text, source_lang, target_lang)
            results.append(translated)
        return results
