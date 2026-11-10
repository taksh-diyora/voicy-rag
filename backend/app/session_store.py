from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)

MAX_SESSIONS = 25
_sessions = OrderedDict()

def get_session(session_id: str):
    """Retrieve session data and mark it as recently used."""
    if session_id in _sessions:
        _sessions.move_to_end(session_id)
        return _sessions[session_id]
    return None

def update_session(session_id: str, index, chunks):
    """Store FAISS index and chunks, enforcing the LRU memory cap."""
    if session_id in _sessions:
        _sessions.move_to_end(session_id)
    else:
        if len(_sessions) >= MAX_SESSIONS:
            oldest = next(iter(_sessions))
            del _sessions[oldest]
            logger.info(f"Evicted oldest session {oldest} to stay under RAM limit.")
    
    _sessions[session_id] = {
        "index": index,
        "chunks": chunks,
        "history": []
    }

def update_history(session_id: str, role: str, text: str):
    """Append a message to the session's history buffer (max 6 turns)."""
    session = get_session(session_id)
    if session:
        session["history"].append((role, text))
        session["history"] = session["history"][-6:]