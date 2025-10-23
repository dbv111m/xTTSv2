import os
from pathlib import Path
from typing import Optional, List
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
import structlog

from config import (
    HOST, PORT, DEBUG, TTS_ENGINE, MODEL_NAME, DEVICE, OUTPUT_DIR,
    DEFAULT_LANGUAGE, DEFAULT_SPEAKER, DEFAULT_FORMAT, API_KEY
)
from modules.tts import TTSEngine
from modules.utils import validate_language, validate_file_exists, cleanup_old_files

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Initialize TTS engine
config_dict = {
    "tts_engine": TTS_ENGINE,
    "model_name": MODEL_NAME,
    "device": DEVICE,
    "output_dir": OUTPUT_DIR,
    "default_speaker": DEFAULT_SPEAKER,
}
tts_engine = TTSEngine(config_dict)
tts = tts_engine.get_engine()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    try:
        tts.initialize()
        logger.info("TTS engine initialized successfully")
        # Cache voices for UI
        global available_voices
        available_voices = tts.get_voices()
        logger.info(f"Cached {len(available_voices)} voices")
    except Exception as e:
        logger.error("Failed to initialize TTS engine", error=str(e))
        raise

    yield

    # Shutdown
    logger.info("Shutting down TTS API")

app = FastAPI(
    title="TTS API",
    description="Universal Text-to-Speech API",
    version="1.0.0",
    lifespan=lifespan
)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Serve static files (HTML client)
app.mount("/static", StaticFiles(directory=".", html=True), name="static")

@app.get("/")
async def read_root():
    """Serve the main HTML client"""
    return FileResponse("index.html", media_type="text/html")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "engine": TTS_ENGINE, "device": DEVICE}

@app.get("/voices")
async def get_voices():
    """Get list of available voices"""
    try:
        voices = tts.get_voices()
        return {"voices": voices}
    except Exception as e:
        logger.error("Failed to get voices", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve voices")

@app.get("/voices-select")
async def get_voices_for_select():
    """Get voices formatted for HTML select options"""
    try:
        voices = available_voices if available_voices else tts.get_voices()
        return {"voices": voices}
    except Exception as e:
        logger.error("Failed to get voices for select", error=str(e))
        return {"voices": []}

@app.get("/languages")
async def get_languages():
    """Get list of supported languages"""
    try:
        languages = tts.get_languages()
        return {"languages": languages}
    except Exception as e:
        logger.error("Failed to get languages", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve languages")

@app.post("/tts")
async def text_to_speech(
    text: str = Form(..., description="Text to convert to speech"),
    language: str = Form(DEFAULT_LANGUAGE, description="Language code"),
    speaker: Optional[str] = Form(None, description="Speaker name for predefined voices"),
    speaker_wav: Optional[str] = Form(None, description="Path to reference audio file for voice cloning"),
    output_format: str = Form(DEFAULT_FORMAT, description="Output format: wav or mp3"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Generate speech from text"""
    try:
        # Validate inputs
        supported_languages = tts.get_languages()
        if not validate_language(language, supported_languages):
            raise HTTPException(status_code=400, detail=f"Unsupported language: {language}")

        speaker_wav_path = None
        if speaker_wav:
            # Save uploaded file temporarily
            temp_dir = Path(OUTPUT_DIR) / "temp"
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

        # Convert format if needed
        if output_format.lower() != "wav":
            audio_path = tts.convert_format(audio_path, output_format)

        # Generate filename with timestamp and speaker
        from datetime import datetime
        speaker_name = speaker or "default"
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"{timestamp}_{speaker_name}.{output_format}"

        # Schedule cleanup
        background_tasks.add_task(cleanup_old_files, OUTPUT_DIR)

        # Return audio file
        return FileResponse(
            path=audio_path,
            media_type=f"audio/{output_format}",
            filename=filename
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to generate speech", error=str(e), text=text[:100])
        raise HTTPException(status_code=500, detail="Failed to generate speech")

@app.post("/clone")
async def voice_clone(
    file: UploadFile = File(..., description="Reference audio file for voice cloning"),
    text: str = Form(..., description="Text to convert to speech"),
    language: str = Form(DEFAULT_LANGUAGE, description="Language code"),
    output_format: str = Form(DEFAULT_FORMAT, description="Output format: wav or mp3"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Clone voice from uploaded reference audio"""
    try:
        # Save uploaded file temporarily
        temp_dir = Path(OUTPUT_DIR) / "temp"
        temp_dir.mkdir(exist_ok=True)

        reference_path = temp_dir / f"reference_{os.urandom(8).hex()}.wav"

        with open(reference_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Validate language
        supported_languages = tts.get_languages()
        if not validate_language(language, supported_languages):
            raise HTTPException(status_code=400, detail=f"Unsupported language: {language}")

        # Generate speech with voice cloning
        audio_path = tts.generate_speech(
            text=text,
            language=language,
            speaker_wav=str(reference_path)
        )

        # Convert format if needed
        if output_format.lower() != "wav":
            audio_path = tts.convert_format(audio_path, output_format)

        # Cleanup temp file
        os.remove(reference_path)

        # Schedule cleanup
        background_tasks.add_task(cleanup_old_files, OUTPUT_DIR)

        # Return audio file
        return FileResponse(
            path=audio_path,
            media_type=f"audio/{output_format}",
            filename=f"cloned_voice.{output_format}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to clone voice", error=str(e))
        if 'reference_path' in locals():
            try:
                os.remove(reference_path)
            except:
                pass
        raise HTTPException(status_code=500, detail="Failed to clone voice")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
