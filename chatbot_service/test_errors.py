"""Tests for error handling functionality."""

import pytest
from unittest.mock import patch

from chatbot_service.error_handler import (
    ErrorCode, ChatbotError, AuthenticationError, BackendError, 
    AgentError, ErrorHandler
)


class TestChatbotError:
    """Test cases for ChatbotError class."""
    
    def test_basic_error_creation(self):
        """Test creating a basic ChatbotError."""
        error = ChatbotError(
            message="Test error",
            error_code=ErrorCode.INTERNAL_ERROR
        )
        
        assert error.message == "Test error"
        assert error.error_code == ErrorCode.INTERNAL_ERROR
        assert error.details == {}
        assert error.retry_after is None
        assert "something went wrong" in error.user_message.lower()
    
    def test_error_with_details(self):
        """Test creating an error with details."""
        details = {"context": "test", "value": 123}
        error = ChatbotError(
            message="Detailed error",
            error_code=ErrorCode.BACKEND_ERROR,
            details=details,
            user_message="Custom user message",
            retry_after=30
        )
        
        assert error.details == details
        assert error.user_message == "Custom user message"
        assert error.retry_after == 30
    
    def test_error_to_dict(self):
        """Test converting error to dictionary."""
        error = ChatbotError(
            message="Test error",
            error_code=ErrorCode.RATE_LIMITED,
            details={"key": "value"},
            retry_after=60
        )
        
        error_dict = error.to_dict()
        
        assert error_dict["code"] == "rate_limited"
        assert "wait a moment" in error_dict["message"].lower()
        assert error_dict["details"] == {"key": "value"}
        assert error_dict["retry_after"] == 60
    
    def test_default_user_messages(self):
        """Test that default user messages are appropriate."""
        test_cases = [
            (ErrorCode.AUTH_FAILED, "ai service"),
            (ErrorCode.BACKEND_UNAVAILABLE, "product database"),
            (ErrorCode.SESSION_EXPIRED, "conversation has expired"),
            (ErrorCode.INVALID_INPUT, "rephrase"),
        ]
        
        for error_code, expected_phrase in test_cases:
            error = ChatbotError("Test", error_code)
            assert expected_phrase.lower() in error.user_message.lower()


class TestSpecificErrors:
    """Test cases for specific error types."""
    
    def test_authentication_error(self):
        """Test AuthenticationError creation."""
        error = AuthenticationError("Auth failed", details={"reason": "expired"})
        
        assert error.error_code == ErrorCode.AUTH_FAILED
        assert error.retry_after == 30
        assert error.details["reason"] == "expired"
    
    def test_backend_error(self):
        """Test BackendError creation."""
        error = BackendError(
            "Backend timeout",
            error_code=ErrorCode.BACKEND_TIMEOUT,
            retry_after=10
        )
        
        assert error.error_code == ErrorCode.BACKEND_TIMEOUT
        assert error.retry_after == 10
    
    def test_agent_error(self):
        """Test AgentError creation."""
        error = AgentError("Processing failed")
        
        assert error.error_code == ErrorCode.AGENT_PROCESSING_ERROR
        assert "processing your request" in error.user_message.lower()


