"""Reports router for management reporting."""

from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Optional
from app.services import reports_service
from app.dependencies import get_principal, Principal
from app.utils.response import success_response

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/revenue", summary="Get revenue report")
async def get_revenue_report(
    start_month: Optional[str] = Query(None),
    end_month: Optional[str] = Query(None),
    current_user: Principal = Depends(get_principal),
):
    if current_user.role not in ["management", "admin"]:
        raise HTTPException(status_code=403, detail="Only management and admin can view reports")

    data = reports_service.get_revenue_report(start_month, end_month)
    return success_response(data=data, message="Lấy báo cáo doanh thu thành công")


@router.get("/debt", summary="Get debt collection report")
async def get_debt_report(
    status: Optional[str] = Query(None),
    overdue_only: bool = Query(False),
    current_user: Principal = Depends(get_principal),
):
    if current_user.role not in ["management", "admin", "staff"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    data = reports_service.get_debt_report(status, overdue_only)
    return success_response(data=data, message="Lấy báo cáo công nợ thành công")


@router.get("/occupancy", summary="Get occupancy report")
async def get_occupancy_report(
    current_user: Principal = Depends(get_principal),
):
    if current_user.role not in ["management", "admin"]:
        raise HTTPException(status_code=403, detail="Only management and admin can view reports")

    data = reports_service.get_occupancy_report()
    return success_response(data=data, message="Lấy báo cáo trạng thái mặt bằng thành công")


@router.get("/kpi", summary="Get KPI dashboard")
async def get_kpi_dashboard(
    current_user: Principal = Depends(get_principal),
):
    if current_user.role not in ["management", "admin"]:
        raise HTTPException(status_code=403, detail="Only management and admin can view reports")

    data = reports_service.get_kpi_dashboard()
    return success_response(data=data, message="Lấy dữ liệu tổng quan KPI thành công")