from collections import deque
import datetime
from typing import Deque
import uuid
from app.config.config import config
from app.models.schemas import SessionEntry


class SessionStore:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.chat_messages: list[dict] = []
        self._log: Deque[SessionEntry] = deque(maxlen=config.session_log_limit)
        self._last_frame_b64: str | None = None
        self._last_frame_arr: None

    # ---------------------------------------------------------------------------
    # Frame state
    # ---------------------------------------------------------------------------

    def set_last_frame(self, b64: str, arr) -> None:
        self._last_frame_b64 = b64
        self._last_frame_arr = arr

    def get_last_frame_arr(self):
        return self._last_frame_arr

    def get_last_frame_b64(self):
        return self._last_frame_b64

    # ---------------------------------------------------------------------------
    # Session log management
    # ---------------------------------------------------------------------------

    def append(self, entry: SessionEntry) -> None:
        self._log.append(entry)

    def recent(self, k: int | None = None) -> list[SessionEntry]:
        k = k or config.context_recent_k
        return list(self._log)[-k:]

    def all_entries(self) -> list[SessionEntry]:
        return list(self._log)


# ---------------------------------------------------------------------------
# Global registry
# ---------------------------------------------------------------------------

_sessions: dict[str, SessionStore] = {}


def get_or_create(session_id: str) -> SessionStore:
    if session_id not in _sessions:
        _sessions[session_id] = SessionStore(session_id)
    return _sessions[session_id]


def destroy(session_id: str) -> None:
    _sessions.pop(session_id, None)


def make_entry(type, description: str, frame_b64: str | None = None) -> SessionEntry:
    return SessionEntry(
        id=str(uuid.uuid4()),
        type=type,
        description=description,
        frame_b64=frame_b64,
        ts=datetime.datetime.now(),
    )


def entry_event(entry: SessionEntry) -> dict:
    return {
        "id": entry.id,
        "type": entry.type,
        "description": entry.description,
        "timestamp": entry.time_stamp.isoformat(),
    }
