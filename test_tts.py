#!/usr/bin/env python3
"""Simple test for TTS module to debug errors"""

import sys
import os
sys.path.append('.')

from modules.tts import TTSEngine

def test_tts():
    """Test TTS functionality"""
    print("Testing TTS module...")

    config_dict = {
        "tts_engine": "coqui_xtts",
        "model_name": "tts_models/multilingual/multi-dataset/xtts_v2",
        "device": "cpu",
        "output_dir": "outputs",
        "default_speaker": "Daisy Studious",
    }

    try:
        print("Creating TTS engine...")
        tts_engine = TTSEngine(config_dict)
        tts = tts_engine.get_engine()

        print("Initializing TTS...")
        tts.initialize()

        print("Getting voices...")
        voices = tts.get_voices()
        print(f"Available voices: {len(voices)}")
        print(f"First 5 voices: {voices[:5]}")

        print("Getting languages...")
        languages = tts.get_languages()
        print(f"Supported languages: {languages}")

        print("Testing speech generation...")
        result = tts.generate_speech(
            text="Hello world",
            language="en",
            speaker="Daisy Studious"
        )
        print(f"Generated speech at: {result}")

        print("✅ All tests passed!")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tts()
