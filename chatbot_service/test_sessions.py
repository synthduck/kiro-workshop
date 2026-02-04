"""Tests for session management."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from chatbot_service.session_manager import SessionManager, Session


class TestSessionManager:
    """Test cases for session management."""
    
    @pytest.fixture
    def session_manager(self):
        """Create a session manager for testing."""
        return SessionManager(session_timeout_minutes=30)
    
    def test_create_session(self, session_manager):
        """Test session creation."""
        session_id = session_manager.create_session()
        
        assert session_id is not None
        assert len(session_id) > 0
        assert session_id in session_manager.sessions
        
        session = session_manager.sessions[session_id]
        assert session.session_id == session_id
        assert isinstance(session.created_at, datetime)
        assert isinstance(session.last_activity, datetime)
        assert session.conversation_history == []
        assert session.user_preferences == {}
    
    def test_get_existing_session(self, session_manager):
        """Test retrieving an existing session."""
        session_id = session_manager.create_session()
        
        retrieved_session = session_manager.get_session(session_id)
        
        assert retrieved_session is not None
        assert retrieved_session.session_id == session_id
    
    def test_get_nonexistent_session(self, session_manager):
        """Test retrieving a non-existent session."""
        session = session_manager.get_session("nonexistent-id")
        
        assert session is None
    
    def test_add_message(self, session_manager):
        """Test adding messages to a session."""
        session_id = session_manager.create_session()
        
        # Add user message
        result = session_manager.add_message(session_id, "user", "Hello")
        assert result is True
        
        # Add assistant message
        result = session_manager.add_message(session_id, "assistant", "Hi there!")
        assert result is True
        
        # Check conversation history
        history = session_manager.get_conversation_history(session_id)
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello"
        assert history[1]["role"] == "assistant"
        assert history[1]["content"] == "Hi there!"
        assert "timestamp" in history[0]
    
    def test_add_message_to_nonexistent_session(self, session_manager):
        """Test adding message to non-existent session."""
        result = session_manager.add_message("nonexistent", "user", "Hello")
        assert result is False
    
    def test_get_conversation_history_with_limit(self, session_manager):
        """Test getting conversation history with limit."""
        session_id = session_manager.create_session()
        
        # Add multiple messages
        for i in range(5):
            session_manager.add_message(session_id, "user", f"Message {i}")
        
        # Get limited history
        history = session_manager.get_conversation_history(session_id, limit=3)
        assert len(history) == 3
        assert history[0]["content"] == "Message 2"  # Last 3 messages
        assert history[2]["content"] == "Message 4"
    
    def test_update_user_preferences(self, session_manager):
        """Test updating user preferences."""
        session_id = session_manager.create_session()
        
        preferences = {"favorite_category": "Electronics", "budget": 1000}
        result = session_manager.update_user_preferences(session_id, preferences)
        
        assert result is True
        
        retrieved_prefs = session_manager.get_user_preferences(session_id)
        assert retrieved_prefs == preferences
    
    def test_update_preferences_nonexistent_session(self, session_manager):
        """Test updating preferences for non-existent session."""
        result = session_manager.update_user_preferences("nonexistent", {"key": "value"})
        assert result is False
    
    def test_session_expiration(self, session_manager):
        """Test session expiration logic."""
        session_id = session_manager.create_session()
        
        # Manually set last activity to past the timeout
        session = session_manager.sessions[session_id]
        session.last_activity = datetime.now() - timedelta(minutes=35)  # 35 minutes ago
        
        # Try to get the session - should be None due to expiration
        retrieved_session = session_manager.get_session(session_id)
        assert retrieved_session is None
        
        # Session should be cleaned up
        assert session_id not in session_manager.sessions
    
    def test_cleanup_expired_sessions(self, session_manager):
        """Test cleanup of expired sessions."""
        # Create multiple sessions
        session_ids = []
        for i in range(3):
            session_ids.append(session_manager.create_session())
        
        # Expire some sessions
        for i in range(2):
            session = session_manager.sessions[session_ids[i]]
            session.last_activity = datetime.now() - timedelta(minutes=35)
        
        # Run cleanup
        cleaned_count = session_manager.cleanup_expired_sessions()
        
        assert cleaned_count == 2
        assert len(session_manager.sessions) == 1
        assert session_ids[2] in session_manager.sessions  # Only the non-expired one remains
    
    def test_get_active_session_count(self, session_manager):
        """Test getting active session count."""
        # Create sessions
        session_ids = []
        for i in range(3):
            session_ids.append(session_manager.create_session())
        
        # All should be active initially
        assert session_manager.get_active_session_count() == 3
        
        # Expire one session
        session = session_manager.sessions[session_ids[0]]
        session.last_activity = datetime.now() - timedelta(minutes=35)
        
        # Should have 2 active sessions
        assert session_manager.get_active_session_count() == 2
    
    def test_delete_session(self, session_manager):
        """Test manual session deletion."""
        session_id = session_manager.create_session()
        
        # Verify session exists
        assert session_id in session_manager.sessions
        
        # Delete session
        result = session_manager.delete_session(session_id)
        assert result is True
        
        # Verify session is gone
        assert session_id not in session_manager.sessions
        
        # Try to delete non-existent session
        result = session_manager.delete_session("nonexistent")
        assert result is False
    
    def test_get_session_stats(self, session_manager):
        """Test getting session statistics."""
        # Create sessions with messages
        for i in range(3):
            session_id = session_manager.create_session()
            for j in range(i + 1):  # Different number of messages per session
                session_manager.add_message(session_id, "user", f"Message {j}")
        
        stats = session_manager.get_session_stats()
        
        assert stats["total_sessions"] == 3
        assert stats["active_sessions"] == 3
        assert stats["expired_sessions"] == 0
        assert stats["total_messages"] == 6  # 1 + 2 + 3 messages
        assert stats["session_timeout_minutes"] == 30
        assert stats["oldest_session"] is not None
        assert stats["newest_session"] is not None
    
    def test_session_activity_update(self, session_manager):
        """Test that session activity is updated on access."""
        session_id = session_manager.create_session()
        
        # Get initial last activity
        initial_activity = session_manager.sessions[session_id].last_activity
        
        # Wait a bit and access the session
        import time
        time.sleep(0.1)
        
        session_manager.get_session(session_id)
        
        # Last activity should be updated
        updated_activity = session_manager.sessions[session_id].last_activity
        assert updated_activity > initial_activity


if __name__ == "__main__":
    # Simple test to verify session manager works
    def test_session_manager():
        """Test basic session manager functionality."""
        manager = SessionManager()
        
        # Create a session
        session_id = manager.create_session()
        print(f"✓ Created session: {session_id}")
        
        # Add messages
        manager.add_message(session_id, "user", "Hello")
        manager.add_message(session_id, "assistant", "Hi there!")
        
        # Get history
        history = manager.get_conversation_history(session_id)
        print(f"✓ Conversation history: {len(history)} messages")
        
        # Get stats
        stats = manager.get_session_stats()
        print(f"✓ Session stats: {stats['total_sessions']} total, {stats['total_messages']} messages")
        
        print("Session manager is working correctly!")
    
    test_session_manager()