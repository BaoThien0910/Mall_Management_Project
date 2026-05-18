# File: app/routers/baocaotaichinh.py
"""
Router Báo cáo tài chính (công nợ & doanh số).
Phân quyền:
- Lập báo cáo, ban hành : TP_KDTC
- Xem danh sách         : BQL, TP_KDTC
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.baocaotaichinh import (
    BaoCaoCongNoCreate,
    BaoCaoDoanhSoCreate,
    BaoCaoFilter,
    BaoCaoTaiChinhResponse,
)
from app.services import financial_report_service
from app.constants.roles import BQL, TP_KDTC

router = APIRouter(prefix="/api/v1/bao-cao-tai-chinh", tags=["Báo cáo tài chính"])

ROLES_XEM = {BQL, TP_KDTC}
ROLES_LAP = {TP_KDTC}


def _require_roles(current_user: Any, allowed: set[str]) -> None:
    if current_user.mavaitro not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền thực hiện thao tác này",
        )


# ── POST /api/v1/bao-cao-tai-chinh/cong-no ───────────────────────────────────

@router.post("/cong-no", response_model=dict, status_code=status.HTTP_201_CREATED)
def lap_bao_cao_cong_no(
    body: BaoCaoCongNoCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> dict:
    """TP_KDTC lập báo cáo công nợ cho một kỳ tháng/năm."""
    _require_roles(current_user, ROLES_LAP)

    bc = financial_report_service.lap_bao_cao_cong_no(db, body, current_user.matk)

    return {
        "success": True,
        "message": f"Lập báo cáo công nợ tháng {body.thang}/{body.nam} thành công",
        "data": BaoCaoTaiChinhResponse.model_validate(bc).model_dump(),
    }


# ── POST /api/v1/bao-cao-tai-chinh/doanh-so ──────────────────────────────────

@router.post("/doanh-so", response_model=dict, status_code=status.HTTP_201_CREATED)
def lap_bao_cao_doanh_so(
    body: BaoCaoDoanhSoCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> dict:
    """TP_KDTC lập báo cáo doanh số cho một kỳ tháng/năm."""
    _require_roles(current_user, ROLES_LAP)

    bc = financial_report_service.lap_bao_cao_doanh_so(db, body, current_user.matk)

    return {
        "success": True,
        "message": f"Lập báo cáo doanh số tháng {body.thang}/{body.nam} thành công",
        "data": BaoCaoTaiChinhResponse.model_validate(bc).model_dump(),
    }


# ── GET /api/v1/bao-cao-tai-chinh ────────────────────────────────────────────

@router.get("", response_model=dict)
def list_bao_cao(
    loai_bao_cao: str | None = Query(None, description="'Công nợ' hoặc 'Doanh số'"),
    thang: int | None = Query(None, ge=1, le=12),
    nam: int | None = Query(None, ge=2000),
    trang_thai: str | None = Query(None),
    nguoi_lap: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> dict:
    """BQL và TP_KDTC xem danh sách báo cáo tài chính."""
    _require_roles(current_user, ROLES_XEM)

    filters = BaoCaoFilter(
        loai_bao_cao=loai_bao_cao,
        thang=thang,
        nam=nam,
        trang_thai=trang_thai,
        nguoi_lap=nguoi_lap,
        page=page,
        page_size=page_size,
    )
    result = financial_report_service.list_bao_cao(db, filters)

    return {
        "success": True,
        "message": "Lấy danh sách báo cáo tài chính thành công",
        "data": {
            **result,
            "items": [
                BaoCaoTaiChinhResponse.model_validate(bc).model_dump()
                for bc in result["items"]
            ],
        },
    }


# ── PATCH /api/v1/bao-cao-tai-chinh/{mabctc}/ban-hanh ────────────────────────

@router.patch("/{mabctc}/ban-hanh", response_model=dict)
def ban_hanh_bao_cao(
    mabctc: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> dict:
    """TP_KDTC ban hành báo cáo tài chính (chỉ từ trạng thái 'Bản nháp')."""
    _require_roles(current_user, ROLES_LAP)

    bc = financial_report_service.ban_hanh_bao_cao(db, mabctc, current_user.matk)

    return {
        "success": True,
        "message": f"Ban hành báo cáo '{mabctc}' thành công",
        "data": BaoCaoTaiChinhResponse.model_validate(bc).model_dump(),
    }
