"""Pydantic models for the chatbot service API."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., description="The user's message to the chatbot", min_length=1)
    session_id: Optional[str] = Field(None, description="Optional session ID for conversation continuity")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional context information")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="The chatbot's response message")
    session_id: str = Field(..., description="Session ID for conversation continuity")
    suggestions: Optional[List[str]] = Field(None, description="Suggested follow-up actions or questions")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Health status of the service")
    service: str = Field(..., description="Service name")
    timestamp: str = Field(..., description="Current timestamp")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional health check details")


class ErrorResponse(BaseModel):
    """Response model for error cases."""
    error: Dict[str, Any] = Field(..., description="Error information")
    session_id: Optional[str] = Field(None, description="Session ID if available")


class SessionInfoResponse(BaseModel):
    """Response model for session information."""
    session_id: str = Field(..., description="Session ID")
    created_at: str = Field(..., description="Session creation timestamp")
    last_activity: str = Field(..., description="Last activity timestamp")
    message_count: int = Field(..., description="Number of messages in conversation")
    user_preferences: Dict[str, Any] = Field(..., description="User preferences for this session")


class StatusResponse(BaseModel):
    """Response model for service status."""
    initialized: bool = Field(..., description="Whether the agent is initialized")
    bedrock_authenticated: bool = Field(..., description="Whether Bedrock authentication is successful")
    model_info: Dict[str, Any] = Field(..., description="Information about the configured model")
    active_sessions: int = Field(..., description="Number of active sessions")
    total_sessions: int = Field(..., description="Total number of sessions")