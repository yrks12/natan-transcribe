import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# MLX-Whisper Configuration
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "mlx-community/whisper-large-v3-turbo")
WHISPER_BATCH_SIZE = int(os.getenv("WHISPER_BATCH_SIZE", "12"))

# Streamlit Configuration
STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))
STREAMLIT_MAX_UPLOAD_SIZE = int(os.getenv("STREAMLIT_MAX_UPLOAD_SIZE", "500"))

# File Processing
TEMP_DIR = Path(os.getenv("TEMP_DIR", "/tmp/natan-transcribe"))
TEMP_DIR.mkdir(parents=True, exist_ok=True)
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "500"))

# Supported file formats
SUPPORTED_VIDEO_FORMATS = ["mp4", "avi", "mov", "mkv", "webm"]
SUPPORTED_AUDIO_FORMATS = ["mp3", "wav", "m4a", "flac", "aac", "ogg"]
SUPPORTED_FORMATS = SUPPORTED_VIDEO_FORMATS + SUPPORTED_AUDIO_FORMATS

# Service Configuration
SERVICE_NAME = os.getenv("SERVICE_NAME", "com.natan.transcribe")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# SRT Configuration
MAX_CHARS_PER_LINE = 42
MAX_SUBTITLE_DURATION = 7.0  # seconds
MIN_SUBTITLE_DURATION = 0.5  # seconds