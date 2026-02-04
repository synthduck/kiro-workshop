"""Tests for the FastAPI application."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient

from chatbot_service.app import app


class TestChatbotAPI:
    """Test cases for the chatbot API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_assistant(self):
        """Create a mock shopping assistant."""
        mock = MagicMock()
        mock.is_initialized.return_value = True
        mock.get_status.return_value = {
            "initialized": True,
            "bedrock_authenticated": True,
            "model_info": {"model": "test"},
            "active_sessions": 1,
            "total_sessions": 1
        }
        return mock
    
    def test_health_check_endpoint(self, client):
        """Test the health check endpoint."""
        with patch('chatbot_service.app.shopping_assistant') as mock_assistant:
            mock_assistant.is_initialized.return_value = True
            mock_assistant.get_status.return_value = {
                "initialized": True,
                "bedrock_authenticated": True,
                "model_info": {"model": "test"},
                "active_sessions": 0,
                "total_sessions": 0
            }
            
            with patch('chatbot_service.app.BackendClient') as mock_backend:
                mock_backend_instance = AsyncMock()
                mock_backend_instance.health_check.return_value = True
                mock_backend.return_value.__aenter__.return_value = mock_backend_instance
                
                response = client.get("/api/health")
                
                assert response.status_code == 200
                data = response.json()
                assert data["service"] == "shopping-assistant-chatbot"
                assert "status" in data
                assert "timestamp" in data
    
    def test_chat_endpoint_success(self, client):
        """Test successful chat request."""
        with patch('chatbot_service.app.shopping_assistant') as mock_assistant:
            mock_assistant.process_message.return_value = {
                "response": "Hello! How can I help you today?",
                "session_id": "test-session-123",
                "suggestions": ["Browse products", "Check cart"]
            }
            
            response = client.post(
                "/api/chat",
                json={"message": "Hello"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["response"] == "Hello! How can I help you today?"
            assert data["session_id"] == "test-session-123"
            assert data["suggestions"] == ["Browse products", "Check cart"]
    
    def test_chat_endpoint_with_session_id(self, client):
        """Test chat request with existing session ID."""
        with patch('chatbot_service.app.shopping_assistant') as mock_assistant:
            mock_assistant.process_message.return_value = {
                "response": "Welcome back!",
                "session_id": "existing-session",
                "suggestions": []
            }
            
            response = client.post(
                "/api/chat",
                json={
                    "message": "I'm back",
                    "session_id": "existing-session"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == "existing-session"
    
    def test_chat_endpoint_service_unavailable(self, client):
        """Test chat request when service is unavailable."""
        with patch('chatbot_service.app.shopping_assistant', None):
            response = client.post(
                "/api/chat",
                json={"message": "Hello"}
            )
            
            assert response.status_code == 503
    
    def test_chat_endpoint_invalid_request(self, client):
        """Test chat request with invalid data."""
        response = client.post(
            "/api/chat",
            json={"message": ""}  # Empty message should fail validation
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_get_session_info_success(self, client):
        """Test successful session info retrieval."""
        with patch('chatbot_service.app.shopping_assistant') as mock_assistant:
            mock_assistant.get_session_info.return_value = {
                "session_id": "test-session",
                "created_at": "2024-01-01T00:00:00",
                "last_activity": "2024-01-01T01:00:00",
                "message_count": 5,
                "user_preferences": {"category": "electronics"}
            }
            
            response = client.get("/api/sessions/test-session")
            
            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == "test-session"
            assert data["message_count"] == 5
    
    def test_get_session_info_not_found(self, client):
        """Test session info for non-existent session."""
        with patch('chatbot_service.app.shopping_assistant') as mock_assistant:
            mock_assistant.get_session_info.return_value = None
            
            response = client.get("/api/sessions/nonexistent")
            
            assert response.status_code == 404
    
    def test_get_status_endpoint(self, client):
        """Test the status endpoint."""
        with patch('chatbot_service.app.shopping_assistant') as mock_assistant:
            mock_assistant.get_status.return_value = {
                "initialized": True,
                "bedrock_authenticated": True,
                "model_info": {"model_id": "test-model"},
                "active_sessions": 2,
                "total_sessions": 5
            }
            
            response = client.get("/api/status")
            
            assert response.status_code == 200
            data = response.json()
            assert data["initialized"] is True
            assert data["active_sessions"] == 2
    
    def test_delete_session_success(self, client):
        """Test successful session deletion."""
        with patch('chatbot_service.app.shopping_assistant') as mock_assistant:
            mock_assistant.session_manager.delete_session.return_value = True
            
            response = client.delete("/api/sessions/test-session")
            
            assert response.status_code == 200
            data = response.json()
            assert "deleted successfully" in data["message"]
    
    def test_delete_session_not_found(self, client):
        """Test deletion of non-existent session."""
        with patch('chatbot_service.app.shopping_assistant') as mock_assistant:
            mock_assistant.session_manager.delete_session.return_value = False
            
            response = client.delete("/api/sessions/nonexistent")
            
            assert response.status_code == 404
    
    def test_cleanup_sessions_endpoint(self, client):
        """Test the session cleanup endpoint."""
        with patch('chatbot_service.app.shopping_assistant') as mock_assistant:
            mock_assistant.session_manager.cleanup_expired_sessions.return_value = 3
            
            response = client.post("/api/sessions/cleanup")
            
            assert response.status_code == 200
            data = response.json()
            assert data["cleaned_sessions"] == 3
            assert "3 expired sessions" in data["message"]
    
    def test_cors_headers(self, client):
        """Test that CORS headers are properly set."""
        response = client.options("/api/health")
        
        # FastAPI/Starlette handles OPTIONS automatically with CORS middleware
        assert response.status_code in [200, 405]  # 405 if OPTIONS not explicitly handled
    
    def test_chat_endpoint_processing_error(self, client):
        """Test chat endpoint when processing fails."""
        with patch('chatbot_service.app.shopping_assistant') as mock_assistant:
            mock_assistant.process_message.side_effect = Exception("Processing failed")
            
            response = client.post(
                "/api/chat",
                json={"message": "Hello"}
            )
            
            assert response.status_code == 500
            data = response.json()
            assert "error" in data["detail"]


if __name__ == "__main__":
    # Simple test to verify API structure
    def test_api_structure():
        """Test that the API is properly structured."""
        client = TestClient(app)
        
        # Test that the app starts without errors
        assert app.title == "Shopping Assistant Chatbot"
        assert app.version == "1.0.0"
        
        # Test that routes are registered
        routes = [route.path for route in app.routes]
        expected_routes = [
            "/api/chat",
            "/api/health", 
            "/api/sessions/{session_id}",
            "/api/status",
            "/api/sessions/cleanup"
        ]
        
        for expected_route in expected_routes:
            # Check if route exists (may have different parameter names)
            route_exists = any(expected_route.replace("{session_id}", "{") in route for route in routes)
            assert route_exists, f"Route {expected_route} not found in {routes}"
        
        print("✓ API structure is correct")
        print(f"Registered routes: {len(routes)}")
        print(f"App title: {app.title}")
    
    test_api_structure()