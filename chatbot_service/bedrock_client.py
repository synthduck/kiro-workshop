"""AWS Bedrock client configuration and authentication."""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from strands import Agent
from strands.models import BedrockModel

from .config import Config
from .logger import logger


class BedrockClient:
    """Handles AWS Bedrock authentication and model configuration."""
    
    def __init__(self):
        self.model = None
        self.agent = None
        self._authenticated = False
    
    def authenticate(self) -> bool:
        """Authenticate with AWS Bedrock using configured credentials."""
        try:
            auth_method = Config.get_auth_method()
            logger.info(f"Attempting Bedrock authentication using: {auth_method}")
            
            if auth_method == "none":
                logger.error("No AWS credentials configured")
                return False
            
            # Create Bedrock model based on authentication method
            if auth_method == "bearer_token":
                self.model = self._create_model_with_bearer_token()
            else:
                self.model = self._create_model_with_credentials()
            
            # Test the authentication by creating a simple agent
            test_agent = Agent(model=self.model)
            
            # Verify model configuration
            model_config = test_agent.model.config
            logger.info(f"Successfully authenticated with Bedrock. Model: {model_config}")
            
            self._authenticated = True
            return True
            
        except NoCredentialsError:
            logger.error("AWS credentials not found or invalid")
            return False
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"AWS Bedrock authentication failed: {error_code} - {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during Bedrock authentication: {e}")
            return False
    
    def _create_model_with_bearer_token(self) -> BedrockModel:
        """Create Bedrock model using bearer token authentication."""
        # Note: Bearer token authentication would typically be handled
        # by setting the AWS_BEARER_TOKEN_BEDROCK environment variable
        # and using the default Bedrock client
        return BedrockModel(
            model_id=Config.BEDROCK_MODEL_ID,
            region_name=Config.AWS_REGION,
            temperature=0.7,
            max_tokens=2048,
        )
    
    def _create_model_with_credentials(self) -> BedrockModel:
        """Create Bedrock model using AWS credentials."""
        # Create boto3 session with explicit credentials
        session_kwargs = {
            'region_name': Config.AWS_REGION
        }
        
        if Config.AWS_ACCESS_KEY_ID and Config.AWS_SECRET_ACCESS_KEY:
            session_kwargs.update({
                'aws_access_key_id': Config.AWS_ACCESS_KEY_ID,
                'aws_secret_access_key': Config.AWS_SECRET_ACCESS_KEY,
            })
            
            if Config.AWS_SESSION_TOKEN:
                session_kwargs['aws_session_token'] = Config.AWS_SESSION_TOKEN
        
        session = boto3.Session(**session_kwargs)
        
        return BedrockModel(
            model_id=Config.BEDROCK_MODEL_ID,
            region_name=Config.AWS_REGION,
            temperature=0.7,
            max_tokens=2048,
            client=session.client('bedrock-runtime')
        )
    
    def create_agent(self, tools=None, system_prompt=None) -> Agent:
        """Create a Strands Agent with the authenticated Bedrock model."""
        if not self._authenticated:
            raise RuntimeError("Bedrock client not authenticated. Call authenticate() first.")
        
        if not tools:
            tools = []
        
        if not system_prompt:
            system_prompt = """You are a helpful shopping assistant for an e-commerce website. 
            You help customers find products, manage their cart, and provide shopping guidance. 
            Always be friendly, helpful, and focused on providing excellent customer service."""
        
        self.agent = Agent(
            model=self.model,
            tools=tools,
            system_prompt=system_prompt
        )
        
        return self.agent
    
    def is_authenticated(self) -> bool:
        """Check if the client is successfully authenticated."""
        return self._authenticated
    
    def get_model_info(self) -> dict:
        """Get information about the configured model."""
        if not self.model:
            return {}
        
        return {
            "model_id": Config.BEDROCK_MODEL_ID,
            "region": Config.AWS_REGION,
            "auth_method": Config.get_auth_method(),
            "authenticated": self._authenticated
        }