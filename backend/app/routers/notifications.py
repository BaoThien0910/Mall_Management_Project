"""Notifications router for announcements and user inbox."""

from fastapi import APIRouter, Query, Depends, HTTPException, Body
from typing import Optional
from app.services import notifications_service
from app.dependencies import get_principal, Principal
from app.schemas.notifications import AnnouncementCreate
from app.utils.response import success_response

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("/announcements", summary="List announcements")
async def list_announcements(
    status: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(20),
    current_user: Principal = Depends(get_principal),
):
    user_role = current_user.role
    result = notifications_service.list_announcements(
        status_filter=status,
        recipient_role=user_role,
        skip=skip,
        limit=limit,
    )
    return success_response(data=result, message="Lấy danh sách thông báo thành công")


@router.get("/announcements/{announcement_id}", summary="Get announcement details")
async def get_announcement(
    announcement_id: str,
    current_user: Principal = Depends(get_principal),
):
    announcement = notifications_service.get_announcement(announcement_id)
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    if current_user.role not in announcement.get("recipients", []):
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    return success_response(data=announcement, message="Lấy chi tiết thông báo thành công")


@router.post("/announcements", summary="Create announcement")
async def create_announcement(
    announcement_data: AnnouncementCreate,
    current_user: Principal = Depends(get_principal),
):
    if current_user.role not in ["management", "admin"]:
        raise HTTPException(status_code=403, detail="Only management and admin can create announcements")

    announcement = notifications_service.create_announcement(
        title=announcement_data.title,
        content=announcement_data.content,
        recipients=announcement_data.recipients,
        created_by=current_user.email,
        scheduled_at=announcement_data.scheduled_at,
    )
    return success_response(data=announcement, message="Tạo thông báo thành công")


@router.get("/inbox", summary="Get user inbox")
async def get_inbox(
    unread_only: bool = Query(False),
    skip: int = Query(0),
    limit: int = Query(20),
    current_user: Principal = Depends(get_principal),
):
    result = notifications_service.get_user_inbox(
        user_email=current_user.email,
        unread_only=unread_only,
        skip=skip,
        limit=limit,
    )
    return success_response(data=result, message="Lấy hộp thư thành công")


@router.put("/inbox/{message_id}/read", summary="Mark message as read")
async def mark_as_read(
    message_id: str,
    current_user: Principal = Depends(get_principal),
):
    message = notifications_service.mark_as_read(message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    return success_response(data=message, message="Đánh dấu đã đọc thành công")


@router.put("/inbox/read-all", summary="Mark all messages as read")
async def mark_all_as_read(
    current_user: Principal = Depends(get_principal),
):
    result = notifications_service.mark_all_as_read(current_user.email)
    return success_response(data=result, message="Đánh dấu đã đọc tất cả thành công")


@router.get("/stats", summary="Get notification statistics")
async def get_stats(
    current_user: Principal = Depends(get_principal),
):
    stats = notifications_service.get_notification_stats(current_user.email)
    return success_response(data=stats, message="Lấy thống kê thông báo thành công")