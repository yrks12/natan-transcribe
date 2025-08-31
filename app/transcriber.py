import mlx_whisper
from pathlib import Path
from typing import Dict, List, Optional, Literal
import streamlit as st
import time

from config.settings import WHISPER_MODEL, WHISPER_BATCH_SIZE


class WhisperTranscriber:
    def __init__(self, model_name: str = WHISPER_MODEL):
        self.model_name = model_name
        self.model = None
        
    def load_model(self, progress_callback=None):
        """Load the Whisper model."""
        if self.model is not None:
            return
        
        if progress_callback:
            progress_callback(f"Loading model: {self.model_name}")
        
        # Model will be downloaded automatically if not cached
        self.model = self.model_name
        
        if progress_callback:
            progress_callback("Model loaded successfully")
    
    def transcribe(
        self,
        audio_path: Path,
        mode: Literal["word", "sentence"] = "sentence",
        progress_callback=None
    ) -> Dict:
        """Transcribe audio file using mlx-whisper."""
        try:
            if progress_callback:
                progress_callback("Starting transcription...")
            
            # Set options based on mode
            word_timestamps = (mode == "word")
            
            # Perform transcription
            result = mlx_whisper.transcribe(
                str(audio_path),
                path_or_hf_repo=self.model_name,
                word_timestamps=word_timestamps,
                verbose=False,
                batch_size=WHISPER_BATCH_SIZE
            )
            
            if progress_callback:
                progress_callback("Transcription complete")
            
            return result
            
        except Exception as e:
            st.error(f"Transcription error: {str(e)}")
            return None
    
    def extract_segments(self, result: Dict, mode: Literal["word", "sentence"] = "sentence") -> List[Dict]:
        """Extract segments with timestamps from transcription result."""
        segments = []
        
        if not result or "segments" not in result:
            return segments
        
        for segment in result["segments"]:
            if mode == "word" and "words" in segment:
                # Extract word-level timestamps
                for word_info in segment["words"]:
                    segments.append({
                        "start": word_info.get("start", 0),
                        "end": word_info.get("end", 0),
                        "text": word_info.get("word", "").strip()
                    })
            else:
                # Use sentence/segment level timestamps
                segments.append({
                    "start": segment.get("start", 0),
                    "end": segment.get("end", 0),
                    "text": segment.get("text", "").strip()
                })
        
        return segments
    
    def get_full_text(self, result: Dict) -> str:
        """Extract full transcribed text from result."""
        if not result or "text" not in result:
            return ""
        return result["text"].strip()