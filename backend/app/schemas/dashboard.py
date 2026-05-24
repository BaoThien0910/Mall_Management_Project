# File: app/schemas/dashboard.py
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class DashboardSummaryCard(BaseModel):
    key: str
    title: str
    value: Any
    description: Optional[str] = None
    status: Optional[str] = None


class DashboardResponse(BaseModel):
    role: str
    summary_cards: List[DashboardSummaryCard]
    menu_badges: Dict[str, int]
