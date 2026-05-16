"""Maintenance service for handling maintenance tickets and schedules."""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from enum import Enum
from app.dependencies import get_principal, Principal

class TicketStatus(str, Enum):
    """Maintenance ticket statuses."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(str, Enum):
    """Maintenance ticket priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# Mock data storage
MOCK_TICKETS = [
    {
        "id": "MNT-001",
        "title": "Air conditioner not working",
        "description": "AC unit in GF-01 producing warm air",
        "location": "GF-01",
        "category": "Climate Control",
        "status": "in_progress",
        "priority": "high",
        "created_by": "tenant@example.com",
        "created_at": (datetime.now() - timedelta(days=2)).isoformat(),
        "assigned_to": "staff@example.com",
        "updated_at": (datetime.now() - timedelta(hours=4)).isoformat(),
        "completion_date": None,
    },
    {
        "id": "MNT-002",
        "title": "Water leak in ceiling",
        "description": "Water dripping from ceiling in L2-05",
        "location": "L2-05",
        "category": "Plumbing",
        "status": "open",
        "priority": "urgent",
        "created_by": "tenant@example.com",
        "created_at": (datetime.now() - timedelta(hours=6)).isoformat(),
        "assigned_to": None,
        "updated_at": (datetime.now() - timedelta(hours=6)).isoformat(),
        "completion_date": None,
    },
    {
        "id": "MNT-003",
        "title": "Elevator maintenance",
        "description": "Scheduled preventive maintenance for elevators",
        "location": "Building Main",
        "category": "Elevator",
        "status": "resolved",
        "priority": "medium",
        "created_by": "staff@example.com",
        "created_at": (datetime.now() - timedelta(days=5)).isoformat(),
        "assigned_to": "staff@example.com",
        "updated_at": (datetime.now() - timedelta(days=1)).isoformat(),
        "completion_date": (datetime.now() - timedelta(days=1)).isoformat(),
    },
]

MOCK_SCHEDULE = [
    {
        "id": "SCH-001",
        "title": "Weekly cleaning - Common areas",
        "date": (datetime.now() + timedelta(days=3)).date().isoformat(),
        "time": "08:00 - 10:00",
        "location": "Ground Floor",
        "type": "Routine",
    },
    {
        "id": "SCH-002",
        "title": "HVAC system inspection",
        "date": (datetime.now() + timedelta(days=7)).date().isoformat(),
        "time": "09:00 - 12:00",
        "location": "Building Main",
        "type": "Preventive",
    },
    {
        "id": "SCH-003",
        "title": "Fire safety drill",
        "date": (datetime.now() + timedelta(days=14)).date().isoformat(),
        "time": "14:00 - 15:00",
        "location": "All Areas",
        "type": "Safety",
    },
]


def list_tickets(
    filters: Optional[Dict[str, Any]] = None, skip: int = 0, limit: int = 10
) -> Dict[str, Any]:
    """
    List maintenance tickets with filtering and pagination.
    
    Args:
        filters: Dict with optional keys: status, priority, location, created_by
        skip: Pagination offset
        limit: Pagination limit
    
    Returns:
        Dict with 'total', 'items', 'skip', 'limit'
    """
    filtered = MOCK_TICKETS.copy()

    if filters:
        if "status" in filters and filters["status"]:
            filtered = [t for t in filtered if t["status"] == filters["status"]]
        if "priority" in filters and filters["priority"]:
            filtered = [t for t in filtered if t["priority"] == filters["priority"]]
        if "location" in filters and filters["location"]:
            filtered = [
                t for t in filtered if filters["location"].lower() in t["location"].lower()
            ]
        if "created_by" in filters and filters["created_by"]:
            filtered = [t for t in filtered if t["created_by"] == filters["created_by"]]

    total = len(filtered)
    items = filtered[skip : skip + limit]

    return {"total": total, "items": items, "skip": skip, "limit": limit}


