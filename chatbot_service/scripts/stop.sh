#!/bin/bash
# Stop script for the shopping assistant chatbot service

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🛑 Stopping Shopping Assistant Chatbot Service${NC}"
echo "=================================================="

# Find and kill the chatbot service process
CHATBOT_PID=$(pgrep -f "python.*run.py" || echo "")

if [ -n "$CHATBOT_PID" ]; then
    echo -e "${YELLOW}📍 Found chatbot service running with PID: $CHATBOT_PID${NC}"
    echo -e "${BLUE}🔄 Sending SIGTERM signal...${NC}"
    
    kill -TERM $CHATBOT_PID
    
    # Wait for graceful shutdown
    sleep 3
    
    # Check if process is still running
    if kill -0 $CHATBOT_PID 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Process still running, sending SIGKILL...${NC}"
        kill -KILL $CHATBOT_PID
        sleep 1
    fi
    
    echo -e "${GREEN}✅ Chatbot service stopped successfully${NC}"
else
    echo -e "${YELLOW}⚠️  No chatbot service process found${NC}"
fi

# Also check for any uvicorn processes on the chatbot port
UVICORN_PID=$(lsof -ti:8000 2>/dev/null || echo "")

if [ -n "$UVICORN_PID" ]; then
    echo -e "${YELLOW}📍 Found process using port 8000: $UVICORN_PID${NC}"
    kill -TERM $UVICORN_PID 2>/dev/null || true
    sleep 2
    kill -KILL $UVICORN_PID 2>/dev/null || true
    echo -e "${GREEN}✅ Port 8000 freed${NC}"
fi

echo -e "${GREEN}🏁 Shutdown complete${NC}"