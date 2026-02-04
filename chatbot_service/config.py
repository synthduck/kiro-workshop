"""Configuration management for the chatbot service."""

import os
from typing import Optional


class Config:
    """Configuration class for environment variables and settings."""
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_SESSION_TOKEN: Optional[str] = os.getenv("AWS_SESSION_TOKEN")
    AWS_BEARER_TOKEN_BEDROCK: Optional[str] = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-west-2")
    
    # Service Configuration
    BACKEND_API_URL: str = os.getenv("BACKEND_API_URL", "http://localhost:5000")
    CHATBOT_PORT: int = int(os.getenv("CHATBOT_PORT", "8000"))
    
    # Bedrock Configuration
    BEDROCK_MODEL_ID: str = os.getenv("BEDROCK_MODEL_ID", "us.amazon.nova-pro-v1:0")
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate_aws_credentials(cls) -> bool:
        """Validate that AWS credentials are properly configured."""
        # Check for bearer token first (preferred for development)
        if cls.AWS_BEARER_TOKEN_BEDROCK:
            return True
            
        # Check for standard AWS credentials
        if cls.AWS_ACCESS_KEY_ID and cls.AWS_SECRET_ACCESS_KEY:
            return True
            
        return False
    
    @classmethod
    def get_auth_method(cls) -> str:
        """Get the authentication method being used."""
        if cls.AWS_BEARER_TOKEN_BEDROCK:
            return "bearer_token"
        elif cls.AWS_ACCESS_KEY_ID and cls.AWS_SECRET_ACCESS_KEY:
            return "aws_credentials"
        else:
            return "none"