def get_ticket(ticket_id: str) -> Optional[Dict[str, Any]]:
    """Get a single ticket by ID."""
    for ticket in MOCK_TICKETS:
        if ticket["id"] == ticket_id:
            return ticket
    return None


def create_ticket(
    title: str,
    description: str,
    location: str,
    category: str,
    priority: str,
    created_by: str,
) -> Dict[str, Any]:
    """
    Create a new maintenance ticket.
    
    Args:
        title: Ticket title
        description: Detailed description
        location: Location/premise
        category: Category (Climate Control, Plumbing, Electrical, etc.)
        priority: Priority level (low, medium, high, urgent)
        created_by: Email of ticket creator
    
    Returns:
        Created ticket object
    """
    ticket_id = f"MNT-{len(MOCK_TICKETS) + 1:03d}"
    now = datetime.now().isoformat()

    ticket = {
        "id": ticket_id,
        "title": title,
        "description": description,
        "location": location,
        "category": category,
        "status": TicketStatus.OPEN.value,
        "priority": priority,
        "created_by": created_by,
        "created_at": now,
        "assigned_to": None,
        "updated_at": now,
        "completion_date": None,
    }

    MOCK_TICKETS.append(ticket)
    return ticket


def update_ticket_status(ticket_id: str, status: str, updated_by: str) -> Optional[Dict[str, Any]]:
    """
    Update ticket status.
    
    Args:
        ticket_id: Ticket ID
        status: New status
        updated_by: Email of user making update
    
    Returns:
        Updated ticket or None if not found
    """
    ticket = get_ticket(ticket_id)
    if ticket:
        ticket["status"] = status
        ticket["updated_at"] = datetime.now().isoformat()
        if status == TicketStatus.CLOSED.value or status == TicketStatus.RESOLVED.value:
            ticket["completion_date"] = datetime.now().isoformat()
        return ticket
    return None


def assign_ticket(ticket_id: str, assigned_to: str) -> Optional[Dict[str, Any]]:
    """
    Assign a ticket to a staff member.
    
    Args:
        ticket_id: Ticket ID
        assigned_to: Email of staff member
    
    Returns:
        Updated ticket or None if not found
    """
    ticket = get_ticket(ticket_id)
    if ticket:
        ticket["assigned_to"] = assigned_to
        ticket["updated_at"] = datetime.now().isoformat()
        if ticket["status"] == TicketStatus.OPEN.value:
            ticket["status"] = TicketStatus.IN_PROGRESS.value
        return ticket
    return None


def list_schedule(
    start_date: Optional[str] = None, end_date: Optional[str] = None, limit: int = 20
) -> Dict[str, Any]:
    """
    List scheduled maintenance events.
    
    Args:
        start_date: Optional filter start date (ISO format)
        end_date: Optional filter end date (ISO format)
        limit: Maximum number of events to return
    
    Returns:
        Dict with 'total', 'items'
    """
    filtered = MOCK_SCHEDULE.copy()

    if start_date:
        filtered = [s for s in filtered if s["date"] >= start_date]
    if end_date:
        filtered = [s for s in filtered if s["date"] <= end_date]

    items = filtered[:limit]
    return {"total": len(items), "items": items}


def get_statistics() -> Dict[str, Any]:
    """Get maintenance statistics."""
    total = len(MOCK_TICKETS)
    open_count = len([t for t in MOCK_TICKETS if t["status"] == TicketStatus.OPEN.value])
    in_progress = len(
        [t for t in MOCK_TICKETS if t["status"] == TicketStatus.IN_PROGRESS.value]
    )
    resolved = len([t for t in MOCK_TICKETS if t["status"] == TicketStatus.RESOLVED.value])
    closed = len([t for t in MOCK_TICKETS if t["status"] == TicketStatus.CLOSED.value])

    return {
        "total": total,
        "open": open_count,
        "in_progress": in_progress,
        "resolved": resolved,
        "closed": closed,
    }
