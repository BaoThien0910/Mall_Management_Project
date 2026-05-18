# File: app/routers/chisodiennuoc.py
"""
Router Nhập chỉ số điện nước từng mặt bằng.
Phân quyền: TP_VHBT, NV_VHBT
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.chisodiennuoc import (
    ChiSoDienNuocCreate,
    ChiSoDienNuocResponse,
    ChiSoFilter,
)
from app.services import meter_service
from app.constants.roles import NV_VHBT, TP_VHBT

router = APIRouter(prefix="/api/v1/chi-so-dien-nuoc", tags=["Chỉ số điện nước"])

ROLES_NHAP = {TP_VHBT, NV_VHBT}


def _require_roles(current_user: Any, allowed: set[str]) -> None:
    if current_user.mavaitro not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền thực hiện thao tác này",
        )


# ── POST /api/v1/chi-so-dien-nuoc ────────────────────────────────────────────

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_chi_so(
    body: ChiSoDienNuocCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> dict:
    """Nhập chỉ số điện nước cho một mặt bằng trong tháng/năm."""
    _require_roles(current_user, ROLES_NHAP)

    chs = meter_service.create_chi_so(
        db=db,
        data=body,
        matk=current_user.matk,
        manv=current_user.manv,
    )

    return {
        "success": True,
        "message": "Nhập chỉ số điện nước thành công",
        "data": ChiSoDienNuocResponse.model_validate(chs).model_dump(),
    }


# ── GET /api/v1/chi-so-dien-nuoc ─────────────────────────────────────────────

@router.get("", response_model=dict)
def list_chi_so(
    mamb: str | None = Query(None),
    thang: int | None = Query(None, ge=1, le=12),
    nam: int | None = Query(None, ge=2000),
    manv_nhap: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> dict:
    """Danh sách chỉ số điện nước (có phân trang, lọc)."""
    _require_roles(current_user, ROLES_NHAP)

    filters = ChiSoFilter(
        mamb=mamb,
        thang=thang,
        nam=nam,
        manv_nhap=manv_nhap,
        page=page,
        page_size=page_size,
    )
    result = meter_service.list_chi_so(db, filters)

    return {
        "success": True,
        "message": "Lấy danh sách chỉ số điện nước thành công",
        "data": {
            **result,
            "items": [
                ChiSoDienNuocResponse.model_validate(item).model_dump()
                for item in result["items"]
            ],
        },
    }


# ── GET /api/v1/chi-so-dien-nuoc/{machs} ─────────────────────────────────────

@router.get("/{machs}", response_model=dict)
def get_chi_so(
    machs: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> dict:
    """Chi tiết một bản ghi chỉ số điện nước."""
    _require_roles(current_user, ROLES_NHAP)

    chs = meter_service.get_chi_so_detail(db, machs)

    return {
        "success": True,
        "message": "Lấy chi tiết chỉ số điện nước thành công",
        "data": ChiSoDienNuocResponse.model_validate(chs).model_dump(),
    }
