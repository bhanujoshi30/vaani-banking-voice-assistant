"""
Azure Text-to-Speech Service
Provides high-quality TTS for Hindi and English with Indian voices
"""
import asyncio
from typing import Optional

# Conditional import - Azure SDK not available in Vercel deployment
try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
    speechsdk = None

from config import settings
from utils import logger, AzureTTSError


class AzureTTSService:
    """Service for Azure Text-to-Speech"""
    
    def __init__(self):
        if speechsdk is None:
            raise ImportError("azure-cognitiveservices-speech is not installed")
        
        self.enabled = settings.azure_tts_enabled
        self.speech_config = None
        
        if self.enabled:
            if not settings.azure_tts_key or not settings.azure_tts_region:
                logger.warning("Azure TTS enabled but credentials missing")
                self.enabled = False
            else:
                self.speech_config = speechsdk.SpeechConfig(
                    subscription=settings.azure_tts_key,
                    region=settings.azure_tts_region
                )
                logger.info(
                    "azure_tts_initialized",
                    region=settings.azure_tts_region
                )
        else:
            logger.info("azure_tts_disabled", message="Using Web Speech API fallback")
    
    def get_voice_name(self, language: str) -> str:
        """
        Get Azure voice name for language
        
        Args:
            language: Language code (en-IN, hi-IN, te-IN)
            
        Returns:
            Azure voice name
        """
        return settings.voice_config.get(language, "en-IN-NeerjaNeural")
    
    async def synthesize_text(
        self,
        text: str,
        language: str = "en-IN",
        output_file: Optional[str] = None
    ) -> bytes:
        """
        Synthesize text to speech
        
        Args:
            text: Text to synthesize
            language: Language code
            output_file: Optional output file path
            
        Returns:
            Audio data as bytes
            
        Raises:
            AzureTTSError: If synthesis fails
        """
        if not self.enabled:
            raise AzureTTSError("Azure TTS is not enabled")
        
        try:
            voice_name = self.get_voice_name(language)
            self.speech_config.speech_synthesis_voice_name = voice_name
            
            # Use in-memory stream if no output file
            if output_file:
                audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file)
            else:
                audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=False)
            
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            # Synthesize in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                synthesizer.speak_text,
                text
            )
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                logger.info(
                    "azure_tts_success",
                    text_length=len(text),
                    language=language,
                    voice=voice_name
                )
                return result.audio_data
                
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                logger.error(
                    "azure_tts_canceled",
                    reason=cancellation.reason,
                    error_details=cancellation.error_details
                )
                raise AzureTTSError(f"Speech synthesis canceled: {cancellation.error_details}")
            
            else:
                raise AzureTTSError(f"Unexpected result: {result.reason}")
                
        except AzureTTSError:
            raise
        except Exception as e:
            logger.error("azure_tts_error", error=str(e))
            raise AzureTTSError(f"TTS failed: {e}")
    
    async def synthesize_ssml(
        self,
        ssml: str,
        output_file: Optional[str] = None
    ) -> bytes:
        """
        Synthesize SSML to speech
        
        Args:
            ssml: SSML markup
            output_file: Optional output file path
            
        Returns:
            Audio data as bytes
        """
        if not self.enabled:
            raise AzureTTSError("Azure TTS is not enabled")
        
        try:
            if output_file:
                audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file)
            else:
                audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=False)
            
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                synthesizer.speak_ssml,
                ssml
            )
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                logger.info("azure_tts_ssml_success")
                return result.audio_data
            else:
                raise AzureTTSError(f"SSML synthesis failed: {result.reason}")
                
        except Exception as e:
            logger.error("azure_tts_ssml_error", error=str(e))
            raise AzureTTSError(f"SSML TTS failed: {e}")
    
    def is_available(self) -> bool:
        """Check if Azure TTS is available"""
        return self.enabled


# Create singleton instance
_azure_tts_service: Optional[AzureTTSService] = None


def get_azure_tts_service() -> AzureTTSService:
    """Get or create Azure TTS service instance"""
    global _azure_tts_service
    if _azure_tts_service is None:
        _azure_tts_service = AzureTTSService()
    return _azure_tts_service
