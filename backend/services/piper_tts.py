"""
Piper Text-to-Speech Service
Converts text to speech using Piper TTS for Vietnamese and English
"""

import os
import tempfile
import wave
import logging
from typing import Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class PiperTTS:
    def __init__(self):
        self.voice_models = {
            "vi": "vi_VN-vais1000-medium.onnx",      # Vietnamese voice
            "en": "en_US-lessac-medium.onnx"         # English voice
        }
        self.models_dir = Path("backend/models/piper")
        self.voice_instances = {}
        
        # Initialize voice models
        self._load_voice_models()
    
    def _load_voice_models(self):
        """Load Piper voice models"""
        try:
            from piper import PiperVoice
            
            for lang, model_file in self.voice_models.items():
                model_path = self.models_dir / model_file
                if model_path.exists():
                    try:
                        self.voice_instances[lang] = PiperVoice.load(str(model_path))
                        logger.info(f"✅ Loaded {lang} voice model: {model_file}")
                    except Exception as e:
                        logger.warning(f"⚠️ Could not load {lang} voice model: {e}")
                else:
                    logger.warning(f"⚠️ Voice model not found: {model_path}")
                    
        except ImportError:
            logger.warning("⚠️ Piper TTS not available. Install with: pip install piper-tts")
            self.voice_instances = {}
    
    def synthesize_speech(self, text: str, language: str = "vi") -> Optional[bytes]:
        """
        Convert text to speech audio data
        
        Args:
            text: Text to convert to speech
            language: Language code ("vi" or "en")
            
        Returns:
            Audio data as bytes (WAV format) or None if failed
        """
        if not text or not text.strip():
            return None
            
        if language not in self.voice_instances:
            logger.warning(f"⚠️ Voice model for {language} not available")
            return None
            
        try:
            voice = self.voice_instances[language]
            
            # Create temporary file for audio output
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Synthesize speech to WAV file
            with wave.open(temp_path, "wb") as wav_file:
                voice.synthesize(text, wav_file)
            
            # Read audio data
            with open(temp_path, "rb") as audio_file:
                audio_data = audio_file.read()
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            logger.info(f"✅ Generated speech for {len(text)} characters in {language}")
            return audio_data
            
        except Exception as e:
            logger.error(f"❌ Error synthesizing speech: {e}")
            return None
    
    def get_available_languages(self) -> list:
        """Get list of available languages"""
        return list(self.voice_instances.keys())
    
    def is_available(self) -> bool:
        """Check if Piper TTS is available"""
        return len(self.voice_instances) > 0

# Global instance
piper_tts = PiperTTS()
