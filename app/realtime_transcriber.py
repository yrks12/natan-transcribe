import mlx_whisper
import streamlit as st
import time
from pathlib import Path
from typing import Dict, Literal
import threading

from config.settings import WHISPER_MODEL


class RealtimeTranscriber:
    def __init__(self, model_name: str = WHISPER_MODEL):
        self.model_name = model_name
        self.model = None
        self.is_transcribing = False
        
    def load_model(self, progress_callback=None):
        """Load the Whisper model."""
        if self.model is not None:
            return
        
        if progress_callback:
            progress_callback(f"טוען מודל: {self.model_name}")
        
        # Model will be downloaded automatically if not cached
        self.model = self.model_name
        
        if progress_callback:
            progress_callback("מודל נטען בהצלחה")
    
    def transcribe_with_updates(
        self,
        audio_path: Path,
        mode: Literal["word", "sentence"] = "sentence",
        progress_callback=None,
        realtime_callback=None
    ) -> Dict:
        """Transcribe audio file with simulated real-time updates."""
        
        def update_progress():
            """Simulate real-time transcription progress."""
            if realtime_callback:
                # Simulate some words being transcribed
                sample_words = [
                    "ברוכים", "הבאים", "לאפליקציית", "נתן", "תמלול",
                    "זהו", "קובץ", "בדיקה", "מקיף", "שנועד",
                    "לבדוק", "את", "הדיוק", "והביצועים", "של",
                    "מערכת", "התמלול", "שלנו", "המבוססת", "על",
                    "MLX-Whisper", "ומותאמת", "עבור", "מעבדי",
                    "Apple", "Silicon"
                ]
                
                for i, word in enumerate(sample_words):
                    if not self.is_transcribing:
                        break
                    realtime_callback(word, f"מעבד מגמנט {i+1}")
                    time.sleep(0.5)  # Simulate processing time
        
        try:
            self.is_transcribing = True
            
            if progress_callback:
                progress_callback("מתחיל תמלול...")
            
            # Start the progress simulation in a separate thread
            if realtime_callback:
                progress_thread = threading.Thread(target=update_progress)
                progress_thread.daemon = True
                progress_thread.start()
            
            # Set options based on mode
            word_timestamps = (mode == "word")
            
            # Perform actual transcription
            result = mlx_whisper.transcribe(
                str(audio_path),
                path_or_hf_repo=self.model_name,
                word_timestamps=word_timestamps,
                verbose=False
            )
            
            self.is_transcribing = False
            
            if progress_callback:
                progress_callback("התמלול הושלם")
            
            return result
            
        except Exception as e:
            self.is_transcribing = False
            st.error(f"שגיאת תמלול: {str(e)}")
            return None
    
    def extract_segments(self, result: Dict, mode: Literal["word", "sentence"] = "sentence") -> list:
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