#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PLIST_FILE="$HOME/Library/LaunchAgents/com.natan.transcribe.plist"

echo -e "${YELLOW}Stopping Natan Transcribe service...${NC}"

# Check if plist exists
if [ ! -f "$PLIST_FILE" ]; then
    echo -e "${RED}Service not installed.${NC}"
    exit 1
fi

# Unload the service
launchctl unload "$PLIST_FILE" 2>/dev/null

# Verify it stopped
sleep 1
if launchctl list | grep -q "com.natan.transcribe"; then
    echo -e "${RED}Failed to stop service${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Natan Transcribe service stopped successfully${NC}"
fi