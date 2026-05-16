"""Notifications and announcements service."""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum


class AnnouncementStatus(str, Enum):
    """Announcement statuses."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    ARCHIVED = "archived"


# Mock data
MOCK_ANNOUNCEMENTS = [
    {
        "id": "ANN-001",
        "title": "Maintenance Alert: Elevator Inspection",
        "content": "Elevator maintenance will be conducted on November 15-16, 2025. Please use stairs during this period.",
        "created_by": "admin@example.com",
        "created_at": (datetime.now() - timedelta(days=2)).isoformat(),
        "scheduled_at": None,
        "published_at": (datetime.now() - timedelta(days=2)).isoformat(),
        "recipients": ["staff", "management", "tenant"],
        "status": "published",
        "read_count": 45,
    },
    {
        "id": "ANN-002",
        "title": "New Payment Policy Update",
        "content": "Effective December 1, 2025, late payment fees will be assessed. Please refer to the attached guidelines.",
        "created_by": "management@example.com",
        "created_at": (datetime.now() - timedelta(days=1)).isoformat(),
        "scheduled_at": None,
        "published_at": (datetime.now() - timedelta(days=1)).isoformat(),
        "recipients": ["tenant"],
        "status": "published",
        "read_count": 62,
    },
    {
        "id": "ANN-003",
        "title": "Staff Meeting - Q1 Planning",
        "content": "All staff are invited to the Q1 planning meeting on November 20, 2025 at 2 PM in the conference room.",
        "created_by": "management@example.com",
        "created_at": datetime.now().isoformat(),
        "scheduled_at": None,
        "published_at": datetime.now().isoformat(),
        "recipients": ["staff"],
        "status": "published",
        "read_count": 12,
    },
]

MOCK_INBOX = [
    {
        "id": "MSG-001",
        "announcement_id": "ANN-001",
        "user_email": "tenant1@example.com",
        "title": "Maintenance Alert: Elevator Inspection",
        "content": "Elevator maintenance will be conducted on November 15-16, 2025.",
        "created_at": (datetime.now() - timedelta(days=2)).isoformat(),
        "read_at": (datetime.now() - timedelta(days=1)).isoformat(),
    },
    {
        "id": "MSG-002",
        "announcement_id": "ANN-002",
        "user_email": "tenant1@example.com",
        "title": "New Payment Policy Update",
        "content": "Effective December 1, 2025, late payment fees will be assessed.",
        "created_at": (datetime.now() - timedelta(days=1)).isoformat(),
        "read_at": None,
    },
    {
        "id": "MSG-003",
        "announcement_id": "ANN-003",
        "user_email": "staff1@example.com",
        "title": "Staff Meeting - Q1 Planning",
        "content": "All staff are invited to the Q1 planning meeting on November 20, 2025 at 2 PM.",
        "created_at": datetime.now().isoformat(),
        "read_at": None,
    },
]


def list_announcements(
    status_filter: Optional[str] = None,
    recipient_role: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> Dict[str, Any]:
    """
    List announcements with filtering and pagination.
    
    Args:
        status_filter: Filter by status (draft, scheduled, published, archived)
        recipient_role: Filter by recipient role (admin, staff, management, tenant)
        skip: Pagination offset
        limit: Pagination limit
    
    Returns:
        Dict with announcements list and pagination info
    """
    filtered = MOCK_ANNOUNCEMENTS.copy()

    if status_filter:
        filtered = [a for a in filtered if a["status"] == status_filter]

    if recipient_role:
        filtered = [a for a in filtered if recipient_role in a["recipients"]]

    # Sort by published_at descending
    filtered.sort(key=lambda x: x["published_at"] or x["created_at"], reverse=True)

    total = len(filtered)
    items = filtered[skip : skip + limit]

    return {"total": total, "items": items, "skip": skip, "limit": limit}


def get_announcement(announcement_id: str) -> Optional[Dict[str, Any]]:
    """Get a single announcement by ID."""
    for ann in MOCK_ANNOUNCEMENTS:
        if ann["id"] == announcement_id:
            return ann
    return None


def create_announcement(
    title: str,
    content: str,
    recipients: List[str],
    created_by: str,
    scheduled_at: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a new announcement.
    
    Args:
        title: Announcement title
        content: Announcement content
        recipients: List of recipient roles (admin, staff, management, tenant)
        created_by: Email of creator
        scheduled_at: Optional schedule time (ISO format)
    
    Returns:
        Created announcement
    """
    announcement_id = f"ANN-{len(MOCK_ANNOUNCEMENTS) + 1:03d}"
    now = datetime.now().isoformat()

    status = (
        AnnouncementStatus.SCHEDULED.value
        if scheduled_at
        else AnnouncementStatus.PUBLISHED.value
    )
    published_at = None if scheduled_at else now

    announcement = {
        "id": announcement_id,
        "title": title,
        "content": content,
        "created_by": created_by,
        "created_at": now,
        "scheduled_at": scheduled_at,
        "published_at": published_at,
        "recipients": recipients,
        "status": status,
        "read_count": 0,
    }

    MOCK_ANNOUNCEMENTS.append(announcement)
    return announcement


def get_user_inbox(
    user_email: str, unread_only: bool = False, skip: int = 0, limit: int = 20
) -> Dict[str, Any]:
    """
    Get user's notification inbox.
    
    Args:
        user_email: User's email address
        unread_only: Only return unread messages
        skip: Pagination offset
        limit: Pagination limit
    
    Returns:
        User's inbox messages
    """
    filtered = [msg for msg in MOCK_INBOX if msg["user_email"] == user_email]

    if unread_only:
        filtered = [msg for msg in filtered if msg["read_at"] is None]

    # Sort by created_at descending
    filtered.sort(key=lambda x: x["created_at"], reverse=True)

    total = len(filtered)
    items = filtered[skip : skip + limit]

    unread_count = len([msg for msg in MOCK_INBOX if msg["user_email"] == user_email and msg["read_at"] is None])

    return {
        "total": total,
        "items": items,
        "skip": skip,
        "limit": limit,
        "unread_count": unread_count,
    }


def mark_as_read(message_id: str) -> Optional[Dict[str, Any]]:
    """
    Mark a message as read.
    
    Args:
        message_id: Message ID
    
    Returns:
        Updated message or None if not found
    """
    for msg in MOCK_INBOX:
        if msg["id"] == message_id:
            msg["read_at"] = datetime.now().isoformat()
            return msg
    return None


def mark_all_as_read(user_email: str) -> Dict[str, int]:
    """
    Mark all messages for user as read.
    
    Args:
        user_email: User's email address
    
    Returns:
        Count of messages marked as read
    """
    count = 0
    now = datetime.now().isoformat()
    for msg in MOCK_INBOX:
        if msg["user_email"] == user_email and msg["read_at"] is None:
            msg["read_at"] = now
            count += 1
    return {"marked": count}


def get_notification_stats(user_email: str) -> Dict[str, Any]:
    """
    Get notification statistics for a user.
    
    Args:
        user_email: User's email address
    
    Returns:
        Notification statistics
    """
    user_msgs = [msg for msg in MOCK_INBOX if msg["user_email"] == user_email]
    unread = len([msg for msg in user_msgs if msg["read_at"] is None])

    return {
        "total_messages": len(user_msgs),
        "unread_count": unread,
        "read_count": len(user_msgs) - unread,
    }
