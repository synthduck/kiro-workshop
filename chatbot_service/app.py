"""FastAPI application for the shopping assistant chatbot service."""

import asyncio
from datetime import datetime
from typing import Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .agent import ShoppingAssistant
from .models import (
    ChatRequest, ChatResponse, HealthResponse, ErrorResponse,
    SessionInfoResponse, StatusResponse
)
from .config import Config
from .logger import logger


# Global shopping assistant instance
shopping_assistant = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown."""
    global shopping_assistant
    
    # Startup
    logger.info("Starting shopping assistant chatbot service...")
    
    try:
        shopping_assistant = ShoppingAssistant()
        
        # Initialize the agent
        if await shopping_assistant.initialize():
            logger.info("Shopping assistant initialized successfully")
        else:
            logger.error("Failed to initialize shopping assistant")
            # Continue anyway - the service can still provide error responses
        
        # Start background task for session cleanup
        cleanup_task = asyncio.create_task(periodic_cleanup())
        
        yield
        
        # Shutdown
        logger.info("Shutting down shopping assistant chatbot service...")
        cleanup_task.cancel()
        
    except Exception as e:
        logger.error(f"Error during application lifespan: {e}")
        yield


async def periodic_cleanup():
    """Periodically clean up expired sessions."""
    while True:
        try:
            await asyncio.sleep(300)  # Run every 5 minutes
            if shopping_assistant:
                cleaned = shopping_assistant.session_manager.cleanup_expired_sessions()
                if cleaned > 0:
                    logger.info(f"Cleaned up {cleaned} expired sessions")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error during session cleanup: {e}")


# Create FastAPI application
app = FastAPI(
    title="Shopping Assistant Chatbot",
    description="AI-powered shopping assistant using Strands Agents SDK and AWS Bedrock Nova Pro",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_server_error",
                "message": "An internal server error occurred. Please try again later.",
                "details": str(exc) if Config.LOG_LEVEL == "DEBUG" else None
            }
        }
    )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process a chat message and return the assistant's response.
    
    This endpoint handles user messages, maintains conversation context,
    and returns AI-generated responses with helpful suggestions.
    """
    if not shopping_assistant:
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "service_unavailable",
                    "message": "Shopping assistant service is not available",
                    "retry_after": 30
                }
            }
        )
    
    try:
        logger.info(f"Processing chat request: {request.message[:100]}...")
        
        # Process the message
        result = await shopping_assistant.process_message(
            message=request.message,
            session_id=request.session_id
        )
        
        # Handle errors in the result
        if "error" in result:
            logger.warning(f"Error in message processing: {result['error']}")
            # Still return the response, but log the error
        
        return ChatResponse(
            response=result["response"],
            session_id=result["session_id"],
            suggestions=result.get("suggestions")
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "processing_error",
                    "message": "Failed to process your message. Please try again.",
                    "details": str(e) if Config.LOG_LEVEL == "DEBUG" else None
                }
            }
        )


@app.get("/api/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint to verify service status.
    
    Returns the current health status of the chatbot service,
    including initialization status and dependency health.
    """
    try:
        details = {}
        
        if shopping_assistant:
            status = shopping_assistant.get_status()
            details.update(status)
            
            # Check backend connectivity
            from .backend_client import BackendClient
            async with BackendClient() as client:
                backend_healthy = await client.health_check()
                details["backend_api_healthy"] = backend_healthy
        else:
            details["error"] = "Shopping assistant not initialized"
        
        return HealthResponse(
            status="healthy" if shopping_assistant and shopping_assistant.is_initialized() else "degraded",
            service="shopping-assistant-chatbot",
            timestamp=datetime.now().isoformat(),
            details=details
        )
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return HealthResponse(
            status="unhealthy",
            service="shopping-assistant-chatbot",
            timestamp=datetime.now().isoformat(),
            details={"error": str(e)}
        )


@app.get("/api/sessions/{session_id}", response_model=SessionInfoResponse)
async def get_session_info(session_id: str) -> SessionInfoResponse:
    """
    Get information about a specific session.
    
    Returns session details including creation time, activity,
    and conversation statistics.
    """
    if not shopping_assistant:
        raise HTTPException(status_code=503, detail="Service not available")
    
    session_info = shopping_assistant.get_session_info(session_id)
    
    if not session_info:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "session_not_found",
                    "message": f"Session {session_id} not found or expired"
                }
            }
        )
    
    return SessionInfoResponse(**session_info)


@app.get("/api/status", response_model=StatusResponse)
async def get_status() -> StatusResponse:
    """
    Get the current status of the shopping assistant service.
    
    Returns detailed information about service initialization,
    authentication status, and session statistics.
    """
    if not shopping_assistant:
        raise HTTPException(status_code=503, detail="Service not available")
    
    status = shopping_assistant.get_status()
    return StatusResponse(**status)


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str) -> Dict[str, str]:
    """
    Delete a specific session and its conversation history.
    
    This endpoint allows manual cleanup of sessions.
    """
    if not shopping_assistant:
        raise HTTPException(status_code=503, detail="Service not available")
    
    success = shopping_assistant.session_manager.delete_session(session_id)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "session_not_found",
                    "message": f"Session {session_id} not found"
                }
            }
        )
    
    return {"message": f"Session {session_id} deleted successfully"}


@app.post("/api/sessions/cleanup")
async def cleanup_sessions() -> Dict[str, Any]:
    """
    Manually trigger cleanup of expired sessions.
    
    Returns the number of sessions that were cleaned up.
    """
    if not shopping_assistant:
        raise HTTPException(status_code=503, detail="Service not available")
    
    cleaned_count = shopping_assistant.session_manager.cleanup_expired_sessions()
    
    return {
        "message": f"Cleaned up {cleaned_count} expired sessions",
        "cleaned_sessions": cleaned_count
    }


if __name__ == "__main__":
    # Run the server
    logger.info(f"Starting chatbot service on port {Config.CHATBOT_PORT}")
    
    uvicorn.run(
        "chatbot_service.app:app",
        host="0.0.0.0",
        port=Config.CHATBOT_PORT,
        reload=False,  # Set to True for development
        log_level=Config.LOG_LEVEL.lower()
    )