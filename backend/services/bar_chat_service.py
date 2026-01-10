"""
RAG Chat Service for Bar Ca l'Elena
Handles chat interactions with LLM (Ollama or Grok) and Elasticsearch RAG
"""
from typing import Dict, Any, List, Optional
import httpx
from backend.config import settings
from backend.services.bar_elasticsearch_service import bar_es_service
import logging

logger = logging.getLogger(__name__)


class BarChatService:
    """Service for handling chat with RAG"""

    def __init__(self):
        """Initialize chat service"""
        self.ollama_url = settings.OLLAMA_BASE_URL
        self.ollama_model = settings.OLLAMA_MODEL
        self.grok_api_key = settings.GROK_API_KEY

    async def chat(
        self,
        message: str,
        language: str = "en",
        llm_provider: str = "ollama",
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Process chat message with RAG

        Args:
            message: User's message
            language: Language code (ca, es, en, de, fr)
            llm_provider: "ollama" or "grok"
            conversation_history: Previous messages for context

        Returns:
            Dict with response, context, and metadata
        """
        try:
            # Step 1: Get relevant context from Elasticsearch
            context = bar_es_service.get_context_for_rag(message, language, limit=3)

            # Step 2: Build system prompt with context
            system_prompt = self._build_system_prompt(language, context)

            # Step 3: Get LLM response
            if llm_provider == "grok" and self.grok_api_key:
                response_text = await self._chat_with_grok(
                    message, system_prompt, conversation_history
                )
            else:
                response_text = await self._chat_with_ollama(
                    message, system_prompt, conversation_history
                )

            return {
                "response": response_text,
                "context_used": context,
                "language": language,
                "llm_provider": llm_provider,
                "success": True
            }

        except Exception as e:
            logger.error(f"❌ Error in chat: {e}")
            return {
                "response": self._get_error_message(language),
                "context_used": "",
                "language": language,
                "llm_provider": llm_provider,
                "success": False,
                "error": str(e)
            }

    def _build_system_prompt(self, language: str, context: str) -> str:
        """Build system prompt with RAG context"""
        prompts = {
            "ca": f"""Ets un assistent amable del Bar Ca l'Elena a Barcelona.
Utilitza la següent informació per respondre les preguntes dels clients:

{context}

Instruccions:
- Respon en català
- Sigues amable i professional
- Si no tens la informació, digues-ho educadament
- Utilitza el context proporcionat per donar respostes precises
- Pots recomanar plats, explicar horaris, i proporcionar informació general""",

            "es": f"""Eres un asistente amable del Bar Ca l'Elena en Barcelona.
Utiliza la siguiente información para responder las preguntas de los clientes:

{context}

Instrucciones:
- Responde en español
- Sé amable y profesional
- Si no tienes la información, dilo educadamente
- Utiliza el contexto proporcionado para dar respuestas precisas
- Puedes recomendar platos, explicar horarios y proporcionar información general""",

            "en": f"""You are a friendly assistant for Bar Ca l'Elena in Barcelona.
Use the following information to answer customer questions:

{context}

Instructions:
- Respond in English
- Be friendly and professional
- If you don't have the information, say so politely
- Use the provided context to give accurate answers
- You can recommend dishes, explain opening hours, and provide general information""",

            "de": f"""Du bist ein freundlicher Assistent für die Bar Ca l'Elena in Barcelona.
Nutze die folgenden Informationen, um Kundenfragen zu beantworten:

{context}

Anweisungen:
- Antworte auf Deutsch
- Sei freundlich und professionell
- Wenn du die Information nicht hast, sage es höflich
- Nutze den bereitgestellten Kontext für präzise Antworten
- Du kannst Gerichte empfehlen, Öffnungszeiten erklären und allgemeine Informationen geben""",

            "fr": f"""Vous êtes un assistant sympathique du Bar Ca l'Elena à Barcelone.
Utilisez les informations suivantes pour répondre aux questions des clients:

{context}

Instructions:
- Répondez en français
- Soyez aimable et professionnel
- Si vous n'avez pas l'information, dites-le poliment
- Utilisez le contexte fourni pour donner des réponses précises
- Vous pouvez recommander des plats, expliquer les horaires et fournir des informations générales"""
        }

        return prompts.get(language, prompts["en"])

    async def _chat_with_ollama(
        self,
        message: str,
        system_prompt: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Chat with Ollama LLM"""
        try:
            # Build messages
            messages = [{"role": "system", "content": system_prompt}]

            if conversation_history:
                messages.extend(conversation_history[-5:])  # Last 5 messages

            messages.append({"role": "user", "content": message})

            # Call Ollama API
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/chat",
                    json={
                        "model": self.ollama_model,
                        "messages": messages,
                        "stream": False
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    return data.get("message", {}).get("content", "")
                else:
                    logger.error(f"Ollama error: {response.status_code}")
                    return "Lo siento, hay un problema con el servicio de chat."

        except Exception as e:
            logger.error(f"Ollama chat error: {e}")
            raise

    async def _chat_with_grok(
        self,
        message: str,
        system_prompt: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Chat with Grok LLM"""
        try:
            # Build messages
            messages = [{"role": "system", "content": system_prompt}]

            if conversation_history:
                messages.extend(conversation_history[-5:])

            messages.append({"role": "user", "content": message})

            # Call Grok API (OpenAI-compatible)
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.grok_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "grok-beta",
                        "messages": messages,
                        "temperature": 0.7
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    return data.get("choices", [{}])[0].get("message", {}).get("content", "")
                else:
                    logger.error(f"Grok error: {response.status_code}")
                    return "Lo siento, hay un problema con el servicio de chat."

        except Exception as e:
            logger.error(f"Grok chat error: {e}")
            raise

    def _get_error_message(self, language: str) -> str:
        """Get error message in appropriate language"""
        messages = {
            "ca": "Ho sento, hi ha hagut un problema. Si us plau, torna-ho a intentar.",
            "es": "Lo siento, ha habido un problema. Por favor, inténtalo de nuevo.",
            "en": "Sorry, there was a problem. Please try again.",
            "de": "Entschuldigung, es gab ein Problem. Bitte versuchen Sie es erneut.",
            "fr": "Désolé, il y a eu un problème. Veuillez réessayer."
        }
        return messages.get(language, messages["en"])


# Global instance
bar_chat_service = BarChatService()
