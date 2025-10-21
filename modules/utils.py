import os
from pathlib import Path
from typing import Optional
import structlog

logger = structlog.get_logger()

def ensure_output_dir(output_dir: str) -> Path:
    """Ensure output directory exists"""
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path

def validate_language(language: str, supported_languages: list) -> bool:
    """Validate if language is supported"""
    return language.lower() in supported_languages

def validate_file_exists(file_path: str) -> bool:
    """Check if file exists"""
    return Path(file_path).exists()

def get_file_size_mb(file_path: str) -> float:
    """Get file size in MB"""
    return Path(file_path).stat().st_size / (1024 * 1024)

def cleanup_old_files(output_dir: str, max_age_hours: int = 24) -> None:
    """Clean up old generated files"""
    import time
    output_path = Path(output_dir)
    if not output_path.exists():
        return

    current_time = time.time()
    for file_path in output_path.glob("*"):
        if file_path.is_file():
            file_age = current_time - file_path.stat().st_mtime
            if file_age > (max_age_hours * 3600):
                try:
                    file_path.unlink()
                    logger.info("Cleaned up old file", file=str(file_path))
                except Exception as e:
                    logger.warning("Failed to cleanup file", file=str(file_path), error=str(e))
