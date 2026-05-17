# File: app/routers/yc_thuethem.py
"""
Router Yêu cầu thuê thêm mặt bằng.

Phân quyền:
- Gửi yêu cầu           : KHACH_THUE
- Xem yêu cầu của mình  : KHACH_THUE
- Xem toàn bộ yêu cầu   : BQL
- Duyệt / Từ chối        : BQL
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.yc_thuethem import (
    YeuCauDuyetBody,
    YeuCauFilter,
    YeuCauThuaThemCreate,
    YeuCauThuaThemResponse,
)
from app.services import rent_request_service
from app.constants.roles import BQL, KHACH_THUE

router = APIRouter(prefix="/api/v1/yeu-cau-thue-them", tags=["Yêu cầu thuê thêm"])


def _require_roles(current_user: Any, allowed_roles: set[str]) -> None:
    if current_user.mavaitro not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền thực hiện thao tác này",
        )


def _require_makh(current_user: Any) -> str:
    """Lấy makh từ current_user, báo lỗi nếu không có."""
    if not current_user.makh:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản không liên kết với khách thuê nào",
        )
    return current_user.makh


# ── POST /api/v1/yeu-cau-thue-them ───────────────────────────────────────────

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def gui_yeu_cau(
    body: YeuCauThuaThemCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> dict:
    """Khách thuê gửi yêu cầu thuê thêm mặt bằng."""
    _require_roles(current_user, {KHACH_THUE})
    makh = _require_makh(current_user)

    yc = rent_request_service.create_yeu_cau(db, body, makh, current_user.matk)

    return {
        "success": True,
        "message": "Gửi yêu cầu thuê thêm thành công",
        "data": YeuCauThuaThemResponse.model_validate(yc).model_dump(),
    }


# ── GET /api/v1/yeu-cau-thue-them/cua-toi ────────────────────────────────────
# Đặt TRƯỚC /{mayc} để tránh route conflict

@router.get("/cua-toi", response_model=dict)
def yeu_cau_cua_toi(
    trangthai: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> dict:
    """Khách thuê xem danh sách yêu cầu thuê thêm của chính mình."""
    _require_roles(current_user, {KHACH_THUE})
    makh = _require_makh(current_user)

    filters = YeuCauFilter(trangthai=trangthai, page=page, page_size=page_size)
    result = rent_request_service.list_yeu_cau_cua_toi(db, makh, filters)

    return {
        "success": True,
        "message": "Lấy danh sách yêu cầu của bạn thành công",
        "data": {
            **result,
            "items": [
                YeuCauThuaThemResponse.model_validate(yc).model_dump()
                for yc in result["items"]
            ],
        },
    }


# ── GET /api/v1/yeu-cau-thue-them ────────────────────────────────────────────

@router.get("", response_model=dict)
def list_yeu_cau(
    trangthai: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> dict:
    """Ban Quản Lý xem toàn bộ danh sách yêu cầu thuê thêm."""
    _require_roles(current_user, {BQL})

    filters = YeuCauFilter(trangthai=trangthai, page=page, page_size=page_size)
    result = rent_request_service.list_yeu_cau_all(db, filters)

    return {
        "success": True,
        "message": "Lấy danh sách yêu cầu thuê thêm thành công",
        "data": {
            **result,
            "items": [
                YeuCauThuaThemResponse.model_validate(yc).model_dump()
                for yc in result["items"]
            ],
        },
    }


# ── PATCH /api/v1/yeu-cau-thue-them/{mayc}/duyet ─────────────────────────────

@router.patch("/{mayc}/duyet", response_model=dict)
def duyet_yeu_cau(
    mayc: str,
    body: YeuCauDuyetBody,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> dict:
    """Ban Quản Lý duyệt hoặc từ chối yêu cầu thuê thêm."""
    _require_roles(current_user, {BQL})

    yc = rent_request_service.duyet_yeu_cau(db, mayc, body, current_user.matk)

    action_label = "Duyệt" if body.ket_qua == "DUYET" else "Từ chối"

    return {
        "success": True,
        "message": f"{action_label} yêu cầu thuê thêm '{mayc}' thành công",
        "data": YeuCauThuaThemResponse.model_validate(yc).model_dump(),
    }
