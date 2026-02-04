"""Comprehensive error handling for the chatbot service."""

import traceback
from typing import Dict, Any, Optional
from enum import Enum

from .logger import logger


class ErrorCode(Enum):
    """Enumeration of error codes for the chatbot service."""
    
    # Authentication errors
    AUTH_FAILED = "authentication_failed"
    AUTH_EXPIRED = "authentication_expired"
    AUTH_INVALID = "invalid_credentials"
    
    # Backend API errors
    BACKEND_UNAVAILABLE = "backend_unavailable"
    BACKEND_TIMEOUT = "backend_timeout"
    BACKEND_ERROR = "backend_error"
    
    # Agent errors
    AGENT_NOT_INITIALIZED = "agent_not_initialized"
    AGENT_PROCESSING_ERROR = "agent_processing_error"
    MODEL_ERROR = "model_error"
    
    # Session errors
    SESSION_NOT_FOUND = "session_not_found"
    SESSION_EXPIRED = "session_expired"
    
    # Validation errors
    INVALID_INPUT = "invalid_input"
    MISSING_REQUIRED_FIELD = "missing_required_field"
    
    # Service errors
    SERVICE_UNAVAILABLE = "service_unavailable"
    INTERNAL_ERROR = "internal_error"
    RATE_LIMITED = "rate_limited"


class ChatbotError(Exception):
    """Base exception class for chatbot service errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
        retry_after: Optional[int] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.user_message = user_message or self._get_default_user_message()
        self.retry_after = retry_after
    
    def _get_default_user_message(self) -> str:
        """Get a user-friendly error message based on the error code."""
        user_messages = {
            ErrorCode.AUTH_FAILED: "I'm having trouble connecting to my AI service. Please try again in a moment.",
            ErrorCode.AUTH_EXPIRED: "My authentication has expired. Please try again.",
            ErrorCode.BACKEND_UNAVAILABLE: "I can't access the product database right now. Please try again later.",
            ErrorCode.BACKEND_TIMEOUT: "The product database is responding slowly. Please try again.",
            ErrorCode.AGENT_NOT_INITIALIZED: "I'm not ready to help yet. Please wait a moment and try again.",
            ErrorCode.AGENT_PROCESSING_ERROR: "I encountered an error while processing your request. Please try rephrasing your question.",
            ErrorCode.MODEL_ERROR: "I'm having trouble understanding your request. Please try again.",
            ErrorCode.SESSION_NOT_FOUND: "I couldn't find our conversation. Let's start fresh!",
            ErrorCode.SESSION_EXPIRED: "Our conversation has expired. Let's start a new one!",
            ErrorCode.INVALID_INPUT: "I didn't understand your request. Could you please rephrase it?",
            ErrorCode.SERVICE_UNAVAILABLE: "I'm temporarily unavailable. Please try again in a few minutes.",
            ErrorCode.INTERNAL_ERROR: "Something went wrong on my end. Please try again.",
            ErrorCode.RATE_LIMITED: "You're sending messages too quickly. Please wait a moment before trying again."
        }
        return user_messages.get(self.error_code, "I encountered an unexpected error. Please try again.")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the error to a dictionary for API responses."""
        error_dict = {
            "code": self.error_code.value,
            "message": self.user_message,
            "details": self.details
        }
        
        if self.retry_after:
            error_dict["retry_after"] = self.retry_after
        
        return error_dict


class AuthenticationError(ChatbotError):
    """Error related to authentication failures."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.AUTH_FAILED,
            details=details,
            retry_after=30
        )


class BackendError(ChatbotError):
    """Error related to backend API failures."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.BACKEND_ERROR,
        details: Optional[Dict[str, Any]] = None,
        retry_after: Optional[int] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            retry_after=retry_after
        )


