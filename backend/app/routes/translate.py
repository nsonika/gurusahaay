"""
Translation routes - translate text between languages.
Uses open-source models (IndicTrans2, Argos, LibreTranslate).
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.services.translation_service import TranslationService

router = APIRouter(prefix="/translate", tags=["Translation"])


class TranslateRequest(BaseModel):
    text: str
    source_lang: str = "en"  # en, hi, kn
    target_lang: str = "hi"  # en, hi, kn


class TranslateResponse(BaseModel):
    original: str
    translated: str
    source_lang: str
    target_lang: str


class BatchTranslateRequest(BaseModel):
    texts: List[str]
    source_lang: str = "en"
    target_lang: str = "hi"


class BatchTranslateResponse(BaseModel):
    translations: List[TranslateResponse]


@router.post("", response_model=TranslateResponse)
async def translate_text(request: TranslateRequest):
    """
    Translate text between English, Hindi, and Kannada.
    
    Uses open-source models:
    1. IndicTrans2 (AI4Bharat) - Best for Indian languages
    2. Argos Translate - Offline
    3. LibreTranslate - Free online API
    """
    if request.source_lang not in ["en", "hi", "kn"]:
        raise HTTPException(status_code=400, detail="Invalid source language. Use: en, hi, kn")
    if request.target_lang not in ["en", "hi", "kn"]:
        raise HTTPException(status_code=400, detail="Invalid target language. Use: en, hi, kn")
    
    translated = await TranslationService.translate(
        request.text,
        request.source_lang,
        request.target_lang
    )
    
    return TranslateResponse(
        original=request.text,
        translated=translated,
        source_lang=request.source_lang,
        target_lang=request.target_lang
    )


@router.post("/batch", response_model=BatchTranslateResponse)
async def translate_batch(request: BatchTranslateRequest):
    """
    Translate multiple texts at once.
    """
    if request.source_lang not in ["en", "hi", "kn"]:
        raise HTTPException(status_code=400, detail="Invalid source language. Use: en, hi, kn")
    if request.target_lang not in ["en", "hi", "kn"]:
        raise HTTPException(status_code=400, detail="Invalid target language. Use: en, hi, kn")
    
    translations = []
    for text in request.texts:
        translated = await TranslationService.translate(
            text,
            request.source_lang,
            request.target_lang
        )
        translations.append(TranslateResponse(
            original=text,
            translated=translated,
            source_lang=request.source_lang,
            target_lang=request.target_lang
        ))
    
    return BatchTranslateResponse(translations=translations)
