# File: app/routers/hopdong.py
"""
Router Quản lý Hợp đồng.

Phân quyền:
- Tạo hợp đồng          : TP_KDTC, NV_KDTC
- Xem danh sách toàn bộ : BQL, TP_KDTC, NV_KDTC
- Xem hợp đồng của mình : KHACH_THUE
- Xem chi tiết          : BQL, TP_KDTC, NV_KDTC (+ KHACH_THUE nếu là hợp đồng của mình)
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.hopdong import HopDongCreate, HopDongFilter, HopDongResponse
from app.services import contract_service
from app.constants.roles import BQL, KHACH_THUE, NV_KDTC, TP_KDTC

router = APIRouter(prefix="/api/v1/hop-dong", tags=["Hợp đồng"])

ROLES_TAO = {TP_KDTC, NV_KDTC}
ROLES_XEM_ALL = {BQL, TP_KDTC, NV_KDTC}


def _require_roles(current_user: Any, allowed_roles: set[str]) -> None:
    if current_user.mavaitro not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền thực hiện thao tác này",
        )


# ── GET /api/v1/hop-dong ──────────────────────────────────────────────────────

@router.get("", response_model=dict)
def list_hop_dong(
    makh: str | None = Query(None),
    mamb: str | None = Query(None),
    trangthai: str | None = Query(None),
    ngaybatdau_tu: str | None = Query(None, description="YYYY-MM-DD"),
    ngaybatdau_den: str | None = Query(None, description="YYYY-MM-DD"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> dict:
    """
    Danh sách hợp đồng.
    Chỉ BQL, TP_KDTC, NV_KDTC mới được xem toàn bộ.
    Khách thuê dùng endpoint /cua-toi.
    """
    _require_roles(current_user, ROLES_XEM_ALL)

    from datetime import date as date_type

    filters = HopDongFilter(
        makh=makh,
        mamb=mamb,
        trangthai=trangthai,
        ngaybatdau_tu=date_type.fromisoformat(ngaybatdau_tu) if ngaybatdau_tu else None,
        ngaybatdau_den=date_type.fromisoformat(ngaybatdau_den) if ngaybatdau_den else None,
        page=page,
        page_size=page_size,
    )

    result = contract_service.list_hopdong(db, filters)

    return {
        "success": True,
        "message": "Lấy danh sách hợp đồng thành công",
        "data": {
            **result,
            "items": [HopDongResponse.model_validate(hd).model_dump() for hd in result["items"]],
        },
    }


# ── GET /api/v1/hop-dong/cua-toi ─────────────────────────────────────────────
# Đặt TRƯỚC /{mahd} để tránh bị FastAPI nhận nhầm route

@router.get("/cua-toi", response_model=dict)
def hop_dong_cua_toi(
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> dict:
    """Khách thuê xem danh sách hợp đồng của chính mình."""
    if current_user.mavaitro != KHACH_THUE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ khách thuê mới được dùng endpoint này",
        )

    if not current_user.makh:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản không liên kết với khách thuê nào",
        )

    items = contract_service.get_hopdong_cua_toi(db, current_user.makh)

    return {
        "success": True,
        "message": "Lấy hợp đồng của bạn thành công",
        "data": [HopDongResponse.model_validate(hd).model_dump() for hd in items],
    }


# ── GET /api/v1/hop-dong/{mahd} ───────────────────────────────────────────────

@router.get("/{mahd}", response_model=dict)
def get_hop_dong(
    mahd: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> dict:
    """
    Chi tiết hợp đồng.
    BQL/TP_KDTC/NV_KDTC xem tất cả.
    Khách thuê chỉ xem hợp đồng của mình.
    """
    allowed = ROLES_XEM_ALL | {KHACH_THUE}
    _require_roles(current_user, allowed)

    hd = contract_service.get_hopdong_detail(db, mahd)

    # Khách thuê chỉ được xem hợp đồng của mình
    if current_user.mavaitro == KHACH_THUE:
        if not current_user.makh or hd.makh != current_user.makh:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền xem hợp đồng này",
            )

    return {
        "success": True,
        "message": "Lấy chi tiết hợp đồng thành công",
        "data": HopDongResponse.model_validate(hd).model_dump(),
    }


# ── POST /api/v1/hop-dong ─────────────────────────────────────────────────────

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_hop_dong(
    body: HopDongCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> dict:
    """Số hóa / tạo hợp đồng thuê mặt bằng."""
    _require_roles(current_user, ROLES_TAO)

    hd = contract_service.create_hopdong(db, body, current_user.matk)

    return {
        "success": True,
        "message": "Tạo hợp đồng thành công",
        "data": HopDongResponse.model_validate(hd).model_dump(),
    }
