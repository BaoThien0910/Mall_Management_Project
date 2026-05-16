"""Notifications router for announcements and user inbox."""

from fastapi import APIRouter, Query, Depends, HTTPException, Body
from typing import Optional, List
from app.services import notifications_service
from app.dependencies import get_principal, Principal

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("/announcements", summary="List announcements")
async def list_announcements(
    status: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(20),
    current_user: Principal = Depends(get_principal),
):
    """
    List announcements.
    
    - **status**: Filter by status (draft, scheduled, published, archived)
    - **skip**: Pagination offset
    - **limit**: Pagination limit
    """
    # Filter by current user's role
    user_role = current_user.role
    
    result = notifications_service.list_announcements(
        status_filter=status,
        recipient_role=user_role,
        skip=skip,
        limit=limit,
    )
    return result


@router.get("/announcements/{announcement_id}", summary="Get announcement details")
async def get_announcement(
    announcement_id: str,
    current_user: Principal = Depends(get_principal),
):
    """Get a specific announcement."""
    announcement = notifications_service.get_announcement(announcement_id)
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    # Check if user's role is in recipients
    if current_user.role not in announcement.get("recipients", []):
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    return announcement


@router.post("/announcements", summary="Create announcement")
async def create_announcement(
    announcement_data: dict = Body(...),
    current_user: Principal = Depends(get_principal),
):
    """
    Create a new announcement.
    
    Request body:
    ```json
    {
        "title": "string",
        "content": "string",
        "recipients": ["admin", "staff"],
        "scheduled_at": "2025-11-20T14:00:00"
    }
    ```
    
    Required role: management or admin
    """
    if current_user.role not in ["management", "admin"]:
        raise HTTPException(status_code=403, detail="Only management and admin can create announcements")

    announcement = notifications_service.create_announcement(
        title=announcement_data.get("title"),
        content=announcement_data.get("content"),
        recipients=announcement_data.get("recipients", []),
        created_by=current_user.email,
        scheduled_at=announcement_data.get("scheduled_at"),
    )
    return announcement


@router.get("/inbox", summary="Get user inbox")
async def get_inbox(
    unread_only: bool = Query(False),
    skip: int = Query(0),
    limit: int = Query(20),
    current_user: Principal = Depends(get_principal),
):
    """
    Get user's notification inbox.
    
    - **unread_only**: Only return unread messages
    - **skip**: Pagination offset
    - **limit**: Pagination limit
    """
    result = notifications_service.get_user_inbox(
        user_email=current_user.email,
        unread_only=unread_only,
        skip=skip,
        limit=limit,
    )
    return result


@router.put("/inbox/{message_id}/read", summary="Mark message as read")
async def mark_as_read(
    message_id: str,
    current_user: Principal = Depends(get_principal),
):
    """Mark a specific message as read."""
    # TODO: Verify user owns the message
    message = notifications_service.mark_as_read(message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    return message


@router.put("/inbox/read-all", summary="Mark all messages as read")
async def mark_all_as_read(
    current_user: Principal = Depends(get_principal),
):
    """Mark all messages for current user as read."""
    result = notifications_service.mark_all_as_read(current_user.email)
    return result


@router.get("/stats", summary="Get notification statistics")
async def get_stats(
    current_user: Principal = Depends(get_principal),
):
    """Get notification statistics for current user."""
    stats = notifications_service.get_notification_stats(current_user.email)
    return stats
