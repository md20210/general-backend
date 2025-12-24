"""
Translation Service - Centralized multi-language support
Merges translations from all modules
"""
from typing import Dict, Optional, Literal

Language = Literal["de", "en", "es"]

# Import translation dictionaries from modules
from backend.translations.cv_matcher import CV_MATCHER_TRANSLATIONS
from backend.translations.homepage import HOMEPAGE_TRANSLATIONS
from backend.translations.privategxt import PRIVATEGXT_TRANSLATIONS
from backend.translations.prompts import LLM_PROMPTS


class TranslationService:
    """
    Centralized translation service for all applications.

    Features:
    - Modular translations (CV Matcher, Homepage, PrivateGxT)
    - Static UI translations (DE/EN/ES)
    - LLM prompt templates in multiple languages
    - Fallback to English if translation missing
    """

    def __init__(self):
        """Initialize translation service by merging all translation modules."""
        # Merge all UI translations
        self.UI_TRANSLATIONS: Dict[str, Dict[Language, str]] = {}
        self.UI_TRANSLATIONS.update(CV_MATCHER_TRANSLATIONS)
        self.UI_TRANSLATIONS.update(HOMEPAGE_TRANSLATIONS)
        self.UI_TRANSLATIONS.update(PRIVATEGXT_TRANSLATIONS)

        # LLM Prompts (separate from UI translations)
        self.LLM_PROMPTS: Dict[str, Dict[Language, str]] = LLM_PROMPTS

    def translate(self, key: str, language: Language = "de", **kwargs) -> str:
        """
        Get translation for a key in specified language.

        Args:
            key: Translation key (e.g., "app_title")
            language: Language code (de/en/es)
            **kwargs: Variables for string formatting (e.g., {count}, {error})

        Returns:
            Translated string with variables replaced

        Example:
            >>> service.translate("pdf_with_chat", "en", count=5)
            "with 5 chat messages"
        """
        # Try to get translation
        translation_dict = self.UI_TRANSLATIONS.get(key, {})

        # Get translation in requested language, fallback to English, then to key
        translation = translation_dict.get(
            language,
            translation_dict.get("en", key)
        )

        # Replace variables if provided
        if kwargs:
            try:
                translation = translation.format(**kwargs)
            except KeyError as e:
                # If a variable is missing, return the template with error
                return f"{translation} [missing variable: {e}]"

        return translation

    def get_prompt(self, prompt_key: str, language: Language = "de") -> Optional[str]:
        """
        Get LLM prompt template in specified language.

        Args:
            prompt_key: Prompt template key (e.g., "match_analysis")
            language: Language code (de/en/es)

        Returns:
            Prompt template string or None if not found
        """
        template = self.LLM_PROMPTS.get(prompt_key, {}).get(language)
        return template

    def get_all_translations(self, language: Language = "de") -> Dict[str, str]:
        """
        Get all UI translations for a specific language.

        Args:
            language: Language code (de/en/es)

        Returns:
            Dictionary with all translations for the language
        """
        return {
            key: translations.get(language, translations.get("en", key))
            for key, translations in self.UI_TRANSLATIONS.items()
        }

    def get_available_languages(self) -> list[str]:
        """
        Get list of available languages.

        Returns:
            List of language codes
        """
        return ["de", "en", "es"]


# Singleton instance
_translation_service = None


def get_translation_service() -> TranslationService:
    """
    Get singleton instance of TranslationService.

    Returns:
        TranslationService instance
    """
    global _translation_service
    if _translation_service is None:
        _translation_service = TranslationService()
    return _translation_service
