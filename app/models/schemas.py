from typing import Literal
from datetime import date, datetime
from pydantic import BaseModel, Field

EntryType = Literal["vision", "audio", "query", "summary"]


class SessionEntry(BaseModel):
    id: str
    type: EntryType
    time_stamp: datetime = Field(default_factory=datetime.now)
    description: str
    frame_b64: str | None = None
