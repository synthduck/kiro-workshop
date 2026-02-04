"""Tests for the shopping assistant agent."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from chatbot_service.agent import ShoppingAssistant


class TestShoppingAssistant:
    """Test cases for the shopping assistant agent."""
    
    @pytest.fixture
    def assistant(self):
        """Create a shopping assistant for testing."""
        return ShoppingAssistant()
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, assistant):
        """Test successful agent initialization."""
        with patch.object(assistant.bedrock_client, 'authenticate', return_value=True), \
             patch.object(assistant.bedrock_client, 'create_agent') as mock_create_agent:
            
            mock_agent = MagicMock()
            mock_create_agent.return_value = mock_agent
            
            result = await assistant.initialize()
            
            assert result is True
            assert assistant.is_initialized() is True
            assert assistant.agent == mock_agent
            
            # Verify agent was created with tools and system prompt
            mock_create_agent.assert_called_once()
            call_args = mock_create_agent.call_args
            assert 'tools' in call_args[1]
            assert 'system_prompt' in call_args[1]
            assert len(call_args[1]['tools']) > 0  # Should have multiple tools
    
    @pytest.mark.asyncio
    async def test_initialize_authentication_failure(self, assistant):
        """Test initialization failure due to authentication."""
        with patch.object(assistant.bedrock_client, 'authenticate', return_value=False):
            result = await assistant.initialize()
            
            assert result is False
            assert assistant.is_initialized() is False
    
    @pytest.mark.asyncio
    async def test_process_message_success(self, assistant):
        """Test successful message processing."""
        # Mock initialization
        assistant._initialized = True
        mock_agent = MagicMock()
        mock_response = MagicMock()
        mock_response.message = "Hello! I can help you find products."
        mock_agent.return_value = mock_response
        assistant.agent = mock_agent
        
        with patch.object(assistant.session_manager, 'create_session', return_value='test-session'), \
             patch.object(assistant.session_manager, 'get_session') as mock_get_session, \
             patch.object(assistant.session_manager, 'add_message', return_value=True):
            
            mock_session = MagicMock()
            mock_get_session.return_value = mock_session
            
            result = await assistant.process_message("Hello")
            
            assert result['response'] == "Hello! I can help you find products."
            assert result['session_id'] == 'test-session'
            assert 'suggestions' in result
    
    @pytest.mark.asyncio
    async def test_process_message_not_initialized(self, assistant):
        """Test message processing when agent is not initialized."""
        result = await assistant.process_message("Hello")
        
        assert "not available" in result['response']
        assert 'error' in result
        assert result['error'] == "Agent not initialized"
    
    @pytest.mark.asyncio
    async def test_process_message_with_existing_session(self, assistant):
        """Test message processing with an existing session."""
        assistant._initialized = True
        mock_agent = MagicMock()
        mock_response = MagicMock()
        mock_response.message = "How can I help you today?"
        mock_agent.return_value = mock_response
        assistant.agent = mock_agent
        
        with patch.object(assistant.session_manager, 'get_session') as mock_get_session, \
             patch.object(assistant.session_manager, 'add_message', return_value=True):
            
            mock_session = MagicMock()
            mock_get_session.return_value = mock_session
            
            result = await assistant.process_message("Hello", session_id="existing-session")
            
            assert result['session_id'] == "existing-session"
            assert result['response'] == "How can I help you today?"
    
    def test_generate_suggestions_search_context(self, assistant):
        """Test suggestion generation for search context."""
        suggestions = assistant._generate_suggestions("search for phones", "Found 5 products")
        
        assert len(suggestions) <= 3
        assert any("products" in s.lower() for s in suggestions)
    
    def test_generate_suggestions_cart_context(self, assistant):
        """Test suggestion generation for cart context."""
        suggestions = assistant._generate_suggestions("add to cart", "Added to cart")
        
        assert len(suggestions) <= 3
        assert any("cart" in s.lower() for s in suggestions)
    
    def test_get_session_info_existing(self, assistant):
        """Test getting session info for existing session."""
        with patch.object(assistant.session_manager, 'get_session') as mock_get_session:
            mock_session = MagicMock()
            mock_session.created_at.isoformat.return_value = "2024-01-01T00:00:00"
            mock_session.last_activity.isoformat.return_value = "2024-01-01T01:00:00"
            mock_session.conversation_history = [{"role": "user", "content": "hello"}]
            mock_session.user_preferences = {"category": "electronics"}
            mock_get_session.return_value = mock_session
            
            info = assistant.get_session_info("test-session")
            
            assert info is not None
            assert info['session_id'] == "test-session"
            assert info['message_count'] == 1
            assert info['user_preferences'] == {"category": "electronics"}
    
    def test_get_session_info_not_found(self, assistant):
        """Test getting session info for non-existent session."""
        with patch.object(assistant.session_manager, 'get_session', return_value=None):
            info = assistant.get_session_info("non-existent")
            
            assert info is None
    
    def test_get_status(self, assistant):
        """Test getting assistant status."""
        with patch.object(assistant.bedrock_client, 'is_authenticated', return_value=True), \
             patch.object(assistant.bedrock_client, 'get_model_info', return_value={"model": "test"}), \
             patch.object(assistant.session_manager, 'get_active_session_count', return_value=5), \
             patch.object(assistant.session_manager, 'get_total_session_count', return_value=10):
            
            status = assistant.get_status()
            
            assert 'initialized' in status
            assert 'bedrock_authenticated' in status
            assert 'model_info' in status
            assert 'active_sessions' in status
            assert 'total_sessions' in status
            assert status['active_sessions'] == 5
            assert status['total_sessions'] == 10


if __name__ == "__main__":
    # Simple test to verify agent structure
    import asyncio
    
    async def test_agent():
        """Test agent initialization structure."""
        assistant = ShoppingAssistant()
        
        # Test that the system prompt is properly defined
        assert len(assistant.system_prompt) > 100
        assert "shopping assistant" in assistant.system_prompt.lower()
        
        # Test status before initialization
        status = assistant.get_status()
        assert status['initialized'] is False
        
        print("✓ Agent structure is correct")
        print(f"System prompt length: {len(assistant.system_prompt)} characters")
        print(f"Status keys: {list(status.keys())}")
    
    asyncio.run(test_agent())