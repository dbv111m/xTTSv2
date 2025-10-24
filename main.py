import os
from pathlib import Path
from typing import Optional, List
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
import structlog

from config import (
    HOST, PORT, DEBUG, TTS_ENGINE, MODEL_NAME, DEVICE, OUTPUT_DIR,
    DEFAULT_LANGUAGE, DEFAULT_SPEAKER, DEFAULT_FORMAT, API_KEY, SHOW_API_INFO_TAB
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

# Global variable to store voices (initialized after TTS engine)
HARDCODED_VOICES = [
    "Claribel Dervla", "Daisy Studious", "Gracie Wise", "Tammie Ema", "Ana Florence",
    "Annmarie Nele", "Asya Anara", "Brenda Stern", "Gitta Nikolina", "Henriette Usha",
    "Sofia Hellen", "Tanja Adelina", "Vjollca Johnnie", "Andrew Chipper", "Badr Odhiambo",
    "Dionisio Schuyler", "Royston Min", "Viktor Eka", "Abrahan Mack", "Adde Michal",
    "Baldur Sanjin", "Craig Gutsy", "Damien Black", "Gilberto Mathias", "Ilkin Urbano",
    "Kazuhiko Atallah", "Ludvig Milivoj", "Suad Qasim", "Torcull Diarmuid", "Viktor Menelaos",
    "Zacharie Aimilios", "Nova Hogarth", "Maja Ruoho", "Uta Obando", "Lidiya Szekeres",
    "Chandra MacFarland", "Szofi Granger", "Camilla Holmström", "Lilya Stainthorpe",
    "Zofija Kendrick", "Narelle Moon", "Barbora MacLean", "Alexandra Hisakawa", "Alma María",
    "Rosemary Okafor", "Ige Behringer", "Filip Traverse", "Damjan Chapman", "Wulf Carlevaro",
    "Aaron Dreschner", "Kumar Dahl", "Eugenio Mataracı", "Ferran Simen", "Xavier Hayasaka",
    "Luis Moray", "Marcos Rudaski"
]

available_voices = HARDCODED_VOICES

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
        try:
            voices = tts.get_voices()
            if voices:
                available_voices = voices
            logger.info(f"Cached {len(available_voices)} voices")
        except Exception as e:
            logger.warning(f"Failed to load voices, using fallback: {e}")
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
        voices = available_voices if available_voices else tts.get_voices()
        return {"voices": voices}
    except Exception as e:
        logger.error("Failed to get voices", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve voices")

@app.get("/voices-select")
async def get_voices_for_select():
    """Get voices formatted for HTML select options"""
    return {"voices": available_voices}

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
    speaker_wav: UploadFile = File(None, description="Reference audio file for voice cloning"),
    text: str = Form(..., description="Text to convert to speech"),
    language: str = Form(DEFAULT_LANGUAGE, description="Language code"),
    speaker: Optional[str] = Form(None, description="Speaker name for predefined voices"),
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
        if speaker_wav and speaker_wav.filename:
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
        speaker_wav_str = str(speaker_wav_path) if speaker_wav_path else None
        logger.info("Calling TTS generate_speech", text=text[:50], language=language, speaker=speaker, speaker_wav=speaker_wav_str)

        audio_path = tts.generate_speech(
            text=text,
            language=language,
            speaker=speaker,
            speaker_wav=speaker_wav_str
        )

        # Clean up temp file
        if speaker_wav_path and speaker_wav_path.exists():
            os.remove(speaker_wav_path)

        # Convert format if needed
        if output_format.lower() != "wav":
            audio_path = tts.convert_format(audio_path, output_format)

        # Generate filename with timestamp and speaker (no spaces)
        from datetime import datetime
        speaker_name = (speaker or "default").replace(" ", "_")
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
        logger.error("Failed to generate speech", error=str(e), text=text[:100], exc_info=True)
        # Return more detailed error message
        error_detail = f"Failed to generate speech: {str(e)}"
        if "sens" in str(e).lower():
            error_detail = "TTS library error. Please try again or use a different voice."
        raise HTTPException(status_code=500, detail=error_detail)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
