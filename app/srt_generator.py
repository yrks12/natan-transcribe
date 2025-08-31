from typing import List, Dict
from datetime import timedelta
import re

from config.settings import MAX_CHARS_PER_LINE, MAX_SUBTITLE_DURATION, MIN_SUBTITLE_DURATION


class SRTGenerator:
    def __init__(self):
        self.max_chars = MAX_CHARS_PER_LINE
        self.max_duration = MAX_SUBTITLE_DURATION
        self.min_duration = MIN_SUBTITLE_DURATION
    
    def format_timestamp(self, seconds: float) -> str:
        """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)."""
        td = timedelta(seconds=seconds)
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        seconds = td.total_seconds() % 60
        
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}".replace('.', ',')
    
    def group_words_into_subtitles(self, segments: List[Dict]) -> List[Dict]:
        """Group word-level segments into subtitle-appropriate chunks."""
        if not segments:
            return []
        
        grouped = []
        current_group = []
        current_start = None
        current_text = ""
        
        for segment in segments:
            word = segment["text"]
            
            # Skip empty words
            if not word:
                continue
            
            # Initialize first group
            if current_start is None:
                current_start = segment["start"]
                current_text = word
                current_group = [segment]
                continue
            
            # Check if adding this word would exceed limits
            potential_text = current_text + " " + word
            potential_duration = segment["end"] - current_start
            
            # Create new subtitle if limits exceeded
            if (len(potential_text) > self.max_chars or 
                potential_duration > self.max_duration or
                word.strip().startswith(('.', '!', '?')) and len(current_text) > 20):
                
                # Save current group
                if current_group and current_text.strip():
                    grouped.append({
                        "start": current_start,
                        "end": current_group[-1]["end"],
                        "text": current_text.strip()
                    })
                
                # Start new group
                current_start = segment["start"]
                current_text = word
                current_group = [segment]
            else:
                # Add to current group
                current_text = potential_text
                current_group.append(segment)
        
        # Add final group
        if current_group and current_text.strip():
            grouped.append({
                "start": current_start,
                "end": current_group[-1]["end"],
                "text": current_text.strip()
            })
        
        return grouped
    
    def clean_text(self, text: str) -> str:
        """Clean and format text for subtitles."""
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        # Ensure proper capitalization after sentence endings
        text = re.sub(r'([.!?])\s*([a-z])', lambda m: m.group(1) + ' ' + m.group(2).upper(), text)
        return text
    
    def generate_srt(self, segments: List[Dict], mode: str = "sentence") -> str:
        """Generate SRT file content from segments."""
        if not segments:
            return ""
        
        # Handle different timestamp modes
        if mode == "word":
            # Group words into readable subtitle chunks
            segments = self.group_words_into_subtitles(segments)
        elif mode == "word_precise":
            # Use individual words as-is for precise timestamps (no grouping)
            pass
        
        srt_lines = []
        
        for idx, segment in enumerate(segments, 1):
            # Skip segments with no text
            if not segment.get("text", "").strip():
                continue
            
            # Clean text
            text = self.clean_text(segment["text"])
            
            # Format timestamps
            start_time = self.format_timestamp(segment["start"])
            end_time = self.format_timestamp(segment["end"])
            
            # Build SRT entry
            srt_lines.append(str(idx))
            srt_lines.append(f"{start_time} --> {end_time}")
            
            # Split long lines if necessary
            if len(text) > self.max_chars:
                words = text.split()
                line1 = []
                line2 = []
                current_length = 0
                
                for word in words:
                    if current_length + len(word) + 1 <= self.max_chars:
                        line1.append(word)
                        current_length += len(word) + 1
                    else:
                        line2.append(word)
                
                if line1:
                    srt_lines.append(" ".join(line1))
                if line2:
                    srt_lines.append(" ".join(line2))
            else:
                srt_lines.append(text)
            
            srt_lines.append("")  # Blank line between entries
        
        return "\n".join(srt_lines)
    
    def validate_srt(self, srt_content: str) -> bool:
        """Validate SRT file format."""
        if not srt_content:
            return False
        
        # Basic validation - check for required elements
        lines = srt_content.strip().split('\n')
        
        # Should have at least one subtitle (4 lines minimum)
        if len(lines) < 4:
            return False
        
        # Check for sequence numbers and timestamps
        has_sequence = any(line.strip().isdigit() for line in lines)
        has_timestamp = any('-->' in line for line in lines)
        
        return has_sequence and has_timestamp