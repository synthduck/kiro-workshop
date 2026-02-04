"""Tests for AWS Bedrock authentication."""

import os
import pytest
from unittest.mock import patch, MagicMock

from .bedrock_client import BedrockClient
from .config import Config


class TestBedrockAuthentication:
    """Test cases for Bedrock authentication functionality."""
    
    def test_no_credentials_configured(self):
        """Test authentication fails when no credentials are configured."""
        with patch.dict(os.environ, {}, clear=True):
            # Clear all AWS environment variables
            Config.AWS_ACCESS_KEY_ID = None
            Config.AWS_SECRET_ACCESS_KEY = None
            Config.AWS_SESSION_TOKEN = None
            Config.AWS_BEARER_TOKEN_BEDROCK = None
            
            client = BedrockClient()
            result = client.authenticate()
            
            assert result is False
            assert not client.is_authenticated()
    
    def test_bearer_token_authentication(self):
        """Test authentication with bearer token."""
        with patch.dict(os.environ, {
            'AWS_BEARER_TOKEN_BEDROCK': 'test-bearer-token',
            'AWS_REGION': 'us-west-2'
        }):
            Config.AWS_BEARER_TOKEN_BEDROCK = 'test-bearer-token'
            Config.AWS_REGION = 'us-west-2'
            
            with patch('chatbot_service.bedrock_client.Agent') as mock_agent:
                mock_agent_instance = MagicMock()
                mock_agent_instance.model.config = {'model_id': 'us.amazon.nova-pro-v1:0'}
                mock_agent.return_value = mock_agent_instance
                
                client = BedrockClient()
                result = client.authenticate()
                
                assert result is True
                assert client.is_authenticated()
                assert Config.get_auth_method() == "bearer_token"
    
    def test_aws_credentials_authentication(self):
        """Test authentication with AWS access keys."""
        with patch.dict(os.environ, {
            'AWS_ACCESS_KEY_ID': 'test-access-key',
            'AWS_SECRET_ACCESS_KEY': 'test-secret-key',
            'AWS_REGION': 'us-west-2'
        }):
            Config.AWS_ACCESS_KEY_ID = 'test-access-key'
            Config.AWS_SECRET_ACCESS_KEY = 'test-secret-key'
            Config.AWS_BEARER_TOKEN_BEDROCK = None
            Config.AWS_REGION = 'us-west-2'
            
            with patch('chatbot_service.bedrock_client.Agent') as mock_agent, \
                 patch('boto3.Session') as mock_session:
                
                mock_agent_instance = MagicMock()
                mock_agent_instance.model.config = {'model_id': 'us.amazon.nova-pro-v1:0'}
                mock_agent.return_value = mock_agent_instance
                
                mock_session_instance = MagicMock()
                mock_session.return_value = mock_session_instance
                
                client = BedrockClient()
                result = client.authenticate()
                
                assert result is True
                assert client.is_authenticated()
                assert Config.get_auth_method() == "aws_credentials"
    
    def test_aws_credentials_with_session_token(self):
        """Test authentication with AWS access keys and session token."""
        with patch.dict(os.environ, {
            'AWS_ACCESS_KEY_ID': 'test-access-key',
            'AWS_SECRET_ACCESS_KEY': 'test-secret-key',
            'AWS_SESSION_TOKEN': 'test-session-token',
            'AWS_REGION': 'us-west-2'
        }):
            Config.AWS_ACCESS_KEY_ID = 'test-access-key'
            Config.AWS_SECRET_ACCESS_KEY = 'test-secret-key'
            Config.AWS_SESSION_TOKEN = 'test-session-token'
            Config.AWS_BEARER_TOKEN_BEDROCK = None
            Config.AWS_REGION = 'us-west-2'
            
            with patch('chatbot_service.bedrock_client.Agent') as mock_agent, \
                 patch('boto3.Session') as mock_session:
                
                mock_agent_instance = MagicMock()
                mock_agent_instance.model.config = {'model_id': 'us.amazon.nova-pro-v1:0'}
                mock_agent.return_value = mock_agent_instance
                
                mock_session_instance = MagicMock()
                mock_session.return_value = mock_session_instance
                
                client = BedrockClient()
                result = client.authenticate()
                
                assert result is True
                assert client.is_authenticated()
                
                # Verify session was created with session token
                mock_session.assert_called_once()
                call_args = mock_session.call_args[1]
                assert 'aws_session_token' in call_args
                assert call_args['aws_session_token'] == 'test-session-token'
    
    def test_create_agent_without_authentication(self):
        """Test that creating an agent fails without authentication."""
        client = BedrockClient()
        
        with pytest.raises(RuntimeError, match="Bedrock client not authenticated"):
            client.create_agent()
    
    def test_create_agent_with_custom_tools_and_prompt(self):
        """Test creating an agent with custom tools and system prompt."""
        client = BedrockClient()
        client._authenticated = True
        client.model = MagicMock()
        
        mock_tools = [MagicMock()]
        custom_prompt = "Custom shopping assistant prompt"
        
        with patch('chatbot_service.bedrock_client.Agent') as mock_agent:
            mock_agent_instance = MagicMock()
            mock_agent.return_value = mock_agent_instance
            
            agent = client.create_agent(tools=mock_tools, system_prompt=custom_prompt)
            
            mock_agent.assert_called_once_with(
                model=client.model,
                tools=mock_tools,
                system_prompt=custom_prompt
            )
            assert agent == mock_agent_instance
    
    def test_get_model_info(self):
        """Test getting model information."""
        client = BedrockClient()
        client.model = MagicMock()
        client._authenticated = True
        
        with patch.object(Config, 'BEDROCK_MODEL_ID', 'us.amazon.nova-pro-v1:0'), \
             patch.object(Config, 'AWS_REGION', 'us-west-2'), \
             patch.object(Config, 'get_auth_method', return_value='bearer_token'):
            
            info = client.get_model_info()
            
            expected = {
                "model_id": "us.amazon.nova-pro-v1:0",
                "region": "us-west-2",
                "auth_method": "bearer_token",
                "authenticated": True
            }
            
            assert info == expected


if __name__ == "__main__":
    # Run a simple test to verify authentication works
    client = BedrockClient()
    if client.authenticate():
        print("✓ Bedrock authentication successful")
        model_info = client.get_model_info()
        print(f"Model info: {model_info}")
    else:
        print("✗ Bedrock authentication failed")
        print("Make sure AWS credentials are configured properly")