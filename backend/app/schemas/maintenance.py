from pydantic import BaseModel
from typing import Optional

class TicketCreate(BaseModel):
    title: str
    description: str
    location: str
    category: str
    priority: str = "medium"

class TicketUpdateStatus(BaseModel):
    status: str

class TicketAssign(BaseModel):
    assigned_to: str