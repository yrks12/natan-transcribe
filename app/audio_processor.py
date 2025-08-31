import ffmpeg
import numpy as np
from pathlib import Path
from typing import Optional, Tuple
import streamlit as st
import tempfile

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config.settings import TEMP_DIR, SUPPORTED_VIDEO_FORMATS


def extract_audio(input_path: Path, progress_callback=None) -> Optional[Path]:
    """Extract audio from video/audio file and convert to WAV format."""
    try:
        # Check if input is video or audio
        extension = input_path.suffix.lower().lstrip(".")
        is_video = extension in SUPPORTED_VIDEO_FORMATS
        
        # Create output path
        output_filename = f"{input_path.stem}_audio.wav"
        output_path = TEMP_DIR / output_filename
        
        if progress_callback:
            progress_callback("Extracting audio from file...")
        
        # Extract/convert audio using ffmpeg
        stream = ffmpeg.input(str(input_path))
        
        # Configure audio settings for optimal Whisper processing
        stream = ffmpeg.output(
            stream,
            str(output_path),
            acodec='pcm_s16le',  # 16-bit PCM
            ar='16000',          # 16kHz sample rate (Whisper's expected rate)
            ac=1,                # Mono channel
            format='wav'
        )
        
        # Run ffmpeg with overwrite output
        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
        
        if progress_callback:
            progress_callback("Audio extraction complete")
        
        return output_path
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode() if e.stderr else str(e)
        st.error(f"FFmpeg error: {error_message}")
        return None
    except Exception as e:
        st.error(f"Error extracting audio: {str(e)}")
        return None


def get_audio_duration(audio_path: Path) -> float:
    """Get duration of audio file in seconds."""
    try:
        probe = ffmpeg.probe(str(audio_path))
        duration = float(probe['streams'][0]['duration'])
        return duration
    except Exception as e:
        st.warning(f"Could not determine audio duration: {e}")
        return 0.0


def validate_audio_file(audio_path: Path) -> Tuple[bool, str]:
    """Validate audio file for processing."""
    if not audio_path.exists():
        return False, "Audio file does not exist"
    
    try:
        probe = ffmpeg.probe(str(audio_path))
        
        # Check if file has audio stream
        audio_streams = [s for s in probe['streams'] if s['codec_type'] == 'audio']
        if not audio_streams:
            return False, "No audio stream found in file"
        
        # Check duration
        duration = get_audio_duration(audio_path)
        if duration <= 0:
            return False, "Invalid audio duration"
        
        return True, f"Valid audio file ({duration/60:.1f} minutes)"
        
    except Exception as e:
        return False, f"Error validating audio: {str(e)}"