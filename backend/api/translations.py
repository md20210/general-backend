"""
Translation API Endpoints
Provides multi-language support for CV Matcher frontend
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Literal
from pydantic import BaseModel

from backend.services.translation_service import translation_service, Language

router = APIRouter(prefix="/translations", tags=["translations"])


class TranslationResponse(BaseModel):
    """Response containing all translations for a language"""
    language: Language
    translations: Dict[str, str]


@router.get("/{language}", response_model=TranslationResponse)
async def get_translations(language: Literal["de", "en", "es"]):
    """
    Get all UI translations for a specific language.

    Args:
        language: Language code (de/en/es)

    Returns:
        TranslationResponse with all translations

    Example:
        GET /translations/en
        {
            "language": "en",
            "translations": {
                "app_title": "CV Matcher",
                "match_button": "Start Match",
                ...
            }
        }
    """
    try:
        translations = translation_service.get_all_translations(language)
        return TranslationResponse(
            language=language,
            translations=translations
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/key/{key}")
async def get_translation_key(
    key: str,
    language: Literal["de", "en", "es"] = "de"
):
    """
    Get a single translation by key.

    Args:
        key: Translation key (e.g., "app_title")
        language: Language code (de/en/es), defaults to "de"

    Returns:
        Dict with key and translated value

    Example:
        GET /translations/key/app_title?language=en
        {
            "key": "app_title",
            "value": "CV Matcher",
            "language": "en"
        }
    """
    try:
        value = translation_service.translate(key, language)
        return {
            "key": key,
            "value": value,
            "language": language
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/languages")
async def get_supported_languages():
    """
    Get list of supported languages.

    Returns:
        Dict with list of supported language codes and names

    Example:
        GET /translations/languages
        {
            "languages": [
                {"code": "de", "name": "Deutsch", "flag": "🇩🇪"},
                {"code": "en", "name": "English", "flag": "🇬🇧"},
                {"code": "es", "name": "Español", "flag": "🇪🇸"}
            ]
        }
    """
    return {
        "languages": [
            {"code": "de", "name": "Deutsch", "flag": "🇩🇪"},
            {"code": "en", "name": "English", "flag": "🇬🇧"},
            {"code": "es", "name": "Español", "flag": "🇪🇸"}
        ]
    }
