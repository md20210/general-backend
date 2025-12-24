"""
Translation API Endpoints
Provides multi-language support for CV Matcher frontend

This module exposes REST endpoints for fetching UI translations and LLM prompts
in multiple languages (German, English, Spanish). The translation service uses
a centralized dictionary with variable interpolation support.

See docs/TRANSLATION_SERVICE.md for complete documentation.
"""
from fastapi import APIRouter, HTTPException, Path, Query
from typing import Dict, Literal
from pydantic import BaseModel, Field

from backend.services.translation_service import TranslationService, Language

# Create service instance
translation_service = TranslationService()

router = APIRouter(
    prefix="/translations",
    tags=["translations"],
    responses={
        500: {"description": "Internal server error"}
    }
)


class TranslationResponse(BaseModel):
    """Response containing all translations for a language"""
    language: Language = Field(
        ...,
        description="Language code of the returned translations",
        example="en"
    )
    translations: Dict[str, str] = Field(
        ...,
        description="Dictionary mapping translation keys to translated strings (~70 keys)",
        example={
            "app_title": "CV Matcher",
            "match_button": "Start Match",
            "analyzing": "Analyzing...",
            "strengths_title": "Strengths",
            "gaps_title": "Gaps"
        }
    )

    class Config:
        schema_extra = {
            "example": {
                "language": "en",
                "translations": {
                    "app_title": "CV Matcher",
                    "llm_toggle_local": "🏠 Local (GDPR)",
                    "llm_toggle_grok": "⚡ GROK (non-GDPR)",
                    "match_button": "Start Match",
                    "analyzing": "Analyzing...",
                    "strengths_title": "Strengths",
                    "gaps_title": "Gaps",
                    "recommendations_title": "Recommendations",
                    "chat_title": "💬 Interactive Chat",
                    "error_analysis_failed": "Analysis error. Please try again."
                }
            }
        }


@router.get(
    "/{language}",
    response_model=TranslationResponse,
    summary="Get all translations for a language",
    description="""
Retrieves all UI translations for the specified language.

**Supported Languages:**
- `de`: German (Deutsch)
- `en`: English
- `es`: Spanish (Español)

**Usage:**
Frontend applications should call this endpoint once per language switch
and cache the results in application state (e.g., React Context).

**Performance:**
- Response time: <10ms
- Response size: ~15KB
- Total keys: ~70

**Example Frontend Usage:**
```typescript
const response = await fetch('/translations/en');
const { translations } = await response.json();
// translations = { "app_title": "CV Matcher", ... }
```
    """,
    responses={
        200: {
            "description": "Translations retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "language": "en",
                        "translations": {
                            "app_title": "CV Matcher",
                            "match_button": "Start Match",
                            "analyzing": "Analyzing...",
                            "strengths_title": "Strengths"
                        }
                    }
                }
            }
        },
        422: {
            "description": "Invalid language code (must be de/en/es)"
        }
    }
)
async def get_translations(
    language: Literal["de", "en", "es"] = Path(
        ...,
        description="Language code: 'de' (German), 'en' (English), or 'es' (Spanish)",
        example="en"
    )
):
    """
    Get all UI translations for a specific language.

    This endpoint returns a complete set of ~70 translation keys used throughout
    the CV Matcher application. Translations support variable interpolation using
    {variable} syntax (e.g., "with {count} messages").

    **Caching Recommendation:**
    Frontend should cache translations in state and only re-fetch on language change.
    """
    try:
        translations = translation_service.get_all_translations(language)
        return TranslationResponse(
            language=language,
            translations=translations
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/key/{key}",
    summary="Get single translation by key",
    description="""
Retrieves a single translation for the specified key and language.

**Use Case:**
This endpoint is useful for:
- Testing specific translation keys
- Debugging translation issues
- Fetching individual translations on-demand

**Note:**
For production use, prefer `GET /translations/{language}` to fetch all
translations at once instead of making multiple requests.

**Example Keys:**
- `app_title`: Application title
- `match_button`: Match button text
- `error_analysis_failed`: Analysis error message
- `chat_title`: Chat section title

See docs/TRANSLATION_SERVICE.md for complete list of ~70 keys.
    """,
    responses={
        200: {
            "description": "Translation retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "key": "match_button",
                        "value": "Start Match",
                        "language": "en"
                    }
                }
            }
        },
        422: {
            "description": "Invalid language code"
        }
    }
)
async def get_translation_key(
    key: str = Path(
        ...,
        description="Translation key to retrieve",
        example="match_button"
    ),
    language: Literal["de", "en", "es"] = Query(
        "de",
        description="Language code (defaults to German)",
        example="en"
    )
):
    """
    Get a single translation by key.

    If the key doesn't exist, returns the key itself as the value (fallback behavior).

    **Performance:**
    - Response time: <5ms
    - Response size: <1KB
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


@router.get(
    "/languages",
    summary="Get list of supported languages",
    description="""
Returns metadata about all supported languages.

**Use Case:**
- Dynamically populate language selector in UI
- Validate language codes
- Display language names and flags

**Current Languages:**
1. **German (de)**: Deutsch 🇩🇪
2. **English (en)**: English 🇬🇧
3. **Spanish (es)**: Español 🇪🇸

**Example Frontend Usage:**
```typescript
const { languages } = await fetch('/translations/languages').then(r => r.json());
// Render language toggle with flags
languages.forEach(lang => {
  console.log(`${lang.flag} ${lang.name} (${lang.code})`);
});
```

**Future Languages:**
Planned support for French (fr), Italian (it), Portuguese (pt).
    """,
    responses={
        200: {
            "description": "List of supported languages retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "languages": [
                            {"code": "de", "name": "Deutsch", "flag": "🇩🇪"},
                            {"code": "en", "name": "English", "flag": "🇬🇧"},
                            {"code": "es", "name": "Español", "flag": "🇪🇸"}
                        ]
                    }
                }
            }
        }
    }
)
async def get_supported_languages():
    """
    Get list of supported languages with metadata.

    Returns language code, display name, and emoji flag for each supported language.

    **Performance:**
    - Response time: <5ms
    - Response size: <1KB
    - Cacheable (static data)
    """
    return {
        "languages": [
            {"code": "de", "name": "Deutsch", "flag": "🇩🇪"},
            {"code": "en", "name": "English", "flag": "🇬🇧"},
            {"code": "es", "name": "Español", "flag": "🇪🇸"}
        ]
    }
