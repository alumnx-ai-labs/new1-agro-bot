# agents/stt_agent.py
import logging
import base64
import tempfile
import os
from typing import Dict, Any, Optional
from google.cloud import speech

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class STTAgent:
    """
    Speech-to-Text agent for transcribing audio files
    """
    
    def __init__(self):
        self.client = speech.SpeechClient()
        
        # Language code mapping for common languages
        self.language_codes = {
            'english': 'en-IN',
            'hindi': 'hi-IN',
            'bengali': 'bn-IN',
            'tamil': 'ta-IN',
            'telugu': 'te-IN',
            'marathi': 'mr-IN',
            'gujarati': 'gu-IN',
            'kannada': 'kn-IN',
            'malayalam': 'ml-IN',
            'punjabi': 'pa-IN',
            'urdu': 'ur-IN'
        }
        
        logger.info("STTAgent initialized")
    
    def transcribe_audio(self, audio_data: str, language: str = 'english') -> Dict[str, Any]:
        """
        Transcribe audio data to text
        
        Args:
            audio_data: Base64 encoded audio data
            language: Language for transcription (default: english)
            
        Returns:
            Dict with transcription results
        """
        
        try:
            # Get language code
            language_code = self.language_codes.get(language.lower(), 'en-IN')
            logger.info(f"Transcribing audio in language: {language} ({language_code})")
            
            # Decode base64 audio data
            audio_bytes = base64.b64decode(audio_data)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name
            
            try:
                # Read audio file
                with open(temp_file_path, 'rb') as audio_file:
                    content = audio_file.read()
                
                # Configure recognition
                audio = speech.RecognitionAudio(content=content)
                config = speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                    sample_rate_hertz=48000,  # Common for web audio
                    language_code=language_code,
                    alternative_language_codes=['en-IN'] if language_code != 'en-IN' else [],
                    enable_automatic_punctuation=True,
                    model='latest_long'
                )
                
                # Perform transcription
                response = self.client.recognize(config=config, audio=audio)
                
                # Process results
                if response.results:
                    transcript = response.results[0].alternatives[0].transcript
                    confidence = response.results[0].alternatives[0].confidence
                    
                    logger.info(f"Transcription successful: {transcript[:50]}...")
                    
                    return {
                        'success': True,
                        'transcript': transcript,
                        'confidence': confidence,
                        'language': language,
                        'language_code': language_code,
                        'agent': 'stt_agent'
                    }
                else:
                    logger.warning("No transcription results")
                    return {
                        'success': False,
                        'error': 'No speech detected in audio',
                        'transcript': '',
                        'language': language,
                        'agent': 'stt_agent'
                    }
                    
            finally:
                # Clean up temp file
                os.unlink(temp_file_path)
                
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'transcript': '',
                'language': language,
                'agent': 'stt_agent'
            }
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return self.language_codes