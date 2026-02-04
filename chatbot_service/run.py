#!/usr/bin/env python3
"""
Standalone runner for the shopping assistant chatbot service.

This script provides a simple way to start the chatbot service independently
from the main e-commerce application.
"""

import sys
import signal
import asyncio
from pathlib import Path

# Add the parent directory to the Python path so we can import chatbot_service
sys.path.insert(0, str(Path(__file__).parent.parent))

from chatbot_service.app import app
from chatbot_service.config import Config
from chatbot_service.logger import logger
import uvicorn


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)


def main():
    """Main entry point for the chatbot service."""
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("=" * 60)
    logger.info("🤖 Shopping Assistant Chatbot Service")
    logger.info("=" * 60)
    logger.info(f"Port: {Config.CHATBOT_PORT}")
    logger.info(f"Backend API: {Config.BACKEND_API_URL}")
    logger.info(f"AWS Region: {Config.AWS_REGION}")
    logger.info(f"Model: {Config.BEDROCK_MODEL_ID}")
    logger.info(f"Auth Method: {Config.get_auth_method()}")
    logger.info("=" * 60)
    
    # Validate configuration
    if not Config.validate_aws_credentials():
        logger.error("❌ AWS credentials not configured properly!")
        logger.error("Please set one of the following:")
        logger.error("  - AWS_BEARER_TOKEN_BEDROCK (recommended for development)")
        logger.error("  - AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY")
        logger.error("  - Configure AWS credentials via 'aws configure'")
        sys.exit(1)
    
    logger.info("✅ Configuration validated")
    
    try:
        # Start the server
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=Config.CHATBOT_PORT,
            log_level=Config.LOG_LEVEL.lower(),
            access_log=True,
            reload=False  # Set to True for development
        )
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()