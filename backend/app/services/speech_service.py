"""
Speech Service - Whisper integration for voice input.

Handles:
- Base64 audio decoding
- Whisper transcription (when available)
- Language detection from speech
- Fallback stub when Whisper not installed
"""
import base64
import tempfile
import os
from typing import Tuple

from app.config import get_settings

settings = get_settings()

# Lazy load whisper to avoid slow startup
_whisper_model = None
_whisper_available = None


def check_whisper_available() -> bool:
    """Check if Whisper is installed."""
    global _whisper_available
    if _whisper_available is None:
        try:
            import whisper
            _whisper_available = True
        except ImportError:
            _whisper_available = False
    return _whisper_available


def get_whisper_model():
    """Lazy load Whisper model to avoid slow startup."""
    global _whisper_model
    if _whisper_model is None and check_whisper_available():
        import whisper
        _whisper_model = whisper.load_model(settings.whisper_model_size)
    return _whisper_model


class SpeechService:
    """
    Handles speech-to-text conversion using Whisper.
    Supports Kannada, Hindi, and English.
    Falls back to a stub if Whisper is not installed.
    """
    
    @staticmethod
    def transcribe_audio(audio_base64: str, language_hint: str = None) -> Tuple[str, str]:
        """
        Transcribe base64-encoded audio to text.
        
        Args:
            audio_base64: Base64 encoded audio data
            language_hint: Optional language code hint (en, kn, hi)
            
        Returns:
            Tuple of (transcribed_text, detected_language)
        """
        if not check_whisper_available():
            # Whisper not installed - return placeholder
            # In production, you would integrate with an external STT API
            return ("", "en")
        
        # Decode base64 audio
        audio_bytes = base64.b64decode(audio_base64)
        
        # Write to temporary file (Whisper needs file path)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name
        
        try:
            model = get_whisper_model()
            
            # Map our hint to Whisper language codes
            whisper_lang = None
            if language_hint == "kn":
                whisper_lang = "kn"
            elif language_hint == "hi":
                whisper_lang = "hi"
            
            # Transcribe with language detection/hint
            result = model.transcribe(
                tmp_path,
                task="transcribe",
                language=whisper_lang
            )
            
            text = result["text"].strip()
            detected_lang = result.get("language", "en")
            
            # Map Whisper language codes to our codes
            lang_map = {
                "kannada": "kn",
                "kn": "kn",
                "hindi": "hi",
                "hi": "hi",
                "english": "en",
                "en": "en",
            }
            language = lang_map.get(detected_lang.lower(), "en")
            
            return (text, language)
            
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    @staticmethod
    def is_available() -> bool:
        """Check if Whisper is available."""
        return check_whisper_available()
