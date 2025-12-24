"""
Speech Service - Wiederverwendbare Speech-to-Text & Text-to-Speech Funktionalität.

Für alle Projekte nutzbar:
- LifeChronicle: Geschichten einsprechen
- CV Matcher: Dokumente vorlesen
- Andere: Beliebige Audio/Text-Verarbeitung
"""
from typing import Dict, Any, List, Optional
import base64
from io import BytesIO


class SpeechService:
    """
    Centralized speech processing service.

    NOTE: For DSGVO compliance, prefer browser-based APIs:
    - Speech-to-Text: Web Speech API (navigator.mediaDevices)
    - Text-to-Speech: SpeechSynthesis API (window.speechSynthesis)

    This service provides server-side fallbacks if needed.
    """

    def __init__(self):
        self.whisper_available = False
        self.tts_available = False
        self._check_dependencies()

    def _check_dependencies(self):
        """Check if Whisper/TTS libraries are available."""
        try:
            import whisper
            self.whisper_available = True
        except ImportError:
            print("⚠️ Whisper not installed. Speech-to-Text unavailable.")

        try:
            import pyttsx3
            self.tts_available = True
        except ImportError:
            print("⚠️ pyttsx3 not installed. Text-to-Speech unavailable.")

    async def transcribe(
        self,
        audio_bytes: bytes,
        language: str = "de"
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text using Whisper (local).

        Args:
            audio_bytes: Audio file bytes (MP3, WAV, etc.)
            language: Language code (de, en, es)

        Returns:
            {
                'text': str,
                'language': str,
                'confidence': float
            }

        Raises:
            RuntimeError: If Whisper not available
            ValueError: If audio format invalid
        """
        if not self.whisper_available:
            raise RuntimeError(
                "Whisper not installed. "
                "Use browser Web Speech API for client-side transcription."
            )

        try:
            import whisper
            import tempfile

            # Save audio to temp file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_file.write(audio_bytes)
                temp_path = temp_file.name

            # Load Whisper model (small for speed)
            model = whisper.load_model("small")

            # Transcribe
            result = model.transcribe(
                temp_path,
                language=language,
                fp16=False  # CPU compatible
            )

            return {
                'text': result['text'].strip(),
                'language': result.get('language', language),
                'confidence': 0.95  # Whisper doesn't provide per-word confidence
            }

        except Exception as e:
            raise ValueError(f"Transcription failed: {str(e)}")

    async def synthesize(
        self,
        text: str,
        language: str = "de-DE",
        voice: Optional[str] = None,
        speed: float = 1.0
    ) -> Dict[str, Any]:
        """
        Synthesize text to speech.

        RECOMMENDED: Use browser SpeechSynthesis API instead!
        This is a server-side fallback.

        Args:
            text: Text to speak
            language: Language code (de-DE, en-US, es-ES)
            voice: Voice name (optional)
            speed: Speech rate (0.5 - 2.0)

        Returns:
            {
                'audio_url': str,  # Base64 data URL or file path
                'duration': float  # seconds
            }

        Browser Example (preferred):
            ```javascript
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'de-DE';
            utterance.rate = 1.0;
            window.speechSynthesis.speak(utterance);
            ```
        """
        if not self.tts_available:
            raise RuntimeError(
                "TTS not installed. "
                "Use browser SpeechSynthesis API for client-side TTS."
            )

        try:
            import pyttsx3

            engine = pyttsx3.init()
            engine.setProperty('rate', 150 * speed)  # Words per minute

            # Save to temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_path = temp_file.name

            engine.save_to_file(text, temp_path)
            engine.runAndWait()

            # Read file and convert to base64
            with open(temp_path, 'rb') as f:
                audio_bytes = f.read()

            audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
            audio_url = f"data:audio/mp3;base64,{audio_b64}"

            # Estimate duration (rough: 150 words per minute)
            word_count = len(text.split())
            duration = (word_count / 150) * 60 / speed

            return {
                'audio_url': audio_url,
                'duration': duration
            }

        except Exception as e:
            raise ValueError(f"Synthesis failed: {str(e)}")

    def get_voices(self) -> List[Dict[str, Any]]:
        """
        Get available TTS voices.

        Returns list of voices grouped by language.

        Browser Example (preferred):
            ```javascript
            const voices = window.speechSynthesis.getVoices();
            const germanVoices = voices.filter(v => v.lang.startsWith('de'));
            ```
        """
        voices = [
            {
                "name": "Browser Default",
                "language": "de-DE",
                "description": "Use browser SpeechSynthesis API for best results"
            },
            {
                "name": "Browser Default",
                "language": "en-US",
                "description": "Use browser SpeechSynthesis API for best results"
            },
            {
                "name": "Browser Default",
                "language": "es-ES",
                "description": "Use browser SpeechSynthesis API for best results"
            }
        ]

        if self.tts_available:
            try:
                import pyttsx3
                engine = pyttsx3.init()
                for voice in engine.getProperty('voices'):
                    voices.append({
                        "name": voice.name,
                        "language": voice.languages[0] if voice.languages else "unknown",
                        "description": f"Server-side TTS: {voice.id}"
                    })
            except:
                pass

        return voices


# Global instance
speech_service = SpeechService()
