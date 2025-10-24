import os
from dotenv import load_dotenv

load_dotenv()

# TTS Configuration
TTS_ENGINE = os.getenv("TTS_ENGINE", "coqui_xtts")  # For future extension: coqui_xtts, elevenlabs, azure, etc.
MODEL_NAME = os.getenv("MODEL_NAME", "tts_models/multilingual/multi-dataset/xtts_v2")
DEVICE = os.getenv("DEVICE", "cpu")  # cpu or cuda

# API Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Output Configuration
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs")
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")
DEFAULT_SPEAKER = os.getenv("DEFAULT_SPEAKER", "Daisy Studious")
DEFAULT_FORMAT = os.getenv("DEFAULT_FORMAT", "mp3")  # wav or mp3

# UI Configuration
SHOW_API_INFO_TAB = os.getenv("SHOW_API_INFO_TAB", "true").lower() == "true"

# Security (for future)
API_KEY = os.getenv("API_KEY")  # Optional API key for authentication
