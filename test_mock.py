#!/usr/bin/env python3
"""Mock test for TTS API to debug without PyTorch"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import structlog

# Mock TTS classes
class MockTTS:
    def __init__(self):
        self.speakers = [
            "Claribel Dervla", "Daisy Studious", "Gracie Wise", "Tammie Ema", "Ana Florence"
        ]

    def tts_to_file(self, text, language, file_path, speaker=None, speaker_wav=None):
        # Create a dummy file
        with open(file_path, 'w') as f:
            f.write(f"Mock audio file for: {text[:50]}...")
        return file_path

class TTSBase:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.tts = None

    def initialize(self) -> None:
        if self.tts is None:
            self.tts = MockTTS()

    def generate_speech(self, text: str, language: str, speaker: Optional[str] = None,
                       speaker_wav: Optional[str] = None) -> str:
        self.initialize()

        output_dir = Path(self.config.get("output_dir", "outputs"))
        output_dir.mkdir(exist_ok=True)

        import uuid
        filename = f"tts_{uuid.uuid4().hex}.wav"
        output_path = output_dir / filename

        try:
            if speaker_wav:
                self.tts.tts_to_file(text=text, language=language, file_path=str(output_path),
                                   speaker_wav=speaker_wav)
            else:
                speaker = speaker or self.config.get("default_speaker", "Daisy Studious")
                self.tts.tts_to_file(text=text, language=language, file_path=str(output_path),
                                   speaker=speaker)

            return str(output_path)

        except Exception as e:
            raise

    def get_voices(self) -> List[str]:
        self.initialize()
        return self.tts.speakers

    def get_languages(self) -> List[str]:
        return ["en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh-cn", "ja", "hu", "ko", "hi"]

class TTSEngine:
    ENGINES = {
        "coqui_xtts": TTSBase,
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

# Mock FastAPI test
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from datetime import datetime

app = FastAPI()

# Mock TTS
config_dict = {
    "tts_engine": "coqui_xtts",
    "model_name": "tts_models/multilingual/multi-dataset/xtts_v2",
    "device": "cpu",
    "output_dir": "outputs",
    "default_speaker": "Daisy Studious",
}
tts_engine = TTSEngine(config_dict)
tts = tts_engine.get_engine()

@app.post("/tts")
async def text_to_speech(
    speaker_wav: UploadFile = File(None),
    text: str = Form(...),
    language: str = Form("en"),
    speaker: Optional[str] = Form(None),
    output_format: str = Form("mp3"),
):
    try:
        speaker_wav_path = None
        if speaker_wav and speaker_wav.filename:
            temp_dir = Path("outputs") / "temp"
            temp_dir.mkdir(exist_ok=True)

            import uuid
            temp_filename = f"reference_{uuid.uuid4().hex()}.wav"
            speaker_wav_path = temp_dir / temp_filename

            with open(speaker_wav_path, "wb") as f:
                content = await speaker_wav.read()
                f.write(content)

        # Generate speech
        audio_path = tts.generate_speech(
            text=text,
            language=language,
            speaker=speaker,
            speaker_wav=str(speaker_wav_path) if speaker_wav_path else None
        )

        # Clean up temp file
        if speaker_wav_path and speaker_wav_path.exists():
            os.remove(speaker_wav_path)

        # Generate filename with timestamp and speaker (no spaces)
        speaker_name = (speaker or "default").replace(" ", "_")
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"{timestamp}_{speaker_name}.{output_format}"

        return FileResponse(
            path=audio_path,
            media_type=f"audio/{output_format}",
            filename=filename
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "engine": "mock", "device": "cpu"}

@app.get("/voices-select")
async def get_voices_for_select():
    voices = ["Claribel Dervla", "Daisy Studious", "Gracie Wise", "Tammie Ema", "Ana Florence"]
    return {"voices": voices}

if __name__ == "__main__":
    import uvicorn
    print("Starting mock TTS API server...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
