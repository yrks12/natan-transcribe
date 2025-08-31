#!/usr/bin/env python3

import os
import subprocess
from pathlib import Path

def create_test_speech():
    """Create a 2000-word test speech for transcription testing."""
    
    speech_text = """
Welcome to the Natan Transcribe application testing session. This is a comprehensive test audio file designed to evaluate the accuracy and performance of our MLX-Whisper transcription system running on Apple Silicon hardware.

The purpose of this test is to verify that our application can successfully process spoken content and generate accurate subtitle files in the SRT format. We will be covering various topics and speaking patterns to ensure robust testing coverage.

First, let me discuss the technical architecture of our transcription system. The application leverages MLX-Whisper, which is specifically optimized for Apple's M1 and M2 processors. This optimization provides significantly faster processing speeds compared to traditional CPU-based transcription methods. The large-v3-turbo model that we're using offers an excellent balance between speed and accuracy, processing audio approximately eight times faster than the standard large-v3 model.

Our system supports multiple audio and video formats including MP4, MP3, WAV, AVI, MOV, MKV, WebM, M4A, FLAC, AAC, and OGG files. This wide format support ensures compatibility with content from various sources and recording devices. The application automatically extracts audio from video files and converts it to the optimal format for Whisper processing.

The user interface is built using Streamlit, providing a clean and intuitive web-based experience. Users can simply drag and drop their media files, select their preferred transcription settings, and receive professionally formatted SRT subtitle files. The interface includes real-time progress tracking, so users always know the status of their transcription jobs.

One of the key features of our implementation is the flexible timestamp generation. Users can choose between word-level timestamps for precise synchronization, or sentence-level timestamps for more readable subtitle blocks. Word-level timestamps are particularly useful for video editors who need frame-accurate subtitle placement, while sentence-level timestamps create cleaner, more readable subtitles for general viewing.

The SRT generation system follows industry-standard formatting rules, ensuring compatibility with all major video players and editing software. Each subtitle entry includes proper sequence numbering, accurate timestamp formatting using hours, minutes, seconds, and milliseconds, and text that respects character limits and line breaking conventions.

Performance optimization is a critical aspect of our design. The system processes files entirely locally, eliminating privacy concerns and network dependency issues. For a typical ten-minute audio file, processing time ranges from thirty seconds using the tiny model to approximately three minutes using the large-v3 model, depending on the complexity of the audio content.

Memory management is handled efficiently through streaming processing and automatic cleanup of temporary files. The system creates temporary audio extractions during processing but removes them immediately after transcription completion, preventing unnecessary disk usage accumulation.

Error handling throughout the application provides clear feedback to users when issues occur. Common scenarios like unsupported file formats, corrupted media files, or insufficient system resources are detected and reported with helpful guidance for resolution.

The installation process has been streamlined to require minimal user intervention. A single installation script handles prerequisite checking, dependency installation, model downloading, and service configuration. Once installed, the application runs as a background service, automatically starting when the system boots and remaining available for use.

Service management is handled through macOS launchd, providing reliable startup behavior and automatic restart capabilities if the service encounters issues. Users can easily start, stop, and monitor the service using provided convenience scripts or standard launchd commands.

The application includes comprehensive logging and monitoring capabilities. All processing activities are logged to help with troubleshooting, and users can easily access these logs to diagnose any issues that might arise during operation.

Quality assurance is maintained through multiple validation steps during the transcription process. Audio files are validated before processing to ensure they contain valid audio streams and are within acceptable duration ranges. The generated SRT content is also validated to ensure proper formatting before being presented to the user.

Future enhancement possibilities include batch processing capabilities for multiple files, automatic language detection for multilingual content, translation services for international audiences, custom vocabulary support for domain-specific terminology, and additional export formats beyond SRT.

Security considerations have been integrated throughout the design. All processing occurs locally on the user's machine, ensuring that sensitive audio content never leaves the device. File validation prevents malicious media files from causing system issues, and the service runs with appropriate user permissions to maintain system security.

The system has been tested with various audio qualities and speaking styles to ensure robust performance across different use cases. Clear speech, accented speech, multiple speakers, background music, and technical terminology have all been evaluated to verify transcription accuracy.

Documentation includes detailed installation instructions, usage guidelines, troubleshooting procedures, and performance optimization recommendations. This comprehensive documentation ensures that users can successfully install, configure, and operate the application regardless of their technical expertise level.

In conclusion, the Natan Transcribe application provides a professional-grade solution for local audio and video transcription needs. By leveraging Apple Silicon optimization, providing an intuitive user interface, and maintaining high accuracy standards, the application serves as an excellent tool for content creators, researchers, journalists, and anyone needing reliable transcription services.

This test audio file contains approximately two thousand words and covers various topics and speaking patterns to thoroughly evaluate the transcription system's capabilities. The generated transcript should demonstrate the application's ability to handle extended content while maintaining accuracy and proper formatting throughout the entire duration.

Thank you for using the Natan Transcribe application, and we hope this test demonstrates the quality and reliability of our transcription technology.
    """
    
    return speech_text.strip()

def main():
    print("Creating 2000-word test audio file using macOS text-to-speech...")
    
    # Generate the speech text
    speech_text = create_test_speech()
    word_count = len(speech_text.split())
    print(f"Generated speech text with {word_count} words")
    
    # Save text to temporary file
    text_file = Path("temp_speech.txt")
    with open(text_file, "w") as f:
        f.write(speech_text)
    
    # Use macOS 'say' command to create audio file
    print("Generating audio using macOS text-to-speech...")
    output_path = Path("test_audio_2000_words.aiff")
    
    try:
        # Generate AIFF file using 'say' command
        subprocess.run([
            "say", 
            "-f", str(text_file),
            "-o", str(output_path),
            "-v", "Alex",  # Use Alex voice (high quality)
            "-r", "180"    # Speaking rate (words per minute)
        ], check=True)
        
        print(f"✅ Test AIFF file created: {output_path.absolute()}")
        
        # Convert to MP3 using FFmpeg (if available)
        mp3_path = Path("test_audio_2000_words.mp3")
        try:
            subprocess.run([
                "ffmpeg", "-i", str(output_path),
                "-acodec", "libmp3lame",
                "-ab", "128k",
                "-y",  # Overwrite output file
                str(mp3_path)
            ], check=True, capture_stdout=True)
            
            print(f"✅ Test MP3 file created: {mp3_path.absolute()}")
            
            # Clean up AIFF file
            output_path.unlink()
            output_file = mp3_path
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("FFmpeg not available, keeping AIFF format")
            output_file = output_path
        
        # Clean up temporary text file
        text_file.unlink()
        
        # Get file size
        file_size = output_file.stat().st_size / (1024 * 1024)
        print(f"📝 Word count: {word_count} words")
        print(f"📁 File size: {file_size:.2f} MB")
        
        print("\nTo test with your application:")
        print("1. Start the Natan Transcribe service:")
        print("   ./scripts/start.sh")
        print("2. Go to http://localhost:8501")
        print(f"3. Upload the audio file: {output_file.name}")
        print("4. Click 'Start Transcription'")
        
    except subprocess.CalledProcessError as e:
        print(f"Error creating audio file: {e}")
        return
    
    except FileNotFoundError:
        print("Error: 'say' command not found. This script requires macOS.")
        return

if __name__ == "__main__":
    main()