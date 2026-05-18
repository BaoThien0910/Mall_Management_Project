# File: app/routers/congno.py
"""
Router Công nợ: Tính toán, xem danh sách, tra cứu cá nhân.
Phân quyền:
- Tính toán, xem toàn bộ : TP_KDTC, NV_KDTC
- Xem của mình           : KHACH_THUE
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.congno import (
    CongNoFilter,
    CongNoResponse,
    TinhCongNoInput,
    TinhCongNoKetQuaResponse,
)
from app.services import billing_service
from app.constants.roles import KHACH_THUE, NV_KDTC, TP_KDTC

router = APIRouter(prefix="/api/v1/cong-no", tags=["Công nợ"])

ROLES_KDTC = {TP_KDTC, NV_KDTC}


def _require_roles(current_user: Any, allowed: set[str]) -> None:
    if current_user.mavaitro not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền thực hiện thao tác này",
        )


def _require_makh(current_user: Any) -> str:
    if not current_user.makh:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản không liên kết với khách thuê nào",
        )
    return current_user.makh


# ── POST /api/v1/cong-no/tinh-toan ───────────────────────────────────────────

@router.post("/tinh-toan", response_model=dict)
def tinh_toan_cong_no(
    body: TinhCongNoInput,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> dict:
    """Tính công nợ tháng cho tất cả hợp đồng đang hiệu lực."""
    _require_roles(current_user, ROLES_KDTC)

    result = billing_service.tinh_cong_no_thang(db, body, current_user.matk)

    return {
        "success": True,
        "message": (
            f"Tính công nợ tháng {body.thang}/{body.nam}: "
            f"{result.tao_thanh_cong} tạo mới"
        ),
        "data": result.model_dump(),
    }


# ── GET /api/v1/cong-no/cua-toi ──────────────────────────────────────────────
# Phải đặt TRƯỚC /{macn}

@router.get("/cua-toi", response_model=dict)
def cong_no_cua_toi(
    mahd: str | None = Query(None),
    thang: int | None = Query(None, ge=1, le=12),
    nam: int | None = Query(None, ge=2000),
    trang_thai: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> dict:
    """Khách thuê xem công nợ của chính mình."""
    if current_user.mavaitro != KHACH_THUE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ khách thuê mới được dùng endpoint này",
        )
    makh = _require_makh(current_user)

    filters = CongNoFilter(
        mahd=mahd,
        thang=thang,
        nam=nam,
        trang_thai=trang_thai,
        page=page,
        page_size=page_size,
    )
    result = billing_service.list_cong_no_cua_toi(db, makh, filters)

    return {
        "success": True,
        "message": "Lấy công nợ của bạn thành công",
        "data": {
            **result,
            "items": [
                CongNoResponse.model_validate(cn).model_dump()
                for cn in result["items"]
            ],
        },
    }


# ── GET /api/v1/cong-no ───────────────────────────────────────────────────────

@router.get("", response_model=dict)
def list_cong_no(
    mahd: str | None = Query(None),
    makh: str | None = Query(None),
    thang: int | None = Query(None, ge=1, le=12),
    nam: int | None = Query(None, ge=2000),
    trang_thai: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> dict:
    """Danh sách công nợ toàn bộ (nội bộ KDTC)."""
    _require_roles(current_user, ROLES_KDTC)

    filters = CongNoFilter(
        mahd=mahd,
        makh=makh,
        thang=thang,
        nam=nam,
        trang_thai=trang_thai,
        page=page,
        page_size=page_size,
    )
    result = billing_service.list_cong_no(db, filters)

    return {
        "success": True,
        "message": "Lấy danh sách công nợ thành công",
        "data": {
            **result,
            "items": [
                CongNoResponse.model_validate(cn).model_dump()
                for cn in result["items"]
            ],
        },
    }