class AgentError(ChatbotError):
    """Error related to agent processing failures."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.AGENT_PROCESSING_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            details=details
        )


class ErrorHandler:
    """Centralized error handling for the chatbot service."""
    
    @staticmethod
    def handle_exception(exc: Exception, context: str = "") -> ChatbotError:
        """Convert any exception to a ChatbotError with appropriate handling."""
        
        # If it's already a ChatbotError, just log and return it
        if isinstance(exc, ChatbotError):
            logger.error(f"ChatbotError in {context}: {exc.message}", exc_info=True)
            return exc
        
        # Handle specific exception types
        if "authentication" in str(exc).lower() or "credentials" in str(exc).lower():
            logger.error(f"Authentication error in {context}: {exc}")
            return AuthenticationError(
                message=str(exc),
                details={"context": context, "original_error": str(exc)}
            )
        
        if "timeout" in str(exc).lower():
            logger.error(f"Timeout error in {context}: {exc}")
            return BackendError(
                message=str(exc),
                error_code=ErrorCode.BACKEND_TIMEOUT,
                details={"context": context, "original_error": str(exc)},
                retry_after=10
            )
        
        if "connection" in str(exc).lower() or "network" in str(exc).lower():
            logger.error(f"Connection error in {context}: {exc}")
            return BackendError(
                message=str(exc),
                error_code=ErrorCode.BACKEND_UNAVAILABLE,
                details={"context": context, "original_error": str(exc)},
                retry_after=30
            )
        
        # Generic error handling
        logger.error(f"Unhandled exception in {context}: {exc}", exc_info=True)
        return ChatbotError(
            message=str(exc),
            error_code=ErrorCode.INTERNAL_ERROR,
            details={
                "context": context,
                "original_error": str(exc),
                "traceback": traceback.format_exc()
            }
        )
    
    @staticmethod
    def create_fallback_response(error: ChatbotError, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a fallback response when the agent fails to process a message."""
        
        fallback_responses = {
            ErrorCode.BACKEND_UNAVAILABLE: "I can't access the product information right now, but I'm still here to help! You can ask me general shopping questions or try again in a few minutes.",
            ErrorCode.BACKEND_TIMEOUT: "The product database is running slowly. Let me try to help you anyway, or you can try your request again in a moment.",
            ErrorCode.AGENT_PROCESSING_ERROR: "I had trouble understanding that request. Could you try asking in a different way? For example, you could ask 'show me electronics' or 'what's in my cart?'",
            ErrorCode.MODEL_ERROR: "I'm having some technical difficulties. Let me try to help you with something simpler - what are you looking to buy today?",
        }
        
        fallback_message = fallback_responses.get(
            error.error_code,
            "I apologize for the inconvenience. I'm having some technical issues, but I'm still here to help! What can I assist you with today?"
        )
        
        suggestions = [
            "Browse all products",
            "Check what's popular",
            "View my cart",
            "Get help with shopping"
        ]
        
        return {
            "response": fallback_message,
            "session_id": session_id or "new-session",
            "suggestions": suggestions,
            "error": error.to_dict()
        }
    
    @staticmethod
    def log_error_metrics(error: ChatbotError, context: str = ""):
        """Log error metrics for monitoring and alerting."""
        
        # Log structured error information
        error_info = {
            "error_code": error.error_code.value,
            "context": context,
            "user_message": error.user_message,
            "details": error.details,
            "retry_after": error.retry_after
        }
        
        logger.error(f"Error metrics: {error_info}")
        
        # In a production environment, you might send these metrics to
        # monitoring systems like CloudWatch, Datadog, etc.
        
    @staticmethod
    def should_retry(error: ChatbotError) -> bool:
        """Determine if an operation should be retried based on the error."""
        
        retryable_errors = {
            ErrorCode.BACKEND_TIMEOUT,
            ErrorCode.BACKEND_UNAVAILABLE,
            ErrorCode.AUTH_EXPIRED,
            ErrorCode.RATE_LIMITED
        }
        
        return error.error_code in retryable_errors
    
    @staticmethod
    def get_retry_delay(error: ChatbotError) -> int:
        """Get the recommended retry delay in seconds."""
        
        if error.retry_after:
            return error.retry_after
        
        delay_map = {
            ErrorCode.BACKEND_TIMEOUT: 5,
            ErrorCode.BACKEND_UNAVAILABLE: 30,
            ErrorCode.AUTH_EXPIRED: 10,
            ErrorCode.RATE_LIMITED: 60,
            ErrorCode.INTERNAL_ERROR: 30
        }
        
        return delay_map.get(error.error_code, 10)