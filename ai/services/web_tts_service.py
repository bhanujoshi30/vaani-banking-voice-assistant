"""
Web-based Text-to-Speech Service
Uses gTTS (Google Text-to-Speech) for free, local TTS without API keys
Supports Hindi and English with Indian accents
"""
import io
from typing import Optional
from gtts import gTTS
from config import settings
from utils import logger


class WebTTSService:
    """Service for web-based Text-to-Speech using gTTS"""
    
    def __init__(self):
        self.enabled = True  # Always enabled, no API keys needed
        logger.info("web_tts_initialized", message="Using gTTS for TTS")
    
    def get_language_code(self, language: str) -> str:
        """
        Get gTTS language code for language
        
        Args:
            language: Language code (en-IN, hi-IN, te-IN)
            
        Returns:
            gTTS language code
        """
        language_map = {
            "en-IN": "en",
            "hi-IN": "hi",
            "te-IN": "te",
            "en": "en",
            "hi": "hi",
            "te": "te",
        }
        return language_map.get(language, "en")
    
    async def synthesize_text(
        self,
        text: str,
        language: str = "en-IN",
        output_file: Optional[str] = None
    ) -> bytes:
        """
        Synthesize text to speech using gTTS
        
        Args:
            text: Text to synthesize
            language: Language code (en-IN, hi-IN, te-IN)
            output_file: Optional output file path (not used, returns bytes)
            
        Returns:
            Audio data as bytes (MP3 format)
        """
        try:
            # Get language code for gTTS
            lang_code = self.get_language_code(language)
            
            logger.info(
                "web_tts_request",
                text_length=len(text),
                language=language,
                lang_code=lang_code
            )
            
            # Create gTTS object
            tts = gTTS(text=text, lang=lang_code, slow=False)
            
            # Generate audio to bytes
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            audio_data = audio_buffer.read()
            
            logger.info(
                "web_tts_success",
                audio_size=len(audio_data),
                language=language
            )
            
            return audio_data
            
        except Exception as e:
            logger.error("web_tts_error", error=str(e), language=language)
            raise Exception(f"TTS failed: {e}")
    
    def is_available(self) -> bool:
        """Check if Web TTS is available (always True)"""
        return True


# Create singleton instance
_web_tts_service: Optional[WebTTSService] = None


def get_web_tts_service() -> WebTTSService:
    """Get singleton Web TTS service instance"""
    global _web_tts_service
    if _web_tts_service is None:
        _web_tts_service = WebTTSService()
    return _web_tts_service

