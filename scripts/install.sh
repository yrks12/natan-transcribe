#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}   Natan Transcribe - Installation Script${NC}"
echo -e "${GREEN}==================================================${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Homebrew
install_homebrew() {
    echo -e "${YELLOW}Installing Homebrew...${NC}"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH for Apple Silicon Macs
    if [[ -f "/opt/homebrew/bin/brew" ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
}

# Step 1: Check Prerequisites
echo -e "${YELLOW}Step 1: Checking prerequisites...${NC}"

# Check for Homebrew
if ! command_exists brew; then
    echo -e "${YELLOW}Homebrew not found.${NC}"
    read -p "Do you want to install Homebrew? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_homebrew
    else
        echo -e "${RED}Homebrew is required. Exiting.${NC}"
        exit 1
    fi
fi

# Check for Python 3.9+
if ! command_exists python3; then
    echo -e "${YELLOW}Python 3 not found. Installing via Homebrew...${NC}"
    brew install python@3.11
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Check for FFmpeg
if ! command_exists ffmpeg; then
    echo -e "${YELLOW}FFmpeg not found. Installing via Homebrew...${NC}"
    brew install ffmpeg
else
    echo -e "${GREEN}✓ FFmpeg found${NC}"
fi

# Step 2: Install Python Dependencies Globally
echo ""
echo -e "${YELLOW}Step 2: Installing Python dependencies globally...${NC}"

cd "$PROJECT_DIR"

# Install requirements globally with user flag
python3 -m pip install --user --upgrade pip
python3 -m pip install --user -r requirements.txt
echo -e "${GREEN}✓ Python dependencies installed globally${NC}"

# Step 4: Download Default Model
echo ""
echo -e "${YELLOW}Step 4: Pre-downloading Whisper model (this may take a while)...${NC}"

python3 -c "
import mlx_whisper
print('Downloading mlx-community/whisper-large-v3-turbo model...')
# This will download the model if not already cached
import tempfile
with tempfile.NamedTemporaryFile(suffix='.wav') as f:
    try:
        result = mlx_whisper.transcribe(
            f.name,
            path_or_hf_repo='mlx-community/whisper-large-v3-turbo',
            verbose=False
        )
    except:
        pass  # Expected to fail on empty file, but model will be downloaded
print('Model download complete!')
"
echo -e "${GREEN}✓ Whisper model cached${NC}"

# Step 5: Create .env file if not exists
echo ""
echo -e "${YELLOW}Step 5: Setting up configuration...${NC}"

if [ ! -f "$PROJECT_DIR/.env" ]; then
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    echo -e "${GREEN}✓ Configuration file created${NC}"
else
    echo -e "${GREEN}✓ Configuration file already exists${NC}"
fi

# Step 6: Configure service
echo ""
echo -e "${YELLOW}Step 6: Configuring service...${NC}"

PLIST_FILE="$PROJECT_DIR/services/com.natan.transcribe.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/com.natan.transcribe.plist"

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$HOME/Library/LaunchAgents"

# Get Python version for user bin path
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')

# Get the correct user's home directory (even when run with sudo)
if [ -n "$SUDO_USER" ]; then
    REAL_USER_HOME=$(eval echo ~$SUDO_USER)
    USER_PYTHON_BIN="$REAL_USER_HOME/Library/Python/$PYTHON_VERSION/bin"
else
    USER_PYTHON_BIN="$HOME/Library/Python/$PYTHON_VERSION/bin"
fi

# Find the correct Python path that has streamlit installed
# Test different Python paths in order of preference
for TEST_PYTHON in "/opt/homebrew/bin/python3" "/usr/local/bin/python3" "/usr/bin/python3" "/Library/Developer/CommandLineTools/usr/bin/python3"; do
    if [ -f "$TEST_PYTHON" ] && $TEST_PYTHON -c "import streamlit" 2>/dev/null; then
        PYTHON_PATH="$TEST_PYTHON"
        echo "Testing $TEST_PYTHON: ✓ has streamlit"
        break
    else
        echo "Testing $TEST_PYTHON: ✗ no streamlit or not found"
    fi
done

# If no Python with streamlit found, default to system python3
if [ -z "$PYTHON_PATH" ]; then
    PYTHON_PATH=$(which python3)
    echo "No Python with streamlit found, using default: $PYTHON_PATH"
fi

echo -e "${GREEN}Using Python: $PYTHON_PATH${NC}"

# Update paths in plist file
sed -e "s|{{PROJECT_DIR}}|$PROJECT_DIR|g" -e "s|{{USER_PYTHON_BIN}}|$USER_PYTHON_BIN|g" -e "s|{{PYTHON_PATH}}|$PYTHON_PATH|g" "$PLIST_FILE" > "$PLIST_DEST"
echo -e "${GREEN}✓ Service configuration updated${NC}"

# Step 7: Installing and starting service...
echo ""
echo -e "${YELLOW}Step 7: Installing and starting service...${NC}"

# Kill any existing processes
pkill -f "streamlit.*8501" 2>/dev/null || true
rm -f /tmp/natan-transcribe.pid

# Create reliable manual start script
cat > "$HOME/.local/bin/natan-transcribe-start" << EOF
#!/bin/bash
# Kill any existing instance first
pkill -f "streamlit.*8501" 2>/dev/null || true
rm -f /tmp/natan-transcribe.pid

cd "$PROJECT_DIR"
echo "Starting Natan Transcribe service..."
nohup $PYTHON_PATH -m streamlit run app/main.py \\
    --server.port=8501 \\
    --server.address=localhost \\
    --server.headless=true \\
    --server.maxUploadSize=10000 \\
    > ~/natan-transcribe.out 2> ~/natan-transcribe.err &

echo \$! > /tmp/natan-transcribe.pid
sleep 2
echo "Natan Transcribe started (PID: \$!)"
echo "Access at: http://localhost:8501"
open http://localhost:8501 2>/dev/null || true
EOF
chmod +x "$HOME/.local/bin/natan-transcribe-start"

# Create stop script
cat > "$HOME/.local/bin/natan-transcribe-stop" << EOF
#!/bin/bash
echo "Stopping Natan Transcribe service..."
pkill -f "streamlit.*8501" 2>/dev/null && echo "Service stopped" || echo "Service was not running"
rm -f /tmp/natan-transcribe.pid
EOF
chmod +x "$HOME/.local/bin/natan-transcribe-stop"

# Start the service immediately
"$HOME/.local/bin/natan-transcribe-start"
echo -e "${GREEN}✓ Service started successfully${NC}"

# Step 8: Verify Installation
echo ""
echo -e "${YELLOW}Step 8: Verifying installation...${NC}"

# Wait a moment for service to start
sleep 5

# Check if the web service is actually responding
if curl -s http://localhost:8501 | grep -q "Streamlit"; then
    echo -e "${GREEN}✓ Web service is running and responding${NC}"
elif [ -f /tmp/natan-transcribe.pid ] && kill -0 $(cat /tmp/natan-transcribe.pid) 2>/dev/null; then
    echo -e "${GREEN}✓ Service is running (manual mode)${NC}"
elif launchctl list | grep -q "com.natan.transcribe"; then
    echo -e "${YELLOW}⚠ Service is loaded but may not be responding. Check logs at /tmp/natan-transcribe.err${NC}"
else
    echo -e "${RED}⚠ Service may not be running. Check logs at /tmp/natan-transcribe.err${NC}"
fi

# Step 9: Create convenience scripts
echo ""
echo -e "${YELLOW}Step 9: Creating convenience commands...${NC}"

# Create local bin directory if not exists
mkdir -p "$HOME/.local/bin"

# Create start script (use the reliable manual method)
cat > "$HOME/.local/bin/natan-start" << EOF
#!/bin/bash
"$HOME/.local/bin/natan-transcribe-start"
EOF

# Create stop script
cat > "$HOME/.local/bin/natan-stop" << EOF
#!/bin/bash
"$HOME/.local/bin/natan-transcribe-stop"
EOF

# Create logs script
cat > "$HOME/.local/bin/natan-logs" << EOF
#!/bin/bash
echo "=== Recent Output ==="
tail -n 50 /tmp/natan-transcribe.out
echo ""
echo "=== Recent Errors ==="
tail -n 50 /tmp/natan-transcribe.err
EOF

# Make scripts executable
chmod +x "$HOME/.local/bin/natan-start"
chmod +x "$HOME/.local/bin/natan-stop"
chmod +x "$HOME/.local/bin/natan-logs"

echo -e "${GREEN}✓ Convenience commands created${NC}"

# Final Instructions
echo ""
echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}   Installation Complete!${NC}"
echo -e "${GREEN}==================================================${NC}"
echo ""
echo -e "${GREEN}The Natan Transcribe service is now running!${NC}"
echo ""
echo -e "Access the application at: ${YELLOW}http://localhost:8501${NC}"
echo ""
echo -e "Convenience commands (add ~/.local/bin to your PATH):"
echo -e "  ${YELLOW}natan-start${NC} - Start the service and open the web app"
echo -e "  ${YELLOW}natan-stop${NC}  - Stop the service"
echo -e "  ${YELLOW}natan-logs${NC}  - View service logs"
echo ""
echo -e "To add these commands to your PATH, run:"
echo -e "${YELLOW}echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.zshrc && source ~/.zshrc${NC}"
echo ""
echo -e "${GREEN}Opening the application now...${NC}"

# Open the application
sleep 2
open http://localhost:8501