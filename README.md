# Natan Transcribe

A macOS web application that uses MLX-Whisper to transcribe audio/video files and generate SRT subtitle files with accurate timelines. Optimized for Apple Silicon (M1/M2).

## Features

- 🎬 **Multiple Format Support**: MP4, MP3, WAV, AVI, MOV, MKV, WebM, M4A, FLAC, AAC, OGG
- 🚀 **Apple Silicon Optimized**: Uses MLX-Whisper for fast transcription on M1/M2 chips
- ⏱️ **Flexible Timestamps**: Choose between word-level or sentence-level timestamps
- 📝 **SRT Generation**: Creates properly formatted SRT subtitle files
- 🖥️ **Web Interface**: Simple Streamlit-based UI accessible via browser
- 🔄 **Auto-start Service**: Runs automatically as a macOS service

## Requirements

- macOS with Apple Silicon (M1/M2)
- Python 3.9 or higher
- 8GB+ RAM recommended

## Quick Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd natan-transcribe
```

2. Run the installation script:
```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

The installer will:
- Check and install prerequisites (Homebrew, FFmpeg, Python)
- Create a virtual environment
- Install all Python dependencies
- Download the default Whisper model
- Configure and start the service
- Open the web app in your browser

## Usage

### Access the Application
After installation, the service runs automatically. Access it at:
```
http://localhost:8501
```

### Using the Web Interface

1. **Upload File**: Click "Browse files" and select your audio/video file
2. **Choose Settings**: 
   - Select Whisper model size (Tiny/Small/Medium/Large)
   - Choose timestamp mode (Sentence or Word level)
3. **Start Transcription**: Click the "Start Transcription" button
4. **Download Results**: Preview and download the generated SRT file

### Service Management

The installer creates convenience commands in `~/.local/bin/`:

```bash
# Start the service and open browser
natan-start

# Stop the service
natan-stop

# View service logs
natan-logs
```

To use these commands, add to your PATH:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc
```

### Manual Service Control

```bash
# Start service
launchctl load ~/Library/LaunchAgents/com.natan.transcribe.plist

# Stop service
launchctl unload ~/Library/LaunchAgents/com.natan.transcribe.plist

# Check service status
launchctl list | grep natan
```

## Models

Available Whisper models (accuracy vs speed tradeoff):

| Model | Parameters | Speed | Accuracy | Use Case |
|-------|------------|-------|----------|----------|
| Large-v3-turbo | 809M | Very Fast | Excellent | **Recommended** |
| Tiny | 39M | Fastest | Basic | Quick drafts |
| Small | 244M | Fast | Good | Light usage |
| Medium | 769M | Moderate | Better | Important content |
| Large-v3 | 1.5B | Slower | Best | Professional use |

## Configuration

Edit `.env` file to customize:

```env
WHISPER_MODEL=mlx-community/whisper-large-v3-turbo
STREAMLIT_PORT=8501
MAX_FILE_SIZE_MB=500
```

## Troubleshooting

### Service won't start
```bash
# Check error logs
tail -f /tmp/natan-transcribe.err

# Restart service
natan-stop && natan-start
```

### Port already in use
Change the port in `.env`:
```env
STREAMLIT_PORT=8502
```
Then restart the service.

### Model download issues
Models are cached in `~/.cache/huggingface/`. Clear this directory if you have download problems.

### FFmpeg errors
Reinstall FFmpeg:
```bash
brew reinstall ffmpeg
```

## File Size Limits

- Default maximum: 500MB
- No duration limits for transcription
- Larger files may require more RAM

## Performance Tips

1. **Use Large-v3-turbo model** for best balance of speed and accuracy (8x faster than large-v3)
2. **Sentence-level timestamps** for readable subtitles
3. **Word-level timestamps** for precise synchronization
4. Close other applications to free up RAM for large files

## Uninstallation

To completely remove the application:

```bash
# Stop and remove service
launchctl unload ~/Library/LaunchAgents/com.natan.transcribe.plist
rm ~/Library/LaunchAgents/com.natan.transcribe.plist

# Remove convenience commands
rm ~/.local/bin/natan-*

# Remove project directory
rm -rf /path/to/natan-transcribe
```

## Support

For issues or questions, please check:
- Error logs: `/tmp/natan-transcribe.err`
- Output logs: `/tmp/natan-transcribe.out`

## License

This project uses:
- [MLX-Whisper](https://github.com/ml-explore/mlx-examples): Apache 2.0
- [Streamlit](https://streamlit.io): Apache 2.0
- [OpenAI Whisper](https://github.com/openai/whisper): MIT