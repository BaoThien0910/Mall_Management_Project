"""Maintenance router for handling maintenance requests and schedules."""

from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Optional
from app.services import maintenance_service
from app.dependencies import get_principal, Principal
from app.schemas.maintenance import TicketCreate, TicketUpdateStatus, TicketAssign
from app.utils.response import success_response

router = APIRouter(prefix="/api/maintenance", tags=["maintenance"])


@router.get("/tickets", summary="List maintenance tickets")
async def list_tickets(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(10),
    current_user: Principal = Depends(get_principal),
):
    filters = {}
    if status: filters["status"] = status
    if priority: filters["priority"] = priority
    if location: filters["location"] = location
    
    if current_user.role == "tenant":
        filters["created_by"] = current_user.email

    result = maintenance_service.list_tickets(filters, skip, limit)
    return success_response(data=result, message="Lấy danh sách sự cố thành công")


@router.get("/tickets/{ticket_id}", summary="Get ticket details")
async def get_ticket(ticket_id: str, current_user: Principal = Depends(get_principal)):
    ticket = maintenance_service.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if current_user.role == "tenant" and ticket["created_by"] != current_user.email:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    return success_response(data=ticket, message="Lấy chi tiết sự cố thành công")


@router.post("/tickets", summary="Create maintenance ticket")
async def create_ticket(
    ticket_data: TicketCreate,
    current_user: Principal = Depends(get_principal),
):
    if current_user.role not in ["tenant", "staff"]:
        raise HTTPException(status_code=403, detail="Only tenants and staff can create tickets")

    ticket = maintenance_service.create_ticket(
        title=ticket_data.title,
        description=ticket_data.description,
        location=ticket_data.location,
        category=ticket_data.category,
        priority=ticket_data.priority,
        created_by=current_user.email,
    )
    return success_response(data=ticket, message="Tạo sự cố thành công")


@router.put("/tickets/{ticket_id}/status", summary="Update ticket status")
async def update_ticket_status(
    ticket_id: str,
    status_data: TicketUpdateStatus,
    current_user: Principal = Depends(get_principal),
):
    if current_user.role not in ["staff", "admin"]:
        raise HTTPException(status_code=403, detail="Only staff and admin can update status")

    ticket = maintenance_service.update_ticket_status(
        ticket_id=ticket_id,
        status=status_data.status,
        updated_by=current_user.email,
    )
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return success_response(data=ticket, message="Cập nhật trạng thái thành công")


@router.put("/tickets/{ticket_id}/assign", summary="Assign ticket to staff")
async def assign_ticket(
    ticket_id: str,
    assign_data: TicketAssign,
    current_user: Principal = Depends(get_principal),
):
    if current_user.role not in ["staff", "admin"]:
        raise HTTPException(status_code=403, detail="Only staff and admin can assign")

    ticket = maintenance_service.assign_ticket(
        ticket_id=ticket_id,
        assigned_to=assign_data.assigned_to,
    )
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return success_response(data=ticket, message="Phân công xử lý thành công")


@router.get("/schedule", summary="Get maintenance schedule")
async def get_schedule(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: int = Query(20),
    current_user: Principal = Depends(get_principal),
):
    result = maintenance_service.list_schedule(start_date, end_date, limit)
    return success_response(data=result, message="Lấy lịch bảo trì thành công")


@router.get("/statistics", summary="Get maintenance statistics")
async def get_statistics(current_user: Principal = Depends(get_principal)):
    data = maintenance_service.get_statistics()
    return success_response(data=data, message="Lấy thống kê bảo trì thành công")