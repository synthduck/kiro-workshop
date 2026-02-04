"""Session management for the shopping assistant chatbot."""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from .logger import logger


@dataclass
class Session:
    """Represents a user session with conversation history."""
    session_id: str
    created_at: datetime
    last_activity: datetime
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)


class SessionManager:
    """Manages user sessions and conversation history."""
    
    def __init__(self, session_timeout_minutes: int = 60):
        self.sessions: Dict[str, Session] = {}
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        logger.info(f"Session manager initialized with {session_timeout_minutes} minute timeout")
    
    def create_session(self) -> str:
        """Create a new session and return the session ID."""
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        session = Session(
            session_id=session_id,
            created_at=now,
            last_activity=now
        )
        
        self.sessions[session_id] = session
        logger.info(f"Created new session: {session_id}")
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID, or None if not found or expired."""
        if session_id not in self.sessions:
            logger.warning(f"Session not found: {session_id}")
            return None
        
        session = self.sessions[session_id]
        
        # Check if session has expired
        if self._is_session_expired(session):
            logger.info(f"Session expired: {session_id}")
            self._cleanup_session(session_id)
            return None
        
        # Update last activity
        session.last_activity = datetime.now()
        return session
    
    def add_message(self, session_id: str, role: str, content: str) -> bool:
        """Add a message to the session's conversation history."""
        session = self.get_session(session_id)
        if not session:
            logger.warning(f"Cannot add message to non-existent session: {session_id}")
            return False
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        session.conversation_history.append(message)
        session.last_activity = datetime.now()
        
        logger.debug(f"Added {role} message to session {session_id}")
        return True
    
    def get_conversation_history(self, session_id: str, limit: int = None) -> List[Dict[str, str]]:
        """Get the conversation history for a session."""
        session = self.get_session(session_id)
        if not session:
            return []
        
        history = session.conversation_history
        if limit:
            history = history[-limit:]  # Get last N messages
        
        return history
    
    def update_user_preferences(self, session_id: str, preferences: Dict[str, Any]) -> bool:
        """Update user preferences for a session."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.user_preferences.update(preferences)
        session.last_activity = datetime.now()
        
        logger.info(f"Updated preferences for session {session_id}: {preferences}")
        return True
    
    def get_user_preferences(self, session_id: str) -> Dict[str, Any]:
        """Get user preferences for a session."""
        session = self.get_session(session_id)
        if not session:
            return {}
        
        return session.user_preferences.copy()
    
    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions and return the count of removed sessions."""
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if self._is_session_expired(session):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self._cleanup_session(session_id)
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        
        return len(expired_sessions)
    
    def get_active_session_count(self) -> int:
        """Get the number of active (non-expired) sessions."""
        active_count = 0
        now = datetime.now()
        
        for session in self.sessions.values():
            if now - session.last_activity < self.session_timeout:
                active_count += 1
        
        return active_count
    
    def get_total_session_count(self) -> int:
        """Get the total number of sessions (including expired)."""
        return len(self.sessions)
    
    def delete_session(self, session_id: str) -> bool:
        """Manually delete a session."""
        if session_id in self.sessions:
            self._cleanup_session(session_id)
            logger.info(f"Manually deleted session: {session_id}")
            return True
        return False
    
    def _is_session_expired(self, session: Session) -> bool:
        """Check if a session has expired."""
        return datetime.now() - session.last_activity > self.session_timeout
    
    def _cleanup_session(self, session_id: str) -> None:
        """Remove a session from memory."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.debug(f"Cleaned up session: {session_id}")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about sessions."""
        now = datetime.now()
        active_sessions = 0
        total_messages = 0
        oldest_session = None
        newest_session = None
        
        for session in self.sessions.values():
            total_messages += len(session.conversation_history)
            
            if now - session.last_activity < self.session_timeout:
                active_sessions += 1
            
            if oldest_session is None or session.created_at < oldest_session:
                oldest_session = session.created_at
            
            if newest_session is None or session.created_at > newest_session:
                newest_session = session.created_at
        
        return {
            "total_sessions": len(self.sessions),
            "active_sessions": active_sessions,
            "expired_sessions": len(self.sessions) - active_sessions,
            "total_messages": total_messages,
            "oldest_session": oldest_session.isoformat() if oldest_session else None,
            "newest_session": newest_session.isoformat() if newest_session else None,
            "session_timeout_minutes": self.session_timeout.total_seconds() / 60
        }