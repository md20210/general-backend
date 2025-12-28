"""LLM Gateway Service - Multi-provider LLM integration."""
import requests
import json
import re
from typing import Dict, List, Optional, Any
from openai import OpenAI
from anthropic import Anthropic

from backend.config import settings


class LLMGateway:
    """Gateway for multiple LLM providers (Ollama, GROK, Anthropic)."""

    def __init__(self):
        """Initialize LLM Gateway with API clients."""
        self.ollama_base_url = settings.OLLAMA_BASE_URL
        self.grok_api_key = settings.GROK_API_KEY
        self.anthropic_api_key = settings.ANTHROPIC_API_KEY

        # Initialize clients
        self._grok_client = None
        self._anthropic_client = None

    @property
    def grok_client(self) -> OpenAI:
        """Lazy-load GROK client."""
        if self._grok_client is None and self.grok_api_key:
            self._grok_client = OpenAI(
                api_key=self.grok_api_key,
                base_url="https://api.x.ai/v1"
            )
        return self._grok_client

    @property
    def anthropic_client(self) -> Anthropic:
        """Lazy-load Anthropic client."""
        if self._anthropic_client is None and self.anthropic_api_key:
            self._anthropic_client = Anthropic(api_key=self.anthropic_api_key)
        return self._anthropic_client

    def generate(
        self,
        prompt: str,
        provider: str = "ollama",
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        timeout: int = 120,
    ) -> Dict[str, Any]:
        """
        Generate text using specified LLM provider.

        Args:
            prompt: Text prompt for the LLM
            provider: "ollama", "grok", or "anthropic"
            model: Model name (provider-specific)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds

        Returns:
            Dict with response, model, provider, usage info
        """
        provider = provider.lower()

        if provider == "ollama":
            return self._generate_ollama(prompt, model, temperature, max_tokens, timeout)
        elif provider == "grok":
            return self._generate_grok(prompt, model, temperature, max_tokens, timeout)
        elif provider == "anthropic":
            return self._generate_anthropic(prompt, model, temperature, max_tokens, timeout)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _generate_ollama(
        self,
        prompt: str,
        model: Optional[str],
        temperature: float,
        max_tokens: int,
        timeout: int,
    ) -> Dict[str, Any]:
        """Generate text using Ollama."""
        model = model or "qwen2.5:3b"

        response = requests.post(
            f"{self.ollama_base_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            },
            timeout=timeout
        )

        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.status_code} - {response.text}")

        response_json = response.json()
        text = response_json.get("response", response_json.get("text", str(response_json)))

        return {
            "response": text,
            "provider": "ollama",
            "model": model,
            "usage": {
                "prompt_tokens": response_json.get("prompt_eval_count", 0),
                "completion_tokens": response_json.get("eval_count", 0),
                "total_tokens": response_json.get("prompt_eval_count", 0) + response_json.get("eval_count", 0),
            }
        }

    def _generate_grok(
        self,
        prompt: str,
        model: Optional[str],
        temperature: float,
        max_tokens: int,
        timeout: int,
    ) -> Dict[str, Any]:
        """Generate text using GROK."""
        if not self.grok_api_key:
            raise ValueError(f"GROK API key not configured. Key value: '{self.grok_api_key}', length: {len(self.grok_api_key) if self.grok_api_key else 0}")

        if not self.grok_client:
            raise ValueError(f"GROK client failed to initialize. API key length: {len(self.grok_api_key)}")

        model = model or "grok-2-latest"

        completion = self.grok_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
        )

        return {
            "response": completion.choices[0].message.content,
            "provider": "grok",
            "model": model,
            "usage": {
                "prompt_tokens": completion.usage.prompt_tokens,
                "completion_tokens": completion.usage.completion_tokens,
                "total_tokens": completion.usage.total_tokens,
            }
        }

    def _generate_anthropic(
        self,
        prompt: str,
        model: Optional[str],
        temperature: float,
        max_tokens: int,
        timeout: int,
    ) -> Dict[str, Any]:
        """Generate text using Anthropic Claude."""
        if not self.anthropic_client:
            raise ValueError("Anthropic API key not configured")

        model = model or "claude-3-5-sonnet-20241022"

        message = self.anthropic_client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
            timeout=timeout,
        )

        return {
            "response": message.content[0].text,
            "provider": "anthropic",
            "model": model,
            "usage": {
                "prompt_tokens": message.usage.input_tokens,
                "completion_tokens": message.usage.output_tokens,
                "total_tokens": message.usage.input_tokens + message.usage.output_tokens,
            }
        }

    def list_models(self, provider: Optional[str] = None) -> List[Dict[str, str]]:
        """
        List available models.

        Args:
            provider: Optional provider filter ("ollama", "grok", "anthropic")

        Returns:
            List of dicts with name, provider, description
        """
        models = []

        # Ollama models
        if provider is None or provider == "ollama":
            try:
                response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    ollama_models = response.json().get("models", [])
                    for model in ollama_models:
                        models.append({
                            "name": model["name"],
                            "provider": "ollama",
                            "description": f"Local Ollama model - {model.get('size', 'unknown size')}"
                        })
            except Exception as e:
                print(f"Warning: Could not fetch Ollama models: {e}")

        # GROK models
        if provider is None or provider == "grok":
            if self.grok_api_key:
                models.extend([
                    {
                        "name": "grok-beta",
                        "provider": "grok",
                        "description": "GROK Beta - X.AI's frontier model"
                    },
                    {
                        "name": "grok-vision-beta",
                        "provider": "grok",
                        "description": "GROK Vision Beta - Multimodal model"
                    }
                ])

        # Anthropic models
        if provider is None or provider == "anthropic":
            if self.anthropic_api_key:
                models.extend([
                    {
                        "name": "claude-3-5-sonnet-20241022",
                        "provider": "anthropic",
                        "description": "Claude 3.5 Sonnet - Most intelligent model"
                    },
                    {
                        "name": "claude-3-opus-20240229",
                        "provider": "anthropic",
                        "description": "Claude 3 Opus - Powerful model"
                    },
                    {
                        "name": "claude-3-haiku-20240307",
                        "provider": "anthropic",
                        "description": "Claude 3 Haiku - Fast and efficient"
                    }
                ])

        return models

    def embed(self, text: str, model: Optional[str] = None) -> List[float]:
        """
        Generate embeddings for text (using Ollama).

        Args:
            text: Text to embed
            model: Embedding model name (default: nomic-embed-text)

        Returns:
            List of floats representing the embedding
        """
        model = model or "nomic-embed-text"

        response = requests.post(
            f"{self.ollama_base_url}/api/embeddings",
            json={
                "model": model,
                "prompt": text
            },
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"Ollama embeddings error: {response.status_code} - {response.text}")

        return response.json().get("embedding", [])

    @staticmethod
    def parse_json_response(text: str) -> dict:
        """
        Extract and parse JSON from LLM response with robust error handling.
        Adapted from CV Matcher's proven implementation.

        Args:
            text: LLM response text potentially containing JSON

        Returns:
            Parsed JSON dict

        Raises:
            ValueError: If JSON cannot be parsed
        """
        try:
            # Extract JSON from markdown code blocks
            if "```json" in text:
                start = text.find("```json") + 7
                end = text.find("```", start)
                text = text[start:end]
            elif "```" in text:
                start = text.find("```") + 3
                end = text.find("```", start)
                text = text[start:end]

            # Clean up
            text = text.strip()

            # Remove trailing commas
            text = re.sub(r',(\s*[}\]])', r'\1', text)

            # Find first complete JSON object
            brace_count = 0
            json_end = -1
            for i, char in enumerate(text):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        json_end = i + 1
                        break

            if json_end > 0 and json_end < len(text):
                text = text[:json_end]

            # Parse JSON
            result = json.loads(text)

            # Fix common LLM mistakes: Convert object arrays to string arrays
            for field in ["strengths", "gaps", "recommendations"]:
                if field in result and isinstance(result[field], list):
                    result[field] = [
                        item["name"] if isinstance(item, dict) and "name" in item else str(item)
                        for item in result[field]
                    ]

            return result

        except json.JSONDecodeError as e:
            # Try to repair common JSON errors
            repaired = re.sub(r',(\s*[}\]])', r'\1', text)
            repaired = re.sub(r'"\s*\n\s*"', '",\n    "', repaired)
            repaired = re.sub(r'"\s*\n\s*"(\w+)":', '",\n    "\\1":', repaired)
            repaired = re.sub(r'(\d)\s*\n\s*"', '\\1,\n    "', repaired)
            repaired = re.sub(r'\}\s*\n\s*"', '},\n    "', repaired)
            repaired = re.sub(r'\]\s*\n\s*"', '],\n    "', repaired)

            try:
                result = json.loads(repaired)

                # Apply fixes for object arrays
                for field in ["strengths", "gaps", "recommendations"]:
                    if field in result and isinstance(result[field], list):
                        result[field] = [
                            item["name"] if isinstance(item, dict) and "name" in item else str(item)
                            for item in result[field]
                        ]

                return result
            except:
                raise ValueError(f"Failed to parse JSON response: {e.msg} at position {e.pos}") from e

        except Exception as e:
            raise ValueError(f"Failed to extract JSON from response: {str(e)}") from e


# Global instance
llm_gateway = LLMGateway()
