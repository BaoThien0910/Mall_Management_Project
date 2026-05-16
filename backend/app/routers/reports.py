"""Reports router for management reporting."""

from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Optional
from app.services import reports_service
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/revenue", summary="Get revenue report")
async def get_revenue_report(
    start_month: Optional[str] = Query(None),
    end_month: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """
    Get revenue report.
    
    - **start_month**: Start month (YYYY-MM format)
    - **end_month**: End month (YYYY-MM format)
    
    Required role: management or admin
    """
    if current_user.get("role") not in ["management", "admin"]:
        raise HTTPException(status_code=403, detail="Only management and admin can view reports")

    return reports_service.get_revenue_report(start_month, end_month)


@router.get("/debt", summary="Get debt collection report")
async def get_debt_report(
    status: Optional[str] = Query(None),
    overdue_only: bool = Query(False),
    current_user: dict = Depends(get_current_user),
):
    """
    Get debt collection report.
    
    - **status**: Filter by status (overdue, paid, pending)
    - **overdue_only**: Only include overdue items
    
    Required role: management or admin
    """
    if current_user.get("role") not in ["management", "admin", "staff"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    return reports_service.get_debt_report(status, overdue_only)


@router.get("/occupancy", summary="Get occupancy report")
async def get_occupancy_report(
    current_user: dict = Depends(get_current_user),
):
    """
    Get occupancy report with breakdown by floor and category.
    
    Required role: management or admin
    """
    if current_user.get("role") not in ["management", "admin"]:
        raise HTTPException(status_code=403, detail="Only management and admin can view reports")

    return reports_service.get_occupancy_report()


@router.get("/kpi", summary="Get KPI dashboard")
async def get_kpi_dashboard(
    current_user: dict = Depends(get_current_user),
):
    """
    Get KPI dashboard combining multiple metrics.
    
    Required role: management or admin
    """
    if current_user.get("role") not in ["management", "admin"]:
        raise HTTPException(status_code=403, detail="Only management and admin can view reports")

    return reports_service.get_kpi_dashboard()
