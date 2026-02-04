#!/bin/bash
"""
Startup script for the shopping assistant chatbot service.
"""

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Shopping Assistant Chatbot Service${NC}"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}Error: Virtual environment not found. Please run setup.sh first.${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source .venv/bin/activate

# Check if required environment variables are set
echo -e "${YELLOW}Checking configuration...${NC}"

# Check for AWS credentials
if [ -z "$AWS_ACCESS_KEY_ID" ] && [ -z "$AWS_BEARER_TOKEN_BEDROCK" ]; then
    echo -e "${YELLOW}Warning: No AWS credentials found. The service will start but AI features will not work.${NC}"
    echo -e "${YELLOW}Please set one of:${NC}"
    echo -e "${YELLOW}  - AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY${NC}"
    echo -e "${YELLOW}  - AWS_BEARER_TOKEN_BEDROCK${NC}"
fi

# Set default values for optional environment variables
export CHATBOT_PORT=${CHATBOT_PORT:-8000}
export CHATBOT_HOST=${CHATBOT_HOST:-0.0.0.0}
export BACKEND_API_URL=${BACKEND_API_URL:-http://localhost:5000}
export LOG_LEVEL=${LOG_LEVEL:-INFO}

echo -e "${GREEN}Configuration:${NC}"
echo -e "  Port: ${CHATBOT_PORT}"
echo -e "  Host: ${CHATBOT_HOST}"
echo -e "  Backend API: ${BACKEND_API_URL}"
echo -e "  Log Level: ${LOG_LEVEL}"

# Check if backend is accessible
echo -e "${YELLOW}Checking backend connectivity...${NC}"
if curl -s --connect-timeout 5 "${BACKEND_API_URL}/api/products" > /dev/null; then
    echo -e "${GREEN}✓ Backend is accessible${NC}"
else
    echo -e "${YELLOW}Warning: Backend is not accessible at ${BACKEND_API_URL}${NC}"
    echo -e "${YELLOW}The service will start but shopping features may not work properly.${NC}"
fi

# Start the service
echo -e "${GREEN}Starting chatbot service on ${CHATBOT_HOST}:${CHATBOT_PORT}...${NC}"
python app.py