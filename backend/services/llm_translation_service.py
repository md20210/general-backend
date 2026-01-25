"""
LLM Translation Service using Ollama/Grok
Translates dish names to all supported languages
"""
import httpx
import json
import os
from typing import Dict, Optional
from backend.models.bar import BarSettings
from sqlalchemy.orm import Session


class LLMTranslationService:
    """Service for translating text using LLM"""

    SUPPORTED_LANGUAGES = {
        'ca': 'Catalan',
        'es': 'Spanish',
        'en': 'English',
        'de': 'German',
        'fr': 'French'
    }

    @staticmethod
    async def translate_dish_name(
        db: Session,
        dish_name: str,
        source_language: str
    ) -> Dict[str, str]:
        """
        Translate a dish name from source language to all supported languages

        Args:
            db: Database session
            dish_name: The dish name to translate
            source_language: The source language code (ca/es/en/de/fr)

        Returns:
            Dict with all language translations: {'ca': '...', 'es': '...', ...}
        """
        # Get LLM settings
        settings = db.query(BarSettings).first()
        if not settings:
            settings = BarSettings()

        llm_provider = settings.llm_provider or 'ollama'

        # Create translation prompt
        source_lang_name = LLMTranslationService.SUPPORTED_LANGUAGES.get(source_language, 'Spanish')

        prompt = f"""You are a professional translator specializing in restaurant menus.

Translate the following dish name from {source_lang_name} to Catalan, Spanish, English, German, and French.

Dish name: "{dish_name}"

Provide ONLY a JSON response in this exact format (no additional text):
{{
  "ca": "Catalan translation",
  "es": "Spanish translation",
  "en": "English translation",
  "de": "German translation",
  "fr": "French translation"
}}

Important:
- Keep the original name in the source language unchanged
- Use appropriate culinary terminology for each language
- Maintain the essence and style of the dish name
- Return ONLY the JSON object, no explanations"""

        try:
            if llm_provider == 'grok':
                # Use environment variable GROK_API_KEY or fall back to database setting
                api_key = os.getenv('GROK_API_KEY') or settings.grok_api_key
                translations = await LLMTranslationService._translate_with_grok(
                    prompt,
                    api_key
                )
            else:
                translations = await LLMTranslationService._translate_with_ollama(
                    prompt,
                    settings.ollama_model or 'llama3.2:3b'
                )

            return translations

        except Exception as e:
            print(f"Translation error: {e}")
            # Fallback: return original name for all languages
            return {lang: dish_name for lang in LLMTranslationService.SUPPORTED_LANGUAGES.keys()}

    @staticmethod
    async def _translate_with_ollama(prompt: str, model: str) -> Dict[str, str]:
        """Translate using Ollama"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': model,
                    'prompt': prompt,
                    'stream': False,
                    'format': 'json'
                }
            )

            result = response.json()
            response_text = result.get('response', '{}')

            # Parse JSON response
            try:
                translations = json.loads(response_text)
                return translations
            except json.JSONDecodeError:
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))
                raise ValueError("Could not parse JSON from LLM response")

    @staticmethod
    async def _translate_with_grok(prompt: str, api_key: Optional[str]) -> Dict[str, str]:
        """Translate using Grok"""
        if not api_key:
            raise ValueError("Grok API key not configured")

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                'https://api.x.ai/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'grok-4-1-fast',
                    'messages': [
                        {'role': 'user', 'content': prompt}
                    ],
                    'response_format': {'type': 'json_object'}
                }
            )

            result = response.json()
            content = result['choices'][0]['message']['content']

            # Parse JSON response
            translations = json.loads(content)
            return translations
