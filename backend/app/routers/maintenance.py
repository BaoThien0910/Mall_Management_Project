"""Maintenance router for handling maintenance requests and schedules."""

from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Optional, List
from app.services import maintenance_service
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/maintenance", tags=["maintenance"])


@router.get("/tickets", summary="List maintenance tickets")
async def list_tickets(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(10),
    current_user: dict = Depends(get_current_user),
):
    """
    List maintenance tickets with filtering and pagination.
    
    - **status**: Filter by status (open, in_progress, resolved, closed)
    - **priority**: Filter by priority (low, medium, high, urgent)
    - **location**: Filter by location keyword
    - **skip**: Pagination offset
    - **limit**: Pagination limit
    """
    filters = {}
    if status:
        filters["status"] = status
    if priority:
        filters["priority"] = priority
    if location:
        filters["location"] = location
    
    # Tenants see only their own requests
    if current_user.get("role") == "tenant":
        filters["created_by"] = current_user.get("email")

    result = maintenance_service.list_tickets(filters, skip, limit)
    return result


@router.get("/tickets/{ticket_id}", summary="Get ticket details")
async def get_ticket(ticket_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific maintenance ticket by ID."""
    ticket = maintenance_service.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Tenants can only view their own tickets
    if current_user.get("role") == "tenant" and ticket["created_by"] != current_user.get("email"):
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    return ticket


@router.post("/tickets", summary="Create maintenance ticket")
async def create_ticket(
    ticket_data: dict,
    current_user: dict = Depends(get_current_user),
):
    """
    Create a new maintenance ticket.
    
    Request body:
    ```json
    {
        "title": "string",
        "description": "string",
        "location": "string",
        "category": "string",
        "priority": "string"
    }
    ```
    """
    if current_user.get("role") not in ["tenant", "staff"]:
        raise HTTPException(status_code=403, detail="Only tenants and staff can create tickets")

    ticket = maintenance_service.create_ticket(
        title=ticket_data.get("title"),
        description=ticket_data.get("description"),
        location=ticket_data.get("location"),
        category=ticket_data.get("category"),
        priority=ticket_data.get("priority", "medium"),
        created_by=current_user.get("email"),
    )
    return ticket


@router.put("/tickets/{ticket_id}/status", summary="Update ticket status")
async def update_ticket_status(
    ticket_id: str,
    status_data: dict,
    current_user: dict = Depends(get_current_user),
):
    """
    Update ticket status.
    
    Request body:
    ```json
    {
        "status": "string"
    }
    ```
    """
    if current_user.get("role") not in ["staff", "admin"]:
        raise HTTPException(status_code=403, detail="Only staff and admin can update status")

    ticket = maintenance_service.update_ticket_status(
        ticket_id=ticket_id,
        status=status_data.get("status"),
        updated_by=current_user.get("email"),
    )
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return ticket


@router.put("/tickets/{ticket_id}/assign", summary="Assign ticket to staff")
async def assign_ticket(
    ticket_id: str,
    assign_data: dict,
    current_user: dict = Depends(get_current_user),
):
    """
    Assign a ticket to a staff member.
    
    Request body:
    ```json
    {
        "assigned_to": "string"
    }
    ```
    """
    if current_user.get("role") not in ["staff", "admin"]:
        raise HTTPException(status_code=403, detail="Only staff and admin can assign")

    ticket = maintenance_service.assign_ticket(
        ticket_id=ticket_id,
        assigned_to=assign_data.get("assigned_to"),
    )
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return ticket


@router.get("/schedule", summary="Get maintenance schedule")
async def get_schedule(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: int = Query(20),
    current_user: dict = Depends(get_current_user),
):
    """
    Get scheduled maintenance events.
    
    - **start_date**: Filter start date (YYYY-MM-DD)
    - **end_date**: Filter end date (YYYY-MM-DD)
    - **limit**: Maximum number of events
    """
    result = maintenance_service.list_schedule(start_date, end_date, limit)
    return result


@router.get("/statistics", summary="Get maintenance statistics")
async def get_statistics(current_user: dict = Depends(get_current_user)):
    """Get maintenance ticket statistics."""
    return maintenance_service.get_statistics()
