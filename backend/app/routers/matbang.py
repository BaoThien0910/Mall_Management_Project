# File: app/routers/matbang.py
"""
Router Quản lý Mặt bằng.

Phân quyền:
- Thêm / Sửa / Xóa : TP_VHBT, NV_VHBT
- Xem danh sách     : BQL, TP_VHBT, NV_VHBT, KHACH_THUE
- Xem chi tiết      : BQL, TP_VHBT, NV_VHBT, KHACH_THUE
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.matbang import (
    MatBangCreate,
    MatBangFilter,
    MatBangResponse,
    MatBangUpdate,
)
from app.services import premise_service
from app.constants.roles import BQL, KHACH_THUE, NV_VHBT, TP_VHBT

router = APIRouter(prefix="/api/v1/mat-bang", tags=["Mặt bằng"])

# Tập hợp role được phép xem
ROLES_XEM = {BQL, TP_VHBT, NV_VHBT, KHACH_THUE}
# Tập hợp role được phép thêm/sửa/xóa
ROLES_QUAN_LY = {TP_VHBT, NV_VHBT}


def _require_roles(current_user: Any, allowed_roles: set[str]) -> None:
    """Kiểm tra vai trò, raise 403 nếu không có quyền."""
    if current_user.mavaitro not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền thực hiện thao tác này",
        )


# ── GET /api/v1/mat-bang ──────────────────────────────────────────────────────

@router.get("", response_model=dict)
def list_mat_bang(
    trangthai: str | None = Query(None),
    tang: str | None = Query(None),
    loaimb: str | None = Query(None),
    dientich_tu: float | None = Query(None, ge=0),
    dientich_den: float | None = Query(None, ge=0),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> dict:
    """
    Danh sách mặt bằng.
    Khách thuê chỉ thấy mặt bằng 'Còn trống'.
    """
    _require_roles(current_user, ROLES_XEM)

    filters = MatBangFilter(
        trangthai=trangthai,
        tang=tang,
        loaimb=loaimb,
        dientich_tu=dientich_tu,
        dientich_den=dientich_den,
        page=page,
        page_size=page_size,
    )

    chi_xem_con_trong = current_user.mavaitro == KHACH_THUE
    result = premise_service.list_matbang(db, filters, chi_xem_con_trong)

    return {
        "success": True,
        "message": "Lấy danh sách mặt bằng thành công",
        "data": {
            **result,
            "items": [MatBangResponse.model_validate(mb).model_dump() for mb in result["items"]],
        },
    }


# ── GET /api/v1/mat-bang/{mamb} ───────────────────────────────────────────────

@router.get("/{mamb}", response_model=dict)
def get_mat_bang(
    mamb: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> dict:
    """Chi tiết một mặt bằng."""
    _require_roles(current_user, ROLES_XEM)

    mb = premise_service.get_matbang_detail(db, mamb)

    # Khách thuê không được xem mặt bằng không phải 'Còn trống'
    if current_user.mavaitro == KHACH_THUE:
        from app.constants.statuses import TrangThaiMatBang
        if mb.trangthai != TrangThaiMatBang.CON_TRONG:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn chỉ được xem mặt bằng có trạng thái 'Còn trống'",
            )

    return {
        "success": True,
        "message": "Lấy chi tiết mặt bằng thành công",
        "data": MatBangResponse.model_validate(mb).model_dump(),
    }


# ── POST /api/v1/mat-bang ─────────────────────────────────────────────────────

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_mat_bang(
    body: MatBangCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> dict:
    """Thêm mới mặt bằng."""
    _require_roles(current_user, ROLES_QUAN_LY)

    mb = premise_service.create_matbang(db, body, current_user.matk)

    return {
        "success": True,
        "message": "Thêm mặt bằng thành công",
        "data": MatBangResponse.model_validate(mb).model_dump(),
    }


# ── PATCH /api/v1/mat-bang/{mamb} ────────────────────────────────────────────

@router.patch("/{mamb}", response_model=dict)
def update_mat_bang(
    mamb: str,
    body: MatBangUpdate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> dict:
    """Cập nhật thông tin mặt bằng (partial update)."""
    _require_roles(current_user, ROLES_QUAN_LY)

    mb = premise_service.update_matbang(db, mamb, body, current_user.matk)

    return {
        "success": True,
        "message": "Cập nhật mặt bằng thành công",
        "data": MatBangResponse.model_validate(mb).model_dump(),
    }


# ── DELETE /api/v1/mat-bang/{mamb} ───────────────────────────────────────────

@router.delete("/{mamb}", response_model=dict)
def delete_mat_bang(
    mamb: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> dict:
    """Xóa mặt bằng (không được xóa nếu đang có hợp đồng hiệu lực)."""
    _require_roles(current_user, ROLES_QUAN_LY)

    premise_service.delete_matbang(db, mamb, current_user.matk)

    return {
        "success": True,
        "message": f"Xóa mặt bằng '{mamb}' thành công",
        "data": None,
    }
