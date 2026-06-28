# Configuration settings

import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings"""
    
    # Server settings
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    # Storage settings
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "storage/uploads")
    PROCESSED_DIR = os.getenv("PROCESSED_DIR", "storage/processed")
    TEMP_DIR = os.getenv("TEMP_DIR", "storage/temp")
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 500 * 1024 * 1024))  # 500MB
    
    # Video settings
    ALLOWED_VIDEO_TYPES = [
        "video/mp4",
        "video/avi",
        "video/quicktime",
        "video/x-matroska"
    ]
    
    # Processing settings
    DEFAULT_QUALITY = os.getenv("DEFAULT_QUALITY", "1080p")
    DEFAULT_FORMAT = os.getenv("DEFAULT_FORMAT", "mp4")
    
    # Whisper AI settings
    WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
    WHISPER_LANGUAGE = os.getenv("WHISPER_LANGUAGE", "en")
    
    # FFmpeg settings
    FFMPEG_PATH = os.getenv("FFMPEG_PATH", "ffmpeg")
    FFPROBE_PATH = os.getenv("FFPROBE_PATH", "ffprobe")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")


# Create settings instance
settings = Settings()

# Create directories if they don't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.PROCESSED_DIR, exist_ok=True)
os.makedirs(settings.TEMP_DIR, exist_ok=True)
os.makedirs("logs", exist_ok=True)
