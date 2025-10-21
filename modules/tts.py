import os
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any
import torch
from TTS.api import TTS
from pydub import AudioSegment
import structlog

logger = structlog.get_logger()

class TTSBase:
    """Base class for TTS engines"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.device = config.get("device", "cpu")
        self.model_name = config.get("model_name")
        self.tts = None

    def initialize(self) -> None:
        """Initialize the TTS model"""
        raise NotImplementedError

    def generate_speech(self, text: str, language: str, speaker: Optional[str] = None,
                       speaker_wav: Optional[str] = None) -> str:
        """Generate speech and return file path"""
        raise NotImplementedError

    def get_voices(self) -> List[str]:
        """Get list of available voices"""
        raise NotImplementedError

    def get_languages(self) -> List[str]:
        """Get list of supported languages"""
        raise NotImplementedError

    def convert_format(self, input_path: str, output_format: str) -> str:
        """Convert audio format if needed"""
        if output_format.lower() == "wav":
            return input_path

        output_path = input_path.replace(".wav", f".{output_format}")
        audio = AudioSegment.from_wav(input_path)
        audio.export(output_path, format=output_format)
        os.remove(input_path)  # Clean up original wav
        return output_path


class CoquiXTTS(TTSBase):
    """Coqui xTTS v2 implementation"""

    SUPPORTED_LANGUAGES = [
        "en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar",
        "zh-cn", "ja", "hu", "ko", "hi"
    ]

    def initialize(self) -> None:
        if self.tts is None:
            logger.info("Initializing Coqui xTTS model", model=self.model_name, device=self.device)
            self.tts = TTS(self.model_name).to(self.device)
            logger.info("Model initialized successfully")

    def generate_speech(self, text: str, language: str, speaker: Optional[str] = None,
                       speaker_wav: Optional[str] = None) -> str:
        self.initialize()

        # Create output directory if not exists
        output_dir = Path(self.config.get("output_dir", "outputs"))
        output_dir.mkdir(exist_ok=True)

        # Generate unique filename
        import uuid
        filename = f"tts_{uuid.uuid4().hex}.wav"
        output_path = output_dir / filename

        logger.info("Generating speech", text_length=len(text), language=language, speaker=speaker)

        try:
            if speaker_wav:
                # Voice cloning with reference audio
                self.tts.tts_to_file(text=text, language=language, file_path=str(output_path),
                                   speaker_wav=speaker_wav)
            else:
                # Use predefined speaker
                speaker = speaker or self.config.get("default_speaker", "Daisy Studious")
                self.tts.tts_to_file(text=text, language=language, file_path=str(output_path),
                                   speaker=speaker)

            logger.info("Speech generated successfully", output_path=str(output_path))
            return str(output_path)

        except Exception as e:
            logger.error("Failed to generate speech", error=str(e))
            raise

    def get_voices(self) -> List[str]:
        self.initialize()
        return self.tts.speakers

    def get_languages(self) -> List[str]:
        return self.SUPPORTED_LANGUAGES


class TTSEngine:
    """Factory for TTS engines"""

    ENGINES = {
        "coqui_xtts": CoquiXTTS,
    }

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.engine_name = config.get("tts_engine", "coqui_xtts")
        self.engine = None

    def get_engine(self) -> TTSBase:
        if self.engine is None:
            engine_class = self.ENGINES.get(self.engine_name)
            if not engine_class:
                raise ValueError(f"Unsupported TTS engine: {self.engine_name}")
            self.engine = engine_class(self.config)
        return self.engine