class TestErrorHandler:
    """Test cases for ErrorHandler class."""
    
    def test_handle_chatbot_error(self):
        """Test handling an existing ChatbotError."""
        original_error = ChatbotError("Test", ErrorCode.INTERNAL_ERROR)
        
        with patch('chatbot_service.error_handler.logger') as mock_logger:
            result = ErrorHandler.handle_exception(original_error, "test_context")
            
            assert result is original_error
            mock_logger.error.assert_called_once()
    
    def test_handle_authentication_exception(self):
        """Test handling authentication-related exceptions."""
        exc = Exception("Invalid credentials provided")
        
        with patch('chatbot_service.error_handler.logger') as mock_logger:
            result = ErrorHandler.handle_exception(exc, "auth_test")
            
            assert isinstance(result, AuthenticationError)
            assert result.error_code == ErrorCode.AUTH_FAILED
            assert "auth_test" in result.details["context"]
    
    def test_handle_timeout_exception(self):
        """Test handling timeout exceptions."""
        exc = Exception("Request timeout occurred")
        
        with patch('chatbot_service.error_handler.logger') as mock_logger:
            result = ErrorHandler.handle_exception(exc, "timeout_test")
            
            assert isinstance(result, BackendError)
            assert result.error_code == ErrorCode.BACKEND_TIMEOUT
            assert result.retry_after == 10
    
    def test_handle_connection_exception(self):
        """Test handling connection exceptions."""
        exc = Exception("Connection refused")
        
        with patch('chatbot_service.error_handler.logger') as mock_logger:
            result = ErrorHandler.handle_exception(exc, "connection_test")
            
            assert isinstance(result, BackendError)
            assert result.error_code == ErrorCode.BACKEND_UNAVAILABLE
            assert result.retry_after == 30
    
    def test_handle_generic_exception(self):
        """Test handling generic exceptions."""
        exc = ValueError("Some random error")
        
        with patch('chatbot_service.error_handler.logger') as mock_logger:
            result = ErrorHandler.handle_exception(exc, "generic_test")
            
            assert isinstance(result, ChatbotError)
            assert result.error_code == ErrorCode.INTERNAL_ERROR
            assert "generic_test" in result.details["context"]
            assert "traceback" in result.details
    
    def test_create_fallback_response(self):
        """Test creating fallback responses."""
        error = BackendError("Backend down", ErrorCode.BACKEND_UNAVAILABLE)
        
        response = ErrorHandler.create_fallback_response(error, "test-session")
        
        assert response["session_id"] == "test-session"
        assert "product information" in response["response"].lower()
        assert len(response["suggestions"]) > 0
        assert "error" in response
        assert response["error"]["code"] == "backend_unavailable"
    
    def test_create_fallback_response_no_session(self):
        """Test creating fallback response without session ID."""
        error = AgentError("Processing failed")
        
        response = ErrorHandler.create_fallback_response(error)
        
        assert response["session_id"] == "new-session"
        assert len(response["suggestions"]) > 0
    
    def test_should_retry(self):
        """Test retry logic for different error types."""
        retryable_errors = [
            BackendError("Timeout", ErrorCode.BACKEND_TIMEOUT),
            BackendError("Unavailable", ErrorCode.BACKEND_UNAVAILABLE),
            ChatbotError("Rate limited", ErrorCode.RATE_LIMITED),
        ]
        
        non_retryable_errors = [
            ChatbotError("Invalid", ErrorCode.INVALID_INPUT),
            ChatbotError("Not found", ErrorCode.SESSION_NOT_FOUND),
        ]
        
        for error in retryable_errors:
            assert ErrorHandler.should_retry(error) is True
        
        for error in non_retryable_errors:
            assert ErrorHandler.should_retry(error) is False
    
    def test_get_retry_delay(self):
        """Test retry delay calculation."""
        # Test with explicit retry_after
        error_with_retry = BackendError("Test", retry_after=45)
        assert ErrorHandler.get_retry_delay(error_with_retry) == 45
        
        # Test with default delays
        timeout_error = BackendError("Timeout", ErrorCode.BACKEND_TIMEOUT)
        assert ErrorHandler.get_retry_delay(timeout_error) == 5
        
        unavailable_error = BackendError("Unavailable", ErrorCode.BACKEND_UNAVAILABLE)
        assert ErrorHandler.get_retry_delay(unavailable_error) == 30
        
        # Test unknown error type
        unknown_error = ChatbotError("Unknown", ErrorCode.INTERNAL_ERROR)
        assert ErrorHandler.get_retry_delay(unknown_error) == 30
    
    def test_log_error_metrics(self):
        """Test error metrics logging."""
        error = BackendError(
            "Test error",
            ErrorCode.BACKEND_TIMEOUT,
            details={"key": "value"},
            retry_after=15
        )
        
        with patch('chatbot_service.error_handler.logger') as mock_logger:
            ErrorHandler.log_error_metrics(error, "test_context")
            
            mock_logger.error.assert_called_once()
            call_args = mock_logger.error.call_args[0][0]
            assert "backend_timeout" in call_args
            assert "test_context" in call_args


if __name__ == "__main__":
    # Simple test to verify error handling works
    def test_error_handling():
        """Test basic error handling functionality."""
        
        # Test creating different error types
        auth_error = AuthenticationError("Auth failed")
        backend_error = BackendError("Backend down")
        agent_error = AgentError("Processing failed")
        
        print(f"✓ AuthenticationError: {auth_error.user_message}")
        print(f"✓ BackendError: {backend_error.user_message}")
        print(f"✓ AgentError: {agent_error.user_message}")
        
        # Test error handling
        generic_error = Exception("Something went wrong")
        handled_error = ErrorHandler.handle_exception(generic_error, "test")
        print(f"✓ Handled generic error: {handled_error.error_code.value}")
        
        # Test fallback response
        fallback = ErrorHandler.create_fallback_response(backend_error)
        print(f"✓ Fallback response has {len(fallback['suggestions'])} suggestions")
        
        print("Error handling is working correctly!")
    
    test_error_handling()