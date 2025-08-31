#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PLIST_FILE="$HOME/Library/LaunchAgents/com.natan.transcribe.plist"

echo -e "${YELLOW}Starting Natan Transcribe service...${NC}"

# Check if plist exists
if [ ! -f "$PLIST_FILE" ]; then
    echo -e "${RED}Service not installed. Please run install.sh first.${NC}"
    exit 1
fi

# Load the service
launchctl load "$PLIST_FILE" 2>/dev/null

# Check if service is running
sleep 2
if launchctl list | grep -q "com.natan.transcribe"; then
    echo -e "${GREEN}✓ Natan Transcribe service started successfully${NC}"
    echo -e "${GREEN}Access the application at: http://localhost:8501${NC}"
    echo ""
    echo "Opening in browser..."
    open http://localhost:8501
else
    echo -e "${RED}Failed to start service. Check logs:${NC}"
    echo -e "${YELLOW}tail -f /tmp/natan-transcribe.err${NC}"
    exit 1
fi