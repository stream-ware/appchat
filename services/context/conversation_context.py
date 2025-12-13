"""
Conversation Context Manager
Maintains conversation history and state for LLM context
Allows LLM to reference previous messages, app state, and user preferences
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from collections import deque

logger = logging.getLogger("streamware.context")


@dataclass
class Message:
    """Single conversation message"""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    app_type: Optional[str] = None
    action: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class AppState:
    """Current state of an app"""
    app_id: str
    last_action: str
    last_result: Dict
    timestamp: str
    context_data: Dict = field(default_factory=dict)


@dataclass
class ConversationSession:
    """Full conversation session with history and state"""
    session_id: str
    messages: List[Message] = field(default_factory=list)
    app_states: Dict[str, AppState] = field(default_factory=dict)
    user_preferences: Dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_activity: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Context window settings
    max_messages: int = 50
    max_tokens_estimate: int = 4000


class ConversationContextManager:
    """
    Manages conversation context for LLM interactions
    Provides history, app state, and context for intelligent responses
    """
    
    def __init__(self, max_sessions: int = 100):
        self.sessions: Dict[str, ConversationSession] = {}
        self.max_sessions = max_sessions
        self.storage_path = Path(__file__).parent.parent.parent / "data" / "conversations"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        logger.info("💬 ConversationContextManager initialized")
    
    def get_or_create_session(self, session_id: str) -> ConversationSession:
        """Get existing session or create new one"""
        if session_id not in self.sessions:
            # Try to load from disk
            session_file = self.storage_path / f"{session_id}.json"
            if session_file.exists():
                self.sessions[session_id] = self._load_session(session_file)
            else:
                self.sessions[session_id] = ConversationSession(session_id=session_id)
            
            # Cleanup old sessions if needed
            self._cleanup_old_sessions()
        
        return self.sessions[session_id]
    
    def add_user_message(
        self,
        session_id: str,
        content: str,
        app_type: Optional[str] = None,
        action: Optional[str] = None,
        metadata: Dict = None
    ):
        """Add user message to conversation history"""
        session = self.get_or_create_session(session_id)
        
        message = Message(
            role="user",
            content=content,
            app_type=app_type,
            action=action,
            metadata=metadata or {}
        )
        
        session.messages.append(message)
        session.last_activity = datetime.now().isoformat()
        
        # Trim if needed
        self._trim_messages(session)
        
        logger.debug(f"Added user message to session {session_id[:8]}")
    
    def add_assistant_message(
        self,
        session_id: str,
        content: str,
        app_type: Optional[str] = None,
        action: Optional[str] = None,
        metadata: Dict = None
    ):
        """Add assistant response to conversation history"""
        session = self.get_or_create_session(session_id)
        
        message = Message(
            role="assistant",
            content=content,
            app_type=app_type,
            action=action,
            metadata=metadata or {}
        )
        
        session.messages.append(message)
        session.last_activity = datetime.now().isoformat()
        
        self._trim_messages(session)
    
    def update_app_state(
        self,
        session_id: str,
        app_id: str,
        action: str,
        result: Dict,
        context_data: Dict = None
    ):
        """Update app state for context"""
        session = self.get_or_create_session(session_id)
        
        session.app_states[app_id] = AppState(
            app_id=app_id,
            last_action=action,
            last_result=result,
            timestamp=datetime.now().isoformat(),
            context_data=context_data or {}
        )
    
    def get_context_for_llm(
        self,
        session_id: str,
        include_app_states: bool = True,
        max_messages: int = 10,
        current_app: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get formatted context for LLM prompt
        Returns conversation history and relevant app states
        """
        session = self.get_or_create_session(session_id)
        
        # Get recent messages
        recent_messages = session.messages[-max_messages:] if session.messages else []
        
        # Format for LLM
        context = {
            "conversation_history": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "app": msg.app_type,
                    "time": msg.timestamp
                }
                for msg in recent_messages
            ],
            "message_count": len(session.messages),
            "session_started": session.created_at
        }
        
        # Add app states
        if include_app_states:
            app_states = {}
            for app_id, state in session.app_states.items():
                # Include current app and recently used apps
                if current_app == app_id or self._is_recent_state(state):
                    app_states[app_id] = {
                        "last_action": state.last_action,
                        "last_result_summary": self._summarize_result(state.last_result),
                        "context": state.context_data
                    }
            context["app_states"] = app_states
        
        # Add user preferences
        if session.user_preferences:
            context["user_preferences"] = session.user_preferences
        
        return context
    
    def get_llm_system_prompt_context(self, session_id: str, current_app: str = None) -> str:
        """
        Generate context string for LLM system prompt
        Summarizes conversation history and relevant state
        """
        context = self.get_context_for_llm(session_id, current_app=current_app)
        
        parts = []
        
        # Conversation summary
        if context["conversation_history"]:
            parts.append("## Poprzednia rozmowa:")
            for msg in context["conversation_history"][-5:]:  # Last 5 messages
                role = "Użytkownik" if msg["role"] == "user" else "Asystent"
                app_info = f" [{msg['app']}]" if msg.get("app") else ""
                parts.append(f"- {role}{app_info}: {msg['content'][:100]}...")
        
        # App states
        if context.get("app_states"):
            parts.append("\n## Stan aplikacji:")
            for app_id, state in context["app_states"].items():
                parts.append(f"- {app_id}: ostatnia akcja '{state['last_action']}' - {state['last_result_summary']}")
        
        # User preferences
        if context.get("user_preferences"):
            prefs = context["user_preferences"]
            parts.append(f"\n## Preferencje użytkownika:")
            for key, value in prefs.items():
                parts.append(f"- {key}: {value}")
        
        return "\n".join(parts) if parts else ""
    
    def set_user_preference(self, session_id: str, key: str, value: Any):
        """Set user preference for session"""
        session = self.get_or_create_session(session_id)
        session.user_preferences[key] = value
    
    def get_last_app_result(self, session_id: str, app_id: str) -> Optional[Dict]:
        """Get last result from specific app"""
        session = self.get_or_create_session(session_id)
        state = session.app_states.get(app_id)
        return state.last_result if state else None
    
    def get_last_message(self, session_id: str, role: str = None) -> Optional[Message]:
        """Get last message, optionally filtered by role"""
        session = self.get_or_create_session(session_id)
        
        if not session.messages:
            return None
        
        if role:
            for msg in reversed(session.messages):
                if msg.role == role:
                    return msg
            return None
        
        return session.messages[-1]
    
    def search_history(
        self,
        session_id: str,
        query: str,
        limit: int = 5
    ) -> List[Message]:
        """Search conversation history for relevant messages"""
        session = self.get_or_create_session(session_id)
        query_lower = query.lower()
        
        matches = []
        for msg in reversed(session.messages):
            if query_lower in msg.content.lower():
                matches.append(msg)
                if len(matches) >= limit:
                    break
        
        return matches
    
    def save_session(self, session_id: str):
        """Save session to disk"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session_file = self.storage_path / f"{session_id}.json"
            
            data = {
                "session_id": session.session_id,
                "messages": [asdict(m) for m in session.messages[-100:]],  # Keep last 100
                "app_states": {k: asdict(v) for k, v in session.app_states.items()},
                "user_preferences": session.user_preferences,
                "created_at": session.created_at,
                "last_activity": session.last_activity
            }
            
            with open(session_file, "w") as f:
                json.dump(data, f, indent=2, default=str)
    
    def _load_session(self, session_file: Path) -> ConversationSession:
        """Load session from disk"""
        with open(session_file, "r") as f:
            data = json.load(f)
        
        session = ConversationSession(
            session_id=data["session_id"],
            created_at=data.get("created_at", datetime.now().isoformat()),
            last_activity=data.get("last_activity", datetime.now().isoformat()),
            user_preferences=data.get("user_preferences", {})
        )
        
        # Restore messages
        for msg_data in data.get("messages", []):
            session.messages.append(Message(**msg_data))
        
        # Restore app states
        for app_id, state_data in data.get("app_states", {}).items():
            session.app_states[app_id] = AppState(**state_data)
        
        return session
    
    def _trim_messages(self, session: ConversationSession):
        """Trim messages to stay within limits"""
        if len(session.messages) > session.max_messages:
            # Keep system messages and trim oldest user/assistant messages
            session.messages = session.messages[-session.max_messages:]
    
    def _is_recent_state(self, state: AppState, hours: int = 1) -> bool:
        """Check if app state is recent"""
        try:
            state_time = datetime.fromisoformat(state.timestamp)
            return datetime.now() - state_time < timedelta(hours=hours)
        except:
            return False
    
    def _summarize_result(self, result: Dict, max_len: int = 100) -> str:
        """Create brief summary of result"""
        if not result:
            return "brak danych"
        
        if "success" in result:
            status = "sukces" if result["success"] else "błąd"
            if "message" in result:
                return f"{status}: {result['message'][:max_len]}"
            return status
        
        # Try to extract key info
        summary_parts = []
        for key in ["title", "message", "count", "total"]:
            if key in result:
                summary_parts.append(f"{key}={result[key]}")
        
        return ", ".join(summary_parts)[:max_len] if summary_parts else "dane dostępne"
    
    def _cleanup_old_sessions(self):
        """Remove old inactive sessions"""
        if len(self.sessions) <= self.max_sessions:
            return
        
        # Sort by last activity
        sorted_sessions = sorted(
            self.sessions.items(),
            key=lambda x: x[1].last_activity,
            reverse=True
        )
        
        # Keep only max_sessions
        self.sessions = dict(sorted_sessions[:self.max_sessions])
    
    def clear_session(self, session_id: str):
        """Clear session history"""
        if session_id in self.sessions:
            del self.sessions[session_id]
        
        session_file = self.storage_path / f"{session_id}.json"
        if session_file.exists():
            session_file.unlink()


# Singleton instance
context_manager = ConversationContextManager()
