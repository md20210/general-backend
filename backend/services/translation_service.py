"""
Translation Service - Backward compatibility wrapper
Imports from new modular translation structure
"""
from backend.translations import TranslationService, Language

# Export for backward compatibility
__all__ = ["TranslationService", "Language"]
