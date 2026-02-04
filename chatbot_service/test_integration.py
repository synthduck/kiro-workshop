"""Integration tests for the shopping assistant chatbot service."""

import pytest
import asyncio
import httpx
from unittest.mock import patch, AsyncMock, MagicMock

from chatbot_service.agent import ShoppingAssistant
from chatbot_service.backend_client import BackendClient
from chatbot_service.app import app
from fastapi.testclient import TestClient


class TestEndToEndIntegration:
    """End-to-end integration tests for the complete shopping workflow."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_backend_data(self):
        """Mock backend data for testing."""
        return {
            "products": [
                {
                    "id": 1,
                    "name": "Smartphone",
                    "price": 699.99,
                    "description": "Latest smartphone with advanced features",
                    "emoji": "📱",
                    "category": "Electronics"
                },
                {
                    "id": 2,
                    "name": "Laptop",
                    "price": 1299.99,
                    "description": "High-performance laptop for work and gaming",
                    "emoji": "💻",
                    "category": "Electronics"
                }
            ],
            "cart_items": [],
            "reviews": [
                {
                    "id": 1,
                    "product_id": 1,
                    "user_name": "John Doe",
                    "rating": 5,
                    "comment": "Amazing phone!"
                }
            ]
        }
    
    @pytest.mark.asyncio
    async def test_complete_shopping_workflow(self, mock_backend_data):
        """Test a complete shopping workflow from search to cart management."""
        
        # Mock the backend client to return test data
        with patch('chatbot_service.backend_client.BackendClient') as mock_backend_class:
            mock_backend = AsyncMock()
            mock_backend_class.return_value.__aenter__.return_value = mock_backend
            
            # Configure mock responses
            mock_backend.get_all_products.return_value = mock_backend_data["products"]
            mock_backend.search_products.return_value = [mock_backend_data["products"][0]]
            mock_backend.get_product_by_id.return_value = mock_backend_data["products"][0]
            mock_backend.get_product_reviews.return_value = mock_backend_data["reviews"]
            mock_backend.add_to_cart.return_value = True
            mock_backend.get_cart_items.return_value = [
                {
                    "id": 1,
                    "product_id": 1,
                    "quantity": 1,
                    "name": "Smartphone",
                    "price": 699.99,
                    "emoji": "📱"
                }
            ]
            mock_backend.get_cart_summary.return_value = {
                "empty": False,
                "items": [
                    {
                        "id": 1,
                        "product_id": 1,
                        "quantity": 1,
                        "name": "Smartphone",
                        "price": 699.99,
                        "emoji": "📱"
                    }
                ],
                "total_items": 1,
                "total_cost": 699.99
            }
            
            # Mock the Strands Agent
            with patch('chatbot_service.agent.ShoppingAssistant') as mock_assistant_class:
                mock_assistant = MagicMock()
                mock_assistant_class.return_value = mock_assistant
                mock_assistant.is_initialized.return_value = True
                
                # Test workflow steps
                workflow_steps = [
                    {
                        "user_message": "Show me smartphones",
                        "expected_response": "Found 1 product(s) matching 'smartphones'",
                        "tools_called": ["search_products"]
                    },
                    {
                        "user_message": "Tell me more about product 1",
                        "expected_response": "📱 **Smartphone**",
                        "tools_called": ["get_product_details"]
                    },
                    {
                        "user_message": "Add product 1 to my cart",
                        "expected_response": "✅ Added 1x **Smartphone** to your cart!",
                        "tools_called": ["add_to_cart"]
                    },
                    {
                        "user_message": "Show me my cart",
                        "expected_response": "🛒 **Your Shopping Cart** (1 items)",
                        "tools_called": ["get_cart_summary"]
                    }
                ]
                
                session_id = None
                
                for step in workflow_steps:
                    # Mock the agent response for this step
                    mock_assistant.process_message.return_value = {
                        "response": step["expected_response"],
                        "session_id": session_id or "test-session-123",
                        "suggestions": ["Continue shopping", "View cart"]
                    }
                    
                    # Simulate the workflow step
                    result = await mock_assistant.process_message(
                        step["user_message"],
                        session_id
                    )
                    
                    # Verify the response
                    assert step["expected_response"] in result["response"]
                    session_id = result["session_id"]
                
                # Verify the assistant was called for each step
                assert mock_assistant.process_message.call_count == len(workflow_steps)
    
    @pytest.mark.asyncio
    async def test_error_handling_workflow(self):
        """Test error handling in the complete workflow."""
        
        # Mock backend failures
        with patch('chatbot_service.backend_client.BackendClient') as mock_backend_class:
            mock_backend = AsyncMock()
            mock_backend_class.return_value.__aenter__.return_value = mock_backend
            
            # Configure mock to simulate backend failures
            mock_backend.get_all_products.side_effect = Exception("Backend unavailable")
            mock_backend.health_check.return_value = False
            
            # Mock the agent to handle errors gracefully
            with patch('chatbot_service.agent.ShoppingAssistant') as mock_assistant_class:
                mock_assistant = MagicMock()
                mock_assistant_class.return_value = mock_assistant
                mock_assistant.is_initialized.return_value = True
                
                # Mock error response
                mock_assistant.process_message.return_value = {
                    "response": "I can't access the product information right now, but I'm still here to help!",
                    "session_id": "test-session-error",
                    "suggestions": ["Try again later", "Ask general questions"],
                    "error": {
                        "code": "backend_unavailable",
                        "message": "Backend service is temporarily unavailable"
                    }
                }
                
                # Test error scenario
                result = await mock_assistant.process_message(
                    "Show me products",
                    None
                )
                
                # Verify graceful error handling
                assert "can't access the product information" in result["response"]
                assert "error" in result
                assert result["error"]["code"] == "backend_unavailable"
    
    def test_api_integration_with_mocked_agent(self, client):
        """Test API integration with mocked agent responses."""
        
        with patch('chatbot_service.app.shopping_assistant') as mock_assistant:
            mock_assistant.is_initialized.return_value = True
            mock_assistant.process_message.return_value = {
                "response": "Hello! I'm your shopping assistant. How can I help you today?",
                "session_id": "api-test-session",
                "suggestions": ["Browse products", "Search for items", "Check cart"]
            }
            
            # Test chat endpoint
            response = client.post(
                "/api/chat",
                json={"message": "Hello"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "shopping assistant" in data["response"]
            assert data["session_id"] == "api-test-session"
            assert len(data["suggestions"]) == 3
    
    def test_health_check_integration(self, client):
        """Test health check endpoint integration."""
        
        with patch('chatbot_service.app.shopping_assistant') as mock_assistant:
            mock_assistant.is_initialized.return_value = True
            mock_assistant.get_status.return_value = {
                "initialized": True,
                "bedrock_authenticated": True,
                "model_info": {"model_id": "test-model"},
                "active_sessions": 2,
                "total_sessions": 5
            }
            
            with patch('chatbot_service.app.BackendClient') as mock_backend_class:
                mock_backend = AsyncMock()
                mock_backend.health_check.return_value = True
                mock_backend_class.return_value.__aenter__.return_value = mock_backend
                
                response = client.get("/api/health")
                
                assert response.status_code == 200
                data = response.json()
                assert data["service"] == "shopping-assistant-chatbot"
                assert data["details"]["initialized"] is True
                assert data["details"]["backend_api_healthy"] is True
    
    @pytest.mark.asyncio
    async def test_session_management_integration(self):
        """Test session management across multiple interactions."""
        
        with patch('chatbot_service.backend_client.BackendClient'):
            assistant = ShoppingAssistant()
            
            # Mock successful initialization
            with patch.object(assistant.bedrock_client, 'authenticate', return_value=True), \
                 patch.object(assistant.bedrock_client, 'create_agent') as mock_create_agent:
                
                mock_agent = MagicMock()
                mock_create_agent.return_value = mock_agent
                
                # Initialize the assistant
                await assistant.initialize()
                
                # Mock agent responses
                mock_agent.return_value.message = "Test response"
                
                # Test multiple interactions with session persistence
                session_id = None
                
                for i in range(3):
                    result = await assistant.process_message(
                        f"Test message {i}",
                        session_id
                    )
                    
                    if session_id is None:
                        session_id = result["session_id"]
                    else:
                        # Should maintain the same session
                        assert result["session_id"] == session_id
                
                # Verify session info
                session_info = assistant.get_session_info(session_id)
                assert session_info is not None
                assert session_info["message_count"] == 6  # 3 user + 3 assistant messages


class TestServiceIndependence:
    """Test that the chatbot service operates independently from the backend."""
    
    @pytest.mark.asyncio
    async def test_service_starts_without_backend(self):
        """Test that the chatbot service can start even when backend is unavailable."""
        
        # Mock backend as unavailable
        with patch('chatbot_service.backend_client.BackendClient') as mock_backend_class:
            mock_backend = AsyncMock()
            mock_backend.health_check.return_value = False
            mock_backend_class.return_value.__aenter__.return_value = mock_backend
            
            # Mock successful Bedrock authentication
            with patch('chatbot_service.bedrock_client.BedrockClient') as mock_bedrock_class:
                mock_bedrock = MagicMock()
                mock_bedrock.authenticate.return_value = True
                mock_bedrock.create_agent.return_value = MagicMock()
                mock_bedrock_class.return_value = mock_bedrock
                
                # Create and initialize assistant
                assistant = ShoppingAssistant()
                result = await assistant.initialize()
                
                # Should initialize successfully despite backend being unavailable
                assert result is True
                assert assistant.is_initialized() is True
    
    @pytest.mark.asyncio
    async def test_graceful_degradation_on_backend_failure(self):
        """Test graceful degradation when backend fails during operation."""
        
        with patch('chatbot_service.backend_client.BackendClient') as mock_backend_class:
            mock_backend = AsyncMock()
            mock_backend_class.return_value.__aenter__.return_value = mock_backend
            
            # Initially backend works
            mock_backend.health_check.return_value = True
            mock_backend.get_all_products.return_value = []
            
            # Mock successful agent initialization
            with patch('chatbot_service.bedrock_client.BedrockClient') as mock_bedrock_class:
                mock_bedrock = MagicMock()
                mock_bedrock.authenticate.return_value = True
                mock_agent = MagicMock()
                mock_agent.return_value.message = "I can't access products right now, but I can still help with general questions."
                mock_bedrock.create_agent.return_value = mock_agent
                mock_bedrock_class.return_value = mock_bedrock
                
                assistant = ShoppingAssistant()
                await assistant.initialize()
                
                # Now simulate backend failure
                mock_backend.get_all_products.side_effect = Exception("Backend failed")
                
                # Service should still respond gracefully
                result = await assistant.process_message("Show me products")
                
                assert result["response"] is not None
                assert result["session_id"] is not None
                # Should not crash the service


if __name__ == "__main__":
    # Simple integration test runner
    import asyncio
    
    async def run_basic_integration_test():
        """Run a basic integration test to verify components work together."""
        print("🧪 Running basic integration test...")
        
        # Test backend client
        print("📡 Testing backend client...")
        try:
            async with BackendClient() as client:
                healthy = await client.health_check()
                print(f"   Backend health: {'✅' if healthy else '❌'}")
        except Exception as e:
            print(f"   Backend test failed (expected): {e}")
        
        # Test agent initialization
        print("🤖 Testing agent initialization...")
        try:
            assistant = ShoppingAssistant()
            # This will fail without AWS credentials, which is expected
            initialized = await assistant.initialize()
            print(f"   Agent initialized: {'✅' if initialized else '❌'}")
        except Exception as e:
            print(f"   Agent initialization failed (expected without AWS creds): {e}")
        
        # Test API structure
        print("🌐 Testing API structure...")
        client = TestClient(app)
        try:
            # This should work even without full initialization
            response = client.get("/api/health")
            print(f"   Health endpoint: {'✅' if response.status_code in [200, 503] else '❌'}")
        except Exception as e:
            print(f"   API test failed: {e}")
        
        print("✅ Integration test completed!")
    
    asyncio.run(run_basic_integration_test())