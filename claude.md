# MLX-Whisper Transcription Service Architecture

## Project Overview
A macOS-native web application that leverages Apple Silicon's ML capabilities through mlx-whisper to provide high-performance audio/video transcription with SRT subtitle generation.

## Technology Stack

### Core Technologies
- **MLX-Whisper**: Apple Silicon-optimized Whisper implementation for transcription
- **Streamlit**: Web framework for the user interface
- **Python 3.9+**: Primary programming language
- **FFmpeg**: Audio/video processing and extraction
- **launchd**: macOS service management

### Key Dependencies
- `mlx-whisper`: Transcription engine
- `streamlit`: Web UI framework
- `ffmpeg-python`: Python bindings for FFmpeg
- `numpy`: Audio processing
- `python-dotenv`: Environment configuration

## Architecture Design

### Component Architecture

```
┌─────────────────────────────────────────────┐
│           Streamlit Web Interface           │
│  • File Upload (MP4, MP3, WAV, AVI)        │
│  • Progress Tracking                        │
│  • SRT Preview & Download                   │
└─────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│          Audio Extraction Service           │
│  • FFmpeg integration                       │
│  • Format conversion                        │
│  • Temporary file management                │
└─────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│        MLX-Whisper Transcription           │
│  • Model loading (cached)                   │
│  • Batch processing                         │
│  • Word/sentence timestamp extraction       │
└─────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│           SRT Generation Service            │
│  • Timestamp formatting                     │
│  • Text segmentation                        │
│  • SRT file creation                        │
└─────────────────────────────────────────────┘
```

### Directory Structure

```
natan-transcribe/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Streamlit main application
│   ├── transcriber.py           # MLX-Whisper integration
│   ├── srt_generator.py         # SRT file generation
│   └── audio_processor.py       # Audio extraction/processing
├── config/
│   ├── __init__.py
│   ├── settings.py              # Application configuration
│   └── models.py                # Model configuration
├── utils/
│   ├── __init__.py
│   ├── file_handler.py          # File upload/download utilities
│   └── progress_tracker.py      # Progress tracking utilities
├── services/
│   └── com.natan.transcribe.plist  # launchd service definition
├── scripts/
│   ├── install.sh               # Installation script
│   ├── start.sh                 # Start service script
│   └── stop.sh                  # Stop service script
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore file
├── README.md                    # User documentation
└── claude.md                    # This architecture document
```

## Implementation Details

### 1. Audio/Video Processing Pipeline

1. **File Upload**: Accept files up to 500MB through Streamlit's file uploader
2. **Audio Extraction**: Use FFmpeg to extract audio track from video files
3. **Format Conversion**: Convert to WAV format for optimal processing
4. **Temporary Storage**: Store in system temp directory, clean up after processing

### 2. Transcription Engine

**Model Selection Strategy**:
- Default: `mlx-community/whisper-small` (good balance of speed/accuracy)
- Options available: tiny, base, medium, large-v3
- Model cached after first download

**Processing Modes**:
- **Word-level timestamps**: For precise subtitle synchronization
- **Sentence-level timestamps**: For readable subtitle blocks

**Performance Optimization**:
- Batch size: 12 (configurable based on file size)
- Use quantized models for memory efficiency
- Implement progress callbacks for user feedback

### 3. SRT Generation

**Format Compliance**:
```
[sequence_number]
[start_time] --> [end_time]
[subtitle_text]
[blank_line]
```

**Timestamp Format**: `HH:MM:SS,mmm`

**Text Processing**:
- Word-level: Group words into ~3-5 second segments
- Sentence-level: Natural sentence boundaries
- Character limit: 42 characters per line (standard)

### 4. Service Configuration

**launchd Service Features**:
- Auto-start on system boot
- Restart on failure
- Log rotation
- Resource limits

**Network Configuration**:
- Default port: 8501
- Bind to: localhost only
- Optional: Custom port configuration

## Installation & Deployment Strategy

### Phase 1: Environment Setup
```bash
# Check system requirements
# Install Homebrew if needed
# Install FFmpeg
# Create virtual environment
```

### Phase 2: Application Installation
```bash
# Clone repository
# Install Python dependencies
# Download default MLX model
# Configure environment variables
```

### Phase 3: Service Configuration
```bash
# Install launchd plist
# Set permissions
# Load service
# Verify service status
```

### Installation Script Features
- Prerequisite checking (Python, FFmpeg, etc.)
- Automatic virtual environment creation
- Dependency installation with pip
- Model pre-download for faster first run
- Service registration and startup
- Post-installation verification

## Performance Considerations

### Memory Management
- Stream large files instead of loading entirely into memory
- Clean up temporary files immediately after processing
- Implement file size limits (default: 500MB)

### Processing Optimization
- Use MLX's Metal acceleration for M2 chip
- Implement request queuing for multiple users
- Cache loaded models between requests
- Progressive SRT generation during transcription

### Expected Performance (M2 Chip)
- Small model (244M params): ~30 seconds for 10-minute audio
- Medium model (769M params): ~90 seconds for 10-minute audio
- Large-v3 model (1.5B params): ~3 minutes for 10-minute audio

## Security Considerations

1. **File Validation**: 
   - Verify file extensions and MIME types
   - Scan for malformed media files
   - Limit file sizes

2. **Service Isolation**:
   - Run service as non-root user
   - Restrict network access to localhost
   - Implement rate limiting

3. **Data Privacy**:
   - Process files locally only
   - Auto-delete temporary files
   - No external API calls

## Error Handling

1. **Upload Errors**: File too large, unsupported format
2. **Processing Errors**: FFmpeg failures, corrupted files
3. **Transcription Errors**: Model loading issues, memory constraints
4. **Service Errors**: Port conflicts, permission issues

Each error type will have specific user-friendly messages and recovery suggestions.

## Future Enhancements

1. **Batch Processing**: Upload multiple files at once
2. **Language Detection**: Auto-detect audio language
3. **Translation**: Translate transcriptions to other languages
4. **Custom Vocabulary**: Support domain-specific terminology
5. **Export Formats**: Support VTT, ASS, and other subtitle formats
6. **Real-time Transcription**: Live audio streaming support

## Testing Strategy

### Unit Tests
- SRT format generation
- Timestamp calculations
- File validation

### Integration Tests
- End-to-end transcription pipeline
- Service start/stop procedures
- Error recovery scenarios

### Performance Tests
- Various file sizes and formats
- Concurrent request handling
- Memory usage monitoring

## Success Metrics

1. **Installation**: < 5 minutes from script execution to running service
2. **Transcription Speed**: Real-time factor < 0.3 (3x faster than playback)
3. **Accuracy**: > 95% for clear audio (using small model)
4. **Reliability**: 99.9% uptime for local service
5. **User Experience**: Single-click installation, intuitive web interface