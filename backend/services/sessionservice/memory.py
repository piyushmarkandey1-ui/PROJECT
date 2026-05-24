import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

SESSION_TIMEOUT_MINUTES = 30
MAX_MESSAGES_PER_SESSION = 50


class SessionManager:
    _instance: Optional["SessionManager"] = None

    def __new__(cls) -> "SessionManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._company_sessions: Dict[str, Dict[str, dict]] = {}
        return cls._instance

    def _is_expired(self, session: dict) -> bool:
        last_active = session.get("last_active", datetime.utcnow())
        return datetime.utcnow() - last_active > timedelta(minutes=SESSION_TIMEOUT_MINUTES)

    def _cleanup_expired(self, company_slug: Optional[str] = None) -> None:
        """Clean up expired sessions for a specific company or all companies."""
        companies = [company_slug] if company_slug else list(self._company_sessions.keys())
        
        for slug in companies:
            if slug not in self._company_sessions:
                continue
            
            sessions = self._company_sessions[slug]
            expired = [sid for sid, s in sessions.items() if self._is_expired(s)]
            
            for sid in expired:
                del sessions[sid]
                logger.info("Session expired and removed: %s (company: %s)", sid, slug)
            
            if not sessions:
                del self._company_sessions[slug]

    def create_session(self, company_slug: str, session_id: Optional[str] = None) -> str:
        """Create a new session tied to a specific company."""
        self._cleanup_expired(company_slug)
        
        if company_slug not in self._company_sessions:
            self._company_sessions[company_slug] = {}
        
        sid = session_id or str(uuid.uuid4())
        self._company_sessions[company_slug][sid] = {
            "company_slug": company_slug,
            "history": [],
            "created_at": datetime.utcnow(),
            "last_active": datetime.utcnow(),
        }
        logger.info("Session created: %s (company: %s)", sid, company_slug)
        return sid

    def session_exists(self, company_slug: str, session_id: str) -> bool:
        """Check if a session exists and is not expired for a specific company."""
        if company_slug not in self._company_sessions:
            return False
        
        sessions = self._company_sessions[company_slug]
        if session_id not in sessions:
            return False
        
        if self._is_expired(sessions[session_id]):
            del sessions[session_id]
            if not sessions:
                del self._company_sessions[company_slug]
            return False
        
        return True

    def get_history(self, company_slug: str, session_id: str) -> List[dict]:
        """Get session history - only accessible for the correct company."""
        if not self.session_exists(company_slug, session_id):
            return []
        return self._company_sessions[company_slug][session_id]["history"]

    def add_message(self, company_slug: str, session_id: str, role: str, content: str) -> None:
        """Add a message to a session - strictly company-isolated."""
        if role not in ("user", "assistant"):
            raise ValueError("role must be 'user' or 'assistant'")
        
        if not self.session_exists(company_slug, session_id):
            self.create_session(company_slug, session_id)

        session = self._company_sessions[company_slug][session_id]
        session["history"].append({"role": role, "content": content})
        session["last_active"] = datetime.utcnow()

        if len(session["history"]) > MAX_MESSAGES_PER_SESSION:
            session["history"] = session["history"][-MAX_MESSAGES_PER_SESSION:]

        logger.debug("Message added to session %s (company: %s, role: %s)", session_id, company_slug, role)

    def clear_session(self, company_slug: str, session_id: str) -> None:
        """Clear session - only for the correct company."""
        if company_slug in self._company_sessions:
            if session_id in self._company_sessions[company_slug]:
                self._company_sessions[company_slug][session_id]["history"] = []
                logger.info("Session cleared: %s (company: %s)", session_id, company_slug)

    def get_session_summary(self, company_slug: str, session_id: str) -> str:
        """Get session summary - company-isolated."""
        history = self.get_history(company_slug, session_id)
        recent = history[-10:]
        if not recent:
            return ""
        lines = [f"{msg['role'].capitalize()}: {msg['content']}" for msg in recent]
        return "\n".join(lines)

    def delete_company_sessions(self, company_slug: str) -> int:
        """Delete all sessions for a company (when company is deleted)."""
        if company_slug not in self._company_sessions:
            return 0
        
        count = len(self._company_sessions[company_slug])
        del self._company_sessions[company_slug]
        logger.info("Deleted all %d sessions for company: %s", count, company_slug)
        return count

    def get_company_session_count(self, company_slug: str) -> int:
        """Get number of active sessions for a company."""
        if company_slug not in self._company_sessions:
            return 0
        return len(self._company_sessions[company_slug])
