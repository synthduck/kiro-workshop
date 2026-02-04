#!/bin/bash
# Start script for the shopping assistant chatbot service

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🤖 Starting Shopping Assistant Chatbot Service${NC}"
echo "=================================================="

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating one...${NC}"
    python3 -m venv .venv
fi

# Activate virtual environment
echo -e "${BLUE}📦 Activating virtual environment...${NC}"
source .venv/bin/activate

# Install/update dependencies
echo -e "${BLUE}📥 Installing dependencies...${NC}"
pip install -r requirements.txt

# Check for environment configuration
if [ ! -f ".env" ] && [ -z "$AWS_BEARER_TOKEN_BEDROCK" ] && [ -z "$AWS_ACCESS_KEY_ID" ]; then
    echo -e "${YELLOW}⚠️  No environment configuration found.${NC}"
    echo -e "${YELLOW}   Please copy .env.example to .env and configure your AWS credentials.${NC}"
    echo -e "${YELLOW}   Or set environment variables directly.${NC}"
    echo ""
    echo -e "${BLUE}Example:${NC}"
    echo "export AWS_BEARER_TOKEN_BEDROCK=your_bedrock_api_key"
    echo "export AWS_REGION=us-west-2"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Load environment variables if .env exists
if [ -f ".env" ]; then
    echo -e "${BLUE}🔧 Loading environment variables from .env...${NC}"
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check backend connectivity
echo -e "${BLUE}🔗 Checking backend connectivity...${NC}"
BACKEND_URL=${BACKEND_API_URL:-http://localhost:5000}
if curl -s --connect-timeout 5 "$BACKEND_URL/api/products" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is accessible at $BACKEND_URL${NC}"
else
    echo -e "${YELLOW}⚠️  Backend not accessible at $BACKEND_URL${NC}"
    echo -e "${YELLOW}   The chatbot will still start but may have limited functionality.${NC}"
fi

# Start the service
echo -e "${BLUE}🚀 Starting chatbot service...${NC}"
echo "=================================================="
python run.py