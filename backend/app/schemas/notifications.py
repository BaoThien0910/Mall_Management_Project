from pydantic import BaseModel
from typing import List, Optional

class AnnouncementCreate(BaseModel):
    title: str
    content: str
    recipients: List[str] = []
    scheduled_at: Optional[str] = None