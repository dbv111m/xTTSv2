#!/usr/bin/env python3
"""Debug test for TTS API logic"""

import os
from pathlib import Path
from datetime import datetime

def test_filename_generation():
    """Test filename generation logic"""
    print("Testing filename generation...")

    # Test data
    speaker = "Daisy Studious"
    output_format = "mp3"

    # Generate filename with timestamp and speaker (no spaces)
    speaker_name = (speaker or "default").replace(" ", "_")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"{timestamp}_{speaker_name}.{output_format}"

    print(f"Original speaker: {speaker}")
    print(f"Clean speaker: {speaker_name}")
    print(f"Timestamp: {timestamp}")
    print(f"Generated filename: {filename}")

    # Test with None speaker
    speaker = None
    speaker_name = (speaker or "default").replace(" ", "_")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"{timestamp}_{speaker_name}.{output_format}"
    print(f"With None speaker: {filename}")

    # Test with speaker containing spaces
    speaker = "Test Speaker Name"
    speaker_name = (speaker or "default").replace(" ", "_")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"{timestamp}_{speaker_name}.{output_format}"
    print(f"With spaces: {filename}")

def test_file_paths():
    """Test file path logic"""
    print("\nTesting file paths...")

    OUTPUT_DIR = "outputs"

    # Create output directory
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(exist_ok=True)

    # Generate unique filename
    import uuid
    filename = f"tts_{uuid.uuid4().hex}.wav"
    output_path = output_dir / filename

    print(f"Output directory: {output_dir}")
    print(f"Generated path: {output_path}")
    print(f"Path exists: {output_path.exists()}")

    # Test temp file logic
    temp_dir = Path(OUTPUT_DIR) / "temp"
    temp_dir.mkdir(exist_ok=True)

    temp_filename = f"reference_{uuid.uuid4().hex}.wav"
    speaker_wav_path = temp_dir / temp_filename

    print(f"Temp directory: {temp_dir}")
    print(f"Temp file path: {speaker_wav_path}")

    # Test filename generation for download
    speaker = "Daisy Studious"
    output_format = "mp3"
    speaker_name = (speaker or "default").replace(" ", "_")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    download_filename = f"{timestamp}_{speaker_name}.{output_format}"

    print(f"Download filename: {download_filename}")

def test_upload_logic():
    """Test the upload file processing logic"""
    print("\nTesting upload file logic...")

    # Mock UploadFile
    class MockUploadFile:
        def __init__(self, filename, content=b"mock audio data"):
            self.filename = filename
            self.content = content

        async def read(self):
            return self.content

    # Test with file
    speaker_wav = MockUploadFile("test_audio.mp3", b"fake audio content")

    speaker_wav_path = None
    if speaker_wav and speaker_wav.filename:
        temp_dir = Path("outputs") / "temp"
        temp_dir.mkdir(exist_ok=True)

        import uuid
        temp_filename = f"reference_{uuid.uuid4().hex}.wav"
        speaker_wav_path = temp_dir / temp_filename

        # Simulate file write
        with open(speaker_wav_path, "wb") as f:
            f.write(speaker_wav.content)

        print(f"Created temp file: {speaker_wav_path}")
        print(f"File exists: {speaker_wav_path.exists()}")

        # Clean up
        if speaker_wav_path.exists():
            os.remove(speaker_wav_path)
            print("Temp file cleaned up")

    # Test without file
    speaker_wav = None
    speaker_wav_path = None
    if speaker_wav and speaker_wav.filename:
        print("Should not reach here")
    else:
        print("Correctly handled None file")

    print("Upload logic test completed!")

if __name__ == "__main__":
    test_filename_generation()
    test_file_paths()
    test_upload_logic()
    print("\nAll debug tests completed!")
