"""Logging configuration for the chatbot service."""

import logging
import sys
from typing import Optional

from .config import Config


def setup_logging(level: Optional[str] = None) -> logging.Logger:
    """Set up structured logging for the chatbot service."""
    
    log_level = level or Config.LOG_LEVEL
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    # Create service logger
    logger = logging.getLogger("chatbot_service")
    
    # Set Strands SDK logging to INFO to avoid debug noise
    logging.getLogger("strands").setLevel(logging.INFO)
    
    return logger


# Global logger instance
logger = setup_logging()